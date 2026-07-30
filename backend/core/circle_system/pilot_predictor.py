"""
Pilot accuracy predictor — how precisely the pilot was / will be embedded.

Model (user note): differential equation with predetermined indicator.
We use a discrete logistic form of dy/dt = k y (1 - y/L) with predetermined
target L = target_accuracy, fitted from assembly + consistency + answer coverage.
"""

from __future__ import annotations

import math
from typing import Any

from backend.paid.types import clamp01


class PilotAccuracyPredictor:
    """
    Predict pilot embedding accuracy.

    Discrete logistic:
      y_{t+1} = y_t + k * y_t * (1 - y_t / L)
    where L = predetermined indicator (default 0.92),
    k = growth from assembly/joints/resources.
    """

    name = "Pilot Accuracy Predictor"
    predetermined_L = 0.92  # predetermined indicator

    def run(
        self,
        *,
        assembly: dict[str, Any] | None = None,
        layers_result: dict[str, Any] | None = None,
        resource_match: dict[str, Any] | None = None,
        days_elapsed: int = 0,
        pilot_horizon_days: int = 21,
        observed_accuracy: float | None = None,
    ) -> dict[str, Any]:
        assembly = assembly or {}
        layers_result = layers_result or {}
        resource_match = resource_match or {}

        a = float(assembly.get("assembly_score") or 0.4)
        j = float(assembly.get("joint_score") or a)
        c = float(layers_result.get("consistency_score") or 0.5)
        r = float(resource_match.get("compatibility_score") or 0.4)
        composed = assembly.get("composed_metrics") or {}
        open_u = float(composed.get("open_uncertainty") or 0.4)

        # Initial embedding quality y0
        y0 = clamp01(0.35 * a + 0.25 * j + 0.2 * c + 0.15 * r + 0.05 * (1 - open_u))
        L = self.predetermined_L
        k = clamp01(0.15 + 0.35 * a + 0.2 * c)  # growth rate

        # Simulate discrete logistic over horizon
        trajectory = []
        y = y0
        steps = max(1, pilot_horizon_days)
        for t in range(0, steps + 1):
            trajectory.append({"day": t, "y": round(y, 4)})
            y = y + k * y * (1.0 - y / L)
            y = min(y, L)

        y_at = trajectory[min(days_elapsed, len(trajectory) - 1)]["y"]
        y_end = trajectory[-1]["y"]

        # If observed post-pilot accuracy provided, residual error
        residual = None
        if observed_accuracy is not None:
            residual = round(float(observed_accuracy) - y_end, 4)

        # Precision of embedding = how close predicted end is to L and assembly
        embed_precision = clamp01(1.0 - abs(L - y_end) - 0.3 * open_u)

        risk = "low"
        if y_end < 0.55 or open_u > 0.5:
            risk = "high"
        elif y_end < 0.7:
            risk = "medium"

        return {
            "module": self.name,
            "model": "discrete_logistic_predetermined_L",
            "equation": "y' = k y (1 - y/L)  [discrete Euler]",
            "predetermined_indicator_L": L,
            "k": round(k, 4),
            "y0": round(y0, 4),
            "days_elapsed": days_elapsed,
            "pilot_horizon_days": pilot_horizon_days,
            "predicted_now": y_at,
            "predicted_end": round(y_end, 4),
            "embedding_precision": round(embed_precision, 4),
            "observed_accuracy": observed_accuracy,
            "residual_vs_prediction": residual,
            "risk": risk,
            "trajectory_sample": trajectory[:: max(1, len(trajectory) // 8)],
            "inputs": {
                "assembly_score": a,
                "joint_score": j,
                "consistency": c,
                "resource_compat": r,
                "open_uncertainty": open_u,
            },
            "recommendation": (
                "Proceed to main package" if y_end >= 0.7 and risk != "high"
                else "Extend pilot / rework uncertain assembly before main package"
            ),
        }
