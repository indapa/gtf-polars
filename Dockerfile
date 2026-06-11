FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the package and its runtime dependencies.
COPY pyproject.toml README.md ./
COPY gtf_polars ./gtf_polars
RUN python -m pip install --upgrade pip && python -m pip install .

# Use a non-root user for runtime safety.
RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

CMD ["python"]
