"""
Paid Product Core Orchestrator (block 18) — 16-step staged flow.

Macro stages (deliberate, no overload of cycles):
  A Intake & Frame          steps 1–2
  B Design Hardware         steps 3–4   (Recursive Schemes + MTMF + Zone Clarity
                                         + Virtual Chips + Parameter Management)
  C Hypothesis & Probe      steps 5–6
  D Compute & Redistribute  steps 7–8
  E Form & Map              steps 9–10  (Calm Point seeds → Mega Map)  [corrected]
  F Verify & Explain        steps 11–13
  G Critique & Learn        steps 14–15
  H Package Showcase        step 16

OPEN spaces left for creative completion:
  · durable Hypothesis Library store
  · multi-iteration recursive schemes (default: single pass)
  · raster rendering of Calm Point (block 19)
  · founder human override UI
"""

from __future__ import annotations

from typing import Any

from backend.paid.blue_ocean.bridge import BlueOceanBridge
from backend.paid.calm_point import CalmPointImageGenerator
from backend.paid.conceptual_engine import ConceptualEngine
from backend.paid.energy_flow import EnergyFlowDisentangler
from backend.paid.function_engine import FunctionCalculationEngine, normalize_iroi
from backend.paid.interfaces import (
    BLUE_OCEAN_BLOCKS,
    CONCEPTUAL_TRAJECTORY_STAGES,
    PAID_FLOW_STAGES,
    PAID_FLOW_STEPS,
)
from backend.paid.mega_map import MegaMapBuilder
from backend.paid.meaning_vectors import get_standard_paid_vectors
from backend.paid.metric_tests import MetricTestBattery
from backend.paid.situation_metrics import SituationMetricsEngine
from backend.paid.supporting.critical_thinking import CriticalThinkingLayer
from backend.paid.supporting.hypothesis import HypothesisModuleSelector
from backend.paid.supporting.hypothesis_library import HypothesisLibrary
from backend.paid.supporting.reader import Reader
from backend.paid.system_design_library import get_system_design_library
from backend.paid.trajectory import TrajectoryBuilder
from backend.paid.types import ConceptualCoords, FlowStepResult, clamp01, safe_float
from backend.paid.virtual_chips import get_virtual_chip_library


def _stage_for_step(step: int) -> str:
    for key, meta in PAID_FLOW_STAGES.items():
        if step in meta["steps"]:
            return key
    return "unknown"


