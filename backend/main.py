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
from backend.api.routes import analytics, fin_models, health, requests, zones
from backend.config import API_PREFIX, CORS_ORIGINS, DEBUG, HOST, PORT

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
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"] if DEBUG else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(requests.router, prefix=API_PREFIX)
app.include_router(fin_models.router, prefix=API_PREFIX)
app.include_router(zones.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)

# Serve existing static frontend if present
_frontend = _ROOT
if (_frontend / "index.html").exists():
    app.mount("/app", StaticFiles(directory=str(_frontend), html=True), name="frontend")


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "brand": __brand__,
            "codename": __codename__,
            "version": __version__,
            "message": "Metrix AI backend is alive. Process requests at POST /api/v1/process",
            "docs": "/docs",
            "frontend": "/app/",
            "health": f"{API_PREFIX}/health",
            "catalog": f"{API_PREFIX}/catalog",
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
