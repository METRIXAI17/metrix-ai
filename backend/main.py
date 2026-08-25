"""
Metrix AI Backend — FastAPI entrypoint.

Запуск из корня проекта (Desktop/metrix-ai):

  pip install -r requirements.txt
  python -m backend.main

  # или:
  uvicorn backend.main:app --host 0.0.0.0 --port 8787 --reload

Акцент: простой HTTP-бекенд для обработки запросов с сайта / демо.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure project root on sys.path when run as script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend import __brand__, __codename__, __version__
from backend.api.routes import analytics, fin_models, health, miniapp, requests, zones
from backend.config import API_PREFIX, CORS_ORIGINS, DEBUG, ENV_NAME, HOST, PORT
from backend.security import install_security

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("metrix")

app = FastAPI(
    title=f"{__brand__} Backend",
    description=(
        "Operational Analytical System — request processing backend. "
        f"Codename: {__codename__}. Orientation → Zones → Fin Models → Monetization."
    ),
    version=__version__,
    docs_url="/docs" if DEBUG else "/docs",
    redoc_url="/redoc" if DEBUG else "/redoc",
)

# Basic cybersecurity: rate limit · headers · body size · ops key gate
install_security(app)

# CORS: explicit origins in production. DEBUG may allow "*".
# credentials + "*" is invalid in browsers — disable credentials when wildcard.
_cors = list(CORS_ORIGINS)
if DEBUG and "*" not in _cors:
    _cors = _cors + ["*"]
_allow_credentials = "*" not in _cors

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors if _cors else ["*"],
    allow_credentials=_allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(requests.router, prefix=API_PREFIX)
app.include_router(fin_models.router, prefix=API_PREFIX)
app.include_router(zones.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(miniapp.router, prefix=API_PREFIX)

# Serve static frontend (Vercel uses public/; local API mounts same tree at /app)
_frontend = _ROOT / "public"
if not (_frontend / "index.html").exists():
    _frontend = _ROOT  # legacy fallback
if (_frontend / "index.html").exists():
    app.mount("/app", StaticFiles(directory=str(_frontend), html=True), name="frontend")
_tg = _frontend / "tg"
if (_tg / "index.html").exists():
    app.mount("/tg", StaticFiles(directory=str(_tg), html=True), name="tg-miniapp")
_assets = _frontend / "assets"
if _assets.exists():
    app.mount("/assets", StaticFiles(directory=str(_assets)), name="public-assets")


@app.get("/")
def root() -> JSONResponse:
    from backend.services.supabase_sync import is_enabled as supabase_on

    return JSONResponse(
        {
            "brand": __brand__,
            "codename": __codename__,
            "version": __version__,
            "env": ENV_NAME,
            "message": "Metrix AI backend is alive. Process requests at POST /api/v1/process",
            "docs": "/docs",
            "frontend": "/app/",
            "telegram_miniapp": "/tg/",
            "health": f"{API_PREFIX}/health",
            "catalog": f"{API_PREFIX}/catalog",
            "ops_panel": "/app/ops-panel.html",
            "supabase_sync": supabase_on(),
            "security": "basic-1",
        }
    )


@app.get("/health")
def root_health() -> JSONResponse:
    """Alias for platform healthchecks that expect /health."""
    from backend.services.supabase_sync import is_enabled as supabase_on

    return JSONResponse(
        {
            "ok": True,
            "brand": __brand__,
            "version": __version__,
            "env": ENV_NAME,
            "service": "metrix-ai-backend",
            "supabase_sync": supabase_on(),
            "security": "basic-1",
        }
    )


def run() -> None:
    import uvicorn

    logger.info("Starting %s %s on %s:%s", __brand__, __version__, HOST, PORT)
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info",
    )


if __name__ == "__main__":
    run()
