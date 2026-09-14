"""Split a raw brief into goal / inbox / artifact / deadline / done-when."""

from __future__ import annotations

import re
from typing import Any

TYPE_A_KW = (
    "заявк", "бот", "crm", "таблиц", "статус", "эскалац", "отчёт", "отчет",
    "inbox", "sla", "лид", "воронк", "amo", "bitrix", "битрикс", "учёт", "учет",
)
TYPE_B_KW = (
    "текст", "концепт", "лендинг", "сценари", "стиль", "копирайт", "серия",
    "оффер", "упаковк", "tone", "референс", "креатив", "пост",
)

QUESTIONS = {
    "goal": "Какая одна цель заказа — контур учёта или серия в одном стиле?",
    "inbox": "Куда сейчас падают заявки / откуда берётся материал?",
    "artifact": "Какой файл считаем сдачей?",
    "deadline": "Какой срок?",
    "done_when": "Как поймём, что готово — одна цифра или повтор в том же стиле?",
}


def classify_order(text: str) -> str:
    t = (text or "").lower()
    a = sum(1 for k in TYPE_A_KW if k in t)
    b = sum(1 for k in TYPE_B_KW if k in t)
    if a >= 2 and b >= 2:
        return "MIXED"
    if b > a and b >= 1:
        return "TYPE_B"
    return "TYPE_A"


def _pull(text: str, keys: tuple[str, ...]) -> str:
    t = text or ""
    for k in keys:
        m = re.search(rf"{k}\s*[:—\-]\s*(.+)", t, re.I)
        if m:
            return m.group(1).strip()[:240]
    return ""


def extract_style_lock(text: str) -> dict[str, str]:
    t = text or ""
    return {
        "tone": _pull(t, ("тон", "tone")) or "",
        "length": _pull(t, ("длина", "length", "объём", "объем")) or "",
        "bans": _pull(t, ("запрет", "нельзя", "bans")) or "",
        "reference": _pull(t, ("референс", "как у", "reference")) or "",
    }


def normalize_brief(text: str, *, prior_style: dict[str, str] | None = None) -> dict[str, Any]:
    raw = (text or "").strip()
    order = classify_order(raw)
    fields = {
        "goal": _pull(raw, ("цель", "goal", "чтобы")),
        "inbox": _pull(raw, ("вход", "заявк", "inbox", "откуда")),
        "artifact": _pull(raw, ("артефакт", "сдача", "файл", "выход")),
        "deadline": _pull(raw, ("срок", "deadline", "до ")),
        "done_when": _pull(raw, ("готово", "приёмка", "приемка", "done")),
    }
    empty = [k for k, v in fields.items() if not v]
    questions = [QUESTIONS[k] for k in empty[:3]]
    assumed: dict[str, str] = {}
    if empty:
        if "goal" in empty:
            assumed["goal"] = (
                "ASSUMED: один контур учёта заявок"
                if order != "TYPE_B"
                else "ASSUMED: один артефакт в замке стиля"
            )
        if "inbox" in empty:
            assumed["inbox"] = "ASSUMED: один канал, который клиент назовёт первым"
        if "artifact" in empty:
            assumed["artifact"] = (
                "ASSUMED: ТЗ + статусы + регламент + отчёт понедельника"
                if order != "TYPE_B"
                else "ASSUMED: первый кусок серии + style_lock"
            )
        if "deadline" in empty:
            assumed["deadline"] = "ASSUMED: 14 дней на пилот одного канала"
        if "done_when" in empty:
            assumed["done_when"] = (
                "ASSUMED: видна недельная цифра потерь"
                if order != "TYPE_B"
                else "ASSUMED: заказчик просит повтор в том же замке"
            )
        for k, v in assumed.items():
            if not fields.get(k):
                fields[k] = v

    style = extract_style_lock(raw)
    if prior_style:
        for k, v in prior_style.items():
            if not style.get(k) and v:
                style[k] = v

    split = None
    if order == "MIXED":
        split = {
            "type_a": "контур учёта: вход / статус / хозяин / отчёт",
            "type_b": "серия: style_lock и первый кусок отдельно",
            "rule": "не смешивать в одном ТЗ",
        }

    return {
        "order_type": order,
        "fields": fields,
        "questions": questions,
        "assumed": assumed,
        "style_lock": style,
        "split": split,
        "raw": raw[:2000],
    }
