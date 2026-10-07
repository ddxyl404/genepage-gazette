# -*- coding: utf-8 -*-
"""
P3.6: sync cytobands, UniProt domains, expression captions, AlphaFold previews.

Usage:
  python3 /workspace/genepage/data/scripts/sync_figures.py
  SYNC_SYMBOLS=TP53,BRCA1 python3 .../sync_figures.py

Does not touch web/api/visual CSS. Local box only.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import zoneinfo

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent  # data/
GENES_DIR = ROOT / "genes"
FIGURES_CYTO = ROOT / "figures" / "cytobands"
CACHE_AF = ROOT / "cache" / "alphafold"
CACHE_UP = ROOT / "cache" / "uniprot"
CYTO_SRC = Path("/tmp/cytoBandIdeo.txt")

EDITION = "0.3.1-p36"
ASIA = zoneinfo.ZoneInfo("Asia/Shanghai")
TODAY = datetime.now(ASIA).strftime("%Y-%m-%d")

UNIPROT_DELAY = float(os.environ.get("UNIPROT_DELAY", "0.35"))
AF_DELAY = float(os.environ.get("AF_DELAY", "0.35"))
MAX_RETRIES = int(os.environ.get("SYNC_MAX_RETRIES", "3"))
UA = "GenePageGazette/0.3.1-p36 (research/teaching; local sync; polite)"

# Prefer structural / functional feature types for DomainStrip
FEATURE_PRIORITY = (
    "Domain",
    "DNA binding",
    "Zinc finger",
    "Repeat",
    "Transmembrane",
    "Topological domain",
    "Signal",
    "Coiled coil",
    "Motif",
    "Region",
)

NAME_ZH_MAP = [
    (re.compile(r"^Protein kinase$", re.I), "蛋白激酶域"),
    (re.compile(r"^Kinase$", re.I), "激酶域"),
    (re.compile(r"^(DNA-binding domain|DNA binding)$", re.I), "DNA 结合域"),
    (re.compile(r"Zinc finger", re.I), "锌指"),
    (re.compile(r"^Transmembrane", re.I), "跨膜区"),
    (re.compile(r"^Extracellular", re.I), "胞外区"),
    (re.compile(r"^Cytoplasmic", re.I), "胞质区"),
    (re.compile(r"^Signal", re.I), "信号肽"),
    (re.compile(r"nuclear localization", re.I), "核定位信号"),
    (re.compile(r"nuclear export", re.I), "核输出信号"),
    (re.compile(r"Oligomeri[sz]ation", re.I), "寡聚化域"),
    (re.compile(r"Transcription activation", re.I), "转录激活区"),
    (re.compile(r"Disordered", re.I), "无序区"),
    (re.compile(r"Helical", re.I), "螺旋跨膜区"),
    (re.compile(r"BRCT", re.I), "BRCT 域"),
    (re.compile(r"RING", re.I), "RING 域"),
    (re.compile(r"SH2", re.I), "SH2 域"),
    (re.compile(r"SH3", re.I), "SH3 域"),
    (re.compile(r"PHD", re.I), "PHD 域"),
    (re.compile(r"EGF", re.I), "EGF 样域"),
    (re.compile(r"ABC.?transporter", re.I), "ABC 转运域"),
    (re.compile(r"Nucleotide.?binding", re.I), "核苷酸结合域"),
    (re.compile(r"GTPase", re.I), "GTPase 域"),
    (re.compile(r"bHLH|helix-loop-helix", re.I), "螺旋-环-螺旋域"),
    (re.compile(r"Leucine zipper", re.I), "亮氨酸拉链"),
    (re.compile(r"Globin", re.I), "珠蛋白域"),
    (re.compile(r"BRCA2\s*\d+", re.I), "BRC 重复"),
    (re.compile(r"^GTPase", re.I), "GTPase 域"),
    (re.compile(r"Hypervariable", re.I), "高变区"),
    (re.compile(r"TR2 region", re.I), "TR2 区"),
    (re.compile(r"Effector region", re.I), "效应区"),
    (re.compile(r"Apolipoprotein", re.I), "载脂蛋白域"),
    (re.compile(r"Amyloid", re.I), "淀粉样区"),
    (re.compile(r"Coiled coil", re.I), "卷曲螺旋"),
    (re.compile(r"^Approximate$", re.I), "重复区"),
]

EXPR_CAPTION_ZH = "图 · GTEx 中位表达（TPM）· 多组织"
EXPR_CAPTION_EN = "Fig. · GTEx median expression (TPM) · small multiples"

STRUCT_CAPTION_ZH = "图 · AlphaFold 结构预测"
STRUCT_CAPTION_EN = "Fig. · AlphaFold structure prediction"


def _http_get(url: str, dest: Path | None = None, timeout: int = 45) -> bytes:
    last_err: BaseException | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if dest is not None:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = exc
            if attempt >= MAX_RETRIES:
                raise
            time.sleep(AF_DELAY * attempt)
    assert last_err is not None
    raise last_err


def _http_json(url: str, timeout: int = 45) -> Any:
    last_err: BaseException | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = exc
            if attempt >= MAX_RETRIES:
                raise
            time.sleep(AF_DELAY * attempt)
    assert last_err is not None
    raise last_err


def ensure_cytoband_source() -> Path:
    if CYTO_SRC.is_file() and CYTO_SRC.stat().st_size > 1000:
        return CYTO_SRC
    url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/cytoBandIdeo.txt.gz"
    import gzip
    import io

    print(f"  downloading cytoBandIdeo from UCSC…")
    raw = _http_get(url)
    text = gzip.decompress(raw).decode("utf-8")
    CYTO_SRC.write_text(text, encoding="utf-8")
    return CYTO_SRC


def parse_cytobands(chroms: set[str]) -> dict[str, list[dict[str, Any]]]:
    path = ensure_cytoband_source()
    wanted = {f"chr{c}" if not str(c).startswith("chr") else str(c) for c in chroms}
    # also accept bare
    bare = {c[3:] if c.startswith("chr") else c for c in wanted}
    out: dict[str, list[dict[str, Any]]] = {c: [] for c in bare}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        chrom_raw, start, end, name, stain = parts[:5]
        bare_c = chrom_raw[3:] if chrom_raw.startswith("chr") else chrom_raw
        if bare_c not in out:
            continue
        out[bare_c].append(
            {
                "id": name,
                "start": int(start),
                "end": int(end),
                "stain": stain,
            }
        )
    return out


def write_cytoband_files(by_chrom: dict[str, list[dict[str, Any]]]) -> list[Path]:
    FIGURES_CYTO.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    source = "UCSC cytoBandIdeo (hg38 / GRCh38)"
    url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/cytoBandIdeo.txt.gz"
    for chrom, bands in sorted(by_chrom.items(), key=lambda x: (len(x[0]), x[0])):
        if not bands:
            print(f"  WARN: no bands for chrom {chrom}")
            continue
        obj = {
            "chrom": chrom,
            "assembly": "GRCh38",
            "bands": bands,
            "source": source,
            "url": url,
            "band_count": len(bands),
            "fetched_at": TODAY,
        }
        path = FIGURES_CYTO / f"{chrom}.json"
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
        print(f"  cytoband → {path.relative_to(ROOT)} ({len(bands)} bands)")
    return written


def uniprot_acc_from_gene(gene: dict[str, Any]) -> str | None:
    url = (gene.get("structure") or {}).get("alphafold_url") or ""
    m = re.search(r"/entry/([A-Z0-9]+)", url)
    if m:
        return m.group(1)
    for s in gene.get("sources") or []:
        u = s.get("url") or ""
        m = re.search(r"/entry/([A-Z0-9]+)", u)
        if m and "alphafold" in u.lower():
            return m.group(1)
    return None


def _loc_value(loc_part: Any) -> int | None:
    if loc_part is None:
        return None
    if isinstance(loc_part, int):
        return loc_part
    if isinstance(loc_part, dict):
        v = loc_part.get("value")
        if isinstance(v, int):
            return v
    return None


def name_zh_for(name: str, ftype: str) -> str:
    for pat, zh in NAME_ZH_MAP:
        if pat.search(name) or pat.search(ftype):
            return zh
    # type-based fallbacks when description empty
    type_zh = {
        "DNA binding": "DNA 结合域",
        "Zinc finger": "锌指",
        "Transmembrane": "跨膜区",
        "Topological domain": "拓扑结构域",
        "Signal": "信号肽",
        "Coiled coil": "卷曲螺旋",
        "Domain": "结构域",
        "Motif": "基序",
        "Repeat": "重复区",
        "Region": "区域",
    }
    if not name or name.strip() == "":
        return type_zh.get(ftype, ftype)
    return name  # keep English / short desc when no map


def feature_display_name(ftype: str, description: str) -> str:
    desc = (description or "").strip()
    if ftype == "DNA binding":
        return desc or "DNA-binding domain"
    if ftype == "Zinc finger":
        return desc or "Zinc finger"
    if ftype == "Transmembrane":
        return f"Transmembrane ({desc})" if desc else "Transmembrane"
    if ftype == "Topological domain":
        return desc or "Topological domain"
    if ftype == "Signal":
        return "Signal peptide"
    if ftype == "Domain":
        return desc or "Domain"
    if ftype == "Motif":
        return desc or "Motif"
    if ftype == "Repeat":
        return f"Repeat ({desc})" if desc else "Repeat"
    if ftype == "Coiled coil":
        return "Coiled coil"
    if ftype == "Region":
        return desc or "Region"
    return desc or ftype


def region_is_useful(description: str) -> bool:
    d = (description or "").strip()
    if not d:
        return False
    # skip noisy interaction-partner regions and tiny disordered fragments unless named well
    low = d.lower()
    if low.startswith("interaction with"):
        return False
    if low.startswith("required for interaction"):
        return False
    if low == "disordered":
        return False
    useful_kw = (
        "activation",
        "oligomer",
        "repression",
        "binding",
        "catalytic",
        "extracellular",
        "cytoplasmic",
        "nuclear",
        "kinase",
        "receptor",
        "transactivation",
        "transcription",
        "dna",
        "rna",
        "basic",
        "acidic",
        "globular",
        "peptidase",
        "amyloid",
        "repeat",
        "tr2",
        "hypervariable",
        "effector",
        "stimulation",
        "polymerization",
    )
    return any(k in low for k in useful_kw)


def select_domains(features: list[dict[str, Any]], acc: str, limit: int = 8) -> list[dict[str, Any]]:
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for i, f in enumerate(features):
        ftype = f.get("type") or ""
        if ftype not in FEATURE_PRIORITY:
            continue
        desc = f.get("description") or ""
        if ftype == "Region" and not region_is_useful(desc):
            continue
        # skip compositional-ish motifs that are tiny chemistry tags
        if ftype == "Motif" and desc.startswith("[") and len(desc) < 20:
            continue
        loc = f.get("location") or {}
        start = _loc_value(loc.get("start"))
        end = _loc_value(loc.get("end"))
        if start is None or end is None or end < start:
            continue
        # skip very tiny regions (< 5 aa) except Motif
        if ftype not in ("Motif", "Signal") and (end - start + 1) < 5:
            continue
        name = feature_display_name(ftype, desc)
        pri = FEATURE_PRIORITY.index(ftype)
        # prefer longer for same priority
        length_penalty = -(end - start)
        dom = {
            "id": f"up:{acc}:{ftype}:{start}-{end}",
            "name": name,
            "name_zh": name_zh_for(name, ftype),
            "start": start,
            "end": end,
            "source": "UniProt",
            "url": f"https://www.uniprot.org/uniprotkb/{acc}",
            "_type": ftype,
        }
        scored.append((pri, length_penalty, i, dom))

    # Chain fallback when few structural features (e.g. KRAS GTPase chain)
    if len(scored) < 3:
        for i, f in enumerate(features):
            if (f.get("type") or "") != "Chain":
                continue
            desc = (f.get("description") or "").strip()
            loc = f.get("location") or {}
            start = _loc_value(loc.get("start"))
            end = _loc_value(loc.get("end"))
            if start is None or end is None or end <= start:
                continue
            name = desc or "Chain"
            # soften long processed isoform names
            if "," in name:
                name = name.split(",")[0].strip()
            dom = {
                "id": f"up:{acc}:Chain:{start}-{end}",
                "name": name,
                "name_zh": name_zh_for(name, "Domain"),
                "start": start,
                "end": end,
                "source": "UniProt",
                "url": f"https://www.uniprot.org/uniprotkb/{acc}",
                "_type": "Chain",
            }
            # priority after Domain-like, before Motif-ish filler
            scored.append((1, -(end - start), i, dom))

    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    # dedupe overlapping same-name
    picked: list[dict[str, Any]] = []
    seen_spans: list[tuple[int, int]] = []
    for _, __, ___, dom in scored:
        s, e = dom["start"], dom["end"]
        # skip near-duplicate spans
        if any(abs(s - a) < 3 and abs(e - b) < 3 for a, b in seen_spans):
            continue
        clean = {k: v for k, v in dom.items() if not k.startswith("_")}
        picked.append(clean)
        seen_spans.append((s, e))
        if len(picked) >= limit:
            break
    # Prefer at least 3 if possible — already limited
    # Sort by genomic/protein start for display
    picked.sort(key=lambda d: d["start"])
    return picked[:limit]


def fetch_uniprot_domains(acc: str) -> tuple[list[dict[str, Any]], str]:
    """Returns (domains, confidence)."""
    cache_path = CACHE_UP / f"{acc}.json"
    CACHE_UP.mkdir(parents=True, exist_ok=True)
    try:
        if cache_path.is_file():
            data = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            url = f"https://rest.uniprot.org/uniprotkb/{acc}.json"
            data = _http_json(url)
            cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            time.sleep(UNIPROT_DELAY)
        features = data.get("features") or []
        domains = select_domains(features, acc, limit=8)
        conf = "high" if domains else "medium"
        return domains, conf
    except Exception as e:
        print(f"  UniProt fail {acc}: {e}")
        return [], "unavailable"


def render_ca_preview(pdb_path: Path, out_png: Path, title: str = "") -> bool:
    """Simple C-alpha trace colored by B-factor (pLDDT)."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection
        import numpy as np
    except ImportError as e:
        print(f"  matplotlib unavailable: {e}")
        return False

    xs, ys, zs, bf = [], [], [], []
    for line in pdb_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("ATOM"):
            continue
        if line[12:16].strip() != "CA":
            continue
        try:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            b = float(line[60:66])
        except ValueError:
            continue
        xs.append(x)
        ys.append(y)
        zs.append(z)
        bf.append(b)
    if len(xs) < 3:
        return False

    coords = np.array([xs, ys, zs], dtype=float)
    # PCA to 2D for a stable silhouette
    center = coords.mean(axis=1, keepdims=True)
    X = coords - center
    try:
        _, _, vt = np.linalg.svd(X, full_matrices=False)
        proj = (vt[:2] @ X).T  # N x 2
    except Exception:
        proj = np.column_stack([xs, ys])

    bfa = np.array(bf)
    points = proj.reshape(-1, 1, 2)
    segs = np.concatenate([points[:-1], points[1:]], axis=1)
    fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=120)
    fig.patch.set_facecolor("#f7f4ef")
    ax.set_facecolor("#f7f4ef")
    lc = LineCollection(segs, cmap="viridis", linewidths=1.6, alpha=0.95)
    lc.set_array(bfa[:-1])
    lc.set_clim(50, 100)
    ax.add_collection(lc)
    ax.autoscale()
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=9, color="#1a1a1a", pad=6)
    cbar = fig.colorbar(lc, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("pLDDT", fontsize=7)
    cbar.ax.tick_params(labelsize=6)
    fig.tight_layout(pad=0.4)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_png.is_file() and out_png.stat().st_size > 500


def fetch_alphafold_preview(symbol: str, acc: str) -> str | None:
    """
    Download AlphaFold model (v6 preferred) and render a CA-trace PNG.
    Fallback: PAE heatmap PNG from API.
    Returns relative path under data/ (e.g. cache/alphafold/TP53.png) or None.
    """
    CACHE_AF.mkdir(parents=True, exist_ok=True)
    out_png = CACHE_AF / f"{symbol}.png"
    rel = f"cache/alphafold/{symbol}.png"

    # 1) API metadata
    api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"
    pdb_url = None
    pae_url = None
    try:
        meta = _http_json(api_url)
        time.sleep(AF_DELAY)
        if isinstance(meta, list) and meta:
            meta = meta[0]
        pdb_url = meta.get("pdbUrl")
        pae_url = meta.get("paeImageUrl")
    except Exception as e:
        print(f"  AF API fail {acc}: {e}")

    # 2) Try render from PDB
    if pdb_url:
        pdb_path = CACHE_AF / f"{symbol}.pdb"
        try:
            _http_get(pdb_url, pdb_path)
            time.sleep(AF_DELAY)
            if render_ca_preview(pdb_path, out_png, title=f"{symbol} · AlphaFold"):
                print(f"  preview (CA trace) → {rel}")
                return rel
        except Exception as e:
            print(f"  AF PDB/render fail {symbol}: {e}")

    # 3) Try classic model PNG URLs (often 404 on v6+)
    for ver in ("v6", "v4", "v3"):
        for pattern in (
            f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{ver}.png",
        ):
            try:
                _http_get(pattern, out_png)
                time.sleep(AF_DELAY)
                if out_png.stat().st_size > 1000:
                    print(f"  preview (model png {ver}) → {rel}")
                    return rel
            except Exception:
                pass

    # 4) PAE image fallback
    if pae_url:
        try:
            _http_get(pae_url, out_png)
            time.sleep(AF_DELAY)
            if out_png.stat().st_size > 1000:
                print(f"  preview (PAE) → {rel}")
                return rel
        except Exception as e:
            print(f"  AF PAE fail {symbol}: {e}")

    if out_png.exists() and out_png.stat().st_size < 1000:
        out_png.unlink(missing_ok=True)
    print(f"  preview FAIL → null for {symbol}")
    return None


def band_label_for(gene: dict[str, Any]) -> str:
    for h in gene.get("headline_stats") or []:
        if h.get("key") == "location" and h.get("value"):
            return str(h["value"])
    loc = gene.get("location") or {}
    return f"{loc.get('chrom', '?')}?"


def upsert_source(sources: list[dict[str, Any]], name_substr: str, entry: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    replaced = False
    for s in sources:
        if name_substr.lower() in str(s.get("name") or "").lower():
            if not replaced:
                out.append(entry)
                replaced = True
            # drop old matching
        else:
            out.append(s)
    if not replaced:
        out.append(entry)
    return out


def update_gene(path: Path, gene: dict[str, Any], domains: list[dict], domains_conf: str, preview: str | None) -> None:
    loc = gene.get("location") or {}
    chrom = str(loc.get("chrom"))
    gene["cytoband"] = {
        "chrom": chrom,
        "start": loc.get("start"),
        "end": loc.get("end"),
        "assembly": loc.get("assembly") or "GRCh38",
        "band_label": band_label_for(gene),
        "figure_id": f"cytobands/{chrom}.json",
    }
    gene["domains"] = domains

    expr = gene.get("expression") or {}
    expr["caption_zh"] = EXPR_CAPTION_ZH
    expr["caption_en"] = EXPR_CAPTION_EN
    # keep tissues TPM desc, ~8
    tissues = expr.get("tissues") or []
    tissues = sorted(tissues, key=lambda t: float(t.get("value") or 0), reverse=True)[:8]
    expr["tissues"] = tissues
    gene["expression"] = expr

    structure = gene.get("structure") or {}
    structure["preview_image"] = preview
    structure["caption_zh"] = STRUCT_CAPTION_ZH
    structure["caption_en"] = STRUCT_CAPTION_EN
    if preview is None:
        # keep captions; empty state handled by frontend
        pass
    gene["structure"] = structure

    colophon = gene.get("colophon") or {}
    colophon["edition"] = EDITION
    # keep data_as_of language-agnostic; bump to today for P3.6 figure sync
    colophon["data_as_of"] = TODAY
    gene["colophon"] = colophon

    acc = uniprot_acc_from_gene(gene)
    sources = list(gene.get("sources") or [])
    up_entry = {
        "name": "UniProt domains",
        "url": f"https://www.uniprot.org/uniprotkb/{acc}" if acc else "https://www.uniprot.org",
        "version": f"{TODAY}; Swiss-Prot features (Domain/Region/…)",
        "confidence": domains_conf if domains_conf != "unavailable" else ("medium" if domains else "unavailable"),
    }
    if not domains and domains_conf == "unavailable":
        up_entry["confidence"] = "unavailable"
        up_entry["note"] = "本期未拉到结构域特征；domains 为空数组。"
    elif not domains:
        up_entry["confidence"] = "medium"
        up_entry["note"] = "查询成功但无代表性 Domain/Region 条目。"
    else:
        up_entry["confidence"] = "high" if len(domains) >= 2 else "medium"
    sources = upsert_source(sources, "uniprot domains", up_entry)

    # refresh AlphaFold source note about preview
    af_url = structure.get("alphafold_url")
    af_entry = {
        "name": "AlphaFold DB",
        "url": af_url or "https://alphafold.ebi.ac.uk",
        "version": f"{TODAY}; entry by UniProt" + ("; local CA-trace preview" if preview else "; preview unavailable"),
        "confidence": "high" if af_url else "unavailable",
    }
    if preview:
        af_entry["note"] = f"preview_image={preview}（本地缓存；由 PDB CA 迹线或 PAE 图生成）"
    else:
        af_entry["note"] = "本期未收录预览图；保留 alphafold_url 外链。"
    sources = upsert_source(sources, "alphafold", af_entry)

    # cytoband source
    cyto_entry = {
        "name": "UCSC cytoBandIdeo",
        "url": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/cytoBandIdeo.txt.gz",
        "version": f"hg38 / GRCh38; {TODAY}",
        "confidence": "high",
        "note": f"figure_id=cytobands/{chrom}.json",
    }
    sources = upsert_source(sources, "cytoband", cyto_entry)

    gene["sources"] = sources
    path.write_text(json.dumps(gene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def selected_symbols() -> list[str] | None:
    raw = os.environ.get("SYNC_SYMBOLS", "").strip()
    if not raw:
        return None
    return [s.strip().upper() for s in raw.split(",") if s.strip()]


def main() -> None:
    print(f"P3.6 sync_figures edition={EDITION} date={TODAY}")
    FIGURES_CYTO.mkdir(parents=True, exist_ok=True)
    CACHE_AF.mkdir(parents=True, exist_ok=True)
    CACHE_UP.mkdir(parents=True, exist_ok=True)

    genes: list[tuple[str, Path, dict[str, Any]]] = []
    for path in sorted(GENES_DIR.glob("*.json")):
        g = json.loads(path.read_text(encoding="utf-8"))
        genes.append((g.get("symbol") or path.stem, path, g))

    filt = selected_symbols()
    if filt:
        genes = [t for t in genes if t[0] in filt]
        print(f"subset: {filt}")

    chroms = {str((g.get("location") or {}).get("chrom")) for _, __, g in genes}
    chroms.discard("None")
    print(f"chromosomes: {sorted(chroms)}")
    by_chrom = parse_cytobands(chroms)
    write_cytoband_files(by_chrom)

    summary = []
    for sym, path, gene in genes:
        print(f"\n=== {sym} ===")
        acc = uniprot_acc_from_gene(gene)
        print(f"  UniProt={acc}")
        domains: list[dict] = []
        dconf = "unavailable"
        if acc:
            domains, dconf = fetch_uniprot_domains(acc)
            print(f"  domains={len(domains)} conf={dconf}")
            for d in domains[:3]:
                print(f"    - {d['name']} ({d['start']}-{d['end']}) / {d['name_zh']}")
        preview = None
        if acc:
            preview = fetch_alphafold_preview(sym, acc)
        update_gene(path, gene, domains, dconf, preview)
        summary.append(
            {
                "symbol": sym,
                "domains": len(domains),
                "preview": preview,
                "cytoband": gene.get("cytoband"),
            }
        )

    print("\n--- summary ---")
    for s in summary:
        print(
            f"  {s['symbol']}: domains={s['domains']} preview={s['preview'] or 'null'} "
            f"band={s['cytoband'].get('band_label') if s['cytoband'] else '?'}"
        )
    print("done. next: python3 data/scripts/rebuild_catalog.py")


if __name__ == "__main__":
    main()
