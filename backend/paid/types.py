"""
Shared types for Metrix AI Paid Product Core (block 18).

All paid components exchange these structures so the layer stays modular
and serializable (JSON-safe dicts via to_dict()).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RequestKind = Literal[
    "product",
    "model",
    "promo",
    "orientation",
    "full_package",
    "analysis",
]

ZoneName = Literal[
    "infa_sol",
    "cloud_sol",
    "structure_fi",
    "product_sol",
    "orientation",
    "market_units",
    "calm_point",
    "mega_map",
]


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


@dataclass
class DesignTemplate:
    """One system-design template from the System Design Library."""

    id: str
    name: str
    direction: str  # industry id
    category: str  # product | model | promo | orientation | analysis
    pattern: str
    base_architecture: list[str]
    default_params: dict[str, float] = field(default_factory=dict)
    chip_refs: list[str] = field(default_factory=list)
    zone_focus: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VirtualChip:
    """
    Parametric virtual “hardware” module.

    Invented once as a template; variants are cheap parametric graphs.
    Carries purpose, zone influence, causal chains, and reverse model influence.
    """

    id: str
    template_id: str
    purpose: str
    zone: str
    params: dict[str, float]
    causal_chain: list[str]
    converters: list[str]  # environment | narrative_economy | parametric_contours
    reverse_influence: dict[str, float]  # how chip feeds back into model weights
    amplitude: float = 0.5
    energy_direction: float = 0.0  # -1 sink .. +1 source
    variant_of: str | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["amplitude"] = round(clamp01(self.amplitude), 4)
        d["energy_direction"] = round(max(-1.0, min(1.0, self.energy_direction)), 4)
        d["params"] = {k: round(float(v), 4) for k, v in self.params.items()}
        d["reverse_influence"] = {
            k: round(float(v), 4) for k, v in self.reverse_influence.items()
        }
        return d


@dataclass
class SensitivityPoint:
    """How a parameter change affects the output plane."""

    parameter: str
    base_value: float
    delta: float
    output_delta: float
    derivative: float
    elasticity: float
    rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "parameter": self.parameter,
            "base_value": round(self.base_value, 4),
            "delta": round(self.delta, 4),
            "output_delta": round(self.output_delta, 4),
            "derivative": round(self.derivative, 6),
            "elasticity": round(self.elasticity, 4),
            "rank": self.rank,
        }


@dataclass
class EnergyNode:
    """Node in the energy-flow graph (Market Units)."""

    id: str
    zone: str
    amplitude: float
    direction: float  # signed energy direction
    entangled_with: list[str] = field(default_factory=list)
    entanglement_score: float = 0.0
    corrected_amplitude: float | None = None
    corrected_direction: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "zone": self.zone,
            "amplitude": round(self.amplitude, 4),
            "direction": round(self.direction, 4),
            "entangled_with": list(self.entangled_with),
            "entanglement_score": round(self.entanglement_score, 4),
            "corrected_amplitude": (
                None
                if self.corrected_amplitude is None
                else round(self.corrected_amplitude, 4)
            ),
            "corrected_direction": (
                None
                if self.corrected_direction is None
                else round(self.corrected_direction, 4)
            ),
        }


@dataclass
class CalmPointImage:
    """Conceptual form born from a low-entropy calm point."""

    id: str
    title: str
    entropy: float
    noise: float
    seed_vector: list[float]
    form_archetype: str
    visual_spec: dict[str, Any]
    assembly_role: str
    physics_method: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "entropy": round(self.entropy, 4),
            "noise": round(self.noise, 4),
            "seed_vector": [round(x, 4) for x in self.seed_vector],
            "form_archetype": self.form_archetype,
            "visual_spec": self.visual_spec,
            "assembly_role": self.assembly_role,
            "physics_method": self.physics_method,
            "notes": self.notes,
        }


@dataclass
class HypothesisModule:
    """Small hypothesis selected from prior-version conclusions."""

    id: str
    claim: str
    source: str
    confidence: float
    coords: dict[str, float]
    supporting_indicators: list[str] = field(default_factory=list)
    tension_with: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "claim": self.claim,
            "source": self.source,
            "confidence": round(clamp01(self.confidence), 4),
            "coords": {k: round(float(v), 4) for k, v in self.coords.items()},
            "supporting_indicators": list(self.supporting_indicators),
            "tension_with": list(self.tension_with),
        }


@dataclass
class MegaMapPoint:
    """Point on the Mega Map with coordinate uncertainty."""

    hypothesis_id: str
    x: float
    y: float
    z: float
    uncertainty: float
    distance_to_root: float
    label: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "z": round(self.z, 4),
            "uncertainty": round(self.uncertainty, 4),
            "distance_to_root": round(self.distance_to_root, 4),
            "label": self.label,
        }


@dataclass
class IndicatorGroup:
    """Grouped indicators for Critical Thinking Layer."""

    group_key: str
    by: str  # zone | amplitude | derivative_sensitivity | energy_direction | discrepancy_type
    members: list[str]
    description: str
    severity: float
    discrepancy_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_key": self.group_key,
            "by": self.by,
            "members": list(self.members),
            "description": self.description,
            "severity": round(clamp01(self.severity), 4),
            "discrepancy_type": self.discrepancy_type,
        }


# Discrepancy reason classes (paid result vs parallel details)
DiscrepancyReason = Literal[
    "param_drift",
    "zone_desync",
    "energy_conflict",
    "map_root_divergence",
    "metric_incompatibility",
    "hypothesis_overfit",
    "calm_premature",
    "parallel_detail_richer",
    "paid_overclaim",
    "founder_frame_error",
    "unknown",
]


@dataclass
class DiscrepancyRecord:
    """Paid-part result vs parallel detail mismatch."""

    id: str
    paid_signal: str
    parallel_signal: str
    delta: float
    reason: str
    chosen_variant: str  # "paid" | "parallel" | "blend" | "hold"
    severity: float
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "paid_signal": self.paid_signal,
            "parallel_signal": self.parallel_signal,
            "delta": round(self.delta, 4),
            "reason": self.reason,
            "chosen_variant": self.chosen_variant,
            "severity": round(clamp01(self.severity), 4),
            "detail": self.detail,
        }


@dataclass
class FounderErrorConclusion:
    """
    Possible founder (system-author / framing) error when paid path
    systematically diverges from parallel verified details.
    """

    suspected: bool
    confidence: float
    error_class: str  # none | frame_bias | metric_blind_spot | over_generalization | zone_blindness
    rationale: str
    recommended_correction: str
    open_point: str = (
        "OPEN: human founder review may override automated suspicion."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "suspected": self.suspected,
            "confidence": round(clamp01(self.confidence), 4),
            "error_class": self.error_class,
            "rationale": self.rationale,
            "recommended_correction": self.recommended_correction,
            "open_point": self.open_point,
        }


@dataclass
class MetricTestResult:
    """Single uncomplicated metric test."""

    id: str
    name: str
    passed: bool
    score: float
    threshold: float
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "passed": self.passed,
            "score": round(self.score, 4),
            "threshold": round(self.threshold, 4),
            "detail": self.detail,
        }


@dataclass
class ConceptualCoords:
    """Initial conceptual coordinates of the request (step 2)."""

    x_product: float
    y_model: float
    z_promo: float
    clarity: float
    risk: float
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "x_product": round(self.x_product, 4),
            "y_model": round(self.y_model, 4),
            "z_promo": round(self.z_promo, 4),
            "clarity": round(self.clarity, 4),
            "risk": round(self.risk, 4),
            "notes": self.notes,
        }


@dataclass
class FlowStepResult:
    """One step of the 16-step paid flow."""

    step: int
    name: str
    stage: str
    status: str  # ok | skip | open
    payload: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "name": self.name,
            "stage": self.stage,
            "status": self.status,
            "payload": self.payload,
            "notes": self.notes,
        }


@dataclass
class LearningState:
    """
    Lightweight learning elements for Hypothesis Library navigator.

    EMA of lever usefulness and pattern weights — deterministic “memory”
    within one request (and optional prior_state from previous iteration).
    OPEN: durable cross-request learning store is intentional future space.
    """

    iteration: int = 0
    lever_ema: dict[str, float] = field(default_factory=dict)
    pattern_weights: dict[str, float] = field(default_factory=dict)
    step_scores: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "lever_ema": {k: round(float(v), 4) for k, v in self.lever_ema.items()},
            "pattern_weights": {
                k: round(float(v), 4) for k, v in self.pattern_weights.items()
            },
            "step_scores": [round(s, 4) for s in self.step_scores],
            "open_point": "OPEN: persist LearningState across requests for true online learning.",
        }


# ── Phenomenon → Notation → Object → Virtual Asset (Blue Ocean / Reader) ─────


@dataclass
class PhenomenonUnit:
    """Raw phenomenon as sensed (pre-notation)."""

    id: str
    raw: str
    source: str  # business | scores | energy | oae | chip | parallel
    amplitude: float = 0.5
    zone: str = "orientation"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "raw": self.raw,
            "source": self.source,
            "amplitude": round(clamp01(self.amplitude), 4),
            "zone": self.zone,
        }


@dataclass
class NotationUnit:
    """Named / bounded structure after Reader stage 2."""

    id: str
    name: str
    boundary: str
    phenomenon_id: str
    category: str  # entity | flow | lever | job | metric | zone | asset

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "boundary": self.boundary,
            "phenomenon_id": self.phenomenon_id,
            "category": self.category,
        }


@dataclass
class VirtualAsset:
    """
    Objectified unit with weight, price signal, owner, and branding.

    Native end of: Phenomenon → Notation → Object → Virtual Asset.
    Carried by Virtual Chips and produced by Reader stage 3.
    """

    id: str
    name: str
    weight: float  # economic / decision mass 0..1+
    price_signal: float  # relative value density, not a quote
    owner: str  # founder | client | platform | agent | market
    branding: str  # short brandable label
    zone: str
    notation_id: str
    chip_id: str | None = None
    tags: list[str] = field(default_factory=list)
    open_point: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "weight": round(self.weight, 4),
            "price_signal": round(self.price_signal, 4),
            "owner": self.owner,
            "branding": self.branding,
            "zone": self.zone,
            "notation_id": self.notation_id,
            "chip_id": self.chip_id,
            "tags": list(self.tags),
            "open_point": self.open_point,
        }


@dataclass
class ConceptualStep:
    """One visible mark on the conceptual trajectory."""

    index: int
    name: str
    stage: str  # e.g. raw_input | hypothesis | mega_map | deliverable
    status: str  # ok | open | skip | blocked
    input_summary: str
    output_summary: str
    coords_delta: float = 0.0  # distance shift vs previous step
    learning_note: str = ""
    open_point: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "stage": self.stage,
            "status": self.status,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "coords_delta": round(self.coords_delta, 4),
            "learning_note": self.learning_note,
            "open_point": self.open_point,
        }


@dataclass
class ConceptualTrajectory:
    """
    Visible path: raw input → hypotheses → Mega Map → paid deliverable.

    Used by Reader stage 5 and Hypothesis Library for learning feedback.
    Final OPEN step reserved for Conceptual Engine (supply-chain vision).
    """

    steps: list[ConceptualStep] = field(default_factory=list)
    root_task: str = ""
    final_status: str = "in_progress"
    residual_uncertainty: float = 0.35
    next_open_engine: str = "ConceptualEngine.supply_chain_vision"

    def append(self, step: ConceptualStep) -> None:
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_task": self.root_task,
            "step_count": len(self.steps),
            "steps": [s.to_dict() for s in self.steps],
            "final_status": self.final_status,
            "residual_uncertainty": round(clamp01(self.residual_uncertainty), 4),
            "path_summary": " → ".join(s.name for s in self.steps),
            "next_open_engine": self.next_open_engine,
            "open_point": (
                "OPEN: Conceptual Engine — vision of outgoing supply-chain stages "
                "from statistics + narrowing models (last planning step)."
            ),
        }
