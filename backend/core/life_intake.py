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


# Operating level is normal. Max is the older abstract bank — kept, not the default.
QUESTION_LEVELS = ("surface", "normal", "max")
OPERATING_QUESTION_LEVEL = "normal"

# Normal: one concrete answer each. These are the questions the system asks.
NORMAL_BANK: list[dict[str, str]] = [
    {"id": "bound", "cat": "суть", "level": "normal", "ru": "Что ломается — одним предметом, как вы это называете?", "en": "What breaks — name it as one object?"},
    {"id": "keep", "cat": "граница", "level": "normal", "ru": "Что остаётся вашим и не уходит в чужой контур?", "en": "What stays yours and does not leave into someone else's contour?"},
    {"id": "slot", "cat": "слот", "level": "normal", "ru": "Куда это садится в вашем проекте на этой неделе?", "en": "Where does this sit in your project this week?"},
    {"id": "owner", "cat": "хозяин", "level": "normal", "ru": "Кто нажимает в понедельник?", "en": "Who presses on Monday?"},
    {"id": "window", "cat": "окно", "level": "normal", "ru": "Какая цифра или срок делает это фактом?", "en": "Which number or date makes this a fact?"},
    {"id": "hands", "cat": "руки", "level": "normal", "ru": "Что уже сделали руками и отпустили?", "en": "What did you already do with your hands and then drop?"},
    {"id": "kill_b2b", "cat": "контур", "level": "normal", "ru": "Это ваш контур или работа для чужого бизнеса?", "en": "Is this your contour, or work for someone else's business?"},
    {"id": "pick", "cat": "вариант", "level": "normal", "ru": "Какой ход ближе: граница, слот, спека или рекурсия?", "en": "Which move is closer: bound, slot, spec, or recursion?"},
]

# Max: abstract. Available when a caller asks level=max. Not the operating state.
Q_BANK: list[dict[str, str]] = [
    {"id": "thought", "cat": "мысль", "level": "max", "ru": "Какая мысль крутится и не садится? Напиши как есть.", "en": "Which thought loops and will not sit? Write it as it is."},
    {"id": "block", "cat": "блок", "level": "max", "ru": "Где самый жирный блок трудности — в голове, в людях, в кассе, в сроке?", "en": "Where is the thickest block — head, people, cash, or time?"},
    {"id": "stuck", "cat": "застревание", "level": "max", "ru": "Где мысль застревает: в начале, в середине или на сдаче?", "en": "Where does the thought stick: start, middle, or handoff?"},
    {"id": "tried", "cat": "попытка", "level": "max", "ru": "Что уже пробовал своими руками — и почему отпустил?", "en": "What did you already try with your hands — and why did you let it go?"},
    {"id": "fear", "cat": "страх", "level": "max", "ru": "Чего боишься сломать, если решение сядет?", "en": "What are you afraid of breaking if the sit lands?"},
    {"id": "easier", "cat": "облегчение", "level": "max", "ru": "Как выглядит «стало легче» одним вечером — своими словами.", "en": "What does «it got easier» look like in one evening — in your words."},
    {"id": "alone", "cat": "рядом", "level": "max", "ru": "Ты в этом один или кто рядом, если сядет?", "en": "Are you alone in this, or who is next to you if it sits?"},
    {"id": "hard_easy", "cat": "голова", "level": "max", "ru": "Что в голове кажется сложным, а руками — простым? Или наоборот.", "en": "What feels hard in the head and simple in the hands? Or the other way."},
    {"id": "skip", "cat": "контекст", "level": "max", "ru": "Какой кусок контекста мы не должны пропустить?", "en": "Which piece of context must we not skip?"},
    {"id": "vector", "cat": "вектор", "level": "max", "ru": "Куда должен показать вектор, если коротко: касса, покой, слот, люди?", "en": "Where should the vector point, short: cash, quiet, slot, people?"},
]

_WEB3_MARKERS = ("жертв", "web3", "ончейн", "on-chain", "токен", "wallet", "nft", "смарт-контракт")


def question_system_state() -> dict[str, Any]:
    """Max level stays in the bank. The system asks at normal."""
    return {
        "module": "QuestionLevels",
        "operating_level": OPERATING_QUESTION_LEVEL,
        "max_level": "max",
        "levels": list(QUESTION_LEVELS),
        "normal_categories": [q["cat"] for q in NORMAL_BANK],
        "max_categories": [q["cat"] for q in Q_BANK],
        "note": "Максимальный уровень — абстрактный банк. Рабочее состояние — normal: конкретный вопрос на категорию.",
    }


