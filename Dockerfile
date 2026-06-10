# Stage 1: build the SPA
FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

COPY --from=web /web/dist ./web/dist

ENV SHEETCUT_DATA_DIR=/data \
    SHEETCUT_WEB_DIST=/app/web/dist \
    PATH="/app/.venv/bin:$PATH"
VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/api/v1/healthz')" || exit 1

CMD ["uvicorn", "--factory", "sheetcut.api.main:create_app", "--host", "0.0.0.0", "--port", "8000"]
