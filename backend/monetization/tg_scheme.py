"""
Telegram + desktop monetization scheme.

Combines flagship cards, work-by-request, promo-lite, functions,
structural earning (Funding pillar 1), market making, auto-orders.
"""

from __future__ import annotations

from typing import Any


# Prices: RUB for RF cards (YooKassa), USD showcase, Stars for TG-native.
SKUS: dict[str, dict[str, Any]] = {
    "access_month": {
        "rub": 1490, "usd": 16, "stars": 0, "tier": "access",
        "name": "Metrix Access · месяц (все вкладки)",
    },
    "access_year": {
        "rub": 12900, "usd": 139, "stars": 0, "tier": "access",
        "name": "Metrix Access · год",
    },
    "ai_tools_base": {
        "rub": 18900, "usd": 200, "stars": 0, "tier": "install",
        "name": "AI-tools · базовый бот",
    },
    "custom_teammate": {
        "rub": 47900, "usd": 500, "stars": 0, "tier": "custom",
        "name": "Custom Teammate",
    },
    "tape_land": {
        "rub": 209000, "usd": 2490, "stars": 0, "tier": "core",
        "name": "Tape Land",
    },
    "request_orient": {
        "rub": 0, "usd": 0, "stars": 0, "tier": "free",
        "name": "Ориентация (работа по запросу, вход)",
    },
    "request_deep": {
        "rub": 2490, "usd": 29, "stars": 1500, "tier": "mid",
        "name": "Глубокий прогон запроса (сборка + режим + пак)",
    },
    "request_complex": {
        "rub": 7900, "usd": 99, "stars": 4500, "tier": "high",
        "name": "Сложный запрос-ответ (три стороны, файлы, delivery)",
    },
    "flagship_reader": {
        "rub": 1490, "usd": 19, "stars": 900, "tier": "mid",
        "name": "Флагман: Task reader",
    },
    "flagship_metric": {
        "rub": 3490, "usd": 39, "stars": 2200, "tier": "high",
        "name": "Флагман: Metric engine",
    },
    "flagship_core": {
        "rub": 4990, "usd": 59, "stars": 3200, "tier": "high",
        "name": "Флагман: Growth/Yield core",
    },
    "flagship_coop": {
        "rub": 4990, "usd": 59, "stars": 3200, "tier": "high",
        "name": "Флагман: Client packs",
    },
    "flagship_assist": {
        "rub": 6900, "usd": 79, "stars": 4000, "tier": "high",
        "name": "Флагман: Implement + test",
    },
    "fn_creative": {
        "rub": 990, "usd": 12, "stars": 400, "tier": "low",
        "name": "Творческий ассистент — прогон",
    },
    "fn_logger": {
        "rub": 1490, "usd": 18, "stars": 700, "tier": "mid",
        "name": "Solution logger — разбор",
    },
    "fn_mockup": {
        "rub": 3490, "usd": 39, "stars": 2000, "tier": "high",
        "name": "Цифровой макет индивидуала",
    },
    "promo_cards": {
        "rub": 490, "usd": 6, "stars": 150, "tier": "mass",
        "name": "Промо: карточки описаний",
    },
    "promo_reels": {
        "rub": 690, "usd": 8, "stars": 200, "tier": "mass",
        "name": "Промо: идеи для роликов",
    },
    "promo_prompts": {
        "rub": 290, "usd": 4, "stars": 100, "tier": "mass",
        "name": "Промо: промпты для консалтинга",
    },
    "promo_pack": {
        "rub": 1490, "usd": 18, "stars": 700, "tier": "mid",
        "name": "Промо-пак (3 выхода)",
    },
    "terminal_mine": {
        "rub": 2490, "usd": 29, "stars": 1500, "tier": "mid",
        "name": "Терминал: майнинг ожидающих ордеров",
    },
    "pilot_14": {
        "rub": 12900, "usd": 149, "stars": 0, "tier": "pilot",
        "name": "Пилот 14 дней (не Stars — слишком крупно)",
    },
    "full_package": {
        "rub": 209000, "usd": 2490, "stars": 0, "tier": "core",
        "name": "Full Orientation Package",
    },
}