def cycle_section(brief: str, explicit: str | None = None) -> str:
    raw = (explicit or "").strip().lower()
    if raw in ("web3", "store", "web3 store"):
        return "web3"
    if raw in ("flagship", "life", "tariffs", "hits"):
        if raw == "flagship":
            # A concept that belongs in Web3 still moves, even if the door was Flagship.
            if any(w in (brief or "").lower() for w in _WEB3_MARKERS):
                return "web3"
        return "web3" if raw == "store" else raw
    if any(w in (brief or "").lower() for w in _WEB3_MARKERS):
        return "web3"
    return "flagship"


def _concept(brief: str) -> dict[str, str] | None:
    """A named notion gets a sit with fields a small task can fill.

    The phrase is the public line. give/keep/library/owner/monday are the spec.
    """
    t = (brief or "").lower()
    if "жертв" in t:
        return {
            "problem": "Жертвенность отдаёт свой объект без названной границы",
            "solution": "Web3-слот своего контура: единица отдачи, граница, хозяин, цифра",
            "give": "время, код или имя, которое уходит из контура",
            "keep": "имя хозяина, касса и право остановить отдачу",
            "room": "Web3 Store · Quality",
            "library": "карточка границы отдачи",
            "owner": "хозяин этого тикера",
            "monday": "граница записана и слот в Web3 открыт",
            "kill": "сборка агентства под чужих клиентов",
        }
    return None


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _one_phrase(text: str, fallback: str, n: int = 140) -> str:
    t = first_sentence(text, fallback)
    t = re.sub(r"\s+", " ", t).strip(" .;:")
    if not t:
        t = fallback
    return clip(t, n).rstrip(".,")


def problem_phrase(brief: str, lang: str = "ru") -> str:
    concept = _concept(brief)
    if concept and _lang(lang) == "ru":
        return concept["problem"]
    ru = _lang(lang) == "ru"
    fb = "контур рвётся без хозяина" if ru else "contour tears without an owner"
    raw = (brief or "").strip()
    # first line if two-line input
    line = raw.split("\n")[0].strip() or raw
    return _one_phrase(line, fb)


def solution_phrase(brief: str, lang: str = "ru") -> str:
    concept = _concept(brief)
    if concept and _lang(lang) == "ru":
        return concept["solution"]
    ru = _lang(lang) == "ru"
    fb = "посадить объект в слот с именем и цифрой понедельника" if ru else "sit the object in a named slot with a Monday number"
    raw = (brief or "").strip()
    parts = [p.strip() for p in re.split(r"[\n;/]+", raw) if p.strip()]
    second = parts[1] if len(parts) > 1 else raw
    # if only one line, invert leak into a sit on their contour
    if len(parts) < 2:
        leak = problem_phrase(raw, lang)
        if ru:
            second = f"закрыть «{leak}» ходом в свой слот, не в чужой бизнес"
        else:
            second = f"close «{leak}» in your slot, not in someone else's business"
    return _one_phrase(second, fb)


