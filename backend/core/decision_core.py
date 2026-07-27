"""
Enhanced Decision Making Core (VerdictLattice+)
===============================================

Полная awareness текущего project state:
- анализирует геометрию проекта (axes + scores + metrics + success TZ)
- предлагает improving decisions
- структурирует thinking process
- решает, когда переключать режимы:
    scoring → generative_development → recursive_refinement

Готов к стыковке с:
- 18: paid product core (backend/paid/)
- 19: generativity concept (backend/generative/)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ProcessingMode = Literal[
    "scoring",
    "generative_development",
    "recursive_refinement",
    "dual_ricochet",
    "paid_handoff",  # reserved for block 18
]


@dataclass
class ProjectGeometry:
    """Сводка геометрии текущего проекта/запроса."""

    industry_id: str
    axes: dict[str, float]
    scores: dict[str, float]
    vvi: float
    er: float
    rrc: float
    health: float
    info_roi: float
    success_composite: float
    success_target: float
    specs_ready: bool
    dominant_axis: str
    tension: float  # max-min of track fits
    voids_pressure: float
    monetization_pull: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ThinkingStep:
    stage: str
    question: str
    finding: str
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ImprovingDecision:
    id: str
    title: str
    rationale: str
    priority: int
    owner: str
    expected_gain: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModeSwitch:
    from_mode: str
    to_mode: ProcessingMode
    reason: str
    confidence: float
    triggers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionCoreResult:
    module: str
    geometry: ProjectGeometry
    thinking_process: list[ThinkingStep]
    improving_decisions: list[ImprovingDecision]
    active_mode: ProcessingMode
    mode_switch: ModeSwitch
    awareness_score: float
    ownership_matrix: dict[str, str]
    handoff_flags: dict[str, bool]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "geometry": self.geometry.to_dict(),
            "thinking_process": [t.to_dict() for t in self.thinking_process],
            "improving_decisions": [d.to_dict() for d in self.improving_decisions],
            "active_mode": self.active_mode,
            "mode_switch": self.mode_switch.to_dict(),
            "awareness_score": self.awareness_score,
            "ownership_matrix": self.ownership_matrix,
            "handoff_flags": self.handoff_flags,
            "summary": self.summary,
        }


class DecisionMakingCore:
    """
    Enhanced Decision Making Core.

    Входы: orientation, metrics, success scorecard, pragma splits, system log features.
    Выход: geometry awareness + mode + decisions + thinking trace.
    """

    name = "Enhanced Decision Making Core"

    def analyze(
        self,
        *,
        industry_id: str,
        orientation: dict[str, Any],
        vvi: float,
        er: float,
        rrc: float,
        health: float,
        info_roi: float,
        success_composite: float,
        success_target: float,
        success_influence: dict[str, Any] | None = None,
        pragma_splits: list[dict[str, Any]] | None = None,
        system_features: dict[str, Any] | None = None,
        specs_ready: bool = False,
        idea_title: str = "",
    ) -> DecisionCoreResult:
        scores = dict(orientation.get("scores") or {})
        axes = dict((orientation.get("frame") or {}).get("axes") or {})
        base_mode = str(orientation.get("operating_mode") or "balanced_product_path")
        influence = success_influence or {}
        splits = pragma_splits or []
        sys_f = system_features or {}

        geometry = self._geometry(
            industry_id,
            axes,
            scores,
            vvi,
            er,
            rrc,
            health,
            info_roi,
            success_composite,
            success_target,
            specs_ready,
        )
        thinking = self._thinking(geometry, base_mode, splits, sys_f)
        switch = self._choose_mode(geometry, influence, splits, base_mode)
        decisions = self._improving_decisions(geometry, switch, idea_title, sys_f)
        awareness = self._awareness(geometry, thinking, decisions)

        ownership = {
            "orientation": "OrientationForge",
            "specs": "SpecsForge Recursive Oracle",
            "mode_switch": self.name,
            "oae": "Main Operational Analytics Engine",
            "scoring": "Success Metrics + seeds",
            "generative": "backend/generative (block 19)",
            "paid_product": "backend/paid (block 18)",
            "pricing_close": "human",
            "promo": "Promo Automation",
        }
        handoff = {
            "ready_for_demo": awareness >= 0.45 and bool(idea_title),
            "ready_for_paid_block_18": info_roi >= 1.8 and success_composite >= 0.5,
            "needs_generative_19": switch.to_mode
            in ("generative_development", "dual_ricochet"),
            "needs_human_price": info_roi >= 1.8,
            "specs_gate": not specs_ready and vvi > 0.45,
        }

        summary = (
            f"{self.name}: awareness={awareness:.2f}, mode={switch.to_mode}, "
            f"decisions={len(decisions)}, tension={geometry.tension:.2f}, "
            f"dominant={geometry.dominant_axis}."
        )
        return DecisionCoreResult(
            module=self.name,
            geometry=geometry,
            thinking_process=thinking,
            improving_decisions=decisions,
            active_mode=switch.to_mode,
            mode_switch=switch,
            awareness_score=round(awareness, 4),
            ownership_matrix=ownership,
            handoff_flags=handoff,
            summary=summary,
        )

    def _geometry(
        self,
        industry_id: str,
        axes: dict[str, float],
        scores: dict[str, float],
        vvi: float,
        er: float,
        rrc: float,
        health: float,
        info_roi: float,
        success_composite: float,
        success_target: float,
        specs_ready: bool,
    ) -> ProjectGeometry:
        ax = {
            "value_density": float(axes.get("value_density", 0.5)),
            "time_pressure": float(axes.get("time_pressure", 0.4)),
            "complexity": float(axes.get("complexity", 0.5)),
            "monetization_fit": float(axes.get("monetization_fit", 0.5)),
            "risk": float(axes.get("risk", 0.25)),
        }
        sc = {
            "product_fit": float(scores.get("product_fit", 0.5)),
            "model_fit": float(scores.get("model_fit", 0.5)),
            "promo_fit": float(scores.get("promo_fit", 0.5)),
            "overall_orientation": float(scores.get("overall_orientation", 0.5)),
            "readiness": float(scores.get("readiness", 0.5)),
        }
        fits = [sc["product_fit"], sc["model_fit"], sc["promo_fit"]]
        tension = max(fits) - min(fits)
        dominant = max(ax.items(), key=lambda x: x[1])[0]
        return ProjectGeometry(
            industry_id=industry_id,
            axes=ax,
            scores=sc,
            vvi=float(vvi),
            er=float(er),
            rrc=float(rrc),
            health=float(health),
            info_roi=float(info_roi),
            success_composite=float(success_composite),
            success_target=float(success_target),
            specs_ready=specs_ready,
            dominant_axis=dominant,
            tension=round(tension, 4),
            voids_pressure=round(float(vvi) * (1.0 - float(er) * 0.5), 4),
            monetization_pull=round(
                0.5 * ax["monetization_fit"] + 0.5 * sc["promo_fit"], 4
            ),
        )

    def _thinking(
        self,
        g: ProjectGeometry,
        base_mode: str,
        splits: list[dict[str, Any]],
        sys_f: dict[str, Any],
    ) -> list[ThinkingStep]:
        steps = [
            ThinkingStep(
                stage="sense",
                question="Where does this project sit in industry geometry?",
                finding=(
                    f"dominant_axis={g.dominant_axis}, "
                    f"readiness={g.scores['readiness']:.2f}, "
                    f"voids_pressure={g.voids_pressure:.2f}"
                ),
                next_action="Map track tension and success gaps",
            ),
            ThinkingStep(
                stage="structure",
                question="Is thinking balanced across Product / Models / Promo?",
                finding=f"tension={g.tension:.2f}, base_operating_mode={base_mode}",
                next_action="Choose processing mode (score / generate / refine)",
            ),
            ThinkingStep(
                stage="metrics_firmware",
                question="What does VVI/ER/RRC + success TZ say?",
                finding=(
                    f"VVI={g.vvi:.2f} ER={g.er:.2f} RRC={g.rrc:.2f} "
                    f"success={g.success_composite:.2f}/{g.success_target:.2f}"
                ),
                next_action="Fire pragma splits if combinations match",
            ),
            ThinkingStep(
                stage="pragma",
                question="Any splitting points from Pragma phenomena?",
                finding=f"{len(splits)} split(s): "
                + ", ".join(s.get("phenomenon", "?") for s in splits[:4]),
                next_action="Route to OAE / generative / refine",
            ),
            ThinkingStep(
                stage="system_memory",
                question="What does the global request log suggest?",
                finding=(
                    f"log_n={sys_f.get('n_requests', 0)}, "
                    f"patterns={sys_f.get('recurring_patterns', [])[:3]}"
                ),
                next_action="Bias decisions without overriding live geometry",
            ),
            ThinkingStep(
                stage="commit",
                question="What improving decisions raise project quality now?",
                finding=f"IROI={g.info_roi:.2f}, health={g.health:.2f}",
                next_action="Emit decision list + mode switch",
            ),
        ]
        return steps

    def _choose_mode(
        self,
        g: ProjectGeometry,
        influence: dict[str, Any],
        splits: list[dict[str, Any]],
        base_mode: str,
    ) -> ModeSwitch:
        triggers: list[str] = []
        # priority from pragma splits (highest severity generative/ricochet/refine)
        branch_votes = {"dual_ricochet": 3, "generative_development": 2, "recursive_refinement": 1, "scoring": 0}
        best_branch = "scoring"
        best_sev = -1.0
        for s in splits:
            bm = s.get("branch_mode") or "scoring"
            sev = float(s.get("severity") or 0)
            if branch_votes.get(bm, 0) > branch_votes.get(best_branch, 0) or (
                bm == best_branch and sev > best_sev
            ):
                if bm in branch_votes:
                    best_branch = bm
                    best_sev = sev
                    triggers.append(s.get("id") or s.get("phenomenon") or bm)

        # success influence overrides soft
        if influence.get("prefer_recursive_refine") and best_branch == "scoring":
            best_branch = "recursive_refinement"
            triggers.append("success_influence:prefer_recursive_refine")
        if influence.get("prefer_generative") and best_branch in (
            "scoring",
            "recursive_refinement",
        ):
            # generative only if scoring soft-failed
            if g.success_composite < g.success_target or g.scores["overall_orientation"] < 0.48:
                best_branch = "generative_development"
                triggers.append("success_influence:prefer_generative")
        if influence.get("prefer_scoring_only") and g.voids_pressure < 0.35:
            best_branch = "scoring"
            triggers.append("success_influence:prefer_scoring_only")

        # paid handoff flag (block 18 ready signal — not full paid core yet)
        if g.info_roi >= 3.0 and g.success_composite >= g.success_target and g.health >= 0.7:
            # stay on scoring/generative but flag; mode stays analytical
            triggers.append("signal:paid_block_18_candidate")

        conf = 0.55 + min(0.4, best_sev * 0.35) if best_sev >= 0 else 0.6
        if not triggers:
            triggers.append(f"default_from_orientation:{base_mode}")

        reason_map = {
            "scoring": "Metrics stable enough — match ready solutions by score",
            "generative_development": "Scoring shelf insufficient or double-bottom — open generative branch",
            "recursive_refinement": "Voids/productive errors demand recursive refine of specs & ideas",
            "dual_ricochet": "Brittle RRC — reverse void ricochet reassembly",
            "paid_handoff": "Reserved for block 18 paid product core",
        }
        return ModeSwitch(
            from_mode=base_mode,
            to_mode=best_branch,  # type: ignore[arg-type]
            reason=reason_map.get(best_branch, best_branch),
            confidence=round(min(0.98, conf), 4),
            triggers=triggers[:8],
        )

    def _improving_decisions(
        self,
        g: ProjectGeometry,
        switch: ModeSwitch,
        idea_title: str,
        sys_f: dict[str, Any],
    ) -> list[ImprovingDecision]:
        out: list[ImprovingDecision] = []
        p = 1
        if g.voids_pressure >= 0.35:
            out.append(
                ImprovingDecision(
                    id="dec_close_voids",
                    title="Close top specification voids",
                    rationale=f"voids_pressure={g.voids_pressure:.2f} (VVI={g.vvi:.2f})",
                    priority=p,
                    owner="SpecsForge",
                    expected_gain="↑ vvi_health, ↑ readiness",
                )
            )
            p += 1
        if g.tension >= 0.18:
            out.append(
                ImprovingDecision(
                    id="dec_balance_tracks",
                    title="Rebalance Product / Models / Promotion emphasis",
                    rationale=f"track tension={g.tension:.2f}",
                    priority=p,
                    owner=self.name,
                    expected_gain="↓ confusion in Full Package tour",
                )
            )
            p += 1
        if switch.to_mode == "generative_development":
            out.append(
                ImprovingDecision(
                    id="dec_open_generative",
                    title="Open generative development branch (demo-fast)",
                    rationale=switch.reason,
                    priority=p,
                    owner="OAE + generative(19)",
                    expected_gain="New idea variants from abstract coordinates",
                )
            )
            p += 1
        if switch.to_mode in ("recursive_refinement", "dual_ricochet"):
            out.append(
                ImprovingDecision(
                    id="dec_recursive_refrag",
                    title="Run reverse refragmentation / ricochet loop",
                    rationale=f"RRC={g.rrc:.2f}, mode={switch.to_mode}",
                    priority=p,
                    owner="Operational Analytics Engine",
                    expected_gain="↑ RRC, double-bottom solution list",
                )
            )
            p += 1
        if g.info_roi >= 1.8:
            out.append(
                ImprovingDecision(
                    id="dec_paid_path",
                    title="Prepare paid implement narrative (block 18 handoff)",
                    rationale=f"IROI={g.info_roi:.2f} attractive",
                    priority=p,
                    owner="human + paid core (18)",
                    expected_gain="Conversion to paid showcase / implement",
                )
            )
            p += 1
        if g.monetization_pull >= 0.55:
            out.append(
                ImprovingDecision(
                    id="dec_promo_mm",
                    title="Arm Promo + Market Making sequence",
                    rationale=f"monetization_pull={g.monetization_pull:.2f}",
                    priority=p,
                    owner="Monetization Layer",
                    expected_gain="Attention liquidity + reverse outreach",
                )
            )
            p += 1
        if not out:
            out.append(
                ImprovingDecision(
                    id="dec_hold_polish",
                    title="Hold geometry — polish demo wording",
                    rationale="No critical voids or tension",
                    priority=1,
                    owner="Product Sol",
                    expected_gain="Clearer client-facing idea text",
                )
            )
        # system log soft suggestion
        patterns = sys_f.get("recurring_patterns") or []
        if "high_iroi_cluster" in patterns and g.info_roi < 2.0:
            out.append(
                ImprovingDecision(
                    id="dec_log_iroi_lift",
                    title="Benchmark against high-IROI cluster in system log",
                    rationale="Log shows high_iroi_cluster pattern",
                    priority=p,
                    owner="System Log Analyst",
                    expected_gain="Lift positioning of success metrics",
                )
            )
        if idea_title:
            out[0].rationale += f" | focus idea: {idea_title[:60]}"
        return out

    def _awareness(
        self,
        g: ProjectGeometry,
        thinking: list[ThinkingStep],
        decisions: list[ImprovingDecision],
    ) -> float:
        # full project awareness score
        return max(
            0.0,
            min(
                1.0,
                0.25 * g.scores["readiness"]
                + 0.20 * g.health
                + 0.15 * min(1.0, g.info_roi / 4.0)
                + 0.15 * g.success_composite
                + 0.10 * (1.0 - g.voids_pressure)
                + 0.10 * min(1.0, len(thinking) / 6.0)
                + 0.05 * min(1.0, len(decisions) / 4.0),
            ),
        )
