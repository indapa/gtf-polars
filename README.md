# gtf-polars

[![PyPI version](https://img.shields.io/pypi/v/gtf-polars.svg)](https://pypi.org/project/gtf-polars/)


Parse GTF files with Polars

Implements a memory-efficient GTF parser that stays fully lazy until .collect() is called. For more information on Polars Lazy API, see this [link](https://docs.pola.rs/user-guide/concepts/lazy-api/)


## Scripts

### `scripts/subset_gtf_feature.py`

Filters a GTF file to keep only rows matching one or more feature types (e.g. `gene`, `transcript`, `exon`) and writes the result as a tab-separated GTF file.

```bash
python scripts/subset_gtf_feature.py gencode.v39.annotation.gtf \
    --feature gene transcript \
    --output subset.gtf
```

| Argument | Description |
|----------|-------------|
| `gtf_file` | Path to the input GTF or gzipped GTF file |
| `--feature` | One or more feature types to keep |
| `--output` | Output path (default: `subset.gtf`) |

---

### `scripts/transcript_to_gene.py`

Builds a transcript-to-gene mapping CSV from a GTF file by extracting `transcript_id`, `gene_id`, and `gene_name` from transcript rows. Useful for downstream tools (e.g. alevin, tximeta) that require a tx2gene table.

```bash
python scripts/transcript_to_gene.py isoseq.gtf --output transcript_to_gene.csv
```

| Argument | Description |
|----------|-------------|
| `gtf_file` | Path to the input GTF file |
| `--output` | Output CSV path (default: `transcript_to_gene.csv`) |

---

## Library usage

```
from gtf_polars import parse_gtf
import polars as pl

lf = parse_gtf("gencode.v39.annotation.sorted.gtf", attributes_to_extract=["gene_id", "gene_name"])

df = (lf.filter(pl.col("feature") == 'transcript').select(['seqname', 'start','end','gene_id', 'gene_name']).collect())

df.head()
shape: (5, 5)
┌─────────┬───────┬───────┬───────────────────┬─────────────┐
│ seqname ┆ start ┆ end   ┆ gene_id           ┆ gene_name   │
│ ---     ┆ ---   ┆ ---   ┆ ---               ┆ ---         │
│ str     ┆ i64   ┆ i64   ┆ str               ┆ str         │
╞═════════╪═══════╪═══════╪═══════════════════╪═════════════╡
│ chr1    ┆ 11869 ┆ 14409 ┆ ENSG00000223972.5 ┆ DDX11L1     │
│ chr1    ┆ 12010 ┆ 13670 ┆ ENSG00000223972.5 ┆ DDX11L1     │
│ chr1    ┆ 14404 ┆ 29570 ┆ ENSG00000227232.5 ┆ WASH7P      │
│ chr1    ┆ 17369 ┆ 17436 ┆ ENSG00000278267.1 ┆ MIR6859-1   │
│ chr1    ┆ 29554 ┆ 31097 ┆ ENSG00000243485.5 ┆ MIR1302-2HG │
└─────────┴───────┴───────┴───────────────────┴─────────────┘
```