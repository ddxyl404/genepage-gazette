# P3.9 Brief — 小报 bento（C / demo3）

**锁定：** 2026-10-07 · 用户确认参考图 **demo3**（editorial tabloid bento）「就很不错」。  
**问题：** P3.8 主栏+粘性侧栏在「滑过目录后」右侧显得空、几栏不协调。  
**约束：** 气质 C；三色不变（`#F4F0E6` / `#1A1A1A` / `#8B3A2F`）；中英与 i18n 不变；本机 `/workspace/genepage` only，禁云端。  
**参考图：** `docs/layout-refs/03-editorial-tabloid-bento.png`（及同目录其它对照；实现以 03 为准）。  
**不做：** 回到纯 sticky 空轨当主解；弹跳/视差/霓虹/轮播；改配色叙事；动上游 API 字段（除非文案键）。

---

## 版面方向（相对 P3.8）

弱化「右 1/3 粘性空轨」，改 **页首期刊分栏 + 通栏压空 + 下半 bento/通栏图栈**。

1. **报头（masthead）**  
   - 保留晨报报头；可略加重墨底/卷期感（vol · edition · data_as_of），对齐 demo3 黑条报头气质，仍用现有三色。

2. **页首「本期 / In this issue」面板（核心）**  
   - 报头下、主内容前：左大 deck（符号 + 导语），右 **本期目录**（编号锚点：要闻 / 基因组 / 表达 / 蛋白 / 结构 / 变异；中英随 `lang`）。  
   - 同区可嵌 **要闻三数**（染色体带、ClinVar P/LP、顶尖组织 TPM）——像 demo3 的 TOC 栏，而不是滑走后空掉的 sticky 轨。  
   - 目录点击平滑滚到现有锚点（`#lede` / `#cyto` / `#expression` / `#domains` / `#structure` / `#variants`，可微调）。

3. **通栏拉条（文武线 / pull band）**  
   - 页首区与图栈之间（或身份短文后）加一条全宽拉条：短句可用 deck 首句或固定刊头句；锈红强调少量斜体即可。  
   - 用途：把下半「空」压住，像 demo3 的 quote ribbon。

4. **主内容流**  
   - 身份/通路短双栏可保留。  
   - 图栈通栏保留（染色体 → 表达条 → 结构域 → AlphaFold）。  
   - 变异表通栏。  
   - 可选：下半用浅 bento 分块（图/表各一格），但勿碎成仪表盘；优先可读。

5. **侧栏 GeneRail**  
   - **桌面：去掉或降级 sticky 右轨**（默认隐藏桌面 sticky `GeneRail`；窄屏可保留顶折叠 TOC）。  
   - 若必须留边栏：仅作「外链 / 印刷 / 语言」薄条，不得再出现大块空轨。  
   - Print：静态「本期目录」即可，无 sticky。

6. **动效**  
   - 沿用 P3.8 克制 fade；尊重 `prefers-reduced-motion`。不加新花活。

---

## 标记与版本

- 页面 class：`page--p39`（可暂并存读 `page--p38` 样式再收敛）。  
- `edition` → `0.3.3-p39`（index + 各基因 colophon；数据同学批量改）。  
- 验收路径：`/g/TP53?lang=zh` · `?lang=en` · `/g/TP53/print?lang=zh`。

---

## 分工

| 角色 | 职责 |
|------|------|
| **版式（主责）** | 按本 brief 重排 `page.tsx` / `gazette.css` / 相关组件；新增页首 IssueToc（或等价）；处理通栏拉条；收敛 GeneRail。对照 `docs/layout-refs/03-editorial-tabloid-bento.png`。 |
| **数据** | `edition` → `0.3.3-p39`；必要时补 TOC/拉条用文案键（优先前端 i18n，能不改种子就不改）。 |
| **工程** | 冒烟 zh/en/print；确认 API health；不改三色与图路由。 |

---

## 验收清单

- [ ] 桌面宽屏：页首可见「本期目录」+ 要闻三数；**无**长页中段右侧大块空白轨  
- [ ] 目录锚点可跳；滚读时主栏饱满（拉条 + 通栏图）  
- [ ] 窄屏不碎；print 无 sticky  
- [ ] 中英切换仍通；气质仍为新闻纸 + 铁锈红  
