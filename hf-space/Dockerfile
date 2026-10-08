# syntax=docker/dockerfile:1
# GenePage Gazette — Hugging Face Docker Space (single container).
#
# Build context = the ASSEMBLED Space directory produced by
#   scripts/build_hf_space.sh  (default output: /workspace/genepage-hf-space)
# whose layout is:
#   README.md  Dockerfile  start.sh  .gitattributes
#   api/main.py  api/requirements.txt
#   data/        (seed JSON + figures + exports + cache)
#   web/         (Next.js 14 source, no node_modules/.next)
#
# Runtime: one container, two processes (see start.sh)
#   uvicorn  127.0.0.1:8000   (FastAPI, internal only)
#   node     0.0.0.0:7860     (Next standalone; README app_port: 7860)
# Browser → same-origin /api/*  → Next rewrite → 127.0.0.1:8000
# Next SSR → http://127.0.0.1:8000 (web/src/lib/api.ts default)

# ---------- 1) web deps ----------
FROM node:20-bookworm-slim AS web-deps
WORKDIR /build
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

# ---------- 2) web build (Next standalone) ----------
FROM node:20-bookworm-slim AS web-build
WORKDIR /build
COPY --from=web-deps /build/node_modules ./node_modules
COPY web/ ./
ENV NEXT_TELEMETRY_DISABLED=1
# Deliberately DO NOT set NEXT_PUBLIC_API_URL:
#   - browser code then calls relative /api/* (same origin, no CORS);
#   - next.config.mjs rewrites are frozen at build time to
#     http://127.0.0.1:8000/api/:path*  (the in-container uvicorn).
# Do not add a Space "Variable" named NEXT_PUBLIC_API_URL (HF passes
# variables as build args/env and it would switch the browser to direct calls).
RUN unset NEXT_PUBLIC_API_URL; mkdir -p public && npm run build

# ---------- 3) runtime: Python + Node ----------
FROM python:3.12-slim-bookworm AS runtime

# Node runtime binary only (same Debian bookworm/glibc as the builder).
COPY --from=node:20-bookworm-slim /usr/local/bin/node /usr/local/bin/node

# Python deps installed system-wide as root (before switching user).
COPY api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# HF Spaces run the container as uid 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    APP_HOME=/home/user/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    GENEPAGE_DATA_DIR=/home/user/app/data \
    GENEPAGE_CACHE_DIR=/home/user/app/data/cache \
    GENEPAGE_WEB_PORT=7860
# NOTE: data is baked under $APP_HOME/data, NOT /data — on HF, /data is the
# mount point for an (optional) attached storage bucket at runtime and is not
# usable during build.
WORKDIR /home/user/app

COPY --chown=user api/main.py api/main.py
COPY --chown=user data/ data/
COPY --chown=user --from=web-build /build/.next/standalone web/
COPY --chown=user --from=web-build /build/.next/static web/.next/static
COPY --chown=user --from=web-build /build/public web/public
COPY --chown=user start.sh start.sh

EXPOSE 7860
CMD ["bash", "/home/user/app/start.sh"]
