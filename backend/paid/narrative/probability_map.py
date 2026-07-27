"""
Highest-Probability Conclusion Map

Idea taken from existing modules:
  Mega Map best hypothesis + Function Engine top lever + VVI/ER/RRC health
  + principles coherence + anti-down gate + situation leak

We rank *candidate conclusions* (not free prose) by joint probability so the
writer may only assert the top-K positive (fitting) conclusions.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


class HighestProbabilityMap:
    name = "Highest-Probability Conclusion Map"

    def build(
        self,
        *,
        paid: dict[str, Any] | None = None,
        business: str = "",
        idea_title: str = "",
        relations: dict[str, Any] | None = None,
        principles: dict[str, Any] | None = None,
        anti_down: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        relations = relations or {}
        principles = principles or {}
        anti_down = anti_down or {}

        pkg = paid.get("package") or {}
        sm = paid.get("situation_metrics") or paid.get("business_metrics") or {}
        fn = paid.get("function_engine") or {}
        hyps = paid.get("hypotheses") or {}
        metrics = paid.get("metric_tests") or {}
        oae = paid.get("oae") or {}

        candidates: list[dict[str, Any]] = []

        # From package / idea
        if idea_title or pkg.get("title"):
            candidates.append(
                self._cand(
                    "spine_offer",
                    f"Primary offer spine: {idea_title or pkg.get('title')}",
                    0.55
                    + 0.25 * safe_float(paid.get("paid_score"), 0.5)
                    + 0.1 * safe_float(pkg.get("root_alignment"), 0.5),
                    sources=["package", "demo_idea"],
                )
            )

        lever = pkg.get("top_lever") or fn.get("top_lever") or "clarity"
        candidates.append(
            self._cand(
                "top_lever",
                f"Dominant operational lever is «{lever}» — near-term work should turn this dial first.",
                0.5 + 0.3 * safe_float((fn.get("output_plane") or {}).get("paid_readiness"), 0.5),
                sources=["function_engine"],
            )
        )

        leak = (sm.get("top_leak") or {})
        if leak:
            candidates.append(
                self._cand(
                    "primary_leak",
                    f"Primary cash/ops leak signal: {leak.get('label') or leak.get('id')}. "
                    f"Detail: {str(leak.get('form') or '')[:120]}",
                    0.4 + 0.4 * safe_float(leak.get("severity"), 0.4),
                    sources=["situation_metrics"],
                    positive=safe_float(leak.get("severity"), 0.5) < 0.85,
                )
            )

        best_h = pkg.get("best_hypothesis")
        if best_h:
            candidates.append(
                self._cand(
                    "best_hypothesis",
                    f"Best-fit hypothesis to pilot: {best_h}",
                    0.5 + 0.2 * safe_float(pkg.get("informational_compatibility"), 0.5),
                    sources=["mega_map", "hypotheses"],
                )
            )

        # True relation hubs as conclusions
        for g in (relations.get("true_groups") or [])[:4]:
            hub = g.get("hub")
            w = safe_float(g.get("weight"), 0.5)
            candidates.append(
                self._cand(
                    f"rel_{hub}",
                    f"True-relation hub «{hub}» carries weight {w:.2f} — prose must keep this actor visible.",
                    clamp01(0.35 + 0.15 * w),
                    sources=["relationship_brain"],
                )
            )

        # Principles coherence
        coh = safe_float(principles.get("coherence"), 0.5)
        candidates.append(
            self._cand(
                "principles_coherence",
                f"21-principle coherence at {coh:.0%} supports a structured (not free-form) recommendation path.",
                clamp01(0.3 + 0.5 * coh),
                sources=["principles_engine"],
            )
        )

        # Anti-down
        gate = str(anti_down.get("gate") or "pass")
        gate_p = {"strong_pass": 0.85, "pass": 0.7, "pass_with_warnings": 0.55, "block_down": 0.2}.get(
            gate, 0.5
        )
        candidates.append(
            self._cand(
                "anti_down",
                f"Anti-down gate is «{gate}» — commercial language must match this honesty level.",
                gate_p,
                sources=["anti_down_sorter"],
                positive=gate != "block_down",
            )
        )

        # Client numbers bind
        for k in ("utilization", "gross_margin", "cycle_days", "rework_rate", "churn", "ARPU", "monthly_revenue"):
            # may sit in situation or extra
            pass

        # Sort by probability, keep positive-fitting first
        for c in candidates:
            c["probability"] = round(clamp01(c["probability"]), 4)
        candidates.sort(key=lambda x: (-(1 if x.get("positive", True) else 0), -x["probability"]))

        top = [c for c in candidates if c.get("positive", True)][:7]
        dim = [c for c in candidates if not c.get("positive", True)][:3]

        return {
            "module": self.name,
            "method": (
                "Joint rank of conclusions from Mega Map + Function Engine + Situation "
                "Metrics + Relationship hubs + Principles coherence + Anti-Down gate "
                "(highest-probability map of *fitting* claims)."
            ),
            "candidates": candidates,
            "top_positive": top,
            "dim_or_warn": dim,
            "writing_rails": [c["id"] for c in top],
            "max_probability": top[0]["probability"] if top else 0.0,
        }

    def _cand(
        self,
        cid: str,
        text: str,
        prob: float,
        sources: list[str],
        positive: bool = True,
    ) -> dict[str, Any]:
        return {
            "id": cid,
            "text": text,
            "probability": clamp01(prob),
            "sources": sources,
            "positive": positive,
        }
