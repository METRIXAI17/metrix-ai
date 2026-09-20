"""Public SKUs for four rooms. Hits view + Web3 Store requests are free."""

from __future__ import annotations

import os
from typing import Any

from backend.config import HUMAN_CONTACT_URL, TRIBUTE_ACCESS_URL, TRIBUTE_CUSTOM_URL

# Amount windows used by Tribute webhook mapping (USD cents-ish / whole USD).
SKU_BY_USD = {
    100: "sku_100",
    490: "sku_490",
    1000: "sku_1000",
    10000: "sku_10000",
}

SKUS: dict[str, dict[str, Any]] = {
    "free_life": {
        "id": "free_life",
        "usd": 0,
        "rub": 0,
        "tier": "free",
        "file": False,
        "automated": False,
        "requests": None,
        "name_ru": "Для жизни · бесплатный слой",
        "name_en": "For life · free layer",
        "gets_ru": (
            "Суть одной фразой. Решение одной фразой. "
            "5–20 простых вопросов. Eval. Тикер. Цепочка в файл."
        ),
        "gets_en": "Problem one phrase, solution one phrase, 5–20 questions, eval, ticker, chain file.",
    },
    "sku_100": {
        "id": "sku_100",
        "usd": 100,
        "rub": 9900,
        "tier": "micro",
        "file": False,
        "automated": True,
        "requests": 120,
        "days": 31,
        "name_ru": "$100 · 120 мелких задач",
        "name_en": "$100 · 120 small tasks",
        "gets_ru": "Подписка на мелкие задачи. 120 запросов. Без файла.",
        "gets_en": "Small-task subscription. 120 requests. No file.",
        "env": "TRIBUTE_SKU_100_URL",
    },
    "sku_490": {
        "id": "sku_490",
        "usd": 490,
        "rub": 45900,
        "tier": "assist",
        "file": True,
        "automated": True,
        "requests": 40,
        "days": 31,
        "name_ru": "$490 · Assist",
        "name_en": "$490 · Assist",
        "gets_ru": "Две строки, не эссе. Нестандартный ход, конкретная библиотека, до слота. Файл.",
        "gets_en": "Two lines, not an essay. Unusual move, concrete library, to the slot. File.",
        "env": "TRIBUTE_SKU_490_URL",
    },
    "sku_1000": {
        "id": "sku_1000",
        "usd": 1000,
        "rub": 99000,
        "tier": "standard",
        "file": True,
        "automated": True,
        "requests": 80,
        "days": 90,
        "name_ru": "$1000 · стандарт",
        "name_en": "$1000 · standard",
        "gets_ru": "Разработка стандарта: рекурсивная методика + спеки + кодовая надстройка. Файл.",
        "gets_en": "Standard: recursive methodology + specs + code overlay. File.",
        "env": "TRIBUTE_SKU_1000_URL",
    },
    "sku_10000": {
        "id": "sku_10000",
        "usd": 10000,
        "rub": 990000,
        "tier": "contour",
        "file": True,
        "automated": False,
        "requests": 200,
        "days": 180,
        "name_ru": "$10 000 · автономный контур",
        "name_en": "$10 000 · autonomous contour",
        "gets_ru": "Дизайн автономного контура в ваш проект. Плотнее спеки, тот же контур. Файл.",
        "gets_en": "Autonomous contour designed into your project. Denser specs, same contour. File.",
        "env": "TRIBUTE_SKU_10000_URL",
    },
}

FREE_FACTS_RU = (
    "Хиты — смотреть бесплатно.\n"
    "Web3 Store — запросы бесплатно."
)
FREE_FACTS_EN = "Hits: view free.\nWeb3 Store: requests free."

