"""
Coordination Layer — multi-node coordination computations.

Computes how system reader, problems, metrics, teammates, and offers
should coordinate: handoff matrix, load balance, deadlock risk, sync score.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


COORD_NODES = (
    "system_reader",
    "problem_lattice",
    "metric_composer",
    "ontology",
    "teammate_network",
    "offer_surface",
    "memo_convert",
    "decision_core",
)


@dataclass
class CoordEdge:
    source: str
    target: str
    weight: float
    kind: str  # data | control | handoff | feedback
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CoordinationResult:
    module: str
    coordination_index: float
    sync_score: float
    deadlock_risk: float
    load_balance: float
    handoff_matrix: dict[str, dict[str, float]]
    edges: list[CoordEdge]
    node_loads: dict[str, float]
    critical_path: list[str]
    recommendations: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "coordination_index": round(self.coordination_index, 4),
            "sync_score": round(self.sync_score, 4),
            "deadlock_risk": round(self.deadlock_risk, 4),
            "load_balance": round(self.load_balance, 4),
            "handoff_matrix": {
                a: {b: round(w, 4) for b, w in row.items()}
                for a, row in self.handoff_matrix.items()
            },
            "edges": [e.to_dict() for e in self.edges],
            "node_loads": {k: round(v, 4) for k, v in self.node_loads.items()},
            "critical_path": self.critical_path,
            "recommendations": self.recommendations,
            "summary": self.summary,
        }


class CoordinationLayer:
    """
    Strong coordination computation layer.

    Inputs: density, problem pressure, PQI components, teammate mesh readiness.
    Outputs: coordination_index + handoff matrix used by ontology + pipeline.
    """

    name = "Coordination Layer"

    def compute(
        self,
        *,
        density: float = 0.5,
        readiness_band: str = "orientation_needed",
        family_pressure: dict[str, float] | None = None,
        primary_leverage: float = 0.0,
        signals: dict[str, float] | None = None,
        teammate_coverage: float = 0.5,
        ontology_fit: float = 0.5,
        decision_mode: str = "scoring",
        health: float = 0.5,
    ) -> CoordinationResult:
        family_pressure = family_pressure or {}
        signals = signals or {}

        # Node loads: how hard each subsystem is working
        ops_p = float(signals.get("ops_friction", 0.3))
        cost_p = float(signals.get("cost_pressure", 0.3))
        product_void = float(signals.get("product_void", 0.3))

        node_loads = {
            "system_reader": _clamp01(0.4 + (1.0 - density) * 0.4),
            "problem_lattice": _clamp01(0.35 + primary_leverage * 0.45 + ops_p * 0.2),
            "metric_composer": _clamp01(0.4 + sum(family_pressure.values()) * 0.15),
            "ontology": _clamp01(0.35 + product_void * 0.35 + ontology_fit * 0.2),
            "teammate_network": _clamp01(0.3 + ops_p * 0.4 + (1.0 - teammate_coverage) * 0.3),
            "offer_surface": _clamp01(0.35 + cost_p * 0.25 + primary_leverage * 0.25),
            "memo_convert": _clamp01(0.4 + product_void * 0.3 + (1.0 - health) * 0.2),
            "decision_core": _clamp01(
                0.4
                + (0.2 if decision_mode in ("generative_development", "dual_ricochet") else 0.05)
                + primary_leverage * 0.2
            ),
        }

        # Canonical coordination edges (data/control flow)
        edge_specs: list[tuple[str, str, str, float, str]] = [
            ("system_reader", "problem_lattice", "data", 0.9, "signals → problems"),
            ("problem_lattice", "metric_composer", "data", 0.85, "pressure → metrics"),
            ("metric_composer", "ontology", "control", 0.8, "PQI drives combo pick"),
            ("ontology", "teammate_network", "handoff", 0.82, "algorithm → roles"),
            ("teammate_network", "offer_surface", "handoff", 0.78, "roles → SKU attach"),
            ("offer_surface", "memo_convert", "data", 0.75, "offer → tech tasks"),
            ("memo_convert", "decision_core", "feedback", 0.7, "tasks → mode refine"),
            ("decision_core", "system_reader", "feedback", 0.55, "mode → re-read pressure"),
            ("problem_lattice", "teammate_network", "control", 0.72, "primary problem → lead role"),
            ("metric_composer", "offer_surface", "control", 0.68, "PQI → pricing confidence"),
            ("ontology", "memo_convert", "data", 0.74, "task algorithms → Specs language"),
            ("system_reader", "metric_composer", "data", 0.65, "density → clarity"),
        ]

        band_mult = {
            "execution_ready": 1.05,
            "pilot_ready": 1.0,
            "orientation_needed": 0.9,
            "intake_thin": 0.78,
        }.get(readiness_band, 0.9)

        edges: list[CoordEdge] = []
        handoff: dict[str, dict[str, float]] = {n: {} for n in COORD_NODES}
        for src, tgt, kind, base_w, note in edge_specs:
            # weight damped by source load saturation
            load_src = node_loads.get(src, 0.5)
            load_tgt = node_loads.get(tgt, 0.5)
            # high load both sides → risk of contention
            contention = load_src * load_tgt
            w = _clamp01(base_w * band_mult * (1.0 - contention * 0.25))
            edges.append(CoordEdge(src, tgt, w, kind, note))
            handoff[src][tgt] = w

        # Sync: mean of critical handoff weights
        critical_path = [
            "system_reader",
            "problem_lattice",
            "metric_composer",
            "ontology",
            "teammate_network",
            "offer_surface",
        ]
        path_weights: list[float] = []
        for i in range(len(critical_path) - 1):
            a, b = critical_path[i], critical_path[i + 1]
            path_weights.append(handoff.get(a, {}).get(b, 0.5))
        sync_score = _clamp01(sum(path_weights) / max(1, len(path_weights)))

        loads = list(node_loads.values())
        mean_load = sum(loads) / max(1, len(loads))
        variance = sum((x - mean_load) ** 2 for x in loads) / max(1, len(loads))
        load_balance = _clamp01(1.0 - variance * 4.0)  # lower variance → better balance

        # Deadlock: feedback loops under high load
        feedback_w = [e.weight for e in edges if e.kind == "feedback"]
        deadlock_risk = _clamp01(
            (1.0 - sync_score) * 0.4
            + (1.0 - load_balance) * 0.3
            + (sum(feedback_w) / max(1, len(feedback_w))) * 0.15 * mean_load
            + primary_leverage * 0.1
        )

        coordination_index = _clamp01(
            sync_score * 0.4
            + load_balance * 0.25
            + (1.0 - deadlock_risk) * 0.2
            + teammate_coverage * 0.1
            + ontology_fit * 0.05
        )

        recs: list[str] = []
        if deadlock_risk > 0.45:
            recs.append("Break feedback loop: freeze decision mode before re-read")
        if load_balance < 0.55:
            hottest = max(node_loads.items(), key=lambda x: x[1])
            recs.append(f"Rebalance load off {hottest[0]} (load={hottest[1]:.2f})")
        if sync_score < 0.6:
            recs.append("Strengthen critical path handoffs (reader→problems→metrics)")
        if teammate_coverage < 0.5:
            recs.append("Spin up missing Terminal Teammate roles for primary problem")
        if not recs:
            recs.append("Coordination healthy — proceed to ontology algorithms + offers")

        return CoordinationResult(
            module=self.name,
            coordination_index=coordination_index,
            sync_score=sync_score,
            deadlock_risk=deadlock_risk,
            load_balance=load_balance,
            handoff_matrix=handoff,
            edges=edges,
            node_loads=node_loads,
            critical_path=critical_path,
            recommendations=recs,
            summary=(
                f"Coordination: CI={coordination_index:.3f} sync={sync_score:.2f} "
                f"deadlock={deadlock_risk:.2f} balance={load_balance:.2f}"
            ),
        )
