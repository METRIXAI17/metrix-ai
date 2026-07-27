"""
Situation Metrics Engine — supporting module for deep commercial situation analysis.

Tracks:
  · revenue levers
  · delivery friction
  · margin pressure
  · leak maps
  · demand clarity / cloud-fit premium (from BusinessMetricsAnalyzer)

Wraps and extends BusinessMetricsAnalyzer with explicit energy-zone coupling
and derivative-lever alignment for Energy Flow Disentangler + Function Engine.
"""

from __future__ import annotations

from typing import Any

from backend.paid.business_metrics import BusinessMetricsAnalyzer
from backend.paid.types import clamp01, safe_float


class SituationMetricsEngine:
    """Named commercial situation layer used by paid orchestrator + Must-Ask."""

    name = "Situation Metrics Engine"

    def __init__(self) -> None:
        self._base = BusinessMetricsAnalyzer()

    def analyze(
        self,
        *,
        business: str,
        industry_id: str,
        scores: dict[str, float] | None = None,
        axes: dict[str, float] | None = None,
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
        success: dict[str, Any] | None = None,
        energy: dict[str, Any] | None = None,
        function_engine: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        base = self._base.analyze(
            business=business,
            industry_id=industry_id,
            scores=scores,
            axes=axes,
            idea_title=idea_title,
            paid=paid,
            extra_params=extra_params,
            success=success,
        )
        energy = energy or (paid or {}).get("energy_flow") or {}
        fn = function_engine or (paid or {}).get("function_engine") or {}
        plane = fn.get("output_plane") or {}
        top_lever = fn.get("top_lever")

        # Couple energy entanglement into leak severity
        te = safe_float(energy.get("total_entanglement"), 0.4)
        leak_map = list(base.get("leak_map") or [])
        for leak in leak_map:
            if isinstance(leak, dict) and "severity" in leak:
                leak["severity"] = round(
                    clamp01(safe_float(leak["severity"]) * (0.75 + 0.5 * te)), 4
                )
            if isinstance(leak, dict):
                leak["energy_coupled"] = True
        leak_map.sort(
            key=lambda x: -safe_float(x.get("severity") if isinstance(x, dict) else 0)
        )

        revenue_levers = {
            "top_function_lever": top_lever,
            "revenue_control_index": base.get("revenue_control_index"),
            "paid_readiness": plane.get("paid_readiness"),
            "monetization_axis": plane.get("promo_axis") or plane.get("monetization"),
        }

        out = {
            **base,
            "module": self.name,
            "engine": self.name,
            "revenue_levers": revenue_levers,
            "delivery_friction": base.get("delivery_friction"),
            "margin_pressure": base.get("margin_pressure"),
            "leak_map": leak_map,
            "top_leak": leak_map[0] if leak_map else base.get("top_leak"),
            "energy_entanglement": round(te, 4),
            "situation_score": base.get("situation_score"),
            "coupled": {
                "energy_flow": True,
                "function_engine": bool(fn),
            },
            "summary": (
                f"{self.name}: situation={base.get('situation_score')}, "
                f"friction={base.get('delivery_friction')}, "
                f"margin_p={base.get('margin_pressure')}, "
                f"leaks={len(leak_map)}, energy={te:.2f}, lever={top_lever}."
            ),
        }
        return out
