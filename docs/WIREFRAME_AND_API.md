# GenePage Gazette — 线框与 API（C 档定稿）

## 路由

| 路径 | 用途 |
|------|------|
| `/` | 刊头首页 + 搜索 + 示范基因目录 |
| `/g/{symbol}` | 基因简报页（主产品） |
| `/api/gene/{id}` | JSON：符号或 Ensembl ID |
| `/api/search?q=` | 联想搜索 |

## 基因页线框（自上而下）

```
┌─────────────────────────────────────────────┐
│ MASTHEAD  基因简报 · Vol.preview · 数据截至  │
│ ════════════════ 双线 ════════════════════ │
│  TP53                         [搜索]        │
│  别名：…  ·  17p13.1  ·  protein编码            │
├─────────────────────────────────────────────┤
│ DECK 导语（2–3 句人话）                       │
├──────────────┬──────────────┬───────────────┤
│ 要闻数字 1    │ 要闻数字 2    │ 要闻数字 3     │
│ 位置          │ ClinVar P/LP │ 最高表达组织   │
├──────────────┴──────────────┴───────────────┤
│ 左栏（季刊留白）      │ 右栏                   │
│ 身份 / 命名           │ 表达图 + 图注          │
│ 通路短列表 + 外链     │ 结构缩略 + AlphaFold   │
├─────────────────────────────────────────────┤
│ 变异摘要表（可扫读）+ 脚注                     │
├─────────────────────────────────────────────┤
│ COLOPHON 许可 · 非诊疗声明 · API · 版次        │
└─────────────────────────────────────────────┘
```

## `GET /api/gene/{id}` 字段（MVP）

```json
{
  "id": "ENSG00000141510",
  "symbol": "TP53",
  "aliases": ["p53"],
  "type": "protein_coding",
  "location": {"chrom": "17", "start": 7661779, "end": 7687550, "assembly": "GRCh38"},
  "deck_zh": "编辑导语…",
  "headline_stats": [
    {"key": "location", "label_zh": "基因组位置", "value": "17p13.1"},
    {"key": "clinvar_plp", "label_zh": "ClinVar 致病/可能致病", "value": 0, "as_of": "2026-09-01"},
    {"key": "top_tissue", "label_zh": "GTEx 最高表达", "value": "…", "as_of": "…"}
  ],
  "pathways": [{"name": "…", "url": "…"}],
  "expression": {"source": "GTEx", "unit": "TPM", "tissues": [{"name": "…", "value": 0}]},
  "structure": {"alphafold_url": "…", "preview_image": null},
  "variants_summary": {"clinvar_pathogenic": 0, "clinvar_likely_pathogenic": 0, "note_zh": "非诊断结论"},
  "colophon": {"data_as_of": "2026-09-29", "edition": "0.1.0-preview", "disclaimer_zh": "科研/教学信息工具，非医疗器械，不提供诊断建议。"},
  "sources": [{"name": "…", "url": "…", "version": "…"}]
}
```

## 前端实现提示（C 档）

- Masthead + 要闻：稍紧、细双线、大号衬线数字  
- Deck 与双栏正文：最大宽度约 42rem，行高宽松  
- 图表：印刷色板（黑/灰 + 一道墨蓝或锈红）
