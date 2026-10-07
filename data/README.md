# GenePage Gazette — 基因数据（P2 / P3 / P3.5 双语 / P3.6 图示）

**edition:** `0.3.1-p36`（基因 JSON / index / CSV 同源；P3.5 双语 + P3.6 染色体带型 / domains / AlphaFold 预览）  
**catalog_schema:** `1.0`（`index.json` 目录条目字段）  
**data_as_of:** `2026-09-30`（Asia/Shanghai）  
**status:** P2 真值 + P3 目录/CSV + P3.5 双语 + P3.6 cytoband / UniProt domains / expression small-multiples captions / AlphaFold 本地预览

## 目录

```
data/
  README.md              ← 本文件
  schema.md              ← 基因 JSON + index 字段说明
  CSV_EXPORT.md          ← CSV 列定义与命令
  index.json             ← 目录页索引（富化条目）
  genes/                 ← API 读取的基因 JSON（10 示范基因）
  exports/
    genes_catalog.csv    ← 扁平目录导出（UTF-8 BOM）
    alphafold_audit.md   ← AlphaFold URL 一致性审计
  figures/
    README.md            ← 图示约定（P3.6）
    cytobands/           ← 染色体带型 JSON（UCSC cytoBandIdeo）
  cache/
    meta.json            ← 全局 data_as_of / 同步摘要
    clinvar/             ← 每基因 ClinVar 原始计数
    gtex/                ← 每基因 GTEx 原始响应摘要
    mygene/              ← 每基因 MyGene 身份缓存
    uniprot/             ← UniProt REST 缓存（domains）
    alphafold/           ← AlphaFold 预览 PNG（+ PDB）
  scripts/
    sync_all.py          ← 一键数据同步入口（P2）
    sync_clinvar.py
    sync_gtex.py
    sync_mygene.py
    sync_figures.py      ← P3.6：cytobands / domains / captions / AF 预览
    tissue_zh.py         ← 组织英→中短名映射
    rebuild_catalog.py   ← 重建 index + AlphaFold 审计 + CSV
    export_csv.py        ← 仅导出 CSV
    ensure_i18n_fields.py ← P3.5：校验 deck_en / name_zh / captions
    ensure_p36_fields.py ← P3.6：校验 cytoband / domains / preview / captions
```

## 如何跑同步（P2 数据）

```bash
python3 /workspace/genepage/data/scripts/sync_all.py
```

可选环境变量：

| 变量 | 默认 | 说明 |
|------|------|------|
| `CLINVAR_DELAY` / `NCBI_DELAY` | `0.34` | NCBI 请求间隔（秒） |
| `GTEX_DELAY` | `0.2` | GTEx 请求间隔 |
| `MYGENE_DELAY` | `0.15` | MyGene 请求间隔 |
| `GTEX_DATASET` | `gtex_v8` | GTEx datasetId |
| `SYNC_SYMBOLS` | （全部 10） | 逗号分隔子集，如 `TP53,BRCA1` |

依赖：Python 3 标准库；若已安装则优先用 `requests`，否则回退 `urllib`。

同步后若需刷新目录页字段与 CSV，再跑：

```bash
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
```

## P3：目录索引与 CSV

### 重建 index + 导出 CSV（一键）

```bash
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
```

仅 CSV：

```bash
python3 /workspace/genepage/data/scripts/export_csv.py
```

### `index.json` 顶层

| 字段 | 说明 |
|------|------|
| `edition` | 与基因 `colophon.edition` 对齐（现 `0.3.1-p36`） |
| `data_as_of` | 取基因 `colophon.data_as_of` 最新值 |
| `count` | 基因条目数（示范 10） |
| `catalog_schema` | 目录条目 schema 版本，现 `1.0` |
| `genes` | 富化目录条目数组 |

### 目录条目字段（每基因至少）

| 字段 | 来源 | 说明 |
|------|------|------|
| `symbol` / `id` | 基因 JSON | 须与 `genes/<SYMBOL>.json` 一致 |
| `file` | 约定路径 | 如 `genes/TP53.json`，文件须存在 |
| `aliases` / `type` | 基因 JSON | 别名与类型 |
| `location_label` | `headline_stats[key=location].value` | 如 `17p13.1` |
| `clinvar_plp` | `headline_stats[key=clinvar_plp].value` | 数字；失败可为 `null` |
| `top_tissue` | `headline_stats[key=top_tissue].value` | 短中文 |
| `top_tissue_detail` | 同上 `detail` | 可选英文全称 |
| `alphafold_url` | `structure.alphafold_url` | URL 或 `null` |
| `data_as_of` / `edition` | `colophon` | 与单基因一致 |

