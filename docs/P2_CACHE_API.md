# P2 Cache API（预告）

缓存契约见 [`data/cache/README.md`](../data/cache/README.md)。`data/genes/*.json` 仍是 API 的唯一主数据源；`data/cache/clinvar/`、`gtex/`、`mygene/` 仅供追溯、重跑和状态清单，不在 API 请求时覆盖基因 JSON。

- `GET /api/cache/status`：扫描三类 `<SYMBOL>.json` 及 `data/cache/meta.json`，返回各类已缓存 symbol。
- 数据侧将真数或失败字段 `「本期未收录」` 合并进基因 JSON；API 原样透传。
- 缺少 cache 文件不会清除基因 JSON 中的 P1 seed 值。
