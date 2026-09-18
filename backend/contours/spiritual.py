"""Spiritual library — attention, void, calm, meaning.

Not natal. Not horoscope. Ontology of load and empty slots.
"""

from __future__ import annotations

from typing import Any

ENTRIES: list[dict[str, Any]] = [
    {
        "id": "sp_attention_as_capital",
        "title": "Внимание как капитал",
        "body": "Внимание тратится. Если слот не назван, внимание уходит в шум. Касса считает то, что названо.",
        "apply": "finance.indicators",
        "not": "не манифест изобилия",
    },
    {
        "id": "sp_void_is_slot",
        "title": "Пустота — слот, не мистика",
        "body": "Void — незакрытый слот: хозяин, цифра, приёмка. Не «энергия вселенной».",
        "apply": "value.outcome",
        "not": "не гороскоп, не natal",
    },
    {
        "id": "sp_calm_point",
        "title": "Точка спокойствия",
        "body": "Спокойствие — когда контур ведут. Пустые цифры понедельника — не покой, а дыра.",
        "apply": "finance.indicators",
        "not": "не медитация как продукт",
    },
    {
        "id": "sp_assembly_not_heat",
        "title": "Сборка ≠ тепло",
        "body": "Тёплый текст не закрывает сборку. Сначала сходимость условий, потом тон.",
        "apply": "brand.world",
        "not": "не cheerleader",
    },
    {
        "id": "sp_world_to_enter",
        "title": "Мир, в который хотят зайти",
        "body": "Бренд — дверь и комнаты одного потока. Не экосистема решений и не next-gen платформа.",
        "apply": "brand.world",
        "not": "не AI-powered unlock",
    },
    {
        "id": "sp_load_gate",
        "title": "Ворота нагрузки",
        "body": "Ночной mute, потолок дня, один выход. Духовное здесь = не сжечь носителя контура.",
        "apply": "chips.robotize",
        "not": "не медицинский совет",
    },
    {
        "id": "sp_named_owner",
        "title": "Имя на слабом звене",
        "body": "Пока нет имени, поток врёт. Дух проекта — ответственность, не атмосфера.",
        "apply": "sales.buy",
        "not": "не тимбилдинг",
    },
    {
        "id": "sp_silence_between",
        "title": "Воздух между местами",
        "body": "Между магнитом и origin — воздух. Не торговать воздух. Не продавать воздух.",
        "apply": "markets.funnel",
        "not": "не сигнал",
    },
]


def catalog() -> dict[str, Any]:
    return {
        "name": "Spiritual library",
        "disclaimer": "ontology of attention and empty slots — not natal, not horoscope, not therapy",
        "n": len(ENTRIES),
        "entries": ENTRIES,
    }


def search(query: str, limit: int = 6) -> dict[str, Any]:
    q = (query or "").lower()
    hits = []
    for e in ENTRIES:
        blob = f"{e['id']} {e['title']} {e['body']} {e['apply']}".lower()
        score = sum(1 for w in q.split() if w and w in blob) if q else 1
        if score:
            hits.append({**e, "score": score})
    hits.sort(key=lambda x: x["score"], reverse=True)
    return {"query": query, "hits": hits[:limit]}
