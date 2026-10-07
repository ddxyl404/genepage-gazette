# P4 Brief — 上线与运维（本机先行）

**锁定：** 2026-10-07 · 用户确认「进入下一阶段」→ 计划中的 **P4**。  
**前置：** P3.9（`0.3.3-p39`，demo3 小报）已三方收口。  
**约束：** 气质 C / 三色不变；科研教学非诊疗；本机 `/workspace/genepage` 为开发真相源；**禁云端 coding agent**。  
**分轨：** **P4a 本机可交付**（本 brief 立刻开工）→ **P4b 公网挂载**（等用户提供域名/主机/SSH 后再开）。

---

## P4a — 本机交付（本期）

### 1. edition 策略（总编定稿 · 数据落文）

| 规则 | 说明 |
|------|------|
| 主号 `0.MAJOR.MINOR-tag` | 现为 `0.3.3-p39` |
| 数据重同步（ClinVar/GTEx/MyGene 计数变） | 只动 `data_as_of`；**不**为日期硬改 edition，除非用户点名发刊 |
| 版式/结构改版（如 P3.x） | 总编写 brief → 数据统一 bump `edition` + rebuild catalog/CSV |
| 脚注 | Colophon / health / index 同源 |

产出：`docs/EDITION_POLICY.md`（数据主笔，总编过一眼）。

### 2. 数据 cron / 手工可复跑（数据主责）

- 文档化推荐周期：示范 10 基因建议 **每周** 或手动；命令：
  - `python3 data/scripts/sync_all.py`
  - `python3 data/scripts/sync_figures.py`（按需）
  - `python3 data/scripts/rebuild_catalog.py` + `export_csv.py`
- 提供本机 cron 示例（注释掉的 crontab 段写入 `docs/OPS_CRON.md`），**默认不装进系统**，等用户确认再启用。
- 失败策略：单源失败 →「本期未收录」；不阻断其它源；日志落 `data/cache/logs/`（若无则建）。
- `/api/cache/status` 保持可读；必要时补「上次成功同步时间」字段（有则写、无则跳过以免拖版式）。

### 3. 上游限额与礼貌（数据 + 工程）

- 在 `docs/OPS_RATE_LIMITS.md` 写清：MyGene / ClinVar / GTEx / AlphaFold 的已知礼貌间隔、重试上限、禁止并发打满。
- `sync_*.py` 已有 sleep/限速则核对；缺则最小补丁（数据改脚本，工程不改视觉）。
- 健康面：`GET /api/health` 继续回 edition + gene_count；可选加 `sync_ok`/`last_sync`（工程接字段，数据写值）。

### 4. 备份（工程主责）

- 脚本 `scripts/backup_data.sh`：打包 `data/genes`、`data/index.json`、`data/catalog*`、`data/cache` 元数据（体积大的 PNG 可 exclude 或可选），输出到 `backups/genepage-YYYYMMDD-HHMM.tgz`。
- README 增加「备份 / 恢复」两行命令。
- **不做**云盘自动上传，除非用户另嘱。

### 5. 部署文档与 Compose 加固（工程主责）

- README「生产注意」：反向代理、`NEXT_PUBLIC_API_URL`、只读数据卷、非 root、端口。
- `docker-compose.yml` 核对可作备份启动路径（本机无 Docker 不强制跑通，但文件保持可用）。
- 冒烟清单写入 `docs/OPS_SMOKE.md`：health、TP53 zh/en/print、CSV、figures。

### 6. 版式（轻量）

- **默认无改版面。** 仅当工程加了公开 `/ops` 或状态页时，用现有 token 做极简刊风状态条；否则不动 `page--p39`。

---

## P4b — 公网（阻塞：等用户）

需要用户提供至少一项后再开：

1. 主机（SSH / 面板）与部署目录  
2. 域名（或 IP）与是否已有证书  
3. 是否要自动 HTTPS（Caddy / nginx + Let’s Encrypt）

产出预期：公网 URL、HTTPS、定时同步、备份落盘路径。**本周不阻塞 P4a。**

---

## 明确不做（本期）

- 棒棒糖变异图、通路简图（仍属内容加厚，另开 brief）  
- 改配色 / 推翻 P3.9 bento  
- 诊疗话术、用户账户系统  

---

## 分工与验收

| 角色 | P4a 任务 |
|------|----------|
| **工程** | backup 脚本、README 生产段、OPS_SMOKE、Compose 注释；可选 health 字段接线 |
| **数据** | EDITION_POLICY、OPS_CRON、OPS_RATE_LIMITS；核对 sync 限速；必要时 last_sync |
| **版式** | 待命；无强制作图 |
| **总编** | 验收文档齐全 + 本机 backup dry-run + smoke；P4b 等域名 |

**验收：**

- [ ] 三份 ops 文档齐（edition / cron / rate limits）  
- [ ] `scripts/backup_data.sh` dry-run 产出 tgz  
- [ ] smoke 清单跑通；health 仍为 `0.3.3-p39`（除非另有发刊）  
- [ ] 频道回传：文档路径 + backup 样例文件名  

**edition：** P4a 文档与脚本 **默认不 bump**；保持 `0.3.3-p39`，除非同步结果需发刊由总编另令。
