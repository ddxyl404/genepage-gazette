# P4b：Koyeb 部署（推荐）

GenePage Gazette 在 Koyeb 上拆成 **两个 App / 两个 Web Service**：`genepage-api`（FastAPI + 烤入 `data/`）与 `genepage-web`（Next.js standalone）。仓库根目录提供 CLI 参考配置：

- `koyeb-compose.api.yaml` → App `genepage-api` / Service `genepage-api`
- `koyeb-compose.web.yaml` → App `genepage-web` / Service `genepage-web`

必须分成两个 App：每个 App 只有一个 `*.koyeb.app` 公网域名；API 与 Web 需要各自独立主机名（浏览器直打 API + CORS），与 Render 双 `.onrender.com` 同构。

> **不要**仅为部署单独 bump edition；edition 随数据/功能迭代，见 `docs/EDITION_POLICY.md`。当前 edition 保持 `0.3.3-p39`，不做 Style C 版式改动。

## 为何选 Koyeb（相对 Render）

- Render Free Blueprint 现常要求绑卡；本仓库仍保留 `render.yaml` / `docs/P4B_RENDER.md` 作 **备选**。
- Koyeb 支持从 GitHub 用 **Dockerfile** 构建，并提供组织级 **1 个 forever-free Web Instance**（512MB RAM / 0.1 vCPU / 2GB SSD）。

## 免费档硬限制（必读）

| 项 | 说明 |
| --- | --- |
| Free Instance 数量 | **每个组织仅 1 个** `free` Web Service |
| 规格 | 512MB RAM · 0.1 vCPU · 2GB SSD |
| 可用区 | 仅 **Frankfurt (`fra`)** 或 **Washington, D.C. (`was`)** |
| 休眠 | 约 **1 小时无流量**后 scale-to-zero（不可关、不可改空闲时长） |
| 冷启动 | Deep Sleep 唤醒约 **1–5 秒** |
| 不可用 | Worker、自定义 Scaling、Volumes（无持久盘） |
| 第二个服务 | 需付费 Instance（建议 `eco-nano` ≈ \$1.61/月，或 `eco-micro` ≈ \$2.68/月）；付费资源通常要支付方式 |

**推荐分配：** Web 用 `free`（512MB，Next 更吃内存）；API 用 `eco-nano` / `eco-micro`（FastAPI + 烤入只读数据更轻）。若坚持双服务且零费用，只能另开第二个 Koyeb 组织占用第二个 free（不推荐），或改用「单容器 Compose」自托管双进程（见文末备选）。

## 前置条件

1. 已有 Koyeb 账号并登录控制台。
2. GitHub 仓库 `ddxyl404/genepage-gazette`（`main`）已含本仓库 Docker / 配置文件。
3. Koyeb → 连接 GitHub：安装 Koyeb GitHub App，授权该仓库（或粘贴 **Public GitHub repository** URL；公开仓自动部署可能关闭，需手动 Redeploy）。

## 公网 URL 形态

Koyeb 给每个 App 一个子域（HTTPS 自动）：

```text
https://<APP_NAME>-<YOUR_ORG_SLUG>.koyeb.app
```

示例（组织 slug 以控制台为准）：

- API：`https://genepage-api-<YOUR_ORG_SLUG>.koyeb.app`
- Web：`https://genepage-web-<YOUR_ORG_SLUG>.koyeb.app`

**首次部署后**到各 App Overview 复制真实 Public URL，再回填：

- Web 的 `NEXT_PUBLIC_API_URL` → API 公网根（**构建时**写入；改完必须 **Deploy with build**）
- API 的 `GENEPAGE_CORS_ORIGINS` → Web 公网根（可逗号追加自定义域）

仓库里 compose 文件用占位符 `YOUR_ORG_SLUG`，部署前或首次部署后务必替换。

## 方式 A：控制台手动创建（推荐，与文档逐步对应）

### 1）创建 API：`genepage-api`

