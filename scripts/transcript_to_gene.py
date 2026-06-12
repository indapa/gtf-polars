#!/usr/bin/env python3
"""Create a transcript-to-gene mapping CSV from an Iso-Seq GTF file."""

from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from gtf_polars import parse_gtf


def build_transcript_to_gene_csv(gtf_file: Path, output_csv: Path) -> None:
    """Parse a GTF file and write transcript_id -> gene_name mapping CSV."""
    lf = parse_gtf(gtf_file, attributes_to_extract=["gene_name", "transcript_id"])

    df = (
        lf.filter(pl.col("feature") == "transcript")
        .select(["transcript_id", "gene_name"])
        .collect()
    )

    df.write_csv(output_csv)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate transcript-to-gene CSV from a GTF file"
    )
    parser.add_argument(
        "gtf_file",
        type=Path,
        help="Path to the input GTF file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("transcriptTogene.csv"),
        help="Output CSV path (default: transcriptTogene.csv)",
    )

    args = parser.parse_args()
    build_transcript_to_gene_csv(args.gtf_file, args.output)


if __name__ == "__main__":
    main()
