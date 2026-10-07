# P4b：Render.com Free 部署

GenePage Gazette 在 Render Free 上拆成两个 Web Service：`genepage-api`（FastAPI + 烤入 `data/`）与 `genepage-web`（Next.js standalone）。根目录 `render.yaml` 为 Blueprint。

> **不要**仅为部署单独 bump edition；edition 随数据/功能迭代，见 `docs/EDITION_POLICY.md`。

## 前置条件

1. 已有 Render 账号。
2. GitHub 仓库已推送本项目（含 `render.yaml`、`api/`、`web/`、`data/`）。
3. Render Dashboard → **Account / Settings → Git** 已连接该 GitHub 账号，并授权该仓库。

当前本地目录可能尚未绑定 remote；等 GitHub 就绪后再 push，再在 Render 选仓库。

## 方式 A：Blueprint（推荐）

1. Render Dashboard → **New** → **Blueprint**。
2. 选择 GitHub 上的 GenePage 仓库；Blueprint 路径默认 `render.yaml`。
3. 确认两个服务：
   - `genepage-api`（Docker，`./api/Dockerfile`，context `.`）
   - `genepage-web`（Docker，`./web/Dockerfile`，context `./web`）
4. **Apply**。等待首次构建（Free 可能较慢）。
5. 若服务名被占用，在 Blueprint 里改 `name`，并同步改：
   - `NEXT_PUBLIC_API_URL` → `https://<新 API 名>.onrender.com`
   - `GENEPAGE_CORS_ORIGINS` → `https://<新 Web 名>.onrender.com`
   改完后需 **清缓存重建** web 镜像（`NEXT_PUBLIC_*` 在 build 时写入）。

## 方式 B：手动两个 Web Service

### API

| 项 | 值 |
| --- | --- |
| Type | Web Service |
| Runtime | Docker |
| Dockerfile Path | `./api/Dockerfile` |
| Docker Context | `.`（仓库根） |
| Plan | Free |
| Region | Oregon（或 Singapore） |
| Health Check Path | `/api/health` |

环境变量见下表。

### Web

| 项 | 值 |
| --- | --- |
| Type | Web Service |
| Runtime | Docker |
| Dockerfile Path | `./web/Dockerfile` |
| Docker Context | `./web` |
| Plan | Free |
| Region | 与 API 同区 |

环境变量见下表。改 `NEXT_PUBLIC_API_URL` 后必须 **Rebuild**（非仅 Restart）。

## 环境变量

| 服务 | 变量 | 示例 / 说明 |
| --- | --- | --- |
| api | `GENEPAGE_DATA_DIR` | `/data`（镜像内烤入） |
| api | `GENEPAGE_CACHE_DIR` | `/data/cache` |
| api | `GENEPAGE_CORS_ORIGINS` | `https://genepage-web.onrender.com`（逗号分隔；自定义域一并加上） |
| api | `PORT` | `8000`（与 Dockerfile CMD 默认一致） |
| web | `NEXT_PUBLIC_API_URL` | `https://genepage-api.onrender.com`（**构建时**注入；Render 会把 env 当 Docker build ARG） |

说明：Blueprint 无独立 `dockerBuildArgs` 字段；Docker 服务的 `envVars` 会在 `docker build` 时作为 ARG 传入，并在运行时仍可用。

建议公网 URL（若名未被占用）：

- API：`https://genepage-api.onrender.com`
- Web：`https://genepage-web.onrender.com`

## 自定义域名（挂在 Web 服务）

假设域名已指向你要绑的站点（只绑 **web**，用户浏览器走 Next；`/api/*` 可由 Next rewrite 到 API，或浏览器直打 API 主机）。

1. Render → `genepage-web` → **Settings → Custom Domains** → 添加例如 `gazette.example.com`。
2. DNS 按 Dashboard 提示添加 **CNAME**：
   - 名称：`gazette`（或 `@` 若提供商支持 ALIAS/ANAME）
   - 目标：Render 给出的 `genepage-web.onrender.com`（以控制台文案为准）
3. 等待证书签发（通常数分钟到数十分钟）。
4. 若浏览器会跨域直调 API，把自定义源站加入 API 的 `GENEPAGE_CORS_ORIGINS`，例如：
   `https://genepage-web.onrender.com,https://gazette.example.com`
   然后重启 API。

API 也可单独绑域，但 P4b 默认只要求 Web 侧自定义域。

## 冒烟检查

部署完成后（注意 Free 冷启动可能要几十秒）：

| 检查 | URL |
| --- | --- |
| API 健康 | `https://genepage-api.onrender.com/api/health` |
| 基因页 | `https://genepage-web.onrender.com/g/TP53` |
| 印刷本 | `https://genepage-web.onrender.com/g/TP53/print` |
| CSV | `https://genepage-web.onrender.com/api/export/genes.csv` 或 API 同源路径 |

期望：`/api/health` 返回 `status: ok`，且 `gene_count` / `edition` 与烤入的 `data/index.json` 一致。

## 注意与限制

- **Free 休眠**：约 15 分钟无流量后休眠；唤醒有冷启动延迟。
- **无持久免费盘**：种子数据已 `COPY` 进 API 镜像；改 `data/` 需重新构建 API。
- **双 `.onrender.com` URL**：未绑自定义域前，Web 与 API 各一个子域。
- **CORS**：`web/src/lib/api.ts` 在设置了 `NEXT_PUBLIC_API_URL` 时会让浏览器直打 API 主机，故 API 需允许 Web 源站。
- **SSR**：Next 服务端同样用该 URL 拉 API，两服务须同区、均可公网互访。

## 不要做的事

- 不要为「只上 Render」单独改 edition / bump 版本号。
- 不要在 Free 上依赖可写 Disk 存种子 JSON。
- 不要把密钥写进 `render.yaml` 明文（本项目 P4b 无密钥需求）。
- 不要用云端 coding agent 改生产配置（P4 禁止）；在仓库内改 Blueprint 后走 Git 部署。

## 本地对照

```bash
# 与 Render 同一套 Dockerfile（仓库根 context）
docker compose up --build
```

Compose 仍用 `./data:/data:ro` 覆盖烤入层，便于本地改数据。详见根 `README.md`。
