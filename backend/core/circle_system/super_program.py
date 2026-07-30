"""
Super Program matcher — compares developed parameters against Super Program
families (Deep Tech row from 4 Бизнеса.xlsx) and returns best-fit subset.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.lexicon import (
    DEEP_TECH_COMPONENTS_EXCEL,
    SUPER_PROGRAM_FAMILIES,
)
from backend.paid.types import clamp01


# Family → which parameter slots they consume / produce
FAMILY_SLOT_AFFINITY: dict[str, dict[str, Any]] = {
    "synthesis_core": {
        "excel": "SYNTHESIS CORE",
        "slots": ("goal", "offer", "constraint"),
        "role": "Compose multi-signal brief into coherent system design.",
        "outputs": ("architecture_sketch", "param_map"),
    },
    "reality_layer_interface": {
        "excel": "REALITY LAYER INTERFACE",
        "slots": ("client_segment", "integration", "resource"),
        "role": "Bind abstract design to real channels, stacks, ledgers.",
        "outputs": ("integration_surface", "data_contracts"),
    },
    "symmetry_bridge": {
        "excel": "SYMMETRY BRIDGE",
        "slots": ("offer", "client_segment", "metric"),
        "role": "Align client need symmetry with product levers.",
        "outputs": ("fit_matrix", "gap_list"),
    },
    "value_proposition_engine": {
        "excel": "VALUE PROPOSITION ENGINE",
        "slots": ("offer", "metric", "success_criterion"),
        "role": "Price and prove value with measurable claims.",
        "outputs": ("value_claim", "roi_story"),
    },
    "engagement_transaction_protocol": {
        "excel": "ENGAGEMENT & TRANSACTION PROTOCOL",
        "slots": ("pilot_scope", "timeline", "client_segment"),
        "role": "Encode how clients engage, pay, and accept delivery.",
        "outputs": ("engagement_flow", "acceptance_protocol"),
    },
    "metrix_ledger_operational_core": {
        "excel": "METRIX LEDGER & OPERATIONAL CORE",
        "slots": ("metric", "resource", "integration"),
        "role": "Operational rules, ledger traces, metric firmware sink.",
        "outputs": ("ops_rules", "ledger_hooks", "support_feed"),
    },
}


class SuperProgramMatcher:
    """Match parameters → best Super Program subset."""

    name = "Super Program Matcher"

    def run(
        self,
        certainty_result: dict[str, Any],
        assembly: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = certainty_result.get("parameters") or []
        by_slot = {p["slot"]: p for p in params}
        assembly_score = float((assembly or {}).get("assembly_score") or 0.4)

        ranked: list[dict[str, Any]] = []
        for fam in SUPER_PROGRAM_FAMILIES:
            meta = FAMILY_SLOT_AFFINITY[fam]
            slot_scores = []
            for s in meta["slots"]:
                p = by_slot.get(s)
                if not p:
                    slot_scores.append(0.1)
                    continue
                st = p.get("status")
                if st == "certain_yes":
                    slot_scores.append(1.0)
                elif st == "certain_no":
                    slot_scores.append(0.25)
                else:
                    slot_scores.append(0.45)
            fit = clamp01(0.7 * (sum(slot_scores) / len(slot_scores)) + 0.3 * assembly_score)
            ranked.append(
                {
                    "family": fam,
                    "excel_name": meta["excel"],
                    "fit": round(fit, 4),
                    "role": meta["role"],
                    "slots_used": list(meta["slots"]),
                    "outputs": list(meta["outputs"]),
                    "slot_scores": dict(zip(meta["slots"], [round(x, 3) for x in slot_scores])),
                }
            )

        ranked.sort(key=lambda x: x["fit"], reverse=True)
        # Best-fit subset: top families until cumulative coverage of slots
        selected = []
        covered: set[str] = set()
        for r in ranked:
            if r["fit"] < 0.35 and selected:
                continue
            selected.append(r)
            covered.update(r["slots_used"])
            if len(selected) >= 3 and len(covered) >= 6:
                break
        if not selected and ranked:
            selected = ranked[:2]

        return {
            "module": self.name,
            "global_step": "3_super_program_match",
            "ref": "ref_4:point_7 + excel_deep_tech",
            "models": "open",
            "deep_tech_components_excel": list(DEEP_TECH_COMPONENTS_EXCEL),
            "ranked": ranked,
            "best_subset": selected,
            "covered_slots": sorted(covered),
            "primary": selected[0] if selected else None,
            "pricing_hint_rub": {
                "solution_design": 750_000,
                "deal_param_usd": 60,
                "source": "4 Бизнеса.xlsx · Deep Tech",
            },
        }
