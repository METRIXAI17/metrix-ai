"""Mini App catalog: demo highway, strategies, agents. Human names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR
from backend.core.agent_studio import list_niches
from backend.core.product_180 import catalog_overlay
from backend.core.sales_offer import access_offer
from backend.core.sales_modes import list_sections
from backend.core.teammates import list_teammates, workflow_payload
from backend.core.functions import FUNCTIONS
from backend.core.strategies import list_strategies
from backend.core.x_posts import HANDLE, X_URL
from backend.monetization.tg_scheme import SKUS, scheme_payload


HITS_PATH = DATA_DIR / "miniapp" / "hits.json"

FLAGSHIPS = [
    {
        "id": "in_out_chain",
        "section": "chain",
        "title_ru": "In-Out Chain",
        "title_en": "In-Out Chain",
        "sticker": "Chain",
        "accent": "#5eead4",
        "sku": "access_month",
        "essence_ru": "Снимает рутину, закрывает решённое и нерешённое, режет стоимость in и out.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "target_place",
        "section": "chain",
        "title_ru": "Target Place · золото",
        "title_en": "Target Place · gold",
        "sticker": "Gold",
        "accent": "#fbbf24",
        "sku": "access_month",
        "essence_ru": "Вход и выход — места. Между местами воздух. Код модели, не сигнал.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "demand",
        "section": "chain",
        "title_ru": "Demand · крипта",
        "title_en": "Demand · crypto",
        "sticker": "Cryp",
        "accent": "#c4b5fd",
        "sku": "access_month",
        "essence_ru": "Сначала окно спроса, потом имя. Местные истории, короткий выстрел.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "ampli",
        "section": "chain",
        "title_ru": "Ampli · Америка",
        "title_en": "Ampli · US",
        "sticker": "US",
        "accent": "#38bdf8",
        "sku": "access_month",
        "essence_ru": "Сборщик амплитуды. Направление не угадывает.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "two_leg_tape",
        "section": "chain",
        "title_ru": "Two-Leg Tape · Tape Land",
        "title_en": "Two-Leg Tape · Tape Land",
        "sticker": "Tape",
        "accent": "#67e8f9",
        "sku": "access_month",
        "essence_ru": "Внимание обгоняет цену, деньги подтверждают. Плечо не рекомендуется.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "risk_engine",
        "section": "chain",
        "title_ru": "Контроль рисков",
        "title_en": "Risk control",
        "sticker": "Risk",
        "accent": "#fb7185",
        "sku": "access_month",
        "essence_ru": "Контроль рисков: R — мера исхода, плечо — размер. Без стопа нет размера.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "agent_studio",
        "section": "teammates",
        "title_ru": "AI Teammates",
        "title_en": "AI Teammates",
        "sticker": "Team",
        "accent": "#67e8f9",
        "sku": "custom_teammate",
        "essence_ru": "IT Desk и Production Geometry. Конфиг на заказ. Edu/ecom выключены.",
        "cta": "teammates",
        "flagship": True,
    },
    {
        "id": "stop_on_shift",
        "section": "chain",
        "title_ru": "Стоп на перемене",
        "title_en": "Stop on shift",
        "sticker": "Stop",
        "accent": "#fb7185",
        "sku": "access_month",
        "essence_ru": "Факт против тезиса стратегии. Бюджет не сливать. Живая проверка не списывает Access.",
        "cta": "chain",
        "flagship": True,
    },
    {
        "id": "thesis_order",
        "section": "artefacts",
        "title_ru": "Тезисы на заказ",
        "title_en": "Theses on order",
        "sticker": "Thesis",
        "accent": "#c4b5fd",
        "sku": "access_month",
        "essence_ru": "Продаём только тезисы. Короткое утверждение про процесс, которое можно убить фактом.",
        "cta": "artefacts",
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
            {
                "id": s["id"],
                "title": s["title"],
                "short": s["title_short"],
                "image": s["image"],
                "one_liner": s["one_liner"],
                "accent": s["accent"],
            }
            for s in list_sections(lang=lang)
        ],
        "sections": list_sections(lang=lang),
        "functions": fns,
        "flagships": flagships,
        "strategies": list_strategies(),
        "niches": list_niches(),
        "teammates": list_teammates(),
        "workflow": workflow_payload(),
        "product": catalog_overlay(),
        "promo": [],
        "hits": hit_board,
        "terminal": {
            "id": "terminal_mine",
            "title": "Журнал решений",
            "price": _price_of("terminal_mine"),
        },
        "scheme": scheme_payload(),
        "promise": (
            "Идеи для жизни · Торговые боты · Конфиги для ремесла · Таргет ИИ-агентов · Каталог магазина. "
            "Access 3 290 ₽. Код модели, не сигналы."
        ),
        "sales": access_offer(lang=lang),
    }
