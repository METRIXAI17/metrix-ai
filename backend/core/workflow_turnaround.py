"""Free workflow turnaround. Part of design, not a brochure."""

from __future__ import annotations

from typing import Any


STEPS: list[dict[str, str]] = [
    {
        "id": "essence",
        "n": "01",
        "title_ru": "Суть",
        "title_en": "Essence",
        "do_ru": "Опиши вопрос.",
        "do_en": "Describe the question.",
    },
    {
        "id": "two_lines",
        "n": "02",
        "title_ru": "Две строки",
        "title_en": "Two lines",
        "do_ru": "Движок подсвечивает проблему и выдаёт способ решения.",
        "do_en": "The engine highlights the problem and returns a way to sit it.",
    },
    {
        "id": "questions",
        "n": "03",
        "title_ru": "5–10 вопросов",
        "title_en": "5–10 questions",
        "do_ru": "Настройки контекста. Своими словами: блоки, мысль, трудность.",
        "do_en": "Context settings. In your words: blocks, thought, friction.",
    },
    {
        "id": "vector",
        "n": "04",
        "title_ru": "Нужный вектор",
        "title_en": "The vector",
        "do_ru": "Сводка, куда сядет результат. Без эссе.",
        "do_en": "A summary of where the result will sit. No essay.",
    },
    {
        "id": "pay",
        "n": "05",
        "title_ru": "Посадка",
        "title_en": "Sit",
        "do_ru": "$490 — комбо рекурсивных решений и терминальная посадка процесса. Eval — после оплаты.",
        "do_en": "$490 — a combo of recursive solutions and a terminal process sit. Eval after pay.",
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
        "Выдаёт суть твоего вопроса и решение одной фразой. Потом несколько вопросов — сводка векторов."
        if ru
        else "Returns the essence of your question and a one-phrase sit. Then a few questions — a vector summary."
    )
    if contour:
        lead = (
            "Флагман сажает автономный контур в ваш проект. Плотнее спеки, тот же поток."
            if ru
            else "Flagship sits an autonomous contour on your project. Denser specs, same stream."
        )
    return {
        "module": "WorkflowTurnaround",
        "free": True,
        "lead": lead,
        "steps": steps,
        "kill": (
            "Eval открывается после оплаты. Не обещаем доход."
            if ru
            else "Eval opens after pay. No yield promise."
        ),
    }


def format_telegram(pack: dict[str, Any] | None = None, *, lang: str = "ru") -> str:
    p = pack or turnaround(lang=lang)
    lines = ["<b>Разворот</b>", p.get("lead") or "", ""]
    for s in p.get("steps") or []:
        lines.append(f"<code>{s['n']}</code> <b>{s['title']}</b> — {s['do']}")
    lines.append("")
    lines.append(p.get("kill") or "")
    return "\n".join(lines)
