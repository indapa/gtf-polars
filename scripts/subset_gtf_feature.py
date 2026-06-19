#!/usr/bin/env python3
"""Subset a GTF file by one or more feature types (e.g. gene, transcript, exon)."""

from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from gtf_polars import GTF_COLUMNS, parse_gtf


def subset_gtf_by_feature(
    gtf_file: Path,
    features: list[str],
    output_gtf: Path,
) -> None:
    """Parse a GTF file, keep only rows matching *features*, and write valid GTF output.

    Parameters
    ----------
    gtf_file:
        Path to the input GTF or gzipped GTF file.
    features:
        Feature type(s) to keep, e.g. ``["gene", "transcript"]``.
    output_gtf:
        Destination path for the filtered GTF file.
    """
    lf = parse_gtf(str(gtf_file))

    filtered = lf.filter(pl.col(GTF_COLUMNS.FEATURE).is_in(features))

    # Reconstruct GTF-compatible string columns before writing.
    # parse_gtf casts start/end to Int64 and replaces "." with null for
    # score and frame — reverse those transformations here.
    filtered = filtered.with_columns(
        [
            pl.col(GTF_COLUMNS.START).cast(pl.Utf8),
            pl.col(GTF_COLUMNS.END).cast(pl.Utf8),
            pl.col(GTF_COLUMNS.SCORE)
            .cast(pl.Utf8)
            .fill_null("."),
            pl.col(GTF_COLUMNS.FRAME)
            .cast(pl.Utf8)
            .fill_null("."),
        ]
    )

    # Select columns in canonical GTF order.
    filtered = filtered.select(list(GTF_COLUMNS))
    filtered.sink_csv(output_gtf, separator="\t", include_header=False)
    

    


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Subset a GTF file by feature type(s)"
    )
    parser.add_argument(
        "gtf_file",
        type=Path,
        help="Path to the input GTF or gzipped GTF file",
    )
    parser.add_argument(
        "--feature",
        dest="features",
        metavar="FEATURE",
        nargs="+",
        required=True,
        help="Feature type(s) to keep (e.g. gene transcript exon)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("subset.gtf"),
        help="Output GTF path (default: subset.gtf)",
    )

    args = parser.parse_args()
    subset_gtf_by_feature(args.gtf_file, args.features, args.output)


if __name__ == "__main__":
    main()
