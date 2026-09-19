"""Flagship free layer: two phrases, 5–20 questions, eval, ticker, chain file."""

from __future__ import annotations

import re
from typing import Any

from backend.core.circle_system.chain_store import save_chain
from backend.core.sku_products import bake_into_output
from backend.core.ticker_registry import bind_ticker, mint_ticker
from backend.core.workflow_turnaround import turnaround
from backend.core.voice import clip, first_sentence


_LEAK = ("лом", "гор", "пуст", "туман", "не зна", "нет хозя", "сжиг", "дорог", "рутин", "слив")
_WINDOW = ("день", "недел", "понедельник", "срок", "минут", "sla", "n мин")
_WHO = ("хозяин", "кто", "owner", "нажима", "слот")


Q_BANK: list[dict[str, str]] = [
    {"id": "when", "ru": "Где ломается чаще — утром, в сдаче, в кассе?", "en": "Where does it break — morning, handoff, or cash?"},
    {"id": "who", "ru": "Кто нажимает, если объект сел?", "en": "Who presses if the object sits?"},
    {"id": "days", "ru": "Какой срок — дни, не месяцы?", "en": "What window — days, not months?"},
    {"id": "killed", "ru": "Что уже пробовали и убили?", "en": "What did you already try and kill?"},
    {"id": "dont", "ru": "Что нельзя трогать?", "en": "What must not be touched?"},
    {"id": "unit", "ru": "За какой unit уже платят?", "en": "Which unit already gets paid?"},
    {"id": "in_out", "ru": "Часы горят на in или на out?", "en": "Do hours burn on the way in or out?"},
    {"id": "monday", "ru": "Какая цифра понедельника должна появиться?", "en": "Which Monday number must appear?"},
    {"id": "library", "ru": "Какая библиотека уже в руках — не «ещё одна»?", "en": "Which library is already in hand — not another one?"},
    {"id": "slot", "ru": "Какой слот должен принять объект?", "en": "Which slot must receive the object?"},
    {"id": "rooms", "ru": "Какие комнаты уже есть — не какую линейку открыть?", "en": "Which rooms already exist — not which line to open?"},
    {"id": "silence", "ru": "Когда молчать клиенту?", "en": "When should the client be left in silence?"},
    {"id": "kill", "ru": "Какое правило убивает тезис?", "en": "Which rule kills the thesis?"},
    {"id": "owner_min", "ru": "Сколько минут на статус, пока не эскалация?", "en": "How many minutes for status before escalate?"},
    {"id": "unusual", "ru": "Какой нестандартный ход выглядел неправильно в учебнике?", "en": "Which unusual move looked wrong in the textbook?"},
    {"id": "proof", "ru": "Какой артефакт уже можно положить на стол?", "en": "Which artifact can already go on the table?"},
    {"id": "cash", "ru": "Где касса — туман, отсрочка, или нет имени у сгоревшего?", "en": "Cash: fog, delay, or burned hours without a name?"},
    {"id": "retain", "ru": "Что должно остаться тем же контуром, только плотнее?", "en": "What must stay the same contour, only denser?"},
    {"id": "web3", "ru": "Это заказ Web3 как входящий — или жизнь/касса?", "en": "Is this a Web3 inbound order — or life/cash?"},
    {"id": "file_need", "ru": "Файл после оплаты нужен — или хватит 120 коротких запросов?", "en": "Do you need the file after pay — or 120 short requests?"},
]


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _one_phrase(text: str, fallback: str, n: int = 140) -> str:
    t = first_sentence(text, fallback)
    t = re.sub(r"\s+", " ", t).strip(" .;:")
    if not t:
        t = fallback
    return clip(t, n).rstrip(".,")


def problem_phrase(brief: str, lang: str = "ru") -> str:
    ru = _lang(lang) == "ru"
    fb = "контур рвётся без хозяина" if ru else "contour tears without an owner"
    raw = (brief or "").strip()
    # first line if two-line input
    line = raw.split("\n")[0].strip() or raw
    return _one_phrase(line, fb)


def solution_phrase(brief: str, lang: str = "ru") -> str:
    ru = _lang(lang) == "ru"
    fb = "посадить объект в слот с именем и цифрой понедельника" if ru else "sit the object in a named slot with a Monday number"
    raw = (brief or "").strip()
    parts = [p.strip() for p in re.split(r"[\n;/]+", raw) if p.strip()]
    second = parts[1] if len(parts) > 1 else raw
    # if only one line, invert leak into a sit
    if len(parts) < 2:
        leak = problem_phrase(raw, lang)
        if ru:
            second = f"закрыть «{leak}» ходом в слот, не новой линейкой"
        else:
            second = f"close «{leak}» with a sit in the slot, not a new line"
    return _one_phrase(second, fb)


