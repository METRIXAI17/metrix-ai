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
    {"id": "thought", "ru": "Какая мысль крутится и не садится? Напиши как есть.", "en": "Which thought loops and will not sit? Write it as it is."},
    {"id": "block", "ru": "Где самый жирный блок трудности — в голове, в людях, в кассе, в сроке?", "en": "Where is the thickest block — head, people, cash, or time?"},
    {"id": "stuck", "ru": "Где мысль застревает: в начале, в середине или на сдаче?", "en": "Where does the thought stick: start, middle, or handoff?"},
    {"id": "tried", "ru": "Что уже пробовал своими руками — и почему отпустил?", "en": "What did you already try with your hands — and why did you let it go?"},
    {"id": "fear", "ru": "Чего боишься сломать, если решение сядет?", "en": "What are you afraid of breaking if the sit lands?"},
    {"id": "easier", "ru": "Как выглядит «стало легче» одним вечером — своими словами.", "en": "What does «it got easier» look like in one evening — in your words."},
    {"id": "alone", "ru": "Ты в этом один или кто рядом, если сядет?", "en": "Are you alone in this, or who is next to you if it sits?"},
    {"id": "hard_easy", "ru": "Что в голове кажется сложным, а руками — простым? Или наоборот.", "en": "What feels hard in the head and simple in the hands? Or the other way."},
    {"id": "skip", "ru": "Какой кусок контекста мы не должны пропустить?", "en": "Which piece of context must we not skip?"},
    {"id": "vector", "ru": "Куда должен показать вектор, если коротко: касса, покой, слот, люди?", "en": "Where should the vector point, short: cash, quiet, slot, people?"},
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
    n = 5 + min(5, words // 6)
    if contour:
        n = max(n, 7)
    return max(5, min(10, n))


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
        if contour and qid in ("vector", "block", "skip", "alone"):
            boost += 4
        if any(w in t for w in ("касс", "cash", "голов", "мысл")) and qid in ("thought", "block"):
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
        "eval_visible": False,
        "paid_inside": (
            "Внутри $490: комбо рекурсивных решений и терминальная посадка процесса. Eval откроется после оплаты."
            if ru
            else "Inside $490: a combo of recursive solutions and a terminal process sit. Eval opens after pay."
        ),
        "next": (
            "Ответь своими словами — блок, мысль, трудность. Потом сводка векторов и $490."
            if ru
            else "Answer in your words — block, thought, friction. Then a vector summary and $490."
        ),
    }


def apply_answers(ticker: str, answers: dict[str, str], *, lang: str = "ru") -> dict[str, Any]:
    from backend.core.circle_system.chain_store import load_chain

    rec = load_chain(ticker) or {}
    brief = rec.get("brief") or rec.get("problem") or ""
    merged = {**(rec.get("answers") or {}), **(answers or {})}
    pack = intake(brief, lang=lang, answers=merged, ticker=ticker, subject=rec.get("subject") or "")
    return pack


def vectors_of(pack: dict[str, Any]) -> list[dict[str, str]]:
    qs = pack.get("questions") or []
    ans = pack.get("answers") or {}
    rows = [
        {"k": "суть", "v": str(pack.get("problem") or "")},
        {"k": "решение", "v": str(pack.get("solution") or "")},
    ]
    for q in qs:
        qid = q.get("id") or ""
        val = str(ans.get(qid) or "").strip()
        if val:
            rows.append({"k": q.get("text") or qid, "v": val})
    return rows


def format_telegram(pack: dict[str, Any]) -> str:
    q0 = (pack.get("questions") or [{}])[0]
    n = pack.get("question_count") or len(pack.get("questions") or [])
    lines = [
        f"<b>{pack.get('ticker') or 'MX'}</b>",
        f"Суть: {pack.get('problem')}",
        f"Решение: {pack.get('solution')}",
        "",
        pack.get("paid_inside") or "",
        "",
        pack.get("next") or "",
        "",
        f"Вопрос 1/{n}: {q0.get('text') or ''}",
    ]
    return "\n".join(lines)
