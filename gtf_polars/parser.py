"""GTF (Gene Transfer Format) parser using Polars lazy evaluation."""

from __future__ import annotations

import polars as pl

# Standard 9 GTF column names as defined by the GTF/GFF2 specification.
GTF_COLUMNS = [
    "seqname",
    "source",
    "feature",
    "start",
    "end",
    "score",
    "strand",
    "frame",
    "attributes",
]


def parse_gtf(
    file_path: str,
    attributes_to_extract: list[str] | None = None,
) -> pl.LazyFrame:
    """Parse a GTF file lazily using Polars.

    Reads the file with ``pl.scan_csv`` so the data is never fully loaded into
    memory until ``.collect()`` is called.  Attribute columns are extracted
    with vectorised Polars string expressions, keeping the query fully lazy.

    Parameters
    ----------
    file_path:
        Path to the GTF (or gzipped GTF) file.
    attributes_to_extract:
        Attribute keys to parse out of the 9th ``attributes`` column into
        their own columns.  For example ``["gene_id", "gene_name",
        "transcript_id"]``.  If *None* or empty the ``attributes`` column is
        returned as-is.

    Returns
    -------
    pl.LazyFrame
        A lazy frame containing the 9 standard GTF columns (the 8 feature
        columns plus the raw ``attributes`` column), and one additional
        column per requested attribute key.  Call ``.collect()`` (optionally
        after chaining further filters) to materialise the result.

    Notes
    -----
    **How lazy regex extraction works**

    GTF attributes look like::

        gene_id "ENSG00000223972"; gene_name "DDX11L1"; transcript_id "ENST00000456328";

    For each requested key (e.g. ``"gene_id"``) the expression

    .. code-block:: python

        pl.col("attributes").str.extract(r'gene_id\\s+"([^"]*)"', group_index=1)

    is compiled into the query plan as a single pass over the ``attributes``
    column.  Polars evaluates this *in parallel across chunks* when
    ``.collect()`` is eventually called, with no Python-level row iteration.
    """
    lf = pl.scan_csv(
        file_path,
        separator="\t",
        comment_prefix="#",
        has_header=False,
        new_columns=GTF_COLUMNS,
        infer_schema=False,
    )

    if attributes_to_extract:
        # Build all extraction expressions up-front so they are applied in a
        # single ``with_columns`` call (one parallel pass over the data).
        exprs = [
            pl.col("attributes")
            .str.extract(rf'{attr}\s+"([^"]*)"', group_index=1)
            .alias(attr)
            for attr in attributes_to_extract
        ]
        lf = lf.with_columns(exprs)

    return lf
