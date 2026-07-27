# Metrix AI — production API image (Railway / any container host)
# Build: docker build -t metrix-ai .
# Run:   docker run -p 8787:8787 -e METRIX_CORS=https://your-app.vercel.app metrix-ai

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    METRIX_DEBUG=0 \
    METRIX_HOST=0.0.0.0 \
    PORT=8787

WORKDIR /app

# curl for container HEALTHCHECK; tini for clean PID 1 signal handling
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

# Writable runtime dirs (ephemeral on Railway unless a volume is attached)
RUN mkdir -p backend/workspace backend/data/requests logs \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8787

# Docker-local health (Railway uses railway.toml healthcheckPath)
HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
  CMD sh -c 'curl -fsS "http://127.0.0.1:${PORT:-8787}/api/v1/health" || exit 1'

# proxy-headers: correct scheme/host behind Railway edge
ENTRYPOINT ["tini", "--"]
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8787} --proxy-headers --forwarded-allow-ips='*' --log-level info --timeout-keep-alive 30"]
