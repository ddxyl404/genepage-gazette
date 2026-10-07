# -*- coding: utf-8 -*-
"""Refresh gene identity / aliases / coordinates / pathways via MyGene.info v3."""

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
CACHE_DIR = ROOT / "cache" / "mygene"
MYGENE_QUERY = "https://mygene.info/v3/query"
FIELDS = "symbol,name,alias,type_of_gene,ensembl.gene,genomic_pos,summary,pathway.kegg,uniprot"
DEFAULT_DELAY = float(os.environ.get("MYGENE_DELAY", "0.15"))
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


def _get_json(url: str, timeout: float = 30.0) -> Any:
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


def _pick_ensembl_gene(hit: dict[str, Any]) -> str | None:
    ens = hit.get("ensembl")
    if isinstance(ens, list):
        for item in ens:
            if isinstance(item, dict) and item.get("gene"):
                return item["gene"]
        return None
    if isinstance(ens, dict):
        return ens.get("gene")
    return None


def _pick_genomic_pos(hit: dict[str, Any]) -> dict[str, Any] | None:
    gp = hit.get("genomic_pos")
    if isinstance(gp, list):
        # prefer chr 1-22/X/Y without weird scaffolds
        for item in gp:
            if isinstance(item, dict) and str(item.get("chr", "")).upper() in (
                *[str(i) for i in range(1, 23)],
                "X",
                "Y",
                "MT",
                "M",
            ):
                return item
        return gp[0] if gp else None
    if isinstance(gp, dict):
        return gp
    return None


def _pick_uniprot(hit: dict[str, Any]) -> str | None:
    up = hit.get("uniprot")
    if isinstance(up, dict):
        swiss = up.get("Swiss-Prot") or up.get("TrEMBL")
        if isinstance(swiss, list):
            return swiss[0] if swiss else None
        if isinstance(swiss, str):
            return swiss
    if isinstance(up, str):
        return up
    return None


def _pathways_from_kegg(hit: dict[str, Any], limit: int = 5) -> list[dict[str, str]]:
    pw = hit.get("pathway") or {}
    kegg = pw.get("kegg") if isinstance(pw, dict) else None
    if not kegg:
        return []
    if isinstance(kegg, dict):
        kegg = [kegg]
    out = []
    for item in kegg:
        if not isinstance(item, dict):
            continue
        kid = item.get("id") or ""
        name = item.get("name") or kid
        if not kid:
            continue
        # MyGene often stores id as "hsa04115"
        url = f"https://www.kegg.jp/pathway/{kid}"
        out.append({"name": name, "url": url})
        if len(out) >= limit:
            break
    return out


def _aliases(hit: dict[str, Any]) -> list[str]:
    alias = hit.get("alias")
    if alias is None:
        return []
    if isinstance(alias, str):
        return [alias]
    if isinstance(alias, list):
        return [str(a) for a in alias if a]
    return []


def fetch_mygene(symbol: str, cache: bool = True) -> dict[str, Any]:
    """Query MyGene for symbol; return normalized identity fields + raw hit."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    import zoneinfo

    today = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    out: dict[str, Any] = {
        "symbol": symbol,
        "ok": False,
        "error": None,
        "queried_at": today,
        "id": None,
        "name": None,
        "aliases": [],
        "type": "protein_coding",
        "location": None,
        "uniprot": None,
        "alphafold_url": None,
        "pathways": [],
        "summary": None,
    }
    try:
        params = {
            "q": f"symbol:{symbol}",
            "species": "human",
            "fields": FIELDS,
            "size": "1",
        }
        url = MYGENE_QUERY + "?" + urllib.parse.urlencode(params)
        data = _get_json(url)
        hits = data.get("hits") if isinstance(data, dict) else None
        if not hits:
            raise RuntimeError(f"MyGene returned no hits for symbol:{symbol}")
        hit = hits[0]
        out["raw_hit"] = hit

        ensembl_id = _pick_ensembl_gene(hit)
        out["id"] = ensembl_id
        out["name"] = hit.get("name")
        out["aliases"] = _aliases(hit)
        tog = hit.get("type_of_gene") or "protein-coding"
        out["type"] = "protein_coding" if "protein" in str(tog).replace("-", "_") else str(tog)

        gp = _pick_genomic_pos(hit)
        if gp:
            chrom = str(gp.get("chr", "")).replace("chr", "")
            out["location"] = {
                "chrom": chrom,
                "start": int(gp["start"]) if gp.get("start") is not None else None,
                "end": int(gp["end"]) if gp.get("end") is not None else None,
                "assembly": "GRCh38",
            }

        uniprot = _pick_uniprot(hit)
        out["uniprot"] = uniprot
        out["alphafold_url"] = (
            f"https://alphafold.ebi.ac.uk/entry/{uniprot}" if uniprot else None
        )
        out["pathways"] = _pathways_from_kegg(hit, limit=5)
        out["summary"] = hit.get("summary")
        out["ok"] = bool(ensembl_id)
        if not ensembl_id:
            out["error"] = "missing ensembl.gene"
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
        out["ok"] = False

    if cache:
        # Drop huge raw for readability? keep it — useful for audit
        path = CACHE_DIR / f"{symbol}.json"
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys

    sym = sys.argv[1] if len(sys.argv) > 1 else "TP53"
    r = fetch_mygene(sym)
    # print without raw_hit for brevity
    slim = {k: v for k, v in r.items() if k != "raw_hit"}
    print(json.dumps(slim, ensure_ascii=False, indent=2))
