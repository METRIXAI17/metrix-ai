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

# Supabase (optional — live log + future ops panel). Never put service role in frontend.
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_ENABLED = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


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
        "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500,"
        "http://127.0.0.1:8787,http://localhost:8787,null,"
        "https://web.telegram.org,https://k.telegram.org",
    ).split(",")
    if o.strip()
]
# Always allow Mini App hosts (Vercel + Telegram Web) even if METRIX_CORS is a tight list.
for _origin in (
    "https://metrix-ai.vercel.app",
    "https://web.telegram.org",
    "https://k.telegram.org",
):
    if _origin not in CORS_ORIGINS:
        CORS_ORIGINS.append(_origin)

# Telegram Mini App / bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_PROVIDER_TOKEN = os.getenv("TELEGRAM_PROVIDER_TOKEN", "").strip()
TELEGRAM_WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "").rstrip("/")
# Payments off until ЮKassa / Tribute / Stars are wired.
TELEGRAM_PAYMENTS = os.getenv("TELEGRAM_PAYMENTS", "0") == "1"
# Tribute — merchant of record. We store HMAC entitlements, not questionnaires.
TRIBUTE_API_KEY = os.getenv("TRIBUTE_API_KEY", "").strip()
TRIBUTE_ACCESS_URL = os.getenv("TRIBUTE_ACCESS_URL", "").rstrip("/")
TRIBUTE_CUSTOM_URL = os.getenv("TRIBUTE_CUSTOM_URL", "").rstrip("/")
METRIX_TOKEN_SECRET = os.getenv("METRIX_TOKEN_SECRET", "").strip()
HUMAN_CONTACT_URL = os.getenv("METRIX_HUMAN_URL", "https://x.com/karimmetrix").rstrip("/")
FREE_RUNS = int(os.getenv("METRIX_FREE_RUNS", "2"))
ACCESS_RUNS_MONTH = int(os.getenv("METRIX_ACCESS_RUNS", "40"))

# ── Client niches (public site + process API) ────────────────────────────────
INDUSTRIES: dict[str, dict[str, Any]] = {
    "ai-agencies": {
        "id": "ai-agencies",
        "name": "AI-агентства и студии",
        "short": "AI-студии",
        "blurb": "Сдача проектов без хаоса",
        "application_point": "operational_efficiency",
        "primary_product": "Terminal Teammate",
        "accent": "#5eead4",
        "default_fin_models": ["orientationforge", "prologforge", "marketforge"],
    },
    "api-for-devs": {
        "id": "api-for-devs",
        "name": "API для разработчиков",
        "short": "API / dev",
        "blurb": "Интеграции и клиентские штуки",
        "application_point": "client_api_integrations",
        "primary_product": "API Cost & Integration Map",
        "accent": "#7dd3fc",
        "default_fin_models": ["edgeforge", "chipforge", "marketforge"],
    },
    "cloud-economy": {
        "id": "cloud-economy",
        "name": "API для разработчиков",
        "short": "API / dev",
        "blurb": "Alias → api-for-devs",
        "application_point": "client_api_integrations",
        "primary_product": "API Cost & Integration Map",
        "accent": "#7dd3fc",
        "alias_of": "api-for-devs",
        "default_fin_models": ["edgeforge", "chipforge", "marketforge"],
    },
    "freelace-d2c": {
        "id": "freelace-d2c",
        "name": "Фриланс и D2C-офферы",
        "short": "Фриланс",
        "blurb": "Идея → документ → заказ",
        "application_point": "d2c_document_liquidity",
        "primary_product": "Workspace Offramp",
        "accent": "#67e8f9",
        "badge": "Автоликвидность",
        "default_fin_models": ["prologforge", "marketforge", "orientationforge"],
    },
    "d2c-offramp": {
        "id": "d2c-offramp",
        "name": "Фриланс и D2C-офферы",
        "short": "D2C",
        "blurb": "Alias → freelace-d2c",
        "application_point": "d2c_document_liquidity",
        "primary_product": "Workspace Offramp",
        "accent": "#67e8f9",
        "badge": "Автоликвидность",
        "alias_of": "freelace-d2c",
        "default_fin_models": ["prologforge", "marketforge", "orientationforge"],
    },
    "expert-services": {
        "id": "expert-services",
        "name": "Экспертные услуги",
        "short": "Эксперты",
        "blurb": "Упаковка оффера и ТЗ",
        "application_point": "offer_packaging",
        "primary_product": "Offer Pack",
        "accent": "#c4b5fd",
        "default_fin_models": ["orientationforge", "prologforge", "marketforge"],
    },
    "ecommerce": {
        "id": "ecommerce",
        "name": "Онлайн-магазины",
        "short": "E-com",
        "blurb": "Оффер, воронка, unit-экон.",
        "application_point": "ecommerce_unit_economics",
        "primary_product": "Offer + Funnel Pack",
        "accent": "#fbbf24",
        "default_fin_models": ["marketforge", "edgeforge", "orientationforge"],
    },
    "content-monetize": {
        "id": "content-monetize",
        "name": "Контент и аудитория",
        "short": "Контент",
        "blurb": "Монетизация без размытия",
        "application_point": "audience_monetization",
        "primary_product": "Monetization Angle Pack",
        "accent": "#86efac",
        "default_fin_models": ["marketforge", "prologforge", "orientationforge"],
    },
    "education": {
        "id": "education",
        "name": "Курсы и обучение",
        "short": "Обучение",
        "blurb": "Программа → продаваемый пакет",
        "application_point": "course_packaging",
        "primary_product": "Course Offer Pack",
        "accent": "#fda4af",
        "default_fin_models": ["prologforge", "orientationforge", "marketforge"],
    },
    "saas-founders": {
        "id": "saas-founders",
        "name": "SaaS и цифровые продукты",
        "short": "SaaS",
        "blurb": "Пилот, метрика, оффер",
        "application_point": "saas_pilot_metric",
        "primary_product": "Pilot Metric Desk",
        "accent": "#a5b4fc",
        "default_fin_models": ["orientationforge", "chipforge", "marketforge"],
    },
    "automation-builders": {
        "id": "automation-builders",
        "name": "Автоматизация и no-code",
        "short": "Авто",
        "blurb": "Сценарии под доход",
        "application_point": "automation_to_income",
        "primary_product": "Automation Income Map",
        "accent": "#f9a8d4",
        "default_fin_models": ["edgeforge", "prologforge", "orientationforge"],
    },
    "cost-ops": {
        "id": "cost-ops",
        "name": "Себестоимость и unit-economics",
        "short": "Unit-экон.",
        "blurb": "Где утекают деньги",
        "application_point": "unit_economics_leak",
        "primary_product": "Leak Map",
        "accent": "#fcd34d",
        "default_fin_models": ["edgeforge", "orientationforge", "chipforge"],
    },
    "cost-engineering": {
        "id": "cost-engineering",
        "name": "Себестоимость и unit-economics",
        "short": "Cost",
        "blurb": "Alias → cost-ops",
        "application_point": "unit_economics_leak",
        "primary_product": "Leak Map",
        "accent": "#fcd34d",
        "alias_of": "cost-ops",
        "default_fin_models": ["edgeforge", "orientationforge", "chipforge"],
    },
    "device-assembly": {
        "id": "device-assembly",
        "name": "Сборка и конфиг устройств",
        "short": "Устройства",
        "blurb": "Руками + онлайн-оффер",
        "application_point": "station_scale",
        "primary_product": "Config product workflow",
        "accent": "#fb7185",
        "default_fin_models": ["metaobject", "chipforge", "orientationforge"],
    },
    "asset-decisions": {
        "id": "asset-decisions",
        "name": "Решения по активам",
        "short": "Активы",
        "blurb": "Метрика и риски, без обещаний",
        "application_point": "decision_support_liquidity",
        "primary_product": "Decision Support Desk",
        "accent": "#f0abfc",
        "badge": "Автоликвидность",
        "default_fin_models": ["marketforge", "edgeforge", "orientationforge"],
    },
    "chipmaking": {
        "id": "chipmaking",
        "name": "Chipmaking",
        "short": "Chips",
        "blurb": "Design-loop voids · yield twin",
        "application_point": "design_loop_clarity",
        "primary_product": "Yield Geometry Twin",
        "accent": "#c4b5fd",
        "default_fin_models": ["chipforge", "metaobject", "edgeforge"],
        "internal": True,
    },
    "telecom": {
        "id": "telecom",
        "name": "Telecom",
        "short": "Telecom",
        "blurb": "SLA SKUs · ARPU/churn",
        "application_point": "sla_arpu_signal",
        "primary_product": "SLA-native SKU Builder",
        "accent": "#86efac",
        "default_fin_models": ["edgeforge", "prologforge", "marketforge"],
        "internal": True,
    },
}

