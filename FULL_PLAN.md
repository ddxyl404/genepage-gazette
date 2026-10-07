# GenePage Gazette — 完整项目计划（多 Bot 分工）

**刊名：** GenePage Gazette（副标：基因简报）  
**气质：** C 档（报头晨报 + 内文季刊留白）  
**配色：** 新闻纸 `#F4F0E6` · 墨黑 `#1A1A1A` · 铁锈红 `#8B3A2F`  
**目标：** 可上线的基因「一页看懂」工具；可视化与可读性优先；差异化靠期刊叙事版式。

---

## 1. 成功标准

1. 打开 `/g/TP53` 即见完整简报页（报头、导语、要闻三数、双栏、变异摘要、报尾）。  
2. Docker Compose 一键起前后端；有公开演示 URL 或内网地址。  
3. 每张卡片可追溯数据源与 `data_as_of`；页脚有非诊疗声明。  
4. 视觉一眼可辨 newsprint，而非通用 SaaS 后台。  
5. 至少 10 个示范基因可离线/缓存快速打开。

---

## 2. 分期路线图

### P0 — 规格冻结（已完成大半）
- [x] 产品定位、C 档气质、刊名与铁锈红配色  
- [x] 线框 + `/api/gene/{id}` 字段草案  
- [ ] 本计划与 Bot 分工确认  

### P1 — 可演示骨架（约 1 周）
- Next.js 前端：首页搜索 + TP53 静态/半静态简报页（先 mock 数据跑通版式）  
- FastAPI：`/api/gene/{id}`、`/api/search`；种子 JSON（10 基因）  
- Docker Compose；README（许可与免责声明）  
- **验收：** 本地或服务器打开即有 newsprint 观感的 TP53 页  

### P2 — 真实数据接入（约 1–2 周）
- MyGene / Ensembl 身份与别名  
- 表达：GTEx 汇总缓存（预计算，不每次打满 API）  
- ClinVar 摘要计数（子集同步）  
- AlphaFold / PDB 外链 + 可选预览图  
- Redis/SQLite 缓存；失败降级文案「本期未收录」  
- **验收：** 随机抽 5 个常见基因，卡片均有出处  

### P3 — 差异化打磨（约 1 周）
- 图注规范、要闻数字排印、Print/PDF 一页纸（可选）  
- 批量基因目录页（Index）+ CSV 导出  
- 性能：首屏 < 2s（缓存命中）  
- **验收：** 截图可当汇报附页；同事能 1 分钟内看懂  

### P4 — 上线与运维（进行中 · 2026-10-07）
- Brief：`docs/P4_OPS_BRIEF.md`（**P4a 本机**先行；**P4b 公网**等域名/主机）  
- 备份、数据更新 cron 文档、限额与 edition 策略  
- 域名 / HTTPS：阻塞项，见 P4b  

---

## 3. 技术架构（摘要）

```
Browser (Next.js, newsprint CSS)
    → FastAPI
        → 本地种子 / SQLite 缓存
        → 上游：MyGene, GTEx 汇总, ClinVar 子集, AlphaFold 链接
Docker Compose: web + api + redis(optional)
```

许可隔离：只缓存允许再分发或按条款使用的公开数据；页面标注版本与用途（科研/教学，非诊断）。

---

## 4. 多 Bot 分工（建议创建 4 个专职 + 你现有 Grok Bot 做总控）

| Bot 名称 | 职责 | 主要产出 | 不做什么 |
|----------|------|----------|----------|
| **Gazette 总编**（可即本助手） | 需求、排期、验收、跨 Bot 协调 | 计划更新、验收清单、对用户汇报 | 不深陷写所有代码 |
| **Gazette 版式** | newsprint CSS、组件、线框落地、可读性 | 前端版式、设计 token、静态视觉页 | 不接上游生信 API |
| **Gazette 数据** | schema、种子基因、上游同步与缓存 | `data/`、同步脚本、出处字段 | 不改视觉 |
| **Gazette 工程** | FastAPI、Docker、部署、CI | 可运行仓库、compose、上线 | 不擅自改产品叙事 |
| **Gazette 审校**（可选） | 生物学表述、免责声明、抽检基因页 | 问题列表、文案修正 | 不写功能代码 |

协作约定：
- 总编下发「本期任务」到对应 Bot；各 Bot 做完在共享频道或私聊回传结果。  
- 唯一事实源：`/workspace/genepage/` 下的 `DESIGN_BRIEF.md`、`WIREFRAME_AND_API.md`、本 `FULL_PLAN.md`。  
- 代码进统一仓库（云端 Origin/Git）；禁止各 Bot 各建一套互不兼容的栈。

---

## 5. 近期任务拆解（P1）

1. **版式 Bot：** 按 C + 铁锈红实现 Masthead / Deck / 要闻 / 双栏组件；先用 mock TP53。  
2. **数据 Bot：** 落 10 基因种子 JSON，字段对齐 API 草案。  
3. **工程 Bot：** FastAPI + Next.js monorepo 或双目录 + Docker Compose。  
4. **总编：** 联调验收、对照成功标准打勾。  

---

## 6. 风险

| 风险 | 对策 |
|------|------|
| 上游 API 限流/条款 | 预缓存示范基因；标注来源；可切换 mock |
| 版式与功能抢工期 | P1 强制 mock 先看版式 |
| 多 Bot 重复劳动 | 总编唯一派活；共享计划文档 |
| 「像诊断工具」误解 | 固定 Colophon 免责声明 |

---

## 7. 你需要拍板的仅剩

1. 是否按上表创建专职 Bot（建议先建：版式、数据、工程；审校可后补）。  
2. 代码放 Cursor Origin 新仓库，还是你已有 GitHub（若有请给地址）。  

确认后：总编写好各 Bot 人设 → CreateAgent → 建协作频道 → 按 P1 派第一周任务。
