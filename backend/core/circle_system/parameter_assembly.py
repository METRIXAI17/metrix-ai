"""
Parameter assembly analyzer — composes metrics and checks joint consistency.

User rule: analyze assembly of uncertain values, not heat.
Also implements Market Units note: «1. Компоновать метрики».
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01


class ParameterAssemblyEngine:
    """Compose parameters into assembly score + metric pack."""

    name = "Parameter Assembly Engine"

    def run(
        self,
        certainty_result: dict[str, Any],
        test_answers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = list(certainty_result.get("parameters") or [])
        answers = test_answers or {}
        counts = certainty_result.get("counts") or {}
        n = max(1, len(params))
        cy = int(counts.get("certain_yes") or 0)
        cn = int(counts.get("certain_no") or 0)
        uu = int(counts.get("uncertain") or 0)

        # Base assembly from certainty buckets
        base = (cy * 1.0 + cn * 0.55 + uu * 0.15) / n

        # Answered tests raise assembly of former uncertainties
        filled = 0
        contradict = 0
        for p in params:
            pid = p["id"]
            if pid not in answers and f"{pid}_bin" not in answers:
                continue
            filled += 1
            ans = answers.get(pid) or answers.get(f"{pid}_bin") or {}
            if isinstance(ans, dict):
                val = str(ans.get("value") or ans.get("status") or "").lower()
            else:
                val = str(ans).lower()
            if val in ("certain_no", "cn", "точно нет", "no"):
                if p.get("status") == "certain_yes":
                    contradict += 1
            if val in ("certain_yes", "cy", "точно да", "yes") and p.get("scores", {}).get("no", 0) > 0.5:
                contradict += 1

        answer_boost = min(0.35, filled * 0.07)
        contradiction_penalty = min(0.4, contradict * 0.15)
        assembly = clamp01(base + answer_boost - contradiction_penalty)

        # Compose metrics (note 1)
        composed = {
            "certainty_density": round(cy / n, 4),
            "rejection_clarity": round(cn / n, 4),
            "open_uncertainty": round(uu / n, 4),
            "assembly_score": round(assembly, 4),
            "answer_coverage": round(filled / max(1, uu or filled or 1), 4),
            "contradiction_index": round(contradict / n, 4),
            "composite_readiness": round(
                clamp01(0.5 * assembly + 0.3 * (cy / n) + 0.2 * (1 - uu / n)), 4
            ),
        }

        joints: list[dict[str, Any]] = []
        slots = {p["slot"]: p for p in params}
        # Critical joints for pilot readiness
        for a, b, reason in (
            ("offer", "metric", "offer without metric cannot pilot"),
            ("pilot_scope", "success_criterion", "pilot needs pass/fail"),
            ("resource", "timeline", "timeline needs resource fit"),
            ("goal", "client_segment", "goal needs who it serves"),
        ):
            if a in slots and b in slots:
                sa, sb = slots[a]["status"], slots[b]["status"]
                ok = sa == "certain_yes" and sb == "certain_yes"
                joints.append(
                    {
                        "pair": [a, b],
                        "ok": ok,
                        "statuses": {a: sa, b: sb},
                        "reason": reason,
                    }
                )

        joint_ok = sum(1 for j in joints if j["ok"])
        joint_score = joint_ok / max(1, len(joints)) if joints else assembly

        return {
            "module": self.name,
            "ref": "compose_metrics_1",
            "assembly_score": round(assembly, 4),
            "joint_score": round(joint_score, 4),
            "composed_metrics": composed,
            "joints": joints,
            "filled_answers": filled,
            "contradictions": contradict,
            "heat_used": False,
            "rule": "Assembly only — linguistic warmth is a separate module.",
        }
