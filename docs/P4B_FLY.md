# P4b：Fly.io 部署（备选；当前主路径见 P4B_HF_SPACES.md）

GenePage Gazette 在 Fly.io 上拆成 **两个 App**，各一台 Machine：

| App | 配置文件 | Dockerfile | 构建 context | 内部端口 | 公网 |
| --- | --- | --- | --- | --- | --- |
| `genepage-api` | 根目录 `fly.api.toml` | `api/Dockerfile` | 仓库根 | 8000 | `https://genepage-api.fly.dev` |
| `genepage-web` | `web/fly.toml` | `web/Dockerfile` | `web/` | 3000 | `https://genepage-web.fly.dev` |

两个 App 都在 **`nrt`（东京）**，备选 **`sin`（新加坡）**；都开 `auto_stop_machines = "stop"` + `auto_start_machines = true` + `min_machines_running = 0`（无流量自动停机、来请求自动拉起）。

> 不为部署单独 bump edition：当前 edition 保持 **`0.3.3-p39`**（见 `docs/EDITION_POLICY.md`），不改 Style C / 版式。Render（`render.yaml`、`docs/P4B_RENDER.md`）与 Koyeb（`koyeb-compose.*.yaml`、`docs/P4B_KOYEB.md`）保留为 **备选**。

## 先看：Fly.io 免费 / 试用规则（2026-10 核对）

**结论：Fly.io 没有永久免费档；新账号有一个不用绑卡的短期试用，用完必须绑卡（或预充值）才能继续跑。** 这不是“长期免费托管”，而是“免卡先跑起来演示”。

