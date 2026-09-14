"""Support after handoff: TYPE_A stabilize, TYPE_B repeat in style_lock."""

from __future__ import annotations

from typing import Any

MONDAY_TEMPLATE = {
    "title": "Отчёт понедельника",
    "fields": ["пришло", "взяли_вовремя", "сгорело", "на_ком", "комментарий"],
    "empty_rule": "контур не ведут",
    "hours": "4–8 часов правок в месяц",
    "channel": "один канал коммуникации",
    "content": "разбор ИХ цифр за неделю, не блог про ИИ",
}

TYPE_B_CTA = "следующий в этом же замке — тема X или Y?"


def support_offer(order_type: str, *, numbers_empty: bool = False, style_lock: dict | None = None) -> dict[str, Any]:
    if order_type == "TYPE_B":
        return {
            "kind": "series_repeat",
            "style_lock": dict(style_lock or {}),
            "cta": TYPE_B_CTA,
            "rule": "не предлагать сменить жанр; совсем другое = новый бриф",
        }
    note = MONDAY_TEMPLATE["empty_rule"] if numbers_empty else "цифры из контура"
    return {
        "kind": "stabilize",
        "monday": MONDAY_TEMPLATE,
        "note": note,
        "offer": "подписка на отчёт + 4–8 часов + один канал",
        "sold_at": "handover",
    }
