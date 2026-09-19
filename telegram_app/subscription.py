"""Bot learning subscription: free hit / paid construction / private room rules."""

from __future__ import annotations

from typing import Any

TIERS = {
    "free": {
        "id": "free",
        "gets": "хиты смотреть бесплатно + глоссарий",
        "rule": "без сигналов, без чужих депозитов",
    },
    "paid": {
        "id": "paid",
        "gets": "разбор одной конструкции глубже + задание «соберите числа своей кассы»",
        "homework": "Соберите числа своей кассы: пришло / дошло / сгорело за неделю.",
    },
    "private": {
        "id": "private",
        "gets": "обсуждение тем: инжиниринг, рынок, венчур, инноватика",
        "rules": [
            "без сигналов на вход",
            "без чужих депозитов",
            "без гарантии доходности",
            "модерация: тикер как факт инсайда — удаление",
        ],
    },
}


def describe(tier: str = "free") -> dict[str, Any]:
    return dict(TIERS.get(tier) or TIERS["free"])


def format_tier(tier: str = "free") -> str:
    t = describe(tier)
    if tier == "private":
        rules = "\n".join(f"· {r}" for r in t.get("rules") or [])
        return f"<b>Приватка</b>\n{t['gets']}\n{rules}"
    if tier == "paid":
        return f"<b>Paid</b>\n{t['gets']}\nЗадание: {t.get('homework')}"
    return f"<b>Бесплатно</b>\n{t['gets']}\n{t.get('rule')}"
