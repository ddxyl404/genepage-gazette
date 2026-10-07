# P3.6 图示加厚 Brief — 染色体 / 结构域 / small multiples / AlphaFold 预览

**锁定：** 2026-09-30 · 用户确认本轮：1 染色体带型、2 蛋白结构域条、4 表达 small multiples、5 AlphaFold 静态预览。  
**不做本轮：** 3 变异棒棒糖、6 通路简图（二期）。  
**约束：** 气质 C；三色不变；中英 `caption_zh|en`；非诊疗；本机 `/workspace/genepage` only，禁云端。  
**edition：** 建议合并后 `0.3.1-p36`（写入前频道确认一句）。

---

## 验收

以 `/g/TP53?lang=zh` 与 `?lang=en` 为准：
1. 可见染色体带型图 + 基因位点钉 + 图注。
2. 可见蛋白结构域条（有数据）或「本期未收录」空态。
3. 表达区为 small multiples（或明确升级后的多组织小图），不止单条排行。
4. 结构区有 AlphaFold 静态预览图（有缓存）或期刊口吻空态 + 外链。
5. Print 页同样带上述图（可略压缩），语言跟随。

---

## 数据（Gazette 数据）

1. **染色体带型**  
   - `data/figures/cytobands/{chr}.json`（或 SVG）骨架；基因 JSON 用现有 `location`（chrom/start/end）钉位点。  
   - 字段建议：`cytoband: { chrom, start, end, assembly, band_label?, figure_id }`。

2. **结构域**  
   - `domains: [{ id, name, name_zh?, start, end, source, url? }]`；无则空数组 + 空态文案键。  
   - 来源优先 UniProt/InterPro/Pfam 公开摘要；必须进 `sources`。

3. **表达**  
   - 现有 `expression.tissues[]` 足够；约定排序（TPM desc）、截断（如 top 8–12）、`caption_zh|en` 更新为 Fig. 表达 multiples。

4. **AlphaFold 预览**  
   - 脚本下载静态图 → `data/cache/alphafold/{SYMBOL}.png`（或 `.webp`）。  
   - JSON：`structure.preview_image`（相对路径或 API 静态 URL）、保留 `alphafold_url`。  
   - 失败：`preview_image: null`，文案「本期未收录预览图」。

脚本与 README 回频道；跑通 10 基因或至少 TP53+BRCA1 示范均可，优先 10/10。

---

## 版式（Gazette 版式）

只改 `web/`（必要时 FIGURE_CAPTION / DESIGN_BRIEF 增量）。

- **ChromIdeogram**：替换/升级现 ChromRuler 为带型图 + 位点钉，铁锈红钉、墨黑带。  
- **DomainStrip**：水平色带 + 图例（印刷色板：墨/灰/一道锈红，忌彩虹）。  
- **ExpressionMultiples**：小 multiples 网格；组织名随 lang（`name_zh` / `name`）。  
- **StructurePreview**：预览图 + 外链；无图空态。  
- 图序与图注：更新 `docs/FIGURE_CAPTION.md`（图1 染色体 / 图2 表达 / 图3 结构域 / 图4 结构…以实际版面为准写清）。  
- Print：四图可缩放但不丢。

---

## 工程（Gazette 工程）

- API 透传新字段；静态预览图可挂 `GET /api/figures/...` 或 Next `public`/`rewrites` 读 `data/cache/alphafold`。  
- 不改三色与非诊疗；保持 `:8000`/`:3000`。  
- 短文档 `docs/P36_FIGURES.md`（路径约定一页）。

---

## 顺序

1. 数据出 schema + TP53 样例字段/图文件。  
2. 工程透传与静态图路由。  
3. 版式四组件落地。  
4. 总编联调 zh/en/print。
