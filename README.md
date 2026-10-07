# GenePage Gazette

新闻纸风基因「一页看懂」简报。P1–P3：FastAPI + Next.js，种子数据在 `data/`。

**配色：** paper `#F4F0E6` · ink `#1A1A1A` · rust `#8B3A2F`  
**免责：** 科研/教学信息工具，非医疗器械，不提供诊断建议。

## 数据真相源

- `data/genes/*.json` + `data/index.json`
- API 通过环境变量 `GENEPAGE_DATA_DIR`（默认 `/workspace/genepage/data`）只读该目录
- P2 cache 根目录由 `GENEPAGE_CACHE_DIR` 指定，默认 `/workspace/genepage/data/cache`；其中 `clinvar/`、`gtex/`、`mygene/` overlay 仅用于追溯、重跑和 `/api/cache/status`，不覆盖 API 的主读源
- **不要**把种子 JSON 复制进 `api/`

## 本地启动（不用 Docker）

### API（:8000）

```bash
cd api && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
export GENEPAGE_DATA_DIR=/workspace/genepage/data   # 可选；默认即此路径
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Web（:3000）

```bash
cd web && npm i && npm run dev
```

浏览器：

- 首页：http://127.0.0.1:3000/
- TP53：http://127.0.0.1:3000/g/TP53
- 健康检查：http://127.0.0.1:8000/api/health
- 基因 JSON：http://127.0.0.1:8000/api/gene/TP53
- 印刷本：http://127.0.0.1:3000/g/TP53/print
- CSV：http://127.0.0.1:8000/api/export/genes.csv

Next 将 `/api/*` rewrite 到 `http://127.0.0.1:8000`（可用 `NEXT_PUBLIC_API_URL` 覆盖）。

## P2 cache

P2 预告建立了 `data/cache/` 契约：基因 JSON 仍是唯一主数据源，缓存文件只做 Gazette 数据追溯、重跑和状态清单。数据侧会把真实数据或失败字段 `「本期未收录」` 合并回基因 JSON，API 原样透传；不会在没有 cache 文件时清除 P1 seed。


## P3（目录 / CSV / 印刷 / 性能）

- 首页 `/` 读 `/api/index`：展示 **edition**（当前 `0.2.0-p2`）、基因数、**下载 CSV**
- `/index` → 307 到 `/`（`next.config.mjs` redirects）
- CSV：`GET /api/export/genes.csv`（API 为真相源；Next `/api/*` rewrite 代理）
- 印刷本：`/g/{symbol}/print`（基因页 Masthead / Colophon 有「印刷本页」）
- 性能记录：[`docs/P3_PERF.md`](docs/P3_PERF.md)
- 基因页 `revalidate = 60`；首页因检索仍为 `force-dynamic`

浏览器补充：

- 印刷本：http://127.0.0.1:3000/g/TP53/print
- CSV：http://127.0.0.1:8000/api/export/genes.csv （或经 Next :3000 同路径）

## Docker Compose（Docker 可用时）

```bash
docker compose up --build
```

- web → http://localhost:3000
- api → http://localhost:8000
- `data/` 以只读卷挂到 API 的 `/data`（`GENEPAGE_DATA_DIR=/data`）


## Render（P4b）

Render.com Free 双 Web Service 部署（API 烤入 `data/`，无持久免费盘）见 [`docs/P4B_RENDER.md`](docs/P4B_RENDER.md)。仓库根目录 `render.yaml` 为 Blueprint；需先把 GitHub 仓库连到 Render 再 Apply。

## 目录

```
genepage/
  api/          FastAPI
  web/          Next.js App Router
  data/         种子基因（唯一真相源）
  frontend-mock/ 版式参考
  docs/         线框与 API 草案（含 P4B_RENDER.md）
  docker-compose.yml
  render.yaml   Render Blueprint（P4b Free）
```

## 生产注意

- **反向代理：** 公网时用 Caddy / nginx 终结 HTTPS，把 `/` 转到 web `:3000`，必要时把 `/api` 转到 api `:8000`（或仍走 Next rewrite）。
- **`NEXT_PUBLIC_API_URL`：** 浏览器可达的 API 根；Compose 内默认 `http://api:8000`。本机 `npm run dev` 可不设（Next rewrite → `127.0.0.1:8000`）。
- **数据卷只读：** Compose 已将 `./data` 挂到 API `/data:ro`；生产勿以可写挂载覆盖种子。
- **非 root：** 容器内以非 root 跑（Dockerfile / 运行用户自行约束）；宿主机备份脚本普通用户即可。
- **端口：** API `8000` · Web `3000`。本机 box 上 Docker 可能未装；Compose 仍是生产备用启动路径。

## 备份 / 恢复

`backups/` 为本地归档目录（含 `.gitkeep`），默认不提交大 tgz。

```bash
# 精简备份（默认排除 alphafold PNG/webp/pdb）
./scripts/backup_data.sh

# 含结构图等大文件
./scripts/backup_data.sh --with-figures

# 验收 smoke（仍产出 backups/*.tgz）
./scripts/backup_data.sh --dry-run
```

归档落在 `backups/genepage-YYYYMMDD-HHMM.tgz`。恢复示例：

```bash
tar -xzf backups/genepage-YYYYMMDD-HHMM.tgz -C /path/to/genepage
# 或解到临时目录后核对再拷入 data/
```

冒烟清单见 [`docs/OPS_SMOKE.md`](docs/OPS_SMOKE.md)。
