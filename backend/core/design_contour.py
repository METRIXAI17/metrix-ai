"""$10k autonomous-contour design. Funding pack is internal; talk is design."""

from __future__ import annotations

from typing import Any

from backend.core.business_gen.funding_pack import build_funding_pack
from backend.core.workflow_turnaround import turnaround


# How Funding fails as a $10k design conversation — encoded so the engine does not repeat it.
FUNDING_GAPS = [
    {
        "id": "yield_pitch",
        "was": "income bands / auto-yield",
        "now": "не обещать доход; считать границы контура",
    },
    {
        "id": "new_line",
        "was": "partner pack as a new product",
        "now": "комнаты того же потока, не новая линейка",
    },
    {
        "id": "capital_first",
        "was": "placement slots before evidence",
        "now": "сначала хозяин, SLA, цифра понедельника",
    },
]


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def analyze(brief: str, *, lang: str = "ru", capital_usd: float | None = 10000) -> dict[str, Any]:
    """Internal funding map → public contour-design talk."""
    L = _lang(lang)
    pack = build_funding_pack(
        brief or "контур в существующий проект, без новой линейки",
        project_name="Contour",
        capital_usd=capital_usd,
        lang=L,
    )
    p1 = (pack.get("raw") or {}).get("structural") or {}
    p2 = (pack.get("raw") or {}).get("assets") or {}
    p3 = (pack.get("raw") or {}).get("capital_coop") or {}
    gate = (p3.get("readiness") or {}).get("gate") or "structure_first"

    questions = [
        _d(L, "Какие комнаты уже есть в проекте — не какую линейку открыть?", "Which rooms already exist — not which line to open?"),
        _d(L, "Кто хозяин понедельника?", "Who owns Monday?"),
        _d(L, "Где часы сгорают — на in или на out?", "Where do hours burn — in or out?"),
        _d(L, "Что уже работает и нельзя трогать?", "What already works and must not be touched?"),
        _d(L, "За какой unit уже платят?", "Which unit already gets paid?"),
        _d(L, "Где контур рвётся: статус, эскалация, отчёт?", "Where does the contour tear: status, escalate, report?"),
        _d(L, "Что не должно стать новой линейкой?", "What must not become a new product line?"),
        _d(L, "Какая библиотека уже в руках?", "Which library is already in hand?"),
        _d(L, "Какой нестандартный ход вы уже убили?", "Which unusual move did you already kill?"),
        _d(L, "Какой слот должен принять объект?", "Which slot must receive the object?"),
        _d(L, "Сколько минут на статус, пока не эскалация?", "Minutes for status before escalate?"),
        _d(L, "Какая цифра понедельника станет фактом?", "Which Monday number becomes a fact?"),
    ]
    # Translate funding pillars into design levers (never yield).
    levers = [
        {
            "id": "structural",
            "from_funding": "p1_structural",
            "ask": _d(L, "Что уже платит без новой комнаты?", "What already pays without a new room?"),
            "internal": (p1.get("thesis") or "")[:180],
        },
        {
            "id": "attach",
            "from_funding": "p2_assets",
            "ask": _d(L, "Что садится 1:1 на продажу, которая уже есть?", "What sits 1:1 on a sale that already happens?"),
            "internal": (p2.get("thesis") or "")[:180],
        },
        {
            "id": "loop",
            "from_funding": "p3_coop",
            "ask": _d(L, "Где петля партнёра, если evidence уже есть — и где её нельзя делать SKU?", "Where is a partner loop once evidence exists — and where it must not become a SKU?"),
            "internal": ((p3.get("readiness") or {}).get("message") or "")[:180],
            "gate": gate,
        },
    ]
    return {
        "module": "DesignContour",
        "sku": "sku_10000",
        "usd": 10000,
        "lang": L,
        "lead": _d(
            L,
            "Автономный контур в ваш проект. Плотнее спеки, тот же поток. Комнаты, не новая линейка.",
            "Autonomous contour on your project. Denser specs, same stream. Rooms, not a new product line.",
        ),
        "kill": _d(
            L,
            "Не авто-доход. Не новая линейка. Funding-столпы — внутренняя карта, не оффер.",
            "No auto-yield. No new product line. Funding pillars are an internal map, not the offer.",
        ),
        "funding_gaps": FUNDING_GAPS,
        "levers": levers,
        "questions": questions,
        "workflow": turnaround(lang=L, contour=True),
        "gate": gate,
        "promise": _d(
            L,
            "После оплаты — файл: рекурсивная методика + спеки + надстройка того же движка, посаженная на ваш контур.",
            "After pay — file: recursive methodology + specs + same-engine overlay, sat on your contour.",
        ),
    }


def format_telegram(pack: dict[str, Any]) -> str:
    lines = [
        f"<b>$10 000 · контур</b>",
        pack.get("lead") or "",
        "",
        pack.get("kill") or "",
        "",
    ]
    for i, q in enumerate((pack.get("questions") or [])[:4], 1):
        lines.append(f"{i}. {q}")
    lines.append("")
    lines.append(pack.get("promise") or "")
    return "\n".join(lines)
