"""Base class for all Fin Models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from backend.core.metrics import CoreMetrics, compute_core_metrics, informational_roi
from backend.fin_models.template import FinModelTemplate, ThreeStageSpec
from backend.modules.profitability_oracle import InformationalProfitabilityOracle


@dataclass
class FinModelRunResult:
    model_id: str
    model_name: str
    three_stage: dict[str, Any]
    calculations: dict[str, Any]
    info_roi: float
    metrics: CoreMetrics
    insights: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "three_stage": self.three_stage,
            "calculations": self.calculations,
            "info_roi": self.info_roi,
            "metrics": self.metrics.to_dict(),
            "insights": self.insights,
            "summary": self.summary,
        }


class BaseFinModel(ABC):
    model_id: str = "base"
    model_name: str = "Base Fin Model"

    def __init__(self) -> None:
        self.profit = InformationalProfitabilityOracle()

    @abstractmethod
    def stage_spec(self, context: dict[str, Any]) -> ThreeStageSpec:
        ...

    @abstractmethod
    def calculate(self, context: dict[str, Any]) -> dict[str, Any]:
        ...

    def run(self, context: dict[str, Any]) -> FinModelRunResult:
        spec = self.stage_spec(context)
        calc = self.calculate(context)
        scores = context.get("scores") or {}
        impact = float(calc.get("impact", scores.get("model_fit", 0.55)))
        scale = float(calc.get("scalability", 0.55))
        ltv = float(calc.get("long_term_value", 0.55))
        cost = float(calc.get("implementation_cost", 0.4))
        risk = float(calc.get("risk_factor", 0.2))

        iroi = informational_roi(impact, scale, ltv, cost, risk, float(calc.get("novelty", 0.1)))
        metrics = compute_core_metrics(
            known_params=int(calc.get("known_params", 6)),
            required_params=int(calc.get("required_params", 10)),
            ambiguity_score=float(calc.get("ambiguity", 0.2)),
            conflict_score=float(calc.get("conflict", 0.08)),
            missing_critical=int(calc.get("missing_critical", 0)),
            detected_errors=int(calc.get("detected_errors", 2)),
            actionable_errors=int(calc.get("actionable_errors", 2)),
            improvement_delta=min(1.0, iroi / 6.0),
            fragments=int(calc.get("fragments", 5)),
            successful_reassemblies=int(calc.get("reassemblies", 3)),
            structure_entropy=float(calc.get("entropy", 0.5)),
            reverse_links=int(calc.get("reverse_links", 2)),
            forward_links=int(calc.get("forward_links", 4)),
            notes=[f"fin model {self.model_id}"],
        )
        insights = list(calc.get("insights") or [])
        insights.append(f"IROI={iroi:.2f} via Informational Profitability Oracle")
        summary = f"{self.model_name}: IROI={iroi:.2f}, health={metrics.health_score:.2f}."

        return FinModelRunResult(
            model_id=self.model_id,
            model_name=self.model_name,
            three_stage=spec.to_dict(),
            calculations=calc,
            info_roi=iroi,
            metrics=metrics,
            insights=insights,
            summary=summary,
        )

    def _ctx_scores(self, context: dict[str, Any]) -> dict[str, float]:
        return dict(context.get("scores") or {})
