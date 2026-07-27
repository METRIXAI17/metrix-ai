"""OrientationForge Engine — dynamic orientation and parameter mapping (fin view)."""

from __future__ import annotations

from typing import Any

from backend.fin_models.base import BaseFinModel
from backend.fin_models.template import FinModelTemplate, ThreeStageSpec


class OrientationForgeEngine(BaseFinModel):
    model_id = "orientationforge"
    model_name = "OrientationForge Engine"

    def stage_spec(self, context: dict[str, Any]) -> ThreeStageSpec:
        return FinModelTemplate.build(
            self.model_id,
            self.model_name,
            definition_bullets=[
                "Financial view of dynamic orientation (no static training dump)",
                "Parameter map is the billable unit of analysis",
                "Axes: value_density, time_pressure, complexity, monetization_fit, risk",
            ],
            definition_deliverables=[
                "Coordinate frame",
                "Mined parameter map",
                "Operating mode",
            ],
            general_bullets=[
                "Orientation run for any industry direction",
                "Track fit Product/Models/Promotion",
                "Standard readiness score",
            ],
            general_deliverables=[
                "Orientation report",
                "Track recommendation",
                "Mode card",
            ],
            general_price=490,
            custom_bullets=[
                "Client-specific lexicon mining",
                "Custom axes weights",
                "Private parameter libraries",
            ],
            custom_deliverables=[
                "Custom orientation profile",
                "Private param lexicon",
                "Ongoing re-orientation SLA",
            ],
            custom_price=1490,
            monetization_hooks=["promo", "market_making", "auto_orders"],
        )

    def calculate(self, context: dict[str, Any]) -> dict[str, Any]:
        scores = self._ctx_scores(context)
        readiness = float(scores.get("readiness", 0.5))
        overall = float(scores.get("overall_orientation", 0.5))
        return {
            "readiness": readiness,
            "overall_orientation": overall,
            "product_fit": scores.get("product_fit", 0.5),
            "model_fit": scores.get("model_fit", 0.5),
            "promo_fit": scores.get("promo_fit", 0.5),
            "impact": round(overall, 4),
            "scalability": 0.78,
            "long_term_value": round(0.5 + readiness * 0.4, 4),
            "implementation_cost": round(max(0.15, 0.55 - readiness * 0.3), 4),
            "risk_factor": round(max(0.08, 0.35 - readiness * 0.2), 4),
            "novelty": 0.22,
            "known_params": int(8 * readiness) + 2,
            "required_params": 10,
            "insights": [
                "Orientation is the cheapest high-leverage paid layer",
                "Re-run per request — zero stale training bias",
            ],
        }
