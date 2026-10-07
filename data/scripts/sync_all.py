# -*- coding: utf-8 -*-
"""
GenePage Gazette P2 one-shot sync entrypoint.

Usage:
  python3 /workspace/genepage/data/scripts/sync_all.py

Optional env:
  CLINVAR_DELAY / NCBI_DELAY  (default 0.34)
  GTEX_DELAY                  (default 0.2)
  MYGENE_DELAY                (default 0.15)
  SYNC_SYMBOLS                comma-separated subset, e.g. TP53,BRCA1
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import zoneinfo

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent  # data/
GENES_DIR = ROOT / "genes"
CACHE_DIR = ROOT / "cache"
INDEX_PATH = ROOT / "index.json"
META_PATH = CACHE_DIR / "meta.json"

EDITION = "0.2.0-p2"
DEMO_SYMBOLS = [
    "TP53",
    "BRCA1",
    "BRCA2",
    "EGFR",
    "KRAS",
    "APOE",
    "CFTR",
    "HBB",
    "APP",
    "MYC",
]

sys.path.insert(0, str(SCRIPTS))
from sync_clinvar import fetch_clinvar  # noqa: E402
from sync_gtex import fetch_gtex  # noqa: E402
from sync_mygene import fetch_mygene  # noqa: E402
from tissue_zh import short_zh_for_headline  # noqa: E402


def today_shanghai() -> str:
    return datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")


def cytoband_hint(chrom: str, start: int | None) -> str:
    """Keep existing location headline if present; else chrom-only fallback."""
    if not chrom:
        return "—"
    return f"{chrom}"


def load_gene(symbol: str) -> dict[str, Any]:
    path = GENES_DIR / f"{symbol}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def save_gene(symbol: str, data: dict[str, Any]) -> None:
    path = GENES_DIR / f"{symbol}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _location_headline_value(gene: dict[str, Any], my: dict[str, Any]) -> str:
    """Preserve prior cytogenetic-style value when possible; else chr from location."""
    for item in gene.get("headline_stats") or []:
        if item.get("key") == "location" and item.get("value"):
            # keep e.g. 17p13.1 if already present
            return item["value"]
    loc = my.get("location") or gene.get("location") or {}
    chrom = loc.get("chrom")
    return f"{chrom}" if chrom else "—"


def merge_gene(
    gene: dict[str, Any],
    my: dict[str, Any],
    cv: dict[str, Any],
    gx: dict[str, Any],
    as_of: str,
) -> dict[str, Any]:
    """Merge sync results into gene JSON; strip seed placeholders."""
    out = dict(gene)

    # --- identity ---
    identity_ok = bool(my.get("ok") and my.get("id"))
    if identity_ok:
        out["id"] = my["id"]
        if my.get("aliases") is not None:
            out["aliases"] = my["aliases"]
        if my.get("type"):
            out["type"] = my["type"]
        if my.get("location") and my["location"].get("start") is not None:
            out["location"] = my["location"]
        # Keep existing fluent deck_zh; only rewrite if missing/empty
        if not (out.get("deck_zh") or "").strip() and my.get("summary"):
            summary = my["summary"]
            # light Chinese-ish placeholder: keep English summary clipped — prefer existing zh
            out["deck_zh"] = (summary[:220] + "…") if len(summary) > 220 else summary
        if my.get("pathways"):
            out["pathways"] = my["pathways"]
        uniprot = my.get("uniprot")
        out["structure"] = {
            "alphafold_url": my.get("alphafold_url"),
            "preview_image": (out.get("structure") or {}).get("preview_image"),
        }
    else:
        # keep prior identity; still ensure structure key
        out.setdefault("structure", {"alphafold_url": None, "preview_image": None})

    # --- clinvar ---
    clinvar_ok = bool(cv.get("ok") and cv.get("pathogenic") is not None)
    if clinvar_ok:
        p = int(cv["pathogenic"])
        lp = int(cv["likely_pathogenic"])
        out["variants_summary"] = {
            "clinvar_pathogenic": p,
            "clinvar_likely_pathogenic": lp,
            "note_zh": "非诊断结论；计数来自 ClinVar E-utilities 检索，非正式导出 tar。本期无逐条收录。",
        }
        out["variants_detail"] = []
        clinvar_plp_value: Any = p + lp
        clinvar_conf = "high"
        clinvar_src_version = f"{as_of}; esearch count by gene+clinsig"
        clinvar_src_name = "ClinVar"
    else:
        out["variants_summary"] = {
            "clinvar_pathogenic": None,
            "clinvar_likely_pathogenic": None,
            "note_zh": "非诊断结论；本期 ClinVar 检索失败或未收录，非正式导出 tar。",
        }
        out["variants_detail"] = []
        clinvar_plp_value = "本期未收录"
        clinvar_conf = "unavailable"
        clinvar_src_version = f"{as_of}; esearch failed"
        clinvar_src_name = "ClinVar"
        if cv.get("error"):
            out["variants_summary"]["note_zh"] += f"（{cv['error'][:80]}）"

    # --- gtex ---
    gtex_ok = bool(gx.get("ok") and gx.get("tissues"))
    if gtex_ok:
        tissues = gx["tissues"]
        out["expression"] = {"source": "GTEx", "unit": "TPM", "tissues": tissues}
        top_en = gx.get("top_tissue_en") or tissues[0]["name"]
        top_zh = gx.get("top_tissue_zh") or short_zh_for_headline(top_en)
        top_tissue_value = top_zh
        top_tissue_detail = top_en
        expr_conf = "high"
        gtex_src_version = f"{as_of}; GTEx Portal API v2 medianGeneExpression"
        gtex_src_conf = "high"
    else:
        out["expression"] = {"source": "GTEx", "unit": "TPM", "tissues": []}
        top_tissue_value = "本期未收录"
        top_tissue_detail = None
        expr_conf = "unavailable"
        gtex_src_version = f"{as_of}; GTEx API unavailable"
        gtex_src_conf = "unavailable"
        if gx.get("error"):
            gtex_src_version += f" — {gx['error'][:100]}"

    # --- headline_stats ---
    loc_value = _location_headline_value(out, my)
    headline = [
        {"key": "location", "label_zh": "基因组位置", "value": loc_value},
        {
            "key": "clinvar_plp",
            "label_zh": "ClinVar 致病/可能致病",
            "value": clinvar_plp_value,
            "as_of": as_of,
        },
        {
            "key": "top_tissue",
            "label_zh": "GTEx 最高表达",
            "value": top_tissue_value,
            "as_of": as_of,
        },
    ]
    if top_tissue_detail:
        headline[2]["detail"] = top_tissue_detail
    out["headline_stats"] = headline

    # --- confidence ---
    out["confidence"] = {
        "identity": "high" if identity_ok else "unavailable",
        "expression": expr_conf,
        "clinvar": clinvar_conf if clinvar_ok else "unavailable",
    }

    # --- sources (no seed) ---
    alphafold_url = (out.get("structure") or {}).get("alphafold_url")
    sources = [
        {
            "name": "MyGene.info",
            "url": "https://mygene.info",
            "version": f"v3; queried {as_of}",
            "confidence": "high" if identity_ok else "unavailable",
        },
        {
            "name": "Ensembl / GRCh38 via MyGene",
            "url": "https://www.ensembl.org",
            "version": "GRCh38",
            "confidence": "high" if identity_ok else "unavailable",
        },
        {
            "name": "KEGG via MyGene",
            "url": "https://www.kegg.jp",
            "version": "via MyGene pathway.kegg",
            "confidence": "medium" if (my.get("pathways")) else "unavailable",
        },
        {
            "name": "AlphaFold DB",
            "url": alphafold_url or "https://alphafold.ebi.ac.uk",
            "version": "entry by UniProt" if alphafold_url else "no UniProt",
            "confidence": "high" if alphafold_url else "unavailable",
        },
        {
            "name": clinvar_src_name,
            "url": "https://www.ncbi.nlm.nih.gov/clinvar/",
            "version": clinvar_src_version,
            "confidence": clinvar_conf if clinvar_ok else "unavailable",
        },
        {
            "name": "GTEx",
            "url": "https://gtexportal.org",
            "version": gtex_src_version,
            "confidence": gtex_src_conf,
            "note": "组织中文（name_zh / top_tissue.value）为展示映射，非 GTEx 官方字段。",
        },
    ]
    out["sources"] = sources

    # --- colophon ---
    out["colophon"] = {
        "data_as_of": as_of,
        "edition": EDITION,
        "disclaimer_zh": "科研/教学信息工具，非医疗器械，不提供诊断建议。",
    }

    return out


def update_index(as_of: str, genes_meta: list[dict[str, str]]) -> None:
    index = {
        "edition": EDITION,
        "data_as_of": as_of,
        "count": len(genes_meta),
        "genes": genes_meta,
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_meta(as_of: str, summary: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    synced_at = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    meta = {
        "edition": EDITION,
        "data_as_of": as_of,
        "synced_at": synced_at,
        "summary": summary,
    }
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # one-line ops log (Asia/Shanghai date); does not change gene edition
    log_dir = CACHE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    day = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d")
    line = (
        f"{synced_at} as_of={as_of} genes={summary.get('total')} "
        f"mygene={summary.get('ok_mygene')} clinvar={summary.get('ok_clinvar')} "
        f"gtex={summary.get('ok_gtex')}\n"
    )
    with (log_dir / f"sync_all-{day}.log").open("a", encoding="utf-8") as fh:
        fh.write(line)


def main() -> int:
    as_of = today_shanghai()
    env_syms = os.environ.get("SYNC_SYMBOLS", "").strip()
    symbols = [s.strip().upper() for s in env_syms.split(",") if s.strip()] if env_syms else list(DEMO_SYMBOLS)

    print(f"[sync_all] edition={EDITION} data_as_of={as_of} genes={len(symbols)}")
    print(f"[sync_all] ROOT={ROOT}")

    results: list[dict[str, Any]] = []
    genes_meta: list[dict[str, str]] = []

    for sym in symbols:
        print(f"\n=== {sym} ===")
        status = {"symbol": sym, "mygene": False, "clinvar": False, "gtex": False, "errors": []}
        try:
            gene = load_gene(sym)
        except FileNotFoundError:
            print(f"  FAIL: missing {GENES_DIR / f'{sym}.json'}")
            status["errors"].append("missing gene json")
            results.append(status)
            continue

        # MyGene first (need ensembl id for GTEx)
        print("  MyGene…")
        my = fetch_mygene(sym)
        status["mygene"] = bool(my.get("ok"))
        if not my.get("ok"):
            status["errors"].append(f"mygene: {my.get('error')}")
            print(f"  MyGene FAIL: {my.get('error')}")
        else:
            print(f"  MyGene OK id={my.get('id')} uniprot={my.get('uniprot')}")

        ensembl_id = my.get("id") or gene.get("id")
        if not ensembl_id:
            status["errors"].append("no ensembl id")
            print("  SKIP GTEx: no ensembl id")
            gx = {"ok": False, "error": "no ensembl id", "tissues": []}
        else:
            print(f"  GTEx ({ensembl_id})…")
            gx = fetch_gtex(sym, ensembl_id)
            status["gtex"] = bool(gx.get("ok") and gx.get("tissues"))
            if status["gtex"]:
                print(f"  GTEx OK tissues={len(gx['tissues'])} top={gx.get('top_tissue_zh')}")
            else:
                status["errors"].append(f"gtex: {gx.get('error')}")
                print(f"  GTEx FAIL/empty: {gx.get('error')}")

        print("  ClinVar…")
        cv = fetch_clinvar(sym)
        status["clinvar"] = bool(cv.get("ok"))
        if status["clinvar"]:
            print(f"  ClinVar OK P={cv.get('pathogenic')} LP={cv.get('likely_pathogenic')}")
        else:
            status["errors"].append(f"clinvar: {cv.get('error')}")
            print(f"  ClinVar FAIL: {cv.get('error')}")

        merged = merge_gene(gene, my, cv, gx, as_of)
        save_gene(sym, merged)
        genes_meta.append({"symbol": sym, "id": merged.get("id") or "", "file": f"genes/{sym}.json"})
        print(f"  wrote genes/{sym}.json")
        results.append(status)

    # For full demo set, rebuild index from DEMO order if syncing all;
    # otherwise refresh only synced entries on top of existing index.
    if set(symbols) >= set(DEMO_SYMBOLS):
        # stable DEMO order
        id_map = {g["symbol"]: g for g in genes_meta}
        genes_meta = [
            id_map[s] if s in id_map else {"symbol": s, "id": "", "file": f"genes/{s}.json"}
            for s in DEMO_SYMBOLS
        ]
        update_index(as_of, genes_meta)
    else:
        # partial: update as_of/edition and patch matching symbols
        try:
            index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            index = {"genes": []}
        by_sym = {g["symbol"]: g for g in genes_meta}
        new_genes = []
        for g in index.get("genes") or []:
            sym = g.get("symbol")
            new_genes.append(by_sym.get(sym, g))
        for g in genes_meta:
            if g["symbol"] not in {x.get("symbol") for x in new_genes}:
                new_genes.append(g)
        update_index(as_of, new_genes)

    summary = {
        "genes": results,
        "ok_mygene": sum(1 for r in results if r["mygene"]),
        "ok_clinvar": sum(1 for r in results if r["clinvar"]),
        "ok_gtex": sum(1 for r in results if r["gtex"]),
        "total": len(results),
    }
    write_meta(as_of, summary)

    print("\n========== SUMMARY ==========")
    for r in results:
        flags = []
        flags.append("MyGene✓" if r["mygene"] else "MyGene✗")
        flags.append("ClinVar✓" if r["clinvar"] else "ClinVar✗")
        flags.append("GTEx✓" if r["gtex"] else "GTEx✗")
        err = f"  errs={r['errors']}" if r["errors"] else ""
        print(f"  {r['symbol']}: {' '.join(flags)}{err}")
    print(
        f"totals: mygene={summary['ok_mygene']}/{summary['total']} "
        f"clinvar={summary['ok_clinvar']}/{summary['total']} "
        f"gtex={summary['ok_gtex']}/{summary['total']}"
    )
    print(f"meta → {META_PATH}")
    print(f"index → {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
