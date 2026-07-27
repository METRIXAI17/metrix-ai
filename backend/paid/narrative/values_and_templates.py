"""
Value catalog (from polished-conclusion vantage) + intermediate templates
+ product recommendation templates (parts scheme).
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import safe_float


# Values readable in operational data when conclusion is polished
VALUE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "v_time_to_cash",
        "label": "Time-to-cash clarity",
        "signal": "cycle_days / delivery time grounded",
        "product_hint": "orientation_run",
    },
    {
        "id": "v_margin_defense",
        "label": "Margin defense",
        "signal": "gross_margin + rework/churn visible",
        "product_hint": "pilot_14",
    },
    {
        "id": "v_capacity_truth",
        "label": "Capacity truth",
        "signal": "utilization without vanity",
        "product_hint": "pilot_14",
    },
    {
        "id": "v_offer_edge",
        "label": "Offer edge (non-generic)",
        "signal": "idea spine ≠ template leak",
        "product_hint": "full_package",
    },
    {
        "id": "v_lever_singularity",
        "label": "Single-lever focus",
        "signal": "one top lever with actions",
        "product_hint": "orientation_run",
    },
    {
        "id": "v_hypothesis_testability",
        "label": "Testable hypothesis",
        "signal": "if/then pilot scope",
        "product_hint": "pilot_14",
    },
    {
        "id": "v_asset_object",
        "label": "Objectifiable asset",
        "signal": "repeatable unit for resale / Objectly",
        "product_hint": "objectly_access",
    },
    {
        "id": "v_edge_belief",
        "label": "Edge belief layer",
        "signal": "archetype / OpeningEdge attach",
        "product_hint": "opening_edge",
    },
    {
        "id": "v_sell_ops_access",
        "label": "Sell-ops access right",
        "signal": "standardized VA for clients-of-clients",
        "product_hint": "objectly_access",
    },
    {
        "id": "v_qc_consistency",
        "label": "QC consistency",
        "signal": "anti-down + anticlone passed",
        "product_hint": "full_package",
    },
    {
        "id": "v_cloud_efficiency",
        "label": "Compute capital efficiency",
        "signal": "local pipeline vs API burn story",
        "product_hint": "finops_board",
    },
    {
        "id": "v_narrative_pack",
        "label": "Client-ready narrative pack",
        "signal": "memo sections filled, not scores only",
        "product_hint": "full_package",
    },
]


# Intermediate templates (between value and generation) — deep prompt model
INTERMEDIATE_TEMPLATES: list[dict[str, str]] = [
    {
        "id": "it_context_bind",
        "part": "context",
        "skeleton": "In {industry}, {client_actor} operates under {constraint} while pursuing {job}.",
    },
    {
        "id": "it_relation_direct",
        "part": "relation_direct",
        "skeleton": "Direct relation: {from_e} {relation} {to_e} (strength {strength}).",
    },
    {
        "id": "it_relation_reverse",
        "part": "relation_reverse",
        "skeleton": "Reverse pressure: {from_e} {relation} {to_e}, which limits how fast {hub} can scale.",
    },
    {
        "id": "it_value_claim",
        "part": "value",
        "skeleton": "Value signal «{value_label}» is present because {evidence}.",
    },
    {
        "id": "it_leak_honest",
        "part": "diagnosis",
        "skeleton": "The working diagnosis is {leak}, not as a slogan but as a constraint on {metric_or_flow}.",
    },
    {
        "id": "it_lever_action",
        "part": "action",
        "skeleton": "For the next 14 days, turn only «{lever}»: {action_1}; {action_2}.",
    },
    {
        "id": "it_hypothesis",
        "part": "hypothesis",
        "skeleton": "If we pilot «{hypothesis}», we expect {metric} to move because {mechanism}.",
    },
    {
        "id": "it_void",
        "part": "honesty",
        "skeleton": "We do not yet know {unknown}; until then, claims about {overclaim} stay provisional.",
    },
    {
        "id": "it_product_bridge",
        "part": "product",
        "skeleton": "Recommended product path: {sku} (${price}) because values {value_ids} dominate.",
    },
    {
        "id": "it_objectly",
        "part": "asset",
        "skeleton": "Objectly angle: package «{unit}» as a transferable success unit for {reseller_or_client}.",
    },
]


PRODUCT_PARTS = (
    "context",
    "diagnosis",
    "relation_map",
    "value_board",
    "hypothesis",
    "pilot_design",
    "product_sku",
    "sell_ops_object",
    "opening_edge",
    "honesty_voids",
    "next_14_days",
)


class ValueTemplateEngine:
    name = "Value & Template Engine"

    def analyze_values(
        self,
        *,
        paid: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
        anticlone: dict[str, Any] | None = None,
        probability_map: dict[str, Any] | None = None,
        idea_title: str = "",
    ) -> dict[str, Any]:
        paid = paid or {}
        extra = extra_params or {}
        anticlone = anticlone or {}
        pmap = probability_map or {}
        sm = paid.get("situation_metrics") or {}
        pkg = paid.get("package") or {}

        found: list[dict[str, Any]] = []
        for v in VALUE_CATALOG:
            score = 0.3
            vid = v["id"]
            if vid == "v_time_to_cash" and "cycle_days" in extra:
                score = 0.75
            if vid == "v_margin_defense" and (
                "gross_margin" in extra or "rework_rate" in extra or "churn" in extra
            ):
                score = 0.8
            if vid == "v_capacity_truth" and "utilization" in extra:
                score = 0.78
            if vid == "v_offer_edge" and idea_title and "oriented" not in idea_title.lower():
                score = 0.7
            if vid == "v_lever_singularity" and (pkg.get("top_lever") or paid.get("function_engine")):
                score = 0.72
            if vid == "v_hypothesis_testability" and pkg.get("best_hypothesis"):
                score = 0.68
            if vid == "v_qc_consistency" and anticlone.get("passed_threshold"):
                score = 0.8
            if vid == "v_narrative_pack" and (pmap.get("top_positive") or []):
                score = 0.65
            if vid == "v_cloud_efficiency" and (paid.get("capital_efficiency") or {}):
                score = 0.6
            if vid in ("v_asset_object", "v_sell_ops_access") and safe_float(
                paid.get("paid_score"), 0
            ) >= 0.55:
                score = 0.55
            if vid == "v_edge_belief" and safe_float(paid.get("paid_score"), 0) >= 0.6:
                score = 0.5
            if score >= 0.5:
                found.append({**v, "score": round(score, 3), "present": True})

        found.sort(key=lambda x: -x["score"])
        return {
            "module": self.name,
            "values_present": found,
            "value_ids": [v["id"] for v in found],
            "catalog_size": len(VALUE_CATALOG),
        }

    def intermediate_fill(
        self,
        *,
        industry_id: str,
        business: str,
        idea_title: str,
        relations: dict[str, Any],
        values: dict[str, Any],
        paid: dict[str, Any],
        extra_params: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        extra = extra_params or {}
        pkg = paid.get("package") or {}
        sm = paid.get("situation_metrics") or {}
        leak = (sm.get("top_leak") or {}).get("label") or "unspecified operational friction"
        lever = pkg.get("top_lever") or "clarity"
        hyp = pkg.get("best_hypothesis") or idea_title
        groups = relations.get("true_groups") or []
        hub = groups[0]["hub"] if groups else "operator"
        d0 = (relations.get("direct") or [{}])[0]
        r0 = (relations.get("reverse") or [{}])[0]
        vals = values.get("values_present") or []
        v0 = vals[0] if vals else {"label": "operational clarity", "id": "v_lever_singularity"}

        filled = []
        ctx = {
            "industry": industry_id or "general",
            "client_actor": hub,
            "constraint": leak,
            "job": (business[:80] + "…") if len(business) > 80 else business,
            "from_e": d0.get("from", hub),
            "to_e": d0.get("to", "product"),
            "relation": d0.get("relation", "drives"),
            "strength": str(d0.get("strength", 0.5)),
            "hub": hub,
            "value_label": v0.get("label"),
            "evidence": f"lever={lever}; paid_score={paid.get('paid_score')}",
            "leak": leak,
            "metric_or_flow": next(iter(extra.keys()), "delivery flow"),
            "lever": lever,
            "action_1": "instrument the metric that proves the lever moved",
            "action_2": "cut one free-discovery activity that burns margin",
            "hypothesis": hyp,
            "metric": next(iter(extra.keys()), "cycle_days"),
            "mechanism": "true-relation pressure routes work through the bottleneck hub",
            "unknown": "buyer job language in their words (must-ask)",
            "overclaim": "full package readiness",
            "sku": "Paid Pilot 14–30d",
            "price": "1490",
            "value_ids": ", ".join(v.get("id", "") for v in vals[:3]),
            "unit": idea_title[:40] or "success unit",
            "reseller_or_client": hub,
        }
        # reverse uses reverse relation fields
        ctx["from_e_r"] = r0.get("from", "product")
        ctx["relation_r"] = r0.get("relation", "pressures")

        for t in INTERMEDIATE_TEMPLATES:
            sk = t["skeleton"]
            # manual safe format
            try:
                if t["id"] == "it_relation_reverse":
                    text = (
                        f"Reverse pressure: {r0.get('from', 'product')} "
                        f"{r0.get('relation', 'pressures')} {r0.get('to', hub)}, "
                        f"which limits how fast {hub} can scale."
                    )
                else:
                    text = sk.format(**{k: ctx.get(k, "?") for k in _keys_in(sk)})
            except Exception:
                text = sk
            filled.append(
                {
                    "id": t["id"],
                    "part": t["part"],
                    "text": text,
                    "skeleton_id": t["id"],
                }
            )
        return filled

    def product_templates(
        self,
        *,
        values: dict[str, Any],
        paid: dict[str, Any],
        industry_id: str,
    ) -> list[dict[str, Any]]:
        """Recommended product templates from value board."""
        vids = set(values.get("value_ids") or [])
        score = safe_float(paid.get("paid_score"), 0.5)
        catalog = [
            {
                "sku": "orient_run",
                "name": "Orientation Run",
                "price_usd": 290,
                "parts": ["context", "diagnosis", "value_board", "next_14_days"],
                "when": "entry / diagnose levers",
            },
            {
                "sku": "pilot_14",
                "name": "Paid Pilot 14–30d",
                "price_usd": 1490,
                "parts": [
                    "context",
                    "diagnosis",
                    "hypothesis",
                    "pilot_design",
                    "honesty_voids",
                    "next_14_days",
                ],
                "when": "numbers present + lever clear",
            },
            {
                "sku": "full_package",
                "name": "Full Package (narrative pack)",
                "price_usd": 2490,
                "parts": list(PRODUCT_PARTS),
                "when": "QC + narrative ready",
            },
            {
                "sku": "objectly_access",
                "name": "Objectly Access (success unit)",
                "price_usd": 1790,
                "parts": ["asset", "sell_ops_object", "value_board"],
                "when": "v_asset_object or v_sell_ops_access",
            },
            {
                "sku": "opening_edge",
                "name": "OpeningEdge Layer",
                "price_usd": 1790,
                "parts": ["opening_edge", "relation_map", "honesty_voids"],
                "when": "v_edge_belief",
            },
            {
                "sku": "finops_board",
                "name": "Cloud FinOps Board",
                "price_usd": 1890,
                "parts": ["context", "value_board", "product_sku", "next_14_days"],
                "when": "cloud-economy or v_cloud_efficiency",
            },
        ]
        out = []
        for p in catalog:
            rec = 0.4
            if p["sku"] == "orient_run":
                rec = 0.9 if score < 0.55 else 0.55
            if p["sku"] == "pilot_14":
                rec = 0.85 if score >= 0.55 else 0.4
            if p["sku"] == "full_package":
                rec = 0.75 if "v_narrative_pack" in vids or "v_qc_consistency" in vids else 0.35
            if p["sku"] == "objectly_access":
                rec = 0.7 if "v_asset_object" in vids or "v_sell_ops_access" in vids else 0.3
            if p["sku"] == "opening_edge":
                rec = 0.65 if "v_edge_belief" in vids else 0.25
            if p["sku"] == "finops_board":
                rec = 0.8 if industry_id == "cloud-economy" or "v_cloud_efficiency" in vids else 0.2
            out.append({**p, "recommend_score": round(rec, 3), "industry_id": industry_id})
        out.sort(key=lambda x: -x["recommend_score"])
        return out


def _keys_in(skeleton: str) -> list[str]:
    import re

    return re.findall(r"\{(\w+)\}", skeleton)
