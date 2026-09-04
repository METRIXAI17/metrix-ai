"""Five sellable bot sections. Concrete names. One engine, five modes."""

from __future__ import annotations

from typing import Any

SECTIONS: list[dict[str, Any]] = [
    {
        "id": "life",
        "title": "Идеи для жизни",
        "title_short": "Жизнь",
        "title_en": "Life ideas",
        "accent": "#5eead4",
        "image": "/tg/assets/sec-life.jpg",
        "mode": "life",
        "industry": "expert-services",
        "one_liner": "Чат: что улучшить сегодня — сон, деньги, дом, нагрузка. Короткие идеи, не лекция.",
        "vitrine_label": "Витрина идей",
        "cta": "Написать, что сейчас тяжело",
        "placeholder": "Мало сна, касса в тумане, не знаю с чего начать день…",
        "legacy": ("chain", "landing", "demo", "лендинг", "демо", "in-out", "inout"),
    },
    {
        "id": "bots",
        "title": "Торговые боты",
        "title_short": "Боты",
        "title_en": "Trading bots",
        "accent": "#fbbf24",
        "image": "/tg/assets/sec-bots.jpg",
        "mode": "trading",
        "industry": "expert-services",
        "one_liner": "Четыре готовых бота. Контроль рисков отдельно. Эксперимент: промпт без кода, оценка зашло / почти / мимо.",
        "vitrine_label": "Витрина ботов",
        "cta": "Промпт для эксперимента",
        "placeholder": "Золото, жду место, не догонять ход…",
        "legacy": ("strategies", "strategy", "стратегии"),
    },
    {
        "id": "craft",
        "title": "Конфиги для ремесла",
        "title_short": "Ремесло",
        "title_en": "Craft configs",
        "accent": "#67e8f9",
        "image": "/tg/assets/sec-craft.jpg",
        "mode": "craft",
        "industry": "expert-services",
        "one_liner": "Билдер конфига для ремесленника: заказ, материал, срок, цена, когда молчать.",
        "vitrine_label": "Витрина конфигов",
        "cta": "Собрать конфиг",
        "placeholder": "Кожаные ремни на заказ, материал жрёт маржу, сроки плывут…",
        "legacy": ("teammates", "teammate", "engine", "движок"),
    },
    {
        "id": "target",
        "title": "Таргет ИИ-агентов",
        "title_short": "Агенты",
        "title_en": "Agent targeting",
        "accent": "#c4b5fd",
        "image": "/tg/assets/sec-target.jpg",
        "mode": "agents",
        "industry": "ai-agencies",
        "one_liner": "Куда целиться агенту: кто платит, какой канал, какой текст, когда молчать.",
        "vitrine_label": "Витрина агентов",
        "cta": "Собрать таргет",
        "placeholder": "Агент для маленькой студии, ищем кто заказывает внедрение…",
        "legacy": ("agents", "agent", "агенты"),
    },
    {
        "id": "shop",
        "title": "Каталог магазина",
        "title_short": "Магазин",
        "title_en": "Shop catalog",
        "accent": "#fb7185",
        "image": "/tg/assets/sec-shop.jpg",
        "mode": "ecom",
        "industry": "ecommerce",
        "one_liner": "Уникальный каталог: название, описание, когда человеку это нужно.",
        "vitrine_label": "Витрина каталога",
        "cta": "Собрать карточку товара",
        "placeholder": "Физический товар, не понятно кому и в какой момент он нужен…",
        "legacy": ("artefacts", "making", "мейкинг", "посты", "posts"),
    },
]


def list_sections(*, lang: str = "ru") -> list[dict[str, Any]]:
    ru = (lang or "ru").startswith("ru")
    out = []
    for s in SECTIONS:
        row = dict(s)
        row["title"] = s["title"] if ru else s["title_en"]
        out.append(row)
    return out


def section_by_id(sid: str) -> dict[str, Any] | None:
    key = (sid or "").strip().lower()
    for s in SECTIONS:
        if s["id"] == key or key in (s.get("legacy") or ()):
            return s
    aliases = {
        "chain": "life",
        "in_out": "life",
        "life_ideas": "life",
        "trading": "bots",
        "bots": "bots",
        "craft": "craft",
        "teammates": "craft",
        "target": "target",
        "agents": "target",
        "shop": "shop",
        "ecom": "shop",
        "artefacts": "shop",
    }
    mapped = aliases.get(key)
    if mapped:
        return section_by_id(mapped)
    return None
