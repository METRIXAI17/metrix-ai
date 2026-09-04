"""Karim Metrix — five sellable sections. One subscription. Code of an agreed model, not signals.
"""

from __future__ import annotations

from typing import Any

VERSION = "1.9.0"
CODENAME = "FIVE SHOPS"
RELEASE = "2026-09-04-five-sections"

# ── Flagship ────────────────────────────────────────────────────────────────
FLAGSHIP = {
    "id": "life",
    "name": "Идеи для жизни",
    "name_ru": "Идеи для жизни",
    "sticker": "Life",
    "accent": "#5eead4",
    "tagline_ru": "Пять разделов. Короткий чат, торговые боты, конфиги ремесла, таргет агентов, каталог магазина.",
    "tagline_en": "Five shops: life ideas, trading bots, craft configs, agent targeting, shop catalog.",
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
        "id": "life",
        "title": "Идеи для жизни",
        "title_short": "Жизнь",
        "legacy": ("chain", "landing", "demo", "лендинг", "демо"),
        "role_ru": "Чат с идеями, что улучшить в дне.",
    },
    {
        "id": "bots",
        "title": "Торговые боты",
        "title_short": "Боты",
        "legacy": ("strategies", "strategy", "стратегии"),
        "role_ru": "Витрина ботов. Эксперимент с промптом без кода и оценкой.",
    },
    {
        "id": "craft",
        "title": "Конфиги для ремесла",
        "title_short": "Ремесло",
        "legacy": ("teammates", "engine", "движок"),
        "role_ru": "Билдер конфига для ремесленника.",
    },
    {
        "id": "target",
        "title": "Таргет ИИ-агентов",
        "title_short": "Агенты",
        "legacy": ("agents", "agent", "агенты"),
        "role_ru": "Куда целиться агенту: роль, канал, текст, молчание.",
    },
    {
        "id": "shop",
        "title": "Каталог магазина",
        "title_short": "Магазин",
        "legacy": ("artefacts", "making", "мейкинг", "посты"),
        "role_ru": "Уникальный каталог: имя, описание, когда нужно.",
    },
]

# ── Pricing (asserted) ──────────────────────────────────────────────────────
# $5 user sub does not cover Tribute 10% + Railway floor + a second render.
# Hobby $5 is the infra floor, not the product price.
PRICING = {
    "access": {
        "sku": "access_month",
        "rub": 3290,
        "usd": 35,
        "period": "month",
        "name": "Metrix Access",
        "covers": "бот: 40 результатов в месяц, три вкладки, 4 модели, риск-движок",
        "monthly_results": 40,
        "live_snapshots_debit": False,
        "free_results": 2,
        "why_not_5usd": (
            "После комиссии Tribute 10% с $5 остаётся $4.50. "
            "Railway Hobby — это пол $5, не потолок. Access 3290 ₽ закрывает хостинг, "
            "комиссию Tribute и развитие моделей. $2490 Main — другой SKU, после пилота."
        ),
        "why_3290": (
            "Движок: две лестницы цен оставляли revenue_hinge дырявым. "
            "Один публичный SKU Access = 3290 ₽. Net Tribute ≈ 2961 ₽. "
            "Год = 32 900 ₽ (10 месяцев)."
        ),
    },
    "access_year": {
        "sku": "access_year",
        "rub": 32900,
        "usd": 350,
        "period": "year",
        "name": "Metrix Access · год",
    },
    "bot_land": {
        "sku": "bot_artefact",
        "usd": 490,
        "usd_max": 1990,
        "rub": 45900,
        "name": "Karim Metrix Bot · артефакт (ленд)",
        "note": (
            "Ленд-продукт: Telegram-бот как артефакт. Не Metrix AI. "
            "Потолок $1990. Не $2490."
        ),
        "covers": "вход: Access 3290 ₽/мес или разовая посадка бота",
    },
    "ai_tools": {
        "sku": "ai_tools_base",
        "usd": 200,
        "rub": 18900,
        "name": "AI-tools · базовый бот",
        "note": "те же четыре модели, без кастомной посадки под автора",
    },
    "metrix_ai": {
        "sku": "full_package",
        "usd": 2490,
        "rub": 209000,
        "name": "Metrix AI · движок",
        "note": (
            "Главный движок 1.8. В боте он собирает: тезисы, конфиги, in-out эксперименты. "
            "Платный SKU $2490 — тот же движок под ecom физических товаров "
            "(ops + каталог + промо). Не второй мозг. Цифра/курсы — не этот SKU."
        ),
        "tracks": ("life", "trading", "craft", "agents", "ecom"),
        "vertical": "physical_goods_ecom",
        "bot_surfaces": ("life", "bots", "craft", "target", "shop"),
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
        "price_rub": 3290,
        "tribute_net_rub": round(3290 * 0.90),
        "predicted_cac_rub": 900,
        "note": (
            "Органика X + Telegram. Стена 3290 жёстче, чем 1490. "
            "Net Tribute ≈ 2961 ₽. Payback < 1 месяца при удержании ≥ 1 цикла."
        ),
        "ltv_3mo_rub": 3290 * 3,
        "conversion_from_paywall": "3–6% тех, кто получил hit-артефакт",
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
