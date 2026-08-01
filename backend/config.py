"""
Конфигурация Metrix AI backend.

Всё важное — в одном месте. Без магии: пути, порты, пороги метрик, тарифы.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# ── Пути ──────────────────────────────────────────────────────────────────────
BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent
WORKSPACE_ROOT = BACKEND_ROOT / "workspace"
DATA_DIR = BACKEND_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

for _p in (WORKSPACE_ROOT, DATA_DIR, LOGS_DIR):
    _p.mkdir(parents=True, exist_ok=True)

# ── Сервер ────────────────────────────────────────────────────────────────────
# Railway/Render/Fly inject PORT; local uses METRIX_PORT or 8787.
HOST = os.getenv("METRIX_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT") or os.getenv("METRIX_PORT", "8787"))
# Default off for safe production; set METRIX_DEBUG=1 only for local dev.
DEBUG = os.getenv("METRIX_DEBUG", "0") == "1"
ENV_NAME = os.getenv("METRIX_ENV", "development" if DEBUG else "production")
# Public HTTPS origin of this API (Railway). Used to mint absolute pack links.
# Example: https://metrix-ai-production.up.railway.app
PUBLIC_BASE_URL = os.getenv("METRIX_PUBLIC_URL", "").rstrip("/")
API_PREFIX = "/api/v1"


def public_api_url(path: str) -> str:
    """Build browser-openable URL for an API path (relative if PUBLIC_BASE_URL unset)."""
    p = path if str(path).startswith("/") else f"/{path}"
    if PUBLIC_BASE_URL:
        return f"{PUBLIC_BASE_URL}{p}"
    return p
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "METRIX_CORS",
        "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500,null",
    ).split(",")
    if o.strip()
]

# ── 6 обязательных индустриальных направлений (как на сайте) ─────────────────
INDUSTRIES: dict[str, dict[str, Any]] = {
    "ai-agencies": {
        "id": "ai-agencies",
        "name": "AI Agencies",
        "short": "Agencies",
        "blurb": "Ops efficiency · Terminal Teammate · buyer fin models.",
        "application_point": "operational_efficiency",
        "primary_product": "Terminal Teammate",
        "accent": "#5eead4",
        "default_fin_models": ["orientationforge", "prologforge", "marketforge"],
    },
    "cloud-economy": {
        "id": "cloud-economy",
        "name": "Cloud Economy",
        "short": "Cloud / API",
        "blurb": "Cut third-party API costs for creative founders · Expert product.",
        "application_point": "third_party_api_cost_cut",
        "primary_product": "Expert",
        "accent": "#7dd3fc",
        "default_fin_models": ["edgeforge", "chipforge", "marketforge"],
    },
    "cost-engineering": {
        "id": "cost-engineering",
        "name": "Cost Engineering",
        "short": "Cost Eng.",
        "blurb": "Simple waste map + resellable Void Scanner for cost-eng clients.",
        "application_point": "ops_for_cost_engineers",
        "primary_product": "Parameter Void Scanner",
        "accent": "#fbbf24",
        "default_fin_models": ["edgeforge", "orientationforge", "chipforge"],
    },
    "chipmaking": {
        "id": "chipmaking",
        "name": "Chipmaking",
        "short": "Chips",
        "blurb": "Design-loop voids · yield twin · clarity promo (3 simple offers).",
        "application_point": "design_loop_clarity",
        "primary_product": "Yield Geometry Twin",
        "accent": "#c4b5fd",
        "default_fin_models": ["chipforge", "metaobject", "edgeforge"],
    },
    "telecom": {
        "id": "telecom",
        "name": "Telecom",
        "short": "Telecom",
        "blurb": "SLA SKUs · ARPU/churn ops · intent-signal promo.",
        "application_point": "sla_arpu_signal",
        "primary_product": "SLA-native SKU Builder",
        "accent": "#86efac",
        "default_fin_models": ["edgeforge", "prologforge", "marketforge"],
    },
    "device-assembly": {
        "id": "device-assembly",
        "name": "Device Assembly & Config",
        "short": "Devices",
        "blurb": "Assembly, setup, and configuration product workflows.",
        "accent": "#fda4af",
        "default_fin_models": ["metaobject", "chipforge", "orientationforge"],
    },
    "asset-decisions": {
        "id": "asset-decisions",
        "name": "Asset decisions",
        "short": "Assets",
        "blurb": "AI for asset management decisions · autoliquidity.",
        "application_point": "decision_support_liquidity",
        "primary_product": "Decision Support Desk",
        "accent": "#f0abfc",
        "badge": "Автоликвидность",
        "default_fin_models": ["marketforge", "edgeforge", "orientationforge"],
    },
    "d2c-offramp": {
        "id": "d2c-offramp",
        "name": "D2C · freelace offramp",
        "short": "D2C",
        "blurb": "Idea → document → exchange → agent · autoliquidity.",
        "application_point": "d2c_document_liquidity",
        "primary_product": "Workspace Offramp",
        "accent": "#67e8f9",
        "badge": "Автоликвидность",
        "default_fin_models": ["prologforge", "marketforge", "orientationforge"],
    },
}

TRACKS = ("product", "models", "promotion")

# ── Зоны архитектуры ──────────────────────────────────────────────────────────
ZONES = {
    "infa_sol": "Infa Sol",
    "cloud_sol": "Cloud Sol",
    "structure_fi": "Structure Fi",
    "product_sol": "Product Sol",
    "superstructure": "Superstructure / Product Overlay",
}

# ── Пороги метрик VVI / ER / RRC ──────────────────────────────────────────────
# VVI — Vulnerability Void Index (пустоты / уязвимости в спецификации)
# ER  — Efficiency of Error (полезность обнаруженных ошибок)
# RRC — Reverse Refragmentation Coefficient (способность к обратной пересборке)
METRIC_THRESHOLDS = {
    "vvi_healthy_max": 0.35,      # ниже — мало «дыр» в спеке
    "vvi_critical": 0.70,
    "er_healthy_min": 0.55,     # выше — ошибки дают ценность (улучшения)
    "rrc_healthy_min": 0.50,    # выше — система хорошо пересобирается
    "info_roi_attractive": 1.8, # информационный ROI «стоит делать»
    "info_roi_premium": 3.0,
}

# ── Рекурсия SpecsForge ───────────────────────────────────────────────────────
SPECS_MAX_DEPTH = 5
SPECS_IMPROVEMENT_DELTA = 0.04  # минимальный прирост качества за итерацию

# ── Cloud Optimization ────────────────────────────────────────────────────────
CLOUD_DEFAULT_BUDGET_UNITS = 100.0
CLOUD_PRECISION_WEIGHT = 0.45
CLOUD_SPEED_WEIGHT = 0.30
CLOUD_RESOURCE_WEIGHT = 0.25

# ── Monetization defaults (showcase) ──────────────────────────────────────────
MONETIZATION = {
    "promo": {
        "name": "Promo Automation",
        "base_price_usd": 490,
        "description": "Автоматизация продвижения идей и готовых решений.",
    },
    "market_making": {
        "name": "Market Making Simulation",
        "base_price_usd": 890,
        "description": "Позиционирование, ликвидность внимания, динамика рынка.",
    },
    "auto_orders": {
        "name": "Auto Orders Engine",
        "base_price_usd": 1290,
        "description": "Автоматические решения и заказные петли (decision → order).",
    },
    "full_package": {
        "name": "Full Orientation Package",
        "base_price_usd": 2490,
        "description": "Product + Models + Promotion + implement path.",
    },
    "metareality_consult": {
        "name": "MetaReality Consultation",
        "base_price_usd": 890,
        "description": "Operational geometry consult + constraint map.",
    },
    "specsforge_tech_write": {
        "name": "SpecsForge Tech Writing",
        "base_price_usd": 650,
        "description": "Recursive tech writing after consultation.",
    },
    "consult_techwrite_bundle": {
        "name": "Full Consult + Tech Write Package",
        "base_price_usd": 1290,
        "description": "MetaReality consult + SpecsForge tech write (bundle).",
    },
}

# ── Self-improvement ──────────────────────────────────────────────────────────
SELF_IMPROVE_MAX_LOOPS = 3
SELF_IMPROVE_MIN_GAIN = 0.03
