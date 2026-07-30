"""
Circle-System architectural layers as *needs* + consistency confirmation.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.lexicon import LAYER_NEED_MARKERS, detect_markers
from backend.paid.types import clamp01


# Ordered ring (outer → inner autopilot core)
LAYER_RING = (
    "identity",
    "orientation",
    "resources",
    "operations",
    "product",
    "pilot",
    "metrics",
    "integration",
    "orchestration",
    "expertise",
)

LAYER_DEPENDS: dict[str, tuple[str, ...]] = {
    "identity": (),
    "orientation": ("identity",),
    "resources": ("orientation",),
    "operations": ("resources",),
    "product": ("orientation", "resources"),
    "pilot": ("product", "operations", "metrics"),
    "metrics": ("product",),
    "integration": ("operations", "product"),
    "orchestration": ("integration", "metrics", "pilot"),
    "expertise": ("orientation", "product", "metrics"),
}


class CircleLayerEngine:
    """Map needs → layers; confirm consistency along the ring."""

    name = "Circle Layer Engine"

    def run(
        self,
        text: str,
        certainty_result: dict[str, Any] | None = None,
        assembly: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        hits = detect_markers(text or "", LAYER_NEED_MARKERS)
        params = (certainty_result or {}).get("parameters") or []
        slot_to_layer = {
            "goal": "orientation",
            "client_segment": "orientation",
            "offer": "product",
            "constraint": "operations",
            "resource": "resources",
            "metric": "metrics",
            "timeline": "pilot",
            "integration": "integration",
            "pilot_scope": "pilot",
            "success_criterion": "metrics",
        }

        layers: list[dict[str, Any]] = []
        for name in LAYER_RING:
            strength = float(hits.get(name, 0.0))
            related = [p for p in params if slot_to_layer.get(p.get("slot")) == name]
            if related:
                cy = sum(1 for p in related if p.get("status") == "certain_yes")
                strength = max(strength, cy / len(related))
            need_level = (
                "critical" if strength >= 0.7 else
                "active" if strength >= 0.35 else
                "latent" if strength > 0 else
                "absent"
            )
            layers.append(
                {
                    "layer": name,
                    "need_strength": round(strength, 3),
                    "need_level": need_level,
                    "depends_on": list(LAYER_DEPENDS[name]),
                    "param_count": len(related),
                }
            )

        # Consistency: for each active/critical layer, dependencies must not be absent
        violations: list[dict[str, Any]] = []
        by_name = {L["layer"]: L for L in layers}
        for L in layers:
            if L["need_level"] not in ("active", "critical"):
                continue
            for dep in L["depends_on"]:
                d = by_name[dep]
                if d["need_level"] == "absent":
                    violations.append(
                        {
                            "layer": L["layer"],
                            "missing_dependency": dep,
                            "fix": f"Raise {dep} before confirming {L['layer']}",
                        }
                    )

        assembly_score = float((assembly or {}).get("assembly_score") or 0.4)
        consistency = clamp01(
            1.0
            - 0.12 * len(violations)
            + 0.15 * assembly_score
            - 0.05 * sum(1 for L in layers if L["need_level"] == "absent")
        )

        confirmed = [L["layer"] for L in layers if L["need_level"] in ("active", "critical") and not any(
            v["layer"] == L["layer"] for v in violations
        )]

        return {
            "module": self.name,
            "system": "circle-system",
            "ring": list(LAYER_RING),
            "layers": layers,
            "violations": violations,
            "consistency_score": round(consistency, 4),
            "confirmed_layers": confirmed,
            "autopilot_ready": consistency >= 0.62 and "pilot" in confirmed and "metrics" in confirmed,
            "rule": "Layers are needs; confirmation is dependency-consistent activation.",
        }
