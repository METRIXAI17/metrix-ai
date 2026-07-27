"""
OpeningEdge — emotional archetypes + recursive secondary combination.

Archetypes: open opportuner · complexity frontier · and supporting cognitive set.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


ARCHETYPES = {
    "open_opportuner": {
        "title": "Open Opportuner",
        "traits": ["opportunity_scan", "asymmetric_upside", "fast_contact"],
        "risk": "over-open without delivery spine",
    },
    "complexity_frontier": {
        "title": "Complexity Frontier",
        "traits": ["front_run_complexity", "structure_before_scale", "anti_chaos"],
        "risk": "over-architecture before first cash",
    },
    "capital_steward": {
        "title": "Capital Steward",
        "traits": ["unit_economics", "spend_to_progress", "margin_discipline"],
        "risk": "under-invest in distribution",
    },
    "metric_navigator": {
        "title": "Metric Navigator",
        "traits": ["startup_success_metrics", "lever_clarity", "sell_ops"],
        "risk": "vanity metrics without JTBD",
    },
    "live_cycler": {
        "title": "Live Cycler",
        "traits": ["self_cycle", "harness_pull", "demo_to_paid"],
        "risk": "loop without customer signal",
    },
}


class OpeningEdgeEngine:
    name = "OpeningEdge"
    status = "live"

    def run(
        self,
        *,
        industry_id: str = "",
        paid: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
        residual_uncertainty: float = 0.35,
        principles: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        scores = scores or {}
        principles = principles or {}

        clarity = safe_float(scores.get("clarity"), 0.5)
        impact = safe_float(scores.get("impact"), 0.5)
        paid_score = safe_float(paid.get("paid_score"), 0.5)

        # Primary archetype selection
        if residual_uncertainty > 0.5 and clarity < 0.55:
            primary = "complexity_frontier"
        elif impact > 0.6 and paid_score > 0.55:
            primary = "open_opportuner"
        elif industry_id in ("cloud-economy", "cost-engineering"):
            primary = "capital_steward"
        elif paid_score > 0.65:
            primary = "live_cycler"
        else:
            primary = "metric_navigator"

        secondary = (
            "open_opportuner"
            if primary != "open_opportuner"
            else "complexity_frontier"
        )

        # Recursive secondary combination of unique variants
        variants = self._combine_variants(primary, secondary, industry_id)
        edge_score = clamp01(
            0.3 * clarity
            + 0.25 * impact
            + 0.25 * paid_score
            + 0.2 * (1.0 - residual_uncertainty)
        )

        return {
            "module": self.name,
            "status": self.status,
            "primary_archetype": {
                "id": primary,
                **ARCHETYPES[primary],
            },
            "secondary_archetype": {
                "id": secondary,
                **ARCHETYPES[secondary],
            },
            "recursive_variants": variants,
            "edge_score": round(edge_score, 4),
            "cognitive_stack": [
                "open opportuner",
                "complexity frontainer",
                "capital stewardship",
                "metric-driven sell ops",
            ],
            "industry_id": industry_id or None,
            "principle_bridge": 18,
            "honesty": (
                "Archetypes guide framing — they do not replace client metrics or cash proof."
            ),
        }

    def _combine_variants(
        self, primary: str, secondary: str, industry_id: str
    ) -> list[dict[str, Any]]:
        a = ARCHETYPES[primary]["traits"]
        b = ARCHETYPES[secondary]["traits"]
        out = []
        for i, t1 in enumerate(a):
            t2 = b[i % len(b)]
            out.append(
                {
                    "id": f"var_{i+1}",
                    "combo": f"{t1}+{t2}",
                    "label": f"{t1.replace('_', ' ')} × {t2.replace('_', ' ')}",
                    "industry_tint": industry_id or "general",
                    "generation": "secondary_recursive",
                }
            )
        # Tertiary: cross with industry keyword
        if industry_id:
            out.append(
                {
                    "id": "var_tertiary",
                    "combo": f"{primary}+{industry_id}",
                    "label": f"{ARCHETYPES[primary]['title']} on {industry_id}",
                    "industry_tint": industry_id,
                    "generation": "tertiary_industry",
                }
            )
        return out
