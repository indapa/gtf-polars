# Tech Stack

## Language & Runtime
- Python >= 3.10
- Requires Python 3.12 in CI and Docker

## Key Dependencies
- `polars >= 1.0.0` — core data processing; lazy API is central to the library
- `pandera[polars] >= 0.18.0` — schema validation
- `pytest >= 7.0` — test framework (dev dependency)

## Build System
- `setuptools >= 61.0` with `pyproject.toml`
- Package name: `gtf-polars`, importable as `gtf_polars`

## Package Manager
- `uv` is used for dependency locking (`uv.lock` is present)
- Standard `pip` is used in CI and Docker

## Common Commands

### Install for development
```bash
pip install -e ".[dev]"
```

### Run tests
```bash
pytest
```

### Run a single test file
```bash
pytest tests/test_parser.py
```

### Build the Docker image
```bash
docker build -t gtf-polars .
```

## CI
- GitHub Actions runs unit tests on pull requests to `master` and on `workflow_dispatch`
- Docker image build is also automated via GitHub Actions

## Docker
- Base image: `python:3.12.13-slim`
- `procps` is installed for Nextflow metric tracking
- The `transcript_to_gene.py` script is installed to `/usr/local/bin/` inside the container
- Runs as root (intentional — required for Nextflow to write task outputs)
