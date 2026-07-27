"""
Sequence Assembler — builds correct sequential interlinking plans
from 21 principles + meaning units (codes 1 → 400+).
"""

from __future__ import annotations

from typing import Any

from backend.paid.principles_engine import PRINCIPLES, get_principles_engine
from backend.paid.types import clamp01, safe_float


# Canonical plan templates (ordered principle ids)
PLAN_TEMPLATES: dict[str, list[int]] = {
    "orientation_levers": [1, 2, 5, 8, 14, 16, 21],
    "resource_to_profit": [3, 4, 15, 14, 16, 19],
    "void_to_object": [17, 12, 13, 19, 20, 21],
    "sandbox_mechanics": [9, 1, 10, 5, 8, 11],
    "edge_recursive": [18, 15, 4, 6, 7, 21],
    "full_delivery": [1, 2, 3, 4, 5, 14, 16, 19, 21],
    "nft_idea_token": [2, 4, 18, 20, 19, 16, 21],
    "industry_default": [1, 2, 3, 4, 14, 16, 17, 21],
}

INDUSTRY_PLAN: dict[str, str] = {
    "ai-agencies": "orientation_levers",
    "cloud-economy": "resource_to_profit",
    "cost-engineering": "resource_to_profit",
    "chipmaking": "void_to_object",
    "telecom": "sandbox_mechanics",
    "device-assembly": "full_delivery",
}


class SequenceAssembler:
    name = "Sequence Assembler"

    def assemble(
        self,
        *,
        industry_id: str = "",
        top_lever: str = "",
        residual_uncertainty: float = 0.35,
        paid_score: float = 0.5,
        plan_key: str | None = None,
        principles_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        eng = get_principles_engine()
        meanings = eng.build_meanings()
        key = plan_key or INDUSTRY_PLAN.get(industry_id, "industry_default")
        if top_lever and "margin" in top_lever.lower():
            key = "resource_to_profit"
        elif top_lever and any(x in top_lever.lower() for x in ("token", "nft", "idea")):
            key = "nft_idea_token"
        elif residual_uncertainty > 0.55:
            key = "void_to_object"

        seq = list(PLAN_TEMPLATES.get(key, PLAN_TEMPLATES["industry_default"]))
        active = set((principles_report or {}).get("active_principle_ids") or seq)
        # Merge unique actives preserving plan order first
        ordered = list(seq)
        for p in sorted(active):
            if p not in ordered:
                ordered.append(p)

        steps: list[dict[str, Any]] = []
        for i, pid in enumerate(ordered):
            p = PRINCIPLES[pid]
            # Find best meaning involving this principle and next
            nxt = ordered[i + 1] if i + 1 < len(ordered) else None
            link_code = None
            link_title = None
            if nxt is not None:
                pair = tuple(sorted((pid, nxt)))
                for m in meanings:
                    if len(m.sequence) == 2 and tuple(sorted(m.sequence)) == pair:
                        link_code = m.code
                        link_title = m.title
                        break
            steps.append(
                {
                    "index": i + 1,
                    "principle_id": pid,
                    "key": p["key"],
                    "title": p["title"],
                    "layer": p["layer"],
                    "sandbox": p["sandbox"],
                    "link_to_next_code": link_code,
                    "link_to_next": link_title,
                    "role": _step_role(i, len(ordered)),
                }
            )

        # Sequential interlinking code string (plan)
        plan_code = "→".join(str(s["principle_id"]) for s in steps)
        plan_numeric = sum(
            s["principle_id"] * (100 ** (len(steps) - i - 1))
            for i, s in enumerate(steps[:6])
        )

        quality = clamp01(
            0.4
            + 0.25 * paid_score
            + 0.2 * (1.0 - residual_uncertainty)
            + 0.15 * (len(steps) / 12)
        )

        return {
            "module": self.name,
            "status": "assembled",
            "plan_key": key,
            "plan_code": plan_code,
            "plan_numeric_seed": plan_numeric % 10_000_000,
            "sequence_length": len(steps),
            "steps": steps,
            "meanings_available": len(meanings),
            "linked_pair_codes": [
                s["link_to_next_code"] for s in steps if s.get("link_to_next_code")
            ],
            "quality": round(quality, 4),
            "industry_id": industry_id or None,
            "note": (
                "Plan = correct sequential interlinking code. "
                "Not a linear checklist of marketing slogans."
            ),
        }


def _step_role(i: int, n: int) -> str:
    if i == 0:
        return "intake"
    if i == n - 1:
        return "live_close"
    if i < n * 0.35:
        return "frame"
    if i < n * 0.7:
        return "compute"
    return "package"
