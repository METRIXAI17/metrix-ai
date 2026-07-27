"""Tests for Paid Product Layer v2 — Reader 5-stage, Virtual Assets, Blue Ocean, Conceptual Engine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.paid.blue_ocean.bridge import BlueOceanBridge
from backend.paid.conceptual_engine import ConceptualEngine
from backend.paid.interfaces import BLUE_OCEAN_BLOCKS, CONCEPTUAL_TRAJECTORY_STAGES
from backend.paid.must_ask import MustAskLoop
from backend.paid.orchestrator import PaidProductCore, flow_overview
from backend.paid.situation_metrics import SituationMetricsEngine
from backend.paid.supporting.reader import Reader
from backend.paid.trajectory import TrajectoryBuilder
from backend.paid.virtual_chips import get_virtual_chip_library


def test_flow_overview_blue_ocean_and_trajectory():
    ov = flow_overview()
    assert len(ov["steps"]) == 16
    assert "Reader" in ov["reader"] or "5" in ov["reader"]
    assert len(ov["blue_ocean_blocks"]) == 6
    assert ov["open_final_step"]
    assert "conceptual_engine" in ov["open_final_step"].lower() or "Conceptual" in ov[
        "open_final_step"
    ]


def test_reader_five_stages():
    reader = Reader()
    bundle = {
        "root_task": "AI agency pilot with unit economics",
        "system_design_library": {
            "industry_id": "ai-agencies",
            "category": "product",
            "pattern": "seed-spine",
            "base_architecture": ["a", "b"],
            "chip_refs": ["chip_product_spine"],
            "merged_params": {"clarity": 0.6, "readiness": 0.55},
        },
        "virtual_chips": {
            "chip_count": 2,
            "variant_count": 1,
            "chips": [
                {
                    "id": "chip_product_spine",
                    "purpose": "Hold product spine",
                    "zone": "product_sol",
                    "amplitude": 0.7,
                    "tags": ["product"],
                }
            ],
            "terminal_agency_ready": True,
            "multi_agent_scalable": False,
        },
        "function_engine": {
            "output_plane": {
                "paid_readiness": 0.62,
                "abstract_value": 1.4,
                "product_axis": 0.6,
            },
            "top_lever": "clarity",
        },
        "energy_flow": {"total_entanglement": 0.35, "pair_count": 2},
        "calm_point": {"entropy": 0.2, "primary": {"form_archetype": "lens"}},
        "mega_map": {
            "comparison": {
                "best_hypothesis_id": "h1",
                "root_alignment_score": 0.7,
                "mean_uncertainty": 0.3,
            }
        },
        "hypotheses": {"count": 2},
        "package": {
            "status": "preview",
            "paid_score": 0.58,
            "title": "Paid package · pilot",
            "recommended_actions": ["Raise clarity"],
        },
    }
    out = reader.explain(bundle)
    assert "stages" in out
    assert "1_perception" in out["stages"]
    assert "5_application_learning" in out["stages"]
    assert out["stages"]["1_perception"]["count"] >= 2
    assert out["virtual_assets"]
    assert out["learning_feedback"].get("feeds_hypothesis_library") is True
    assert out["phenomenon_chain"]["phenomena"]


def test_virtual_chips_assets_and_new_templates():
    lib = get_virtual_chip_library()
    graph = lib.build_graph(
        [
            "chip_orientation_core",
            "chip_phenomenon_bridge",
            "chip_virtual_asset",
            "chip_supply_contour",
        ],
        context={
            "scores": {"product_fit": 0.7},
            "axes": {"risk": 0.3},
            "request_id": "v2",
        },
    )
    assert graph["chip_count"] == 4
    assert graph["virtual_assets"]
    assert graph["causal_mesh"]["edge_count"] >= 0
    assert "chip_phenomenon_bridge" in [c["template_id"] for c in graph["chips"]]


def test_situation_metrics_engine():
    eng = SituationMetricsEngine()
    out = eng.analyze(
        business="AI agency with low utilization and margin pressure on GPU hours",
        industry_id="ai-agencies",
        scores={"product_fit": 0.6, "promo_fit": 0.5},
        axes={"risk": 0.4, "monetization_fit": 0.55},
        energy={"total_entanglement": 0.5},
        function_engine={"top_lever": "clarity", "output_plane": {"paid_readiness": 0.5}},
    )
    assert out["module"] == "Situation Metrics Engine"
    assert "revenue_levers" in out
    assert "leak_map" in out


def test_must_ask_loop_language():
    loop = MustAskLoop()
    out = loop.run(
        business="We build agents for clients",
        industry_id="ai-agencies",
        idea_title="Agent pilot",
        paid={"function_engine": {"output_plane": {"paid_readiness": 0.3}}},
        metrics={},
        modeling_answers={},
    )
    assert out["must_count"] >= 1
    assert out["language"].startswith("entities")
    assert out["block_rerun"] is True


def test_trajectory_and_conceptual_engine_open():
    traj = TrajectoryBuilder().build(
        root_task="Pilot path",
        flow_trace=[
            {"step": 1, "name": "Intake", "payload": {"summary": "ok"}},
            {"step": 16, "name": "Package", "payload": {"summary": "packaged"}},
        ],
        package={"status": "preview", "paid_score": 0.5, "paid_readiness": 0.5},
        mega_map={"comparison": {"mean_uncertainty": 0.4}},
    )
    assert traj["step_count"] >= 1
    assert "ConceptualEngine" in traj["next_open_engine"]

    ce = ConceptualEngine()
    prev = ce.preview(
        paid={"function_engine": {"output_plane": {"paid_readiness": 0.55}, "sensitivities": []}},
        situation_metrics={
            "delivery_friction": 0.4,
            "margin_pressure": 0.35,
            "situation_score": 0.5,
        },
        blue_ocean={
            "architecture": {
                "synthesis_core": {
                    "potential_phenomenon_space": {"open_volume": 0.5}
                }
            },
            "aggregate_readiness": 0.55,
        },
        trajectory=traj,
    )
    assert prev["mode"] == "preview"
    assert prev["outgoing_chain"]
    plan = ce.plan(paid={}, situation_metrics={}, blue_ocean={}, trajectory=traj)
    assert plan["vision"]["state"] == "OPEN"
    assert plan["status"] == "awaiting_final_creative_pass"


def test_blue_ocean_bridge_six_blocks():
    bridge = BlueOceanBridge()
    out = bridge.synthesize(
        paid={
            "root_task": "Blue ocean pilot",
            "package": {"paid_score": 0.6, "status": "preview"},
            "function_engine": {
                "output_plane": {"paid_readiness": 0.6, "product_axis": 0.6},
                "top_lever": "clarity",
            },
            "energy_flow": {"total_entanglement": 0.3},
            "mega_map": {
                "comparison": {
                    "root_alignment_score": 0.65,
                    "best_hypothesis_id": "h1",
                },
                "points": [],
            },
            "hypotheses": {
                "hypotheses": [
                    {
                        "id": "h1",
                        "claim": "Raise clarity",
                        "confidence": 0.7,
                        "navigator_score": 0.7,
                    }
                ]
            },
            "virtual_chips": {"chips": []},
            "reader": {},
        },
        industry_id="ai-agencies",
        business="Agency with delivery friction",
        scores={"product_fit": 0.6},
        axes={"risk": 0.3},
    )
    arch = out["architecture"]
    assert len(arch) == 6
    assert set(BLUE_OCEAN_BLOCKS) == {
        arch["synthesis_core"]["block"],
        arch["reality_layer_interface"]["block"],
        arch["symmetry_bridge"]["block"],
        arch["value_proposition_engine"]["block"],
        arch["engagement_transaction_protocol"]["block"],
        arch["metrix_ledger_operational_core"]["block"],
    }


def test_paid_core_end_to_end_v2_fields():
    core = PaidProductCore()
    out = core.run(
        industry_id="ai-agencies",
        business=(
            "We run an AI agency with custom cloud for developers. "
            "Need control of revenue levers and less delivery rework."
        ),
        track="product",
        request_id="test-v2",
        idea_title="Lever-control pilot for AI agency",
        axes={
            "value_density": 0.6,
            "complexity": 0.45,
            "risk": 0.35,
            "monetization_fit": 0.55,
            "time_pressure": 0.5,
        },
        scores={
            "product_fit": 0.65,
            "model_fit": 0.55,
            "promo_fit": 0.5,
            "readiness": 0.58,
        },
        info_roi=1.8,
        decision={
            "handoff_flags": {"ready_for_paid_block_18": True},
            "active_mode": "scoring",
        },
        oae={"embedding": {"dimensions": [0.1] * 12}, "abstract_coordinates": []},
        product={"demo_idea": {"title": "Lever-control pilot"}},
        fin_models=[],
        success={"weighted_composite": 0.6},
        force=True,
    )
    assert out["flow"]["step_count"] == 16
    assert out["reader"]["stages"]["1_perception"]["count"] >= 1
    assert out["virtual_assets"]
    assert out["conceptual_trajectory"]["path_summary"]
    assert out["blue_ocean"]["aggregate_readiness"] is not None
    assert out["conceptual_engine"]["status"] == "open_scaffold"
    assert out["situation_metrics"]["module"] == "Situation Metrics Engine"
    assert out["components"]["reader_5_stage"] is True
    assert out["components"]["conceptual_engine_open"] is True
    assert any(
        "Conceptual Engine" in p or "supply-chain" in p for p in out["open_points"]
    )
    assert CONCEPTUAL_TRAJECTORY_STAGES[-1].startswith("conceptual_engine")
