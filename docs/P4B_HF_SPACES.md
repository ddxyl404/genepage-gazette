# P4b：Hugging Face Spaces 部署（单容器，当前选定路径）

GenePage Gazette 在 HF Spaces 上合成 **一个 Docker 容器**：

| 进程 | 监听 | 说明 |
| --- | --- | --- |
| `uvicorn main:app` | `127.0.0.1:8000`（仅容器内） | FastAPI，读烤进镜像的 `data/` |
| `node server.js` | `0.0.0.0:7860`（Space 对外端口，README `app_port: 7860`） | Next.js 14 standalone |

- 浏览器 → 同源 `/api/*` → Next rewrite → `http://127.0.0.1:8000/api/*`（构建时**不设** `NEXT_PUBLIC_API_URL`，rewrite 目标在 build 时固化为 `127.0.0.1:8000`）。
- Next SSR → `http://127.0.0.1:8000`（`web/src/lib/api.ts` 的服务端默认值）。
- 同源访问，不涉及 CORS；API 的 CORS 设置保持原样。
- 任一进程退出 → `start.sh` 停掉另一个并以非 0 退出，Space 显示错误/重启。
- edition 保持 **`0.3.3-p39`**，不改 Style C / 版式 / 配色。Render / Fly / Koyeb / Compose 配置原样保留为备选。

## ⚠ 先看：2026-07 起 Docker Space 免费档需要 PRO（2026-10-08 核对）

**结论：HF 官方文档现写明“Static Spaces 对所有人免费；Gradio 与 Docker Space 跑在算力上，创建需要付费计划（个人 = PRO）”。免费账号在 `cpu-basic` 上创建 Docker Space 会被拒（HTTP 402）。** 也就是说“免费 + 不绑卡”的 Docker Space 目前**走不通**；PRO 订阅需要付款方式。

