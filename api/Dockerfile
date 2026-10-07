# GenePage Gazette API — build context MUST be repository root
# (Koyeb: workdir repo root + dockerfile api/Dockerfile;
#  Render: dockerContext . + dockerfilePath ./api/Dockerfile;
#  Compose: context: . + dockerfile: api/Dockerfile).
FROM python:3.12-slim
WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/main.py .

# Bake seed data into the image (Koyeb free / Render Free have no durable free disk).
# Local Compose still mounts ./data:/data:ro over this for live iteration.
COPY data/ /data/
ENV GENEPAGE_DATA_DIR=/data
ENV GENEPAGE_CACHE_DIR=/data/cache

EXPOSE 8000
# Platforms may set PORT; local/Compose default to 8000.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