1. Overview → **Create Web Service** → **GitHub**。
2. 选仓库 `ddxyl404/genepage-gazette`（或粘贴 `https://github.com/ddxyl404/genepage-gazette`），分支 `main`。
3. Builder：**Dockerfile**。
4. 覆盖项：
   - **Dockerfile location**：`api/Dockerfile`
   - **Work directory**：留空（仓库根）。API 镜像需同时看到 `api/` 与 `data/`；若把 workdir 设成 `api/`，烤入 `data/` 会失败。
5. Instance：第二个服务建议 **`eco-nano`**（或 `eco-micro`）；若这是组织里 **唯一** 服务且想零费用，可选 **`free`**（fra / was）。
6. Region：与 Web 同区（`fra` 或 `was`）。
7. Exposed ports：`8000` · HTTP；Route：`/` → `8000`。
8. Health check（HTTP）：path `/api/health`，port `8000`；冷启动可把 grace 调大（如 60–120s）。
9. App / Service 名称均设为 **`genepage-api`**。
10. 环境变量见下表 → **Deploy**。

### 2）创建 Web：`genepage-web`

1. 再开一次 **Create Web Service** → GitHub → 同一仓库 / `main`。
2. Builder：**Dockerfile**。
3. 覆盖项：
   - **Work directory**：`web`（monorepo：构建环境只含该子目录）
   - **Dockerfile location**：`Dockerfile`（相对 workdir，即 `web/Dockerfile`）
4. Instance：建议把组织的 **`free`** 留给 Web（512MB）。
5. Region：与 API 相同。
6. Exposed ports：`3000` · HTTP；Route：`/` → `3000`。
7. App / Service 名称均设为 **`genepage-web`**。
8. 先填占位 `NEXT_PUBLIC_API_URL`（见下表）→ Deploy。
9. API / Web 都 Healthy 后：把双方真实 `*.koyeb.app` URL 写回环境变量；**Web 必须 Deploy with build**（`NEXT_PUBLIC_*` 在 `npm run build` 时烘焙）；API 改 CORS 后 Redeploy（可不重建镜像）。

## 方式 B：Koyeb CLI + compose 文件

```bash
# 安装 CLI 后登录：https://www.koyeb.com/docs/build-and-deploy/cli
# 先把两个 yaml 里的 YOUR_ORG_SLUG 换成控制台组织段（若尚未部署，可先用占位部署 API，再按真实 URL 改 Web）

koyeb compose ./koyeb-compose.api.yaml
koyeb compose ./koyeb-compose.web.yaml
```

compose 会创建/更新对应 App 与 Service。改 env 后对 Web 执行带 rebuild 的 redeploy。

等价的单服务 `app init` 示例（API）：

```bash
koyeb app init genepage-api \
  --git github.com/ddxyl404/genepage-gazette \
  --git-branch main \
  --git-builder docker \
  --git-docker-dockerfile api/Dockerfile \
  --ports 8000:http \
  --routes /:8000 \
  --regions fra \
  --instance-type eco-nano \
  --env GENEPAGE_DATA_DIR=/data \
  --env GENEPAGE_CACHE_DIR=/data/cache \
  --env GENEPAGE_CORS_ORIGINS=https://genepage-web-YOUR_ORG_SLUG.koyeb.app \
  --env PORT=8000
```

Web（workdir=`web`）：

```bash
koyeb app init genepage-web \
  --git github.com/ddxyl404/genepage-gazette \
  --git-branch main \
  --git-builder docker \
  --git-workdir web \
  --git-docker-dockerfile Dockerfile \
  --ports 3000:http \
  --routes /:3000 \
  --regions fra \
  --instance-type free \
  --env NEXT_PUBLIC_API_URL=https://genepage-api-YOUR_ORG_SLUG.koyeb.app
```

## 环境变量

| 服务 | 变量 | 示例 / 说明 |
| --- | --- | --- |
| api | `GENEPAGE_DATA_DIR` | `/data`（镜像内烤入） |
| api | `GENEPAGE_CACHE_DIR` | `/data/cache` |
| api | `GENEPAGE_CORS_ORIGINS` | `https://genepage-web-<ORG>.koyeb.app`（逗号分隔；自定义域一并加上） |
| api | `PORT` | `8000`（与 Dockerfile CMD 默认一致） |
| web | `NEXT_PUBLIC_API_URL` | `https://genepage-api-<ORG>.koyeb.app`（**构建时**注入；Dockerfile 已 `ARG`/`ENV`） |

