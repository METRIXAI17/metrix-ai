"""
Conceptual Engine — 21 Principles fully interlinked.

Each principle is a node. Every pair is an edge (210). Plan sequences
encode ordered interlinking codes from 1 → 400+ meanings. Reader groups
meanings; Sequence Assembler builds correct order; Anti-Down filters.
"""

from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass, field
from typing import Any

from backend.paid.types import clamp01, safe_float


# ── 21 Principles (Top 7 paradigm + 8–21 expansion) ──────────────────────────

PRINCIPLES: dict[int, dict[str, Any]] = {
    1: {
        "id": 1,
        "key": "sector",
        "title": "Sector",
        "layer": "top7",
        "summary": "Container of phenomena by unique signs.",
        "axes": ["container", "classification", "ports"],
        "sandbox": "sectors",
    },
    2: {
        "id": 2,
        "key": "service_metrics",
        "title": "Service = Metric Stream",
        "layer": "top7",
        "summary": "Input metric sets hide growth zones and development paths.",
        "axes": ["metrics", "growth_zones", "resource_redistribution"],
        "sandbox": "metric_set",
    },
    3: {
        "id": 3,
        "key": "resource_assembly",
        "title": "Resource Assembly",
        "layer": "top7",
        "summary": "Consumer vs business resources in balance; modular fields without rigid binding.",
        "axes": ["consumer", "business", "modules"],
        "sandbox": "basis",
    },
    4: {
        "id": 4,
        "key": "concept",
        "title": "Concept",
        "layer": "top7",
        "summary": "Final executable action with assembled resource for the consumer.",
        "axes": ["action", "consumer_end", "context"],
        "sandbox": "phases",
    },
    5: {
        "id": 5,
        "key": "measure",
        "title": "Measure",
        "layer": "top7",
        "summary": "Complex of mechanical parameters to tune (balance, linear-time dynamics).",
        "axes": ["balance", "mechanics", "params"],
        "sandbox": "basis",
    },
    6: {
        "id": 6,
        "key": "methodicalness",
        "title": "Methodicalness",
        "layer": "top7",
        "summary": "Turn unconnected elements into a living system via context + assembly + concepts.",
        "axes": ["context", "system", "methods"],
        "sandbox": "framework",
    },
    7: {
        "id": 7,
        "key": "pragma_collection",
        "title": "Pragma Collection",
        "layer": "top7",
        "summary": "Foundation Campus + Metrics paradigm for directions and tools.",
        "axes": ["campus", "paradigm", "tools"],
        "sandbox": "framework",
    },
    8: {
        "id": 8,
        "key": "functions_corrector",
        "title": "Functions as Correctors",
        "layer": "expand",
        "summary": "Functions correct factors inside Measure so constructions fit phenomena.",
        "axes": ["correction", "factors", "fit"],
        "sandbox": "phases",
    },
    9: {
        "id": 9,
        "key": "sandbox",
        "title": "Sandbox",
        "layer": "expand",
        "summary": "sectors · contours · vectors · framework · phases · basis · metric set.",
        "axes": ["sandbox", "topology", "playfield"],
        "sandbox": "sectors",
    },
    10: {
        "id": 10,
        "key": "game_mechanics",
        "title": "Game-like Mechanics",
        "layer": "expand",
        "summary": "Mechanics under contours and metric sets (analogy to game systems).",
        "axes": ["mechanics", "contour", "rules"],
        "sandbox": "contours",
    },
    11: {
        "id": 11,
        "key": "planning_meanings",
        "title": "Planning as Meaning Switch",
        "layer": "expand",
        "summary": "Planning switches meanings — exit from flat conceptual thinking.",
        "axes": ["planning", "meaning_switch", "framework"],
        "sandbox": "framework",
    },
    12: {
        "id": 12,
        "key": "unoccupied_ports",
        "title": "Unoccupied Ports",
        "layer": "expand",
        "summary": "Discover unused ports inside sectors for alternative approach.",
        "axes": ["ports", "discovery", "sector"],
        "sandbox": "sectors",
    },
    13: {
        "id": 13,
        "key": "pattern_replace",
        "title": "Pattern Replacement",
        "layer": "expand",
        "summary": "Replace action pattern when current regulation cannot solve the event.",
        "axes": ["pattern", "event", "regulation"],
        "sandbox": "phases",
    },
    14: {
        "id": 14,
        "key": "financial_participation",
        "title": "Financial Participation + Campus RM",
        "layer": "expand",
        "summary": "Growth driver: redistribute resources to raise productivity & detail.",
        "axes": ["finance", "campus", "redistribution"],
        "sandbox": "metric_set",
    },
    15: {
        "id": 15,
        "key": "adaptation_asset",
        "title": "Adaptation as Consumer Asset",
        "layer": "expand",
        "summary": "Adapt environment for operational efficiency and capital control.",
        "axes": ["adaptation", "consumer", "capital"],
        "sandbox": "vectors",
    },
    16: {
        "id": 16,
        "key": "pragma_profit",
        "title": "Pragma Profit Review",
        "layer": "expand",
        "summary": "Review deal profit on business-resource products; model profitable schemes.",
        "axes": ["profit", "pragma", "modeling"],
        "sandbox": "metric_set",
    },
    17: {
        "id": 17,
        "key": "vvi_er_rrc_object",
        "title": "VVI → ER → RRC → Object M",
        "layer": "expand",
        "summary": "Void analysis → error efficiency → reverse refragmentation → virtual object.",
        "axes": ["vvi", "er", "rrc", "object_m"],
        "sandbox": "vectors",
    },
    18: {
        "id": 18,
        "key": "opening_edge",
        "title": "OpeningEdge",
        "layer": "expand",
        "summary": "Emotional archetypes + recursive secondary combination (open opportuner · complexity frontier).",
        "axes": ["archetype", "recursive", "edge"],
        "sandbox": "vectors",
    },
    19: {
        "id": 19,
        "key": "objectly",
        "title": "Objectly",
        "layer": "expand",
        "summary": "Turn phenomena into Virtual Assets with weight, price and owner.",
        "axes": ["virtual_asset", "weight", "owner"],
        "sandbox": "phases",
    },
    20: {
        "id": 20,
        "key": "nft_create_building",
        "title": "NFT Create-Building",
        "layer": "expand",
        "summary": "Keyword-combinatorial query building; strange generations; tertiary nets from gaps.",
        "axes": ["token", "generation", "library"],
        "sandbox": "phases",
    },
    21: {
        "id": 21,
        "key": "harness_live",
        "title": "Self-cycling Harness + Live Mode",
        "layer": "expand",
        "summary": "Showcase self-cycles: one component pulls the other into live automatic mode.",
        "axes": ["harness", "live", "cycle"],
        "sandbox": "framework",
    },
}

