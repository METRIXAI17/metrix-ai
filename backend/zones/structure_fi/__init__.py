"""
Structure Fi zone — decisions, optics, zone topology, money geometry.

Modules:
- VerdictLattice Decision Core
- OpticPrism Insight Lens
- ZoneWeave Topology Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.core.metrics import CoreMetrics, compute_core_metrics


@dataclass
class StructureFiOutput:
    verdict_lattice: dict[str, Any]
    optic_prism: dict[str, Any]
    zone_weave: dict[str, Any]
    metrics: CoreMetrics
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone": "Structure Fi",
            "verdict_lattice": self.verdict_lattice,
            "optic_prism": self.optic_prism,
            "zone_weave": self.zone_weave,
            "metrics": self.metrics.to_dict(),
            "summary": self.summary,
        }


class StructureFiZone:
    zone_id = "structure_fi"
    name = "Structure Fi"

    def run(
        self,
        industry_id: str,
        orientation: dict[str, Any],
        tracks_recommended: list[str],
        info_roi: float,
    ) -> StructureFiOutput:
        scores = orientation.get("scores") or {}
        mode = orientation.get("operating_mode") or "balanced_product_path"

        # VerdictLattice — who decides what
        decisions = [
            {
                "decision": "Select industry orientation",
                "owner": "system+client",
                "when": "request_start",
                "escalation": "human if industry unclear",
            },
            {
                "decision": "Pick primary track",
                "owner": "system",
                "when": "after_orientation",
                "escalation": "client override allowed",
            },
            {
                "decision": "Recommend paid implement",
                "owner": "system+human",
                "when": f"info_roi>={1.8}",
                "escalation": "human closes price",
            },
            {
                "decision": "Trigger auto-order simulation",
                "owner": "MarketForge / Auto Orders",
                "when": "monetization_enabled",
                "escalation": "client approval gate",
            },
        ]
        verdict = {
            "module": "VerdictLattice Decision Core",
            "note": (
                "Lightweight zone view. Full project awareness lives in "
                "backend.core.decision_core.DecisionMakingCore (pipeline v2)."
            ),
            "operating_mode": mode,
            "decisions": decisions,
            "ownership_matrix": {
                "orientation": "OrientationForge",
                "specs": "SpecsForge",
                "mode_switch": "Enhanced Decision Making Core",
                "oae": "Main Operational Analytics Engine",
                "pricing": "human",
                "promo": "Promo Automation",
                "paid_block_18": "backend/paid",
                "generative_block_19": "backend/generative",
            },
        }

        # OpticPrism — insights
        insights = [
            f"Primary track signal: {tracks_recommended[0] if tracks_recommended else 'product'}",
            f"Readiness={scores.get('readiness', 0):.2f}",
            f"Informational ROI={info_roi:.2f}",
            f"Mode={mode}",
        ]
        if scores.get("promo_fit", 0) > 0.6:
            insights.append("Promotion geometry is hot — reverse outreach ready.")
        if scores.get("model_fit", 0) > 0.6:
            insights.append("Fin model path will pay for itself narrative.")
        optic = {
            "module": "OpticPrism Insight Lens",
            "insights": insights,
            "semi_manual_ceiling": {
                "note": "How far semi-manual + AI scales before full automation",
                "ceiling_hint": round(min(0.95, 0.4 + float(scores.get("readiness", 0.4))), 3),
            },
        }

        # ZoneWeave — topology across zones for this product result
        topology = {
            "module": "ZoneWeave Topology Engine",
            "path": [
                "Infa Sol → specs & twin",
                "Cloud Sol → compute & language",
                "Structure Fi → decisions & money view",
                "Product Sol → client architecture",
                "Superstructure → unified product overlay",
            ],
            "revenue_zones": {
                "demo": "free idea + breakdown",
                "core": "single track paid",
                "expansion": "full package + auto orders",
            },
            "industry": industry_id,
        }

        metrics = compute_core_metrics(
            known_params=7,
            required_params=9,
            ambiguity_score=max(0.0, 1.0 - float(scores.get("readiness", 0.5))),
            conflict_score=0.08,
            missing_critical=0 if info_roi >= 1.0 else 1,
            detected_errors=2,
            actionable_errors=2,
            improvement_delta=min(1.0, info_roi / 5.0),
            fragments=5,
            successful_reassemblies=4,
            structure_entropy=0.5,
            reverse_links=3,
            forward_links=5,
        )
        summary = (
            f"Structure Fi: VerdictLattice decisions={len(decisions)}, "
            f"Optic insights={len(insights)}, ZoneWeave path locked."
        )
        return StructureFiOutput(
            verdict_lattice=verdict,
            optic_prism=optic,
            zone_weave=topology,
            metrics=metrics,
            summary=summary,
        )
