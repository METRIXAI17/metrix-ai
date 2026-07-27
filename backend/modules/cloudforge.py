"""
CloudForge Precision Optimizer

Оптимизация вычислений *под конкретный продукт*:
precision, speed, resource efficiency — динамическая настройка
в контексте продукта.

Market Units 2026-07-26: primary application for cloud-economy /
productive-creativity founders = cut third-party API spend while
keeping quality (Expert path). Preserves unit-economics + placement levers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import (
    CLOUD_DEFAULT_BUDGET_UNITS,
    CLOUD_PRECISION_WEIGHT,
    CLOUD_RESOURCE_WEIGHT,
    CLOUD_SPEED_WEIGHT,
)
from backend.core.metrics import CoreMetrics, compute_core_metrics


@dataclass
class CloudWorkload:
    """Описание вычислительной нагрузки продукта."""

    name: str
    ops_estimate: float          # условные операции
    precision_need: float        # 0..1
    latency_budget_ms: float
    memory_units: float
    parallelism: float = 1.0
    edge_eligible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CloudPlan:
    placement: str               # edge | regional | core
    batch_size: int
    precision_mode: str          # full | mixed | approximate
    cache_policy: str
    replica_factor: float
    estimated_latency_ms: float
    estimated_cost_units: float
    quality_score: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CloudOptimizeResult:
    product_context: str
    workload: dict[str, Any]
    plan: CloudPlan
    before: dict[str, float]
    after: dict[str, float]
    gains: dict[str, float]
    metrics: CoreMetrics
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "CloudForge Precision Optimizer",
            "product_context": self.product_context,
            "workload": self.workload,
            "plan": self.plan.to_dict(),
            "before": self.before,
            "after": self.after,
            "gains": self.gains,
            "metrics": self.metrics.to_dict(),
            "summary": self.summary,
        }


class CloudForgePrecisionOptimizer:
    name = "CloudForge Precision Optimizer"

    def optimize(
        self,
        product_context: str,
        workload: CloudWorkload | None = None,
        budget_units: float | None = None,
        orientation_scores: dict[str, float] | None = None,
    ) -> CloudOptimizeResult:
        budget = budget_units or CLOUD_DEFAULT_BUDGET_UNITS
        orientation_scores = orientation_scores or {}
        wl = workload or self._default_workload(product_context, orientation_scores)

        # Baseline (naive cloud)
        base_latency = max(20.0, wl.ops_estimate / max(1.0, wl.parallelism) * 0.05)
        base_cost = wl.ops_estimate * 0.02 + wl.memory_units * 0.1
        base_precision = min(1.0, 0.55 + wl.precision_need * 0.4)
        base_speed = min(1.0, wl.latency_budget_ms / max(base_latency, 1.0))
        base_resource = min(1.0, budget / max(base_cost, 1.0))

        before = {
            "precision": round(base_precision, 4),
            "speed_index": round(min(1.0, base_speed), 4),
            "resource_efficiency": round(min(1.0, base_resource), 4),
            "latency_ms": round(base_latency, 2),
            "cost_units": round(base_cost, 2),
        }

        plan = self._build_plan(wl, budget, orientation_scores)

        after_latency = plan.estimated_latency_ms
        after_cost = plan.estimated_cost_units
        after_precision = plan.quality_score
        after_speed = min(1.0, wl.latency_budget_ms / max(after_latency, 1.0))
        after_resource = min(1.0, budget / max(after_cost, 1.0))

        after = {
            "precision": round(after_precision, 4),
            "speed_index": round(after_speed, 4),
            "resource_efficiency": round(after_resource, 4),
            "latency_ms": round(after_latency, 2),
            "cost_units": round(after_cost, 2),
        }

        # composite product quality under context
        w_p, w_s, w_r = CLOUD_PRECISION_WEIGHT, CLOUD_SPEED_WEIGHT, CLOUD_RESOURCE_WEIGHT
        before_q = before["precision"] * w_p + before["speed_index"] * w_s + before["resource_efficiency"] * w_r
        after_q = after["precision"] * w_p + after["speed_index"] * w_s + after["resource_efficiency"] * w_r

        gains = {
            "precision": round(after["precision"] - before["precision"], 4),
            "speed_index": round(after["speed_index"] - before["speed_index"], 4),
            "resource_efficiency": round(after["resource_efficiency"] - before["resource_efficiency"], 4),
            "composite_quality": round(after_q - before_q, 4),
            "latency_reduction_ms": round(before["latency_ms"] - after["latency_ms"], 2),
            "cost_reduction_units": round(before["cost_units"] - after["cost_units"], 2),
        }

        # map cloud quality into core metrics language
        metrics = compute_core_metrics(
            known_params=8,
            required_params=10,
            ambiguity_score=max(0.0, 1.0 - after_precision),
            conflict_score=0.05,
            missing_critical=0 if after_precision > 0.7 else 1,
            detected_errors=2 if gains["composite_quality"] < 0 else 1,
            actionable_errors=1,
            improvement_delta=max(0.0, gains["composite_quality"]),
            fragments=4,
            successful_reassemblies=3 if plan.placement == "edge" else 2,
            structure_entropy=0.48,
            reverse_links=2,
            forward_links=3,
            notes=[f"cloud plan placement={plan.placement}"],
        )

        # API-cost collapse narrative (valuable data kept for Expert path)
        api_spend_before = round(before["cost_units"] * 1.35, 2)
        api_spend_after = round(after["cost_units"] * 0.55, 2)
        gains = {
            **gains,
            "third_party_api_units_before": api_spend_before,
            "third_party_api_units_after": api_spend_after,
            "third_party_api_reduction": round(api_spend_before - api_spend_after, 2),
            "expert_path_note": (
                "Prefer Expert / local metrix path over pure third-party LLM API swarms"
            ),
        }

        summary = (
            f"{self.name} for «{product_context}»: "
            f"{plan.placement}/{plan.precision_mode}, "
            f"latency {before['latency_ms']:.0f}→{after['latency_ms']:.0f}ms, "
            f"cost {before['cost_units']:.1f}→{after['cost_units']:.1f}, "
            f"API-units {api_spend_before:.1f}→{api_spend_after:.1f}, "
            f"Δquality={gains['composite_quality']:+.3f}."
        )

        return CloudOptimizeResult(
            product_context=product_context,
            workload=wl.to_dict(),
            plan=plan,
            before=before,
            after=after,
            gains=gains,
            metrics=metrics,
            summary=summary,
        )

    def _default_workload(
        self,
        product_context: str,
        scores: dict[str, float],
    ) -> CloudWorkload:
        complexity = scores.get("model_fit", 0.5)
        urgency = scores.get("promo_fit", 0.4)
        return CloudWorkload(
            name=f"wl_{product_context[:32]}",
            ops_estimate=800 + complexity * 2200,
            precision_need=0.45 + complexity * 0.4,
            latency_budget_ms=120 if urgency > 0.55 else 250,
            memory_units=20 + complexity * 40,
            parallelism=2.0 + complexity * 4.0,
            edge_eligible=urgency > 0.4,
        )

    def _build_plan(
        self,
        wl: CloudWorkload,
        budget: float,
        scores: dict[str, float],
    ) -> CloudPlan:
        notes: list[str] = []

        # Placement
        if wl.edge_eligible and wl.latency_budget_ms <= 150:
            placement = "edge"
            notes.append("Edge placement: decision near data / user")
            lat_factor = 0.45
            cost_factor = 0.85
        elif wl.ops_estimate > 2500:
            placement = "core"
            notes.append("Core placement: heavy ops, batch-friendly")
            lat_factor = 1.15
            cost_factor = 0.70
        else:
            placement = "regional"
            notes.append("Regional placement: balanced")
            lat_factor = 0.75
            cost_factor = 0.80

        # Precision mode vs product need
        if wl.precision_need >= 0.8:
            precision_mode = "full"
            prec_score = 0.92
            cost_factor *= 1.15
            notes.append("Full precision — product quality critical")
        elif wl.precision_need >= 0.5:
            precision_mode = "mixed"
            prec_score = 0.82
            cost_factor *= 0.95
            notes.append("Mixed precision — quality/speed trade")
        else:
            precision_mode = "approximate"
            prec_score = 0.70
            cost_factor *= 0.80
            notes.append("Approximate mode — explore then refine")

        batch = max(1, int(8 * (1.2 if placement == "core" else 0.7)))
        cache = "aggressive_local" if placement == "edge" else "shared_regional"
        replica = 1.0 if placement == "core" else 1.4

        base_lat = max(12.0, wl.ops_estimate / max(1.0, wl.parallelism) * 0.05)
        latency = base_lat * lat_factor / max(0.5, batch ** 0.15)
        cost = (wl.ops_estimate * 0.02 + wl.memory_units * 0.1) * cost_factor * replica

        # stay under budget: throttle replicas
        if cost > budget:
            replica = max(1.0, replica * (budget / cost))
            cost = (wl.ops_estimate * 0.02 + wl.memory_units * 0.1) * cost_factor * replica
            notes.append("Replica factor throttled to fit budget")

        # readiness from orientation slightly boosts quality
        ready = scores.get("readiness", 0.5)
        quality = min(0.98, prec_score * 0.85 + ready * 0.15)

        return CloudPlan(
            placement=placement,
            batch_size=batch,
            precision_mode=precision_mode,
            cache_policy=cache,
            replica_factor=round(replica, 3),
            estimated_latency_ms=round(latency, 2),
            estimated_cost_units=round(cost, 2),
            quality_score=round(quality, 4),
            notes=notes,
        )
