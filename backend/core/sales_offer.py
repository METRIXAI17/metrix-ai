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


def access_offer(*, lang: str = "ru") -> dict[str, Any]:
    ru = lang.startswith("ru")
    price = f"{ACCESS_RUB} ₽ / месяц" if ru else f"{ACCESS_RUB} RUB / month"
    block = CF().offer_block(
        who="оператор, которому нужна названная дыра закрытой" if ru else "an operator who needs a named gap closed",
        void="несобранный оффер и две лестницы цен" if ru else "unassembled offer and colliding prices",
        gate="сходимость ≥ 0.45 · Tribute живой · без ПДн" if ru else "assembly ≥ 0.45 · Tribute live · no PII",
        price=price,
        not_included="сигналы, Main без пилота, Custom $500, Tape Land" if ru else "signals, Main without pilot, Custom $500, Tape Land",
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
        "flagship": FLAGSHIP["name"],
        "legal": LEGAL["what_this_is"] if ru else LEGAL["what_this_is_en"],
        "copy": block,
        "cta_ru": f"Metrix Access · {ACCESS_RUB} ₽ / месяц",
        "cta_en": f"Metrix Access · {ACCESS_RUB} RUB / month",
        "not_this": {
            "main_usd": 2490,
            "note_ru": "Full Package $2490 — отдельный B2B после пилота. Не эта подписка.",
            "note_en": "Full Package $2490 is a separate B2B after pilot. Not this subscription.",
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
            "Two free runs, then wall",
            "Do not sell Main as Access",
        ],
    }
