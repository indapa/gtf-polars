# Product: gtf-polars

A Python library for parsing GTF (Gene Transfer Format) files using the Polars lazy evaluation API.

## Purpose

GTF files are standard genomics annotation files (e.g., GENCODE, Ensembl) that describe gene structures. `gtf-polars` provides a memory-efficient parser that stays fully lazy until `.collect()` is called, enabling users to filter and select data before loading anything into memory.

## Primary API

- `parse_gtf(file_path, attributes_to_extract=None)` — returns a `pl.LazyFrame` with the 9 standard GTF columns plus any requested attribute columns extracted from the 9th `attributes` field.
- `GTF_COLUMNS` — a frozen dataclass instance exposing the 9 standard column names (`seqname`, `source`, `feature`, `start`, `end`, `score`, `strand`, `frame`, `attributes`).

## Target Users

Bioinformaticians and data scientists who need to process large genomics annotation files in Python pipelines, including Nextflow workflows.

## Key Constraint

The library must remain fully lazy — no eager materialisation inside `parse_gtf`. Users call `.collect()` themselves after chaining filters and selects.
