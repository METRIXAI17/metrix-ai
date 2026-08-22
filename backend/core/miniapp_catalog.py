"""Mini App catalog: flagships, promo SKUs, functions, hits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR
from backend.core.functions import FUNCTIONS
from backend.monetization.tg_scheme import SKUS, scheme_payload


HITS_PATH = DATA_DIR / "miniapp" / "hits.json"

FLAGSHIPS = [
    {
        "id": "request_work",
        "section": "работа по запросу",
        "title_ru": "Работа по запросу",
        "title_en": "Work by request",
        "sticker": "QA",
        "accent": "#5eead4",
        "sku": "request_deep",
        "essence_ru": "Сложный запрос-ответ. Читалка → сборка → авто-режим.",
        "cta": "request",
        "flagship": True,
    },
    {
        "id": "flagship_metric",
        "section": "флагманские карточки",
        "title_ru": "Metric engine",
        "title_en": "Metric engine",
        "sticker": "MX",
        "accent": "#38bdf8",
        "sku": "flagship_metric",
        "essence_ru": "Quality-first. Поднимает значения, не отвечает на вопрос.",
        "cta": "flagships",
        "flagship": True,
    },
    {
        "id": "flagship_reader",
        "section": "флагманские карточки",
        "title_ru": "Task reader",
        "title_en": "Task reader",
        "sticker": "RD",
        "accent": "#a78bfa",
        "sku": "flagship_reader",
        "essence_ru": "Несколько концов считывания. Без предвзятого collapse.",
        "cta": "request",
        "flagship": True,
    },
    {
        "id": "core",
        "section": "флагманские карточки",
        "title_ru": "Ядро Growth / Yield",
        "title_en": "Growth / Yield core",
        "sticker": "Core",
        "accent": "#5eead4",
        "sku": "flagship_core",
        "essence_ru": "Идентичность + активы в панели.",
        "cta": "flagships",
        "flagship": True,
    },
    {
        "id": "coop",
        "section": "флагманские карточки",
        "title_ru": "Пакеты клиентов",
        "title_en": "Client packs",
        "sticker": "Coop",
        "accent": "#67e8f9",
        "sku": "flagship_coop",
        "essence_ru": "Конфиг под похожие запросы.",
        "cta": "request",
        "flagship": True,
    },
    {
        "id": "assist",
        "section": "флагманские карточки",
        "title_ru": "Внедрение + тест",
        "title_en": "Implement + test",
        "sticker": "Assist",
        "accent": "#fbbf24",
        "sku": "flagship_assist",
        "essence_ru": "Ассистент раскатки после одного шага.",
        "cta": "later",
        "flagship": True,
    },
]

PROMO_SKUS = [
    {
        "id": "promo_cards",
        "title_ru": "Карточки описаний",
        "essence_ru": "Массовый бизнес-билдер: описания оффера.",
        "sku": "promo_cards",
    },
    {
        "id": "promo_reels",
        "title_ru": "Идеи для роликов",
        "essence_ru": "Крючки, 12с структура, без воды.",
        "sku": "promo_reels",
    },
    {
        "id": "promo_prompts",
        "title_ru": "Промпты для консалтинга",
        "essence_ru": "Готовые промпты под сессию, не generic GPT.",
        "sku": "promo_prompts",
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
        "request_work": 48,
        "creative_assistant": 31,
        "promo_cards": 27,
        "solution_logger": 22,
        "digital_mockup": 19,
        "flagship_metric": 17,
        "terminal_mine": 11,
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
        out = {**row, "title": title, "price": _price_of(row.get("sku") or "")}
        return out

    flagships = [titled(f) for f in FLAGSHIPS]
    promo = [titled(p) for p in PROMO_SKUS]
    fns = []
    for f in FUNCTIONS:
        fns.append(
            {
                **f,
                "title": f["title_ru"] if ru else f["title_en"],
                "blurb": f.get("blurb_ru") if ru else f.get("blurb_ru"),
                "price": _price_of(
                    {"creative_assistant": "fn_creative", "solution_logger": "fn_logger", "digital_mockup": "fn_mockup"}[
                        f["id"]
                    ]
                ),
                "hits": hits.get(f["id"], 0),
            }
        )
    hit_board = sorted(
        [{"id": k, "hits": v} for k, v in hits.items()],
        key=lambda x: -x["hits"],
    )[:8]
    return {
        "brand": "Metrix AI",
        "app": "Metrix AI Bot",
        "nav": [
            {"id": "home", "title": "Главная"},
            {"id": "request", "title": "Работа по запросу"},
            {"id": "flagships", "title": "Флагманские карточки"},
            {"id": "promo", "title": "Промо"},
            {"id": "terminal", "title": "Терминал"},
        ],
        "functions": fns,
        "flagships": flagships,
        "promo": promo,
        "hits": hit_board,
        "terminal": {
            "id": "terminal_mine",
            "title": "Путь к ордерам / майнинг",
            "price": _price_of("terminal_mine"),
        },
        "scheme": scheme_payload(),
    }
