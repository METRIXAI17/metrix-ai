"""
Metric tests + informational compatibility (step 11).

Uncomplicated, transparent checks — not a second OAE.
When a test fails, Critical Thinking uses the result as a parallel detail
to compare against the paid-part claim.
"""

from __future__ import annotations

import math
from typing import Any

from backend.paid.types import MetricTestResult, clamp01, safe_float


class MetricTestBattery:
    """Special uncomplicated metric tests for the paid layer."""

    name = "Metric Tests"

    def run(
        self,
        *,
        params: dict[str, float] | None = None,
        output_plane: dict[str, float] | None = None,
        energy: dict[str, Any] | None = None,
        mega_map: dict[str, Any] | None = None,
        hypotheses: dict[str, Any] | None = None,
        calm_point: dict[str, Any] | None = None,
        info_roi: float = 0.0,
        success_composite: float | None = None,
        parallel: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = {k: safe_float(v) for k, v in (params or {}).items()}
        plane = {k: safe_float(v) for k, v in (output_plane or {}).items()}
        energy = energy or {}
        mega_map = mega_map or {}
        hypotheses = hypotheses or {}
        calm_point = calm_point or {}
        parallel = parallel or {}
        comparison = mega_map.get("comparison") or {}

        tests: list[MetricTestResult] = []

        # T1 — paid readiness vs IROI consistency
        pr = safe_float(plane.get("paid_readiness"), 0.5)
        iroi_norm = clamp01(math.tanh(max(0.0, info_roi) / 3.0))
        t1_score = 1.0 - abs(pr - iroi_norm)
        tests.append(
            MetricTestResult(
                id="t_paid_iroi_align",
                name="Paid readiness ↔ IROI alignment",
                passed=t1_score >= 0.55,
                score=t1_score,
                threshold=0.55,
                detail=f"paid_readiness={pr:.2f}, iroi_norm={iroi_norm:.2f}",
            )
        )

        # T2 — entanglement not crushing abstract value
        av = safe_float(plane.get("abstract_value"), 0.0)
        ent = safe_float(energy.get("total_entanglement"), 0.4)
        t2_score = clamp01(av / 2.5) * (1.0 - 0.5 * ent)
        tests.append(
            MetricTestResult(
                id="t_value_under_entanglement",
                name="Abstract value survives entanglement",
                passed=t2_score >= 0.25,
                score=t2_score,
                threshold=0.25,
                detail=f"abstract_value={av:.2f}, entanglement={ent:.2f}",
            )
        )

        # T3 — root alignment of best hypothesis
        align = safe_float(comparison.get("root_alignment_score"), 0.5)
        tests.append(
            MetricTestResult(
                id="t_root_alignment",
                name="Mega Map root alignment",
                passed=align >= 0.4,
                score=align,
                threshold=0.4,
                detail=f"root_alignment={align:.2f}",
            )
        )

        # T4 — calm entropy not faking readiness
        entropy = safe_float(calm_point.get("entropy"), 0.4)
        # fail if very calm but paid readiness low (form without substance)
        fake_calm = entropy < 0.22 and pr < 0.4
        t4_score = 0.2 if fake_calm else clamp01(1.0 - abs(entropy - (1.0 - pr)) * 0.5)
        tests.append(
            MetricTestResult(
                id="t_calm_substance",
                name="Calm form vs paid substance",
                passed=not fake_calm and t4_score >= 0.45,
                score=t4_score,
                threshold=0.45,
                detail=f"entropy={entropy:.2f}, paid_readiness={pr:.2f}, fake_calm={fake_calm}",
            )
        )

        # T5 — hypothesis count / confidence mass
        hyps = hypotheses.get("hypotheses") or []
        conf_mass = (
            sum(safe_float(h.get("confidence")) for h in hyps) / max(1, len(hyps))
            if hyps
            else 0.0
        )
        tests.append(
            MetricTestResult(
                id="t_hypothesis_mass",
                name="Hypothesis confidence mass",
                passed=conf_mass >= 0.4 and len(hyps) >= 1,
                score=conf_mass,
                threshold=0.4,
                detail=f"n={len(hyps)}, mean_confidence={conf_mass:.2f}",
            )
        )

        # T6 — informational compatibility (paid plane vs parallel orientation scores)
        par_scores = parallel.get("scores") or {}
        if par_scores:
            prod = safe_float(plane.get("product_axis"), 0.5)
            p_fit = safe_float(par_scores.get("product_fit"), prod)
            model = safe_float(plane.get("model_axis"), 0.5)
            m_fit = safe_float(par_scores.get("model_fit"), model)
            compat = 1.0 - 0.5 * (abs(prod - p_fit) + abs(model - m_fit))
        else:
            compat = 0.7  # no parallel → neutral pass
        if success_composite is not None:
            compat = 0.7 * compat + 0.3 * (
                1.0 - abs(pr - clamp01(success_composite))
            )
        tests.append(
            MetricTestResult(
                id="t_info_compatibility",
                name="Informational compatibility (paid ↔ parallel)",
                passed=compat >= 0.5,
                score=clamp01(compat),
                threshold=0.5,
                detail=f"compatibility={compat:.2f}",
            )
        )

        # T7 — zone clarity: at least one zone influence declared
        zones = parallel.get("zone_influence") or energy.get("zone_balance_after") or {}
        z_ok = bool(zones)
        tests.append(
            MetricTestResult(
                id="t_zone_clarity",
                name="Zone clarity present",
                passed=z_ok,
                score=1.0 if z_ok else 0.0,
                threshold=1.0,
                detail=f"zones={list(zones.keys()) if isinstance(zones, dict) else zones}",
            )
        )

        passed_n = sum(1 for t in tests if t.passed)
        overall = passed_n / max(1, len(tests))
        failed = [t.to_dict() for t in tests if not t.passed]

        return {
            "module": self.name,
            "tests": [t.to_dict() for t in tests],
            "passed_count": passed_n,
            "total": len(tests),
            "overall_score": round(overall, 4),
            "all_passed": passed_n == len(tests),
            "failed": failed,
            "informational_compatibility": round(clamp01(compat), 4),
            "summary": (
                f"Metric tests {passed_n}/{len(tests)} passed; "
                f"info_compat={compat:.2f}."
            ),
        }