def small_task_variants(
    problem: str,
    solution: str,
    *,
    section: str,
    lang: str = "ru",
    sit: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """Several sits. Each one is a small task with a done-line. $100 specs them, $490 recurses one."""
    ru = _lang(lang) == "ru"
    s = sit or {}
    give = s.get("give") or ("что уходит из контура" if ru else "what leaves the contour")
    keep = s.get("keep") or ("что остаётся у хозяина" if ru else "what stays with the owner")
    room = s.get("room") or ("Web3 Store" if section == "web3" else "Флагман")
    library = s.get("library") or ("карточка границы" if ru else "bound card")
    owner = s.get("owner") or ("хозяин слота" if ru else "slot owner")
    monday = s.get("monday") or ("граница записана" if ru else "bound is written")
    kill = s.get("kill") or ("сборка чужого бизнеса" if ru else "a business built for other people")
    if ru:
        rows = [
            ("v_bound", "Единица отдачи", f"Записать два поля: отдают «{give}»; остаётся «{keep}».", "Оба поля есть в спеке.", "sku_100"),
            ("v_slot", "Слот", f"Открыть комнату {room} и посадить туда единицу отдачи.", "У комнаты есть имя и объект.", "sku_100"),
            ("v_spec", "Кастом спека", f"Собрать четыре поля: отдача, граница, {owner}, цифра.", "Спека $100 открывается без пустых полей.", "sku_100"),
            ("v_recurse", "Рекурсия", f"Разложить слот: граница → kill «{kill}» → {library} → {monday}.", "В файле $490 четыре шага заполнены этим тикером.", "sku_490"),
            ("v_kill", "Свой контур", f"Закрыть ход «{kill}» отдельной карточкой.", "Карточка kill лежит рядом со спекой.", "sku_100"),
        ]
    else:
        rows = [
            ("v_bound", "Unit of giving", f"Write two fields: given «{give}»; kept «{keep}».", "Both fields are in the spec.", "sku_100"),
            ("v_slot", "Slot", f"Open {room} and sit the unit there.", "The room has a name and an object.", "sku_100"),
            ("v_spec", "Custom spec", f"Four fields: give, bound, {owner}, number.", "The $100 spec opens with those fields filled.", "sku_100"),
            ("v_recurse", "Recursion", f"Unfold: bound → kill «{kill}» → {library} → {monday}.", "The $490 file has four steps filled for this ticker.", "sku_490"),
            ("v_kill", "Own contour", f"Close «{kill}» on its own card.", "The kill card sits next to the spec.", "sku_100"),
        ]
    return [
        {"id": i, "title": title, "task": task, "done": done, "sku": sku}
        for i, title, task, done, sku in rows
    ]


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


def pick_questions(
    brief: str,
    *,
    lang: str = "ru",
    n: int | None = None,
    level: str | None = None,
) -> list[dict[str, str]]:
    ru = _lang(lang) == "ru"
    contour = _is_contour(brief)
    count = n or _n_questions(brief, contour)
    use = (level or OPERATING_QUESTION_LEVEL).lower()
    if use not in QUESTION_LEVELS:
        use = OPERATING_QUESTION_LEVEL
    bank = Q_BANK if use == "max" else NORMAL_BANK
    t = (brief or "").lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for i, q in enumerate(bank):
        boost = 0
        qid = q["id"]
        if contour and qid in ("slot", "owner", "window", "vector", "block"):
            boost += 3
        if any(w in t for w in _WEB3_MARKERS) and qid in ("keep", "kill_b2b", "pick", "slot"):
            boost += 4
        if any(w in t for w in ("касс", "cash")) and qid in ("bound", "window", "owner"):
            boost += 2
        scored.append((boost * 10 + (20 - i), q))
    scored.sort(key=lambda x: -x[0])
    out = []
    seen = set()
    for _, q in scored:
        if q["id"] in seen:
            continue
        seen.add(q["id"])
        out.append(
            {
                "id": q["id"],
                "cat": q.get("cat") or q["id"],
                "level": q.get("level") or use,
                "text": q["ru"] if ru else q["en"],
            }
        )
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
    if any(w in t for w in ("120", "мелк", "подписк", "small task", "кастом", "спек", "custom spec")):
        return "sku_100"
    if any(w in t for w in ("рекурс", "assist", "490")):
        return "sku_490"
    if any(w in t for w in ("стандарт", "standard", "методик")):
        return "sku_1000"
    if any(w in t for w in ("слот", "библиотек")):
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
    section: str | None = None,
    question_level: str | None = None,
) -> dict[str, Any]:
    ru = _lang(lang) == "ru"
    problem = problem_phrase(brief, lang)
    solution = solution_phrase(brief, lang)
    sit = _concept(brief) or {}
    contour = _is_contour(brief)
    level = question_level or OPERATING_QUESTION_LEVEL
    questions = pick_questions(brief, lang=lang, level=level)
    ev = eval_help(brief, answers=answers, lang=lang)
    sec = cycle_section(brief, section)
    variants = small_task_variants(problem, solution, section=sec, lang=lang, sit=sit or None)
    try:
        from backend.core.business_gen.client_segmentation import segment_client

        seg = segment_client(brief, lang=lang)
    except Exception:  # noqa: BLE001
        seg = {}
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
        "cycle_section": sec,
        "section_fix": (
            "Раздел цикла — Web3 Store. Запрос сидел не там."
            if sec == "web3" and (section or "").lower() in ("", "flagship", "life")
            else ""
        ),
        "question_level": level,
        "variants": variants,
        "sit": sit,
        "frame": seg.get("frame") or ("web3_order" if sec == "web3" else "own_contour"),
        "eternal_b2b": bool(seg.get("eternal_b2b")),
        "modern": seg.get("modern") or [],
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
        "cycle_section": sec,
        "section_fix": chain["section_fix"],
        "question_level": level,
        "variants": variants,
        "sit": chain.get("sit") or {},
        "frame": chain["frame"],
        "eternal_b2b": chain.get("eternal_b2b"),
        "modern": chain.get("modern") or [],
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
    pack = intake(
        brief,
        lang=lang,
        answers=merged,
        ticker=ticker,
        subject=rec.get("subject") or "",
        section=rec.get("cycle_section") or None,
        question_level=rec.get("question_level") or None,
    )
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
    vars_ = pack.get("variants") or []
    var_line = " · ".join(v.get("title") or "" for v in vars_[:5])
    lines = [
        f"<b>{pack.get('ticker') or 'MX'}</b>",
        f"Раздел: {'Web3 Store' if pack.get('cycle_section') == 'web3' else 'Флагман'}",
        f"Суть: {pack.get('problem')}",
        f"Решение: {pack.get('solution')}",
        f"Варианты: {var_line}",
        "",
        pack.get("paid_inside") or "",
        "",
        pack.get("next") or "",
        "",
        f"Вопрос 1/{n}: {q0.get('text') or ''}",
    ]
    return "\n".join(lines)