CSV 列定义见 [`CSV_EXPORT.md`](./CSV_EXPORT.md)。


## P3.5：双语字段

- 每基因保留 `deck_zh`，新增 `deck_en`（2–3 句英文导语）。
- `expression.tissues[]` 每项含 `name`（英）与 `name_zh`（中）；`expression` / `structure` 挂 `caption_zh` / `caption_en`。
- `sources`、`data_as_of`、ClinVar 数字、坐标：**语言无关**。
- `colophon.edition` = `0.3.1-p36`；CSV 增加 `deck_en` 列。
- 校验：`python3 /workspace/genepage/data/scripts/ensure_i18n_fields.py`

## 示范基因（10）

| symbol | Ensembl id      | UniProt |
|--------|-----------------|---------|
| TP53   | ENSG00000141510 | P04637  |
| BRCA1  | ENSG00000012048 | P38398  |
| BRCA2  | ENSG00000139618 | P51587  |
| EGFR   | ENSG00000146648 | P00533  |
| KRAS   | ENSG00000133703 | P01116  |
| APOE   | ENSG00000130203 | P02649  |
| CFTR   | ENSG00000001626 | P13569  |
| HBB    | ENSG00000244734 | P68871  |
| APP    | ENSG00000142192 | P05067  |
| MYC    | ENSG00000136997 | P01106  |

## 数据来源与置信度（P2）

| 字段域 | 来源 | confidence |
|--------|------|------------|
| id / symbol / aliases / location | MyGene.info v3 → Ensembl GRCh38 | **high** |
| pathways | MyGene `pathway.kegg` → KEGG URL | **medium** |
| structure.alphafold_url | UniProt → AlphaFold DB | **high** |
| ClinVar P / LP 计数 | NCBI E-utilities `esearch`（`[gene]` + `clinsig_*[prop]`），非正式 tar 导出 | **high**（失败则 `unavailable`，value「本期未收录」） |
| GTEx TPM / top_tissue | GTEx Portal API v2 `medianGeneExpression`（默认 `gtex_v8`）；`name_zh` / `top_tissue.value` 为展示映射 | **high**（失败则 tissues=[]，value「本期未收录」） |
| deck_zh / deck_en | 中/英导语（科研/教学，无诊疗建议；P3.5 补全英文） | medium |
| expression/structure captions | `caption_zh` / `caption_en` 短图注（P3.5） | medium |

P2 **不再**使用 `seed` 占位；失败字段写「本期未收录」并在 `sources` / `confidence` 标明 `unavailable`。

`variants_detail` 本期为空数组（无逐条收录）；前端已有空态。

## 许可与引用（摘要）

- **ClinVar / NCBI E-utilities**：遵守 NCBI 使用政策与礼貌限速（无 API key 约 ≤3 req/s）。
- **GTEx**：遵从 GTEx Portal / 相关数据使用条款；组织中文标签为本站展示映射，非官方字段。
- **MyGene.info / Ensembl / KEGG / AlphaFold**：按各来源条款引用；本仓库仅缓存同步结果供示范站使用。

## 免责声明

**科研/教学信息工具，非医疗器械，不提供诊断建议。**  
ClinVar 计数来自 E-utilities 检索，非正式诊断结论，非正式 ClinVar 导出归档。见各文件 `colophon.disclaimer_zh`。

## 约束

- 本目录仅含数据资产与同步/导出脚本；不改动 `web/` / `api/` / 视觉。
- JSON：UTF-8，`indent=2`，`ensure_ascii=False`。
- CSV：UTF-8 with BOM（`utf-8-sig`）。


## 如何跑图示同步（P3.6）

```bash
python3 /workspace/genepage/data/scripts/sync_figures.py
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
# 可选校验
python3 /workspace/genepage/data/scripts/ensure_p36_fields.py
```

写入：`cytoband`、`domains[]`、`expression.caption_*`（small multiples）、`structure.preview_image`、`colophon.edition=0.3.1-p36`。  
礼貌限速：`UNIPROT_DELAY` / `AF_DELAY`（默认 0.35）。子集：`SYNC_SYMBOLS=TP53,BRCA1`。
