"""Tests for gtf_polars.parse_gtf."""

from __future__ import annotations

import pathlib

import polars as pl


from gtf_polars import GTF_COLUMNS, parse_gtf

DATA_DIR = pathlib.Path(__file__).parent / "data"
SAMPLE_GTF = DATA_DIR / "test.gtf"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect(lf: pl.LazyFrame) -> pl.DataFrame:
    """Materialise a LazyFrame for assertions."""
    return lf.collect()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_lazyframe(self):
        result = parse_gtf(str(SAMPLE_GTF))
        assert isinstance(result, pl.LazyFrame), (
            "parse_gtf must return a pl.LazyFrame, not a DataFrame"
        )

    def test_no_attributes_still_lazy(self):
        lf = parse_gtf(str(SAMPLE_GTF), attributes_to_extract=None)
        assert isinstance(lf, pl.LazyFrame)

    def test_empty_attributes_still_lazy(self):
        lf = parse_gtf(str(SAMPLE_GTF), attributes_to_extract=[])
        assert isinstance(lf, pl.LazyFrame)


class TestStandardColumns:
    def test_has_all_gtf_columns(self):
        df = collect(parse_gtf(str(SAMPLE_GTF)))
        for col in GTF_COLUMNS:
            assert col in df.columns, f"Expected column '{col}' not found"

    def test_column_order(self):
        df = collect(parse_gtf(str(SAMPLE_GTF)))
        assert df.columns[:9] == GTF_COLUMNS

    def test_row_count(self):
        # Fixture has 8 data rows (comment lines are skipped).
        df = collect(parse_gtf(str(SAMPLE_GTF)))
        assert df.height == 8

    def test_seqname_values(self):
        df = collect(parse_gtf(str(SAMPLE_GTF)))
        assert df["seqname"].to_list() == ["chr1"] * 8

    def test_feature_values(self):
        df = collect(parse_gtf(str(SAMPLE_GTF)))
        features = set(df["feature"].to_list())
        assert features == {"gene", "transcript", "exon"}


class TestAttributeExtraction:
    def test_gene_id_extracted(self):
        df = collect(parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["gene_id"]))
        assert "gene_id" in df.columns
        # All rows must have a non-null gene_id.
        assert df["gene_id"].null_count() == 0

    def test_gene_id_values(self):
        df = collect(parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["gene_id"]))
        gene_ids = set(df["gene_id"].to_list())
        assert "ENSG00000223972" in gene_ids
        assert "ENSG00000278267" in gene_ids
        assert "ENSG00000243485" in gene_ids

    def test_multiple_attributes(self):
        attrs = ["gene_id", "gene_name", "transcript_id"]
        df = collect(parse_gtf(str(SAMPLE_GTF), attributes_to_extract=attrs))
        for attr in attrs:
            assert attr in df.columns

    def test_transcript_id_null_for_gene_rows(self):
        df = collect(
            parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["transcript_id"])
        )
        gene_rows = df.filter(pl.col("feature") == "gene")
        # Gene-level rows in the fixture do not have a transcript_id attribute.
        assert gene_rows["transcript_id"].null_count() == gene_rows.height

    def test_transcript_id_present_for_transcript_rows(self):
        df = collect(
            parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["transcript_id"])
        )
        tx_rows = df.filter(pl.col("feature") == "transcript")
        assert tx_rows["transcript_id"].null_count() == 0

    def test_unknown_attribute_returns_null_column(self):
        df = collect(
            parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["nonexistent_attr"])
        )
        assert "nonexistent_attr" in df.columns
        assert df["nonexistent_attr"].null_count() == df.height

    def test_attributes_column_preserved(self):
        df = collect(parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["gene_id"]))
        # Raw attributes column must still be present.
        assert "attributes" in df.columns


class TestLazyChaining:
    def test_can_filter_before_collect(self):
        lf = parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["gene_id"])
        filtered = lf.filter(pl.col("feature") == "gene")
        assert isinstance(filtered, pl.LazyFrame)
        df = filtered.collect()
        assert (df["feature"] == "gene").all()

    def test_can_select_before_collect(self):
        lf = parse_gtf(str(SAMPLE_GTF), attributes_to_extract=["gene_id"])
        selected = lf.select(["seqname", "feature", "gene_id"])
        assert isinstance(selected, pl.LazyFrame)
        df = selected.collect()
        assert df.columns == ["seqname", "feature", "gene_id"]
