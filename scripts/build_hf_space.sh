#!/usr/bin/env bash
# Assemble the Hugging Face Docker Space repo for GenePage Gazette.
#
#   scripts/build_hf_space.sh [OUT_DIR]      (default: /workspace/genepage-hf-space)
#
# Output root contains exactly what the HF Space git repo needs:
#   README.md (YAML frontmatter: sdk: docker, app_port: 7860)
#   Dockerfile  start.sh  .gitattributes  .dockerignore
#   api/main.py  api/requirements.txt
#   data/   (genes/, index.json, figures/, exports/, cache/ — no sync scripts, no logs)
#   web/    (Next.js source — no node_modules/.next/tsbuildinfo)
#
# The OUT_DIR's own .git (if you cloned the Space into it) is preserved, so the
# update loop is: rerun this script → git add -A → commit → push (or `hf upload`).
# Never commit OUT_DIR into the main GitHub repo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-/workspace/genepage-hf-space}"
OUT="$(mkdir -p "$OUT" && cd "$OUT" && pwd)"

case "$OUT" in
  "$ROOT"|"$ROOT"/*) echo "refusing: OUT_DIR must be outside the main repo ($ROOT)" >&2; exit 2 ;;
  /|"$HOME") echo "refusing: unsafe OUT_DIR $OUT" >&2; exit 2 ;;
esac


EDITION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["edition"])' "$ROOT/data/index.json")"
DATA_AS_OF="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("data_as_of",""))' "$ROOT/data/index.json")"

echo "[hf] root=$ROOT"
echo "[hf] out =$OUT  edition=$EDITION data_as_of=$DATA_AS_OF"

# Clean previous output but keep a cloned Space .git
find "$OUT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +

mkdir -p "$OUT/api"
cp "$ROOT/api/main.py" "$ROOT/api/requirements.txt" "$OUT/api/"

mkdir -p "$OUT/data"
tar -C "$ROOT/data" \
  --exclude='./scripts' \
  --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='./cache/logs/*' \
  --exclude='.DS_Store' \
  -cf - . | tar -C "$OUT/data" -xf -
mkdir -p "$OUT/data/cache/logs"

mkdir -p "$OUT/web"
tar -C "$ROOT/web" \
  --exclude='./node_modules' --exclude='./.next' \
  --exclude='./tsconfig.tsbuildinfo' \
  --exclude='./Dockerfile' --exclude='./fly.toml' \
  --exclude='./.env' --exclude='./.env.*' \
  --exclude='.DS_Store' \
  -cf - . | tar -C "$OUT/web" -xf -
mkdir -p "$OUT/web/public"

cp "$ROOT/hf-space/Dockerfile" "$OUT/Dockerfile"
cp "$ROOT/hf-space/start.sh" "$OUT/start.sh"
chmod +x "$OUT/start.sh"
cp "$ROOT/hf-space/gitattributes.space" "$OUT/.gitattributes"
cp "$ROOT/hf-space/dockerignore.space" "$OUT/.dockerignore"
sed -e "s/__EDITION__/$EDITION/g" -e "s/__DATA_AS_OF__/$DATA_AS_OF/g" \
  "$ROOT/hf-space/README.space.md" > "$OUT/README.md"

# Provenance (handy when diffing Space vs GitHub)
GIT_SHA="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf 'source=https://github.com/ddxyl404/genepage-gazette\ncommit=%s\nedition=%s\ndata_as_of=%s\n' \
  "$GIT_SHA" "$EDITION" "$DATA_AS_OF" > "$OUT/BUILD_INFO"

# Sanity checks
for f in README.md Dockerfile start.sh api/main.py api/requirements.txt \
         data/index.json web/package.json web/package-lock.json web/next.config.mjs; do
  [ -f "$OUT/$f" ] || { echo "[hf] missing $f" >&2; exit 1; }
done
grep -q '^sdk: docker$' "$OUT/README.md"
grep -q '^app_port: 7860$' "$OUT/README.md"
ls "$OUT/data/genes/"*.json >/dev/null

echo "[hf] files: $(find "$OUT" -path "$OUT/.git" -prune -o -type f -print | wc -l)  size: $(du -sh --exclude=.git "$OUT" | cut -f1)"
echo "[hf] done → $OUT"
