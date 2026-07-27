"""
Function Calculation Engine — core component 3 of the Paid Product.

Calculates functions and abstractions. Builds mathematical relationships
(including derivative sensitivity metrics) and shows how a change in one
parameter affects the entire output plane.
"""

from __future__ import annotations

import math
from typing import Any, Callable

from backend.paid.types import SensitivityPoint, clamp01, safe_float


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


class FunctionCalculationEngine:
    """
    Builds an abstract multi-parameter function F(params) → output plane,
    then estimates partial derivatives / elasticities for each parameter.
    """

    name = "Function Calculation Engine"

    def __init__(self, step: float = 0.05) -> None:
        self.step = max(1e-4, float(step))

    # ── Scalar output functions (composable abstractions) ────────────────

    def abstract_value(self, params: dict[str, float]) -> float:
        """
        Core abstraction plane (0..~3): clarity of leverage under risk.

        Weighted mix of known design/orientation params with soft defaults.
        """
        p = {k: safe_float(v, 0.5) for k, v in params.items()}
        clarity = p.get("clarity", p.get("value_density", 0.5))
        impact = p.get("impact", p.get("product_fit", 0.5))
        model_fit = p.get("model_fit", p.get("param_coverage", 0.5))
        promo = p.get("promo_fit", p.get("liquidity", 0.5))
        readiness = p.get("readiness", p.get("handoff_readiness", 0.5))
        risk = p.get("risk", 0.35)
        complexity = p.get("complexity", 0.45)
        iroi_pull = p.get("iroi_pull", p.get("iroi_norm", 0.5))
        entanglement = p.get("entanglement", 0.4)
        time_tv = p.get("time_to_value", p.get("time_pressure", 0.5))

        # Nonlinear abstractions (interaction terms)
        leverage = clarity * impact * (1.0 - 0.4 * risk)
        model_surface = model_fit * (0.5 + 0.5 * p.get("sensitivity_depth", 0.5))
        commercial = promo * readiness * (0.6 + 0.4 * iroi_pull)
        drag = 0.25 * complexity + 0.2 * entanglement + 0.1 * (1.0 - time_tv)

        return max(0.0, 1.15 * leverage + 0.9 * model_surface + 0.85 * commercial - drag)

    def output_plane(self, params: dict[str, float]) -> dict[str, float]:
        """Multi-axis output plane derived from the same parameter set."""
        p = {k: safe_float(v, 0.5) for k, v in params.items()}
        base = self.abstract_value(p)
        risk = p.get("risk", 0.35)
        complexity = p.get("complexity", 0.45)
        return {
            "abstract_value": round(base, 4),
            "product_axis": round(
                clamp01(p.get("impact", 0.5) * p.get("clarity", 0.5) * (1 - 0.3 * risk)),
                4,
            ),
            "model_axis": round(
                clamp01(p.get("model_fit", 0.5) * p.get("param_coverage", 0.55)),
                4,
            ),
            "promo_axis": round(
                clamp01(p.get("promo_fit", 0.5) * p.get("order_readiness", 0.45)),
                4,
            ),
            "risk_adjusted": round(clamp01(base / (1.0 + risk + 0.5 * complexity)), 4),
            "scalability": round(
                clamp01(0.4 + 0.3 * p.get("param_coverage", 0.5) + 0.2 * (1 - complexity)),
                4,
            ),
            "paid_readiness": round(
                clamp01(
                    0.35 * p.get("handoff_readiness", p.get("readiness", 0.5))
                    + 0.35 * p.get("iroi_norm", 0.5)
                    + 0.3 * clamp01(base / 2.0)
                ),
                4,
            ),
        }

    def partial_derivative(
        self,
        params: dict[str, float],
        parameter: str,
        fn: Callable[[dict[str, float]], float] | None = None,
    ) -> SensitivityPoint:
        """Finite-difference derivative of F w.r.t. one parameter."""
        fn = fn or self.abstract_value
        base_params = {k: safe_float(v, 0.5) for k, v in params.items()}
        if parameter not in base_params:
            base_params[parameter] = 0.5
        x0 = base_params[parameter]
        f0 = fn(base_params)

        plus = dict(base_params)
        plus[parameter] = _clamp(x0 + self.step)
        f1 = fn(plus)
        dx = plus[parameter] - x0
        if abs(dx) < 1e-12:
            deriv = 0.0
            out_delta = 0.0
        else:
            out_delta = f1 - f0
            deriv = out_delta / dx

        elasticity = 0.0
        if abs(x0) > 1e-9 and abs(f0) > 1e-9:
            elasticity = deriv * (x0 / f0)

        return SensitivityPoint(
            parameter=parameter,
            base_value=x0,
            delta=dx if abs(dx) > 1e-12 else self.step,
            output_delta=out_delta,
            derivative=deriv,
            elasticity=elasticity,
        )

    def sensitivity_report(
        self,
        params: dict[str, float],
        parameters: list[str] | None = None,
        top_k: int = 8,
    ) -> dict[str, Any]:
        """
        Ranked sensitivity of the abstract value to each parameter.
        Shows how a change in one parameter affects the output plane.
        """
        params = {k: safe_float(v, 0.5) for k, v in params.items()}
        keys = parameters or sorted(params.keys())
        # Ensure we always probe a useful default set
        for extra in (
            "clarity",
            "impact",
            "model_fit",
            "promo_fit",
            "risk",
            "complexity",
            "readiness",
            "entanglement",
        ):
            if extra not in keys:
                keys.append(extra)
                params.setdefault(extra, 0.5)

        points = [self.partial_derivative(params, k) for k in keys]
        points.sort(key=lambda p: abs(p.derivative), reverse=True)
        for i, pt in enumerate(points):
            pt.rank = i + 1

        plane = self.output_plane(params)
        # Plane shift if top lever moves +step
        top = points[0] if points else None
        plane_after: dict[str, float] = {}
        if top:
            shifted = dict(params)
            shifted[top.parameter] = _clamp(top.base_value + self.step)
            plane_after = self.output_plane(shifted)

        relationships = []
        for pt in points[:top_k]:
            direction = "increases" if pt.derivative > 0 else "decreases"
            relationships.append(
                {
                    "from": pt.parameter,
                    "to": "abstract_value",
                    "relationship": (
                        f"Raising {pt.parameter} {direction} abstract_value "
                        f"(∂F/∂x ≈ {pt.derivative:.4f}, elasticity={pt.elasticity:.3f})"
                    ),
                    "derivative": round(pt.derivative, 6),
                    "elasticity": round(pt.elasticity, 4),
                }
            )

        # Cross-term: risk × impact interaction magnitude
        risk = params.get("risk", 0.35)
        impact = params.get("impact", params.get("product_fit", 0.5))
        cross = abs(-0.4 * impact)  # from leverage = clarity * impact * (1 - 0.4*risk)

        return {
            "module": self.name,
            "base_params": {k: round(float(v), 4) for k, v in params.items()},
            "output_plane": plane,
            "output_plane_if_top_lever_plus_step": plane_after,
            "step": self.step,
            "sensitivities": [p.to_dict() for p in points[:top_k]],
            "top_lever": top.parameter if top else None,
            "top_derivative": round(top.derivative, 6) if top else 0.0,
            "relationships": relationships,
            "abstractions": {
                "leverage_surface": round(
                    params.get("clarity", 0.5)
                    * params.get("impact", 0.5)
                    * (1.0 - 0.4 * risk),
                    4,
                ),
                "risk_impact_cross_magnitude": round(cross, 4),
                "entropy_proxy": round(
                    clamp01(
                        0.3 * params.get("entanglement", 0.4)
                        + 0.3 * params.get("complexity", 0.45)
                        + 0.2 * (1.0 - params.get("clarity", 0.5))
                        + 0.2 * risk
                    ),
                    4,
                ),
            },
            "summary": (
                f"F≈{plane['abstract_value']:.3f}; top lever={top.parameter if top else 'n/a'} "
                f"(∂={top.derivative:.4f}); paid_readiness={plane['paid_readiness']:.2f}."
                if top
                else "No parameters to differentiate."
            ),
        }

    def apply_reverse_influence(
        self,
        params: dict[str, float],
        reverse: dict[str, float],
    ) -> dict[str, float]:
        """Virtual chips reverse-influence model parameters before calc."""
        out = {k: safe_float(v, 0.5) for k, v in params.items()}
        for k, delta in (reverse or {}).items():
            # Map influence keys onto param space
            target = k
            aliases = {
                "vvi_pull": "entanglement",
                "rrc_pull": "readiness",
                "iroi": "iroi_norm",
                "iroi_pull": "iroi_norm",
                "function_engine_gain": "sensitivity_depth",
                "decision_confidence": "handoff_readiness",
            }
            target = aliases.get(k, k)
            if target not in out:
                out[target] = 0.5
            out[target] = clamp01(out[target] + safe_float(delta))
        return out


def normalize_iroi(info_roi: float) -> float:
    """Map raw IROI (~0..5+) into 0..1 for the function plane."""
    return clamp01(math.tanh(max(0.0, safe_float(info_roi)) / 3.0))
