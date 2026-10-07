# OPS Smoke — GenePage Gazette（P4a）

本机验收清单。API 默认 `http://127.0.0.1:8000`，Web 默认 `http://127.0.0.1:3000`。

> **预览说明：** 在 assistant 桌面 / box 上 curl 或浏览器可打到本机进程。用户笔记本上的 `127.0.0.1` **无法**直连共享 box；请用桌面预览或经代理转发。

**期望 edition：** `0.3.3-p39`（P4a 文档与脚本默认不 bump）。

## 1. Health

```bash
curl -s http://127.0.0.1:8000/api/health
# expect: "status":"ok" · "edition":"0.3.3-p39" · gene_count
```

## 2. 基因页 / 印刷本（经 Web）

```bash
curl -sI "http://127.0.0.1:3000/g/TP53?lang=zh" | head -5
curl -sI "http://127.0.0.1:3000/g/TP53?lang=en" | head -5
curl -sI "http://127.0.0.1:3000/g/TP53/print?lang=zh" | head -5
# expect: HTTP 200（或 Next 正常响应头）
```

浏览器核对：中文 / 英文气质与印刷本一页。

## 3. CSV 导出

```bash
curl -sI http://127.0.0.1:8000/api/export/genes.csv | head -10
curl -s http://127.0.0.1:8000/api/export/genes.csv | head -3
# expect: text/csv · 含表头与 TP53 等行
```

## 4. Figures

```bash
curl -sI http://127.0.0.1:8000/api/figures/cytobands/17 | head -10
curl -sI http://127.0.0.1:8000/api/figures/alphafold/TP53 | head -10
curl -s http://127.0.0.1:8000/api/figures/status
# expect: cytobands/alphafold 有图或合理 404/占位；status JSON 可读
```

## 5. 备份 smoke

```bash
./scripts/backup_data.sh --dry-run
ls -lh backups/genepage-*.tgz
# expect: 至少一个 tgz；路径打印到 stdout
```

## 勾选

- [ ] health edition = `0.3.3-p39`
- [ ] TP53 zh / en / print 可开
- [ ] genes.csv 可下
- [ ] figures cytobands·alphafold·status 可达
- [ ] `backups/genepage-*.tgz` 已生成
