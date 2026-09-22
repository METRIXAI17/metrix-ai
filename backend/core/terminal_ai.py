"""Line 7 — Terminal AI on agent placements in money flows.

An agent is a seat, not a chat. Seat lives on a cash path:
  who pays → when money moves → when the agent speaks → when it stays silent.
"""

from __future__ import annotations

from typing import Any

from backend.core.resonance import new_id, remember
from backend.core.voice import DISCLAIMER, clip, first_sentence


def place(brief: str) -> dict[str, Any]:
    text = (brief or "").strip() or "поток без места для агента"
    sit = first_sentence(text, "поток")
    low = text.lower()
    if any(w in low for w in ("чип", "rtl", "fpga", "прошив")):
        seat = "узел телеметрии → kill на перегреве критической функции"
        pay = "B2B node fee, не слайд SaaS"
    elif any(w in low for w in ("пост", "x.com", "видео", "контент")):
        seat = "после кадра, до публикации — агент держит голос и kill"
        pay = "unit = один пост / один ролик"
    else:
        seat = "на входе денег, не в FAQ"
        pay = "доля с закрытой сделки, не подписка «на всякий случай»"
    art = {
        "id": new_id(),
        "kind": "line.terminal",
        "lane": "placements",
        "line": 7,
        "title": "Терминальный ИИ",
        "break": f"«{clip(sit, 80)}» не имеет места, где агент имеет право действовать.",
        "move": "Посадка: одно место в потоке, одно молчание, один kill.",
        "steps": [
            f"Место: {seat}.",
            f"Деньги: {pay}.",
            "Молчание: агент не пишет, пока слот не его.",
            "Kill: 14 дней без движения денег — вынуть агента.",
            "A2A: навигатор (линия 1) передаёт скринер → терминал сажает.",
        ],
        "seat": {
            "where": seat,
            "pay": pay,
            "silence": "пока слот не его",
            "kill": "14 дней без движения денег",
        },
        "artifact_week": "Карточка посадки: место · платёж · молчание · kill.",
        "anti": ["Не делать чат «помощник основателя».", "Не обещать доходность потока."],
        "disclaimer": DISCLAIMER,
        "wow": "Агент — стул в ваших деньгах. Не собеседник и не бизнес для чужих клиентов.",
        "meta": {"engine": "metrix_ai", "a2a": True},
    }
    remember(art)
    return art