PUBLIC_INDUSTRY_IDS = [
    "ai-agencies",
    "api-for-devs",
    "freelace-d2c",
    "expert-services",
    "ecommerce",
    "content-monetize",
    "education",
    "saas-founders",
    "automation-builders",
    "cost-ops",
    "device-assembly",
    "asset-decisions",
]

CLIENT_NICHE_LIST_RU = [
    "AI-агентства и студии",
    "API-интеграции для разработчиков клиентских продуктов",
    "Фриланс и D2C-офферы (документ под заказ)",
    "Экспертные услуги (коучинг, консалтинг, упаковка)",
    "Онлайн-магазины и товарный D2C",
    "Контент-креаторы и монетизация аудитории",
    "Онлайн-курсы и образовательные продукты",
    "SaaS и цифровые продукты на ранней стадии",
    "Автоматизация, no-code, агентные сценарии под доход",
    "Себестоимость, unit-economics, cost-ops",
    "Сборка, конфиг, периферия + онлайн-продажа",
    "Решения по активам и капиталу (decision support)",
    "Маркетинговые и performance-команды",
    "B2B-услуги и агентства (не только AI)",
    "Локальный сервис с онлайн-записью и оффером",
]

DECISION_SUPPORT_PRODUCT: dict[str, Any] = {
    "id": "decision_support_income_path",
    "name": "Система поддержки решений → доход",
    "one_liner": (
        "Проблема → ясное решение → документ, метрики и следующий оплачиваемый шаг. "
        "Не чат: артефакт, который рынок может купить или агент выполнить."
    ),
    "inputs": ["problem_in_own_words", "niche", "numbers_if_any"],
    "outputs": ["diagnosis", "one_track", "success_metric", "document_pack", "acceptance"],
    "free_layer": ["expert_ideas", "orientation", "tech_tz_draft"],
    "paid_layer": ["implementation_after_confirm", "live_call", "pilot", "main_package"],
    "forbidden": ["subscriptions", "royalties", "yield_guarantees", "placement_percent"],
}


def resolve_industry_id(industry_id: str) -> str:
    """Follow alias_of once (e.g. cloud-economy → api-for-devs)."""
    ind = INDUSTRIES.get(industry_id) or {}
    alias = ind.get("alias_of")
    if alias and alias in INDUSTRIES:
        return str(alias)
    return industry_id

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
    "policy": {
        "expert_ideas_free": True,
        "implementation_after_confirm": True,
        "live_call_on_paid": True,
        "no_subscriptions": True,
        "no_royalties": True,
        "no_placement_percent": True,
        "not_a_cat_in_a_bag": True,
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
