"""
Anti-Down Sorter — high-quality filter that prevents low-value / collapsing outputs.

Scores candidates on structural integrity, commercial honesty, metric grounding,
and sequence coherence. Drops or demotes "down" trajectories.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


class AntiDownSorter:
    name = "Anti-Down Sorter"
    version = "1.0"

    # Hard floors — below these, status becomes blocked_down
    FLOORS = {
        "structural": 0.28,
        "honesty": 0.35,
        "metric_ground": 0.22,
        "sequence_coherence": 0.25,
        "composite": 0.32,
    }

    def sort(
        self,
        *,
        candidates: list[dict[str, Any]] | None = None,
        paid: dict[str, Any] | None = None,
        sequence: dict[str, Any] | None = None,
        principles: dict[str, Any] | None = None,
        situation_metrics: dict[str, Any] | None = None,
        commercial: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        sequence = sequence or {}
        principles = principles or {}
        sm = situation_metrics or paid.get("situation_metrics") or {}
        commercial = commercial or {}

        base_pool = list(candidates or [])
        if not base_pool:
            base_pool = self._default_candidates(paid, sequence, principles)

        scored: list[dict[str, Any]] = []
        for c in base_pool:
            s = self._score_one(c, paid=paid, sequence=sequence, sm=sm, principles=principles)
            scored.append(s)

        scored.sort(key=lambda x: -x["composite"])

        kept = [x for x in scored if not x["is_down"]]
        dropped = [x for x in scored if x["is_down"]]

        best = kept[0] if kept else (scored[0] if scored else None)
        gate = "pass" if best and not best["is_down"] else "block_down"
        if best and best["composite"] >= 0.62:
            gate = "strong_pass"
        elif best and best["composite"] >= 0.45:
            gate = "pass_with_warnings"

        return {
            "module": self.name,
            "version": self.version,
            "gate": gate,
            "ranked": scored[:12],
            "kept_count": len(kept),
            "dropped_count": len(dropped),
            "best": best,
            "floors": self.FLOORS,
            "warnings": self._warnings(best, sm, paid),
            "honesty": (
                "Anti-Down demotes collapsing / empty / oversold outputs. "
                "Never upgrades preview to packageable without metric ground."
            ),
        }

    def _score_one(
        self,
        c: dict[str, Any],
        *,
        paid: dict[str, Any],
        sequence: dict[str, Any],
        sm: dict[str, Any],
        principles: dict[str, Any],
    ) -> dict[str, Any]:
        structural = clamp01(
            0.4 * safe_float(c.get("structural"), 0.5)
            + 0.3 * safe_float(sequence.get("quality"), 0.5)
            + 0.3 * safe_float(principles.get("coherence"), 0.5)
        )
        # Honesty: penalize if selling package without readiness
        status = str(paid.get("status") or c.get("status") or "preview")
        paid_score = safe_float(paid.get("paid_score") or c.get("paid_score"), 0.5)
        honesty = 0.75
        if "package" in status and paid_score < 0.55:
            honesty = 0.25  # hard honesty hit
        if status in ("candidate_preview", "preview", "open_scaffold"):
            honesty = clamp01(0.55 + 0.2 * paid_score)
        if c.get("oversell"):
            honesty = clamp01(honesty - 0.35)

        metric_ground = clamp01(
            0.35 * safe_float(sm.get("situation_score"), 0.4)
            + 0.25 * (1.0 - safe_float(sm.get("delivery_friction"), 0.4))
            + 0.20 * (1.0 - safe_float(sm.get("margin_pressure"), 0.4))
            + 0.20 * paid_score
        )
        # Bonus if client filled real numbers
        if sm.get("has_client_numbers") or c.get("has_client_numbers"):
            metric_ground = clamp01(metric_ground + 0.15)

        seq_coh = clamp01(
            safe_float(sequence.get("quality"), 0.5)
            * (0.7 + 0.3 * min(1.0, safe_float(sequence.get("sequence_length"), 5) / 8))
        )

        # Collapse detectors
        collapse_flags: list[str] = []
        if structural < self.FLOORS["structural"]:
            collapse_flags.append("structural_collapse")
        if honesty < self.FLOORS["honesty"]:
            collapse_flags.append("honesty_collapse")
        if metric_ground < self.FLOORS["metric_ground"]:
            collapse_flags.append("metric_void")
        if seq_coh < self.FLOORS["sequence_coherence"]:
            collapse_flags.append("sequence_noise")
        if c.get("empty_charts_only"):
            collapse_flags.append("pretty_empty_charts")
            metric_ground = clamp01(metric_ground - 0.2)

        composite = clamp01(
            0.28 * structural
            + 0.30 * honesty
            + 0.24 * metric_ground
            + 0.18 * seq_coh
        )
        is_down = (
            composite < self.FLOORS["composite"]
            or len(collapse_flags) >= 2
            or "honesty_collapse" in collapse_flags
        )

        return {
            "id": c.get("id") or c.get("title") or "candidate",
            "title": c.get("title") or c.get("id") or "candidate",
            "structural": round(structural, 4),
            "honesty": round(honesty, 4),
            "metric_ground": round(metric_ground, 4),
            "sequence_coherence": round(seq_coh, 4),
            "composite": round(composite, 4),
            "collapse_flags": collapse_flags,
            "is_down": is_down,
            "rank_label": _rank_label(composite, is_down),
            "source": c.get("source", "derived"),
        }

    def _default_candidates(
        self,
        paid: dict[str, Any],
        sequence: dict[str, Any],
        principles: dict[str, Any],
    ) -> list[dict[str, Any]]:
        pkg = paid.get("package") or {}
        hyps = (paid.get("hypotheses") or {}).get("selected") or []
        out = [
            {
                "id": "primary_package",
                "title": pkg.get("title") or paid.get("idea_title") or "Primary paid path",
                "structural": safe_float(paid.get("paid_score"), 0.55),
                "status": paid.get("status"),
                "paid_score": paid.get("paid_score"),
                "source": "paid_core",
            },
            {
                "id": "sequence_plan",
                "title": f"Plan {sequence.get('plan_key', 'default')}",
                "structural": safe_float(sequence.get("quality"), 0.5),
                "source": "sequence_assembler",
            },
            {
                "id": "principles_coherent",
                "title": "21-principle coherent path",
                "structural": safe_float(principles.get("coherence"), 0.5),
                "source": "principles_engine",
            },
        ]
        for i, h in enumerate(hyps[:3]):
            if isinstance(h, dict):
                out.append(
                    {
                        "id": f"hyp_{i}",
                        "title": h.get("title") or h.get("id") or f"hypothesis_{i}",
                        "structural": safe_float(h.get("score") or h.get("confidence"), 0.45),
                        "source": "hypothesis",
                    }
                )
        # Explicit anti-patterns for sorter to reject
        out.append(
            {
                "id": "empty_showcase",
                "title": "Pretty charts without numbers",
                "structural": 0.2,
                "empty_charts_only": True,
                "oversell": True,
                "source": "anti_pattern",
            }
        )
        return out

    def _warnings(
        self,
        best: dict[str, Any] | None,
        sm: dict[str, Any],
        paid: dict[str, Any],
    ) -> list[str]:
        w: list[str] = []
        if not best:
            return ["No candidates to rank"]
        if best.get("is_down"):
            w.append("Best path still classified as DOWN — do not sell as packageable")
        if safe_float(sm.get("situation_score"), 0.5) < 0.4:
            w.append("Situation score weak — require 5 client numbers before full package")
        if str(paid.get("status")) == "candidate_preview":
            w.append("Status is candidate_preview — UI must not show packageable green")
        for f in best.get("collapse_flags") or []:
            w.append(f"flag:{f}")
        return w


def _rank_label(composite: float, is_down: bool) -> str:
    if is_down:
        return "DOWN"
    if composite >= 0.72:
        return "FLAGSHIP"
    if composite >= 0.55:
        return "SOLID"
    if composite >= 0.42:
        return "WORKABLE"
    return "THIN"
