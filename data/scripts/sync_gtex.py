# -*- coding: utf-8 -*-
"""Fetch GTEx median gene expression (TPM) via GTEx Portal API v2."""

from __future__ import annotations

import json
import os
import time
import urllib.parse
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None
    import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "cache" / "gtex"
GTEX_BASE = "https://gtexportal.org/api/v2"
DEFAULT_DELAY = float(os.environ.get("GTEX_DELAY", "0.2"))
MAX_RETRIES = int(os.environ.get("SYNC_MAX_RETRIES", "3"))
UA = "GenePageGazette/0.2 (research)"

_last_request_at = 0.0


def _throttle(delay: float = DEFAULT_DELAY) -> None:
    global _last_request_at
    now = time.monotonic()
    wait = delay - (now - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _get_json(url: str, timeout: float = 45.0) -> dict[str, Any]:
    import urllib.error

    last_err: BaseException | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        _throttle()
        try:
            if requests is not None:
                r = requests.get(url, timeout=timeout, headers={"User-Agent": UA})
                r.raise_for_status()
                return r.json()
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            retryable = False
            if requests is not None and isinstance(exc, requests.exceptions.RequestException):
                retryable = True
            elif isinstance(exc, (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError)):
                retryable = True
            if not retryable or attempt >= MAX_RETRIES:
                raise
            last_err = exc
            time.sleep(DEFAULT_DELAY * attempt)
    assert last_err is not None
    raise last_err


def resolve_gencode_id(ensembl_id: str) -> str | None:
    """Resolve ENSG… to a gencodeId that GTEx accepts (often ENSG….version)."""
    # Strip version if present for geneId query
    base = ensembl_id.split(".")[0]
    url = f"{GTEX_BASE}/reference/gene?" + urllib.parse.urlencode({"geneId": base})
    data = _get_json(url)
    # Response shapes: {"data":[{...}]} or list
    items = data.get("data") if isinstance(data, dict) else data
    if not items:
        # try with full id
        url2 = f"{GTEX_BASE}/reference/gene?" + urllib.parse.urlencode({"geneId": ensembl_id})
        data2 = _get_json(url2)
        items = data2.get("data") if isinstance(data2, dict) else data2
    if not items:
        return None
    first = items[0] if isinstance(items, list) else items
    gencode = first.get("gencodeId") or first.get("id") or first.get("geneId")
    return gencode


def fetch_median_expression(gencode_id: str, dataset_id: str | None = None) -> list[dict[str, Any]]:
    """Return list of {tissueSiteDetailId, median, ...} from medianGeneExpression.

    GTEx Portal API v2 typically requires datasetId (e.g. gtex_v8 / gtex_v10).
    """
    dataset_id = dataset_id or os.environ.get("GTEX_DATASET", "gtex_v8")
    candidates = [dataset_id]
    for alt in ("gtex_v8", "gtex_v10"):
        if alt not in candidates:
            candidates.append(alt)

    last_items: list = []
    for ds in candidates:
        params = {"gencodeId": gencode_id, "datasetId": ds}
        url = f"{GTEX_BASE}/expression/medianGeneExpression?" + urllib.parse.urlencode(params)
        data = _get_json(url)
        items = data.get("data") if isinstance(data, dict) else data
        if items:
            return list(items)
        last_items = list(items or [])

    # retry without version suffix
    base = gencode_id.split(".")[0]
    if base != gencode_id:
        for ds in candidates:
            params = {"gencodeId": base, "datasetId": ds}
            url = f"{GTEX_BASE}/expression/medianGeneExpression?" + urllib.parse.urlencode(params)
            data = _get_json(url)
            items = data.get("data") if isinstance(data, dict) else data
            if items:
                return list(items)
    return list(last_items)


def _tissue_label(row: dict[str, Any]) -> str:
    return (
        row.get("tissueSiteDetailId")
        or row.get("tissueSiteDetail")
        or row.get("tissue")
        or row.get("ontologyId")
        or "Unknown"
    )


def _median_value(row: dict[str, Any]) -> float | None:
    for key in ("median", "medianValue", "value", "tpm", "medianTpm"):
        if key in row and row[key] is not None:
            try:
                return float(row[key])
            except (TypeError, ValueError):
                continue
    return None


def fetch_gtex(symbol: str, ensembl_id: str, top_n: int = 8, cache: bool = True) -> dict[str, Any]:
    """
    Fetch top-N tissues by median TPM for a gene.
    Returns tissues list ready for gene JSON (name, name_zh, value) plus status.
    """
    # Import tissue mapping from sibling module
    import sys

    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from tissue_zh import normalize_tissue_name, short_zh_for_headline, tissue_name_zh

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    import zoneinfo

    today = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    out: dict[str, Any] = {
        "symbol": symbol,
        "ensembl_id": ensembl_id,
        "gencode_id": None,
        "ok": False,
        "error": None,
        "queried_at": today,
        "raw_count": 0,
        "tissues": [],
        "top_tissue_en": None,
        "top_tissue_zh": None,
    }
    raw_payload: dict[str, Any] = {"symbol": symbol, "ensembl_id": ensembl_id}

    try:
        gencode = resolve_gencode_id(ensembl_id)
        out["gencode_id"] = gencode
        raw_payload["gencode_id"] = gencode
        if not gencode:
            raise RuntimeError(f"GTEx reference/gene returned no gencodeId for {ensembl_id}")

        rows = fetch_median_expression(gencode)
        raw_payload["median_rows"] = rows
        out["raw_count"] = len(rows)

        scored: list[tuple[str, float]] = []
        for row in rows:
            label = _tissue_label(row)
            val = _median_value(row)
            if val is None:
                continue
            scored.append((normalize_tissue_name(label), val))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_n]
        tissues = []
        for name, val in top:
            tissues.append(
                {
                    "name": name,
                    "name_zh": tissue_name_zh(name),
                    "value": round(val, 3) if isinstance(val, float) else val,
                }
            )
        out["tissues"] = tissues
        if tissues:
            out["top_tissue_en"] = tissues[0]["name"]
            out["top_tissue_zh"] = short_zh_for_headline(tissues[0]["name"])
        out["ok"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
        out["ok"] = False
        out["tissues"] = []
        raw_payload["error"] = out["error"]

    if cache:
        raw_payload["result"] = {
            k: out[k]
            for k in ("ok", "error", "gencode_id", "raw_count", "tissues", "top_tissue_en", "top_tissue_zh", "queried_at")
        }
        path = CACHE_DIR / f"{symbol}.json"
        path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys

    sym = sys.argv[1] if len(sys.argv) > 1 else "TP53"
    eid = sys.argv[2] if len(sys.argv) > 2 else "ENSG00000141510"
    print(json.dumps(fetch_gtex(sym, eid), ensure_ascii=False, indent=2))
