# P3.6 Figures — 路径约定 / Path convention

工程静态图路由与基因 JSON 字段（透传）。版式组件由版式频道落地；edition `0.3.1-p36` 由数据/总编 bump，工程不单独改 edition。

Engineering owns static figure routes + gene JSON passthrough. Layout components are out of scope here. Edition bump `0.3.1-p36` is data/editor; eng does not bump edition alone.

## Gene JSON fields（API 透传）

| Field | 说明 / Notes |
| --- | --- |
| `cytoband` | `{ chrom, start, end, assembly?, band_label?, figure_id? }` — 位点钉元数据 |
| `domains` | `[{ id, name, name_zh?, start, end, source, url? }]` — 结构域条；无则 `[]` |
| `structure.preview_image` | AlphaFold 静态预览；**约定写 API URL**（见下）或 `null` |
| `expression.tissues` | 既有字段；版式做 small multiples（TPM desc / top N） |

`GET /api/gene/{id}` 原样返回基因 JSON，不改写上述字段。

## Static paths → API

| On disk | HTTP |
| --- | --- |
| `data/figures/cytobands/{chr}.json` 或 `{chr}.svg` | `GET /api/figures/cytobands/{chr}` |
| `data/cache/alphafold/{SYMBOL}.png`（或 `.webp` / `.jpg`） | `GET /api/figures/alphafold/{SYMBOL}` |

- Chrom 归一化：`17` / `chr17` / `CHR17` 都会尝试 bare 与 `chr` 前缀文件名。
- AlphaFold：大小写不敏感；同 symbol 优先 `.png` → `.webp` → `.jpg`。
- 缺失 → `404`（版式走空态文案）。
- 清单：`GET /api/figures/status` → `{ cytobands: [...], alphafold: [...] }`。

## Convention：`structure.preview_image`

基因 JSON 中应写成 API URL，例如：

```json
"structure": {
  "alphafold_url": "https://alphafold.ebi.ac.uk/entry/P04637",
  "preview_image": "/api/figures/alphafold/TP53"
}
```

无缓存时 `"preview_image": null`。相对 cache 路径也可暂存，但版式/联调优先 API URL。

## Acceptance curls

```bash
# health
curl -s http://127.0.0.1:8000/api/health

# figure status (empty lists OK until data lands)
curl -s http://127.0.0.1:8000/api/figures/status

# cytoband / alphafold — 404 until assets drop; 200 when present
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/api/figures/cytobands/17
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/api/figures/cytobands/chr17
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/api/figures/alphafold/TP53

# gene passthrough (expect structure.preview_image key)
curl -s http://127.0.0.1:8000/api/gene/TP53 | python3 -c "import sys,json; g=json.load(sys.stdin); print('preview_image=', g.get('structure',{}).get('preview_image', '<MISSING>')); print('cytoband=', g.get('cytoband')); print('domains=', 'present' if 'domains' in g else 'absent')"
```

Editor front: `/g/TP53?lang=zh` · `/g/TP53?lang=en` · print 同页（版式验收）。