| 项 | 现行规则 | 出处 |
| --- | --- | --- |
| 谁能建 Docker Space | 需 **PRO**（个人）或 Team/Enterprise（组织）；Static Space 免费；免费个人号仅可托管最多 2 个 ZeroGPU 上的 Gradio Space | [Spaces Overview](https://huggingface.co/docs/hub/spaces-overview) · [Spaces Launch](https://huggingface.co/spaces/launch) |
| 免费号创建报错 | 无订阅时在 `cpu-basic` 上创建/复制/迁移 Gradio 或 Docker Space 返回 **HTTP 402**；付费硬件只需绑支付方式 + 预充值 | [huggingface_hub · Manage your Space](https://huggingface.co/docs/huggingface_hub/guides/manage-spaces) |
| 变更时间 | 社区反馈 2026-07-08 起 UI 将 Docker 标为 “Paid”，CLI 报 “hosting Gradio and Docker Spaces on free cpu-basic requires a PRO subscription” | [HF 论坛帖](https://discuss.huggingface.co/t/docker-sdk-now-marked-as-paid-when-creating-a-new-space/177580) |
| PRO 包含 | “Host ZeroGPU, Gradio & Docker Spaces”、Dev Mode 等 | [Pricing](https://huggingface.co/pricing) |

**对本项目的含义：** 本目录的单容器方案已就绪并在本机验证通过，但要上 HF 必须二选一：

1. 账号开 **PRO**（要付款方式）→ 按下文步骤建 Docker Space、推送；或
2. 不走 HF Docker：回 Render（$1 临时验证后 Free 档）、或把站点改成**纯静态导出**后用免费的 Static Space / GitHub Pages / Cloudflare Pages（需要改造：Next `output: "export"` + 预生成 10 个基因页与 API JSON/CSV，属于新工作量，未实施）。

单容器镜像本身与平台无关，任何“一个容器 + 一个端口”的主机（含 HF PRO）都能直接用。

## HF Docker Space 规则核对

| 项 | 规则 | 出处 |
| --- | --- | --- |
| README frontmatter | Space 仓根 `README.md` 顶部 YAML：`sdk: docker`；对外端口默认 **7860**，可用 `app_port` 改 | [Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) |
| 端口 | 只对外暴露 `app_port` 一个端口；容器内可开任意多端口（本项目 8000 只在容器内） | [Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) |
| 运行用户 | 容器以 **uid 1000** 运行；官方建议 `useradd -m -u 1000 user`、`USER user`、`HOME=/home/user`、`COPY --chown=user` | [Docker Spaces · Permissions](https://huggingface.co/docs/hub/spaces-sdks-docker#permissions) |
| `/data` | `/data` 是挂载存储桶（Storage Bucket）的运行时挂载点，**构建期不可用**；磁盘写入在重启后丢失 | [Docker Spaces · Data Persistence](https://huggingface.co/docs/hub/spaces-sdks-docker#data-persistence) |
| CPU Basic 规格 | **2 vCPU / 16 GB RAM / 50 GB 非持久磁盘**，无小时费用（但见上：Docker 需 PRO） | [Spaces Overview](https://huggingface.co/docs/hub/spaces-overview) · [GPU Spaces](https://huggingface.co/docs/hub/spaces-gpus) |
| 休眠 | `cpu-basic` **闲置 48 小时**自动休眠；有人访问自动重启；不能自定义休眠时间或常开（需付费硬件） | [GPU Spaces · sleep time](https://huggingface.co/docs/hub/spaces-gpus#sleep-time) |
| 出站网络 | 只允许 80/443/8080 出站（本容器运行时不需要外网） | [Spaces Overview · Networking](https://huggingface.co/docs/hub/spaces-overview) |
| 变量 / 构建参数 | Space Variables 会作为 build-arg 传入构建、运行时注入环境 | [Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) |
| 自定义域名 | **PRO 或 Team/Enterprise 功能**；Space 需 Public/Protected；CNAME 指向 `hf.space` | [Spaces Custom Domain](https://huggingface.co/docs/hub/spaces-custom-domain) |
| 默认公网地址 | `https://<user>-<space>.hf.space`（环境变量 `SPACE_HOST`） | [Spaces Overview](https://huggingface.co/docs/hub/spaces-overview) |

据此本方案做了两处取舍：

- 数据烤在 **`/home/user/app/data`**（`GENEPAGE_DATA_DIR`），**不放 `/data`**，避免与 HF 存储桶挂载点冲突。
- **不要**在 Space Settings 里加名为 `NEXT_PUBLIC_API_URL` 的 Variable：它会作为 build-arg/env 进入构建，把浏览器切回直连 API。

## 文件

| 路径（主仓） | 作用 |
| --- | --- |
| `hf-space/Dockerfile` | 单容器多阶段构建：`node:20-bookworm-slim` 构建 Next standalone → `python:3.12-slim-bookworm` 运行时 + 拷入 node 二进制；uid 1000 用户 `user` |
| `hf-space/start.sh` | 同时启动 uvicorn(127.0.0.1:8000) 与 node(0.0.0.0:7860)，先等 API 健康再起 Web；任一退出则整体退出 |
| `hf-space/README.space.md` | Space README 模板（frontmatter：`sdk: docker`、`app_port: 7860`），组装时填入 edition / data_as_of |
| `hf-space/gitattributes.space` | 组装为 Space 的 `.gitattributes`：png/ico/woff/pdb 走 LFS/Xet（HF 拒绝普通 git 推二进制） |
| `hf-space/dockerignore.space` | 组装为 `.dockerignore` |
| `scripts/build_hf_space.sh` | 组装 Space 仓目录（默认 `/workspace/genepage-hf-space`） |

组装输出（**不提交进主仓**）：

```
/workspace/genepage-hf-space/
  README.md  Dockerfile  start.sh  .gitattributes  .dockerignore  BUILD_INFO
  api/main.py  api/requirements.txt
  data/   genes/ index.json figures/ exports/ cache/（不含 data/scripts、cache/logs 内容、__pycache__）
  web/    Next 源码（不含 node_modules、.next、tsbuildinfo、web/Dockerfile、web/fly.toml）
```

约 9.7 MB / 144 个文件（2026-10-08）。

## 部署步骤（需账号已开 PRO）

### 1. 建 Space（网页）

[huggingface.co/new-space](https://huggingface.co/new-space)：

- Owner：你的账号；Space name：建议 `genepage-gazette`
- License：可选
- **SDK：Docker → 模板 Blank**
- **Hardware：CPU basic**
- **Visibility：Public**
- 不要添加 `NEXT_PUBLIC_API_URL` 变量；本项目不需要任何 Secret

### 2. 准备 token

[Settings → Access Tokens](https://huggingface.co/settings/tokens)：新建 **Write** 角色 token，或 fine-grained token 勾选对该 Space 的 **write** 权限。只放环境变量，别写进仓库/脚本。

### 3. 组装并推送（推荐 `hf upload`，自动处理 LFS/Xet）

```bash
cd /workspace/genepage
bash scripts/build_hf_space.sh                    # → /workspace/genepage-hf-space

python3 -m pip install -U huggingface_hub         # 提供 `hf` 命令
export HF_TOKEN=hf_xxx                            # 上一步的 write token
SPACE=<hf用户名>/genepage-gazette

hf upload "$SPACE" /workspace/genepage-hf-space . \
  --repo-type=space \
  --commit-message "deploy 0.3.3-p39 ($(git rev-parse --short HEAD))"
```

以后若删过文件，想让 Space 端同步删除，可加 `--delete="*"`（删除远端存在、本地没有的文件；本地已含 `.gitattributes`/`README.md`，不会被删）。

备选（git）：

```bash
git clone https://huggingface.co/spaces/$SPACE /workspace/genepage-hf-space   # 克隆到输出目录
bash scripts/build_hf_space.sh                    # 脚本保留输出目录里的 .git
cd /workspace/genepage-hf-space
git lfs install                                   # 或按 HF 文档装 git-xet
git add -A && git commit -m "deploy 0.3.3-p39"
git push https://<hf用户名>:$HF_TOKEN@huggingface.co/spaces/$SPACE main
```

推送后 Space 自动构建（Logs → Build / Container 可看）。首次构建约几分钟（npm ci + next build + pip）。

### 4. 冒烟清单

`BASE=https://<hf用户名>-genepage-gazette.hf.space`

| URL | 期望 |
| --- | --- |
| `$BASE/` | 200，首页报头 |
| `$BASE/g/TP53` | 200，TP53 屏幕版 |
| `$BASE/g/TP53/print` | 200，打印版 |
| `$BASE/api/health` | 200，`"edition":"0.3.3-p39"`、`gene_count: 10` |
| `$BASE/api/export/genes.csv` | 200，`text/csv` |
| `$BASE/api/figures/alphafold/TP53` | 200，`image/png` |
| `$BASE/g/NOPE` | 404 |

```bash
for u in / /g/TP53 /g/TP53/print /api/health /api/export/genes.csv; do
  printf '%-24s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "$BASE$u")"; done
curl -s "$BASE/api/health"
```

> 注意：HF Space 页面 `https://huggingface.co/spaces/<user>/<space>` 是带 iframe 的外壳；冒烟请直接打 `*.hf.space` 域名。

### 5. 休眠 / 冷启动

- CPU basic 闲置 **48 小时**自动休眠；下一位访客访问时自动重启，期间会看到 HF 的 “Building/Starting” 页面，通常需要几十秒到一两分钟（经验值，未实测）。
- 免费硬件无法常开、不能改休眠时间；也可在 Settings 手动 Pause。
- 容器内写入不持久（Next 的 `.next/cache` 每次重启清空，正常）。

### 6. 自定义域名

HF 自定义域名是 **PRO / Team / Enterprise** 功能（既然 Docker 本身已需 PRO，开了 PRO 即可用）：Space Settings → Custom Domain，DNS 加 CNAME → `hf.space`，等状态变 ready。Space 必须 Public 或 Protected。

## 以后更新数据 / 代码

1. 在主仓照常更新（`data/scripts/sync_all.py` 等 → `data/` 变更 → 本地冒烟）并 commit/push 到 GitHub。
2. 重跑 `bash scripts/build_hf_space.sh`。
3. 再执行第 3 步的 `hf upload`（或 git add/commit/push）。HF 收到新提交会自动重建并重启。

## 本机验证（2026-10-08，box 无 Docker 的模拟）

box 没有 Docker，用组装目录按 Dockerfile 的阶段手工模拟：`npm ci` → `next build`（未设 `NEXT_PUBLIC_API_URL`）→ 拷 `.next/standalone` + `.next/static` + `public` → Python venv 装 `api/requirements.txt` → `data/` 设为只读 → 执行 `start.sh`。为避开本机已占用的 8000/3000，整个测试跑在 `unshare -rn` 的隔离网络命名空间里，端口与线上一致（8000/7860）。

- `routes-manifest.json` 中 rewrite 目标确为 `http://127.0.0.1:8000/api/:path*`。
- 经 7860：`/` 200、`/g/TP53` 200、`/g/TP53/print` 200、`/api/health` 200（edition `0.3.3-p39`，gene_count 10）、`/api/export/genes.csv` 200（text/csv）、`/api/gene/TP53` 200、`/api/figures/alphafold/TP53` 200（image/png）、`/g/NOPE` 404。
- 监听：node `0.0.0.0:7860`，uvicorn `127.0.0.1:8000`。
- 停掉 uvicorn 后 `start.sh` 随即退出（非 0），无残留监听。
- 尚未实测：真实 `docker build` 与 HF 构建（box 无 Docker；HF 需 PRO）。
