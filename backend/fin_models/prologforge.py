"""PrologForge Logic Engine — logical reasoning and rule-based systems."""

from __future__ import annotations

from typing import Any

from backend.fin_models.base import BaseFinModel
from backend.fin_models.template import FinModelTemplate, ThreeStageSpec


class PrologForgeLogicEngine(BaseFinModel):
    model_id = "prologforge"
    model_name = "PrologForge Logic Engine"

    def stage_spec(self, context: dict[str, Any]) -> ThreeStageSpec:
        return FinModelTemplate.build(
            self.model_id,
            self.model_name,
            definition_bullets=[
                "Rule-based reasoning over orientation facts",
                "Prolog-style predicates as billable logic packs",
                "Explainable decisions for clients who hate black boxes",
            ],
            definition_deliverables=["Fact base", "Rule set v0"],
            general_bullets=[
                "Standard rule packs per industry",
                "Explain traces for each recommendation",
            ],
            general_deliverables=["Rule pack", "Explanation traces"],
            general_price=650,
            custom_bullets=[
                "Client policy rules",
                "Compliance predicates",
            ],
            custom_deliverables=["Custom knowledge base", "Audit-ready traces"],
            custom_price=1990,
        )

    def calculate(self, context: dict[str, Any]) -> dict[str, Any]:
        scores = self._ctx_scores(context)
        mode = context.get("operating_mode") or "balanced_product_path"
        facts = [
            f"industry({context.get('industry_id', 'unknown')})",
            f"mode({mode})",
            f"readiness({scores.get('readiness', 0):.2f})",
            f"product_fit({scores.get('product_fit', 0):.2f})",
            f"model_fit({scores.get('model_fit', 0):.2f})",
            f"promo_fit({scores.get('promo_fit', 0):.2f})",
        ]
        rules_fired = []
        if scores.get("promo_fit", 0) >= scores.get("product_fit", 0):
            rules_fired.append("recommend(promotion_first) :- promo_fit >= product_fit.")
        if scores.get("readiness", 0) < 0.4:
            rules_fired.append("recommend(orientation_expand) :- readiness < 0.4.")
        if scores.get("model_fit", 0) >= 0.55:
            rules_fired.append("recommend(fin_model_focus) :- model_fit >= 0.55.")
        if not rules_fired:
            rules_fired.append("recommend(balanced_product_path).")

        return {
            "facts": facts,
            "rules_fired": rules_fired,
            "explainability": 0.9,
            "impact": round(0.5 + len(rules_fired) * 0.08, 4),
            "scalability": 0.74,
            "long_term_value": 0.68,
            "implementation_cost": 0.33,
            "risk_factor": 0.12,
            "novelty": 0.15,
            "insights": [
                "Logic pack is auditable — ideal for regulated clients",
                f"Fired {len(rules_fired)} rules under current orientation",
            ],
        }
