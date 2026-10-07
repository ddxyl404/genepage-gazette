# GenePage Gazette P3 — local perf (box)

Measured on this box with `curl -w` against `127.0.0.1` (CST / Asia/Shanghai).
Data is local file JSON via `GENEPAGE_DATA_DIR=/workspace/genepage/data`. No CloudAgent.

**Date:** 2026-09-29 18:27 CST

## Method

```bash
FMT='ttfb=%{time_starttransfer} total=%{time_total} code=%{http_code} size=%{size_download}\n'
curl -s -o /dev/null -w "$FMT" "http://127.0.0.1:3000/g/TP53"
curl -s -o /dev/null -w "$FMT" "http://127.0.0.1:8000/api/gene/TP53"
```

- **TTFB** = `time_starttransfer` (first byte)
- **total** = full transfer
- Cold ≈ first hit in the series after services already compiled; warm = subsequent hits

## Results

### HTML `GET http://127.0.0.1:3000/g/TP53`

| hit   | TTFB (s) | total (s) | code | size |
|-------|----------|-----------|------|------|
| cold  | 0.048    | 0.052     | 200  | 31906 |
| warm1 | 0.025    | 0.026     | 200  | 31906 |
| warm2 | 0.023    | 0.023     | 200  | 31906 |
| warm3 | 0.033    | 0.034     | 200  | 31906 |

**Target &lt;2s HTML:** met (warm ≪ 2s; cold ≪ 2s with local data).

### API `GET http://127.0.0.1:8000/api/gene/TP53`

| hit   | TTFB (s) | total (s) | code | size |
|-------|----------|-----------|------|------|
| cold  | 0.0033   | 0.0033    | 200  | 3343 |
| warm1 | 0.0013   | 0.0013    | 200  | 3343 |
| warm2 | 0.0013   | 0.0013    | 200  | 3343 |
| warm3 | 0.0012   | 0.0012    | 200  | 3343 |

### Related

| URL | TTFB (s) | total (s) |
|-----|----------|-----------|
| `/api/gene/TP53` via Next rewrite `:3000` | 0.0055 | 0.0055 |
| `/g/TP53/print` warm | ~0.024 | ~0.025 |
| `/` home warm | ~0.022 | ~0.023 |

## Caching notes

- Gene page + print: `export const revalidate = 60` (ISR-style); `fetchGene` uses `next: { revalidate: 60 }`.
- Homepage stays `force-dynamic` because of `?q=` search params; catalog still reads `/api/index` + `/api/search`.
- Local file reads already meet &lt;2s without aggressive CDN caching.
- Do **not** break live reads from `GENEPAGE_DATA_DIR`; 60s revalidate is safe for gazette seed/sync cadence.

## Pass criteria

- [x] HTML `/g/TP53` &lt; 2s (warm and cold local)
- [x] API `/api/gene/TP53` &lt; 2s
- [x] Print route available for layout bot: `/g/{symbol}/print`
