"""Web3 Store — seven rooms. Requests are free. Lead-gen, not a new product line."""

from __future__ import annotations

from typing import Any

CATEGORIES: list[dict[str, Any]] = [
    {
        "n": 1,
        "id": "a2a",
        "title": "Наводка A2A",
        "title_en": "A2A steer",
        "one": "Первый A2A: наводит запрос и режет неэффективности скринером.",
        "unit": "Screener pass",
        "accent": "#5eead4",
        "image": "/assets/store/cat-a2a.jpg",
        "line": 1,
        "sku": "store_a2a",
        "placeholder": "Что ломается в запросе: люди, деньги, срок…",
    },
    {
        "n": 2,
        "id": "deeptech",
        "title": "Deep Tech",
        "title_en": "Deep Tech",
        "one": "RTL, FPGA, данные с чипов, метрическая прошивка.",
        "unit": "Silicon brief",
        "accent": "#fbbf24",
        "image": "/assets/store/cat-deeptech.jpg",
        "line": 2,
        "sku": "store_deeptech",
        "placeholder": "Какой чип слепой и какую функцию он должен держать…",
    },
    {
        "n": 3,
        "id": "brand",
        "title": "Бренд-активы",
        "title_en": "Brand assets",
        "one": "Имя, голос, кадр. Объект, который можно поставить в X.",
        "unit": "Brand object",
        "accent": "#c4b5fd",
        "image": "/assets/store/cat-brand.jpg",
        "line": 3,
        "sku": "store_brand",
        "placeholder": "Какой объект бренда должен остаться в руках…",
    },
    {
        "n": 4,
        "id": "libraries",
        "title": "Библиотеки",
        "title_en": "Libraries",
        "one": "Пак, который повторяется. Не чат — карточка.",
        "unit": "Library pack",
        "accent": "#67e8f9",
        "image": "/assets/store/cat-libraries.jpg",
        "line": 4,
        "sku": "store_libraries",
        "placeholder": "Какой пак должен открываться без нового брифа…",
    },
    {
        "n": 5,
        "id": "rails",
        "title": "Рельсы продаж",
        "title_en": "Sales rails",
        "one": "Типизация продажи: кто платит, какой unit, какой kill.",
        "unit": "Sales rail",
        "accent": "#fb7185",
        "image": "/assets/store/cat-rails.jpg",
        "line": 5,
        "sku": "store_rails",
        "placeholder": "Кто платит, за какой unit, когда молчать…",
    },
    {
        "n": 6,
        "id": "quality",
        "title": "Качество и метрики",
        "title_en": "Quality & metrics",
        "one": "Самая проработанная линия: понятие, метрика, готовые проекты.",
        "unit": "Quality lattice",
        "accent": "#38bdf8",
        "image": "/assets/store/cat-quality.jpg",
        "line": 6,
        "sku": "store_quality",
        "placeholder": "Какое понятие размыто и какую метрику поставить на него…",
    },
    {
        "n": 7,
        "id": "placements",
        "title": "Размещения в потоках",
        "title_en": "Flow placements",
        "one": "Терминальный ИИ: агент садится в ваш денежный поток и молчит, пока не его ход.",
        "unit": "Placement seat",
        "accent": "#f59e0b",
        "image": "/assets/store/cat-placements.jpg",
        "line": 7,
        "sku": "store_placements",
        "placeholder": "Куда посадить агента в вашем денежном потоке…",
    },
]


def list_categories(*, lang: str = "ru") -> list[dict[str, Any]]:
    ru = not (lang or "ru").startswith("en")
    out = []
    for c in CATEGORIES:
        row = dict(c)
        if not ru:
            row["title"] = c["title_en"]
        out.append(row)
    return out


def category_by_id(sid: str) -> dict[str, Any] | None:
    key = (sid or "").strip().lower()
    if key.isdigit():
        n = int(key)
        for c in CATEGORIES:
            if c["n"] == n:
                return dict(c)
        return None
    for c in CATEGORIES:
        if c["id"] == key or str(c["n"]) == key:
            return dict(c)
    aliases = {
        "screener": "a2a",
        "steer": "a2a",
        "chip": "deeptech",
        "rtl": "deeptech",
        "assets": "brand",
        "lib": "libraries",
        "sales": "rails",
        "metrics": "quality",
        "terminal": "placements",
        "flows": "placements",
        "seat": "placements",
    }
    mapped = aliases.get(key)
    if mapped:
        return category_by_id(mapped)
    return None


def catalog_payload(*, lang: str = "ru") -> dict[str, Any]:
    return {
        "ok": True,
        "brand": "Metrix Store",
        "door_rule": "Один код. Семь комнат. Друг не спрашивает паспорт дважды.",
        "domain": {"main": "mtrx.ai", "store": "mx.store"},
        "categories": list_categories(lang=lang),
    }
