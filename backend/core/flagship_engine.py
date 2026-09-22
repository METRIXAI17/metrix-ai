"""Flagship conversation: free turnaround → intake → answers → SKU → file."""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.chain_store import load_chain
from backend.core.design_contour import analyze as analyze_contour
from backend.core.life_intake import apply_answers, format_telegram as format_intake
from backend.core.life_intake import intake, vectors_of
from backend.core.pricing_lanes import sku_of, tariff_board
from backend.core.product_file import generate_paid_file
from backend.core.tribute_products import create_product
from backend.core.workflow_turnaround import format_telegram as format_wf
from backend.core.workflow_turnaround import turnaround


def start(brief: str = "", *, lang: str = "ru", subject: str = "") -> dict[str, Any]:
    wf = turnaround(lang=lang, contour=False)
    if (brief or "").strip():
        pack = intake(brief, lang=lang, subject=subject)
        pack["workflow"] = pack.get("workflow") or wf
        if pack.get("contour"):
            pack["contour_design"] = analyze_contour(brief, lang=lang)
        return pack
    return {
        "ok": True,
        "free": True,
        "await": "two_lines",
        "workflow": wf,
        "prompt": (
            "Две строки, не эссе. Что ломается — и куда должно сесть."
            if (lang or "ru").startswith("ru")
            else "Two lines, not an essay. What breaks — and where it should sit."
        ),
    }


def answer(ticker: str, text: str, *, lang: str = "ru") -> dict[str, Any]:
    rec = load_chain(ticker) or {}
    questions = rec.get("questions") or []
    answers = dict(rec.get("answers") or {})
    # fill next unanswered question
    qid = ""
    for q in questions:
        if q.get("id") and not str(answers.get(q["id"]) or "").strip():
            qid = q["id"]
            break
    if not qid and questions:
        qid = f"q{len(answers)+1}"
    if qid:
        answers[qid] = (text or "").strip()[:800]
    pack = apply_answers(ticker, answers, lang=lang)
    remaining = [
        q for q in (pack.get("questions") or []) if not str(answers.get(q.get("id")) or "").strip()
    ]
    pack["remaining"] = remaining
    pack["answered"] = len(answers)
    pack["done_questions"] = not remaining
    if remaining:
        pack["next_question"] = remaining[0]
        n = pack.get("question_count") or len(pack.get("questions") or [])
        pack["prompt"] = f"Вопрос {pack['answered']+1}/{n}: {remaining[0].get('text')}"
    else:
        pack["vectors"] = vectors_of(pack)
        pack["prompt"] = pack.get("next") or "Сводка векторов готова. $490 — посадка."
    return pack


def check_before_pay(ticker: str = "", *, lang: str = "ru") -> dict[str, Any]:
    ru = (lang or "ru").startswith("ru")
    rec = load_chain(ticker) if ticker else None
    if not rec:
        return {
            "ok": False,
            "need": "flagship",
            "ask": (
                "Сначала Флагман — две строки. Потом сверить собранное до оплаты."
                if ru
                else "Flagship first — two lines. Then check what was assembled, before pay."
            ),
        }
    sku = sku_of("sku_490")
    vec = vectors_of({**rec, "questions": rec.get("questions") or [], "answers": rec.get("answers") or {}})
    return {
        "ok": True,
        "ticker": rec.get("ticker") or ticker,
        "problem": rec.get("problem") or "",
        "solution": rec.get("solution") or "",
        "vectors": vec,
        "eval_visible": False,
        "pay": sku,
        "inside": (
            "До оплаты видно суть, решение и варианты. $100 — кастом спека. $490 — рекурсия. Eval после оплаты."
            if ru
            else "Before pay: essence, solution, variants. $100 custom spec. $490 recursion. Eval after pay."
        ),
    }


def fulfill(ticker: str, sku_id: str = "sku_490", *, lang: str = "ru") -> dict[str, Any]:
    rec = load_chain(ticker) or {}
    if sku_id not in ("sku_100", "sku_490", "sku_1000", "sku_10000"):
        sku_id = "sku_490"
    product = create_product(
        ticker=ticker,
        solution=rec.get("solution") or "",
        sku_id=sku_id,
        problem=rec.get("problem") or "",
    )
    paid = generate_paid_file(ticker, sku_id=sku_id, lang=lang)
    ev = rec.get("eval") or {}
    return {
        "ok": True,
        "product": product,
        "file": paid,
        "ticker": ticker,
        "sku": sku_id,
        "eval": ev,
        "eval_visible": True,
    }


def format_start_telegram(lang: str = "ru") -> str:
    wf = format_wf(turnaround(lang=lang), lang=lang)
    ask = (
        "\n\n<b>Флагман.</b> Бесплатный слой. Две строки, не эссе.\n"
        "Выдаёт суть твоего вопроса и решение одной фразой.\n"
        "Потом несколько вопросов — сводка векторов результата."
    )
    return wf + ask


def format_pack_telegram(pack: dict[str, Any]) -> str:
    if pack.get("problem"):
        return format_intake(pack)
    return format_start_telegram()


def format_skus_telegram(pack: dict[str, Any]) -> str:
    s = sku_of("sku_490")
    vec = pack.get("vectors") or []
    lines = [
        f"<b>{pack.get('ticker') or ''}</b> · сводка векторов",
        "",
    ]
    for row in vec[:8]:
        lines.append(f"· <b>{row.get('k')}</b> — {row.get('v')}")
    lines.append("")
    lines.append(pack.get("paid_inside") or s.get("gets_ru") or "")
    lines.append("")
    lines.append("<b>После оплаты вы получите</b> рекурсивный файл и eval.")
    lines.append("Комбо рекурсивных решений и терминальная посадка процесса.")
    return "\n".join(lines)


def format_check_telegram(pack: dict[str, Any]) -> str:
    if not pack.get("ok"):
        return pack.get("ask") or "Сначала Флагман."
    lines = [
        "<b>Сверить файл</b> · до оплаты",
        f"Тикер <code>{pack.get('ticker')}</code>",
        "",
        f"Суть: {pack.get('problem')}",
        f"Решение: {pack.get('solution')}",
        "",
    ]
    for row in (pack.get("vectors") or [])[:8]:
        lines.append(f"· {row.get('k')}: {row.get('v')}")
    lines.append("")
    lines.append(pack.get("inside") or "")
    return "\n".join(lines)


def board(lang: str = "ru") -> dict[str, Any]:
    return tariff_board(lang)
