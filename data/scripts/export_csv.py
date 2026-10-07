# -*- coding: utf-8 -*-
"""
Export genes/*.json → exports/genes_catalog.csv

Usage:
  python3 /workspace/genepage/data/scripts/export_csv.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent  # data/
GENES_DIR = ROOT / "genes"
EXPORTS_DIR = ROOT / "exports"
OUT_CSV = EXPORTS_DIR / "genes_catalog.csv"
INDEX_PATH = ROOT / "index.json"

# Prefer catalog order from index.json when present.
DEMO_ORDER = [
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

COLUMNS = [
    "symbol",
    "ensembl_id",
    "aliases",
    "type",
    "chrom",
    "start",
    "end",
    "assembly",
    "location_label",
    "clinvar_pathogenic",
    "clinvar_likely_pathogenic",
    "clinvar_plp",
    "top_tissue_zh",
    "top_tissue_en",
    "alphafold_url",
    "data_as_of",
    "edition",
    "sources",
    "deck_zh",
    "deck_en",
]


def _headline(gene: dict[str, Any], key: str) -> dict[str, Any] | None:
    for h in gene.get("headline_stats") or []:
        if h.get("key") == key:
            return h
    return None


def _fmt_sources(sources: list[dict[str, Any]] | None) -> str:
    parts: list[str] = []
    for s in sources or []:
        name = str(s.get("name") or "")
        url = str(s.get("url") or "")
        version = str(s.get("version") or "")
        confidence = str(s.get("confidence") or "")
        parts.append(f"{name}|{url}|{version}|{confidence}")
    return ";".join(parts)


def gene_to_row(gene: dict[str, Any]) -> dict[str, Any]:
    loc = gene.get("location") or {}
    vs = gene.get("variants_summary") or {}
    structure = gene.get("structure") or {}
    colophon = gene.get("colophon") or {}
    h_loc = _headline(gene, "location") or {}
    h_plp = _headline(gene, "clinvar_plp") or {}
    h_tissue = _headline(gene, "top_tissue") or {}
    aliases = gene.get("aliases") or []
    return {
        "symbol": gene.get("symbol") or "",
        "ensembl_id": gene.get("id") or "",
        "aliases": ";".join(str(a) for a in aliases),
        "type": gene.get("type") or "",
        "chrom": loc.get("chrom") if loc.get("chrom") is not None else "",
        "start": loc.get("start") if loc.get("start") is not None else "",
        "end": loc.get("end") if loc.get("end") is not None else "",
        "assembly": loc.get("assembly") or "",
        "location_label": h_loc.get("value") if h_loc.get("value") is not None else "",
        "clinvar_pathogenic": vs.get("clinvar_pathogenic")
        if vs.get("clinvar_pathogenic") is not None
        else "",
        "clinvar_likely_pathogenic": vs.get("clinvar_likely_pathogenic")
        if vs.get("clinvar_likely_pathogenic") is not None
        else "",
        "clinvar_plp": h_plp.get("value") if h_plp.get("value") is not None else "",
        "top_tissue_zh": h_tissue.get("value") if h_tissue.get("value") is not None else "",
        "top_tissue_en": h_tissue.get("detail") if h_tissue.get("detail") is not None else "",
        "alphafold_url": structure.get("alphafold_url") or "",
        "data_as_of": colophon.get("data_as_of") or "",
        "edition": colophon.get("edition") or "",
        "sources": _fmt_sources(gene.get("sources")),
        "deck_zh": gene.get("deck_zh") or "",
        "deck_en": gene.get("deck_en") or "",
    }


def load_gene_paths() -> list[Path]:
    """Return gene JSON paths in index / DEMO order, then any extras."""
    by_symbol: dict[str, Path] = {}
    for p in sorted(GENES_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sym = data.get("symbol") or p.stem
        except Exception:
            sym = p.stem
        by_symbol[sym] = p

    order: list[str] = []
    if INDEX_PATH.exists():
        try:
            index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
            for g in index.get("genes") or []:
                sym = g.get("symbol")
                if sym and sym in by_symbol and sym not in order:
                    order.append(sym)
        except Exception:
            pass
    for sym in DEMO_ORDER:
        if sym in by_symbol and sym not in order:
            order.append(sym)
    for sym in sorted(by_symbol):
        if sym not in order:
            order.append(sym)
    return [by_symbol[s] for s in order]


def export_csv(out_path: Path | None = None) -> Path:
    out = out_path or OUT_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for path in load_gene_paths():
        gene = json.loads(path.read_text(encoding="utf-8"))
        rows.append(gene_to_row(gene))

    # UTF-8 with BOM for Excel-friendliness on Windows.
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out


def main() -> None:
    out = export_csv()
    print(f"wrote {out} ({sum(1 for _ in out.open(encoding='utf-8-sig')) - 1} genes)")


if __name__ == "__main__":
    main()
