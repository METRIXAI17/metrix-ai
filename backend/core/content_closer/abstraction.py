"""Abstract engine — the first voice of Metrix.

The user asked for emphasis on abstraction: binaries collapse when
the subject is movement. This module writes that register, then the
card translator turns it into functional designations.

Style register (do not flatten into slogans):
  Разочарованный Деятель. Работа и отдых, нищета и богатство, жизнь и смерть
  разрушаются, когда речь заходит о движении. Стремиться к состоянию —
  значит стремиться к смерти.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from backend.core.content_closer.archetypes import (
    inversion_line,
    pick_archetypes,
    score_vectors,
)


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:10], 16)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-zА-Яа-яёЁ0-9\-]{3,}", text or "")


def _clip_sentence(text: str, n: int = 88) -> str:
    t = " ".join((text or "").split())
    if len(t) <= n:
        return t.rstrip(".")
    return t[: n - 1].rstrip() + "…"


def _situation_object(brief: str) -> str:
    t = " ".join((brief or "").split())
    if not t:
        return "живая ситуация без имени"
    # keep a concrete shard so the essay is not generic philosophy
    for sep in (". ", "! ", "? ", "\n"):
        i = t.find(sep)
        if 0 < i < 140:
            return t[:i].strip().rstrip(".")
    return t[:120].rstrip(".")


BINARIES_RU = (
    ("работа", "отдых"),
    ("нищета", "богатство"),
    ("жизнь", "смерть"),
    ("победа", "провал"),
    ("команда", "одиночество"),
    ("метод", "окружение"),
    ("знание", "движение"),
    ("образ", "жест"),
    ("цель", "путь"),
    ("полный", "пустой"),
)


def _binaries_for(brief: str, vectors: dict[str, float]) -> list[tuple[str, str]]:
    t = (brief or "").lower()
    picked: list[tuple[str, str]] = []
    if any(w in t for w in ("работ", "выгор", "отдых", "баланс", "burnout")):
        picked.append(("работа", "отдых"))
    if any(w in t for w in ("бедн", "нищет", "богат", "деньг", "выруч", "марж", "чеком")):
        picked.append(("нищета", "богатство"))
    if any(w in t for w in ("побед", "провал", "цель", "kpi", "успех")):
        picked.append(("победа", "провал"))
    if any(w in t for w in ("команд", "сотруд", "нанима", "штат")):
        picked.append(("команда", "одиночество"))
    if any(w in t for w in ("стратег", "метод", "бренд", "образ", "упаков")):
        picked.append(("метод", "окружение"))
    if any(w in t for w in ("фич", "продукт", "бэклог", "jira")):
        picked.append(("объект", "труд"))
    if not picked:
        # default antagonists from the user's engine sample
        picked = [("работа", "отдых"), ("нищета", "богатство"), ("жизнь", "смерть")]
    if vectors.get("state_seeking", 0) >= 0.5 and ("жизнь", "смерть") not in picked:
        picked.append(("жизнь", "смерть"))
    return picked[:4]


def _cadence(seed: int) -> str:
    return ("long", "cut", "breath")[seed % 3]


def compose_abstraction(
    brief: str,
    *,
    lang: str = "ru",
    archetypes: dict[str, Any] | None = None,
    vectors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write the abstract essay. This is the engine's first answer."""
    ru = not (lang or "").lower().startswith("en")
    text = (brief or "").strip()
    vec = vectors or score_vectors(text)
    arch = archetypes or pick_archetypes(vec, text)
    primary = arch["primary"]
    secondary = arch["secondary"]
    sit = _situation_object(text)
    binaries = _binaries_for(text, vec)
    inv = inversion_line(vec, lang)
    seed = _seed(text + primary["id"])
    cadence = _cadence(seed)
    bin_line = ", ".join(f"{a} и {b}" for a, b in binaries)

    name = primary["name_ru"] if ru else primary["name_en"]
    name2 = secondary["name_ru"] if ru else secondary["name_en"]

    if ru:
        openers = (
            f"{name}.",
            f"Все мы знаем эти привычные понятия-антагонисты. {bin_line.capitalize()}. "
            f"Но что если я вам скажу, что эти понятия — да и вообще само слово «понятие» — "
            f"разрушаются, когда речь заходит о движении?",
            f"Можно сказать, что движение разрушает всё, что можно как-то обозначить. "
            f"Получается, что всё, что имеет значение в этом мире — бессмысленно, пока ты жив. "
            f"Стремиться к какому-то состоянию — это значит стремиться к смерти.",
        )
        middle = (
            f"Ситуация, которую ты принёс — «{sit}» — всё ещё названа как место, в которое надо прийти. "
            f"Пока это место, оно уже немного мертво.",
            inv,
            f"{name2}. Личная сила этого человека. Или обстоятельства, которые побеждают?",
        )
        if vec.get("crowd_noise", 0) >= 0.35 or vec.get("knowledge_glut", 0) >= 0.35 or vec.get("object_glut", 0) >= 0.35:
            glut = (
                "Слишком много людей, которые мешают. "
                "Слишком много знаний, которые обесценивают информацию. "
                "Слишком много объектов, которые обесценивают труд."
            )
            if glut not in middle:
                middle = middle + (glut,)
        if vec.get("empty_outside", 0) >= 0.28 and vec.get("full_inside", 0) >= 0.25:
            middle = middle + (
                "Когда мир пустой вовне и полон изнутри — это хорошо, "
                "как самолёт, полный пассажиров, топлива и турбодвигателей. Нечему сопротивляться.",
            )
        close = (
            "Между методом и окружением.",
            "Оно может двигаться только тем или иным образом. Образы не имеют смысла. "
            "Ты всё равно продолжаешь играть. Ты можешь сделать ровно то, что соответствует "
            "узкому кругу действий, задуманных в данной ситуации. "
            "Когда ты влезаешь в то, что невозможно сделать, ты не проявляешь личную силу. "
            "Тебе это не надо. Просто обстоятельства меняются. И всё.",
        )
        if cadence == "cut":
            close = close + ("Не кнопка. Комната. Событие уже идёт.",)
        elif cadence == "breath":
            close = close + ("Дыши. Сначала где пусто снаружи. Потом где полно внутри.",)
        else:
            close = close + (f"Узкий круг этой недели не обязан называться «{ _clip_sentence(sit, 42) }».",)
        paragraphs = [" ".join(openers), " ".join(middle), " ".join(close)]
    else:
        paragraphs = [
            (
                f"{name}. We know the usual antagonists: {bin_line}. "
                f"What if the word «concept» itself collapses when the subject is movement? "
                f"Movement destroys whatever can be designated. "
                f"What matters is meaningless while you are alive. "
                f"To strive toward a state is to strive toward death."
            ),
            (
                f"The situation you brought — «{sit}» — is still named as a place to arrive at. "
                f"While it is a place, it is already a little dead. {inv} {name2}."
            ),
            (
                "Between method and environment. It can only move this way or that. "
                "Images have no meaning. You keep playing. You can do exactly the narrow circle "
                "of actions this situation already designed. Climbing into the impossible is not personal power. "
                "You don't need that. Circumstances change. That's all."
            ),
        ]

    essay = "\n\n".join(paragraphs)
    # density: unique content words / length — abstraction should be dense, not watery
    words = [w.lower() for w in _tokens(essay)]
    uniq = len(set(words))
    density = round(min(1.0, 0.38 + uniq / max(80, len(words) * 1.1)), 3)
    motion_verbs = ("движ", "игра", "влез", "меня", "разруш", "стрем", "вход", "move", "play", "collapse")
    has_motion = any(v in essay.lower() for v in motion_verbs)
    has_death_state = "смер" in essay.lower() or "death" in essay.lower()

    return {
        "module": "AbstractionEngine",
        "version": "1.0.0",
        "register": "motion_destroys_designation",
        "archetype": name,
        "archetype_id": primary["id"],
        "secondary": name2,
        "secondary_id": secondary["id"],
        "binaries": [{"a": a, "b": b} for a, b in binaries],
        "situation_object": sit,
        "inversion": inv,
        "essay": essay,
        "paragraphs": paragraphs,
        "cadence": cadence,
        "density": density,
        "has_motion": has_motion,
        "has_state_as_death": has_death_state,
        "word_count": len(words),
        "lead": f"{name}.",
        "message": (
            f"Абстракция · {name} · density={density}"
            if ru
            else f"Abstraction · {name} · density={density}"
        ),
    }


def format_abstraction_html(pack: dict[str, Any]) -> str:
    essay = (pack.get("essay") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lead = (pack.get("lead") or pack.get("archetype") or "").replace("&", "&amp;")
    body = essay.replace("\n\n", "</p><p>")
    return f"<b>{lead}</b>\n\n<p>{body}</p>"


def format_abstraction_telegram(pack: dict[str, Any]) -> str:
    essay = pack.get("essay") or ""
    lead = pack.get("lead") or pack.get("archetype") or ""
    # Telegram HTML
    def esc(s: str) -> str:
        return (
            str(s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    return f"<b>{esc(lead)}</b>\n\n{esc(essay)}"
