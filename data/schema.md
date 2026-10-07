# GenePage Gazette — Gene JSON Schema（P2 / P3.5 双语 / P3.6 图示）

每个 `genes/<SYMBOL>.json` 必须符合下列结构。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | Ensembl gene id，如 `ENSG00000141510` |
| `symbol` | string | ✓ | HGNC 符号 |
| `aliases` | string[] | ✓ | 别名列表（可空数组） |
| `type` | string | ✓ | P1/P2 统一为 `protein_coding` |
| `location` | object | ✓ | 见下 |
| `deck_zh` | string | ✓ | 2–3 句中文导语（科研/教学，无诊疗建议） |
| `deck_en` | string | ✓ | 2–3 句英文导语（对应 `deck_zh` 科研/教学语气；无诊疗建议；P3.5） |
| `headline_stats` | object[] | ✓ | 页头统计条 |
| `pathways` | object[] | ✓ | KEGG 等通路，3–5 条优先 |
| `expression` | object | ✓ | GTEx 表达 |
| `structure` | object | ✓ | AlphaFold（含 `preview_image`） |
| `cytoband` | object | ✓（P3.6） | 染色体带型位点 + figure 引用 |
| `domains` | object[] | ✓（P3.6） | UniProt 结构域条；无则 `[]` |
| `variants_summary` | object | ✓ | ClinVar 摘要 |
| `variants_detail` | object[] | 可选 | 逐条变异；本期可为 `[]` |
| `colophon` | object | ✓ | 版本与免责 |
| `sources` | object[] | ✓ | 出处列表 |
| `confidence` | object | 推荐 | 分项置信度（P2 不再使用 `seed`） |

## `location`

```json
{"chrom": "17", "start": 7661779, "end": 7687550, "assembly": "GRCh38"}
```

- `chrom`：无 `chr` 前缀的染色体名  
- `start` / `end`：整数，GRCh38  
- `assembly`：固定 `GRCh38`

## `headline_stats[]`

每项：

| 字段 | 说明 |
|------|------|
| `key` | `location` \| `clinvar_plp` \| `top_tissue` |
| `label_zh` | 中文标签 |
| `value` | 字符串或数字（`clinvar_plp` 为 P+LP 数字；失败时为「本期未收录」） |
| `detail` | 可选。`top_tissue` 时为英文全称；`value` 为短中文要闻大字（尽量 ≤8 汉字） |
| `as_of` | `YYYY-MM-DD`（location 项可省略） |

## `pathways[]`

```json
{"name": "…", "url": "https://www.kegg.jp/pathway/<id>"}
```

## `expression`

```json
{
  "source": "GTEx",
  "unit": "TPM",
  "caption_zh": "图 · GTEx 中位表达（TPM）· 多组织",
  "caption_en": "Fig. · GTEx median expression (TPM) · small multiples",
  "tissues": [{"name": "…", "name_zh": "…", "value": 0}]
}
```

| 字段 | 说明 |
|------|------|
| `caption_zh` / `caption_en` | 推荐。表达图短图注（挂在 `expression` 对象上，P3.5） |
| `name` | 英文组织名（GTEx 展示名） |
| `name_zh` | 中文展示标签（可读短名）；每项必填 |
| `value` | 中位 TPM |

P2：优先 GTEx Portal API v2 真实中位 TPM（前 8 组织）。失败时 `tissues: []`，headline `top_tissue.value` =「本期未收录」。**禁止** seed 假数。组织中文为展示映射，非 GTEx 官方字段。

## `structure`

```json
{
  "alphafold_url": "https://alphafold.ebi.ac.uk/entry/<UniProt>" | null,
  "preview_image": null,
  "caption_zh": "图 · AlphaFold 结构预测",
  "caption_en": "Fig. · AlphaFold structure prediction"
}
```

| 字段 | 说明 |
|------|------|
| `alphafold_url` | AlphaFold DB 条目；可 `null` |
| `preview_image` | 相对 `data/` 的预览图路径（如 `cache/alphafold/TP53.png`）；失败为 `null`（P3.6） |
| `caption_zh` / `caption_en` | 推荐。结构区短图注（挂在 `structure` 对象上，P3.5） |

## `variants_summary`

```json
{
  "clinvar_pathogenic": 0,
  "clinvar_likely_pathogenic": 0,
  "note_zh": "非诊断结论；计数来自 ClinVar E-utilities 检索，非正式导出 tar。"
}
```

P2：数值来自 NCBI `esearch` count（`{SYM}[gene] AND clinsig_pathogenic|likely_pathogenic[prop]`）。失败时字段可为 `null`，headline 写「本期未收录」。`sources` 中 ClinVar 条 `confidence` 为 `high` / `medium` / `unavailable`，**不再**使用 `seed`。

## `variants_detail`

本期可为空数组 `[]`（无逐条收录）。前端已有空态。

## `colophon`

```json
{
  "data_as_of": "2026-09-29",
  "edition": "0.3.1-p36",
  "disclaimer_zh": "科研/教学信息工具，非医疗器械，不提供诊断建议。"
}
```

`edition`：P3.6 改版为 `0.3.1-p36`（与 index / CSV 同源；含 cytoband / domains / preview）。`data_as_of`、`sources`、ClinVar 计数、坐标为**语言无关**字段，不双语化。

## `sources[]`

