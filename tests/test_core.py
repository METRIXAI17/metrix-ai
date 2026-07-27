"""Unit tests for core metrics, orientation, pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.metrics import (
    compute_core_metrics,
    compute_er,
    compute_rrc,
    compute_vvi,
    informational_roi,
)
from backend.core.orientation_engine import OrientationEngine
from backend.core.request_pipeline import process_client_request
from backend.fin_models.registry import get_fin_model_registry
from backend.modules.specsforge import SpecsForgeRecursiveOracle


def test_vvi_er_rrc_bounds():
    v = compute_vvi(5, 10, 0.2, 0.1, 1)
    e = compute_er(4, 3, 0, 0.2)
    r = compute_rrc(6, 4, 0.5, 2, 4)
    assert 0 <= v <= 1
    assert 0 <= e <= 1
    assert 0 <= r <= 1


def test_core_metrics_health():
    m = compute_core_metrics(
        known_params=8,
        required_params=10,
        ambiguity_score=0.2,
        detected_errors=3,
        actionable_errors=2,
        fragments=5,
        successful_reassemblies=3,
    )
    assert m.health_score > 0
    assert "vvi" in m.labels


def test_info_roi():
    roi = informational_roi(0.8, 0.7, 0.7, 0.3, 0.2, 0.1)
    assert roi > 1.0


def test_orientation_ai_agencies():
    eng = OrientationEngine()
    res = eng.orient(
        "AI agency building agents for ops teams with retainer and demo offers",
        "ai-agencies",
    )
    assert res.frame.industry_id == "ai-agencies"
    assert "product_fit" in res.scores
    assert res.operating_mode


def test_specsforge_recursion():
    oracle = SpecsForgeRecursiveOracle()
    out = oracle.refine(
        "We need a product that orients client businesses and sells ready solutions.",
        "ai-agencies",
    )
    assert out.iterations >= 1
    assert out.final_metrics.health_score >= 0
    assert out.root.children


def test_all_fin_models_run():
    reg = get_fin_model_registry()
    ctx = {
        "industry_id": "chipmaking",
        "scores": {
            "product_fit": 0.6,
            "model_fit": 0.7,
            "promo_fit": 0.5,
            "readiness": 0.6,
            "overall_orientation": 0.6,
        },
        "axes": {
            "value_density": 0.6,
            "time_pressure": 0.4,
            "complexity": 0.7,
            "monetization_fit": 0.5,
            "risk": 0.4,
        },
        "operating_mode": "fin_model_focus",
    }
    for mid in reg.list_models():
        result = reg.run(mid["id"], ctx)
        assert result["info_roi"] >= 0
        assert "stage1_definition" in result["three_stage"]
        assert "stage2_general_paid" in result["three_stage"]
        assert "stage3_custom_paid" in result["three_stage"]


def test_pipeline_telecom():
    out = process_client_request(
        {
            "industry": "telecom",
            "business": (
                "MVNO platform with QoS issues, ARPU pressure, and need for "
                "linguistic signal cooperation between care agents and core network."
            ),
            "track": "product",
            "name": "Test",
        }
    )
    assert out["ok"] is True
    assert out["demo_idea"]
    assert out["fin_models"]
    assert out["monetization"]
    assert "promo" in out["monetization"]


def test_pipeline_multi_idea_portfolio():
    """Backend must return several ideas for exhaustive ops-success improvement."""
    out = process_client_request(
        {
            "industry": "ai-agencies",
            "business": (
                "AI agency, 12 people. We build custom GPT agents and RAG bots for "
                "mid-market SaaS. Utilization about 55%, rework high, need packaging "
                "and pricing levers without free discovery burn."
            ),
            "track": "all",
            "name": "Portfolio Test",
            "extra_params": {
                "utilization": 0.55,
                "gross_margin": 0.32,
                "rework_rate": 0.22,
            },
        }
    )
    assert out["ok"] is True
    ideas = out.get("demo_ideas") or []
    assert len(ideas) >= 3, f"expected multi-idea portfolio, got {len(ideas)}"
    assert ideas[0].get("is_primary") is True or ideas[0].get("rank") == 1
    assert out["demo_idea"].get("title")
    # primary title matches first portfolio item
    assert out["demo_idea"]["title"] == ideas[0]["title"]
    roles = {i.get("role") for i in ideas if i.get("role")}
    assert len(roles) >= 2
    assert out["meta"].get("idea_count", 0) >= 3
    # product_result also carries list
    pr = (out.get("meta") or {}).get("product_result") or {}
    assert len(pr.get("demo_ideas") or []) >= 3


def test_pipeline_validation():
    out = process_client_request({"industry": "", "business": "short"})
    assert out["ok"] is False
    assert out["errors"]