def _n_questions(brief: str, contour: bool) -> int:
    words = len((brief or "").split())
    n = 5 + min(15, words // 4)
    if contour:
        n = max(n, 12)
    return max(5, min(20, n))


def _is_contour(brief: str) -> bool:
    t = (brief or "").lower()
    return any(
        w in t
        for w in ("10k", "10000", "10 000", "контур", "contour", "автоном", "дизайн за", "funding")
    )


def pick_questions(brief: str, *, lang: str = "ru", n: int | None = None) -> list[dict[str, str]]:
    ru = _lang(lang) == "ru"
    contour = _is_contour(brief)
    count = n or _n_questions(brief, contour)
    t = (brief or "").lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for i, q in enumerate(Q_BANK):
        boost = 0
        qid = q["id"]
        if contour and qid in ("rooms", "retain", "monday", "owner_min", "in_out"):
            boost += 4
        if any(w in t for w in ("касс", "cash")) and qid == "cash":
            boost += 3
        if any(w in t for w in ("web3", "заказ")) and qid == "web3":
            boost += 3
        scored.append((boost * 10 + (20 - i), q))
    scored.sort(key=lambda x: -x[0])
    out = []
    seen = set()
    for _, q in scored:
        if q["id"] in seen:
            continue
        seen.add(q["id"])
        out.append({"id": q["id"], "text": q["ru"] if ru else q["en"]})
        if len(out) >= count:
            break
    return out


def eval_help(brief: str, *, answers: dict[str, str] | None = None, lang: str = "ru") -> dict[str, Any]:
    ru = _lang(lang) == "ru"
    t = (brief or "").lower()
    score = 0.34
    reasons: list[str] = []
    if any(w in t for w in _LEAK):
        score += 0.16
        reasons.append("есть именованная поломка" if ru else "named leak")
    else:
        reasons.append("поломка ещё общая" if ru else "leak still generic")
    if any(w in t for w in _WINDOW):
        score += 0.10
        reasons.append("есть окно" if ru else "window present")
    if any(w in t for w in _WHO):
        score += 0.10
        reasons.append("есть кто нажимает" if ru else "someone presses")
    if len((brief or "").split()) >= 8:
        score += 0.06
    ans = answers or {}
    filled = sum(1 for v in ans.values() if str(v).strip())
    score += min(0.18, 0.015 * filled)
    if _is_contour(brief):
        score += 0.04
        reasons.append("запрос на контур, не на чат" if ru else "contour ask, not a chat")
    score = max(0.12, min(0.93, score))
    rec = recommend_sku(brief, score)
    if score >= 0.72:
        verdict = "можем сесть в слот" if ru else "can sit in the slot"
    elif score >= 0.5:
        verdict = "можем помочь, нужны ответы" if ru else "can help, answers needed"
    else:
        verdict = "пока слабо: мало границ" if ru else "weak for now: few bounds"
    return {
        "score": round(score, 3),
        "verdict": verdict,
        "reasons": reasons[:5],
        "recommended_sku": rec,
        "answers_filled": filled,
    }


def recommend_sku(brief: str, score: float) -> str:
    t = (brief or "").lower()
    if any(w in t for w in ("10k", "10000", "10 000", "автоном", "contour", "контур в")):
        return "sku_10000"
    if any(w in t for w in ("120", "мелк", "подписк", "small task")):
        return "sku_100"
    if any(w in t for w in ("стандарт", "standard", "методик", "спек")):
        return "sku_1000"
    if any(w in t for w in ("assist", "490", "слот", "библиотек")):
        return "sku_490"
    if score < 0.48:
        return "sku_100"
    if score < 0.68:
        return "sku_490"
    return "sku_1000"


def intake(
    brief: str,
    *,
    lang: str = "ru",
    answers: dict[str, str] | None = None,
    ticker: str | None = None,
    subject: str = "",
) -> dict[str, Any]:
    ru = _lang(lang) == "ru"
    problem = problem_phrase(brief, lang)
    solution = solution_phrase(brief, lang)
    contour = _is_contour(brief)
    questions = pick_questions(brief, lang=lang)
    ev = eval_help(brief, answers=answers, lang=lang)
    tick = ticker or mint_ticker(problem)
    wf = turnaround(lang=lang, contour=contour)
    rec_sku = ev["recommended_sku"]
    skus = bake_into_output(brief, recommended=rec_sku, lang=lang, ticker=tick)
    chain = {
        "chain_id": tick,
        "ticker": tick,
        "brief": (brief or "").strip()[:4000],
        "problem": problem,
        "solution": solution,
        "questions": questions,
        "answers": dict(answers or {}),
        "eval": ev,
        "lang": lang,
        "subject": subject[:64] if subject else "",
        "contour": contour,
        "recommended_sku": rec_sku,
        "workflow": wf,
        "skus": skus,
        "layer": "free_life",
    }
    saved = save_chain(chain)
    bind_ticker(tick, problem=problem, solution=solution, sku=rec_sku, eval=ev["score"])
    return {
        "ok": True,
        "free": True,
        "ticker": tick,
        "problem": problem,
        "solution": solution,
        "questions": questions,
        "question_count": len(questions),
        "eval": ev,
        "workflow": wf,
        "skus": skus,
        "recommended_sku": rec_sku,
        "chain_id": saved.get("chain_id") or tick,
        "contour": contour,
        "next": (
            "Ответьте на вопросы по одному. Потом — тариф. Файл после оплаты, кроме $100."
            if ru
            else "Answer the questions one by one. Then a tariff. File after pay, except $100."
        ),
    }


def apply_answers(ticker: str, answers: dict[str, str], *, lang: str = "ru") -> dict[str, Any]:
    from backend.core.circle_system.chain_store import load_chain

    rec = load_chain(ticker) or {}
    brief = rec.get("brief") or rec.get("problem") or ""
    merged = {**(rec.get("answers") or {}), **(answers or {})}
    pack = intake(brief, lang=lang, answers=merged, ticker=ticker, subject=rec.get("subject") or "")
    return pack


def format_telegram(pack: dict[str, Any]) -> str:
    ev = pack.get("eval") or {}
    q0 = (pack.get("questions") or [{}])[0]
    n = pack.get("question_count") or len(pack.get("questions") or [])
    score = float(ev.get("score") or 0)
    lines = [
        f"<b>{pack.get('ticker') or 'MX'}</b>",
        f"Суть: {pack.get('problem')}",
        f"Решение: {pack.get('solution')}",
        f"Eval: {score:.0%} — {ev.get('verdict') or ''}",
        "",
        pack.get("next") or "",
        "",
        f"Вопрос 1/{n}: {q0.get('text') or ''}",
    ]
    return "\n".join(lines)
