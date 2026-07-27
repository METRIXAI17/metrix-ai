"""
Cloud Sol zone — edge/cloud compute + patterns + linguistic signal.

Modules:
- CloudForge Precision Optimizer
- PragmaVault Pattern Lattice
- Linguistic Signal Weaver (Telecom)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.core.metrics import CoreMetrics, blend_metrics
from backend.modules.cloudforge import CloudForgePrecisionOptimizer
from backend.modules.linguistic_signal_weaver import LinguisticSignalWeaver


PRAGMA_PATTERNS = {
    "ai-agencies": [
        "Demo-first delivery pack",
        "Retainer + project hybrid pricing",
        "Agent handoff matrix",
    ],
    "cloud-economy": [
        "Third-party API burn vs Expert env scorecard",
        "Token-unit collapse table (creative founders)",
        "Edge placement as residual cost lever (kept)",
    ],
    "cost-engineering": [
        "Parameter cost burn map",
        "Tolerance vs price curve",
        "Rework killer checklist",
    ],
    "chipmaking": [
        "Yield-first design review",
        "NRE stage gates",
        "DFT early insertion",
    ],
    "telecom": [
        "SLA-backed product SKU",
        "Intent-to-QoS mapping",
        "Churn early-warning weave",
    ],
    "device-assembly": [
        "Station setup playbook",
        "Config SKU matrix",
        "Rework loop timer",
    ],
}


@dataclass
class CloudSolOutput:
    cloudforge: dict[str, Any]
    pragma_vault: dict[str, Any]
    linguistic: dict[str, Any]
    metrics: CoreMetrics
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone": "Cloud Sol",
            "cloudforge": self.cloudforge,
            "pragma_vault": self.pragma_vault,
            "linguistic": self.linguistic,
            "metrics": self.metrics.to_dict(),
            "summary": self.summary,
        }


class CloudSolZone:
    zone_id = "cloud_sol"
    name = "Cloud Sol"

    def __init__(self) -> None:
        self.cloudforge = CloudForgePrecisionOptimizer()
        self.weaver = LinguisticSignalWeaver()

    def run(
        self,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
        product_title: str,
    ) -> CloudSolOutput:
        scores = orientation.get("scores") or {}
        cloud = self.cloudforge.optimize(
            product_context=product_title or industry_id,
            orientation_scores=scores,
        )
        ling = self.weaver.weave(business_text, industry_id=industry_id)

        patterns = PRAGMA_PATTERNS.get(industry_id, PRAGMA_PATTERNS["ai-agencies"])
        fit = float(scores.get("overall_orientation", 0.5))
        pragma = {
            "module": "PragmaVault Pattern Lattice",
            "patterns": [
                {"name": p, "fit_score": round(min(1.0, fit + i * 0.03), 3)}
                for i, p in enumerate(patterns)
            ],
            "adaptation_notes": [
                "Pick top pattern by fit; adapt language to client geometry.",
                "Do not invent new process if a pragma already closes the void.",
            ],
        }

        metrics = blend_metrics(
            [cloud.metrics, ling.metrics],
            weights=[0.55, 0.45],
        )
        summary = (
            f"Cloud Sol: CloudForge Δq={cloud.gains.get('composite_quality', 0):+.3f}, "
            f"PragmaVault n={len(patterns)}, "
            f"LinguisticWeave coop={ling.cooperation_score:.2f}."
        )
        return CloudSolOutput(
            cloudforge=cloud.to_dict(),
            pragma_vault=pragma,
            linguistic=ling.to_dict(),
            metrics=metrics,
            summary=summary,
        )
