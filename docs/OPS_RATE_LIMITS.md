# 运维 · 上游礼貌限速

脚本默认 **串行、单进程**；禁止多进程并发打满同一上游。间隔可用环境变量覆盖。

## 默认间隔（来自代码）

| 源 | 环境变量 | 默认 | 说明 |
|----|----------|------|------|
| ClinVar / NCBI E-utilities | `CLINVAR_DELAY` 或 `NCBI_DELAY` | **0.34 s** | ≈3 req/s（无 API key）；User-Agent `GenePageGazette` |
| GTEx Portal API v2 | `GTEX_DELAY` | **0.2 s** | |
| MyGene.info v3 | `MYGENE_DELAY` | **0.15 s** | |
| UniProt | `UNIPROT_DELAY` | **0.35 s** | `sync_figures.py` 请求间 sleep |
| AlphaFold | `AF_DELAY` | **0.35 s** | 同上 |

ClinVar / GTEx / MyGene 用 `_throttle()` 保证两次请求间隔 ≥ 上述 delay。

## 重试（P4a）

- 环境变量：`SYNC_MAX_RETRIES`（默认 **3**）
- 适用范围：`sync_clinvar` / `sync_gtex` / `sync_mygene` 的 `_get_json`；`sync_figures` 的 `_http_get` / `_http_json`
- 可重试：HTTP/网络错误（`HTTPError` / `URLError` / `RequestException` / `Timeout` 等）
- 行为：每次尝试前先 throttle（或 figures 用 delay 退避）；失败后 `sleep(delay * attempt)`，用尽次数后抛出最后一次异常
- backoff 基数：三源脚本用各自 `DEFAULT_DELAY`；figures 用 `AF_DELAY`（可用 `UNIPROT_DELAY` 同量级覆盖习惯）

## 并发纪律

- **禁止**同时跑多个 `sync_all` / `sync_figures` / 单源 sync 打同一 API。
- 一进程、按基因顺序；figures 在 UniProt / AF 循环内已 `sleep`。
- cron 示例见 `OPS_CRON.md`（注释掉、默认不装）。

## 其它环境变量

- `SYNC_SYMBOLS`：逗号分隔子集（如 `TP53,BRCA1`），限缩请求量。
