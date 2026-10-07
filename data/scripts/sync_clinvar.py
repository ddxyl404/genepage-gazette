# -*- coding: utf-8 -*-
"""Fetch ClinVar Pathogenic / Likely pathogenic counts via NCBI E-utilities esearch."""

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

ROOT = Path(__file__).resolve().parents[1]  # data/
CACHE_DIR = ROOT / "cache" / "clinvar"
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

# Default ≥0.34s between NCBI requests (≈3 req/s without API key)
DEFAULT_DELAY = float(os.environ.get("CLINVAR_DELAY", os.environ.get("NCBI_DELAY", "0.34")))
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


def _get_json(url: str, timeout: float = 30.0) -> dict[str, Any]:
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
        except Exception as exc:  # noqa: BLE001 — filter below
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


def esearch_count(symbol: str, clin_sig_prop: str) -> int:
    """Return esearchresult.count for gene + clinsig property."""
    term = f"{symbol}[gene] AND {clin_sig_prop}[prop]"
    params = {
        "db": "clinvar",
        "term": term,
        "retmode": "json",
        "retmax": "0",
    }
    url = ESEARCH + "?" + urllib.parse.urlencode(params)
    data = _get_json(url)
    count_str = data.get("esearchresult", {}).get("count", "0")
    return int(count_str)


def fetch_clinvar(symbol: str, cache: bool = True) -> dict[str, Any]:
    """
    Fetch P / LP counts for a gene symbol.
    Returns dict with pathogenic, likely_pathogenic, ok, error, queried_at.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Any] = {
        "symbol": symbol,
        "pathogenic": None,
        "likely_pathogenic": None,
        "ok": False,
        "error": None,
        "method": "esearch count by gene+clinsig",
        "queried_at": None,
    }
    try:
        from datetime import datetime
        import zoneinfo

        today = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
        out["queried_at"] = today
        p = esearch_count(symbol, "clinsig_pathogenic")
        lp = esearch_count(symbol, "clinsig_likely_pathogenic")
        out["pathogenic"] = p
        out["likely_pathogenic"] = lp
        out["ok"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
        out["ok"] = False

    if cache:
        path = CACHE_DIR / f"{symbol}.json"
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys

    syms = sys.argv[1:] or ["TP53"]
    for s in syms:
        r = fetch_clinvar(s)
        print(json.dumps(r, ensure_ascii=False))
