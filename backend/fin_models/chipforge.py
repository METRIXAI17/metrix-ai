"""ChipForge Metrics — chip design, vulnerability, production optimization."""

from __future__ import annotations

from typing import Any

from backend.fin_models.base import BaseFinModel
from backend.fin_models.template import FinModelTemplate, ThreeStageSpec


class ChipForgeMetrics(BaseFinModel):
    model_id = "chipforge"
    model_name = "ChipForge Metrics"

    def stage_spec(self, context: dict[str, Any]) -> ThreeStageSpec:
        industry = context.get("industry_id", "chipmaking")
        return FinModelTemplate.build(
            self.model_id,
            self.model_name,
            definition_bullets=[
                "Chip design loop + yield + vulnerability voids (VVI)",
                f"Anchored industry: {industry}",
                "Parameters: node, yield, NRE, defect density, DFT coverage",
                "Links OrientationForge axes: complexity, risk, monetization_fit",
            ],
            definition_deliverables=[
                "Chip parameter map",
                "Vulnerability void list",
                "Baseline yield geometry",
            ],
            general_bullets=[
                "Yield risk scorecard for all semiconductor clients",
                "NRE vs iteration cost navigator",
                "Standard DFT insertion gates",
            ],
            general_deliverables=[
                "Yield scorecard",
                "NRE stage-gate sheet",
                "VVI design checklist",
            ],
            general_price=890,
            custom_bullets=[
                "Client process node & PDK constraints",
                "Custom defect model / fab-side decisions",
                "White-label void oracle thresholds",
            ],
            custom_deliverables=[
                "Client yield twin",
                "Custom NRE simulation",
                "Paid showcase chip-optimization pack",
            ],
            custom_price=2490,
            metrics_hooks={
                "VVI": "Design & process voids before tapeout",
                "ER": "Failing tests that improve yield learning",
                "RRC": "Reverse re-fragment design blocks",
            },
            monetization_hooks=["promo", "auto_orders"],
        )

    def calculate(self, context: dict[str, Any]) -> dict[str, Any]:
        scores = self._ctx_scores(context)
        complexity = float((context.get("axes") or {}).get("complexity", 0.5))
        risk = float((context.get("axes") or {}).get("risk", 0.3))
        yield_est = max(0.55, 0.92 - complexity * 0.25 - risk * 0.15)
        nre_index = 0.3 + complexity * 0.5
        vuln_voids = max(0.05, 1.0 - yield_est)
        impact = min(1.0, yield_est * 0.6 + scores.get("model_fit", 0.5) * 0.4)
        return {
            "yield_estimate": round(yield_est, 4),
            "nre_index": round(nre_index, 4),
            "vulnerability_void_index": round(vuln_voids, 4),
            "dft_coverage_hint": round(min(0.98, 0.6 + (1 - risk) * 0.3), 4),
            "impact": round(impact, 4),
            "scalability": 0.62,
            "long_term_value": round(0.55 + yield_est * 0.3, 4),
            "implementation_cost": round(0.35 + nre_index * 0.35, 4),
            "risk_factor": round(risk, 4),
            "novelty": 0.18,
            "known_params": 7,
            "required_params": 11,
            "ambiguity": vuln_voids,
            "missing_critical": 1 if vuln_voids > 0.35 else 0,
            "detected_errors": 3,
            "actionable_errors": 2,
            "fragments": 6,
            "reassemblies": 4,
            "insights": [
                f"Estimated yield geometry ≈ {yield_est:.1%}",
                f"Vulnerability voids={vuln_voids:.2f} — SpecsForge can close",
                "ChipForge pairs with MetaObject Simulator for virtual die runs",
            ],
        }
