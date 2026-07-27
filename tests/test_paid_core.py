"""Tests for Paid Product Core (block 18) — 16-step flow."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.request_pipeline import process_client_request
from backend.paid.energy_flow import EnergyFlowDisentangler
from backend.paid.function_engine import FunctionCalculationEngine
from backend.paid.interfaces import PAID_FLOW_STEPS, PAID_FLOW_STAGES
from backend.paid.orchestrator import PaidProductCore, flow_overview
from backend.paid.supporting.critical_thinking import CriticalThinkingLayer
from backend.paid.supporting.hypothesis_library import HypothesisLibrary
from backend.paid.system_design_library import get_system_design_library
from backend.paid.virtual_chips import get_virtual_chip_library


def test_flow_overview_has_16_steps():
    ov = flow_overview()
    assert len(ov["steps"]) == 16
    assert len(PAID_FLOW_STEPS) == 16
    assert "A_intake" in PAID_FLOW_STAGES
    assert "H_package" in PAID_FLOW_STAGES
    # Corrected order: calm (9) before mega map (10)
    assert "Calm" in PAID_FLOW_STEPS[9] or "calm" in PAID_FLOW_STEPS[9].lower()
    assert "Mega Map" in PAID_FLOW_STEPS[10]


def test_system_design_library_loads_by_industry():
    lib = get_system_design_library()
    loaded = lib.load_for_request("ai-agencies", track="product")
    assert loaded["industry_id"] == "ai-agencies"
    assert loaded["category"] == "product"
    assert loaded["chip_refs"]
    assert loaded["base_architecture"]


def test_virtual_chips_graph():
    chips = get_virtual_chip_library()
    graph = chips.build_graph(
        ["chip_orientation_core", "chip_product_spine", "chip_energy_flow"],
        context={
            "scores": {"product_fit": 0.7, "promo_fit": 0.5},
            "axes": {"risk": 0.3, "complexity": 0.5},
            "request_id": "t1",
        },
    )
    assert graph["chip_count"] == 3
    assert graph["terminal_agency_ready"] is True


def test_function_engine_sensitivity():
    eng = FunctionCalculationEngine(step=0.05)
    report = eng.sensitivity_report(
        {"clarity": 0.6, "impact": 0.55, "risk": 0.3, "model_fit": 0.5}
    )
    assert report["sensitivities"]
    assert report["top_lever"]


def test_energy_flow_disentangle():
    out = EnergyFlowDisentangler().analyze(
        chips=[
            {
                "id": "a",
                "zone": "product_sol",
                "amplitude": 0.8,
                "energy_direction": 0.6,
            },
            {
                "id": "b",
                "zone": "product_sol",
                "amplitude": 0.75,
                "energy_direction": -0.5,
            },
        ],
        zone_influence={"product_sol": 1.5, "cloud_sol": 0.8},
        scores={"promo_fit": 0.6},
        axes={"monetization_fit": 0.55, "risk": 0.3},
    )
    assert out["redistributed"] is True


def test_hypothesis_library_navigator():
    lib = HypothesisLibrary()
    hyps = [
        {
            "id": "h1",
            "claim": "Raise clarity lever for pilot",
            "source": "decision_core",
            "confidence": 0.7,
            "coords": {"x": 0.6, "y": 0.5, "z": 0.4},
            "supporting_indicators": ["clarity", "product"],
            "tension_with": [],
        },
        {
            "id": "h2",
            "claim": "Promo first",
            "source": "oae.demo_ideas",
            "confidence": 0.4,
            "coords": {"x": 0.2, "y": 0.2, "z": 0.8},
            "supporting_indicators": ["promo"],
            "tension_with": ["h1"],
        },
    ]
    nav = lib.navigate(
        hypotheses=hyps,
        step_trace=[
            {
                "step": 7,
                "name": "Function",
                "stage": "D_compute_energy",
                "status": "ok",
                "payload": {"top_lever": "clarity"},
            }
        ],
        sensitivities=[
            {"parameter": "clarity", "derivative": 0.8},
            {"parameter": "risk", "derivative": -0.3},
        ],
        mega_map={
            "points": [
                {"hypothesis_id": "h1", "distance_to_root": 0.2},
                {"hypothesis_id": "h2", "distance_to_root": 0.7},
            ],
            "comparison": {"root_alignment_score": 0.6},
        },
        outcome_score=0.7,
        iteration=1,
    )
    assert nav["scored_hypotheses"]
    assert nav["picked"]
    assert nav["learning_state"]["lever_ema"]
    assert nav["formulas"]["selection"]


def test_critical_thinking_founder_path():
    ct = CriticalThinkingLayer()
    out = ct.analyze(
        function_engine={
            "output_plane": {
                "product_axis": 0.9,
                "model_axis": 0.85,
                "paid_readiness": 0.85,
                "abstract_value": 2.0,
            },
            "sensitivities": [{"parameter": "impact", "derivative": 0.5}],
        },
        energy_flow={
            "nodes": [
                {
                    "id": "n1",
                    "amplitude": 0.8,
                    "direction": 0.5,
                    "corrected_direction": 0.5,
                }
            ],
            "total_entanglement": 0.7,
            "pair_count": 3,
            "zone_balance_after": {"product_sol": {"amplitude_mean": 0.7}},
        },
        virtual_chips={"zone_influence": {"product_sol": 2.0, "cloud_sol": 0.3}},
        mega_map={
            "comparison": {
                "competing_pairs": 2,
                "mean_uncertainty": 0.6,
                "root_alignment_score": 0.3,
                "best_hypothesis_id": "h1",
            }
        },
        hypotheses={"count": 1, "hypotheses": []},
        calm_point={"entropy": 0.15},
        metric_tests={
            "failed": [
                {
                    "id": "t_info_compatibility",
                    "score": 0.2,
                    "detail": "compat low",
                },
                {
                    "id": "t_calm_substance",
                    "score": 0.2,
                    "detail": "fake calm",
                },
                {
                    "id": "t_root_alignment",
                    "score": 0.2,
                    "detail": "align low",
                },
            ]
        },
        parallel={
            "scores": {
                "product_fit": 0.4,
                "model_fit": 0.4,
                "readiness": 0.7,
            },
            "abstract_coordinates": [{"a": 1}, {"b": 2}, {"c": 3}],
        },
        package_claim={"paid_score": 0.85},
    )
    assert out["discrepancy_count"] >= 1
    assert "founder_error" in out
    assert out["resolved_variant"]["trust"]


def test_paid_product_core_full_16_steps():
    core = PaidProductCore()
    result = core.run(
        industry_id="chipmaking",
        business="Fabless design house needing yield geometry and NRE stage gates for 5nm tapeout.",
        track="all",
        request_id="test-paid-1",
        idea_title="Yield twin pilot",
        axes={
            "value_density": 0.6,
            "complexity": 0.7,
            "risk": 0.4,
            "monetization_fit": 0.55,
            "time_pressure": 0.5,
        },
        scores={
            "product_fit": 0.65,
            "model_fit": 0.7,
            "promo_fit": 0.5,
            "readiness": 0.6,
        },
        info_roi=2.2,
        decision={
            "active_mode": "scoring",
            "awareness_score": 0.7,
            "handoff_flags": {"ready_for_paid_block_18": True},
            "improving_decisions": [
                {
                    "title": "Close specs voids before tapeout",
                    "priority": 1,
                    "rationale": "VVI high",
                }
            ],
        },
        oae={
            "embedding": {"values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.5, 0.4]},
            "abstract_coordinates": [
                {"label": "DFT gate pack", "energy": 0.7},
                {"label": "NRE navigator", "energy": 0.6},
            ],
            "demo_ideas": [{"title": "Yield twin pilot"}],
        },
        product={"demo_idea": {"title": "Yield twin pilot"}},
        fin_models=[
            {
                "model_id": "chipforge",
                "model_name": "ChipForge Metrics",
                "calculations": {
                    "impact": 0.7,
                    "insights": ["Estimated yield geometry improves with void close"],
                },
            }
        ],
        success={"weighted_composite": 0.62},
        force=True,
    )
    assert result["block"] == 18
    assert result["flow"]["step_count"] == 16
    assert result["components"]["hypothesis_library"] is True
    assert result["components"]["metric_tests"] is True
    assert result["metric_tests"]["tests"]
    assert result["critical_thinking"]["founder_error"]
    assert result["hypothesis_library"]["formulas"]
    assert result["package"]["custom_positioning"]
    assert result["open_points"]
    # stages A..H present in trace
    stages = {t["stage"] for t in result["flow"]["trace"]}
    assert "A_intake" in stages
    assert "H_package" in stages
    assert "E_form_map" in stages


def test_pipeline_includes_paid_core():
    out = process_client_request(
        {
            "industry": "ai-agencies",
            "business": (
                "We build AI agents that find growth points in client IT products "
                "and sell orientation-first delivery kits with clear pilots."
            ),
            "track": "all",
            "name": "PaidTest",
            "success_metrics": {
                "weights": {"iroi": 0.4, "impact": 0.3, "clarity": 0.2},
                "composite_target": 0.55,
            },
        }
    )
    assert out["ok"] is True
    paid = (out.get("meta") or {}).get("paid_product_core") or {}
    assert paid.get("block") == 18
    assert (paid.get("flow") or {}).get("step_count") == 16
    bd = (out.get("breakdown") or {}).get("paid_product_core") or {}
    assert bd.get("flow_step_count") == 16
    assert "paid_product_core" in (out.get("zones_touched") or [])
