"""Tests for Memo Convert engine + Market Units (v1.1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.market_units import (
    MARKET_UNITS,
    package_cost_report,
    simple_offers,
)
from backend.core.memo_convert import MemoConvertEngine
from backend.core.request_pipeline import process_client_request


def test_memo_convert_basic():
    eng = MemoConvertEngine()
    out = eng.convert(
        business_text=(
            "Boutique AI agency with 55% utilization, 22% rework, "
            "custom agents for mid-market ops teams and retainer chaos"
        ),
        industry_id="ai-agencies",
        orientation={
            "scores": {
                "overall_orientation": 0.72,
                "readiness": 0.6,
                "product_fit": 0.65,
                "promo_fit": 0.5,
            },
            "frame": {"axes": {"value_density": 0.6, "risk": 0.3}},
        },
        ideas=[
            {"title": "Terminal Teammate for agency ops efficiency", "track": "product", "score": 0.8},
            {"title": "Buyer financial model for Teammate sale", "track": "models", "score": 0.7},
        ],
    ).to_dict()
    assert out["module"] == "Memo Convert Engine"
    assert out["analog_engine"]["selected_function"]
    assert out["analog_engine"]["refuses_raw_values"] is True
    assert len(out["open_opportunities"]) >= 1
    assert len(out["technical_tasks"]) >= 2
    assert out["categorical_data"]["dominant_category"]
    assert out["engine_on_same_arch"]["feasible"] is True
    assert "tech write" in out["technical_tasks"][0]["language"].lower() or "TASK" in out[
        "technical_tasks"
    ][0]["language"]


def test_memo_convert_cloud_api_path():
    eng = MemoConvertEngine()
    out = eng.convert(
        business_text=(
            "Founder building creative tools burns OpenAI and Anthropic API "
            "tokens on every custom operation and wants lower cost higher quality"
        ),
        industry_id="cloud-economy",
        orientation={
            "scores": {"overall_orientation": 0.6, "readiness": 0.55},
            "frame": {"axes": {}},
        },
    ).to_dict()
    assert out["analog_engine"]["selected_function"] == "api_cost_collapse"
    assert any(
        "api" in o["title"].lower() or o["system_category"] == "third_party_api_spend"
        for o in out["open_opportunities"]
    )


def test_package_cost_consult_techwrite():
    report = package_cost_report()
    primary = report["primary_package"]
    assert primary["client_price_usd"] == 1290
    assert primary["if_bought_separate_usd"] == 1540
    assert primary["bundle_discount_usd"] == 250
    assert primary["ops_variable_total_usd"] == 3.0
    assert primary["structural_savings_x"] == 12.5
    assert report["related_ladder"]["full_orientation_usd"] == 2490


def test_chipmaking_three_offers():
    offers = simple_offers("chipmaking")
    tracks = {o["track"] for o in offers}
    assert tracks == {"ops", "product", "promotion"}
    assert len(offers) == 3


def test_telecom_offers():
    offers = simple_offers("telecom")
    assert len(offers) == 3
    assert MARKET_UNITS["telecom"]["product"]["name"]


def test_cost_engineering_two_simple():
    offers = simple_offers("cost-engineering")
    assert len(offers) == 2
    assert any(o["price_usd"] == 290 for o in offers)


def test_pipeline_includes_memo_convert():
    res = process_client_request(
        {
            "industry": "ai-agencies",
            "business": (
                "We run an AI agency for mid-market ops teams with retainers, "
                "high rework and need operational efficiency with a teammate console"
            ),
            "name": "Test",
            "contact": "@test",
        }
    )
    assert res["ok"]
    meta = res["meta"]
    assert "memo_convert" in meta
    assert meta["memo_convert"]["analog_engine"]["selected_function"]
    assert "market_unit" in meta
    assert meta["market_unit"]["product"]["name"] == "Terminal Teammate"
    assert meta["package_costs"]["primary_package"]["client_price_usd"] == 1290
    assert "memo_convert" in res["zones_touched"]
    assert str(meta.get("pipeline_version") or "").startswith("2.")
    assert "memo_convert" in (res.get("breakdown") or {})

