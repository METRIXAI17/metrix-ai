"""Final layer: 21 principles, assembler, anti-down, capital, NFT, harness."""

from __future__ import annotations

from backend.paid.anti_down_sorter import AntiDownSorter
from backend.paid.capital_efficiency import CapitalEfficiencyEngine, MONTHLY_SCENARIOS
from backend.paid.final_layer import FinalProductLayer
from backend.paid.nft_create_building import NFTCreateBuilding
from backend.paid.principles_engine import get_principles_engine
from backend.paid.sequence_assembler import SequenceAssembler


def test_principles_meanings_over_400():
    eng = get_principles_engine()
    n = eng.meaning_count()
    assert n >= 400, f"expected >=400 meanings, got {n}"
    g = eng.graph()
    assert g["node_count"] == 21
    assert g["edge_count"] == 210  # C(21,2)
    assert g["complete_graph"] is True


def test_principles_run_and_reader():
    eng = get_principles_engine()
    r = eng.run(industry_id="ai-agencies", top_lever="margin", residual_uncertainty=0.3)
    assert r["meanings_count"] >= 400
    assert len(r["active_principle_ids"]) >= 5
    reader = eng.read_groups("cloud-economy")
    assert reader["total_meanings"] >= 400
    assert "pair" in reader["group_counts"]


def test_sequence_assembler():
    seq = SequenceAssembler().assemble(
        industry_id="chipmaking",
        paid_score=0.6,
        residual_uncertainty=0.4,
    )
    assert seq["sequence_length"] >= 4
    assert seq["plan_code"]
    assert seq["steps"][0]["principle_id"] >= 1


def test_anti_down_rejects_empty_charts():
    out = AntiDownSorter().sort(
        paid={"status": "candidate_preview", "paid_score": 0.7},
        sequence={"quality": 0.6, "sequence_length": 7},
        principles={"coherence": 0.6},
        situation_metrics={"situation_score": 0.5, "delivery_friction": 0.3},
    )
    assert out["gate"] in ("pass", "strong_pass", "pass_with_warnings", "block_down")
    downs = [x for x in out["ranked"] if x["id"] == "empty_showcase"]
    assert downs and downs[0]["is_down"] is True


def test_anti_down_honesty_on_oversell_package():
    out = AntiDownSorter().sort(
        candidates=[
            {
                "id": "fake_package",
                "title": "Sell full package",
                "structural": 0.8,
                "status": "packageable",
                "paid_score": 0.3,
                "oversell": True,
            }
        ],
        paid={"status": "packageable", "paid_score": 0.3},
        sequence={"quality": 0.5, "sequence_length": 5},
        principles={"coherence": 0.5},
        situation_metrics={"situation_score": 0.3},
    )
    assert out["best"]["is_down"] is True or out["best"]["honesty"] < 0.5


def test_capital_efficiency_numbers():
    eng = CapitalEfficiencyEngine()
    r = eng.run(scenario_key="traction_200")
    a = r["per_orientation_usd"]["A_pure_llm_cloud"]["total_usd"]
    c = r["per_orientation_usd"]["C_metrix_architecture"]["total_usd"]
    assert a > c > 0
    assert r["comparisons"]["savings_C_vs_A_pct"] > 50
    assert "per_orientation_cost" in r["charts"]
    assert "scale_curve" in r["charts"]
    assert r["revenue_model_usd"]["gross_revenue"] > 50_000
    # all scenarios exist
    for k in MONTHLY_SCENARIOS:
        s = eng.run(scenario_key=k)
        assert s["monthly"]["C_metrix_architecture"]["total_ops_usd"] > 0


def test_nft_and_final_layer():
    nft = NFTCreateBuilding().build(
        industry_id="ai-agencies",
        business="We build AI agents that find growth points in client products and sell kits.",
        idea_title="Orientation-first delivery",
        paid={"paid_score": 0.62},
        principles={"active_principles": [{"key": "service_metrics"}, {"key": "concept"}]},
    )
    assert nft["token_draft"]["id"].startswith("nftcb_")
    assert len(nft["strange_generations"]) >= 5
    assert "tertiary_nets" in nft

    final = FinalProductLayer().run(
        industry_id="ai-agencies",
        business="We build AI agents that find growth points in client products and sell kits with pilots.",
        idea_title="Reverse outreach",
        request_id="test-final",
        paid={
            "status": "candidate_preview",
            "paid_score": 0.65,
            "package": {"top_lever": "clarity"},
            "conceptual_trajectory": {"residual_uncertainty": 0.32},
            "situation_metrics": {"situation_score": 0.48, "delivery_friction": 0.35},
        },
        scores={"clarity": 0.6, "impact": 0.55},
    )
    assert final["principles_engine"]["meanings_count"] >= 400
    assert final["sequence_assembler"]["plan_code"]
    assert final["anti_down_sorter"]["gate"]
    assert final["harness_showcase"]["live_mode"] is True
    assert final["ui_status"]["sellable"] is False  # preview
    assert final["capital_efficiency"]["comparisons"]["savings_C_vs_A_pct"] > 0
