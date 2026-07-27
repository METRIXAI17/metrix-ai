"""
Informational Profitability Oracle (Profitability Oracle)

Считает «информационный ROI» и прибыльность для:
- идей, сгенерированных агентами / пайплайном
- финансовых / оптимизационных моделей (Fin Models)

Не путать с бухгалтерской прибылью: это ценность информации × масштабируемость
относительно стоимости внедрения и риска.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import METRIC_THRESHOLDS
from backend.core.metrics import informational_roi


@dataclass
class ProfitabilityInput:
    """Входы калькулятора (все по возможности 0..1, cost тоже 0..1)."""

    name: str
    kind: str  # "idea" | "fin_model" | "program" | "promo"
    impact: float
    scalability: float
    long_term_value: float
    implementation_cost: float
    risk_factor: float = 0.15
    novelty_bonus: float = 0.0
    expected_cash_uplift: float = 0.0  # optional $ or relative
    time_to_value_days: float = 30.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProfitabilityResult:
    name: str
    kind: str
    info_roi: float
    score_band: str
    recommended: bool
    formula: str
    components: dict[str, float]
    cash_efficiency: float
    narrative: str
    next_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class InformationalProfitabilityOracle:
    name = "Informational Profitability Oracle"

    FORMULA = (
        "IROI = 4 × (impact × scalability × long_term × (1+novelty)) "
        "/ (implementation_cost × (1+risk))"
    )

    def evaluate(self, inp: ProfitabilityInput) -> ProfitabilityResult:
        iroi = informational_roi(
            impact=inp.impact,
            scalability=inp.scalability,
            long_term_value=inp.long_term_value,
            implementation_cost=inp.implementation_cost,
            risk_factor=inp.risk_factor,
            novelty_bonus=inp.novelty_bonus,
        )

        attractive = METRIC_THRESHOLDS["info_roi_attractive"]
        premium = METRIC_THRESHOLDS["info_roi_premium"]

        if iroi >= premium:
            band = "premium"
        elif iroi >= attractive:
            band = "attractive"
        elif iroi >= 1.0:
            band = "borderline"
        else:
            band = "weak"

        # cash efficiency: uplift per unit cost, time-discounted
        ttv = max(1.0, float(inp.time_to_value_days))
        time_factor = min(1.0, 30.0 / ttv)
        cost = max(0.05, min(1.0, float(inp.implementation_cost)))
        cash_eff = (max(0.0, inp.expected_cash_uplift) * time_factor) / cost
        # if no cash given, mirror info_roi lightly
        if inp.expected_cash_uplift <= 0:
            cash_eff = iroi * 0.6

        recommended = iroi >= attractive or (band == "borderline" and cash_eff > 1.2)

        actions: list[str] = []
        if inp.implementation_cost > 0.7:
            actions.append("Cut scope to lower implementation cost before full build")
        if inp.risk_factor > 0.4:
            actions.append("Run a paid pilot to reduce risk_factor")
        if inp.scalability < 0.4:
            actions.append("Redesign for reuse across clients / industries")
        if iroi >= premium:
            actions.append("Package as paid showcase + market-making offer")
        if not actions:
            actions.append("Proceed to Full Orientation Package sample")

        narrative = (
            f"{self.name} scored «{inp.name}» ({inp.kind}): "
            f"IROI={iroi:.2f} → {band}. "
            f"impact={inp.impact:.2f}, scale={inp.scalability:.2f}, "
            f"LTV={inp.long_term_value:.2f}, cost={inp.implementation_cost:.2f}, "
            f"risk={inp.risk_factor:.2f}. Recommended={recommended}."
        )

        return ProfitabilityResult(
            name=inp.name,
            kind=inp.kind,
            info_roi=iroi,
            score_band=band,
            recommended=recommended,
            formula=self.FORMULA,
            components={
                "impact": round(inp.impact, 4),
                "scalability": round(inp.scalability, 4),
                "long_term_value": round(inp.long_term_value, 4),
                "implementation_cost": round(inp.implementation_cost, 4),
                "risk_factor": round(inp.risk_factor, 4),
                "novelty_bonus": round(inp.novelty_bonus, 4),
                "cash_efficiency": round(cash_eff, 4),
            },
            cash_efficiency=round(cash_eff, 4),
            narrative=narrative,
            next_actions=actions,
        )

    def evaluate_idea(
        self,
        title: str,
        *,
        impact: float,
        scalability: float,
        long_term_value: float,
        implementation_cost: float,
        risk_factor: float = 0.2,
        novelty_bonus: float = 0.15,
        expected_cash_uplift: float = 0.0,
        time_to_value_days: float = 21.0,
    ) -> ProfitabilityResult:
        return self.evaluate(
            ProfitabilityInput(
                name=title,
                kind="idea",
                impact=impact,
                scalability=scalability,
                long_term_value=long_term_value,
                implementation_cost=implementation_cost,
                risk_factor=risk_factor,
                novelty_bonus=novelty_bonus,
                expected_cash_uplift=expected_cash_uplift,
                time_to_value_days=time_to_value_days,
            )
        )

    def evaluate_fin_model(
        self,
        model_name: str,
        *,
        impact: float,
        scalability: float,
        long_term_value: float,
        implementation_cost: float,
        risk_factor: float = 0.18,
        novelty_bonus: float = 0.1,
    ) -> ProfitabilityResult:
        return self.evaluate(
            ProfitabilityInput(
                name=model_name,
                kind="fin_model",
                impact=impact,
                scalability=scalability,
                long_term_value=long_term_value,
                implementation_cost=implementation_cost,
                risk_factor=risk_factor,
                novelty_bonus=novelty_bonus,
                time_to_value_days=14.0,
            )
        )

    def rank(self, items: list[ProfitabilityInput]) -> list[ProfitabilityResult]:
        results = [self.evaluate(i) for i in items]
        results.sort(key=lambda r: r.info_roi, reverse=True)
        return results
