#!/usr/bin/env bash
# GenePage Gazette — pack local data for offline restore (P4a).
# Usage:
#   ./scripts/backup_data.sh              # lean: genes + index + catalog* + cache meta; exclude alphafold PNG/webp
#   ./scripts/backup_data.sh --with-figures
#   ./scripts/backup_data.sh --dry-run    # same as a normal run (smoke); still writes one tgz
#   ./scripts/backup_data.sh --force      # overwrite if stamp collides
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT}"

WITH_FIGURES=0
DRY_RUN=0
FORCE=0

for arg in "$@"; do
  case "${arg}" in
    --with-figures) WITH_FIGURES=1 ;;
    --dry-run)      DRY_RUN=1 ;;
    --force)        FORCE=1 ;;
    -h|--help)
      cat <<'HELP'
Usage: ./scripts/backup_data.sh [--with-figures] [--dry-run] [--force]

Packs data/genes, data/index.json, data/catalog* (if any),
data/exports/*catalog*, data/cache/meta.json and other small cache
metadata into backups/genepage-YYYYMMDD-HHMM.tgz.

By default excludes data/cache/alphafold/*.{png,webp}.
--with-figures includes those image files.
--dry-run still produces one archive (smoke / 验收用).
--force allows overwriting an existing stamp file.
HELP
      exit 0
      ;;
    *)
      echo "Unknown option: ${arg}" >&2
      echo "Try --help" >&2
      exit 2
      ;;
  esac
done

mkdir -p "${ROOT}/backups"
STAMP="$(date +%Y%m%d-%H%M)"
OUT="${ROOT}/backups/genepage-${STAMP}.tgz"

if [[ -e "${OUT}" && "${FORCE}" -ne 1 ]]; then
  echo "Refusing to overwrite existing archive: ${OUT}" >&2
  echo "Pass --force to replace, or wait a minute for a new stamp." >&2
  exit 1
fi

# Paths relative to ROOT (only include what exists).
INCLUDE=()
[[ -d data/genes ]]            && INCLUDE+=(data/genes)
[[ -f data/index.json ]]       && INCLUDE+=(data/index.json)
# catalog* at data root (may appear after rebuild)
shopt -s nullglob
for f in data/catalog*; do
  INCLUDE+=("${f}")
done
# exported catalog CSV / audit notes
for f in data/exports/*catalog* data/exports/genes_catalog.csv data/exports/alphafold_audit.md; do
  [[ -e "${f}" ]] || continue
  # dedupe
  skip=0
  for e in "${INCLUDE[@]+"${INCLUDE[@]}"}"; do
    [[ "${e}" == "${f}" ]] && skip=1 && break
  done
  [[ ${skip} -eq 1 ]] || INCLUDE+=("${f}")
done
shopt -u nullglob

[[ -f data/cache/meta.json ]]  && INCLUDE+=(data/cache/meta.json)
[[ -f data/cache/README.md ]]  && INCLUDE+=(data/cache/README.md)

# Small per-source cache metadata (json/md/txt); skip large binaries unless --with-figures for images.
# Always try to include non-image files under cache source dirs.
shopt -s nullglob
for src in clinvar gtex mygene uniprot alphafold; do
  dir="data/cache/${src}"
  [[ -d "${dir}" ]] || continue
  for f in "${dir}"/*; do
    base="$(basename "${f}")"
    ext="${base##*.}"
    case "${ext}" in
      png|webp)
        if [[ "${WITH_FIGURES}" -eq 1 ]]; then
          INCLUDE+=("${f}")
        fi
        ;;
      pdb)
        # Large structure blobs: skip by default (regenerable via sync_figures).
        # Include when --with-figures for a fuller offline pack.
        if [[ "${WITH_FIGURES}" -eq 1 ]]; then
          INCLUDE+=("${f}")
        fi
        ;;
      *)
        INCLUDE+=("${f}")
        ;;
    esac
  done
done
shopt -u nullglob

if [[ ${#INCLUDE[@]} -eq 0 ]]; then
  echo "Nothing to back up under ${ROOT}/data" >&2
  exit 1
fi

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "[dry-run] still writing archive for smoke / 验收 (brief: dry-run 产出 backups/*.tgz)"
fi

echo "Backing up ${#INCLUDE[@]} path(s) → ${OUT}"
if [[ "${WITH_FIGURES}" -eq 1 ]]; then
  echo "Mode: with figures (png/webp/pdb under alphafold included)"
else
  echo "Mode: lean (excluding alphafold png/webp/pdb; pass --with-figures to include)"
fi

# tar from ROOT so paths inside the archive are data/...
tar -czf "${OUT}" -C "${ROOT}" "${INCLUDE[@]}"

SIZE="$(du -h "${OUT}" | awk '{print $1}')"
echo "Wrote ${OUT} (${SIZE})"
echo "${OUT}"
