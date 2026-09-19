"""Free workflow turnaround. Part of design, not a brochure."""

from __future__ import annotations

from typing import Any


STEPS: list[dict[str, str]] = [
    {
        "id": "two_lines",
        "n": "01",
        "title_ru": "Две строки",
        "title_en": "Two lines",
        "do_ru": "Суть и желаемая посадка. Не эссе.",
        "do_en": "Essence and the slot it should sit in. Not an essay.",
    },
    {
        "id": "phrases",
        "n": "02",
        "title_ru": "Две фразы назад",
        "title_en": "Two phrases back",
        "do_ru": "Движок возвращает суть одной фразой и решение одной фразой.",
        "do_en": "Engine returns the problem in one phrase and the solution in one phrase.",
    },
    {
        "id": "questions",
        "n": "03",
        "title_ru": "5–20 вопросов",
        "title_en": "5–20 questions",
        "do_ru": "Простые настройки. Кастом, не допрос.",
        "do_en": "Simple settings. Custom, not an interrogation.",
    },
    {
        "id": "eval",
        "n": "04",
        "title_ru": "Eval",
        "title_en": "Eval",
        "do_ru": "Насколько реально можем помочь. Без 100%.",
        "do_en": "How much we can actually help. Never a fake 100%.",
    },
    {
        "id": "ticker",
        "n": "05",
        "title_ru": "Тикер",
        "title_en": "Ticker",
        "do_ru": "Объект получает имя в системе. Цепочка пишется в файл.",
        "do_en": "The object gets a name in the system. The chain is written to a file.",
    },
    {
        "id": "pay",
        "n": "06",
        "title_ru": "Оплата",
        "title_en": "Pay",
        "do_ru": "$100 — 120 запросов, без файла. $490 / $1000 / $10 000 — файл.",
        "do_en": "$100 — 120 requests, no file. $490 / $1000 / $10k — file.",
    },
    {
        "id": "file",
        "n": "07",
        "title_ru": "Файл",
        "title_en": "File",
        "do_ru": "Рекурсивная методика + спеки, переведённые в кодовую надстройку того же движка.",
        "do_en": "Recursive methodology + specs, translated into a code overlay of the same engine.",
    },
]


def turnaround(*, lang: str = "ru", contour: bool = False) -> dict[str, Any]:
    ru = (lang or "ru").startswith("ru")
    steps = []
    for s in STEPS:
        steps.append(
            {
                "id": s["id"],
                "n": s["n"],
                "title": s["title_ru"] if ru else s["title_en"],
                "do": s["do_ru"] if ru else s["do_en"],
            }
        )
    lead = (
        "Разворот, как сядет дизайн. Бесплатно. Комнаты, не новая линейка."
        if ru
        else "How the design will sit. Free. Rooms, not a new product line."
    )
    if contour:
        lead = (
            "Автономный контур в ваш проект: сначала этот разворот, потом две строки, потом спеки."
            if ru
            else "Autonomous contour on your project: this turnaround first, then two lines, then specs."
        )
    return {
        "module": "WorkflowTurnaround",
        "free": True,
        "lead": lead,
        "steps": steps,
        "kill": (
            "Не обещаем доход. Не открываем новую линейку."
            if ru
            else "No yield promise. No new product line."
        ),
    }


def format_telegram(pack: dict[str, Any] | None = None, *, lang: str = "ru") -> str:
    p = pack or turnaround(lang=lang)
    lines = [f"<b>Разворот</b>", p.get("lead") or "", ""]
    for s in p.get("steps") or []:
        lines.append(f"<code>{s['n']}</code> <b>{s['title']}</b> — {s['do']}")
    lines.append("")
    lines.append(p.get("kill") or "")
    return "\n".join(lines)
