"""Financial-construction hits. Not a signal assistant."""

from __future__ import annotations

from pathlib import Path

HITS: list[dict[str, str]] = [
    {
        "id": "spread_desk",
        "title": "Спред как плата за нетерпение",
        "body": (
            "Кто держит запас, живёт на разнице входа и выхода — не на «росте рынка».\n"
            "На объёме спред кажется копейками. На марже это доля оборота.\n"
            "Тупик: считать спред комиссией и не смотреть, сколько часов ты реально держишь.\n"
            "Не рекомендация сделки."
        ),
    },
    {
        "id": "venture_option",
        "title": "Венчур как допуск, не как ставка",
        "body": (
            "Чек — это право быть в следующем круге. Не заголовок раунда.\n"
            "Кто не в бумаге — не в потоке, сколько бы ни читал имя сделки.\n"
            "Тупик: копировать название раунда и звать это инвестицией.\n"
            "Не рекомендация сделки."
        ),
    },
    {
        "id": "innovatika_loop",
        "title": "Инноватика как журнал, не секрет",
        "body": (
            "Платят за то, что отказ записан. Не за тайную стратегию.\n"
            "Живой контур появляется, когда убитая гипотеза дешевле нового ложного старта.\n"
            "Тупик: купить секрет вместо журнала.\n"
            "Не рекомендация сделки."
        ),
    },
]

_TEMPLATE = Path(__file__).resolve().parent / "hit_template.md"
STICKER = Path(__file__).resolve().parent / "hit-sticker.jpg"


def format_hit(hit: dict[str, str]) -> str:
    title = hit.get("title") or "Конструкция"
    body = hit.get("body") or ""
    return (
        "<b>Хиты — не сигнальный ассистент</b>\n"
        "Мувики, которые заслужили данные. 🎞\n\n"
        f"<b>{title}</b>\n\n{body}"
    )


def weekly_hit(week_index: int = 0) -> dict[str, str]:
    return HITS[int(week_index) % len(HITS)]


def glossary() -> str:
    return (
        "<b>Коротко</b>\n"
        "Поток — кто платит кому.\n"
        "Допуск — право быть внутри, не название.\n"
        "Хит — мувик конструкции. Не сигнал."
    )
