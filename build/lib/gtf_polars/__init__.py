"""gtf_polars – parse GTF files with Polars lazy evaluation."""

from gtf_polars.parser import GTF_COLUMNS, parse_gtf

__all__ = ["parse_gtf", "GTF_COLUMNS"]