class PaidProductCore:
    """
    Production entrypoint for the paid product layer.

    One linear 16-step pass (plus optional prior_learning for navigator).
    Deterministic · JSON-serializable · showcase-ready.
    """

    name = "Paid Product Core"
    block = 18

    def __init__(self) -> None:
        self.design_library = get_system_design_library()
        self.chips = get_virtual_chip_library()
        self.functions = FunctionCalculationEngine()
        self.energy = EnergyFlowDisentangler()
        self.calm = CalmPointImageGenerator()
        self.mega_map = MegaMapBuilder()
        self.hyp_modules = HypothesisModuleSelector()
        self.hyp_library = HypothesisLibrary()
        self.metrics = MetricTestBattery()
        self.reader = Reader()
        self.critical = CriticalThinkingLayer()
        self.trajectory = TrajectoryBuilder()
        self.blue_ocean = BlueOceanBridge()
        self.conceptual = ConceptualEngine()
        self.situation = SituationMetricsEngine()

    def run(
        self,
        *,
        industry_id: str,
        business: str = "",
        track: str | None = None,
        request_kind: str | None = None,
        request_id: str = "",
        idea_title: str = "",
        axes: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
        info_roi: float = 0.0,
        decision: dict[str, Any] | None = None,
        oae: dict[str, Any] | None = None,
        product: dict[str, Any] | None = None,
        fin_models: list[dict[str, Any]] | None = None,
        success: dict[str, Any] | None = None,
        force: bool = False,
        prior_learning: dict[str, Any] | None = None,
        iteration: int = 1,
    ) -> dict[str, Any]:
        axes = {k: safe_float(v) for k, v in (axes or {}).items()}
        scores = {k: safe_float(v) for k, v in (scores or {}).items()}
        decision = decision or {}
        oae = oae or {}
        product = product or {}
        fin_models = fin_models or []
        success = success or {}

        handoff = decision.get("handoff_flags") or {}
        ready = bool(handoff.get("ready_for_paid_block_18")) or force
        trace: list[FlowStepResult] = []

        # ── A. Intake & Frame ────────────────────────────────────────────
        # Step 1 — root task
        root_task = idea_title or business[:120] or f"{industry_id} paid path"
        step1 = {
            "root_task": root_task,
            "industry_id": industry_id,
            "track": track,
            "request_id": request_id,
            "business_excerpt": (business or "")[:200],
            "client_request_received": True,
        }
        trace.append(
            FlowStepResult(
                1, PAID_FLOW_STEPS[1], _stage_for_step(1), "ok", step1
            )
        )

        # Step 2 — parameters + conceptual coordinates
        coords = ConceptualCoords(
            x_product=clamp01(
                0.5 * scores.get("product_fit", 0.5)
                + 0.5 * axes.get("value_density", 0.5)
            ),
            y_model=clamp01(
                0.5 * scores.get("model_fit", 0.5)
                + 0.5 * (1.0 - axes.get("complexity", 0.45) * 0.5)
            ),
            z_promo=clamp01(
                0.5 * scores.get("promo_fit", 0.5)
                + 0.5 * axes.get("monetization_fit", 0.5)
            ),
            clarity=clamp01(
                scores.get("readiness", 0.5) * 0.6
                + axes.get("value_density", 0.5) * 0.4
            ),
            risk=clamp01(axes.get("risk", 0.35)),
            notes="Initial conceptual coordinates from orientation axes/scores.",
        )
        params: dict[str, float] = {
            "clarity": coords.clarity,
            "impact": scores.get("product_fit", 0.5),
            "model_fit": scores.get("model_fit", 0.5),
            "promo_fit": scores.get("promo_fit", 0.5),
            "readiness": scores.get("readiness", 0.5),
            "risk": coords.risk,
            "complexity": axes.get("complexity", 0.45),
            "value_density": axes.get("value_density", 0.5),
            "monetization_fit": axes.get("monetization_fit", 0.5),
            "time_pressure": axes.get("time_pressure", 0.5),
            "iroi_norm": normalize_iroi(info_roi),
            "iroi_pull": normalize_iroi(info_roi),
            "x_product": coords.x_product,
            "y_model": coords.y_model,
            "z_promo": coords.z_promo,
        }
        sc_card = success if isinstance(success, dict) else {}
        if sc_card.get("weighted_composite") is not None:
            params["handoff_readiness"] = clamp01(
                0.5 * params.get("readiness", 0.5)
                + 0.5 * safe_float(sc_card.get("weighted_composite"))
            )
        else:
            params["handoff_readiness"] = params.get("readiness", 0.5)

        step2 = {
            "conceptual_coordinates": coords.to_dict(),
            "params": {k: round(v, 4) for k, v in params.items()},
            "mtmf": {
                "meaning": "root_task + orientation scores",
                "topology": "axes frame",
                "metrics": "iroi_norm + readiness",
                "form": "OPEN: filled by calm point later",
            },
        }
        trace.append(
            FlowStepResult(
                2, PAID_FLOW_STEPS[2], _stage_for_step(2), "ok", step2
            )
        )

        # ── B. Design Hardware ───────────────────────────────────────────
        # Step 3 — System Design Library
        loaded = self.design_library.load_for_request(
            industry_id,
            track=track,
            request_kind=request_kind,
            include_analysis=True,
        )
        loaded = self.design_library.blend_with_context(
            loaded, axes=axes, scores=scores
        )
        for k, v in (loaded.get("merged_params") or {}).items():
            params[k] = clamp01(
                0.55 * params.get(k, safe_float(v)) + 0.45 * safe_float(v)
            )
        step3 = {
            "category": loaded.get("category"),
            "pattern": loaded.get("pattern"),
            "base_architecture": loaded.get("base_architecture"),
            "chip_refs": loaded.get("chip_refs"),
            "zone_focus": loaded.get("zone_focus"),
            "summary": loaded.get("summary"),
            "principles": PAID_FLOW_STAGES["B_design_hardware"]["principles"],
        }
        trace.append(
            FlowStepResult(
                3, PAID_FLOW_STEPS[3], _stage_for_step(3), "ok", step3
            )
        )

        # Step 4 — Virtual Chips
        chip_ctx = {
            "scores": scores,
            "axes": axes,
            "request_id": request_id,
            "industry_id": industry_id,
        }
        chip_graph = self.chips.build_graph(
            list(loaded.get("chip_refs") or []),
            context=chip_ctx,
            library_params=params,
        )
        params = self.functions.apply_reverse_influence(
            params, chip_graph.get("reverse_influence") or {}
        )
        step4 = {
            "chip_count": chip_graph.get("chip_count"),
            "variant_count": chip_graph.get("variant_count"),
            "zone_influence": chip_graph.get("zone_influence"),
            "converter_load": chip_graph.get("converter_load"),
            "reverse_influence": chip_graph.get("reverse_influence"),
            "terminal_agency_ready": chip_graph.get("terminal_agency_ready"),
            "summary": chip_graph.get("summary"),
            # keep full graph available but step payload stays readable
            "chips": chip_graph.get("chips"),
            "variants": chip_graph.get("variants"),
        }
        trace.append(
            FlowStepResult(
                4,
                PAID_FLOW_STEPS[4],
                _stage_for_step(4),
                "ok",
                step4,
                notes="Virtual Chips = parametric hardware, not code packages.",
            )
        )

        # ── C. Hypothesis & Probe ────────────────────────────────────────
        # Step 5 — primary hypotheses (modules + sensitivity pre-pass for levers)
        pre_fn = self.functions.sensitivity_report(params, top_k=6)
        hyp_report = self.hyp_modules.select(
            root_task=root_task,
            decision=decision,
            oae=oae,
            product=product if product else {"demo_idea": {"title": idea_title}},
            fin_models=fin_models,
            success=success,
            energy={},
            function_plane=pre_fn.get("output_plane") or {},
        )
        # Early navigator scoring (learning from prior if any)
        early_scored = self.hyp_library.score_hypotheses(
            list(hyp_report.get("hypotheses") or []),
            sensitivities=list(pre_fn.get("sensitivities") or []),
            root_alignment=0.5,
            learning=None,
            mega_points=[],
        )
        hyp_report = {
            **hyp_report,
            "hypotheses": early_scored,
            "navigator_pre_scored": True,
        }
        step5 = {
            "count": hyp_report.get("count"),
            "sources_used": hyp_report.get("sources_used"),
            "hypotheses": early_scored,
            "top_levers_hint": pre_fn.get("top_lever"),
            "summary": hyp_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                5, PAID_FLOW_STEPS[5], _stage_for_step(5), "ok", step5
            )
        )

        # Step 6 — probe vs root (distance-like score without full map yet)
        probed = []
        for h in early_scored:
            c = h.get("coords") or {}
            # distance in conceptual space to root coords
            dx = safe_float(c.get("x"), 0.5) - coords.x_product
            dy = safe_float(c.get("y"), 0.5) - coords.y_model
            dz = safe_float(c.get("z"), 0.5) - coords.z_promo
            dist = (dx * dx + dy * dy + dz * dz) ** 0.5
            probed.append(
                {
                    "id": h.get("id"),
                    "claim": h.get("claim"),
                    "dist_to_root_coords": round(dist, 4),
                    "pass": dist < 0.75,
                    "navigator_score": h.get("navigator_score"),
                }
            )
        probe_pass = sum(1 for p in probed if p["pass"])
        step6 = {
            "probed": probed,
            "pass_count": probe_pass,
            "total": len(probed),
            "root_coords": coords.to_dict(),
            "summary": f"Probe: {probe_pass}/{len(probed)} hypotheses near root coords.",
        }
        trace.append(
            FlowStepResult(
                6, PAID_FLOW_STEPS[6], _stage_for_step(6), "ok", step6
            )
        )

        # ── D. Compute & Redistribute ────────────────────────────────────
        # Step 7 — Function Calculation Engine (full)
        fn_report = self.functions.sensitivity_report(params)
        step7 = {
            "output_plane": fn_report.get("output_plane"),
            "top_lever": fn_report.get("top_lever"),
            "top_derivative": fn_report.get("top_derivative"),
            "sensitivities": fn_report.get("sensitivities"),
            "relationships": fn_report.get("relationships"),
            "abstractions": fn_report.get("abstractions"),
            "summary": fn_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                7, PAID_FLOW_STEPS[7], _stage_for_step(7), "ok", step7
            )
        )

        # Step 8 — Energy Flow Disentangler
        energy_chip_params: dict[str, float] = {}
        for c in chip_graph.get("chips") or []:
            if c.get("template_id") == "chip_energy_flow" or "energy" in (
                c.get("tags") or []
            ):
                energy_chip_params = {
                    k: safe_float(v) for k, v in (c.get("params") or {}).items()
                }
                break
        energy_report = self.energy.analyze(
            chips=list(chip_graph.get("chips") or []),
            zone_influence=chip_graph.get("zone_influence") or {},
            scores=scores,
            axes=axes,
            chip_params=energy_chip_params,
        )
        params["entanglement"] = safe_float(
            energy_report.get("total_entanglement"), 0.4
        )
        step8 = {
            "total_entanglement": energy_report.get("total_entanglement"),
            "pair_count": energy_report.get("pair_count"),
            "zone_balance_after": energy_report.get("zone_balance_after"),
            "resolution_steps": energy_report.get("resolution_steps"),
            "nodes": energy_report.get("nodes"),
            "summary": energy_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                8,
                PAID_FLOW_STEPS[8],
                _stage_for_step(8),
                "ok",
                step8,
                notes="Market Units: entanglement as wrong interconnection.",
            )
        )

        # ── E. Form & Map (corrected: Calm → Mega Map) ───────────────────
        # Step 9 — Calm-Point
        calm_report = self.calm.generate(
            industry_id=industry_id,
            request_id=request_id,
            idea_title=root_task,
            params=params,
            energy=energy_report,
            embedding=oae.get("embedding") or {},
            reverse_influence=chip_graph.get("reverse_influence") or {},
        )
        step9 = {
            "entropy": calm_report.get("entropy"),
            "noise": calm_report.get("noise"),
            "physics_method": calm_report.get("physics_method"),
            "assembly_points": calm_report.get("assembly_points"),
            "primary": calm_report.get("primary"),
            "summary": calm_report.get("summary"),
            "open_point": "OPEN: external raster render deferred (block 19 / design tools).",
        }
        trace.append(
            FlowStepResult(
                9, PAID_FLOW_STEPS[9], _stage_for_step(9), "ok", step9
            )
        )

        # Step 10 — Mega Map
        mega_report = self.mega_map.build(
            root_task=root_task,
            hypotheses=list(hyp_report.get("hypotheses") or []),
            params=params,
            output_plane=fn_report.get("output_plane") or {},
            calm_point=calm_report,
            energy=energy_report,
            root_coords={
                "x": coords.x_product,
                "y": coords.y_model,
            },
        )
        step10 = {
            "hypothesis_count": mega_report.get("hypothesis_count"),
            "comparison": mega_report.get("comparison"),
            "points": mega_report.get("points"),
            "pairwise_deltas": mega_report.get("pairwise_deltas"),
            "summary": mega_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                10, PAID_FLOW_STEPS[10], _stage_for_step(10), "ok", step10
            )
        )

        # ── F. Verify & Explain ──────────────────────────────────────────
        # Step 11 — metric tests
        parallel_ctx = {
            "scores": scores,
            "zone_influence": chip_graph.get("zone_influence"),
            "abstract_coordinates": oae.get("abstract_coordinates") or [],
        }
        sc_comp = None
        if sc_card.get("weighted_composite") is not None:
            sc_comp = safe_float(sc_card.get("weighted_composite"))
        metric_report = self.metrics.run(
            params=params,
            output_plane=fn_report.get("output_plane") or {},
            energy=energy_report,
            mega_map=mega_report,
            hypotheses=hyp_report,
            calm_point=calm_report,
            info_roi=info_roi,
            success_composite=sc_comp,
            parallel=parallel_ctx,
        )
        step11 = {
            "overall_score": metric_report.get("overall_score"),
            "passed_count": metric_report.get("passed_count"),
            "total": metric_report.get("total"),
            "failed": metric_report.get("failed"),
            "informational_compatibility": metric_report.get(
                "informational_compatibility"
            ),
            "tests": metric_report.get("tests"),
            "summary": metric_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                11, PAID_FLOW_STEPS[11], _stage_for_step(11), "ok", step11
            )
        )

        # Pre-package claim for critical layer
        plane = fn_report.get("output_plane") or {}
        comparison = mega_report.get("comparison") or {}
        paid_score_pre = clamp01(
            0.35 * safe_float(plane.get("paid_readiness"))
            + 0.25 * safe_float(comparison.get("root_alignment_score"))
            + 0.2 * (1.0 - safe_float(energy_report.get("total_entanglement")))
            + 0.2 * safe_float(metric_report.get("overall_score"))
        )

        # Step 12 — grouping (via critical, groups only first — full at 14)
        # We run full critical at 14; step 12 exposes groups early for Reader.
        critical_partial = self.critical.analyze(
            function_engine=fn_report,
            energy_flow=energy_report,
            virtual_chips=chip_graph,
            mega_map=mega_report,
            hypotheses=hyp_report,
            calm_point=calm_report,
            metric_tests=metric_report,
            parallel={
                **parallel_ctx,
                "abstract_coordinates": oae.get("abstract_coordinates") or [],
            },
            package_claim={"paid_score": paid_score_pre},
        )
        step12 = {
            "groups": critical_partial.get("groups"),
            "group_count": critical_partial.get("group_count"),
            "descriptions": critical_partial.get("descriptions"),
            "summary": f"Grouped {critical_partial.get('group_count')} indicator sets.",
        }
        trace.append(
            FlowStepResult(
                12, PAID_FLOW_STEPS[12], _stage_for_step(12), "ok", step12
            )
        )

        # Step 13 — Reader (uses partial bundle; final narrative refreshed after G)
        reader_bundle = {
            "system_design_library": loaded,
            "virtual_chips": chip_graph,
            "function_engine": fn_report,
            "energy_flow": energy_report,
            "calm_point": calm_report,
            "mega_map": mega_report,
            "hypotheses": hyp_report,
            "critical_thinking": critical_partial,
            "metric_tests": metric_report,
        }
        reader_report = self.reader.explain(reader_bundle)
        step13 = {
            "sections": reader_report.get("sections"),
            "plain_summary": reader_report.get("plain_summary"),
            "action_bullets": reader_report.get("action_bullets"),
            "summary": reader_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                13, PAID_FLOW_STEPS[13], _stage_for_step(13), "ok", step13
            )
        )

        # ── G. Critique & Learn ──────────────────────────────────────────
        # Step 14 — full discrepancy + founder error (critical already ran;
        # re-expose with emphasis)
        step14 = {
            "discrepancies": critical_partial.get("discrepancies"),
            "discrepancy_count": critical_partial.get("discrepancy_count"),
            "resolved_variant": critical_partial.get("resolved_variant"),
            "founder_error": critical_partial.get("founder_error"),
            "field_severity": critical_partial.get("field_severity"),
            "summary": critical_partial.get("summary"),
        }
        trace.append(
            FlowStepResult(
                14, PAID_FLOW_STEPS[14], _stage_for_step(14), "ok", step14
            )
        )

        # Step 15 — Hypothesis Library navigator (deep step + group + learn)
        trace_dicts = [t.to_dict() for t in trace]
        outcome = paid_score_pre * safe_float(metric_report.get("overall_score"), 0.5)
        lib_report = self.hyp_library.navigate(
            hypotheses=list(hyp_report.get("hypotheses") or []),
            step_trace=trace_dicts,
            sensitivities=list(fn_report.get("sensitivities") or []),
            mega_map=mega_report,
            prior_learning=prior_learning,
            outcome_score=outcome,
            iteration=iteration,
        )
        # Refresh hyp list with navigator picks
        hyp_report = {
            **hyp_report,
            "navigator": {
                "picked": lib_report.get("picked"),
                "variants": lib_report.get("variants_from_previous_stage"),
                "learning_state": lib_report.get("learning_state"),
            },
            "scored_hypotheses": lib_report.get("scored_hypotheses"),
        }
        step15 = {
            "iteration": lib_report.get("iteration"),
            "deep_previous_step": lib_report.get("deep_previous_step"),
            "group_patterns": lib_report.get("group_patterns"),
            "picked": lib_report.get("picked"),
            "variants_from_previous_stage": lib_report.get(
                "variants_from_previous_stage"
            ),
            "learning_state": lib_report.get("learning_state"),
            "formulas": lib_report.get("formulas"),
            "open_points": lib_report.get("open_points"),
            "summary": lib_report.get("summary"),
        }
        trace.append(
            FlowStepResult(
                15, PAID_FLOW_STEPS[15], _stage_for_step(15), "ok", step15
            )
        )

        # ── H. Package Showcase ──────────────────────────────────────────
        # Step 16 — final plane + paid showcase
        founder = critical_partial.get("founder_error") or {}
        trust = (critical_partial.get("resolved_variant") or {}).get("trust", "paid")

        # Adjust score if founder error or parallel trust
        paid_score = paid_score_pre
        if founder.get("suspected"):
            paid_score = clamp01(paid_score * (1.0 - 0.25 * safe_float(founder.get("confidence"))))
        if trust == "parallel":
            paid_score = clamp01(paid_score * 0.9)
        elif trust == "hold":
            paid_score = clamp01(paid_score * 0.85)

        status = "ready" if ready else "preview"
        if founder.get("suspected") and safe_float(founder.get("confidence")) >= 0.55:
            status = "preview_founder_review"
        elif paid_score >= 0.65 and ready and metric_report.get("overall_score", 0) >= 0.5:
            status = "packageable"
        elif not ready and paid_score >= 0.55:
            status = "candidate_preview"

        # Custom positioning from success TZ + best hypothesis
        custom_positioning = {
            "success_composite": sc_comp,
            "best_hypothesis": comparison.get("best_label")
            or comparison.get("best_hypothesis_id"),
            "top_lever": fn_report.get("top_lever"),
            "trust_variant": trust,
            "meaning_vectors": get_standard_paid_vectors(),
            "industry_id": industry_id,
            "category": loaded.get("category"),
            "open_point": "OPEN: client white-label positioning copy per showcase.",
        }

        package = {
            "title": f"Paid package · {root_task[:60]}",
            "status": status,
            "paid_score": round(paid_score, 4),
            "best_hypothesis": custom_positioning["best_hypothesis"],
            "navigator_pick": (lib_report.get("picked") or [{}])[0].get("claim")
            if lib_report.get("picked")
            else None,
            "top_lever": fn_report.get("top_lever"),
            "paid_readiness": plane.get("paid_readiness"),
            "root_alignment": comparison.get("root_alignment_score"),
            "informational_compatibility": metric_report.get(
                "informational_compatibility"
            ),
            "founder_error_suspected": bool(founder.get("suspected")),
            "recommended_actions": list(reader_report.get("action_bullets") or []),
            "architecture": list(loaded.get("base_architecture") or [])[:8],
            "chip_ids": [c.get("id") for c in (chip_graph.get("chips") or [])],
            "calm_point_id": (calm_report.get("primary") or {}).get("id"),
            "mega_map_best_id": comparison.get("best_hypothesis_id"),
            "custom_positioning": custom_positioning,
            "result_plane": {
                **plane,
                "paid_score": round(paid_score, 4),
                "metric_overall": metric_report.get("overall_score"),
                "entanglement": energy_report.get("total_entanglement"),
                "field_severity": critical_partial.get("field_severity"),
            },
        }

        step16 = {
            "status": status,
            "paid_score": round(paid_score, 4),
            "package": package,
            "custom_positioning": custom_positioning,
            "result_plane": package["result_plane"],
            "showcase_ready": status in ("packageable", "ready"),
            "summary": (
                f"Showcase status={status}, score={paid_score:.2f}, "
                f"trust={trust}, founder={founder.get('suspected')}."
            ),
        }
        trace.append(
            FlowStepResult(
                16, PAID_FLOW_STEPS[16], _stage_for_step(16), "ok", step16
            )
        )

        # Situation Metrics (early commercial coupling for Reader / Blue Ocean)
        situation_report = self.situation.analyze(
            business=business,
            industry_id=industry_id,
            scores=scores,
            axes=axes,
            idea_title=root_task,
            paid={
                "function_engine": fn_report,
                "energy_flow": energy_report,
                "package": package,
            },
            success=success,
            energy=energy_report,
            function_engine=fn_report,
        )

        # Conceptual trajectory (visible path; residual uncertainty explicit)
        trace_for_traj = [t.to_dict() for t in trace]
        trajectory_report = self.trajectory.build(
            root_task=root_task,
            flow_trace=trace_for_traj,
            package=package,
            mega_map=mega_report,
            hyp_lib=lib_report,
            founder_error=founder,
        )

        # Final reader refresh — 5-stage with full context
        reader_final = self.reader.explain(
            {
                **reader_bundle,
                "root_task": root_task,
                "critical_thinking": critical_partial,
                "hypothesis_library": lib_report,
                "package": package,
                "business_metrics": situation_report,
                "situation_metrics": situation_report,
                "conceptual_trajectory": trajectory_report,
            }
        )

        # Apply Reader learning feedback into hyp library learning state (soft)
        learn_fb = reader_final.get("learning_feedback") or {}
        if learn_fb and isinstance(lib_report.get("learning_state"), dict):
            ls = dict(lib_report["learning_state"])
            lever = str(learn_fb.get("lever_hint") or "")
            if lever:
                ema = dict(ls.get("lever_ema") or {})
                prev = safe_float(ema.get(lever), 0.3)
                ema[lever] = round(
                    clamp01(0.65 * prev + 0.35 * safe_float(learn_fb.get("outcome_score"))),
                    4,
                )
                ls["lever_ema"] = ema
                ls["reader_feedback_applied"] = True
            lib_report = {**lib_report, "learning_state": ls}

        virtual_assets = list(reader_final.get("virtual_assets") or [])
        if not virtual_assets:
            virtual_assets = list(chip_graph.get("virtual_assets") or [])

        # Blue Ocean Identifier bridge
        blue_ocean_report = self.blue_ocean.synthesize(
            paid={
                "root_task": root_task,
                "system_design_library": loaded,
                "virtual_chips": chip_graph,
                "function_engine": fn_report,
                "energy_flow": energy_report,
                "mega_map": mega_report,
                "hypotheses": hyp_report,
                "hypothesis_library": lib_report,
                "package": package,
                "critical_thinking": critical_partial,
                "reader": reader_final,
                "situation_metrics": situation_report,
                "business_metrics": situation_report,
                "conceptual_trajectory": trajectory_report,
            },
            industry_id=industry_id,
            business=business,
            oae=oae,
            decision=decision,
            scores=scores,
            axes=axes,
            virtual_assets=virtual_assets,
        )

        # Conceptual Engine — OPEN final step (preview only; plan stays open)
        conceptual_preview = self.conceptual.preview(
            paid={
                "function_engine": fn_report,
                "package": package,
                "situation_metrics": situation_report,
                "blue_ocean": blue_ocean_report,
                "conceptual_trajectory": trajectory_report,
            },
            situation_metrics=situation_report,
            blue_ocean=blue_ocean_report,
            trajectory=trajectory_report,
        )

        return {
            "module": self.name,
            "block": self.block,
            "status": status,
            "ready_for_paid": ready,
            "paid_score": round(paid_score, 4),
            "industry_id": industry_id,
            "track": track,
            "category": loaded.get("category"),
            "root_task": root_task,
            "request_id": request_id,
            "iteration": iteration,
            # Flow documentation
            "flow": {
                "stages": PAID_FLOW_STAGES,
                "steps": PAID_FLOW_STEPS,
                "trace": [t.to_dict() for t in trace],
                "step_count": len(trace),
            },
            # Conceptual trajectory (raw → … → deliverable → OPEN engine)
            "conceptual_trajectory": trajectory_report,
            "conceptual_trajectory_stages": list(CONCEPTUAL_TRAJECTORY_STAGES),
            # Core 6 surfaces
            "system_design_library": {
                "industry_id": industry_id,
                "category": loaded.get("category"),
                "pattern": loaded.get("pattern"),
                "base_architecture": loaded.get("base_architecture"),
                "merged_params": {k: round(float(v), 4) for k, v in params.items()},
                "chip_refs": loaded.get("chip_refs"),
                "zone_focus": loaded.get("zone_focus"),
                "primary": loaded.get("primary"),
                "summary": loaded.get("summary"),
            },
            "virtual_chips": chip_graph,
            "function_engine": fn_report,
            "energy_flow": energy_report,
            "calm_point": calm_report,
            "mega_map": mega_report,
            # Supporting
            "hypotheses": hyp_report,
            "hypothesis_library": lib_report,
            "metric_tests": metric_report,
            "critical_thinking": critical_partial,
            "reader": reader_final,
            "situation_metrics": situation_report,
            "business_metrics": situation_report,
            "virtual_assets": virtual_assets,
            "phenomenon_chain": reader_final.get("phenomenon_chain"),
            "blue_ocean": blue_ocean_report,
            "blue_ocean_blocks": list(BLUE_OCEAN_BLOCKS),
            "conceptual_engine": conceptual_preview,
            "meaning_vectors": get_standard_paid_vectors(),
            "package": package,
            "conceptual_coordinates": coords.to_dict(),
            "components": {
                "1_system_design_library": True,
                "2_virtual_chips": True,
                "3_function_calculation_engine": True,
                "4_energy_flow_disentangler": True,
                "5_calm_point_image_generator": True,
                "6_mega_map_builder": True,
                "hypothesis_modules": True,
                "hypothesis_library": True,
                "reader_5_stage": True,
                "critical_thinking_layer": True,
                "metric_tests": True,
                "situation_metrics_engine": True,
                "conceptual_trajectory": True,
                "blue_ocean_bridge": True,
                "conceptual_engine_open": True,
            },
            "open_points": [
                "OPEN: Conceptual Engine full plan() — outgoing supply-chain vision "
                "(statistics + narrowing models) — intentional last step",
                "OPEN: durable Hypothesis Library across requests",
                "OPEN: multi-iteration recursive scheme (single pass default)",
                "OPEN: Calm Point raster rendering",
                "OPEN: founder human override UI",
                "OPEN: client white-label positioning copy",
                "OPEN: live Reality Layer streamers / smart-contract rail",
            ],
            "summary": (
                f"{self.name}: status={status}, score={paid_score:.2f}, "
                f"steps={len(trace)}, chips={chip_graph.get('chip_count', 0)}, "
                f"hypotheses={hyp_report.get('count', 0)}, "
                f"assets={len(virtual_assets)}, "
                f"metrics={metric_report.get('passed_count')}/{metric_report.get('total')}, "
                f"discrepancies={critical_partial.get('discrepancy_count')}, "
                f"founder={founder.get('suspected')}, "
                f"best={comparison.get('best_hypothesis_id')}, "
                f"traj_u={trajectory_report.get('residual_uncertainty')}, "
                f"bo={blue_ocean_report.get('aggregate_readiness')}."
            ),
        }


