# gtf-polars
Parse GTF files with Polars

Implements a memory-efficient GTF parser that stays fully lazy until .collect() is called


```
from gtf_polars import parse_gt
from gtf_polars import parse_gtf

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