Koyeb 会把 Service 环境变量提供给 Docker **build**（需在 Dockerfile 声明 `ARG`）；本仓库 `web/Dockerfile` 已声明 `NEXT_PUBLIC_API_URL`。

## 自定义域名（挂在 Web App）

1. Koyeb → **Domains** → Add domain，例如 `gazette.example.com`，指派给 App **`genepage-web`**。
2. DNS 按控制台提示添加 **CNAME** → `\<org-uuid\>.cname.koyeb.app`（以控制台文案为准）。
3. 等状态 Active（证书自动签发）。
4. 把自定义源站加入 API 的 `GENEPAGE_CORS_ORIGINS`，例如：  
   `https://genepage-web-<ORG>.koyeb.app,https://gazette.example.com`  
   然后重启/Redeploy API。

apex 域多数需先绑 `www` 再在 DNS 做 HTTP 跳转。P4b 默认只要求 Web 侧自定义域。

## 冒烟检查

部署完成后（注意 free 休眠后的冷启动）：

| 检查 | URL |
| --- | --- |
| API 健康 | `https://genepage-api-<ORG>.koyeb.app/api/health` |
| 基因页 | `https://genepage-web-<ORG>.koyeb.app/g/TP53` |
| 印刷本 | `https://genepage-web-<ORG>.koyeb.app/g/TP53/print` |
| CSV | Web 或 API 同源 `/api/export/genes.csv` |

期望：`/api/health` 返回 `status: ok`，且 `gene_count` / `edition` 与烤入的 `data/index.json` 一致（edition **`0.3.3-p39`**）。

## 注意与限制

- **Free 休眠**：约 1 小时无流量 → scale-to-zero；唤醒 1–5 秒。付费 Instance 可另配 Scale-to-Zero / Light Sleep（见 Koyeb 文档）。
- **无持久免费盘**：种子数据已 `COPY` 进 API 镜像；改 `data/` 需重新构建 API。
- **双 `*.koyeb.app` URL**：未绑自定义域前，Web 与 API 各一个 App 子域。
- **CORS**：`web/src/lib/api.ts` 在设置了 `NEXT_PUBLIC_API_URL` 时会让浏览器直打 API 主机，故 API 需允许 Web 源站。
- **SSR**：Next 服务端同样用该 URL 拉 API，两服务须均可公网互访。
- **不要**把两个服务塞进同一个 App 却用 `/api` 子路径路由：Koyeb 会 **剥掉路径前缀**，FastAPI 的 `/api/health` 会对不上。

## 不要做的事

- 不要为「只上 Koyeb」单独改 edition / bump 版本号。
- 不要在 free 上依赖 Volume 存种子 JSON。
- 不要把密钥写进 compose 明文（本项目 P4b 无密钥需求）。
- 不要用云端 coding agent 改生产配置（P4 禁止）；在仓库内改配置后走 Git / 控制台部署。

## 备选：单 free Instance 跑 Docker Compose（真·单槽免费）

若组织只能放 1 个 free、又暂时不想开付费 Instance，可用 Koyeb 的 privileged Docker Compose 路径（`Dockerfile.koyeb` + `koyeb/docker-compose`）在 **一个** Service 里起 api+web。公网通常只暴露 Web `:3000`，API 走容器内网。此路径与本仓库「双 App 双 URL」主方案不同，需另写 `Dockerfile.koyeb` 与对外端口约定；**P4b 默认不走这条**，仅作零费用权宜。

## 本地对照

```bash
# 与 Koyeb / Render 同一套 Dockerfile（仓库根 context）
docker compose up --build
```

Compose 仍用 `./data:/data:ro` 覆盖烤入层，便于本地改数据。详见根 `README.md`。Render 备选见 [`docs/P4B_RENDER.md`](P4B_RENDER.md)。
