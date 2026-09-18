"""Engine G — Multi-step outcome filter (policy graph, not 100% accuracy)."""

from __future__ import annotations

from typing import Any

from backend.contours.eval_protocol import orient


def _hard_filters(candidate: dict[str, Any]) -> list[str]:
    reasons = []
    sku = str(candidate.get("recommended_offer_sku") or "")
    if sku in {"compute_broker", "cold_chain"} and candidate.get("flag_off"):
        reasons.append("flag_off")
    if candidate.get("schema_fail"):
        reasons.append("schema")
    if candidate.get("escalate"):
        reasons.append("STATE_ESCALATED")
    return reasons


def _score(candidate: dict[str, Any]) -> float:
    axes = candidate.get("axes") or {}
    err = float(axes.get("error_rate") or 0)
    esc = float(axes.get("escalation_rate") or 0)
    conf = float(candidate.get("confidence") or 0)
    return round(conf * (1 - err) * (1 - 0.5 * esc), 4)


def run(text: str, *, extra: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    primary = orient(text)
    candidates = [primary, *(extra or [])]
    kept = []
    rejected = []
    for c in candidates:
        reasons = _hard_filters(c)
        row = {**c, "score": _score(c), "reject_reasons": reasons}
        if reasons:
            rejected.append(row)
        else:
            kept.append(row)
    kept.sort(key=lambda x: x.get("score") or 0, reverse=True)
    top = kept[0] if kept else None
    escalate = (not top) or bool((top or {}).get("escalate"))
    selected = None if escalate else top
    return {
        "candidates": candidates,
        "kept": kept,
        "rejected": rejected,
        "selected": selected,
        "escalate": escalate,
        "language": "raise usable outcomes; measured rates only — never 30%→100%",
        "axes": (selected or primary).get("axes"),
    }
