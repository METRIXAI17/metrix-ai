"""
Terminal Teammate Network — mesh of specialized terminal roles.

Borrows the business idea of a network of terminal teammates:
roles, links, coverage, load, and attach plan for the primary problem.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


ROLE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "ops_controller",
        "name": "Ops Controller Teammate",
        "families": ["ops", "metrics"],
        "skills": ["control_loop", "sla", "handoff"],
        "base_load": 0.4,
    },
    {
        "id": "cost_surgeon",
        "name": "Cost Surgeon Teammate",
        "families": ["cost"],
        "skills": ["unit_econ", "api_burn", "param_waste"],
        "base_load": 0.35,
    },
    {
        "id": "product_architect",
        "name": "Product Architect Teammate",
        "families": ["product", "liquidity"],
        "skills": ["sku", "specs", "acceptance"],
        "base_load": 0.45,
    },
    {
        "id": "proof_writer",
        "name": "Proof Writer Teammate",
        "families": ["promo"],
        "skills": ["fin_model", "case_card", "buyer_language"],
        "base_load": 0.3,
    },
    {
        "id": "risk_sentinel",
        "name": "Risk Sentinel Teammate",
        "families": ["ops", "metrics", "cost"],
        "skills": ["kill_switch", "deadlock", "gates"],
        "base_load": 0.25,
    },
    {
        "id": "liquidity_runner",
        "name": "Liquidity Runner Teammate",
        "families": ["liquidity"],
        "skills": ["document", "offramp", "match"],
        "base_load": 0.35,
    },
]


@dataclass
class TeammateNode:
    id: str
    name: str
    active: bool
    load: float
    families: list[str]
    skills: list[str]
    links: list[str] = field(default_factory=list)
    attach_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TeammateNetworkResult:
    module: str
    nodes: list[TeammateNode]
    lead_id: str
    coverage: float
    mesh_density: float
    attach_plan: list[dict[str, Any]]
    network_score: float
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "nodes": [n.to_dict() for n in self.nodes],
            "lead_id": self.lead_id,
            "coverage": round(self.coverage, 4),
            "mesh_density": round(self.mesh_density, 4),
            "attach_plan": self.attach_plan,
            "network_score": round(self.network_score, 4),
            "summary": self.summary,
        }


class TeammateNetwork:
    """Build a terminal teammate mesh for the recognized problem lattice."""

    name = "Terminal Teammate Network"

    def build(
        self,
        *,
        industry_id: str,
        problems: list[dict[str, Any]] | None = None,
        family_pressure: dict[str, float] | None = None,
        product_sku: str = "",
        coordination_index: float = 0.5,
        readiness_band: str = "orientation_needed",
    ) -> TeammateNetworkResult:
        problems = problems or []
        family_pressure = family_pressure or {}
        families_present = set(family_pressure.keys()) | {
            str(p.get("family")) for p in problems if p.get("family")
        }
        if not families_present:
            families_present = {"ops"}

        primary_family = "ops"
        if problems:
            primary_family = str(problems[0].get("family") or "ops")
        elif family_pressure:
            primary_family = max(family_pressure.items(), key=lambda x: x[1])[0]

        nodes: list[TeammateNode] = []
        active_ids: list[str] = []
        for role in ROLE_CATALOG:
            overlap = set(role["families"]) & families_present
            # always consider risk sentinel if high ops/cost
            force = role["id"] == "risk_sentinel" and (
                float(family_pressure.get("ops", 0)) > 0.4
                or float(family_pressure.get("cost", 0)) > 0.4
            )
            active = bool(overlap) or force
            # product_architect always on for product SKUs
            if role["id"] == "product_architect" and product_sku:
                active = True
            # ops controller default for teammate SKUs
            if role["id"] == "ops_controller" and "teammate" in (product_sku or "").lower():
                active = True
            if not active and readiness_band == "execution_ready" and role["id"] == "ops_controller":
                active = True

            load = float(role["base_load"])
            if primary_family in role["families"]:
                load = _clamp01(load + 0.2)
            if active:
                active_ids.append(role["id"])
            nodes.append(
                TeammateNode(
                    id=role["id"],
                    name=role["name"],
                    active=active,
                    load=load if active else 0.0,
                    families=list(role["families"]),
                    skills=list(role["skills"]),
                    attach_reason=(
                        f"covers {', '.join(sorted(overlap))}"
                        if overlap
                        else ("forced risk gate" if force else "standby")
                    ),
                )
            )

        # wire links among active nodes (ring + lead spokes)
        lead_id = "ops_controller"
        for role in ROLE_CATALOG:
            if primary_family in role["families"] and role["id"] in active_ids:
                lead_id = role["id"]
                break
        if lead_id not in active_ids and active_ids:
            lead_id = active_ids[0]

        by_id = {n.id: n for n in nodes}
        for i, nid in enumerate(active_ids):
            links = []
            # ring
            if len(active_ids) > 1:
                links.append(active_ids[(i + 1) % len(active_ids)])
            # spoke to lead
            if nid != lead_id:
                links.append(lead_id)
            by_id[nid].links = list(dict.fromkeys(links))

        # coverage: fraction of problem families that have an active role
        covered = 0
        for fam in families_present:
            if any(n.active and fam in n.families for n in nodes):
                covered += 1
        coverage = _clamp01(covered / max(1, len(families_present)))

        # mesh density: links / possible among active
        n_act = len(active_ids)
        link_count = sum(len(by_id[i].links) for i in active_ids)
        max_links = max(1, n_act * (n_act - 1))
        mesh_density = _clamp01(link_count / max_links) if n_act > 1 else (0.5 if n_act == 1 else 0.0)

        attach_plan: list[dict[str, Any]] = []
        for p in problems[:4]:
            fam = str(p.get("family") or "ops")
            role = next((n for n in nodes if n.active and fam in n.families), None)
            attach_plan.append(
                {
                    "problem_id": p.get("id"),
                    "family": fam,
                    "teammate_id": role.id if role else lead_id,
                    "teammate_name": role.name if role else by_id[lead_id].name,
                    "action": f"Own problem {p.get('id')} until severity < 0.35",
                    "product_hook": p.get("product_hook"),
                }
            )

        network_score = _clamp01(
            coverage * 0.45
            + mesh_density * 0.25
            + coordination_index * 0.2
            + min(1.0, n_act / 4.0) * 0.1
        )

        return TeammateNetworkResult(
            module=self.name,
            nodes=nodes,
            lead_id=lead_id,
            coverage=coverage,
            mesh_density=mesh_density,
            attach_plan=attach_plan,
            network_score=network_score,
            summary=(
                f"TeammateNetwork[{industry_id}]: lead={lead_id} active={n_act} "
                f"coverage={coverage:.2f} score={network_score:.3f}"
            ),
        )
