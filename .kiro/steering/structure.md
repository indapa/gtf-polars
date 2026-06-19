# Project Structure

```
gtf-polars/
├── gtf_polars/              # Main library package
│   ├── __init__.py          # Public API: exports parse_gtf and GTF_COLUMNS
│   └── parser.py            # Core implementation: GTFColumns dataclass + parse_gtf()
├── tests/
│   ├── data/
│   │   └── test.gtf         # Small fixture GTF file (8 data rows, comments stripped)
│   └── test_parser.py       # All unit tests, organised into test classes
├── scripts/
│   └── transcript_to_gene.py  # CLI script: builds transcript→gene mapping CSV
├── pyproject.toml           # Project metadata, dependencies, pytest config
├── uv.lock                  # Locked dependency versions
├── Dockerfile               # Container image for use in Nextflow pipelines
└── .github/workflows/       # CI: unit-tests.yml, docker-image.yml
```

## Conventions

### Library code (`gtf_polars/`)
- All public exports must be declared in `__init__.py` via `__all__`
- `parse_gtf` must always return `pl.LazyFrame` — never a `DataFrame`
- Column names are centralised in the `GTFColumns` frozen dataclass; use `GTF_COLUMNS.<FIELD>` constants rather than string literals throughout the code
- All attribute extraction must be done in a single `with_columns()` call (one parallel pass), not row-by-row
- Use `from __future__ import annotations` at the top of every module

### Tests (`tests/`)
- Tests are grouped into classes by concern (e.g. `TestReturnType`, `TestStandardColumns`, `TestAttributeExtraction`, `TestLazyChaining`)
- Use the `collect()` helper to materialise a `LazyFrame` inside tests — do not call `.collect()` inline
- Test data lives in `tests/data/`; add new fixture files there when needed
- Tests must verify laziness: any function returning a `LazyFrame` should assert `isinstance(result, pl.LazyFrame)` before collecting

### Scripts (`scripts/`)
- Standalone CLI utilities that use the library
- Must use `argparse` for argument parsing
- Follow the `if __name__ == "__main__": main()` pattern

### Naming
- Snake_case for all Python identifiers
- GTF column name constants are UPPER_CASE fields on `GTFColumns`
