# 刊号策略（Edition Policy）

**现行刊号：** `0.3.3-p39`  
**格式：** `0.MAJOR.MINOR-tag`（如 `0.3.3-p39`）  
**P4a 默认：** **不 bump**；保持 `0.3.3-p39`，除非总编/用户点名发刊。

## 何时动什么

| 场景 | 动作 |
|------|------|
| 数据重同步（ClinVar / GTEx / MyGene 计数变） | 只更新 `data_as_of`（及 cache `synced_at`）；**不**因日期硬改 edition |
| 版式 / 结构改版（P3.x 等） | 总编写 brief → 数据统一 bump `edition` → `rebuild_catalog.py` + `export_csv.py` |
| 用户/总编下令发刊 | 按 brief  bump；全库同源 |

## 同源要求

以下必须同一 `edition`：

- 各基因 JSON 的 `colophon.edition`
- `data/index.json`（及条目内 edition）
- `GET /api/health` 的 `edition`（读自 index）

改版时勿只改单文件；以 `rebuild_catalog.py` 从基因 JSON 重建 index/CSV 为准。

## 操作口令（改版时）

```bash
# 1. 按 brief 改基因 JSON / 脚本中的 EDITION 常量（仅在有发刊令时）
# 2. 重建目录与 CSV
python3 /workspace/genepage/data/scripts/rebuild_catalog.py
# （rebuild_catalog 已调用 export_csv；也可单独：）
# python3 /workspace/genepage/data/scripts/export_csv.py
```

日常同步请见 `OPS_CRON.md`；**不要**把 `sync_all.py` / `sync_figures.py` 内遗留的旧 EDITION 常量当现行刊号，发刊前须与总编对齐后再改。
