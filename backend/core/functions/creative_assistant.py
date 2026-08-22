"""Creative assistant — function 1 of the Mini App."""

from __future__ import annotations

from typing import Any

from backend.core.task_reader import assemble_query


ANGLES = (
    "constraint inversion — make the limit the signature",
    "one object, three tempos",
    "silent demo: the work explains itself without a caption",
    "borrow a craft rule, not an aesthetic",
    "negative space as the product",
)


def run_creative_assistant(
    brief: str,
    *,
    lang: str = "ru",
    kind: str = "ideas",
) -> dict[str, Any]:
    packed = assemble_query(brief, lang=lang, surface_hint="creative_assist")
    text = (brief or "").strip()
    stem = text[:80] or "untitled"
    ideas = [
        {
            "id": f"c{i+1}",
            "angle": ANGLES[i % len(ANGLES)],
            "line": f"{stem} → {ANGLES[i % len(ANGLES)]}",
        }
        for i in range(5)
    ]
    prompts = [
        f"Снять 12с: объект из брифа крупно, без лица, один жест, текст не читать.",
        f"Карточка: заголовок = ограничение, подзаголовок = что снимает Metrix.",
        f"Консалтинг-промпт: «разложи бриф на 3 конца считывания, не выбирай лучший».",
    ]
    return {
        "module": "Creative Assistant",
        "function": "creative_assistant",
        "kind": kind,
        "ideas": ideas,
        "prompts": prompts,
        "reel_hooks": [
            "Не идея. Правило, которое видно за 3 секунды.",
            "Сначала ограничение, потом картинка.",
            "Покажите процесс, спрячьте объяснение.",
        ],
        "assembly": packed,
        "summary": packed.get("summary"),
    }
