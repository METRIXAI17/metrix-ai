"""Heavy Launch — three projects, four supporting layers, three public SKUs."""

from __future__ import annotations

from typing import Any

from backend.contours.spiritual import search as spirit_search

PROJECTS = [
    {
        "id": "finance",
        "title": "Финансы",
        "title_en": "Finance",
        "job_ru": "Рисуем показатели.",
        "job_en": "Draw the indicators.",
        "objects": ["monday_number", "leak", "cash_cycle", "ownerless_pct"],
    },
    {
        "id": "deeptech",
        "title": "Диптех",
        "title_en": "Deeptech",
        "job_ru": "Убираем переплату и гемор поддержки. Контур работает.",
        "job_en": "Cut overpay and support pain. The contour runs.",
        "objects": ["eval", "flight_recorder", "recursive_spec", "orientation"],
    },
    {
        "id": "brand",
        "title": "Бренд",
        "title_en": "Brand",
        "job_ru": "Мир, в который хотят зайти. Дверь и комнаты, не слоган.",
        "job_en": "A world people want to enter. Door and rooms, not a slogan.",
        "objects": ["door", "rooms", "stream", "void"],
    },
]

LAYERS = [
    {"id": "chips", "title": "Чипы", "job_ru": "Роботизируем процессы.", "key": "chips.robotize"},
    {"id": "markets", "title": "Маркеты", "job_ru": "Привлекаем в воронку.", "key": "markets.funnel"},
    {"id": "sales", "title": "Продажи", "job_ru": "Делаем решение купить лёгким.", "key": "sales.buy"},
    {"id": "value", "title": "Ценность", "job_ru": "Делаем всё для этого.", "key": "value.outcome"},
]

SKUS = {
    "access_month": {
        "sku": "access_month",
        "name": "Metrix Access",
        "price_rub": 3290,
        "period": "month",
        "includes": ["door", "store", "craftshift", "conversation", "eval"],
        "runs": 40,
        "eval": True,
        "not_included": ["signals", "main_without_pilot", "custom_spec"],
    },
    "custom_spec_pilot": {
        "sku": "custom_spec_pilot",
        "name": "Custom spec pilot",
        "price_rub": 45000,
        "period": "pilot",
        "includes": ["recursive_conclusions", "named_void", "gate", "acceptance"],
        "eval": True,
        "not_included": ["signals", "main_without_pilot"],
    },
    "cross_assist": {
        "sku": "cross_assist",
        "name": "Cross assist solution",
        "price_rub": 80000,
        "period": "solution",
        "includes": ["query_search", "assistant_pick", "packed_keys"],
        "eval": True,
        "not_included": ["signals", "yield_promise"],
    },
}


def assembly() -> dict[str, Any]:
    return {
        "name": "Heavy Launch",
        "projects": PROJECTS,
        "layers": LAYERS,
        "skus": list(SKUS.values()),
        "rule": "platform fully handles paid implementation",
        "not_a_catalog": True,
    }


def sku(code: str) -> dict[str, Any] | None:
    return SKUS.get(code)


KEYS: dict[str, dict[str, Any]] = {
    "finance.indicators": {
        "project": "finance",
        "object": "indicators",
        "offer": "access_month",
        "hint_ru": "Касса и понедельник. Не дашборд настроения.",
    },
    "deeptech.eval": {
        "project": "deeptech",
        "object": "eval",
        "offer": "access_month",
        "hint_ru": "Eval на Access. Четыре оси. Без 30%→100%.",
    },
    "deeptech.recursive": {
        "project": "deeptech",
        "object": "recursive_spec",
        "offer": "custom_spec_pilot",
        "hint_ru": "Рекурсивные выводы под капотом. 45 000 ₽.",
    },
    "brand.world": {
        "project": "brand",
        "object": "world",
        "offer": "access_month",
        "hint_ru": "Дверь и комнаты. Не экосистема.",
    },
    "chips.robotize": {
        "project": "chips",
        "object": "process",
        "offer": "custom_spec_pilot",
        "hint_ru": "Процесс в чипе: хозяин, SLA, эскалация.",
    },
    "markets.funnel": {
        "project": "markets",
        "object": "funnel",
        "offer": "cross_assist",
        "hint_ru": "Воронка из ключей, не из охватов.",
    },
    "sales.buy": {
        "project": "sales",
        "object": "buy",
        "offer": "access_month",
        "hint_ru": "Три цены. Что не входит — названо.",
    },
    "value.outcome": {
        "project": "value",
        "object": "outcome",
        "offer": "custom_spec_pilot",
        "hint_ru": "OutcomeContract до Stage 1.",
    },
}


def pack_keys(selected: list[str]) -> dict[str, Any]:
    packed = {}
    for k in selected:
        if k in KEYS:
            packed[k] = dict(KEYS[k])
    return {"keys": packed, "n": len(packed)}


def cross_search(query: str, limit: int = 6) -> dict[str, Any]:
    """Search proposed options with assistant. Pack into keys."""
    q = (query or "").lower()
    options = []
    for key, meta in KEYS.items():
        blob = f"{key} {meta['project']} {meta['object']} {meta['hint_ru']} {meta['offer']}"
        score = sum(1 for w in q.split() if w and w in blob.lower()) if q else 1
        if "финанс" in q or "касс" in q or "понедельник" in q:
            if meta["project"] == "finance":
                score += 2
        if "диптех" in q or "eval" in q or "поддерж" in q:
            if meta["project"] == "deeptech":
                score += 2
        if "бренд" in q or "мир" in q or "двер" in q:
            if meta["project"] == "brand":
                score += 2
        if "чип" in q or "робот" in q:
            if key.startswith("chips"):
                score += 2
        if "ворон" in q or "маркет" in q:
            if key.startswith("markets"):
                score += 2
        if "купи" in q or "цен" in q or "access" in q:
            if key.startswith("sales") or meta["offer"] == "access_month":
                score += 1
        if score:
            options.append({"key": key, "score": score, **meta})
    options.sort(key=lambda x: x["score"], reverse=True)
    options = options[:limit]
    spirit = spirit_search(query, limit=3)
    pick = options[0]["key"] if options else "value.outcome"
    packed = pack_keys([o["key"] for o in options[:3]])
    assistant = {
        "pick": pick,
        "reason_ru": (options[0]["hint_ru"] if options else "Слот ценности, пока запрос пустой."),
        "sku": KEYS.get(pick, {}).get("offer"),
        "note": "assistant ranks proposed options; does not invent a seventh product",
    }
    return {
        "query": query,
        "options": options,
        "assistant": assistant,
        "packed": packed,
        "spiritual": spirit["hits"],
        "skus": [SKUS[k] for k in ("access_month", "custom_spec_pilot", "cross_assist")],
    }
