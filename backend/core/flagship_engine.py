"""Flagship conversation: free turnaround → intake → answers → SKU → file."""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.chain_store import load_chain
from backend.core.design_contour import analyze as analyze_contour
from backend.core.life_intake import apply_answers, format_telegram as format_intake
from backend.core.life_intake import intake
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
        answers[qid] = (text or "").strip()[:400]
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
        pack["prompt"] = pack.get("next") or "Вопросы закрыты. Выберите тариф."
    return pack


def fulfill(ticker: str, sku_id: str, *, lang: str = "ru") -> dict[str, Any]:
    rec = load_chain(ticker) or {}
    product = create_product(
        ticker=ticker,
        solution=rec.get("solution") or "",
        sku_id=sku_id,
        problem=rec.get("problem") or "",
    )
    paid = generate_paid_file(ticker, sku_id=sku_id, lang=lang)
    return {"ok": True, "product": product, "file": paid, "ticker": ticker, "sku": sku_id}


def format_start_telegram(lang: str = "ru") -> str:
    wf = format_wf(turnaround(lang=lang), lang=lang)
    ask = (
        "\n\n<b>Флагман.</b> Две строки, не эссе.\n"
        "Что ломается — одной фразой.\nЧто должно сесть — второй."
    )
    return wf + ask


def format_pack_telegram(pack: dict[str, Any]) -> str:
    if pack.get("problem"):
        return format_intake(pack)
    return format_start_telegram()


def format_skus_telegram(pack: dict[str, Any]) -> str:
    rec = pack.get("recommended_sku") or "sku_490"
    lines = ["<b>Тариф под эту цепочку</b>", f"Тикер <code>{pack.get('ticker')}</code>", ""]
    for c in (pack.get("skus") or {}).get("cards") or []:
        mark = " ←" if c.get("id") == rec or c.get("recommended") else ""
        file_note = "файл" if c.get("file") else "без файла"
        lines.append(f"<b>${c.get('usd')}</b> · {c.get('name_ru')} · {file_note}{mark}")
        lines.append(c.get("move") or c.get("gets_ru") or "")
        lines.append("")
    lines.append("Хиты смотреть бесплатно. Web3 Store — запросы бесплатно.")
    return "\n".join(lines)


def board(lang: str = "ru") -> dict[str, Any]:
    return tariff_board(lang)