# Mix assumption for 90-day TG launch (conservative).
MIX_90D = {
    "mau": 400,
    "paying_pct": 0.08,
    "payers": 32,
    "avg_tickets": [
        ("promo_mass", 18, 490),
        ("functions", 8, 1490),
        ("request_deep", 5, 2490),
        ("flagship", 2, 3490),
        ("terminal", 1, 2490),
        ("pilot", 0.4, 12900),
    ],
}


def _gm(rub: float, pay_in: str) -> float:
    """Gross after payment rails."""
    if pay_in == "stars":
        # Telegram keeps ~30% of Stars in many regions
        return rub * 0.70
    if pay_in == "yookassa":
        # ~3.5% acquirer + ~5% TG payment if via Bot Payments; we model 8% all-in
        return rub * 0.92
    return rub * 0.95


def scheme_payload() -> dict[str, Any]:
    payers = MIX_90D["payers"]
    gmv = 0.0
    for _name, n, price in MIX_90D["avg_tickets"]:
        gmv += n * price
    # mix is "per 32 payers over 90d" as ticket counts
    gmv_90 = gmv
    net_yk = _gm(gmv_90, "yookassa")
    net_stars = _gm(gmv_90, "stars")
    # earning (structural): % of GMV that repeats without new sales work
    repeat_share = 0.22  # promo + logger subscriptions / re-runs
    structural_90 = gmv_90 * repeat_share
    return {
        "module": "TG Monetization Scheme",
        "skus": SKUS,
        "rails": {
            "rf_cards": {
                "possible": True,
                "how": "Telegram Payments + ЮKassa (provider_token). МИР / RF Visa/MC.",
                "not": "Stripe, PayPal, Apple Pay US — не для карт РФ.",
                "stars": "Telegram Stars — да, но комиссия высокая и потолок для B2B низкий.",
            },
            "recommended": "YooKassa for RUB SKUs ≤ pilot; wire/invoice for $2490; Stars only for promo mass.",
        },
        "layers": [
            {"id": "promo", "role": "top-of-funnel mass, 290–690 ₽", "earning": "repeat SKU"},
            {"id": "functions", "role": "habit (logger) + identity (mockup)", "earning": "re-run + mockup one-off"},
            {"id": "request", "role": "core complex Q&A", "earning": "orient_run lever"},
            {"id": "flagships", "role": "named products, not a catalog dump", "earning": "SKU + upsell to pilot"},
            {"id": "terminal", "role": "pending orders / mining", "earning": "auto_orders + MM two-sided"},
            {"id": "pilot_full", "role": "ops close, not in Stars", "earning": "structural income after setup"},
        ],
        "unit_90d_conservative": {
            "mau": MIX_90D["mau"],
            "payers": payers,
            "gmv_rub": round(gmv_90, 0),
            "net_yookassa_rub": round(net_yk, 0),
            "net_if_all_stars_rub": round(net_stars, 0),
            "structural_repeat_rub": round(structural_90, 0),
            "note": "32 платящих из 400 MAU за 90 дней. Это не прогноз рынка — это нижняя планка при ручном MM.",
        },
        "market_making": {
            "formal": "Two-sided quote on attention: bid=free demo/orientation, ask=paid implement/SKU.",
            "inventory": "Flagship cards + promo SKUs always in stock (digital).",
            "spread": "Free→490 ₽ promo is the tight spread; 0→2490 ₽ request is wide — only quote after reader.",
            "inventory_risk": "Zero COGS on digital; risk is reputation if auto-mode misfires.",
            "how_to_promote": [
                "Quote both sides in every public post (demo free / pack paid).",
                "Seed the bid: 10 public orientations/week, no DM-first.",
                "Tighten spread on promo SKUs (mass) to make a visible tape.",
                "Do not market-make the $2490 like a sticker — that is a negotiated ask after pilot.",
            ],
        },
        "earning_vs_sales": {
            "sales": "Someone buys a SKU once.",
            "earning": "Surface already running produces cash when touched (structural auto-income).",
            "wired_levers": ["orient_run", "promo_pack", "pilot_14", "full_package", "auto_orders"],
        },
    }
