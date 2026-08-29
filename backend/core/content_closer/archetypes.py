"""Movement archetypes — the people who arrive in the landing room.

Not personas. Not ICPs. Figures that appear when binaries collapse
and the only thing left is how a person actually moves.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:12], 16)


def _low(text: str) -> str:
    return (text or "").lower()


def _hit(text: str, words: tuple[str, ...]) -> int:
    t = _low(text)
    return sum(1 for w in words if w in t)


ARCHETYPES: dict[str, dict[str, Any]] = {
    "disappointed_actor": {
        "id": "disappointed_actor",
        "name_ru": "Разочарованный Деятель",
        "name_en": "Disappointed Actor",
        "figure": "тот, кто уже делал — и обнаружил, что «сделать» было состоянием, а не движением",
        "binary_it_dissolves": ("работа/отдых", "победа/провал", "жизнь/смерть как цели"),
        "personal_power": "перестать стремиться к состоянию",
        "circumstance": "название победы сгнивает само, если его не кормить",
        "growth_question": "какой узкий круг действий остаётся, когда цель умерла?",
        "accent": "#7dd3fc",
    },
    "antifragile_manager": {
        "id": "antifragile_manager",
        "name_ru": "Менеджер, стремящийся к антихрупкости",
        "name_en": "Manager seeking antifragility",
        "figure": "тот, кто копит запас и людей, потому что боится пустоты снаружи",
        "binary_it_dissolves": ("команда/одиночество", "знание/незнание", "объект/труд"),
        "personal_power": "выдержать пустой внешний контур при полном внутреннем",
        "circumstance": "лишние люди, знания и объекты обесценивают то, что ещё живо",
        "growth_question": "что останется, если убрать всех, кто мешает, и всё, что обесценивает?",
        "accent": "#c4b5fd",
    },
    "method_environment": {
        "id": "method_environment",
        "name_ru": "Между методом и окружением",
        "name_en": "Between method and environment",
        "figure": "тот, кто играет образами стратегии, пока ситуация требует узкого круга действий",
        "binary_it_dissolves": ("метод/среда", "образ/движение", "возможное/невозможное"),
        "personal_power": "делать только то, что соответствует узкому кругу данной ситуации",
        "circumstance": "влезание в невозможное не проявляет силу — оно её тратит",
        "growth_question": "какой единственный способ движения здесь вообще существует?",
        "accent": "#5eead4",
    },
    "full_plane": {
        "id": "full_plane",
        "name_ru": "Пилот с полным баком",
        "name_en": "Pilot with a full tank",
        "figure": "мир пуст снаружи и полон внутри — как самолёт с пассажирами, топливом и турбинами",
        "binary_it_dissolves": ("пустота/полнота", "сопротивление/поток"),
        "personal_power": "нечему сопротивляться",
        "circumstance": "внешний шум уже не кормит, внутренний контур уже собран",
        "growth_question": "куда летит полный самолёт, если некуда «доказывать»?",
        "accent": "#fbbf24",
    },
    "narrow_circle": {
        "id": "narrow_circle",
        "name_ru": "Носитель узкого круга",
        "name_en": "Bearer of a narrow circle",
        "figure": "тот, кто продолжает играть, даже когда образы потеряли смысл",
        "binary_it_dissolves": ("смысл/бессмыслица", "сила/обстоятельства"),
        "personal_power": "не влезать в то, что невозможно сделать",
        "circumstance": "обстоятельства меняются сами. И всё.",
        "growth_question": "какой круг действий уже задуман ситуацией — без твоей драмы?",
        "accent": "#fda4af",
    },
    "living_motion": {
        "id": "living_motion",
        "name_ru": "Живое движение",
        "name_en": "Living motion",
        "figure": "тот, для кого понятие разрушается, едва речь заходит о движении",
        "binary_it_dissolves": ("обозначить/двигаться", "значение/бессмысленность"),
        "personal_power": "оставаться живым, не стремясь к состоянию",
        "circumstance": "пока ты жив, всё, что имеет значение, ещё не зафиксировано",
        "growth_question": "что движется уже сейчас — без названия?",
        "accent": "#67e8f9",
    },
}


VECTOR_LEX = {
    "state_seeking": (
        "цель",
        "побед",
        "успех",
        "хочу стать",
        "выйти на",
        "масштабир",
        "результат",
        "kpi",
        "достич",
        "закрыть год",
        "выйти в плюс",
        "состояние",
        "наконец",
        "когда-нибудь",
        "grow",
        "win",
        "success",
        "goal",
    ),
    "binary_trap": (
        "либо",
        "или или",
        "работа",
        "отдых",
        "нищет",
        "богат",
        "провал",
        "успех",
        "жизнь или",
        "смерть",
        "win/lose",
        "burnout",
        "баланс",
        "work-life",
        "либо так",
    ),
    "crowd_noise": (
        "команд",
        "сотруд",
        "менедж",
        "отдел",
        "штат",
        "нанима",
        "люди меш",
        "созвон",
        "митинг",
        "standup",
        "80 человек",
        "50–500",
        "headcount",
        "все хотят",
    ),
    "knowledge_glut": (
        "много зна",
        "информ",
        "курс",
        "книг",
        "фреймворк",
        "методол",
        "best practice",
        "все уже сказано",
        "переизбыт",
        "контент",
        "рассылк",
        "дашборд",
    ),
    "object_glut": (
        "фич",
        "продукт",
        "объект",
        "артефакт",
        "слайд",
        "таблиц",
        "jira",
        "тикет",
        "backlog",
        "много всего",
        "инструмент",
        "saas",
        "платформ",
    ),
    "empty_outside": (
        "тишин",
        "никого",
        "пусто",
        "нет спроса",
        "не пишут",
        "залип",
        "окно",
        "одиноч",
        "тихий рынок",
        "нет лидов",
        "молча",
    ),
    "full_inside": (
        "внутри",
        "своё",
        "уже есть",
        "собрано",
        "модель",
        "движок",
        "контур",
        "топлив",
        "полный",
        "готово внутри",
        "сам знаю",
    ),
    "method_over_env": (
        "стратег",
        "метод",
        "систем",
        "фрейм",
        "процесс",
        "как правильно",
        "по книге",
        "playbook",
        "воронк",
        "схем",
    ),
    "image_over_move": (
        "бренд",
        "образ",
        "позицион",
        "визуал",
        "презентац",
        "личный бренд",
        "картинк",
        "упаковк",
        "позиционир",
        "нарратив",
    ),
    "impossible_climb": (
        "невозможн",
        "надо всё",
        "сразу",
        "прорыв",
        "изменить всё",
        "перестроит",
        "с нуля",
        "идеальн",
        "когда будет готово",
        "не могу пока",
    ),
    "resistance": (
        "бесит",
        "застрял",
        "не идёт",
        "сопротивл",
        "страх",
        "боюсь",
        "не могу поменять",
        "финструктур",
        "касс",
        "марж",
        "выручк",
        "не отпускает",
    ),
    "money_structure": (
        "выручк",
        "марж",
        "юнит",
        "ltv",
        "чеком",
        "касса",
        "revenue",
        "комисс",
        "success fee",
        "долю",
        "финмодел",
        "оплат",
        "цен",
        "подписк",
        "ретейнер",
    ),
}


def score_vectors(brief: str) -> dict[str, float]:
    """Score movement vectors from a raw situation. Deterministic, no LLM."""
    t = brief or ""
    n = max(12, len(re.findall(r"[a-zA-Zа-яА-ЯёЁ]{3,}", t)))
    out: dict[str, float] = {}
    for key, words in VECTOR_LEX.items():
        raw = _hit(t, words)
        # density plus a small seed wobble so close briefs don't collapse
        wobble = ((_seed(t + key) % 17) / 200.0)
        val = min(1.0, (raw / 3.4) + min(0.22, raw / max(8, n / 9)) + wobble)
        if raw == 0:
            val = min(val, 0.12 + wobble)
        out[key] = round(val, 3)

    # inversion: "плохо когда хорошо" is itself a vector
    if _hit(t, ("плохо", "хорошо", "кажется", "думаю что")) >= 2:
        out["state_seeking"] = min(1.0, out["state_seeking"] + 0.18)
        out["binary_trap"] = min(1.0, out["binary_trap"] + 0.18)

    # a loaded inner system with no outer noise
    if out["full_inside"] > 0.35 and out["empty_outside"] > 0.28:
        out["resistance"] = max(0.0, out["resistance"] - 0.15)

    out["motion_over_concept"] = round(
        min(
            1.0,
            0.25
            + 0.35 * out["resistance"]
            + 0.2 * out["state_seeking"]
            + 0.2 * (1.0 - out["image_over_move"]),
        ),
        3,
    )
    return out


def pick_archetypes(vectors: dict[str, float], brief: str = "") -> dict[str, Any]:
    """Primary + secondary figure. Always two — one is never enough."""
    scores = {
        "disappointed_actor": (
            0.42 * vectors.get("state_seeking", 0)
            + 0.28 * vectors.get("binary_trap", 0)
            + 0.18 * vectors.get("resistance", 0)
            + 0.12 * vectors.get("impossible_climb", 0)
        ),
        "antifragile_manager": (
            0.34 * vectors.get("crowd_noise", 0)
            + 0.26 * vectors.get("knowledge_glut", 0)
            + 0.24 * vectors.get("object_glut", 0)
            + 0.16 * vectors.get("money_structure", 0)
        ),
        "method_environment": (
            0.4 * vectors.get("method_over_env", 0)
            + 0.32 * vectors.get("image_over_move", 0)
            + 0.28 * vectors.get("impossible_climb", 0)
        ),
        "full_plane": (
            0.46 * vectors.get("empty_outside", 0)
            + 0.38 * vectors.get("full_inside", 0)
            + 0.16 * (1.0 - vectors.get("crowd_noise", 0))
        ),
        "narrow_circle": (
            0.36 * vectors.get("impossible_climb", 0)
            + 0.28 * vectors.get("method_over_env", 0)
            + 0.2 * vectors.get("resistance", 0)
            + 0.16 * vectors.get("image_over_move", 0)
        ),
        "living_motion": (
            0.4 * vectors.get("motion_over_concept", 0)
            + 0.3 * vectors.get("binary_trap", 0)
            + 0.3 * (1.0 - vectors.get("state_seeking", 0))
        ),
    }
    ordered = sorted(scores.items(), key=lambda kv: -kv[1])
    # slight seed to break exact ties without changing the leader much
    if len(ordered) >= 2 and abs(ordered[0][1] - ordered[1][1]) < 0.04:
        if _seed(brief) % 2:
            ordered[0], ordered[1] = ordered[1], ordered[0]

    primary_id = ordered[0][0]
    secondary_id = ordered[1][0]
    return {
        "primary": {**ARCHETYPES[primary_id], "score": round(ordered[0][1], 3)},
        "secondary": {**ARCHETYPES[secondary_id], "score": round(ordered[1][1], 3)},
        "board": [{"id": k, "score": round(v, 3), "name_ru": ARCHETYPES[k]["name_ru"]} for k, v in ordered],
    }


def inversion_line(vectors: dict[str, float], lang: str = "ru") -> str:
    ru = not (lang or "").lower().startswith("en")
    if vectors.get("state_seeking", 0) >= 0.45:
        return (
            "Тебе плохо тогда, когда ты думаешь, что тебе хорошо, "
            "и хорошо тогда, когда ты думаешь, что тебе плохо."
            if ru
            else "It is bad when you think it is good, and good when you think it is bad."
        )
    if vectors.get("crowd_noise", 0) >= 0.4 or vectors.get("knowledge_glut", 0) >= 0.4:
        return (
            "Слишком много людей, которые мешают. Слишком много знаний, которые обесценивают информацию. "
            "Слишком много объектов, которые обесценивают труд."
            if ru
            else "Too many people in the way. Too much knowledge that cheapens information. Too many objects that cheapen labor."
        )
    if vectors.get("empty_outside", 0) >= 0.35 and vectors.get("full_inside", 0) >= 0.3:
        return (
            "Когда мир пустой вовне и полон изнутри — это хорошо, "
            "как самолёт, полный пассажиров, топлива и турбин. Нечему сопротивляться."
            if ru
            else "When the world is empty outside and full inside, that is good — a plane full of passengers, fuel, turbines. Nothing to resist."
        )
    return (
        "Оно может двигаться только тем или иным образом. Образы не имеют смысла. "
        "Ты всё равно продолжаешь играть."
        if ru
        else "It can only move this way or that. Images have no meaning. You keep playing anyway."
    )
