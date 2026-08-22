"""Solution logger — useful analysis of one's own trading. Not signals, not advice."""

from __future__ import annotations

from typing import Any


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def run_solution_logger(
    *,
    thesis: str,
    market: str = "",
    side: str = "",
    result: str = "",
    r_multiple: float | None = None,
    notes: str = "",
    journal: list[dict[str, Any]] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """
    Log one decision (or a small journal) and extract *useful* structure:
    repeated error families, thesis quality, process — never a trade signal.
    """
    entry = {
        "thesis": (thesis or "").strip(),
        "market": market,
        "side": side,
        "result": result,
        "r_multiple": r_multiple,
        "notes": notes,
    }
    rows = list(journal or [])
    if entry["thesis"]:
        rows = rows + [entry]

    n = len(rows)
    wins = sum(1 for r in rows if str(r.get("result") or "").lower() in ("win", "+", "plus", "tp"))
    losses = sum(1 for r in rows if str(r.get("result") or "").lower() in ("loss", "-", "minus", "sl"))
    r_sum = sum(_f(r.get("r_multiple")) for r in rows)
    empty_thesis = sum(1 for r in rows if len(str(r.get("thesis") or "")) < 20)

    families: list[str] = []
    blob = " ".join(str(r.get("thesis") or "") + " " + str(r.get("notes") or "") for r in rows).lower()
    if any(k in blob for k in ("фомо", "fomo", "опоздал", "догон")):
        families.append("chase_after_move")
    if any(k in blob for k in ("усредн", "martingale", "добав")):
        families.append("averaging_without_new_thesis")
    if any(k in blob for k in ("новост", "twitter", "канал", "сигнал")):
        families.append("outsourced_thesis")
    if any(k in blob for k in ("скуч", "нечего", "просто вошёл")):
        families.append("boredom_entry")
    if empty_thesis:
        families.append("unwritten_thesis")
    if not families:
        families.append("insufficient_sample_or_clean_log")

    usefulness = 0.35
    if n >= 3:
        usefulness += 0.2
    if empty_thesis == 0 and n:
        usefulness += 0.2
    if families and families[0] != "insufficient_sample_or_clean_log":
        usefulness += 0.15
    usefulness = min(0.95, usefulness)

    next_rules = [
        "Не входить без тезиса ≥20 символов (причина, инвалидация, горизонт).",
        "Одна семья ошибок — один запрет на неделю, не десять правил.",
        "Лог полезен, когда объясняет *решение*, а не цену.",
    ]
    if "outsourced_thesis" in families:
        next_rules.insert(0, "Запрет чужого сигнала без собственной инвалидации.")
    if "chase_after_move" in families:
        next_rules.insert(0, "Вход только до импульса или по своей модели, не вдогонку.")

    path_to_orders = {
        "status": "journal_only" if n < 5 or usefulness < 0.55 else "mine_candidate",
        "note": (
            "Автоордера с журнала не стреляют, пока нет стабильного процесса. "
            "Терминал майнит *ожидающие* ордера из повторяемых тезисов — не из PnL."
        ),
        "pending_if": "n>=5 and written thesis and one error family owned",
    }
    return {
        "module": "Solution Logger",
        "function": "solution_logger",
        "disclaimer": "Decision journal. Not investment advice, not a signal.",
        "entry": entry,
        "stats": {
            "n": n,
            "wins": wins,
            "losses": losses,
            "r_sum": round(r_sum, 3),
            "empty_thesis": empty_thesis,
            "usefulness": round(usefulness, 3),
        },
        "error_families": families,
        "next_rules": next_rules,
        "path_to_orders": path_to_orders,
        "summary": f"n={n} usefulness={usefulness:.2f} families={families[:2]}",
    }
