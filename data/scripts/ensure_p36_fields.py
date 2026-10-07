# -*- coding: utf-8 -*-
"""Validate P3.6 fields on genes/*.json and cytoband figure files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENES = ROOT / "genes"
FIG = ROOT / "figures"
EDITION = "0.3.1-p36"


def main() -> None:
    errors: list[str] = []
    for path in sorted(GENES.glob("*.json")):
        g = json.loads(path.read_text(encoding="utf-8"))
        sym = g.get("symbol") or path.stem
        if (g.get("colophon") or {}).get("edition") != EDITION:
            errors.append(f"{sym}: edition != {EDITION}")
        cy = g.get("cytoband")
        if not isinstance(cy, dict):
            errors.append(f"{sym}: missing cytoband")
        else:
            for k in ("chrom", "start", "end", "assembly", "band_label", "figure_id"):
                if cy.get(k) in (None, ""):
                    errors.append(f"{sym}: cytoband.{k} missing")
            fid = cy.get("figure_id") or ""
            fpath = FIG / fid
            if fid and not fpath.is_file():
                errors.append(f"{sym}: figure missing {fid}")
        if "domains" not in g or not isinstance(g["domains"], list):
            errors.append(f"{sym}: domains must be list")
        expr = g.get("expression") or {}
        if "多组织" not in str(expr.get("caption_zh") or "") and "small multiples" not in str(
            expr.get("caption_en") or ""
        ):
            errors.append(f"{sym}: expression captions not small-multiples wording")
        struct = g.get("structure") or {}
        if "preview_image" not in struct:
            errors.append(f"{sym}: structure.preview_image key missing")
        elif struct.get("preview_image"):
            rel = struct["preview_image"]
            if not (ROOT / rel).is_file():
                errors.append(f"{sym}: preview file missing {rel}")
        src_names = [str(s.get("name") or "") for s in (g.get("sources") or [])]
        if not any("uniprot domains" in n.lower() for n in src_names):
            errors.append(f"{sym}: sources missing UniProt domains")
        if not any("cytoband" in n.lower() or "ucsc" in n.lower() for n in src_names):
            errors.append(f"{sym}: sources missing cytoband/UCSC")

    if errors:
        print(f"FAIL ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)
    print(f"OK: all genes have P3.6 fields (edition={EDITION})")


if __name__ == "__main__":
    main()
