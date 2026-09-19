"""Eval suite for Flagship product generation. Threshold 0.72. Do not lower it — fix the overlay."""

from __future__ import annotations

import ast
import re
from typing import Any

from backend.core.code_overlay import inspect_overlay
from backend.core.flagship_engine import start
from backend.core.life_intake import intake
from backend.core.product_file import generate_paid_file
from backend.core.workflow_turnaround import turnaround

THRESHOLD = 0.72

GOLD: list[dict[str, Any]] = [
    {
        "id": "life_cash",
        "brief": "Касса как туман, понедельник пустой.\nНужен хозяин и цифра.",
        "sku": "sku_490",
        "expect_file": True,
    },
    {
        "id": "saas_ops",
        "brief": "SaaS 80 человек, фичи пилим, никто не знает что считается победой.\nПосадить слот с именем.",
        "sku": "sku_1000",
        "expect_file": True,
    },
    {
        "id": "contour_10k",
        "brief": "Нужен автономный контур в наш проект, дизайн за 10k. Комнаты уже есть.",
        "sku": "sku_10000",
        "expect_file": True,
    },
    {
        "id": "micro_100",
        "brief": "Мелкие задачи, подписка 120 запросов, без файла.",
        "sku": "sku_100",
        "expect_file": False,
    },
]

CLICHE = (
    "в современном мире",
    "комплексный подход",
    "синерг",
    "готовое решение под ключ",
    "уникальное ценностное предложение",
)


def _clip_score(n: float) -> float:
    return max(0.0, min(1.0, n))


def score_intake(pack: dict[str, Any]) -> dict[str, Any]:
    axes: dict[str, float] = {}
    problem = pack.get("problem") or ""
    solution = pack.get("solution") or ""
    axes["problem_len"] = 1.0 if 8 <= len(problem) <= 160 else 0.2
    axes["solution_len"] = 1.0 if 8 <= len(solution) <= 180 else 0.2
    nq = int(pack.get("question_count") or len(pack.get("questions") or []))
    axes["questions"] = 1.0 if 5 <= nq <= 20 else 0.0
    axes["ticker"] = 1.0 if str(pack.get("ticker") or "").startswith("MX-") else 0.0
    axes["chain"] = 1.0 if pack.get("chain_id") else 0.0
    ev = pack.get("eval") or {}
    sc = float(ev.get("score") or 0)
    axes["eval_calibrated"] = 1.0 if 0.12 <= sc <= 0.93 else 0.3
    cards = ((pack.get("skus") or {}).get("cards") or [])
    ids = {c.get("id") for c in cards}
    axes["skus_baked"] = 1.0 if {"sku_100", "sku_490", "sku_1000"} <= ids else 0.2
    wf = pack.get("workflow") or {}
    axes["workflow"] = 1.0 if len(wf.get("steps") or []) >= 5 else 0.2
    blob = f"{problem} {solution}".lower()
    axes["no_cliche"] = 0.0 if any(c in blob for c in CLICHE) else 1.0
    mean = sum(axes.values()) / len(axes)
    return {"score": round(mean, 3), "axes": axes, "go": mean >= THRESHOLD}


def score_file(paid: dict[str, Any], *, expect_file: bool) -> dict[str, Any]:
    if not expect_file:
        ok = paid.get("file") is False or paid.get("reason") == "sku_100_no_file"
        return {"score": 1.0 if ok else 0.0, "axes": {"no_file": 1.0 if ok else 0.0}, "go": ok}
    src = paid.get("source") or ""
    q = paid.get("quality") or inspect_overlay(src, ticker=str(paid.get("ticker") or ""))
    axes = {
        "syntax": 1.0 if "syntax_ok" in (q.get("reasons") or []) else 0.0,
        "overlay": 1.0 if q.get("go") else float(q.get("score") or 0),
        "recurse": 1.0 if "recurse" in (q.get("reasons") or []) else 0.0,
        "method": 1.0 if "рекурсив" in (paid.get("methodology") or "").lower() or "recurs" in (paid.get("methodology") or "").lower() else 0.2,
        "path": 1.0 if (paid.get("py_path") or (paid.get("paths") or {}).get("py")) else 0.0,
    }
    try:
        ast.parse(src)
        axes["ast"] = 1.0
    except SyntaxError:
        axes["ast"] = 0.0
    if re.search(r"\bTODO\b|NotImplemented", src):
        axes["no_stub"] = 0.0
    else:
        axes["no_stub"] = 1.0
    mean = sum(axes.values()) / len(axes)
    return {"score": round(mean, 3), "axes": axes, "go": mean >= THRESHOLD and axes.get("ast") == 1.0}


def eval_brief(case: dict[str, Any]) -> dict[str, Any]:
    pack = intake(case["brief"], lang="ru")
    s1 = score_intake(pack)
    ticker = pack.get("ticker") or ""
    if case.get("expect_file"):
        paid = generate_paid_file(ticker, sku_id=case.get("sku") or "sku_490")
    else:
        paid = generate_paid_file(ticker, sku_id="sku_100")
    s2 = score_file(paid, expect_file=bool(case.get("expect_file")))
    mean = (s1["score"] * 0.45) + (s2["score"] * 0.55)
    return {
        "id": case["id"],
        "ticker": ticker,
        "intake": s1,
        "file": s2,
        "score": round(mean, 3),
        "go": s1["go"] and s2["go"] and mean >= THRESHOLD,
        "recommended": pack.get("recommended_sku"),
    }


def run_suite() -> dict[str, Any]:
    rows = [eval_brief(c) for c in GOLD]
    scores = [r["score"] for r in rows]
    mean = sum(scores) / len(scores) if scores else 0.0
    hard_fail = [r["id"] for r in rows if not r["go"]]
    wf = turnaround(lang="ru")
    start_pack = start("Касса пустая, нет хозяина", lang="ru")
    return {
        "module": "ProductEval",
        "threshold": THRESHOLD,
        "mean": round(mean, 3),
        "go": mean >= THRESHOLD and not hard_fail,
        "hard_fail": hard_fail,
        "cases": rows,
        "workflow_steps": len(wf.get("steps") or []),
        "start_has_ticker": bool(start_pack.get("ticker")),
    }
