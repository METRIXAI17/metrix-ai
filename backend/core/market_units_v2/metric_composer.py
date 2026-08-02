"""
Metric Composer — assemble core + commercial metrics into product quality index.

Composes VVI / ER / RRC with situation levers and problem pressure into
actionable PQI (Product Quality Index) and improvement forecasts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass
class ComposedMetrics:
    module: str
    vvi: float
    er: float
    rrc: float
    health: float
    situation_score: float
    coordination_index: float
    product_quality_index: float  # PQI — main outbound quality score
    clarity_index: float
    actionability_index: float
    originality_pressure: float
    deltas: dict[str, float] = field(default_factory=dict)
    levers: list[dict[str, Any]] = field(default_factory=list)
    forecast: dict[str, float] = field(default_factory=dict)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in (
            "vvi",
            "er",
            "rrc",
            "health",
            "situation_score",
            "coordination_index",
            "product_quality_index",
            "clarity_index",
            "actionability_index",
            "originality_pressure",
        ):
            d[k] = round(float(d[k]), 4)
        d["deltas"] = {k: round(float(v), 4) for k, v in (d.get("deltas") or {}).items()}
        d["forecast"] = {
            k: round(float(v), 4) for k, v in (d.get("forecast") or {}).items()
        }
        return d


class MetricComposer:
    """Compose multi-layer metrics → PQI + forecast of product quality lift."""

    name = "Metric Composer"

    def compose(
        self,
        *,
        vvi: float = 0.4,
        er: float = 0.5,
        rrc: float = 0.5,
        health: float | None = None,
        scores: dict[str, float] | None = None,
        signals: dict[str, float] | None = None,
        family_pressure: dict[str, float] | None = None,
        density: float = 0.5,
        success_composite: float = 0.5,
        situation_score: float | None = None,
        coordination_index: float = 0.5,
        primary_problem_leverage: float = 0.0,
    ) -> ComposedMetrics:
        scores = scores or {}
        signals = signals or {}
        family_pressure = family_pressure or {}

        vvi = _clamp01(vvi)
        er = _clamp01(er)
        rrc = _clamp01(rrc)
        if health is None:
            health = _clamp01((1.0 - vvi) * 0.4 + er * 0.3 + rrc * 0.3)
        else:
            health = _clamp01(health)

        overall = float(scores.get("overall_orientation", 0.5))
        product_fit = float(scores.get("product_fit", 0.5))
        readiness = float(scores.get("readiness", 0.5))

        # situation from commercial layer or synthetic
        if situation_score is None:
            cost_p = float(signals.get("cost_pressure", 0.3))
            ops_p = float(signals.get("ops_friction", 0.3))
            demand = float(signals.get("demand_signal", 0.4))
            situation_score = _clamp01(
                0.55
                + demand * 0.2
                + overall * 0.15
                - cost_p * 0.15
                - ops_p * 0.12
            )
        situation_score = _clamp01(situation_score)
        coordination_index = _clamp01(coordination_index)

        clarity = _clamp01(
            density * 0.35
            + (1.0 - vvi) * 0.3
            + product_fit * 0.2
            + readiness * 0.15
        )
        actionability = _clamp01(
            readiness * 0.3
            + er * 0.25
            + rrc * 0.2
            + coordination_index * 0.15
            + (1.0 - primary_problem_leverage) * 0.1
            + success_composite * 0.1
        )
        # originality pressure: voids + multi-family pressure invite original combos
        multi_family = min(1.0, len([v for v in family_pressure.values() if v > 0.25]) / 3.0)
        originality = _clamp01(vvi * 0.35 + multi_family * 0.35 + (1.0 - overall) * 0.15 + 0.15)

        # Product Quality Index — main outbound quality of core products
        pqi = _clamp01(
            health * 0.22
            + clarity * 0.18
            + actionability * 0.22
            + situation_score * 0.12
            + coordination_index * 0.12
            + success_composite * 0.08
            + (1.0 - min(0.5, primary_problem_leverage)) * 0.06
        )

        # expected lift if coordination + ontology layers applied
        forecast = {
            "pqi_now": pqi,
            "pqi_after_coordination": _clamp01(pqi + 0.06 + coordination_index * 0.08),
            "pqi_after_ontology": _clamp01(pqi + 0.09 + originality * 0.07),
            "pqi_after_full_v2": _clamp01(
                pqi + 0.08 + coordination_index * 0.07 + originality * 0.06 + clarity * 0.04
            ),
            "clarity_lift": _clamp01(0.05 + (1.0 - clarity) * 0.12),
            "actionability_lift": _clamp01(0.04 + (1.0 - actionability) * 0.14),
            "void_reduction": _clamp01(vvi * 0.25 + primary_problem_leverage * 0.1),
        }

        levers = [
            {
                "id": "reduce_voids",
                "weight": round(vvi, 3),
                "action": "Fill top voids via Memo Convert + SpecsForge",
            },
            {
                "id": "raise_coordination",
                "weight": round(1.0 - coordination_index, 3),
                "action": "Attach Terminal Teammate mesh + handoff matrix",
            },
            {
                "id": "compose_metrics",
                "weight": round(1.0 - success_composite, 3),
                "action": "Lock custom Success TZ before pilot",
            },
            {
                "id": "problem_primary",
                "weight": round(primary_problem_leverage, 3),
                "action": "Route offer to primary problem product_hook",
            },
        ]
        levers.sort(key=lambda x: -float(x["weight"]))

        deltas = {
            "vs_health": round(pqi - health, 4),
            "vs_situation": round(pqi - situation_score, 4),
            "forecast_full_lift": round(
                forecast["pqi_after_full_v2"] - forecast["pqi_now"], 4
            ),
        }

        return ComposedMetrics(
            module=self.name,
            vvi=vvi,
            er=er,
            rrc=rrc,
            health=health,
            situation_score=situation_score,
            coordination_index=coordination_index,
            product_quality_index=pqi,
            clarity_index=clarity,
            actionability_index=actionability,
            originality_pressure=originality,
            deltas=deltas,
            levers=levers,
            forecast=forecast,
            summary=(
                f"MetricComposer: PQI={pqi:.3f} clarity={clarity:.2f} "
                f"act={actionability:.2f} forecast_full={forecast['pqi_after_full_v2']:.3f}"
            ),
        )
