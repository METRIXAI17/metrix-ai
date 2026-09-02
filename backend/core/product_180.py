"""Karim Metrix 1.8.0 — product source of truth.

Three formal tabs. One subscription. Code of an agreed model, not signals.
"""

from __future__ import annotations

from typing import Any

VERSION = "1.8.0"
CODENAME = "IN-OUT CHAIN"
RELEASE = "2026-09-03-in-out-chain"

# ── Flagship ────────────────────────────────────────────────────────────────
FLAGSHIP = {
    "id": "in_out_chain",
    "name": "In-Out Chain",
    "name_ru": "In-Out Chain",
    "sticker": "Chain",
    "accent": "#5eead4",
    "tagline_ru": "Снимает рутину. Закрывает решённое и нерешённое. Режет стоимость проекта на входе и на выходе.",
    "tagline_en": "Kills routine. Closes solved and unsolved work. Cuts project cost on the way in and the way out.",
    "essence_ru": (
        "Цепочка in→out: рутина снимается кодом согласованной модели, "
        "решённые задачи закрываются триггером, нерешённые ставятся в параметр, "
        "стоимость проекта падает и на входе (онбординг, закупка внимания), "
        "и на выходе (сдача, сопровождение, риск)."
    ),
    "page": "/chain/",
}

TABS = [
    {
        "id": "chain",
        "title": "In-Out Chain",
        "title_short": "Chain",
        "legacy": ("landing", "demo", "лендинг", "демо"),
        "role_ru": "Каталог доступных моделей и одна подписка, которая финансирует развитие.",
    },
    {
        "id": "teammates",
        "title": "AI Teammates",
        "title_short": "Teammates",
        "legacy": ("engine", "движок", "агенты", "agents"),
        "role_ru": "Воркфлоу новых решений, четыре живых агента, кастом, связь с человеком.",
    },
    {
        "id": "artefacts",
        "title": "Artefacts",
        "title_short": "Artefacts",
        "legacy": ("making", "мейкинг", "посты", "posts"),
        "role_ru": "Аналитическая панель и генератор предложений. Папка Tape Land / two-leg-tape.",
    },
]

# ── Pricing (asserted) ──────────────────────────────────────────────────────
# $5 user sub does not cover Tribute 10% + Railway floor + a second render.
# Hobby $5 is the infra floor, not the product price.
PRICING = {
    "access": {
        "sku": "access_month",
        "rub": 1490,
        "usd": 16,
        "period": "month",
        "name": "Metrix Access",
        "covers": "все три вкладки, 4 модели, риск-движок, артефакты, обновления кода как есть",
        "why_not_5usd": (
            "После комиссии Tribute 10% с $5 остаётся $4.50. "
            "Railway Hobby — это пол $5, не потолок. Второй сервис (отдельный рендер Tape Land) "
            "съедает ещё $5–12. $5-подписка финансирует хостинг в ноль или в минус "
            "и не оплачивает обновления моделей."
        ),
    },
    "access_year": {
        "sku": "access_year",
        "rub": 12900,
        "usd": 139,
        "period": "year",
        "name": "Metrix Access · год",
    },
    "ai_tools": {
        "sku": "ai_tools_base",
        "usd": 200,
        "rub": 18900,
        "name": "AI-tools · базовый бот",
        "note": "те же четыре модели, без кастомной посадки под автора",
    },
    "custom_teammate": {
        "sku": "custom_teammate",
        "usd": 500,
        "rub": 47900,
        "name": "Custom Teammate",
        "note": "посадка под специфику бизнеса, автора и контура",
    },
    "tape_land": {
        "sku": "tape_land",
        "usd": 2490,
        "rub": 209000,
        "name": "Tape Land",
        "note": "сложные проекты: отношение параметров как образование, метрики как артефакт",
    },
}

# ── Legal ───────────────────────────────────────────────────────────────────
LEGAL = {
    "what_this_is": (
        "Код согласованной модели. Обновляется в реальном времени как есть. "
        "Не торговые сигналы, не индивидуальная инвестиционная рекомендация, "
        "не обещание доходности."
    ),
    "what_this_is_en": (
        "Code of an agreed model, updated in real time as-is. "
        "Not trading signals, not personalized investment advice, not a return promise."
    ),
    "forbidden_words_public": ("сигнал", "signals", "гарантир", "безриск"),
    "terms": {
        "code_event": "событие кода согласованной модели (не сигнал)",
        "close_trigger": "закрывающий триггер сделки по правилу модели",
        "stop_trigger": "стоп-триггер: инвалидация тезиса, не «откат настроения»",
        "r_multiple": "мера исхода после закрытия. Не размер позиции.",
        "leverage": "отношение нотионала к капиталу. Риск-движок не путает его с R.",
    },
}

