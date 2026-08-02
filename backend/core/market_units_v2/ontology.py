"""
Ontology Engine — original ontological combinations → task algorithms.

Combines problem family × industry entity × coordination mode into
named ontological pairs, then generates algorithms for different tasks
(ops fix, product pack, promo proof, tech write, teammate attach).
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


# Ontological primitives (axes of combination)
ONTO_AXES: dict[str, list[str]] = {
    "substance": ["void", "flow", "constraint", "signal", "artifact"],
    "relation": ["handoff", "feedback", "mirror", "cut", "bridge"],
    "time": ["intake", "pilot", "scale", "repair", "exit"],
    "agency": ["reader", "teammate", "buyer", "system", "founder"],
}

# Task types for algorithm generation
TASK_TYPES = (
    "ops_stabilization",
    "product_packaging",
    "promo_proof",
    "tech_write",
    "teammate_attach",
    "metric_lock",
    "risk_containment",
)

INDUSTRY_ENTITY: dict[str, str] = {
    "ai-agencies": "delivery_mesh",
    "api-for-devs": "call_graph",
    "cloud-economy": "call_graph",
    "cost-engineering": "parameter_space",
    "chipmaking": "design_loop",
    "telecom": "sla_surface",
    "device-assembly": "station_graph",
    "asset-decisions": "decision_desk",
    "freelace-d2c": "document_offramp",
    "d2c-offramp": "document_offramp",
    "expert-services": "offer_surface",
    "ecommerce": "sku_channel",
}


@dataclass
class OntoCombo:
    id: str
    substance: str
    relation: str
    time: str
    agency: str
    entity: str
    fit: float
    narrative: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskAlgorithm:
    task_type: str
    name: str
    steps: list[str]
    inputs: list[str]
    outputs: list[str]
    combo_id: str
    estimated_gain: float
    failure_guard: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OntologyResult:
    module: str
    combos: list[OntoCombo]
    primary_combo: OntoCombo | None
    algorithms: list[TaskAlgorithm]
    ontology_fit: float
    figurative_awareness: dict[str, Any]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "combos": [c.to_dict() for c in self.combos],
            "primary_combo": self.primary_combo.to_dict() if self.primary_combo else None,
            "algorithms": [a.to_dict() for a in self.algorithms],
            "ontology_fit": round(self.ontology_fit, 4),
            "figurative_awareness": self.figurative_awareness,
            "summary": self.summary,
        }


def _pick_axis(axis: str, seed: int, bias: int = 0) -> str:
    opts = ONTO_AXES[axis]
    return opts[(seed + bias) % len(opts)]


class OntologyEngine:
    """Generate ontological combinations and task-specific algorithms."""

    name = "Ontology Engine"

    def generate(
        self,
        *,
        industry_id: str,
        primary_problem: dict[str, Any] | None = None,
        family_pressure: dict[str, float] | None = None,
        signals: dict[str, float] | None = None,
        coordination_index: float = 0.5,
        originality_pressure: float = 0.4,
        readiness_band: str = "orientation_needed",
        product_sku: str = "",
    ) -> OntologyResult:
        family_pressure = family_pressure or {}
        signals = signals or {}
        primary_problem = primary_problem or {}
        entity = INDUSTRY_ENTITY.get(industry_id, "system_surface")
        seed_src = f"{industry_id}|{primary_problem.get('id')}|{product_sku}"
        seed = int(hashlib.md5(seed_src.encode()).hexdigest()[:8], 16)

        # Bias axes from signals / problem family
        family = str(primary_problem.get("family") or "ops")
        substance_bias = {
            "ops": 1,  # flow
            "cost": 2,  # constraint
            "product": 0,  # void
            "promo": 3,  # signal
            "liquidity": 4,  # artifact
            "metrics": 3,
        }.get(family, 0)
        relation_bias = 0 if float(signals.get("ops_friction", 0)) > 0.4 else 4  # handoff vs bridge
        time_bias = {
            "execution_ready": 2,
            "pilot_ready": 1,
            "orientation_needed": 0,
            "intake_thin": 0,
        }.get(readiness_band, 0)
        agency_bias = 1 if "teammate" in (product_sku or "").lower() else 0

        combos: list[OntoCombo] = []
        for i in range(3):
            s = _pick_axis("substance", seed, substance_bias + i)
            r = _pick_axis("relation", seed, relation_bias + i * 2)
            t = _pick_axis("time", seed, time_bias + i)
            a = _pick_axis("agency", seed, agency_bias + i)
            fit = _clamp01(
                0.45
                + coordination_index * 0.2
                + originality_pressure * 0.15
                + float(primary_problem.get("leverage") or 0.3) * 0.15
                - i * 0.06
            )
            cid = f"{s[:3]}-{r[:3]}-{t[:3]}-{a[:3]}-{i}"
            narrative = (
                f"{entity}: treat {s} via {r} at {t}-time under {a} agency "
                f"(family={family})"
            )
            combos.append(
                OntoCombo(
                    id=cid,
                    substance=s,
                    relation=r,
                    time=t,
                    agency=a,
                    entity=entity,
                    fit=fit,
                    narrative=narrative,
                )
            )
        combos.sort(key=lambda c: -c.fit)
        primary = combos[0] if combos else None

        # Task algorithms derived from primary combo + family
        algorithms = self._algorithms_for(
            primary=primary,
            family=family,
            industry_id=industry_id,
            product_sku=product_sku,
            problem=primary_problem,
            coordination_index=coordination_index,
        )

        ontology_fit = _clamp01(
            (primary.fit if primary else 0.4) * 0.6
            + coordination_index * 0.25
            + min(1.0, len(algorithms) / 5.0) * 0.15
        )

        # Figurative awareness — specialized pass on same core architecture
        figurative = {
            "mode": "specialized_pass_on_core_arch",
            "image": primary.narrative if primary else "system surface without image",
            "metaphor": self._metaphor(primary),
            "awareness_score": round(
                _clamp01(ontology_fit * 0.7 + originality_pressure * 0.3), 4
            ),
            "note": (
                "Figurative awareness reuses Decision/OAE geometry but narrates "
                "the combo as an operational image for founder + teammate alignment."
            ),
        }

        return OntologyResult(
            module=self.name,
            combos=combos,
            primary_combo=primary,
            algorithms=algorithms,
            ontology_fit=ontology_fit,
            figurative_awareness=figurative,
            summary=(
                f"Ontology: fit={ontology_fit:.3f} primary="
                + (primary.id if primary else "none")
                + f" algorithms={len(algorithms)}"
            ),
        )

    def _metaphor(self, combo: OntoCombo | None) -> str:
        if not combo:
            return "blank map"
        table = {
            ("void", "bridge"): "arch over a gap — do not fill the void, span it",
            ("flow", "handoff"): "relay baton — speed only matters if grip is clean",
            ("constraint", "cut"): "surgical cut — remove fat parameter without nerve damage",
            ("signal", "mirror"): "mirror signal — buyer sees their fin model, not yours",
            ("artifact", "bridge"): "document as bridge — liquidity lives in the artifact",
        }
        return table.get(
            (combo.substance, combo.relation),
            f"{combo.substance} shaped by {combo.relation} under {combo.agency}",
        )

    def _algorithms_for(
        self,
        *,
        primary: OntoCombo | None,
        family: str,
        industry_id: str,
        product_sku: str,
        problem: dict[str, Any],
        coordination_index: float,
    ) -> list[TaskAlgorithm]:
        combo_id = primary.id if primary else "default"
        entity = primary.entity if primary else industry_id
        leverage = float(problem.get("leverage") or 0.4)
        gain_base = _clamp01(0.35 + leverage * 0.3 + coordination_index * 0.2)

        family_to_tasks: dict[str, list[str]] = {
            "ops": ["ops_stabilization", "teammate_attach", "metric_lock", "tech_write"],
            "cost": ["ops_stabilization", "product_packaging", "metric_lock", "tech_write"],
            "product": ["product_packaging", "tech_write", "metric_lock", "teammate_attach"],
            "promo": ["promo_proof", "product_packaging", "metric_lock"],
            "liquidity": ["product_packaging", "tech_write", "teammate_attach", "promo_proof"],
            "metrics": ["metric_lock", "ops_stabilization", "tech_write"],
        }
        tasks = family_to_tasks.get(family, list(TASK_TYPES[:4]))
        if "risk_containment" not in tasks and leverage > 0.65:
            tasks = list(tasks) + ["risk_containment"]

        out: list[TaskAlgorithm] = []
        for tt in tasks:
            out.append(self._one_algorithm(tt, combo_id, entity, product_sku, gain_base, primary))
        return out

    def _one_algorithm(
        self,
        task_type: str,
        combo_id: str,
        entity: str,
        product_sku: str,
        gain_base: float,
        primary: OntoCombo | None,
    ) -> TaskAlgorithm:
        rel = primary.relation if primary else "bridge"
        sub = primary.substance if primary else "void"
        templates: dict[str, dict[str, Any]] = {
            "ops_stabilization": {
                "name": f"Stabilize {entity} via {rel}",
                "steps": [
                    f"Map control points on {entity}",
                    f"Apply {rel} on highest-friction edge",
                    f"Absorb residual {sub} into constructor slot",
                    "Recompute VVI/ER after one cycle",
                    "Lock ops gate before scale",
                ],
                "inputs": ["system_reader.signals", "problem_lattice.primary"],
                "outputs": ["ops_control_loop", "vvi_delta"],
                "guard": "Do not add agents before control loop exists",
            },
            "product_packaging": {
                "name": f"Package {product_sku or entity} as SKU",
                "steps": [
                    "Select application point from Market Unit",
                    f"Bind ontology combo {combo_id} to offer one-liner",
                    "Compose acceptance criteria from reverse categories",
                    "Attach price ladder (simple offer → pilot)",
                    "Export package deliverable spine",
                ],
                "inputs": ["market_unit.product", "ontology.primary"],
                "outputs": ["sku_pack", "acceptance_criteria"],
                "guard": "No SKU without measurable acceptance",
            },
            "promo_proof": {
                "name": "Buyer-facing proof card",
                "steps": [
                    "Extract joint surplus (coop open-opp)",
                    "Render fin model or before/after card",
                    "Mirror buyer language (figurative awareness)",
                    "Point to paid SKU without guarantee inflation",
                ],
                "inputs": ["memo_convert.open_opportunities", "fin_models"],
                "outputs": ["proof_card", "promo_angle"],
                "guard": "No yield/ROI guarantees on asset niches",
            },
            "tech_write": {
                "name": "SpecsForge tech-write from combo",
                "steps": [
                    f"Translate {combo_id} into technical-task language",
                    "List reverse categories → constraints",
                    "Write acceptance + VVI/ER/RRC improvement log",
                    "Handoff to Terminal Teammate / Expert",
                ],
                "inputs": ["memo_convert.technical_tasks", "ontology.algorithms"],
                "outputs": ["tech_task", "specs_tree"],
                "guard": "Gate tech-write after consult geometry exists",
            },
            "teammate_attach": {
                "name": "Terminal Teammate mesh attach",
                "steps": [
                    "Pick lead role for primary problem family",
                    "Wire handoff matrix edges to offer surface",
                    "Set milestone proof + escrow cut if workers path",
                    "Run one specialized figurative pass for team alignment",
                ],
                "inputs": ["teammate_network", "coordination.handoff_matrix"],
                "outputs": ["teammate_plan", "role_matrix"],
                "guard": "Coverage < 0.5 → spin missing roles first",
            },
            "metric_lock": {
                "name": "Lock Success TZ + PQI",
                "steps": [
                    "Compose Success Metrics TZ for this request",
                    "Bind PQI levers to primary problem",
                    "Set pilot composite target",
                    "Expose metric firmware to support system",
                ],
                "inputs": ["metric_composer", "success_metrics"],
                "outputs": ["success_tz", "pqi_baseline"],
                "guard": "Do not pilot without composite target",
            },
            "risk_containment": {
                "name": f"Contain {sub} risk on {entity}",
                "steps": [
                    "Identify failure_mode from problem lattice",
                    "Install kill-switch / gate on critical path",
                    "Lower deadlock risk via coordination rebalance",
                    "Re-score situation after gate",
                ],
                "inputs": ["problem_lattice", "coordination.deadlock_risk"],
                "outputs": ["risk_gates", "deadlock_delta"],
                "guard": "High deadlock → freeze mode switch",
            },
        }
        t = templates.get(task_type) or templates["ops_stabilization"]
        return TaskAlgorithm(
            task_type=task_type,
            name=str(t["name"]),
            steps=list(t["steps"]),
            inputs=list(t["inputs"]),
            outputs=list(t["outputs"]),
            combo_id=combo_id,
            estimated_gain=round(_clamp01(gain_base + (0.05 if task_type == "teammate_attach" else 0)), 4),
            failure_guard=str(t["guard"]),
        )
