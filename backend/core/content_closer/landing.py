"""Landing studio — first of three bot sections.

Semantic design: the landing is not a page and not a studio button.
It is a vision of an event (видение события). You do not start. You arrive.

The room is empty outside (no chrome noise) and full inside
(archetype, atmosphere, who enters, what moves, what stays).
"""

from __future__ import annotations

import hashlib
from typing import Any


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:10], 16)


ROOMS = (
    {
        "id": "dim_table",
        "lighting": "низкий тёплый свет на столе, края комнаты не проявлены",
        "objects": "стол, несколько карт рубашкой вниз, пульс в углу",
        "tempo": "медленно, 4 секунды на вдох",
        "sound": "почти тишина, иногда турбина далеко",
    },
    {
        "id": "plane_cabin",
        "lighting": "холодная полоска над креслами, иллюминатор чёрный",
        "objects": "полный бак, полный салон, нечему сопротивляться",
        "tempo": "ровный гул, без объявлений",
        "sound": "двигатели, не голос",
    },
    {
        "id": "narrow_circle",
        "lighting": "круг света, за кругом нет декораций",
        "objects": "один жест, который уже задуман ситуацией",
        "tempo": "короткие шаги, без разбега",
        "sound": "ни музыки, ни питча",
    },
    {
        "id": "empty_outside",
        "lighting": "окно без вида, лампа на 40Вт",
        "objects": "внутри — движок, карточки, топливо. Снаружи — никто.",
        "tempo": "сидеть можно долго",
        "sound": "клавиатура иногда, не слак",
    },
)


INVITES_RU = (
    "Не кнопка. Комната. Событие уже идёт — ты входишь в него, или нет.",
    "Можно сесть. Можно войти. Не надо начинать.",
    "Образы можно оставить в коридоре. Здесь только узкий круг действий.",
    "Если ты пришёл за состоянием — здесь его нет. Есть движение.",
)


def _room_for(vectors: dict[str, float], brief: str) -> dict[str, str]:
    if vectors.get("empty_outside", 0) >= 0.35 and vectors.get("full_inside", 0) >= 0.28:
        return ROOMS[1]
    if vectors.get("impossible_climb", 0) >= 0.4 or vectors.get("method_over_env", 0) >= 0.45:
        return ROOMS[2]
    if vectors.get("crowd_noise", 0) < 0.25:
        return ROOMS[3]
    return ROOMS[_seed(brief) % len(ROOMS)]


def compose_event(
    brief: str,
    *,
    archetypes: dict[str, Any],
    vectors: dict[str, float],
    lang: str = "ru",
) -> dict[str, Any]:
    ru = not (lang or "").lower().startswith("en")
    primary = archetypes["primary"]
    name = primary["name_ru"] if ru else primary["name_en"]
    sit = " ".join((brief or "").split())
    sit_short = sit[:90] + ("…" if len(sit) > 90 else "") or (
        "живая ситуация без имени" if ru else "unnamed living situation"
    )
    room = _room_for(vectors, brief)
    seed = _seed(brief + primary["id"])
    invite = INVITES_RU[seed % len(INVITES_RU)] if ru else INVITES_RU[0]

    if ru:
        title = f"Вход · {name}"
        who = (
            f"{name} входит не как клиент и не как ученик. "
            f"Входит как человек, который ещё движется внутри «{sit_short}»."
        )
        moves = (
            "Движется только то, что уже может двигаться. "
            "Фичи, слайды, оргсхемы — стоят у стены. Их не просят сесть за стол."
        )
        stays = (
            "Стоит узкий круг действий этой недели. Стоит единица денег, если она уже есть. "
            "Стоит условие смерти пакета. Остальное не входит."
        )
        atmosphere = (
            f"{room['lighting']}. {room['objects']}. Темп: {room['tempo']}. "
            f"Звук: {room['sound']}."
        )
        vision = (
            f"Событие называется «{title}».\n\n"
            f"{atmosphere}\n\n"
            f"{who}\n\n"
            f"{moves}\n\n"
            f"{stays}\n\n"
            f"{invite}"
        )
        anti_cta = (
            "На лендинге нет «начать», «купить», «запустить», «гарантируем». "
            "Есть дверь. Есть стол. Есть пульс."
        )
    else:
        title = f"Entry · {name}"
        who = f"{name} enters as someone still moving inside «{sit_short}»."
        moves = "Only what can already move, moves. Decks stay at the wall."
        stays = "The narrow circle of this week stays. The money unit, if it exists, stays. The kill condition stays."
        atmosphere = f"{room['lighting']}. {room['objects']}."
        vision = f"The event is «{title}». {atmosphere} {who} {moves} {stays} {invite}"
        anti_cta = "No start / buy / launch / guarantee. A door, a table, a pulse."

    return {
        "module": "LandingStudio",
        "version": "1.0.0",
        "section": "landing",
        "title": title,
        "archetype": name,
        "atmosphere": atmosphere,
        "who_enters": who,
        "what_moves": moves,
        "what_stays": stays,
        "invitation": invite,
        "anti_cta": anti_cta,
        "room": room,
        "vision_text": vision,
        "field_label": "Что сейчас движется" if ru else "What is already moving",
        "enter_label": "Войти" if ru else "Enter",
        "eyebrow": "Видение события" if ru else "Event vision",
        "hero": "Не кнопка. Комната." if ru else "Not a button. A room.",
        "lead": (
            "Работа и отдых здесь не противоположности. "
            "Стремиться к состоянию — значит стремиться к смерти. "
            "Metrix собирает видение события, в котором финансовая структура "
            "может сдвинуться без театра «новой жизни»."
            if ru
            else "Work and rest are not opposites here. To strive toward a state is to strive toward death."
        ),
        "hype_leaked": any(
            w in vision.lower()
            for w in ("купи", "гарант", "roi", "прорыв", "масштабир", "10x", "запустить успех")
        ),
        "message": title,
    }
