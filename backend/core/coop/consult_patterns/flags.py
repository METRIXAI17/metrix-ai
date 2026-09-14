"""Thinking/behavior flags P1–P10 for consult. No moralizing."""

from __future__ import annotations

import re
from typing import Any

CANON_QUOTES = {
    "P1": "технические переливы одного потока, не 7 направлений",
    "P2": "третьего пути почти нет",
    "P3": "сначала дыра и отчёт, труба — последней",
    "P4": "чат за 30к vs потеря с именем",
    "P5": "×3 только как маржа часа после 15 повторов",
    "P6": "квалификация: сколько заявок/нед, где живут, кто берёт",
    "P7": "пакет часов + оценка сверх пакета",
    "P8": "граница оффера в договоре/ТЗ одной строкой",
    "P9": "ретейнер продаётся НА сдаче",
    "P10": "технические переливы одного потока, не 7 направлений",
}

_LOCO = (
    "игр", "edu", "обучен", "видео", "чип", "chip", "стор", "store",
    "маркетплейс", "marketplace", "агентств", "saas", "ecom", "nft",
    "токен", "token", "платформ", "вселенн", "локомотив", "PdM",
)

_FLAG_SPEC: list[dict[str, Any]] = [
    {
        "id": "P1",
        "code": "UNIVERSE_BUILD",
        "wrong_move": "собрать супер-платформу",
        "right_move": "выбрать один контур TYPE_A или одну серию TYPE_B",
        "kind": "loco_count",
    },
    {
        "id": "P2",
        "code": "THIRD_PATH",
        "wrong_move": "архитектура маркетплейса",
        "right_move": "откуда первый платящий и какой повторный платёж",
        "rx": r"сами принес|ии сам продаж|прод\s*×?\s*3|прод\s*x3|сеть агент|стор сам",
    },
    {
        "id": "P3",
        "code": "SURFACE_BOT",
        "wrong_move": "спецификация бота",
        "right_move": "сначала дыра и отчёт, труба — последней",
        "rx": r"^(сделай\s+бота|telegram|кнопк|бот\s+с\s+меню)|начн[ие].{0,40}(бот|telegram|кнопк)",
    },
    {
        "id": "P4",
        "code": "PRICE_COLLAPSE",
        "wrong_move": "конкурировать кнопками",
        "right_move": "фраза «чат за 30к vs потеря с именем»",
        "rx": r"за\s*(25|30|35|40)\s*[кk]|бот за\s*\d",
    },
    {
        "id": "P5",
        "code": "SLOGAN_MATH",
        "wrong_move": "масштабировать слоган",
        "right_move": "сначала есть ли агентство; ×3 только как маржа часа после 15 повторов",
        "rx": r"1\s*млн|миллион\s*/?\s*мес|прод\s*[×xх]\s*3|агентств.{0,20}3",
    },
    {
        "id": "P6",
        "code": "NO_NUMBER",
        "wrong_move": "писать ТЗ",
        "right_move": "5 вопросов квалификации, стоп-генерации полного пакета",
        "kind": "no_number",
    },
    {
        "id": "P7",
        "code": "SCOPE_CREEP_LENA",
        "wrong_move": "бесконечный кастом в том же чеке",
        "right_move": "пакет часов + оценка сверх пакета",
        "rx": r"ещё ветк|наш(его)? менеджер|под наш|ещё один сценари",
    },
    {
        "id": "P8",
        "code": "MARKETING_SWAP",
        "wrong_move": "становиться директологом",
        "right_move": "граница оффера в договоре/ТЗ одной строкой",
        "rx": r"почему мало заявок|мало лид|нет трафик|увелич(ь|ить) продаж",
    },
    {
        "id": "P9",
        "code": "RETAINER_AMNESIA",
        "wrong_move": "«контур ваш, я исчез»",
        "right_move": "ретейнер продаётся НА сдаче",
        "rx": r"сдал и всё|без сопровожд|без отчёт|исчез|не нужен ретейн",
    },
    {
        "id": "P10",
        "code": "IDEA_FACTORY",
        "wrong_move": "7 направлений",
        "right_move": "технические переливы одного потока",
        "rx": r"7 направлен|список идей|ещё идей|много идей|вселенн",
    },
]


def _loco_count(text: str) -> int:
    t = (text or "").lower()
    return sum(1 for w in _LOCO if w.lower() in t)


def _has_metric(text: str) -> bool:
    t = (text or "").lower()
    if re.search(r"без\s+(цифр|числ|хозяин|sla|метрик)", t):
        return False
    if re.search(r"\d+\s*(заяв|лид|заявок|шт|/нед|в неделю|минут)", t):
        return True
    if re.search(r"(кто берёт|кто берет|owner\s+is|sla\s*\d)", t):
        return True
    if re.search(r"(есть хозяин|хозяин:|хозяин —|хозяин -)", t):
        return True
    return False


def detect_flags(brief: str) -> list[dict[str, Any]]:
    t = (brief or "").strip()
    low = t.lower()
    out: list[dict[str, Any]] = []
    locos = _loco_count(low)
    for spec in _FLAG_SPEC:
        hit = False
        if spec.get("kind") == "loco_count":
            hit = locos > 2
        elif spec.get("kind") == "no_number":
            hit = not _has_metric(low)
        else:
            rx = spec.get("rx")
            hit = bool(rx and re.search(rx, low, re.I | re.S))
        if not hit:
            continue
        out.append(
            {
                "id": spec["id"],
                "code": spec["code"],
                "trigger": spec["id"] + " " + spec["code"],
                "wrong_move": spec["wrong_move"],
                "right_move": spec["right_move"],
                "canon": CANON_QUOTES[spec["id"]],
                "label": spec["code"],
            }
        )
    return out


def has_flag(flags: list[dict[str, Any]], code: str) -> bool:
    c = code.upper()
    return any(f.get("id") == c or f.get("code") == c for f in flags)
