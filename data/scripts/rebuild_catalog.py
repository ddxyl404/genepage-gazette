# -*- coding: utf-8 -*-
"""
Rebuild data/index.json from genes/*.json and export CSV catalog.

Also writes AlphaFold consistency audit to exports/alphafold_audit.md.

Usage:
  python3 /workspace/genepage/data/scripts/rebuild_catalog.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import zoneinfo

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent  # data/
GENES_DIR = ROOT / "genes"
EXPORTS_DIR = ROOT / "exports"
INDEX_PATH = ROOT / "index.json"
AUDIT_PATH = EXPORTS_DIR / "alphafold_audit.md"

sys.path.insert(0, str(SCRIPTS))
from export_csv import DEMO_ORDER, export_csv  # noqa: E402

CATALOG_SCHEMA = "1.0"


def _headline(gene: dict[str, Any], key: str) -> dict[str, Any] | None:
    for h in gene.get("headline_stats") or []:
        if h.get("key") == key:
            return h
    return None


def _plp_value(raw: Any) -> int | None:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float) and raw == int(raw):
        return int(raw)
    return None


def gene_to_index_entry(gene: dict[str, Any], file_rel: str) -> dict[str, Any]:
    h_loc = _headline(gene, "location") or {}
    h_plp = _headline(gene, "clinvar_plp") or {}
    h_tissue = _headline(gene, "top_tissue") or {}
    structure = gene.get("structure") or {}
    colophon = gene.get("colophon") or {}
    entry: dict[str, Any] = {
        "symbol": gene.get("symbol"),
        "id": gene.get("id"),
        "file": file_rel,
        "aliases": gene.get("aliases") or [],
        "type": gene.get("type"),
        "location_label": h_loc.get("value"),
        "clinvar_plp": _plp_value(h_plp.get("value")),
        "top_tissue": h_tissue.get("value"),
    }
    detail = h_tissue.get("detail")
    if detail:
        entry["top_tissue_detail"] = detail
    entry["alphafold_url"] = structure.get("alphafold_url")
    entry["data_as_of"] = colophon.get("data_as_of")
    entry["edition"] = colophon.get("edition")
    return entry


def load_genes_ordered() -> list[tuple[str, Path, dict[str, Any]]]:
    by_symbol: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in sorted(GENES_DIR.glob("*.json")):
        gene = json.loads(path.read_text(encoding="utf-8"))
        sym = gene.get("symbol") or path.stem
        by_symbol[sym] = (path, gene)

    order: list[str] = []
    for sym in DEMO_ORDER:
        if sym in by_symbol:
            order.append(sym)
    for sym in sorted(by_symbol):
        if sym not in order:
            order.append(sym)
    return [(sym, by_symbol[sym][0], by_symbol[sym][1]) for sym in order]


def rebuild_index() -> dict[str, Any]:
    ordered = load_genes_ordered()
    entries: list[dict[str, Any]] = []
    editions: list[str] = []
    as_ofs: list[str] = []

    for sym, path, gene in ordered:
        expected = GENES_DIR / f"{sym}.json"
        if path.resolve() != expected.resolve() and path.stem != sym:
            raise SystemExit(f"symbol/file mismatch: {sym} vs {path.name}")
        file_rel = f"genes/{sym}.json"
        if not (ROOT / file_rel).is_file():
            raise SystemExit(f"missing file for index entry: {file_rel}")
        if gene.get("symbol") != sym:
            raise SystemExit(f"symbol mismatch in {path.name}: {gene.get('symbol')} != {sym}")
        if not gene.get("id"):
            raise SystemExit(f"missing id in {path.name}")
        entry = gene_to_index_entry(gene, file_rel)
        entries.append(entry)
        if entry.get("edition"):
            editions.append(str(entry["edition"]))
        if entry.get("data_as_of"):
            as_ofs.append(str(entry["data_as_of"]))

    # Top-level edition / data_as_of: prefer majority / max as_of from genes.
    edition = max(set(editions), key=editions.count) if editions else "0.3.0-p35"
    data_as_of = max(as_ofs) if as_ofs else datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")

    index = {
        "edition": edition,
        "data_as_of": data_as_of,
        "count": len(entries),
        "catalog_schema": CATALOG_SCHEMA,
        "genes": entries,
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index


def audit_alphafold() -> dict[str, Any]:
    """Check structure.alphafold_url vs sources AlphaFold entry URL."""
    passed: list[str] = []
    issues: list[str] = []
    details: list[dict[str, Any]] = []

    for sym, path, gene in load_genes_ordered():
        structure = gene.get("structure") or {}
        struct_url = structure.get("alphafold_url")
        af_sources = [
            s
            for s in (gene.get("sources") or [])
            if "alphafold" in str(s.get("name") or "").lower()
            or "alphafold" in str(s.get("url") or "").lower()
        ]
        status = "pass"
        note = ""
        if struct_url and af_sources:
            urls = {s.get("url") for s in af_sources}
            if struct_url in urls:
                status = "pass"
                note = "structure.alphafold_url matches sources AlphaFold url"
                passed.append(sym)
            else:
                status = "mismatch"
                note = f"structure={struct_url!r} sources={[s.get('url') for s in af_sources]!r}"
                issues.append(f"{sym}: {note}")
        elif struct_url and not af_sources:
            # Allowed: structure has link, no independent sources row.
            status = "pass"
            note = "structure has alphafold_url; no independent AlphaFold sources row (allowed)"
            passed.append(sym)
        elif not struct_url and af_sources:
            status = "issue"
            note = f"sources has AlphaFold but structure.alphafold_url is null/empty: {[s.get('url') for s in af_sources]!r}"
            issues.append(f"{sym}: {note}")
        else:
            status = "pass"
            note = "no AlphaFold url in structure or sources"
            passed.append(sym)
        details.append(
            {
                "symbol": sym,
                "status": status,
                "structure_url": struct_url,
                "source_urls": [s.get("url") for s in af_sources],
                "note": note,
            }
        )

    return {"passed": passed, "issues": issues, "details": details}


def write_audit(report: dict[str, Any]) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        "# AlphaFold URL consistency audit",
        "",
        f"**generated:** {now} (Asia/Shanghai)",
        f"**genes checked:** {len(report['details'])}",
        f"**passed:** {len(report['passed'])}",
        f"**issues:** {len(report['issues'])}",
        "",
        "## Rule",
        "",
        "`structure.alphafold_url` must match the AlphaFold entry in `sources[]` when both exist.",
        "If `sources` has no AlphaFold row but `structure` has a URL, that is allowed.",
        "",
        "## Results",
        "",
    ]
    if not report["issues"]:
        lines.append("**All genes passed.**")
        lines.append("")
    else:
        lines.append("### Issues")
        lines.append("")
        for issue in report["issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    lines.append("| symbol | status | structure.alphafold_url | sources AlphaFold url(s) |")
    lines.append("|--------|--------|-------------------------|--------------------------|")
    for d in report["details"]:
        src = ", ".join(u or "—" for u in (d["source_urls"] or ["—"]))
        struct = d["structure_url"] or "—"
        lines.append(f"| {d['symbol']} | {d['status']} | `{struct}` | `{src}` |")
    lines.append("")

    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return AUDIT_PATH


def validate_index(index: dict[str, Any]) -> None:
    genes = index.get("genes") or []
    if len(genes) != 10:
        raise SystemExit(f"expected 10 genes in index, got {len(genes)}")
    for g in genes:
        for key in ("symbol", "id", "file"):
            if not g.get(key):
                raise SystemExit(f"index entry missing {key}: {g}")
        path = ROOT / g["file"]
        if not path.is_file():
            raise SystemExit(f"index file missing: {g['file']}")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if loaded.get("symbol") != g["symbol"] or loaded.get("id") != g["id"]:
            raise SystemExit(
                f"index/gene mismatch for {g['file']}: "
                f"index=({g['symbol']},{g['id']}) gene=({loaded.get('symbol')},{loaded.get('id')})"
            )


def main() -> None:
    index = rebuild_index()
    validate_index(index)
    print(f"index → {INDEX_PATH} (count={index['count']}, edition={index['edition']}, catalog_schema={index.get('catalog_schema')})")

    report = audit_alphafold()
    audit_path = write_audit(report)
    if report["issues"]:
        print(f"alphafold audit → {audit_path}  ISSUES: {len(report['issues'])}")
        for issue in report["issues"]:
            print(f"  - {issue}")
    else:
        print(f"alphafold audit → {audit_path}  all {len(report['passed'])} passed")

    csv_path = export_csv()
    print(f"csv → {csv_path}")


if __name__ == "__main__":
    main()
