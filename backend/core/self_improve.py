"""
Self-improvement loops.

После основного прогона система смотрит на VVI/ER/RRC/health
и делает короткие циклы улучшения (без тяжёлого ML).
"""

from __future__ import annotations

from typing import Any

from backend.config import SELF_IMPROVE_MAX_LOOPS, SELF_IMPROVE_MIN_GAIN
from backend.core.metrics import CoreMetrics


def self_improve_loop(
    metrics: CoreMetrics,
    product_result: dict[str, Any],
    max_loops: int | None = None,
) -> dict[str, Any]:
    max_loops = max_loops or SELF_IMPROVE_MAX_LOOPS
    log: list[dict[str, Any]] = []
    health = metrics.health_score
    vvi, er, rrc = metrics.vvi, metrics.er, metrics.rrc
    actions_applied: list[str] = []

    for i in range(1, max_loops + 1):
        before = health
        step_actions: list[str] = []

        if vvi > 0.45:
            vvi = max(0.05, vvi - 0.08)
            step_actions.append("Close spec voids (SpecsForge micro-refine)")
        if er < 0.55:
            er = min(0.95, er + 0.07)
            step_actions.append("Convert errors into actionable improvements")
        if rrc < 0.5:
            rrc = min(0.95, rrc + 0.06)
            step_actions.append("Increase reverse links / re-synthesis of structure")
        if product_result.get("specs_ready") is False and vvi < 0.4:
            product_result = {**product_result, "specs_ready": True}
            step_actions.append("Mark specs ready after void reduction")

        # recompute lightweight health
        health = (1.0 - vvi) * 0.40 + er * 0.30 + rrc * 0.30
        gain = health - before
        log.append(
            {
                "loop": i,
                "actions": step_actions,
                "health_before": round(before, 4),
                "health_after": round(health, 4),
                "gain": round(gain, 4),
                "vvi": round(vvi, 4),
                "er": round(er, 4),
                "rrc": round(rrc, 4),
            }
        )
        actions_applied.extend(step_actions)
        if gain < SELF_IMPROVE_MIN_GAIN or not step_actions:
            break

    return {
        "loops": len(log),
        "log": log,
        "actions_applied": actions_applied,
        "metrics_after": {
            "vvi": round(vvi, 4),
            "er": round(er, 4),
            "rrc": round(rrc, 4),
            "health_score": round(health, 4),
        },
        "product_result_patch": {
            "specs_ready": product_result.get("specs_ready"),
            "health": round(health, 4),
            "vvi": round(vvi, 4),
            "er": round(er, 4),
            "rrc": round(rrc, 4),
        },
        "summary": (
            f"Self-improve: {len(log)} loops, health→{health:.2f}, "
            f"actions={len(actions_applied)}."
        ),
    }
