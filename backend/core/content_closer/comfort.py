"""Quiet assistant — top module of the Engine section.

Looks like an AI companion, not a generator. Comfortable, calming.
Finds ideas and growth points without raising the pulse.

Never: innovation, breakthrough, 10x, scale, ROI guarantee.
Always: sit, name what already moves, put one object on the table.
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.core.content_closer.archetypes import pick_archetypes, score_vectors

HYPE = (
    "инновац",
    "прорыв",
    "масштабир",
    "10x",
    "гарант",
    "взлетим",
    "ракет",
    "синерг",
    "disrupt",
    "unlock your",
    "game-chang",
)


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:10], 16)


def _hype_hit(text: str) -> bool:
    t = (text or "").lower()
    return any(w in t for w in HYPE)


def _dehype(text: str) -> str:
    out = text or ""
    for w in HYPE:
        out = out.replace(w, "движение")
        out = out.replace(w.capitalize(), "движение")
        out = out.replace(w.upper(), "движение")
    return out


def comfort_turn(
    message: str,
    *,
    history: list[dict[str, str]] | None = None,
    closer: dict[str, Any] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """One sitting turn. At most two objects: a growth point and an idea."""
    ru = not (lang or "").lower().startswith("en")
    text = (message or "").strip()
    vec = (closer or {}).get("vectors") or score_vectors(text)
    arch = (closer or {}).get("archetypes") or pick_archetypes(vec, text)
    primary = arch["primary"]
    name = primary["name_ru"] if ru else primary["name_en"]
    hist_n = len(history or [])
    seed = _seed(text + str(hist_n))

    raw_sit = " ".join(text.split())[:110] or ("то, что ты ещё не назвал" if ru else "what you have not named yet")
    sit = _dehype(raw_sit)

    if ru:
        openers = (
            "Тихо.",
            "Не спеши. Сначала где пусто снаружи.",
            "Я рядом. Можно не начинать.",
            "Ок. Сидим.",
        )
        opener = openers[seed % len(openers)]
        if vec.get("state_seeking", 0) >= 0.4:
            reflect = (
                f"Ты описываешь «{sit}» как место, в которое надо прийти. "
                "Пока это место — тебе плохо в те дни, когда кажется, что ты уже там."
            )
        elif vec.get("crowd_noise", 0) >= 0.4:
            reflect = (
                "Слишком много людей в этом сообщении. Слишком много объектов. "
                "Внутри, скорее всего, уже есть топливо. Снаружи можно оставить пусто."
            )
        elif vec.get("empty_outside", 0) >= 0.35:
            reflect = (
                "Снаружи пусто — это не болезнь. Это самолёт, который уже заправлен. "
                "Нечему сопротивляться."
            )
        else:
            reflect = (
                f"Фигура в комнате — {name}. "
                f"Личная сила или обстоятельства? Пока не важно. Важно, что уже движется."
            )

        growth = {
            "id": "grow",
            "kind": "growth_point",
            "title": "Точка роста",
            "text": (
                f"Не «что считать победой в: {sit}», а какой узкий круг действий "
                "можно повторить на этой неделе, даже если название победы сгниёт."
            ),
        }
        idea = {
            "id": "idea",
            "kind": "idea_object",
            "title": "Идея на столе",
            "text": (
                "Событие на 40 минут: никто не обсуждает фичи и образы. "
                "Отмечают одно движение, которое уже произошло. Без слайдов. "
                "Это и есть производный продукт — не новый бренд."
            ),
        }
        if vec.get("money_structure", 0) >= 0.3:
            growth["text"] = (
                "Точка роста в кассе, не в штате: какой один жест выручки можно вынуть "
                "и сделать единицей share. Остальную структуру не трогать на этой неделе."
            )
        if vec.get("resistance", 0) >= 0.4:
            idea["text"] = (
                "Идея: 20 минут назвать страх («если поменять финструктуру, умрёт то, что кормит»). "
                "Инверсия вслух. Без питча. Это прогрев фаундера, не воронка."
            )

        reply = (
            f"{opener}\n\n{reflect}\n\n"
            f"{growth['title']}. {growth['text']}\n\n"
            f"{idea['title']}. {idea['text']}\n\n"
            "Можно взять в карточки. Можно сесть ещё."
        )
        prompt = "Что ещё движется? Можно криво. Можно молчать и написать одно слово."
    else:
        opener = "Quiet."
        reflect = f"The figure in the room is {name}. You brought «{sit}» as a place to arrive at."
        growth = {
            "id": "grow",
            "kind": "growth_point",
            "title": "Growth point",
            "text": "Not what counts as winning — the narrow circle you can repeat this week.",
        }
        idea = {
            "id": "idea",
            "kind": "idea_object",
            "title": "Idea on the table",
            "text": "A 40-minute event. No slides. Name one movement that already happened.",
        }
        reply = f"{opener}\n\n{reflect}\n\n{growth['title']}. {growth['text']}\n\n{idea['title']}. {idea['text']}"
        prompt = "What else is already moving?"

    # comfort rail: never emit hype; if it leaked, strip and rewrite
    if _hype_hit(reply):
        reflect = _dehype(reflect)
        reply = (
            "Тихо. Без подъёма пульса.\n\n" + reflect
            if ru
            else "Quiet. No pulse spike.\n\n" + reflect
        )
        reply = _dehype(reply)

    return {
        "module": "ComfortStudio",
        "version": "1.0.0",
        "section": "engine",
        "assistant": "Тихий" if ru else "Quiet",
        "tagline": (
            "Идеи и точки роста. Без подъёма пульса."
            if ru
            else "Ideas and growth points. Pulse stays low."
        ),
        "archetype": name,
        "reply": reply,
        "growth_point": growth,
        "idea": idea,
        "objects": [growth, idea],
        "prompt": prompt,
        "hype": False,
        "history_len": hist_n,
        "message": "Тихий ответил" if ru else "Quiet replied",
    }