| 项 | 说明 | 出处 |
| --- | --- | --- |
| 免费档 | **没有**。新组织无 free tier、无每月免费额度（2024-10 前的旧套餐组织保留旧额度） | [Pricing · Is there a free tier?](https://fly.io/docs/about/pricing/) |
| 试用开通 | **不需要信用卡** 即可开始试用 | [Pricing](https://fly.io/docs/about/pricing/) |
| 试用期限 | **2 小时 Machine 运行时长 或 7 天**，先到者为准；用尽后 App 停止，不能再建 Machine / 部署，直到添加支付方式 | [Free Trial](https://fly.io/docs/about/free-trial/) |
| 试用资源上限 | 2 VM 小时（所有 Machine 合计）、最多 10 台 Machine、20GB 卷、每台 ≤2 vCPU / 4GB 内存；**试用 Machine 运行 5 分钟后会被自动停止**；不含独享 IPv4、performance CPU | [Free Trial](https://fly.io/docs/about/free-trial/) |
| 绑卡 | 试用期间可随时在 Dashboard 加卡；**加卡即结束试用**，开始按量计费。“除 Linked Organization 外所有组织都需要卡”；部署多个 App / 公共镜像等操作对多数账号需要有效信用卡。可能做 < US$10 的预授权（随即撤销） | [Pricing](https://fly.io/docs/about/pricing/) · [Billing](https://fly.io/docs/about/billing/) |
| 无信用卡 | 可在 Billing 购买 credits（最低 **$25**）；预付卡只能用于买 credits，不能作默认支付方式 | [Billing](https://fly.io/docs/about/billing/) |
| 最小机器价格 | `shared-cpu-1x` 256MB ≈ **$2.19/30 天**（iad/ewr 常开）；512MB ≈ $3.69；按秒计费，**停机时只收 rootfs $0.15/GB/月**；`nrt`/`sin` 单价高于 iad（例：1GB `sin` $8.50 vs `iad` $6.70） | [Pricing](https://fly.io/docs/about/pricing/) · [Billing](https://fly.io/docs/about/billing/) |
| 出站流量 | 亚太 $0.04/GB；入站免费；共享 IPv4 / IPv6 免费 | [Pricing](https://fly.io/docs/about/pricing/) |
| 证书 | 每组织前 **10 个单域名证书免费**（之后 $0.10/月/个） | [Pricing](https://fly.io/docs/about/pricing/) |
| 自动休眠 | `auto_stop_machines = "stop"/"suspend"`：Fly Proxy 每隔几分钟检查，空闲/有富余容量即停机；`auto_start_machines = true` 来请求时拉起；`min_machines_running` 只在主区域保底 | [Autostop/autostart](https://fly.io/docs/launch/autostop-autostart/) · [fly.toml 参考](https://fly.io/docs/reference/configuration/) |

**对本项目的含义：**

- 2 个 App × 1 台 Machine，加上 auto stop，试用期 2 VM 小时足够完成部署 + 冒烟 + 短期演示，但撑不了常驻。
- 远端构建（builder）也可能消耗试用资源；尽量少重复 `fly deploy`。
- 若试用期内被要求加卡（例如“deploying multiple apps”触发卡校验），只能：加卡（按量付费，本配置 auto stop 时月成本大约在 $1–3 量级，主要看实际运行时长与区域）、预充值 $25 credits，或回到其他平台。
- 部署时请用 `--ha=false`：`fly deploy` 默认 `--ha=true` 会为每个进程组建 **2 台** Machine，白白翻倍消耗试用时长。

## 配置文件要点

### flyctl 的路径规则（已对照文档与 flyctl 源码）

- **构建 context = `fly deploy` 的工作目录**（第一个位置参数，缺省当前目录）。见 [Monorepo 部署](https://fly.io/docs/launch/monorepo/)。
- `fly.toml` 里 `[build] dockerfile = "…"` **相对配置文件所在目录** 解析（flyctl `internal/command/deploy/deploy_build.go: resolveDockerfilePath` 用 `filepath.Join(filepath.Dir(ConfigFilePath()), path)`）；它**不会改变 context**（[fly.toml 参考 · Specify a Dockerfile](https://fly.io/docs/reference/configuration/#specify-a-dockerfile)）。
- 同时给出工作目录与 `--config` 时，`--config` / `--dockerfile` 相对**工作目录**。
- `.dockerignore` 缺省取工作目录下的那份。

因此：

- **API**：`fly.api.toml` 放仓库根，`dockerfile = "api/Dockerfile"`，**在仓库根执行** `fly deploy -c fly.api.toml` → context 为仓库根（`api/Dockerfile` 需要 `COPY api/…` 与 `data/`），使用根目录 `.dockerignore`。
- **Web**：`web/fly.toml` 放 `web/` 下，不写 `dockerfile`（默认用工作目录的 `Dockerfile`），**在 `web/` 执行** `fly deploy`（或在根执行 `fly deploy web`）→ context 为 `web/`，使用新增的 `web/.dockerignore`（排除本地 `node_modules`、`.next`，避免上传 ~500MB 并污染镜像）。

### 关键字段

- API `[env]`：`GENEPAGE_DATA_DIR=/data`、`GENEPAGE_CACHE_DIR=/data/cache`、`GENEPAGE_CORS_ORIGINS=https://genepage-web.fly.dev`、`PORT=8000`；健康检查 `GET /api/health`；`shared-cpu-1x` **256MB**（OOM 时改 512mb）。
- Web `[build.args]`：`NEXT_PUBLIC_API_URL=https://genepage-api.fly.dev`（Next 构建期内联到 `next.config.mjs` rewrites 与 `src/lib/api.ts`）；`shared-cpu-1x` **512MB**；健康检查 `GET /`。
- 两者：`primary_region = "nrt"`、`force_https = true`、`auto_stop_machines = "stop"`、`auto_start_machines = true`、`min_machines_running = 0`。
- 种子数据已烤进 API 镜像（`COPY data/ /data/`），不需要 Fly Volume（Volume 要收费，也会阻止 bluegreen/canary）。

## 前置条件

1. 有 Fly.io 账号（GitHub 登录即可，试用无需卡）。
2. 本机已装 flyctl（本机：`~/.fly/bin/flyctl`）：
   ```bash
   curl -L https://fly.io/install.sh | sh          # 不需要 sudo，装到 ~/.fly
   export FLYCTL_INSTALL="$HOME/.fly"
   export PATH="$FLYCTL_INSTALL/bin:$PATH"
   flyctl version
   ```
3. 本仓库在 `main`，含 `fly.api.toml`、`web/fly.toml`、`web/.dockerignore`。
4. 不需要本地 Docker：缺省用 Fly 远端 builder（`--remote-only`）。

## 登录

```bash
fly auth login          # 打开浏览器授权；无浏览器环境会打印 URL，在任意已登录浏览器打开即可
fly auth whoami
fly orgs list           # 确认组织（通常 personal）
```

CI / 无交互环境可用 token：`fly tokens create deploy -a genepage-api`，再以 `FLY_API_TOKEN` 环境变量传入（不要提交到仓库）。

## 创建 App（只建一次，不部署）

推荐直接建空 App，**不会改写**仓库里的 toml：

```bash
cd /workspace/genepage
fly apps create genepage-api -o personal
fly apps create genepage-web -o personal
```

或用 `fly launch --no-deploy`（复用现有配置；`--copy-config` 防止它重新生成 toml，执行后用 `git diff` 确认没被改写）：

```bash
cd /workspace/genepage
fly launch --no-deploy --copy-config -c fly.api.toml --name genepage-api -r nrt -o personal --ha=false -y
cd web
fly launch --no-deploy --copy-config --name genepage-web -r nrt -o personal --ha=false -y
cd ..
git diff --stat   # 若 launch 改写了 fly.api.toml / web/fly.toml，按需 git checkout 恢复
```

> 报 “Name has already been taken” 即名字冲突，见下文“改名”。

## 部署

先 API、后 Web（Web 构建时内联 API 地址）：

```bash
cd /workspace/genepage
fly deploy -c fly.api.toml --ha=false            # context = 仓库根
fly status -a genepage-api
curl -fsS https://genepage-api.fly.dev/api/health

cd web
fly deploy --ha=false                            # context = web/，读取 web/fly.toml
fly status -a genepage-web
```

常用排错：

```bash
fly logs -a genepage-api
fly logs -a genepage-web
fly machine list -a genepage-web
fly scale memory 512 -a genepage-api             # API OOM 时；之后同步改 fly.api.toml 的 [[vm]]，否则下次 deploy 会还原
fly deploy -c fly.api.toml --ha=false --wait-timeout 10m   # 拉镜像慢导致超时时
```

确保每个 App 只有 1 台 Machine：`fly scale count 1 -a genepage-api`、`fly scale count 1 -a genepage-web`。

## 改名时要同步改的变量

`*.fly.dev` 子域全局唯一。若 `genepage-api` / `genepage-web` 被占，例如改成 `genepage-api-ddx` / `genepage-web-ddx`：

| 改了谁 | 要改的地方 | 之后 |
| --- | --- | --- |
| API 名 | `fly.api.toml` 的 `app`；`web/fly.toml` 的 `[build.args] NEXT_PUBLIC_API_URL` 与 `[env] NEXT_PUBLIC_API_URL` → `https://<新API名>.fly.dev` | 重新 `fly deploy` **Web**（必须重建镜像，单改 env/secrets 不会生效） |
| Web 名 | `web/fly.toml` 的 `app`；`fly.api.toml` 的 `GENEPAGE_CORS_ORIGINS` → `https://<新Web名>.fly.dev` | 重新 `fly deploy -c fly.api.toml` |
| 区域 | 两个文件的 `primary_region`（建议保持一致，如都改 `sin`） | 两个都重新部署 |

也可不改文件，临时覆盖：`fly deploy --build-arg NEXT_PUBLIC_API_URL=https://… -a <web名>`（命令行参数优先于 toml）——但记得最后回写到 toml，避免下次部署又回旧值。

## 自定义域名

以 `gazette.example.com`（Web）与 `api.gazette.example.com`（API，可选）为例：

```bash
fly ips list -a genepage-web                     # 记下共享 IPv4 与 IPv6
fly certs add gazette.example.com -a genepage-web
fly certs show gazette.example.com -a genepage-web   # 按提示的 DNS 记录配置；状态变 Issued 即可
```

DNS（在你的域名服务商）：

- 子域：`CNAME gazette → genepage-web.fly.dev`（最简单）；
- 根域（apex）：`A @ → <共享 IPv4>` + `AAAA @ → <IPv6>`；
- 若 `fly certs show` 要求，增加 `_acme-challenge` CNAME 用于验证。

上线自定义域名后同步：

- API 允许来源：`fly.api.toml` 的 `GENEPAGE_CORS_ORIGINS = "https://genepage-web.fly.dev,https://gazette.example.com"` → 重新部署 API；
- 若 API 也换自定义域名（`fly certs add api.gazette.example.com -a genepage-api`），把 `web/fly.toml` 的 `NEXT_PUBLIC_API_URL` 改成新地址 → 重新部署 Web。

每组织前 10 个单域名证书免费；共享 IPv4 免费，**不要**分配独享 IPv4（$2/月，试用也不含）。

## 冒烟清单

首个请求可能遇到冷启动（Machine 从 stopped 拉起，通常几秒）。

| 检查 | 命令 / URL | 期望 |
| --- | --- | --- |
| API 健康 | `curl -fsS https://genepage-api.fly.dev/api/health` | `status: ok`，`edition` 为 **`0.3.3-p39`**，`gene_count` 与 `data/index.json` 一致 |
| 首页 | `https://genepage-web.fly.dev/` | 200，报头正常 |
| 基因页 | `https://genepage-web.fly.dev/g/TP53` | TP53 版面完整、图注正常 |
| 印刷本 | `https://genepage-web.fly.dev/g/TP53/print` | 印刷版式正常（浏览器打印预览） |
| CSV | `curl -fsSI https://genepage-web.fly.dev/api/export/genes.csv` 及 `https://genepage-api.fly.dev/api/export/genes.csv` | 200，`text/csv`，可下载 |
| CORS | 浏览器 DevTools 看 Web 页对 API 的请求 | 无 CORS 报错 |
| 自动停机 | 空闲数分钟后 `fly machine list -a genepage-web` | 状态 `stopped`；再访问自动 `started` |

## 免费 / 成本限制回顾

- 无永久免费档；试用 = **2 VM 小时或 7 天**，先到为准，**无需卡**；用尽后 App 停止，需加卡或买 credits（≥$25）。
- 试用 Machine 运行 **5 分钟后自动停止**；加卡后本配置靠 `auto_stop_machines` 省钱，停机只收 rootfs 存储费。
- `nrt` / `sin` 单价高于美国区；亚太出站 $0.04/GB。
- 不用 Volume（数据烤入镜像），不用独享 IPv4。
- 想真正 0 成本常开，Fly 不合适；备选见 `docs/P4B_RENDER.md`（需绑卡）、`docs/P4B_KOYEB.md`（控制台近期无法新建服务 + 每组织仅 1 个 free 实例）。
