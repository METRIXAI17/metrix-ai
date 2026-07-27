"""
Infa Sol zone — informational / specification / meta-reality foundation.

Modules:
- SpecsForge Recursive Oracle
- MetaReality Synthesizer
- AnalogBridge Operator Surface
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.metrics import CoreMetrics, compute_core_metrics
from backend.modules.specsforge import SpecsForgeRecursiveOracle


@dataclass
class MetaRealityResult:
    """MetaReality Synthesizer — conceptual twin of the client's operation."""

    constraints: list[str]
    reality_checklist: list[str]
    risk_flags: list[str]
    twin_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "MetaReality Synthesizer",
            "constraints": self.constraints,
            "reality_checklist": self.reality_checklist,
            "risk_flags": self.risk_flags,
            "twin_summary": self.twin_summary,
        }


@dataclass
class AnalogBridgeResult:
    """AnalogBridge Operator Surface — human-facing control surface."""

    ui_flow: list[str]
    operator_script: list[str]
    handoff_rules: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "AnalogBridge Operator Surface",
            "ui_flow": self.ui_flow,
            "operator_script": self.operator_script,
            "handoff_rules": self.handoff_rules,
            "summary": self.summary,
        }


@dataclass
class InfaSolOutput:
    specs: dict[str, Any]
    meta_reality: dict[str, Any]
    analog_bridge: dict[str, Any]
    metrics: CoreMetrics
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone": "Infa Sol",
            "specs": self.specs,
            "meta_reality": self.meta_reality,
            "analog_bridge": self.analog_bridge,
            "metrics": self.metrics.to_dict(),
            "summary": self.summary,
        }


class InfaSolZone:
    zone_id = "infa_sol"
    name = "Infa Sol"

    def __init__(self) -> None:
        self.specs_oracle = SpecsForgeRecursiveOracle()

    def run(
        self,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
    ) -> InfaSolOutput:
        params = (orientation.get("parameter_map") or {}).get("params") or {}
        specs = self.specs_oracle.refine(business_text, industry_id, params)

        axes = (orientation.get("frame") or {}).get("axes") or {}
        constraints = [
            f"Time pressure axis={axes.get('time_pressure', 0):.2f}",
            f"Complexity axis={axes.get('complexity', 0):.2f}",
            f"Risk axis={axes.get('risk', 0):.2f}",
            "Stay inside mined parameter map — no scope bloat",
        ]
        checklist = [
            "Client outcome stated in one sentence",
            "Who pays / who uses / who operates — named",
            "At least one measurable success metric",
            "VVI of specs below critical threshold",
        ]
        risks = list(specs.root.voids) if hasattr(specs.root, "voids") else []
        for child in specs.root.children:
            risks.extend(child.voids[:1])
        risks = risks[:6] or ["Low explicit risk flags — validate with client"]

        meta = MetaRealityResult(
            constraints=constraints,
            reality_checklist=checklist,
            risk_flags=risks,
            twin_summary=(
                "MetaReality Synthesizer built a conceptual twin: "
                f"{len(constraints)} constraints, {len(checklist)} checks, "
                f"{len(risks)} risk flags."
            ),
        )

        analog = AnalogBridgeResult(
            ui_flow=[
                "1. Orient industry",
                "2. Show demo idea + metrics",
                "3. Walk Full Package (Product → Models → Promo)",
                "4. Offer paid implement",
            ],
            operator_script=[
                "Confirm industry direction first.",
                "Reflect geometry in client's words (no jargon dump).",
                "Offer free demo idea + breakdown, then close to Full Package.",
            ],
            handoff_rules=[
                "Human owns price and relationship.",
                "System owns orientation, specs recursion, metrics.",
                "Escalate if VVI critical after refine.",
            ],
            summary="AnalogBridge ready: simple surface, deep handoff rules.",
        )

        metrics = specs.final_metrics
        summary = (
            f"Infa Sol: SpecsForge health={metrics.health_score:.2f}, "
            f"MetaReality risks={len(risks)}, AnalogBridge flows ready."
        )
        return InfaSolOutput(
            specs=specs.to_dict(),
            meta_reality=meta.to_dict(),
            analog_bridge=analog.to_dict(),
            metrics=metrics,
            summary=summary,
        )
