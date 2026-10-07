# -*- coding: utf-8 -*-
"""
Validate P3.5 i18n fields on genes/*.json.

Checks:
  - deck_en present and non-empty
  - deck_zh present (retained)
  - each expression.tissues[] has name + name_zh
  - recommended expression/structure caption_zh + caption_en
  - colophon.edition == 0.3.1-p36 (warn if not)

Usage:
  python3 /workspace/genepage/data/scripts/ensure_i18n_fields.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENES_DIR = ROOT / "genes"
EXPECTED_EDITION = "0.3.1-p36"


def main() -> int:
    paths = sorted(GENES_DIR.glob("*.json"))
    if not paths:
        print("ERROR: no gene JSON files", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    ok_deck_en = 0

    for path in paths:
        gene = json.loads(path.read_text(encoding="utf-8"))
        sym = gene.get("symbol") or path.stem

        if not (gene.get("deck_zh") or "").strip():
            errors.append(f"{sym}: missing deck_zh")
        if not (gene.get("deck_en") or "").strip():
            errors.append(f"{sym}: missing deck_en")
        else:
            ok_deck_en += 1

        expr = gene.get("expression") or {}
        for i, t in enumerate(expr.get("tissues") or []):
            if not (t.get("name") or "").strip():
                errors.append(f"{sym}: tissues[{i}] missing name")
            if not (t.get("name_zh") or "").strip():
                errors.append(f"{sym}: tissues[{i}] missing name_zh")

        for side, obj in (("expression", expr), ("structure", gene.get("structure") or {})):
            for key in ("caption_zh", "caption_en"):
                if not (obj.get(key) or "").strip():
                    warnings.append(f"{sym}: recommended {side}.{key} missing")

        edition = (gene.get("colophon") or {}).get("edition")
        if edition != EXPECTED_EDITION:
            warnings.append(f"{sym}: edition={edition!r} (expected {EXPECTED_EDITION})")

        # no seed confidence
        for src in gene.get("sources") or []:
            if str(src.get("confidence") or "").lower() == "seed":
                errors.append(f"{sym}: sources still has confidence=seed ({src.get('name')})")

    print(f"genes checked: {len(paths)}")
    print(f"deck_en present: {ok_deck_en}/{len(paths)}")
    if warnings:
        print(f"warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  WARN  {w}")
    if errors:
        print(f"errors ({len(errors)}):")
        for e in errors:
            print(f"  ERROR {e}")
        return 1
    print("OK: all required i18n fields present; no seed confidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
