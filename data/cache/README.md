# Gazette P2 数据缓存

`data/genes/*.json` 是 GenePage 的**唯一主数据源**。本目录缓存供追溯、重跑与 `/api/cache/status` 清单使用；API **不**把 cache overlay 运行时覆盖到基因返回。

`GENEPAGE_CACHE_DIR` 可指定缓存根，默认 `/workspace/genepage/data/cache`。

同步入口：`python3 /workspace/genepage/data/scripts/sync_all.py`  
当前 P2（`0.2.0-p2`，`data_as_of` 见 `meta.json`）已写入 10 示范基因的 clinvar / gtex / mygene 缓存。

## 布局

```
cache/
  meta.json           # edition / data_as_of / 同步摘要
  clinvar/<SYMBOL>.json
  gtex/<SYMBOL>.json
  mygene/<SYMBOL>.json
```

`SYMBOL` 大写。同步脚本写入的是**原始拉取/审计形状**（含 `ok`、`error`、`queried_at` 与原始字段）；合并后的展示字段以 `genes/<SYMBOL>.json` 为准。

## 脚本写出的字段摘要

### `clinvar/SYMBOL.json`

`pathogenic` / `likely_pathogenic`（esearch count）、`ok`、`queried_at`、`method`。

### `gtex/SYMBOL.json`

`gencode_id`、原始 `median_rows`、以及规范化后的 `result.tissues`（含 `name` / `name_zh` / `value`）。

### `mygene/SYMBOL.json`

身份字段（`id`、`aliases`、`location`、`uniprot`、`alphafold_url`、`pathways`）+ 可选 `raw_hit`。

失败时基因 JSON 对应字段为「本期未收录」或空 `tissues`，`sources`/`confidence` 标 `unavailable`；**不再**保留 seed 假数。
