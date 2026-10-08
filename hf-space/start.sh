#!/usr/bin/env bash
# GenePage Gazette single-container entrypoint (HF Docker Space).
# Runs FastAPI (127.0.0.1:8000) + Next standalone (0.0.0.0:${GENEPAGE_WEB_PORT:-7860}).
# If either process exits, the other is stopped and the container exits
# with that status (HF then shows the Space as errored / restarts it).
set -uo pipefail

APP_HOME="${APP_HOME:-/home/user/app}"
# Must stay 8000: Next rewrites (/api/* → 127.0.0.1:8000) are frozen at build time
# and web/src/lib/api.ts SSR default is http://127.0.0.1:8000.
API_PORT=8000
WEB_PORT="${GENEPAGE_WEB_PORT:-7860}"
export GENEPAGE_DATA_DIR="${GENEPAGE_DATA_DIR:-$APP_HOME/data}"
export GENEPAGE_CACHE_DIR="${GENEPAGE_CACHE_DIR:-$GENEPAGE_DATA_DIR/cache}"
PYTHON="${GENEPAGE_PYTHON:-python3}"
NODE="${GENEPAGE_NODE:-node}"

API_PID=""
WEB_PID=""
shutdown() {
  trap - TERM INT
  [ -n "$WEB_PID" ] && kill -TERM "$WEB_PID" 2>/dev/null
  [ -n "$API_PID" ] && kill -TERM "$API_PID" 2>/dev/null
  wait 2>/dev/null
}
trap 'shutdown; exit 143' TERM INT

echo "[start] api  → 127.0.0.1:${API_PORT}  data=${GENEPAGE_DATA_DIR}"
(cd "$APP_HOME/api" && exec "$PYTHON" -m uvicorn main:app \
    --host 127.0.0.1 --port "$API_PORT" --no-access-log) &
API_PID=$!

# Wait (≤30s) for the API so the first SSR render doesn't hit a cold socket.
for _ in $(seq 1 60); do
  if "$PYTHON" - "$API_PORT" <<'PY' 2>/dev/null; then break; fi
import sys, urllib.request
urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[1]}/api/health", timeout=1)
PY
  kill -0 "$API_PID" 2>/dev/null || break
  sleep 0.5
done

echo "[start] web  → 0.0.0.0:${WEB_PORT}"
(cd "$APP_HOME/web" && HOSTNAME=0.0.0.0 PORT="$WEB_PORT" exec "$NODE" server.js) &
WEB_PID=$!

wait -n "$API_PID" "$WEB_PID"
code=$?
echo "[start] a process exited (status ${code}); stopping container" >&2
shutdown
exit "$code"
