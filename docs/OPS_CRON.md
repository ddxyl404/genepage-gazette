# 运维 · 定时同步（Cron）

示范 10 基因建议 **每周一次** 或 **手动**；默认 **不** 装进系统 crontab，仅文档备查。时区：**Asia/Shanghai**。

## 推荐命令（绝对路径）

在 `/workspace/genepage` 下：

```bash
cd /workspace/genepage
python3 /workspace/genepage/data/scripts/sync_all.py
# 结构图 / UniProt / AlphaFold 按需：
python3 /workspace/genepage/data/scripts/sync_figures.py
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
# rebuild_catalog 已内调 export_csv，写出 exports/genes_catalog.csv；
# 若只想重导 CSV：
# python3 /workspace/genepage/data/scripts/export_csv.py
```

可选子集：`SYNC_SYMBOLS=TP53,BRCA1 python3 .../sync_all.py`

## 失败策略

- **单源失败** → 该源在基因页按「本期未收录」/ unavailable；**不阻断**其它源。
- `sync_all` 按基因顺序串行拉 MyGene → GTEx → ClinVar；单基因某源 fail 仍写盘并继续下一基因。
- 日志目录：`data/cache/logs/`（缺则建；可重定向 stdout，或看 `sync_all-YYYYMMDD.log` 一行摘要）。

## 可读状态

- `data/cache/meta.json` 含 `synced_at`（Asia/Shanghai ISO）、`data_as_of`、`summary`。
- `GET /api/cache/status`：回 cache 目录、各 overlay 符号列表、`meta.present` / `meta.path`（**不**自动展开 meta 全文；勿臆造 API 字段）。
- `GET /api/health`：`edition`、`data_as_of`、`gene_count`。

日常重同步默认 **不 bump edition**（见 `EDITION_POLICY.md`）。

## 示例 crontab（默认全部注释，勿直接安装）

```cron
# GenePage Gazette — demo 10 genes, Asia/Shanghai
# SHELL=/bin/bash
# CRON_TZ=Asia/Shanghai
# 每周一 03:30：同步数据 + 重建目录（figures 按需另跑）
# 30 3 * * 1 cd /workspace/genepage && python3 data/scripts/sync_all.py >> data/cache/logs/cron-sync_all.log 2>&1 && python3 data/scripts/rebuild_catalog.py >> data/cache/logs/cron-rebuild.log 2>&1
# 每月 1 日 04:00：figures（可选）
# 0 4 1 * * cd /workspace/genepage && python3 data/scripts/sync_figures.py >> data/cache/logs/cron-figures.log 2>&1 && python3 data/scripts/rebuild_catalog.py >> data/cache/logs/cron-rebuild.log 2>&1
```

启用前须用户确认；一次只跑一个 sync 进程（见 `OPS_RATE_LIMITS.md`）。
