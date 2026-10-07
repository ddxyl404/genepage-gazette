# GenePage figures（P3.6）

科研示意用图示数据与缓存；**非诊疗**。

## 目录

```
figures/
  README.md           ← 本文件
  cytobands/          ← 染色体带型骨架 JSON（按 chrom）
    7.json
    8.json
    11.json
    12.json
    13.json
    17.json
    19.json
    21.json
```

相关缓存（在 `data/cache/`）：

```
cache/alphafold/{SYMBOL}.png   ← AlphaFold 静态预览（CA 迹线或 PAE）
cache/alphafold/{SYMBOL}.pdb   ← 渲染用 PDB（可选保留）
cache/uniprot/{ACC}.json       ← UniProt REST 缓存
```

## cytobands/{chrom}.json

```json
{
  "chrom": "17",
  "assembly": "GRCh38",
  "bands": [{"id": "p13.1", "start": 6500000, "end": 10700000, "stain": "gneg"}],
  "source": "UCSC cytoBandIdeo (hg38 / GRCh38)",
  "url": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/cytoBandIdeo.txt.gz"
}
```

基因 JSON 通过 `cytoband.figure_id`（如 `cytobands/17.json`）引用，并用 `start`/`end` 钉位点。

## 同步

```bash
python3 /workspace/genepage/data/scripts/sync_figures.py
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
```

可选：`SYNC_SYMBOLS=TP53,BRCA1` · `UNIPROT_DELAY` / `AF_DELAY`（默认 ~0.35s）。