# Industry affinity (weights 0..1 for ranking)
INDUSTRY_AFFINITY: dict[str, dict[int, float]] = {
    "ai-agencies": {2: 0.95, 4: 0.9, 14: 0.85, 16: 0.8, 18: 0.88, 20: 0.75, 21: 0.9},
    "cloud-economy": {3: 0.9, 5: 0.85, 8: 0.8, 14: 0.95, 15: 0.85, 16: 0.9},
    "cost-engineering": {2: 0.9, 5: 0.95, 8: 0.9, 14: 0.92, 16: 0.88},
    "chipmaking": {1: 0.85, 3: 0.9, 9: 0.8, 12: 0.75, 17: 0.95, 19: 0.85},
    "telecom": {1: 0.8, 6: 0.85, 10: 0.8, 12: 0.9, 13: 0.85, 18: 0.7},
    "device-assembly": {3: 0.88, 4: 0.85, 9: 0.8, 13: 0.9, 15: 0.85, 17: 0.8},
}


def _pair_code(a: int, b: int) -> int:
    """Stable code 1..210 for unordered pair."""
    lo, hi = (a, b) if a < b else (b, a)
    # triangular index
    return (hi - 1) * (hi - 2) // 2 + lo


def _meaning_id(seq: tuple[int, ...], flavor: str = "") -> str:
    raw = "-".join(str(x) for x in seq) + ("|" + flavor if flavor else "")
    return hashlib.sha1(raw.encode()).hexdigest()[:10]