def paid_ready_payload(
    *,
    industry_id: str,
    business: str,
    track: str | None,
    request_id: str,
    idea_title: str,
    axes: dict[str, Any],
    scores: dict[str, Any],
    info_roi: float,
    decision: dict[str, Any],
    oae: dict[str, Any],
    product: dict[str, Any],
    fin_models: list[dict[str, Any]],
    success: dict[str, Any],
) -> dict[str, Any]:
    return {
        "industry_id": industry_id,
        "business": business,
        "track": track,
        "request_id": request_id,
        "idea_title": idea_title,
        "axes": axes,
        "scores": scores,
        "info_roi": info_roi,
        "decision": decision,
        "oae": oae,
        "product": product,
        "fin_models": fin_models,
        "success": success,
    }


def flow_overview() -> dict[str, Any]:
    """Public architecture overview for docs / API."""
    return {
        "block": 18,
        "name": "Paid Product Core — 16-step flow + Blue Ocean bridge",
        "stages": PAID_FLOW_STAGES,
        "steps": PAID_FLOW_STEPS,
        "conceptual_trajectory_stages": list(CONCEPTUAL_TRAJECTORY_STAGES),
        "blue_ocean_blocks": list(BLUE_OCEAN_BLOCKS),
        "reader": "5-Stage Learning Interpreter (no static DB)",
        "correction_note": (
            "Steps 9–10 ordered Calm Point → Mega Map so assembly forms "
            "seed the map (original draft had map before calm form)."
        ),
        "principles": [
            "Recursive Schemes (single refine pass)",
            "MTMF Specifications (Meaning / Topology / Metrics / Form)",
            "Zone Clarity",
            "Virtual Chips",
            "Parameter Management",
            "Phenomenon → Notation → Object → Virtual Asset",
            "Honest overclaim protection (Critical Thinking + founder-frame)",
        ],
        "open_final_step": (
            "ConceptualEngine.supply_chain_vision — statistics + narrowing models"
        ),
    }