```json
{"name": "…", "url": "…", "version": "…", "confidence": "high|medium|unavailable", "note": "…"}
```

`note` 可选。`confidence` 取值：`high` | `medium` | `unavailable`（P2 真值后不再用 `seed`）。

## `confidence`

```json
{"identity": "high", "expression": "high", "clinvar": "high"}
```

分项可为 `high` / `medium` / `unavailable`。




## `cytoband`（P3.6）

基因位点钉到染色体带型骨架：

```json
{
  "chrom": "17",
  "start": 7661779,
  "end": 7687546,
  "assembly": "GRCh38",
  "band_label": "17p13.1",
  "figure_id": "cytobands/17.json"
}
```

| 字段 | 说明 |
|------|------|
| `chrom` / `start` / `end` / `assembly` | 与 `location` 对齐 |
| `band_label` | 细胞遗传学带标（通常同 headline location） |
| `figure_id` | 相对 `data/figures/` 的带型 JSON，如 `cytobands/17.json` |

带型文件：`data/figures/cytobands/{chrom}.json`，字段含 `chrom`、`assembly`、`bands[{id,start,end,stain}]`、`source`、`url`（UCSC cytoBandIdeo hg38）。

## `domains[]`（P3.6）

```json
{
  "id": "up:P04637:DNA binding:102-292",
  "name": "DNA-binding domain",
  "name_zh": "DNA 结合域",
  "start": 102,
  "end": 292,
  "source": "UniProt",
  "url": "https://www.uniprot.org/uniprotkb/P04637"
}
```

取 3–8 个代表性 UniProt features（Domain / DNA binding / Zinc finger / Region / Motif / Transmembrane 等）。失败或无条目时为 `[]`；`sources` 必须含 **UniProt domains** 条（`confidence` high/medium/unavailable）。`name_zh`：常见域中文，否则可与 `name` 相同。

## `structure.preview_image`（P3.6）

- 成功：相对 `data/` 路径，如 `cache/alphafold/TP53.png`（由 AlphaFold PDB CA 迹线渲染，或 PAE 静态图回退）。
- 失败：`null`；保留 `alphafold_url`；空态由前端处理。
- `sources` 保留/更新 **AlphaFold DB** 条。

## 双语字段（P3.5）

| 字段 | 语言 | 说明 |
|------|------|------|
| `deck_zh` / `deck_en` | 中 / 英 | 导语；前端按 `lang` 选用 |
| `expression.tissues[].name` / `name_zh` | 英 / 中 | 组织短名；图注长句可由前端字典拼 |
| `expression.caption_zh` / `caption_en` | 中 / 英 | 表达图短图注（推荐） |
| `structure.caption_zh` / `caption_en` | 中 / 英 | 结构图短图注（推荐） |
| `sources` / `data_as_of` / ClinVar 计数 / 坐标 | — | **语言无关**，不双语化 |

## `index.json` 目录条目（P3 / catalog_schema 1.0）

顶层：

| 字段 | 类型 | 说明 |
|------|------|------|
| `edition` | string | 与基因 `colophon.edition` 对齐（现 `0.3.1-p36`） |
| `data_as_of` | string | `YYYY-MM-DD`；取基因 colophon 最新值 |
| `count` | number | `genes.length` |
| `catalog_schema` | string | 目录条目 schema 版本，现 `"1.0"` |
| `genes` | object[] | 富化目录条目 |

每个 `genes[]` 条目：

| 字段 | 类型 | 必填 | 来源 / 说明 |
|------|------|------|-------------|
| `symbol` | string | ✓ | 基因 `symbol`；须与文件一致 |
| `id` | string | ✓ | 基因 `id`（Ensembl） |
| `file` | string | ✓ | 相对路径，如 `genes/TP53.json`（文件须存在） |
| `aliases` | string[] | ✓ | 基因 `aliases` |
| `type` | string | ✓ | 基因 `type` |
| `location_label` | string | ✓ | `headline_stats` 中 `key=location` 的 `value` |
| `clinvar_plp` | number\|null | ✓ | `key=clinvar_plp` 的数字 `value`；失败为 `null` |
| `top_tissue` | string | ✓ | `key=top_tissue` 的短中文 `value` |
| `top_tissue_detail` | string | 可选 | 同上 `detail`（英文全称） |
| `alphafold_url` | string\|null | ✓ | `structure.alphafold_url` |
| `data_as_of` | string | ✓ | `colophon.data_as_of` |
| `edition` | string | ✓ | `colophon.edition` |

```json
{
  "edition": "0.3.1-p36",
  "data_as_of": "2026-09-29",
  "count": 10,
  "catalog_schema": "1.0",
  "genes": [
    {
      "symbol": "TP53",
      "id": "ENSG00000141510",
      "file": "genes/TP53.json",
      "aliases": ["BCC7", "BMFS5", "LFS1", "P53", "TRP53"],
      "type": "protein_coding",
      "location_label": "17p13.1",
      "clinvar_plp": 1447,
      "top_tissue": "淋巴细胞",
      "top_tissue_detail": "Cells - EBV-transformed lymphocytes",
      "alphafold_url": "https://alphafold.ebi.ac.uk/entry/P04637",
      "data_as_of": "2026-09-29",
      "edition": "0.3.1-p36"
    }
  ]
}
```

由 `scripts/rebuild_catalog.py` 从 `genes/*.json` 重建。CSV 导出见 `CSV_EXPORT.md`。