MEANING_TEMPLATES = (
    "bind_{a}_into_{b}",
    "project_{a}_through_{b}",
    "balance_{a}_against_{b}",
    "amplify_{a}_via_{b}",
    "correct_{a}_using_{b}",
    "redistribute_{a}_under_{b}",
    "objectify_{a}_as_{b}",
    "cycle_{a}_with_{b}",
)


@dataclass
class MeaningUnit:
    code: int
    sequence: tuple[int, ...]
    title: str
    group: str
    flavor: str
    weight: float = 0.5
    edges: list[tuple[int, int]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "sequence": list(self.sequence),
            "title": self.title,
            "group": self.group,
            "flavor": self.flavor,
            "weight": round(self.weight, 4),
            "edges": [list(e) for e in self.edges],
            "meaning_id": _meaning_id(self.sequence, self.flavor),
        }


class PrinciplesEngine:
    """
    Full interlinking graph + 400+ meanings.
    Plan = correct sequential interlinking code.
    """

    name = "21-Principle Conceptual Engine"
    n_principles = 21

    def __init__(self) -> None:
        self.principles = PRINCIPLES
        self._meanings: list[MeaningUnit] | None = None
        self._edges: list[dict[str, Any]] | None = None

    def graph(self) -> dict[str, Any]:
        """All 21 nodes + all pairwise edges (C(21,2)=210)."""
        if self._edges is None:
            edges = []
            for a, b in itertools.combinations(range(1, 22), 2):
                pa, pb = PRINCIPLES[a], PRINCIPLES[b]
                shared = set(pa["axes"]) & set(pb["axes"])
                strength = 0.35 + 0.15 * len(shared)
                if pa["layer"] == pb["layer"]:
                    strength += 0.1
                if pa.get("sandbox") == pb.get("sandbox"):
                    strength += 0.12
                edges.append(
                    {
                        "code": _pair_code(a, b),
                        "from": a,
                        "to": b,
                        "from_key": pa["key"],
                        "to_key": pb["key"],
                        "shared_axes": sorted(shared),
                        "strength": round(clamp01(strength), 4),
                        "label": f"{pa['title']} ↔ {pb['title']}",
                    }
                )
            self._edges = edges
        return {
            "nodes": [
                {
                    "id": p["id"],
                    "key": p["key"],
                    "title": p["title"],
                    "layer": p["layer"],
                    "summary": p["summary"],
                    "axes": p["axes"],
                    "sandbox": p["sandbox"],
                }
                for p in PRINCIPLES.values()
            ],
            "edges": self._edges,
            "edge_count": len(self._edges),
            "node_count": 21,
            "complete_graph": True,
        }

    def build_meanings(self) -> list[MeaningUnit]:
        """
        Generate 400+ meaning units:
          · 210 pairwise (one primary flavor each)
          · extra flavors on strong pairs
          · ordered triples from top7 + expansion bridges
          · plan chains (length 4–5) for sequential codes
        """
        if self._meanings is not None:
            return self._meanings

        units: list[MeaningUnit] = []
        code = 1
        graph = self.graph()
        strength_map = {(e["from"], e["to"]): e["strength"] for e in graph["edges"]}

        # 1) All pairs — primary
        for a, b in itertools.combinations(range(1, 22), 2):
            pa, pb = PRINCIPLES[a]["key"], PRINCIPLES[b]["key"]
            flavor = MEANING_TEMPLATES[code % len(MEANING_TEMPLATES)].format(a=pa, b=pb)
            w = strength_map.get((a, b), 0.4)
            units.append(
                MeaningUnit(
                    code=code,
                    sequence=(a, b),
                    title=f"{PRINCIPLES[a]['title']} × {PRINCIPLES[b]['title']}",
                    group="pair",
                    flavor=flavor,
                    weight=w,
                    edges=[(a, b)],
                )
            )
            code += 1

        # 2) Secondary flavors on strongest pairs → push past 210
        strong = sorted(strength_map.items(), key=lambda x: -x[1])[:48]
        for (a, b), w in strong:
            for fi, tmpl in enumerate(MEANING_TEMPLATES[1:4]):
                pa, pb = PRINCIPLES[a]["key"], PRINCIPLES[b]["key"]
                flavor = tmpl.format(a=pa, b=pb)
                units.append(
                    MeaningUnit(
                        code=code,
                        sequence=(a, b),
                        title=f"{PRINCIPLES[a]['title']} ⇢ {PRINCIPLES[b]['title']} [{fi+1}]",
                        group="pair_flavor",
                        flavor=flavor,
                        weight=w * (0.95 - 0.05 * fi),
                        edges=[(a, b)],
                    )
                )
                code += 1

        # 3) Ordered triples (top7 with expand bridges)
        top7 = list(range(1, 8))
        expand = list(range(8, 22))
        triple_count = 0
        for a, b in itertools.combinations(top7, 2):
            for c in expand[:8]:
                if triple_count >= 80:
                    break
                seq = (a, b, c)
                units.append(
                    MeaningUnit(
                        code=code,
                        sequence=seq,
                        title=(
                            f"{PRINCIPLES[a]['title']} → "
                            f"{PRINCIPLES[b]['title']} → "
                            f"{PRINCIPLES[c]['title']}"
                        ),
                        group="triple",
                        flavor=f"plan_bridge_{a}_{b}_{c}",
                        weight=0.55
                        + 0.1 * strength_map.get((min(a, b), max(a, b)), 0.3),
                        edges=[(a, b), (b, c) if b < c else (c, b)],
                    )
                )
                code += 1
                triple_count += 1
            if triple_count >= 80:
                break

        # 4) Plan chains length 4–5 (sequential interlinking codes)
        plan_seeds = [
            (1, 2, 14, 16),
            (1, 9, 12, 13),
            (3, 4, 15, 16),
            (5, 8, 10, 11),
            (6, 7, 14, 21),
            (2, 5, 8, 16),
            (17, 19, 20, 21),
            (18, 15, 4, 21),
            (1, 3, 4, 19),
            (9, 10, 11, 13),
            (2, 14, 15, 16),
            (17, 18, 19, 20),
            (1, 2, 3, 4, 5),
            (7, 14, 16, 21),
            (12, 13, 15, 18),
            (3, 5, 8, 14, 16),
            (1, 12, 13, 17, 19),
            (6, 9, 10, 11, 21),
            (2, 4, 18, 20, 21),
            (5, 8, 14, 16, 21),
        ]
        for seq in plan_seeds:
            units.append(
                MeaningUnit(
                    code=code,
                    sequence=seq,
                    title=" → ".join(PRINCIPLES[i]["title"] for i in seq),
                    group="plan_chain",
                    flavor=f"seq_{'_'.join(str(x) for x in seq)}",
                    weight=0.72,
                    edges=[
                        (seq[i], seq[i + 1])
                        if seq[i] < seq[i + 1]
                        else (seq[i + 1], seq[i])
                        for i in range(len(seq) - 1)
                    ],
                )
            )
            code += 1

        # 5) Industry-tinted meanings (push count)
        for ind, aff in INDUSTRY_AFFINITY.items():
            keys = sorted(aff.keys(), key=lambda k: -aff[k])[:4]
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    a, b = keys[i], keys[j]
                    units.append(
                        MeaningUnit(
                            code=code,
                            sequence=(a, b),
                            title=f"[{ind}] {PRINCIPLES[a]['title']} × {PRINCIPLES[b]['title']}",
                            group=f"industry:{ind}",
                            flavor=f"ind_{ind}_{a}_{b}",
                            weight=0.5 * (aff[a] + aff[b]),
                            edges=[(a, b) if a < b else (b, a)],
                        )
                    )
                    code += 1

        self._meanings = units
        return units

    def meaning_count(self) -> int:
        return len(self.build_meanings())

    def read_groups(self, industry_id: str = "") -> dict[str, Any]:
        """
        Reader: classify meanings into groups from combinations
        (does not load a prebuilt DB of client data).
        """
        units = self.build_meanings()
        groups: dict[str, list[dict[str, Any]]] = {}
        for u in units:
            g = u.group.split(":")[0]
            groups.setdefault(g, []).append(u.to_dict())

        # Industry boost
        aff = INDUSTRY_AFFINITY.get(industry_id or "", {})
        ranked = []
        for u in units:
            boost = sum(aff.get(p, 0.0) for p in u.sequence) / max(1, len(u.sequence))
            ranked.append({**u.to_dict(), "industry_boost": round(boost, 4)})
        ranked.sort(key=lambda x: -(x["weight"] + x.get("industry_boost", 0)))

        return {
            "module": "Principles Reader",
            "total_meanings": len(units),
            "group_counts": {k: len(v) for k, v in groups.items()},
            "groups": {k: v[:12] for k, v in groups.items()},  # sample per group
            "top_for_industry": ranked[:24],
            "industry_id": industry_id or None,
            "stages_hint": [
                "1 perception of principle signs",
                "2 notation of pair/triple codes",
                "3 objectification of meaning units",
                "4 interpretation via shared axes",
                "5 application → sequence assembler",
            ],
        }

    def run(
        self,
        *,
        industry_id: str = "",
        scores: dict[str, Any] | None = None,
        top_lever: str = "",
        residual_uncertainty: float = 0.35,
    ) -> dict[str, Any]:
        scores = scores or {}
        graph = self.graph()
        reader = self.read_groups(industry_id)
        # Active principles from scores / lever
        active = list(range(1, 8))  # always top7
        if top_lever:
            # map lever keywords lightly
            lever_map = {
                "clarity": [6, 11, 4],
                "model_fit": [2, 5, 8],
                "margin": [14, 16, 5],
                "utilization": [3, 14, 15],
                "delivery": [4, 13, 10],
            }
            for k, ids in lever_map.items():
                if k in (top_lever or "").lower():
                    active.extend(ids)
        aff = INDUSTRY_AFFINITY.get(industry_id, {})
        for pid, w in sorted(aff.items(), key=lambda x: -x[1])[:5]:
            if pid not in active:
                active.append(pid)
        active = sorted(set(active))[:12]

        coherence = clamp01(
            0.55
            + 0.15 * safe_float(scores.get("clarity"), 0.5)
            + 0.15 * (1.0 - residual_uncertainty)
            + 0.1 * (len(active) / 21)
        )

        return {
            "module": self.name,
            "status": "live",
            "principles_count": 21,
            "meanings_count": reader["total_meanings"],
            "edge_count": graph["edge_count"],
            "active_principle_ids": active,
            "active_principles": [
                {
                    "id": i,
                    "key": PRINCIPLES[i]["key"],
                    "title": PRINCIPLES[i]["title"],
                }
                for i in active
            ],
            "graph_summary": {
                "nodes": graph["node_count"],
                "edges": graph["edge_count"],
                "complete": True,
            },
            "reader": {
                "group_counts": reader["group_counts"],
                "top_meanings": reader["top_for_industry"][:10],
                "stages_hint": reader["stages_hint"],
            },
            "coherence": round(coherence, 4),
            "honesty": (
                "Interlinking graph is complete (210 pairs). "
                "Meanings are generated combinatorially — not a client CRM dump."
            ),
        }


_engine: PrinciplesEngine | None = None


def get_principles_engine() -> PrinciplesEngine:
    global _engine
    if _engine is None:
        _engine = PrinciplesEngine()
    return _engine
