# 图注规范（P3 → P3.9）

期刊口吻，短而可引。图注挂在图/块下方，不进要闻数字本身。

## 结构
`图 N · 短标题` + 一句说明（单位、来源、局限）。

数据字段优先：`expression.caption_zh|caption_en`、`structure.caption_zh|caption_en`。  
前端字典仅作缺字段时的回落。

## 要写清
- **单位**（如 TPM）
- **来源**（GTEx 本机汇总 / ClinVar / AlphaFold）
- **标签策略**：表达条按语言选 `name_zh`（zh）或 `name`（en）
- **空态**：写「本期未收录…」或「本期未附结构图」，不露内部字段名

## 不要写
- 「种子数据 / 待 P2 / 正式版将…」等工程进度语（已上线真数后）
- 把长英文组织名塞进要闻大字

## 现用（P3.9 版面图序）

P3.9 取消桌面粘性右轨，改为页首「封面故事 + 本期目录」分栏、通栏引语拉条，主内容通宽；图序仍为染色体 → 表达条 → 结构域 → AlphaFold（组件与图注编号不变）。

## 曾用（P3.8 版面图序）

P3.8 屏幕版为 **主栏≈2/3 + 粘性侧栏≈1/3（L2）**：要闻三数浓缩进侧栏；主栏仍为导语 → 短双栏（身份/通路）→ **通栏图栈** → 变异。印刷本无粘性侧栏，主栏通栏；图序与组件不变。

屏幕版与印刷本页（`/g/{SYMBOL}` 与 `/g/{SYMBOL}/print`）同一套四图，放在**通栏图栈**（`figure-stack`）内，不再与身份/通路双栏左右对打。

页面信息流：刊头 → 导语 → 要闻三数（通栏）→ **短双栏**（左身份/命名 · 右通路节选，仅文字）→ **通栏图栈** → 变异摘要 → 刊尾。

- **图 1 · 染色体带型** — `ChromIdeogram`（`chrom-ideogram`）。带型取 `GET /api/figures/cytobands/{chrom}`（如 TP53 → `17.json`）；基因 JSON `cytoband.band_label` 作位点名（TP53 为 `17p13.1`），钉用 `location.start/end` 中点，铁锈红。无带型文件时简版深浅墨条，仍可见。
- **图 2 · 组织表达（水平排行条）** — `ExpressionBars`（`expr-bars`）。`expression.tissues` 按 TPM 降序，最多 12；组织名随语言（`name_zh` / `name`）；TPM 一位小数；铁锈红条、墨黑轴注。图注优先 `expression.caption_zh|en`。不再以 `ExpressionMultiples`（`expr-multiples`）为默认主图。
- **图 3 · 蛋白结构域** — `DomainStrip`（`domain-strip`）。`domains[]`（name / name_zh / start / end / source）。色板仅墨、灰、一道铁锈红。空数组或缺字段：本期未收录 / Not in this edition。
- **图 4 · 结构预览** — `StructurePreview`（`structure-preview`）。`structure.preview_image` 有值时 `<img src="/api/figures/alphafold/{SYMBOL}">`（不要把 `cache/alphafold/….png` 当 src）。`null`（如 BRCA2）为空态 + AlphaFold 外链。图注优先 `structure.caption_zh|en`。

数据 edition 仍可来自 colophon（如 `0.3.1-p36`）；版式记号写在页脚（Style C · P3.9；P3.8 及更早见曾用）。数据 edition 可仍为 colophon（如 `0.3.2-p38`），勿为改刊头硬改 JSON。UI 刊头可不硬改数据 edition。

0.3.1-p36 数据图注写成「图 · …」「Fig. · …」（编号留空）。前端按上列图序填入编号；若数据已自带数字则不改写。

## 曾用（P3.6，已替换为通栏图栈）
- 左栏图 1、右栏自上而下图 2–4 的双栏塞图版面。图 2 曾为 small multiples（`expr-multiples`）。

## 曾用（P3.5）
- 单条表达排行与染色体标尺不再作为主图。`ChromRuler` 仅作 `ChromIdeogram` 别名。

## 印刷
- 屏幕版：`/g/{SYMBOL}?lang=zh|en` → 「印刷本页」进入 `/g/{SYMBOL}/print?lang=…`
- 印刷本页用 `PrintBar` 调起浏览器打印；`@media print`（A4）隐藏 `.no-print` / 工具条 / `lang-switch` / 搜索
- 变异 `<details>`：屏幕可折叠；print CSS 强制显示明细
- Print 图栈加大间距，勿挤成一团
