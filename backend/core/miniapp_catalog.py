"""Mini App catalog: demo highway, strategies, agents. Human names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR
from backend.core.agent_studio import list_niches
from backend.core.functions import FUNCTIONS
from backend.core.strategies import list_strategies
from backend.core.x_posts import HANDLE, X_URL
from backend.monetization.tg_scheme import SKUS, scheme_payload


HITS_PATH = DATA_DIR / "miniapp" / "hits.json"

FLAGSHIPS = [
    {
        "id": "landing_studio",
        "section": "лендинг",
        "title_ru": "Видение события",
        "title_en": "Event vision",
        "sticker": "Room",
        "accent": "#5eead4",
        "sku": "request_orient",
        "essence_ru": "Не кнопка. Комната. Входите в событие — абстракция, потом карточки.",
        "cta": "landing",
        "flagship": True,
    },
    {
        "id": "demo_highway",
        "section": "лендинг",
        "title_ru": "Демо-артефакт",
        "title_en": "Demo artifact",
        "sticker": "Demo",
        "accent": "#67e8f9",
        "sku": "request_orient",
        "essence_ru": "Ситуация своими словами → один артефакт. Если зайдёт — это товар.",
        "cta": "landing",
        "flagship": True,
    },
    {
        "id": "target_place",
        "section": "движок",
        "title_ru": "Target Place · золото",
        "title_en": "Target Place · gold",
        "sticker": "Gold",
        "accent": "#fbbf24",
        "sku": "request_deep",
        "essence_ru": "Вход и выход — места. Между местами воздух.",
        "cta": "engine",
        "flagship": True,
    },
    {
        "id": "demand",
        "section": "движок",
        "title_ru": "Demand · крипта",
        "title_en": "Demand · crypto",
        "sticker": "Cryp",
        "accent": "#c4b5fd",
        "sku": "request_deep",
        "essence_ru": "Сначала окно спроса, потом имя. Местные истории, короткий выстрел.",
        "cta": "engine",
        "flagship": True,
    },
    {
        "id": "ampli",
        "section": "движок",
        "title_ru": "Ampli · Америка",
        "title_en": "Ampli · US",
        "sticker": "US",
        "accent": "#38bdf8",
        "sku": "request_deep",
        "essence_ru": "Сборщик амплитуды. Направление не угадывает.",
        "cta": "engine",
        "flagship": True,
    },
    {
        "id": "comfort_studio",
        "section": "движок",
        "title_ru": "Тихий ассистент",
        "title_en": "Quiet assistant",
        "sticker": "Quiet",
        "accent": "#c4b5fd",
        "sku": "request_deep",
        "essence_ru": "Идеи и точки роста. Без подъёма пульса. Верхний модуль движка.",
        "cta": "engine",
        "flagship": True,
    },
    {
        "id": "agent_studio",
        "section": "движок",
        "title_ru": "Собрать агента",
        "title_en": "Build an agent",
        "sticker": "Agent",
        "accent": "#67e8f9",
        "sku": "pilot_14",
        "essence_ru": "Агент с финмоделью: SaaS, агентства, школы, e-com.",
        "cta": "engine",
        "flagship": True,
    },
    {
        "id": "making_chamber",
        "section": "мейкинг",
        "title_ru": "Камера сборки",
        "title_en": "Making chamber",
        "sticker": "Make",
        "accent": "#fbbf24",
        "sku": "pilot_14",
        "essence_ru": "Неделя, которую можно прожить: событие, прогрев, страх, share, сателлит.",
        "cta": "making",
        "flagship": True,
    },
    {
        "id": "implement",
        "section": "мейкинг",
        "title_ru": "Посадка в проект",
        "title_en": "Land it",
        "sticker": "Pilot",
        "accent": "#f59e0b",
        "sku": "pilot_14",
        "essence_ru": "14 дней: внедряем тот артефакт, который уже зашёл. Share, не ретейнер.",
        "cta": "making",
        "flagship": True,
    },
]


def _price_of(sku: str) -> dict[str, Any]:
    row = SKUS.get(sku) or {}
    return {
        "sku": sku,
        "rub": row.get("rub"),
        "usd": row.get("usd"),
        "stars": row.get("stars"),
        "tier": row.get("tier"),
    }


def _load_hits() -> dict[str, int]:
    if HITS_PATH.exists():
        try:
            return {str(k): int(v) for k, v in json.loads(HITS_PATH.read_text("utf-8")).items()}
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return {}
    return {
        "demo_highway": 12,
        "target_place": 9,
        "demand": 7,
        "ampli": 6,
        "agent_studio": 11,
        "creative_assistant": 4,
    }


def bump_hit(item_id: str) -> dict[str, int]:
    hits = _load_hits()
    hits[item_id] = int(hits.get(item_id) or 0) + 1
    HITS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HITS_PATH.write_text(json.dumps(hits, ensure_ascii=False, indent=2), encoding="utf-8")
    return hits


def catalog_payload(lang: str = "ru") -> dict[str, Any]:
    hits = _load_hits()
    ru = (lang or "ru").startswith("ru")

    def titled(row: dict[str, Any]) -> dict[str, Any]:
        title = row.get("title_ru") if ru else row.get("title_en") or row.get("title_ru")
        return {**row, "title": title, "price": _price_of(row.get("sku") or "")}

    flagships = [titled(f) for f in FLAGSHIPS]
    fns = []
    sku_map = {
        "creative_assistant": "fn_creative",
        "solution_logger": "fn_logger",
        "digital_mockup": "fn_mockup",
    }
    for f in FUNCTIONS:
        fns.append(
            {
                **f,
                "title": f["title_ru"] if ru else f["title_en"],
                "blurb": f.get("blurb_ru"),
                "price": _price_of(sku_map.get(f["id"], "")),
                "hits": hits.get(f["id"], 0),
            }
        )
    hit_board = sorted(
        [{"id": k, "hits": v} for k, v in hits.items()],
        key=lambda x: -x["hits"],
    )[:8]
    return {
        "brand": "Metrix AI",
        "person": "Карим",
        "handle": HANDLE,
        "x": X_URL,
        "app": "Karim Metrix",
        "nav": [
            {"id": "landing", "title": "Лендинг"},
            {"id": "engine", "title": "Движок"},
            {"id": "making", "title": "Мейкинг"},
        ],
        "functions": fns,
        "flagships": flagships,
        "strategies": list_strategies(),
        "niches": list_niches(),
        "promo": [],
        "hits": hit_board,
        "terminal": {
            "id": "terminal_mine",
            "title": "Журнал решений",
            "price": _price_of("terminal_mine"),
        },
        "scheme": scheme_payload(),
        "promise": "Лендинг (событие) → движок (тихий) → мейкинг (неделя). Если зашло — share. Не сигналы.",
    }
