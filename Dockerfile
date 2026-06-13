FROM python:3.12.13-slim

# Install procps so Nextflow can track metrics
RUN apt-get update && \
    apt-get install -y procps && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the package and its runtime dependencies.
COPY pyproject.toml README.md ./
COPY gtf_polars ./gtf_polars
RUN python -m pip install --upgrade pip && python -m pip install .
COPY scripts/transcript_to_gene.py /usr/local/bin/transcript_to_gene.py
RUN chmod +x /usr/local/bin/transcript_to_gene.py

# NOTE: Removed 'USER appuser' so Nextflow can freely write 
# task outputs and metrics to the mounted working directory.