# ── Auth decision ───────────────────────────────────────────────────────────
AUTH_DECISION = {
    "problem": "cookie vs token-per-tab vs raw telegram_id",
    "rejected": [
        {
            "id": "cookie",
            "why": (
                "Telegram Mini App — WebView. Cookie с Vercel на Railway кросс-ориджин "
                "часто не живёт. ITP / третий сайт / iframe Telegram."
            ),
        },
        {
            "id": "token_per_tab",
            "why": (
                "Три Tribute-продукта, три вебхука, пользователь теряет доступ к одной вкладке. "
                "Дробит единственную подписку, которая должна финансировать развитие."
            ),
        },
        {
            "id": "store_telegram_id",
            "why": (
                "telegram user_id — персональные данные. Хранение сырого id на Railway (не РФ) "
                "попадает под 152-ФЗ / локализацию."
            ),
        },
    ],
    "chosen": {
        "id": "one_opaque_token",
        "how": (
            "Один access-токен на все вкладки. На диске только HMAC-SHA256(subject) и hash токена, "
            "срок, тариф. Сырой telegram_id, имя, телефон, email не пишем. "
            "Tribute — merchant of record по платежу. Мы храним факт доступа, не анкету."
        ),
    },
}

# ── Railway ─────────────────────────────────────────────────────────────────
RAILWAY = {
    "current": "Hobby $5/mo credit, one FastAPI service (metrix-ai-production)",
    "rates_2026": {
        "hobby_floor_usd": 5,
        "pro_floor_usd": 20,
        "cpu_usd_per_vcpu_mo": 20,
        "ram_usd_per_gb_mo": 10,
        "egress_usd_per_gb": 0.05,
        "volume_usd_per_gb_mo": 0.15,
    },
    "forecast_one_service_usd": {
        "idle_api_0.15vcpu_0.4gb": 5.0,  # covered by Hobby floor
        "busy_0.4vcpu_0.8gb_plus_egress": 11.0,
        "plus_separate_tape_land_node": 18.0,
    },
    "decision": (
        "Не рендерить Tape Land отдельным Node-сервисом в 1.8.0. "
        "Порт two-leg-tape в Python внутри этого же процесса. "
        "Hobby $5 хватает на API+бота при низком трафике. "
        "Отдельный рендер — после 20+ Access, тогда Pro $20."
    ),
    "enough_for_updates": (
        "Сами обновления кода — git push, Railway пересобирает тот же сервис, "
        "отдельный тариф не нужен. Платить за «каждый апдейт как отдельный сервис» — нет."
    ),
}

# ── Unit economics (lead) ───────────────────────────────────────────────────
LEAD = {
    "access": {
        "price_rub": 1490,
        "tribute_net_rub": round(1490 * 0.90),
        "predicted_cac_rub": 650,
        "note": (
            "Органика X + Telegram, без закупки на старте. "
            "CAC ≈ время Карима на пост/ответ, приведённое к 650 ₽ на конверт. "
            "Payback < 1 месяца при удержании ≥ 2 циклов."
        ),
        "ltv_3mo_rub": 1490 * 3,
        "conversion_from_paywall": "4–8% тех, кто получил hit-артефакт",
    },
    "custom_teammate": {
        "price_usd": 500,
        "predicted_cac_usd": 110,
        "note": (
            "10–18% тех, кто нажал «связаться с человеком» после двух прогонов тимейта. "
            "Цикл 7–21 день. Не из холодного трафика."
        ),
        "conversion_from_access": "8–15% Access, кто дошёл до кастома",
    },
}

HUMAN_CONTACT_DEFAULT = "https://x.com/karimmetrix"


def catalog_overlay() -> dict[str, Any]:
    return {
        "version": VERSION,
        "codename": CODENAME,
        "flagship": FLAGSHIP,
        "tabs": TABS,
        "pricing": PRICING,
        "legal": LEGAL,
        "auth": AUTH_DECISION["chosen"],
        "human": HUMAN_CONTACT_DEFAULT,
        "promise": LEGAL["what_this_is"],
    }
