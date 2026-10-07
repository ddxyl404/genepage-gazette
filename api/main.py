"""GenePage Gazette API — seed JSON from GENEPAGE_DATA_DIR (single source of truth)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import csv
import io

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

DATA_DIR = Path(
    os.environ.get("GENEPAGE_DATA_DIR", "/workspace/genepage/data")
).resolve()
GENES_DIR = DATA_DIR / "genes"
INDEX_PATH = DATA_DIR / "index.json"
# Cache files are provenance/re-run inputs; genes/*.json remains the API source.
CACHE_DIR = Path(
    os.environ.get("GENEPAGE_CACHE_DIR", "/workspace/genepage/data/cache")
).resolve()
CACHE_KINDS = ("clinvar", "gtex", "mygene")
# P3.6 figure assets (cytobands under DATA_DIR; AlphaFold previews under CACHE_DIR)
CYTOBANDS_DIR = DATA_DIR / "figures" / "cytobands"
ALPHAFOLD_DIR = CACHE_DIR / "alphafold"
CYTOBANDS_DIR.mkdir(parents=True, exist_ok=True)
ALPHAFOLD_DIR.mkdir(parents=True, exist_ok=True)

_MEDIA_BY_SUFFIX = {
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def _chrom_stems(chrom: str) -> list[str]:
    """Normalize chrom like '17' / 'chr17' / 'CHR17' → try both bare and chr-prefixed stems."""
    raw = chrom.strip()
    if not raw:
        return []
    bare = raw
    lower = raw.lower()
    if lower.startswith("chr"):
        bare = raw[3:]
    stems: list[str] = []
    for s in (bare, f"chr{bare}", f"Chr{bare}", f"CHR{bare}", raw):
        if s and s not in stems:
            stems.append(s)
    return stems


def _resolve_cytoband(chrom: str) -> Path | None:
    for stem in _chrom_stems(chrom):
        for ext in (".json", ".svg"):
            candidate = CYTOBANDS_DIR / f"{stem}{ext}"
            if candidate.is_file():
                return candidate
    return None


def _resolve_alphafold(symbol: str) -> Path | None:
    key = symbol.strip()
    if not key:
        return None
    # Prefer exact SYMBOL upper, then case-insensitive scan
    for ext in (".png", ".webp", ".jpg", ".jpeg"):
        candidate = ALPHAFOLD_DIR / f"{key.upper()}{ext}"
        if candidate.is_file():
            return candidate
    if not ALPHAFOLD_DIR.is_dir():
        return None
    key_upper = key.upper()
    # Prefer png > webp > jpg among case-insensitive matches
    found: dict[str, Path] = {}
    for path in ALPHAFOLD_DIR.iterdir():
        if not path.is_file():
            continue
        if path.stem.upper() != key_upper:
            continue
        suf = path.suffix.lower()
        if suf in (".png", ".webp", ".jpg", ".jpeg") and suf not in found:
            found[suf] = path
    for ext in (".png", ".webp", ".jpg", ".jpeg"):
        if ext in found:
            return found[ext]
    return None


app = FastAPI(title="GenePage Gazette API", version="0.1.0-preview")

def _cors_origins() -> list[str]:
    """Local dev defaults + optional GENEPAGE_CORS_ORIGINS (comma-separated)."""
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    extra = os.environ.get("GENEPAGE_CORS_ORIGINS", "")
    for part in extra.split(","):
        origin = part.strip()
        if origin and origin not in origins:
            origins.append(origin)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_index() -> dict[str, Any]:
    if not INDEX_PATH.is_file():
        raise HTTPException(status_code=500, detail=f"index missing: {INDEX_PATH}")
    with INDEX_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _load_gene_file(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _all_gene_paths() -> list[Path]:
    if not GENES_DIR.is_dir():
        return []
    return sorted(GENES_DIR.glob("*.json"))


def _find_gene(id_or_symbol: str) -> dict[str, Any] | None:
    """Resolve by HGNC symbol, alias, or Ensembl id (case-insensitive)."""
    key = id_or_symbol.strip()
    if not key:
        return None
    key_upper = key.upper()

    # Fast path: symbol filename
    by_symbol = GENES_DIR / f"{key_upper}.json"
    if by_symbol.is_file():
        # Prefer exact case from file; still try common casing
        return _load_gene_file(by_symbol)

    # Also try exact filename as given
    by_exact = GENES_DIR / f"{key}.json"
    if by_exact.is_file():
        return _load_gene_file(by_exact)

    for path in _all_gene_paths():
        gene = _load_gene_file(path)
        symbol = str(gene.get("symbol", "")).upper()
        gene_id = str(gene.get("id", "")).upper()
        aliases = [str(a).upper() for a in gene.get("aliases") or []]
        if key_upper == symbol or key_upper == gene_id or key_upper in aliases:
            return gene
    return None


@app.get("/api/cache/status")
def cache_status() -> dict[str, Any]:
    """List cached symbols without overlaying cache data onto gene JSON."""
    overlays: dict[str, list[str]] = {}
    for kind in CACHE_KINDS:
        kind_dir = CACHE_DIR / kind
        symbols = {path.stem.upper() for path in kind_dir.glob("*.json")} if kind_dir.is_dir() else set()
        overlays[kind] = sorted(symbols)
    meta_path = CACHE_DIR / "meta.json"
    return {
        "cache_dir": str(CACHE_DIR),
        "overlays": overlays,
        "meta": {"present": meta_path.is_file(), "path": str(meta_path)},
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    index = _load_index() if INDEX_PATH.is_file() else {}
    return {
        "status": "ok",
        "data_dir": str(DATA_DIR),
        "edition": index.get("edition"),
        "data_as_of": index.get("data_as_of"),
        "gene_count": index.get("count", len(_all_gene_paths())),
    }


@app.get("/api/figures/status")
def figures_status() -> dict[str, Any]:
    """List available cytoband chrom files and AlphaFold preview symbols."""
    cytobands: list[str] = []
    if CYTOBANDS_DIR.is_dir():
        for path in sorted(CYTOBANDS_DIR.iterdir()):
            if path.is_file() and path.suffix.lower() in (".json", ".svg"):
                cytobands.append(path.name)
    alphafold: list[str] = []
    if ALPHAFOLD_DIR.is_dir():
        for path in sorted(ALPHAFOLD_DIR.iterdir()):
            if path.is_file() and path.suffix.lower() in (".png", ".webp", ".jpg", ".jpeg"):
                alphafold.append(path.stem.upper())
    # unique symbols preserving sort
    alphafold = sorted(set(alphafold))
    return {
        "cytobands_dir": str(CYTOBANDS_DIR),
        "alphafold_dir": str(ALPHAFOLD_DIR),
        "cytobands": cytobands,
        "alphafold": alphafold,
    }


@app.get("/api/figures/cytobands/{chrom}")
def get_cytoband_figure(chrom: str):
    """Serve cytoband JSON or SVG from data/figures/cytobands/."""
    path = _resolve_cytoband(chrom)
    if path is None:
        raise HTTPException(status_code=404, detail=f"cytoband figure not found: {chrom}")
    media = _MEDIA_BY_SUFFIX.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(path, media_type=media)


@app.get("/api/figures/alphafold/{symbol}")
def get_alphafold_preview(symbol: str):
    """Serve AlphaFold static preview from data/cache/alphafold/ (png > webp > jpg)."""
    path = _resolve_alphafold(symbol)
    if path is None:
        raise HTTPException(status_code=404, detail=f"alphafold preview not found: {symbol}")
    media = _MEDIA_BY_SUFFIX.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(path, media_type=media)


@app.get("/api/gene/{gene_id}")
def get_gene(gene_id: str) -> dict[str, Any]:
    gene = _find_gene(gene_id)
    if gene is None:
        raise HTTPException(status_code=404, detail=f"gene not found: {gene_id}")
    return gene


@app.get("/api/search")
def search(q: str = Query("", min_length=0)) -> dict[str, Any]:
    query = q.strip()
    index = _load_index()
    results: list[dict[str, Any]] = []

    if not query:
        for entry in index.get("genes") or []:
            symbol = entry.get("symbol")
            item = {
                "symbol": symbol,
                "id": entry.get("id"),
                "file": entry.get("file"),
            }
            gene_path = GENES_DIR / f"{symbol}.json"
            if gene_path.is_file():
                gene = _load_gene_file(gene_path)
                item["aliases"] = gene.get("aliases") or []
                item["type"] = gene.get("type")
                item["deck_zh"] = gene.get("deck_zh")
                item["deck_en"] = gene.get("deck_en")
                loc = None
                for stat in gene.get("headline_stats") or []:
                    if stat.get("key") == "location":
                        loc = stat.get("value")
                        break
                item["location"] = loc
            results.append(item)
        return {"q": q, "count": len(results), "results": results}

    q_upper = query.upper()
    seen: set[str] = set()

    for path in _all_gene_paths():
        gene = _load_gene_file(path)
        symbol = str(gene.get("symbol", ""))
        gene_id = str(gene.get("id", ""))
        aliases = [str(a) for a in gene.get("aliases") or []]
        haystack = [symbol.upper(), gene_id.upper()] + [a.upper() for a in aliases]
        if any(q_upper in h or h.startswith(q_upper) for h in haystack):
            if symbol.upper() in seen:
                continue
            seen.add(symbol.upper())
            loc = None
            for stat in gene.get("headline_stats") or []:
                if stat.get("key") == "location":
                    loc = stat.get("value")
                    break
            results.append(
                {
                    "symbol": symbol,
                    "id": gene_id,
                    "aliases": aliases,
                    "location": loc,
                    "type": gene.get("type"),
                    "deck_zh": gene.get("deck_zh"),
                    "deck_en": gene.get("deck_en"),
                }
            )

    return {"q": q, "count": len(results), "results": results}


@app.get("/api/index")
def get_index() -> dict[str, Any]:
    """Catalog listing — same index.json as data truth source."""
    return _load_index()


@app.get("/api/export/genes.csv")
def export_genes_csv():
    """Stream CSV of all genes from data/genes/*.json (index order preferred)."""
    index = _load_index() if INDEX_PATH.is_file() else {}
    edition_default = index.get("edition") or ""
    as_of_default = index.get("data_as_of") or ""

    # Prefer index order; fall back to filesystem
    ordered_paths: list[Path] = []
    seen: set[str] = set()
    for entry in index.get("genes") or []:
        symbol = entry.get("symbol")
        if not symbol:
            continue
        path = GENES_DIR / f"{symbol}.json"
        if path.is_file():
            ordered_paths.append(path)
            seen.add(symbol.upper())
    for path in _all_gene_paths():
        if path.stem.upper() not in seen:
            ordered_paths.append(path)

    def _stat_value(gene: dict[str, Any], key: str) -> Any:
        for stat in gene.get("headline_stats") or []:
            if stat.get("key") == key:
                return stat.get("value")
        return None

    def _clinvar_plp(gene: dict[str, Any]) -> Any:
        plp = _stat_value(gene, "clinvar_plp")
        if plp is not None and plp != "":
            return plp
        vs = gene.get("variants_summary") or {}
        p = vs.get("clinvar_pathogenic")
        lp = vs.get("clinvar_likely_pathogenic")
        if isinstance(p, (int, float)) or isinstance(lp, (int, float)):
            return (p or 0) + (lp or 0)
        return ""

    def generate():
        buf = io.StringIO()
        # UTF-8 BOM for Excel
        yield "\ufeff"
        writer = csv.writer(buf)
        writer.writerow(
            [
                "symbol",
                "id",
                "aliases",
                "chrom",
                "start",
                "end",
                "clinvar_plp",
                "top_tissue",
                "data_as_of",
                "edition",
                "sources_count",
            ]
        )
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)

        for path in ordered_paths:
            gene = _load_gene_file(path)
            loc = gene.get("location") or {}
            colophon = gene.get("colophon") or {}
            aliases = gene.get("aliases") or []
            sources = gene.get("sources") or []
            writer.writerow(
                [
                    gene.get("symbol") or path.stem,
                    gene.get("id") or "",
                    ";".join(str(a) for a in aliases),
                    loc.get("chrom") or "",
                    loc.get("start") if loc.get("start") is not None else "",
                    loc.get("end") if loc.get("end") is not None else "",
                    _clinvar_plp(gene),
                    _stat_value(gene, "top_tissue") or "",
                    colophon.get("data_as_of") or as_of_default,
                    colophon.get("edition") or edition_default,
                    len(sources),
                ]
            )
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    headers = {
        "Content-Disposition": 'attachment; filename="genepage-genes.csv"',
        "Cache-Control": "public, max-age=60",
    }
    return StreamingResponse(
        generate(),
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )
