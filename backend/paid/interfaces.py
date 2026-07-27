"""
Interfaces for the 6 core paid components + supporting modules.

These are contracts (structural typing). Implementations live in sibling modules.
Interaction principles (not cycles):
  · Recursive Schemes     — each step may refine prior outputs once (no nested loops)
  · MTMF Specifications   — Meaning / Topology / Metrics / Form layers
  · Zone Clarity          — every energy/chip/map object declares a zone
  · Virtual Chips         — parametric hardware between agents
  · Parameter Management  — single merged param plane, reverse-influence applied once

OPEN: block-19 generativity may implement richer Form layer rendering later.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


# ── Core 6 ───────────────────────────────────────────────────────────────────


@runtime_checkable
class SystemDesignLibraryPort(Protocol):
    """Component 1 — load design templates by direction + category."""

    name: str

    def load_for_request(
        self,
        industry_id: str,
        track: str | None = None,
        request_kind: str | None = None,
        *,
        include_analysis: bool = True,
    ) -> dict[str, Any]: ...

    def blend_with_context(
        self,
        loaded: dict[str, Any],
        axes: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class VirtualChipLibraryPort(Protocol):
    """
    Component 2 — Virtual Chips.

    Not ordinary libraries: one template invented once; variants are cheap
    parametric graphs. Carry purpose, zone influence, causal chains, and
    reverse influence on the model. Depend on converters:
    environment · narrative_economy · parametric_contours.
    """

    name: str

    def build_graph(
        self,
        chip_refs: list[str],
        *,
        context: dict[str, Any] | None = None,
        library_params: dict[str, float] | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class FunctionCalculationEnginePort(Protocol):
    """Component 3 — functions, abstractions, derivative sensitivity."""

    name: str

    def sensitivity_report(
        self,
        params: dict[str, float],
        parameters: list[str] | None = None,
        top_k: int = 8,
    ) -> dict[str, Any]: ...

    def apply_reverse_influence(
        self,
        params: dict[str, float],
        reverse: dict[str, float],
    ) -> dict[str, float]: ...


@runtime_checkable
class EnergyFlowDisentanglerPort(Protocol):
    """
    Component 4 — Energy Flow Disentangler (Market Units).

    Sees wrong interconnections as entanglement; redistributes amplitude,
    zones, and energy direction for gradual situation resolution.
    """

    name: str

    def analyze(
        self,
        *,
        chips: list[dict[str, Any]] | None = None,
        zone_influence: dict[str, float] | None = None,
        scores: dict[str, float] | None = None,
        axes: dict[str, float] | None = None,
        chip_params: dict[str, float] | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class CalmPointImageGeneratorPort(Protocol):
    """Component 5 — low-entropy conceptual forms as assembly points."""

    name: str

    def generate(
        self,
        *,
        industry_id: str,
        request_id: str = "",
        idea_title: str = "",
        params: dict[str, float] | None = None,
        energy: dict[str, Any] | None = None,
        embedding: dict[str, Any] | None = None,
        reverse_influence: dict[str, float] | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class MegaMapBuilderPort(Protocol):
    """Component 6 — map hypotheses with uncertainty vs root task."""

    name: str

    def build(
        self,
        *,
        root_task: str,
        hypotheses: list[dict[str, Any]],
        params: dict[str, float] | None = None,
        output_plane: dict[str, float] | None = None,
        calm_point: dict[str, Any] | None = None,
        energy: dict[str, Any] | None = None,
        root_coords: dict[str, float] | None = None,
    ) -> dict[str, Any]: ...


# ── Supporting ───────────────────────────────────────────────────────────────


@runtime_checkable
class HypothesisModulesPort(Protocol):
    """Small modules from previous-version conclusions."""

    name: str

    def select(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class HypothesisLibraryPort(Protocol):
    """
    Iterative navigator: variants of previous stage + pattern search
    across step group with learning-weighted formulas.
    """

    name: str

    def navigate(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class ReaderPort(Protocol):
    """
    5-Stage Learning Interpreter — does NOT read a ready database.
    Builds meaning on the fly: Perception → Notation → Objectification
    → Interpretation → Application + Learning Loop.
    """

    name: str

    def explain(self, paid_bundle: dict[str, Any]) -> dict[str, Any]: ...

    def run_five_stages(self, paid_bundle: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class SituationMetricsPort(Protocol):
    """Revenue levers, delivery friction, margin pressure, leak maps."""

    name: str

    def analyze(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class MustAskPort(Protocol):
    """Gate before re-run: entities · flows · levers · jobs · metrics."""

    name: str

    def run(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class BlueOceanBridgePort(Protocol):
    """Meta-Reality Engine compatibility bridge."""

    name: str

    def synthesize(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class ConceptualEnginePort(Protocol):
    """
    OPEN final step: outgoing supply-chain vision via statistics
    + narrowing models. Preview is safe; plan() stays intentionally open.
    """

    name: str

    def preview(self, **kwargs: Any) -> dict[str, Any]: ...

    def plan(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class CriticalThinkingPort(Protocol):
    """
    Group indicators; compare paid vs parallel details; classify discrepancy;
    conclude possible founder error.
    """

    name: str

    def analyze(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class MetricTestsPort(Protocol):
    """Uncomplicated metric tests + informational compatibility."""

    name: str

    def run(self, **kwargs: Any) -> dict[str, Any]: ...


# ── 16-step stage map (corrected) ────────────────────────────────────────────

PAID_FLOW_STAGES: dict[str, dict[str, Any]] = {
    "A_intake": {
        "title": "Intake & Frame",
        "steps": [1, 2],
        "purpose": "Receive root task; extract params and conceptual coordinates",
    },
    "B_design_hardware": {
        "title": "Design Hardware",
        "steps": [3, 4],
        "purpose": "System Design Library + Virtual Chips (Zone Clarity, Parameter Mgmt)",
        "principles": [
            "Recursive Schemes",
            "MTMF Specifications",
            "Zone Clarity",
            "Virtual Chips",
            "Parameter Management",
        ],
    },
    "C_hypothesis_probe": {
        "title": "Hypothesis & Probe",
        "steps": [5, 6],
        "purpose": "Generate hypotheses; compare against root task",
    },
    "D_compute_energy": {
        "title": "Compute & Redistribute",
        "steps": [7, 8],
        "purpose": "Function plane + Market Units energy disentanglement",
    },
    "E_form_map": {
        "title": "Form & Map",
        "steps": [9, 10],
        "purpose": "Calm-point assembly forms first, then Mega Map with uncertainty",
        "note": "Corrected order: Calm Point seeds → Mega Map anchors (not map-then-form)",
    },
    "F_verify_explain": {
        "title": "Verify & Explain",
        "steps": [11, 12, 13],
        "purpose": "Metric tests, indicator grouping, Reader narration",
    },
    "G_critique_learn": {
        "title": "Critique & Learn",
        "steps": [14, 15],
        "purpose": "Paid vs parallel discrepancies + founder error; Hypothesis Library navigator",
    },
    "H_package": {
        "title": "Package Showcase",
        "steps": [16],
        "purpose": "Final result plane + paid showcase with custom positioning",
    },
}

PAID_FLOW_STEPS: dict[int, str] = {
    1: "Receive root task / client request",
    2: "Extract parameters and build initial conceptual coordinates",
    3: "Load relevant System Design Library (direction + category)",
    4: "Activate Virtual Chips as modular parametric hardware",
    5: "Generate primary hypotheses (modules + derivative sensitivity)",
    6: "Probe hypotheses against root task",
    7: "Function Calculation Engine (functions, abstractions, sensitivities)",
    8: "Energy Flow Disentangler — entanglement → redistribute flows",
    9: "Calm-Point Image Generator — low-entropy assembly forms",
    10: "Mega Map Builder — coordinates, uncertainty, root distance",
    11: "Metric tests + informational compatibility",
    12: "Group all indicators (zone, amplitude, sensitivity, direction, discrepancy)",
    13: "Reader 5-stage — Perception→Notation→Object→Interpret→Learn",
    14: "Discrepancies paid vs parallel; classify; founder-error conclusion",
    15: "Hypothesis Library update — deep one-step + group patterns (learning)",
    16: "Assemble final result plane + paid showcase (custom positioning)",
}

# Macro conceptual trajectory stages (visible path; not micro-steps)
CONCEPTUAL_TRAJECTORY_STAGES: tuple[str, ...] = (
    "raw_input",
    "design_hardware",
    "hypotheses",
    "compute_energy",
    "form_map",
    "verify",
    "learn_narrate",
    "deliverable",
    # intentional last open mark:
    "conceptual_engine_supply_chain_vision",
)

# Blue Ocean Identifier architecture blocks (exact names)
BLUE_OCEAN_BLOCKS: tuple[str, ...] = (
    "Synthesis Core",
    "Reality Layer Interface",
    "Symmetry Bridge",
    "Value Proposition Engine",
    "Engagement & Transaction Protocol",
    "Metrix Ledger & Operational Core",
)
