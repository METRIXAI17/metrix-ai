"""Consult slot: diagnosis → one contour → canon compare → reinforcements."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.core.coop.brief_normalizer import normalize_brief
from backend.core.coop.consult_patterns.flags import detect_flags
from backend.core.coop.deadend import DeadendRouter
from backend.core.output_editor import edit_client_text

_CANON = Path(__file__).resolve().parent / "consult_patterns" / "leak_report_canon.md"


def _canon_text() -> str:
    try:
        return _CANON.read_text(encoding="utf-8")
    except OSError:
        return "продавать ДЫРУ и ОТЧЁТ, не Telegram"


def _said(raw: str) -> str:
    t = (raw or "").strip().replace("\n", " ")
    return t[:280] + ("…" if len(t) > 280 else "")


def _means(order: str, flags: list[dict[str, Any]]) -> str:
    if any(f.get("id") == "P3" for f in flags):
        return "Клиент говорит «бот». Имеет в виду дыру: заявки без хозяина и без цифры потерь."
    if order == "TYPE_B":
        return "Клиент просит креатив. Имеет в виду серию, которую можно повторить в одном замке стиля."
    return "Клиент просит автоматизацию. Имеет в виду контур учёта: вход, статус, хозяин, отчёт."


def _missing_number(flags: list[dict[str, Any]], assumed: dict[str, str]) -> str:
    if any(f.get("id") == "P6" for f in flags):
        return assumed.get("leads_week") or "нет числа: заявки/неделя, время реакции или % без хозяина"
    return "число названо или ASSUMED помечено"


def build_consult(brief: str, *, prior_style: dict[str, str] | None = None) -> dict[str, Any]:
    flags = detect_flags(brief)
    norm = normalize_brief(brief, prior_style=prior_style)
    dead = DeadendRouter().route(brief, flags=flags, prior_style=prior_style)
    order = norm["order_type"]
    labels = " ".join(f"[{f['code']}]" for f in flags)

    a = {
        "said": _said(brief),
        "means": _means(order, flags),
        "missing_number": _missing_number(flags, dead.get("assumed") or {}),
    }
    if order == "TYPE_B":
        b = {
            "contour": "одна серия в style_lock",
            "in": "референс / тон / длина / запреты",
            "status": "черновик → правка в замке → сдача куска",
            "owner": "автор серии (фрилансер) до вопроса «повторяем?»",
            "escalate": "если просят другой жанр — новый бриф",
            "report": "тихий вопрос: следующий в этом же замке — тема X или Y?",
            "out_of_scope": "реклама, найм, смена жанра, список направлений",
        }
    else:
        b = {
            "contour": "один контур TYPE_A",
            "in": "все входы → один список",
            "status": "стадии без пустого перевода",
            "owner": "хозяин + N минут",
            "escalate": "если не взяли — следующий по имени",
            "report": "понедельник: пришло / взяли вовремя / сгорело / на ком",
            "out_of_scope": "реклама, скрипты продаж, найм, рост трафика",
        }

    reinforcements = [
        {
            "if": "P6",
            "do": "5 вопросов квалификации, стоп полного пакета",
            "active": any(f["id"] == "P6" for f in flags),
        },
        {
            "if": "P3",
            "do": "труба (Telegram/таблица/CRM) последней в ТЗ",
            "active": any(f["id"] == "P3" for f in flags),
        },
        {
            "if": "P4",
            "do": "фраза: чат за 30к vs потеря с именем. Если нужен только чат — не брать",
            "active": any(f["id"] == "P4" for f in flags),
        },
        {
            "if": "P9",
            "do": "оффер ретейнера отчёта вписать в сдачу",
            "active": True,
        },
    ]
    reinforcements = [r for r in reinforcements if r["active"]][:4]

    body = [
        "A. ДИАГНОЗ ДЫРЫ",
        f"Сказал: {a['said']}",
        f"Имеет в виду: {a['means']}",
        f"Число, которого не хватает: {a['missing_number']}",
        labels,
        "",
        "B. РЕШЕНИЕ НА ОДИН КОНТУР",
        f"Контур: {b['contour']}",
        f"Входы: {b['in']}",
        f"Статусы: {b['status']}",
        f"Хозяин: {b['owner']}",
        f"Эскалация: {b['escalate']}",
        f"Отчёт: {b['report']}",
        f"Не входит: {b['out_of_scope']}",
        "",
        "C. АНАЛИЗ КАК В ЭТАЛОНЕ",
        "Продавать дыру и отчёт, не Telegram. Дешёвый бот = чат. Дорогой контур = хозяин + срок + эскалация + недельная цифра.",
        "Ретейнер держат из понедельничного отчёта. Трафик не обещаем.",
        "",
        "D. УСИЛЕНИЯ",
    ]
    for r in reinforcements:
        body.append(f"- делать только если диагноз {r['if']}: {r['do']}")
    if order == "TYPE_B":
        body.append("Следующий в этом же замке — тема X или Y?")
    else:
        body.append("Ретейнер отчёта продаётся на сдаче.")
    if dead.get("next_question"):
        body.append(f"Next: {dead['next_question']}")

    text = edit_client_text("\n".join(body), order_type=order)
    return {
        "order_type": order,
        "thinking_flags": flags,
        "brief": norm,
        "deadlock": dead,
        "diagnosis": a,
        "solution": b,
        "canon": "leak_report_canon",
        "reinforcements": reinforcements,
        "client_text": text,
        "allow_codegen": bool(dead.get("allow_codegen")),
        "magistral": "M2" if order == "TYPE_B" else "M1",
    }
