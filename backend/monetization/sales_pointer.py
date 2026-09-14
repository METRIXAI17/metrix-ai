"""Sales pointer from Auto Orders — plus and minus, one road. No syrup."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.core.coop.brief_normalizer import classify_order
from backend.core.coop.consult_patterns.flags import detect_flags
from backend.core.output_editor import banned_hits, edit_client_text

_PROMPT = Path(__file__).resolve().parents[1] / "core" / "prompts" / "sales_pointer.md"


def _levels(brief: str, order: str) -> list[dict[str, str]]:
    t = (brief or "").lower()
    has_n = any(ch.isdigit() for ch in t) or "заявк" in t
    return [
        {"level": "0", "diff": "есть ли одно число (заявки/нед или объём серии)", "hit": "yes" if has_n else "no"},
        {
            "level": "1",
            "diff": "пришло − дошло до разговора" if order != "TYPE_B" else "сделано − повторено",
        },
        {"level": "2", "diff": "кто обязан взять − кто взял" if order != "TYPE_B" else "замок есть − замок держат"},
        {"level": "3", "diff": "цена дыры vs цена контура"},
    ]


def build_pointer(brief: str, *, order_type: str | None = None) -> dict[str, Any]:
    order = order_type or classify_order(brief)
    flags = detect_flags(brief)
    if order == "TYPE_B":
        lines = [
            "Плюс: стиль можно замкнуть и повторять серию.",
            "Минус: один креатив без замка не даёт хвоста.",
            "Дорога: референс → style_lock → первый кусок → вопрос «повторяем в этом замке?»",
        ]
        obj = "Если просят совсем другое — это новый бриф, не тот же ретейнер."
    else:
        lines = [
            "Плюс: заявки уже есть, теряются без имени.",
            "Минус: мы не увеличим трафик. Дешёвый бот снаружи похож.",
            "Дорога: 5 вопросов → одна цифра потерь → пилот одного канала → отчёт → ретейнер на сдаче.",
        ]
        obj = "Возражение «за 30к сделают бота»: чат vs потеря с именем. Если нужен только чат — не брать нас."
    talk = edit_client_text("\n".join(lines + [obj]), order_type=order)
    return {
        "module": "SalesPointer",
        "mode": "auto_orders",
        "order_type": order,
        "talk": talk,
        "objection": obj,
        "levels_log": _levels(brief, order),
        "method_named_to_client": False,
        "flags": [f.get("id") for f in flags],
        "banned": banned_hits(talk),
        "prompt_ref": "backend/core/prompts/sales_pointer.md",
    }