PUBLIC_TABS = [
    {
        "id": "hits",
        "title": "Хиты",
        "title_en": "Hits",
        "title_short": "Хиты",
        "free": True,
        "one_liner": "Мувики, которые заслужили данные. Не сигнальный ассистент.",
        "accent": "#5eead4",
    },
    {
        "id": "flagship",
        "title": "Флагман",
        "title_en": "Flagship",
        "title_short": "Флагман",
        "free": True,
        "one_liner": "Выдаёт суть вопроса и решение одной фразой. Потом вопросы — сводка векторов. $490.",
        "accent": "#38bdf8",
    },
    {
        "id": "store",
        "title": "Web3 Store",
        "title_en": "Web3 Store",
        "title_short": "Store",
        "free": True,
        "one_liner": "Заказы Web3 как входящий поток. Запросы бесплатно.",
        "accent": "#c4b5fd",
    },
    {
        "id": "tariffs",
        "title": "Тарифы",
        "title_en": "Tariffs",
        "title_short": "Тарифы",
        "free": True,
        "one_liner": "Флагман — автономный контур в ваш проект. Хиты и Store бесплатно.",
        "accent": "#fbbf24",
    },
]


def _url_for(sku: str) -> str:
    meta = SKUS.get(sku) or {}
    env_name = meta.get("env") or ""
    raw = (os.getenv(env_name, "") if env_name else "").strip().rstrip("/")
    if raw:
        return raw
    if sku in ("sku_490", "sku_1000") and TRIBUTE_CUSTOM_URL:
        return TRIBUTE_CUSTOM_URL
    return TRIBUTE_ACCESS_URL or TRIBUTE_CUSTOM_URL or "https://t.me/tribute"


def sku_of(sid: str) -> dict[str, Any]:
    row = dict(SKUS.get(sid) or SKUS["free_life"])
    row["pay_url"] = _url_for(sid) if sid != "free_life" else ""
    return row


def map_tribute_amount(amount: Any, name: str = "") -> str:
    """Map Tribute payload amount / product name onto a SKU."""
    text = f"{name} {amount}".lower()
    for needle, sid in (
        ("10000", "sku_10000"),
        ("10 000", "sku_10000"),
        ("10k", "sku_10000"),
        ("contour", "sku_10000"),
        ("1000", "sku_1000"),
        ("standard", "sku_1000"),
        ("стандарт", "sku_1000"),
        ("490", "sku_490"),
        ("assist", "sku_490"),
        ("120", "sku_100"),
        ("sku_100", "sku_100"),
    ):
        if needle in text:
            return sid
    try:
        n = float(str(amount).replace(",", "").replace("$", "").strip() or 0)
    except ValueError:
        n = 0.0
    if n >= 8000:
        return "sku_10000"
    if n >= 800:
        return "sku_1000"
    if n >= 300:
        return "sku_490"
    if n >= 50:
        return "sku_100"
    return "access_month"


def tariff_board(lang: str = "ru") -> dict[str, Any]:
    ru = (lang or "ru").startswith("ru")
    paid = [sku_of(s) for s in ("sku_100", "sku_490", "sku_1000", "sku_10000")]
    free = sku_of("free_life")
    return {
        "tabs": PUBLIC_TABS,
        "free_facts": FREE_FACTS_RU if ru else FREE_FACTS_EN,
        "free_life": free,
        "paid": paid,
        "human": HUMAN_CONTACT_URL or "https://x.com/karimmetrix",
        "flagship": {
            "usd": 490,
            "role_ru": (
                "Флагман — автономный контур в ваш проект. "
                "Плотнее спеки, тот же поток. Комнаты, не новая линейка. "
                "В боте посадка $490: комбо рекурсивных решений и терминальный процесс."
            ),
            "role_en": (
                "Flagship is an autonomous contour on your project. "
                "Denser specs, same stream. Rooms, not a new product line. "
                "In the bot the sit is $490: recursive combo + terminal process."
            ),
        },
        "note": (
            "Флагман в тарифах = контур в ваш проект. В комнате Флагман оплата одна: $490. "
            "После оплаты файл — кроме $100."
            if ru
            else "Flagship in tariffs = contour on your project. In the Flagship room the pay is $490. File after pay except $100."
        ),
    }
