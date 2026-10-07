# P3.7 排版重排 Brief — 表达水平条 + 通栏杂志 L1

**锁定：** 2026-09-30 · 用户确认：表达改**水平排行条（A）**；整页**通栏杂志 L1**。  
**约束：** 气质 C；三色不变；中英不变；图1/3/4（染色体、结构域、AF）保留；本机 only，禁云端。  
**edition：** 建议 UI 记号 `0.3.2-p37`（仅前端/刊头即可；数据无 schema 变更则可不强制改 genes edition，与总编确认后写刊头）。

---

## 目标

解决：图2 multiples 碎、难比；整页双栏抢戏、发挤不舒服。

验收（`/g/TP53?lang=zh|en` + print）：
1. 表达为水平排行条（组织名随语言，TPM 一位小数，按 TPM desc，top ≤12）。
2. 染色体 → 表达 → 结构域 → 结构为**通栏图栈**，图间留白充足。
3. 双栏仅用于身份 / 通路等文字；要闻三数可通栏或轻量横条，不与大图左右对打。
4. 行距、栏缝、图注明显疏于 P3.6；Print 不挤成一团。

---

## 版式（主责）

只改 `web/`（更新 FIGURE_CAPTION：图2 改为水平排行条）。

页面信息流建议：
1. Masthead + LangSwitch  
2. 基因大标题 + Deck  
3. 要闻三数（通栏）  
4. **短双栏**：左身份/命名 · 右通路节选（文字为主，勿塞大图）  
5. **通栏图栈**：图1 ChromIdeogram → 图2 ExpressionBars（新）→ 图3 DomainStrip → 图4 StructurePreview  
6. 变异摘要 + Colophon  

- 删除或停用拥挤的 ExpressionMultiples 作为默认。  
- ExpressionBars：铁锈红条、墨黑轴注、清晰图注 `caption_*`。  
- 加大 section 间距与 figure 上下 padding；避免双栏内塞图。

---

## 数据 / 工程

- 数据：无 schema 变更；现有 `expression.tissues` 足够。可选更新 caption 文案为「水平排行」语气（非必须）。  
- 工程：无新路由；确认 `:3000` 热更新即可。

---

## 不做

- Cleveland / 热力 / 再开 multiples 默认。  
- L2/L3、棒棒糖、通路简图、P4。
