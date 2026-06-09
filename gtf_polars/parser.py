"""GTF (Gene Transfer Format) parser using Polars lazy evaluation."""

from __future__ import annotations

from dataclasses import dataclass, astuple
import polars as pl

@dataclass(frozen=True)
class GTFColumns:
    """Standard 9 GTF column names as defined by the GTF/GFF2 specification."""
    SEQNAME: str = "seqname"
    SOURCE: str = "source"
    FEATURE: str = "feature"
    START: str = "start"
    END: str = "end"
    SCORE: str = "score"
    STRAND: str = "strand"
    FRAME: str = "frame"
    ATTRIBUTES: str = "attributes"

GTF_COLUMNS = GTFColumns()


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
    # Safeguard: Convert the dataclass fields to a native list for the Rust layer
    gtf_columns_list = list(astuple(GTF_COLUMNS))

    # 1. Scan the CSV file without schema inference to avoid parse crashes 
    # caused by standard "." missing value tokens in numeric/integer columns.
    lf = pl.scan_csv(
        file_path,
        separator="\t",
        comment_prefix="#",
        has_header=False,
        new_columns=gtf_columns_list,
        infer_schema=False,
    )

    # 2. Lazily sanitize missing value representations (".") and cast types cleanly
    lf = lf.with_columns([
        # Cast guaranteed integer coordinates directly
        pl.col(GTF_COLUMNS.START).cast(pl.Int64),
        pl.col(GTF_COLUMNS.END).cast(pl.Int64),

        # Handle "." markers in the score column by mapping to null prior to float conversion
        pl.when(pl.col(GTF_COLUMNS.SCORE) == ".")
        .then(None)
        .otherwise(pl.col(GTF_COLUMNS.SCORE))
        .cast(pl.Float64)
        .alias(GTF_COLUMNS.SCORE),

        # Handle "." markers in the frame column by mapping to null
        pl.when(pl.col(GTF_COLUMNS.FRAME) == ".")
        .then(None)
        .otherwise(pl.col(GTF_COLUMNS.FRAME))
        .alias(GTF_COLUMNS.FRAME)
    ])

    if attributes_to_extract:
        # Deduplicate while preserving order and guard against column collisions.
        seen: set[str] = set()
        attrs: list[str] = []
        for attr in attributes_to_extract:
            if attr in gtf_columns_list:
                raise ValueError(
                    f"Attribute name '{attr}' would overwrite a standard GTF column"
                )
            if attr not in seen:
                seen.add(attr)
                attrs.append(attr)

        import re

        # Build all extraction expressions up-front so they are applied in a
        # single ``with_columns`` call (one parallel pass over the data).
        exprs = [
            pl.col(GTF_COLUMNS.ATTRIBUTES)
            .str.extract(rf'(?:^|;\s*){re.escape(attr)}\s+"([^"]*)"', group_index=1)
            .alias(attr)
            for attr in attrs
        ]
        lf = lf.with_columns(exprs)

    return lf
