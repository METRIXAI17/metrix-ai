"""
Relationship brain — direct and reverse relations between operational entities.

Direct: A drives / constrains / funds B
Reverse: B pressure / demand / feedback on A

True-relation groups become the only legal writing rails.
"""

from __future__ import annotations

import re
from typing import Any

from backend.paid.types import clamp01, safe_float


# Industry-tinted entity seeds
_ENTITY_BANK: dict[str, list[str]] = {
    "ai-agencies": ["client", "agency", "delivery_team", "agent_stack", "pilot", "margin"],
    "cloud-economy": ["buyer", "cloud_bill", "placement", "gpu_pool", "retainer", "margin"],
    "cost-engineering": ["sponsor", "cost_map", "parameter", "waste", "cycle", "margin"],
    "chipmaking": ["design_team", "verification", "yield", "NRE", "tapeout", "schedule"],
    "telecom": ["subscriber", "MVNO", "support", "ARPU", "churn", "tariff"],
    "device-assembly": ["OEM", "SMT_line", "rework", "cycle_time", "config_service", "margin"],
    "default": ["buyer", "operator", "product", "delivery", "cash", "metric"],
}


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_]{3,}", text or "")}


class RelationshipBrain:
    name = "Relationship Brain"

    def map(
        self,
        *,
        industry_id: str = "",
        business: str = "",
        idea_title: str = "",
        top_lever: str = "",
        top_leak: str = "",
        scores: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scores = scores or {}
        extra = extra_params or {}
        bank = list(_ENTITY_BANK.get(industry_id, _ENTITY_BANK["default"]))
        # Inject client-token entities
        for t in list(_tokens(business))[:8]:
            if t not in bank and len(t) > 4:
                bank.append(t)

        entities = bank[:10]
        direct: list[dict[str, Any]] = []
        reverse: list[dict[str, Any]] = []

        pairs = [
            (0, 1, "pays", "demands_outcome"),
            (1, 2, "assigns", "reports_friction"),
            (2, 3, "uses", "limits_capacity"),
            (3, 4, "produces", "exposes_gap"),
            (4, 5, "protects", "pressures_cost"),
            (1, 4, "sells", "requires_proof"),
            (0, 5, "funds", "signals_health"),
        ]
        for a, b, d_rel, r_rel in pairs:
            if a >= len(entities) or b >= len(entities):
                continue
            ea, eb = entities[a], entities[b]
            strength = 0.45 + 0.08 * (a % 3)
            if top_lever and top_lever.lower() in (ea + eb + d_rel):
                strength += 0.12
            if any(x in business.lower() for x in (ea[:4], eb[:4])):
                strength += 0.1
            strength = clamp01(strength)
            direct.append(
                {
                    "from": ea,
                    "to": eb,
                    "relation": d_rel,
                    "direction": "direct",
                    "strength": round(strength, 4),
                    "true": strength >= 0.48,
                }
            )
            reverse.append(
                {
                    "from": eb,
                    "to": ea,
                    "relation": r_rel,
                    "direction": "reverse",
                    "strength": round(clamp01(strength * 0.92), 4),
                    "true": strength >= 0.48,
                }
            )

        # Metric-bound relations from client numbers
        metric_links = []
        for k, v in extra.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                metric_links.append(
                    {
                        "from": "operator",
                        "to": str(k),
                        "relation": "measures",
                        "direction": "direct",
                        "strength": 0.7,
                        "true": True,
                        "value": v,
                    }
                )

        true_direct = [r for r in direct if r["true"]]
        true_reverse = [r for r in reverse if r["true"]]
        true_groups = self._group_true(true_direct + true_reverse + metric_links)

        return {
            "module": self.name,
            "entities": entities,
            "direct": direct,
            "reverse": reverse,
            "metric_links": metric_links,
            "true_groups": true_groups,
            "true_count": len(true_direct) + len(true_reverse),
            "top_lever": top_lever or None,
            "top_leak": top_leak or None,
            "idea_title": idea_title or None,
            "clarity": safe_float(scores.get("clarity"), 0.5),
        }

    def _group_true(self, rels: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in rels:
            key = r.get("from") or "unknown"
            groups.setdefault(key, []).append(r)
        out = []
        for hub, items in groups.items():
            out.append(
                {
                    "hub": hub,
                    "relations": items,
                    "weight": round(sum(safe_float(i.get("strength"), 0) for i in items), 4),
                    "label": f"true_cluster:{hub}",
                }
            )
        out.sort(key=lambda g: -g["weight"])
        return out
