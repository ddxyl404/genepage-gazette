# GenePage Gazette — CSV 导出说明（P3 / P3.5）

从 `genes/*.json` 导出扁平目录表，便于 Excel / 表格工具浏览。

## 命令

```bash
# 仅导出 CSV
python3 /workspace/genepage/data/scripts/export_csv.py

# 重建 index.json + AlphaFold 审计 + CSV（推荐）
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
```

## 输出

| 路径 | 说明 |
|------|------|
| `exports/genes_catalog.csv` | 基因目录表（UTF-8 **with BOM**，便于 Excel 打开中文） |
| `exports/alphafold_audit.md` | AlphaFold URL 一致性审计（由 `rebuild_catalog.py` 生成） |

行顺序：优先 `index.json` 中的基因顺序，否则示范 10 基因固定顺序（TP53→…→MYC），再补其余文件。

## 字段表

| 列名 | 来源 JSON 路径 | 说明 |
|------|----------------|------|
| `symbol` | `symbol` | HGNC 符号 |
| `ensembl_id` | `id` | Ensembl gene id |
| `aliases` | `aliases` | 别名，以 `;` 连接 |
| `type` | `type` | 如 `protein_coding` |
| `chrom` | `location.chrom` | 染色体（无 `chr` 前缀） |
| `start` | `location.start` | GRCh38 起点 |
| `end` | `location.end` | GRCh38 终点 |
| `assembly` | `location.assembly` | 如 `GRCh38` |
| `location_label` | `headline_stats[key=location].value` | 细胞遗传学位点，如 `17p13.1` |
| `clinvar_pathogenic` | `variants_summary.clinvar_pathogenic` | ClinVar 致病计数 |
| `clinvar_likely_pathogenic` | `variants_summary.clinvar_likely_pathogenic` | ClinVar 可能致病计数 |
| `clinvar_plp` | `headline_stats[key=clinvar_plp].value` | P+LP 合计（headline）；失败可为空/文案 |
| `top_tissue_zh` | `headline_stats[key=top_tissue].value` | GTEx 最高表达组织短中文 |
| `top_tissue_en` | `headline_stats[key=top_tissue].detail` | 对应英文组织全称 |
| `alphafold_url` | `structure.alphafold_url` | AlphaFold DB 条目 URL；可空 |
| `data_as_of` | `colophon.data_as_of` | `YYYY-MM-DD` |
| `edition` | `colophon.edition` | 数据版号，如 `0.3.0-p35` |
| `sources` | `sources[]` | 多源以 `;` 分隔；每源格式 `name\|url\|version\|confidence` |
| `deck_zh` | `deck_zh` | 中文导语（双语列；CSV 标准双引号转义） |
| `deck_en` | `deck_en` | 英文导语（双语列；P3.5） |


## 语言相关列 vs 语言无关列（P3.5）

| 类别 | 列 | 说明 |
|------|-----|------|
| **双语** | `deck_zh`, `deck_en` | 导语；前端/读者按语言选用 |
| **双语展示辅助** | `top_tissue_zh`, `top_tissue_en` | 组织短中文 / 英文全称（已有） |
| **语言无关** | `symbol`, `ensembl_id`, `aliases`, `type`, `chrom`, `start`, `end`, `assembly`, `location_label`, `clinvar_*`, `alphafold_url`, `data_as_of`, `edition`, `sources` | 符号、坐标、ClinVar 计数、出处与日期不按语言分列 |

逐组织 TPM、`expression.caption_*` / `structure.caption_*` 仍只在单基因 JSON 中。

## 编码与转义

- 文件编码：`utf-8-sig`（UTF-8 with BOM）。
- `csv` 模块默认 `QUOTE_MINIMAL`：含逗号、换行或双引号的字段会加引号，内部 `"` → `""`。
- 空值写为空单元格（非字面量 `null`）。

## 与 schema 对齐

列集覆盖身份、坐标、headline 摘要、ClinVar、表达 top、结构、colophon 与 sources，供目录页 / 表格导出使用；逐组织 TPM 与 pathways 仍只在单基因 JSON 中。
