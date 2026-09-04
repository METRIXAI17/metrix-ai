"""Sellable Access offer. One price. Copy firmware. Engine gates.

Main $2490 is a separate B2B package after pilot — not this SKU.
"""

from __future__ import annotations

import os
from typing import Any

from backend.core.circle_system.copy_firmware import CopyFirmware as CF
from backend.core.product_180 import FLAGSHIP, LEGAL, PRICING, VERSION


ACCESS_RUB = 3290
ACCESS_YEAR_RUB = 32900  # 10 months
ACCESS_USD = 35
BOT_LAND_USD = 490
BOT_LAND_MAX_USD = 1990
METRIX_AI_USD = 2490
ACCESS_RESULTS_MONTH = 40
FREE_RESULTS = 2


def access_offer(*, lang: str = "ru") -> dict[str, Any]:
    ru = lang.startswith("ru")
    price = f"{ACCESS_RUB} ₽ / месяц" if ru else f"{ACCESS_RUB} RUB / month"
    block = CF().offer_block(
        who="оператор, которому нужна названная дыра закрытой" if ru else "an operator who needs a named gap closed",
        void="несобранный оффер и две лестницы цен" if ru else "unassembled offer and colliding prices",
        gate="сходимость ≥ 0.45 · Tribute живой · без ПДн" if ru else "assembly ≥ 0.45 · Tribute live · no PII",
        price=price,
        not_included="сигналы, Metrix AI $2490, Custom $500" if ru else "signals, Metrix AI $2490, Custom $500",
        voice="b2c",
        lang=lang,
    )
    return {
        "sku": "access_month",
        "name": "Metrix Access",
        "rub": ACCESS_RUB,
        "usd": ACCESS_USD,
        "year_rub": ACCESS_YEAR_RUB,
        "period": "month",
        "covers": PRICING["access"]["covers"],
        "free_results": FREE_RESULTS,
        "monthly_results": ACCESS_RESULTS_MONTH,
        "bot_land_usd": BOT_LAND_USD,
        "bot_land_max_usd": BOT_LAND_MAX_USD,
        "metrix_ai_usd": METRIX_AI_USD,
        "flagship": FLAGSHIP["name"],
        "legal": LEGAL["what_this_is"] if ru else LEGAL["what_this_is_en"],
        "copy": block,
        "cta_ru": f"Metrix Access · {ACCESS_RUB} ₽ / месяц",
        "cta_en": f"Metrix Access · {ACCESS_RUB} RUB / month",
        "not_this": {
            "metrix_ai_usd": METRIX_AI_USD,
            "bot_land_usd": BOT_LAND_USD,
            "note_ru": "Бот — ленд ≤ $1990. Metrix AI $2490 — движок ecom физ. товаров. Access — подписка на бот.",
            "note_en": "Bot is the land product ≤ $1990. Metrix AI $2490 is the physical-goods ecom engine. Access is the bot subscription.",
        },
        "layers": {
            "land": "Karim Metrix Bot · artefact",
            "engine": "Metrix AI · physical goods ecom (ops + catalog project + promo)",
            "access": "3290 ₽ / month · 40 results",
            "theses": "Artefacts · theses on order",
        },
    }


def sales_readiness() -> dict[str, Any]:
    tribute = (os.getenv("TRIBUTE_ACCESS_URL") or "").strip()
    secret = bool((os.getenv("METRIX_TOKEN_SECRET") or "").strip())
    key = bool((os.getenv("TRIBUTE_API_KEY") or "").strip())
    bot = bool((os.getenv("TELEGRAM_BOT_TOKEN") or "").strip())
    checks = {
        "price_unified_3290": True,
        "tribute_url": bool(tribute) and "tribute" in tribute.lower(),
        "tribute_api_key": key,
        "token_secret": secret,
        "bot_token": bot,
        "pii_minimized": True,
        "signals_forbidden": True,
    }
    open_slots = [k for k, v in checks.items() if not v]
    sellable_access = checks["price_unified_3290"]  # copy is ready; Tribute is ops
    sellable_live = all(checks.values())
    return {
        "module": "Sales Readiness",
        "version": VERSION,
        "access": access_offer(lang="ru"),
        "checks": checks,
        "open_slots": open_slots,
        "sellable_access_copy": sellable_access,
        "sellable_live_payments": sellable_live,
        "main_package_ready": False,
        "main_reason": "engine: void_membrane must stay bound; Main $2490 only after predicted_end≥0.7 and risk≠high",
        "next": [
            "Tribute product Metrix Access 3290 ₽ / month",
            "TRIBUTE_ACCESS_URL + TRIBUTE_API_KEY + webhook + METRIX_TOKEN_SECRET",
            "Two free results in the bot, then Access 3290",
            "Do not sell Metrix AI $2490 as the bot",
        ],
    }
