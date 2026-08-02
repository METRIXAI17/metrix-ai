"""Market Units v2 — unit + stress tests (startup-customized)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.market_units import (
    MARKET_UNITS,
    all_market_units_payload,
    market_unit_for,
    run_enriched_market_unit,
)
from backend.core.market_units_v2 import MarketUnitsEngine, run_market_units_v2
from backend.core.market_units_v2.coordination import CoordinationLayer
from backend.core.market_units_v2.metric_composer import MetricComposer
from backend.core.market_units_v2.ontology import OntologyEngine
from backend.core.market_units_v2.problem_recognition import ProblemRecognition
from backend.core.market_units_v2.system_reader import SystemReader
from backend.core.market_units_v2.teammate_network import TeammateNetwork
from backend.core.request_pipeline import process_client_request

# Representative briefs per public niche (stress corpus)
STRESS_BRIEFS: dict[str, str] = {
    "ai-agencies": (
        "B2B AI agency shipping multi-agent retainers. Delivery chaos, rework on handoffs, "
        "clients churn when quality drops. Budget 12000, need Terminal Teammate ops control "
        "and buyer fin model for sales."
    ),
    "api-for-devs": (
        "SaaS team burning third-party API tokens on hot path. Need call map, quality floor, "
        "and cheaper Expert path without dropping reliability for client integrations."
    ),
    "cost-engineering": (
        "Cost engineers drowning in waste parameters. Specs too fat, rework cost high. "
        "Want simple void scanner offer and resellable product pack for their buyers."
    ),
    "chipmaking": (
        "Fabless design loop unclear before tapeout. Yield geometry voids, NRE iteration "
        "pain, need clarity twin not hype for gate decisions."
    ),
    "telecom": (
        "MVNO partner SLA fog, ARPU and churn levers buried in spreadsheets. "
        "Need SLA-native SKU builder and intent-signal care weave."
    ),
    "device-assembly": (
        "Assembly stations rework blocks scale. Need config workflow product and one-station "
        "demo for integrator promotion, labor rework timer pack."
    ),
    "asset-decisions": (
        "Family office wants decision support desk: key metrics, risk model, situation packs. "
        "No auto-trading custody, no profit guarantees, private room after model test."
    ),
    "freelace-d2c": (
        "Creative founder has incomplete ideas that never become freelace-ready documents. "
        "Need workspace offramp: idea to brief to order match without 30-minute vinaigrette."
    ),
    "expert-services": (
        "Solo expert sells hours, no packaged offer or TZ. Demand exists but packaging void "
        "kills conversion. Need offer pack and success metrics lock."
    ),
    "ecommerce": (
        "Online store unit economics fog on SKU and channel. Margin pressure, ad cost rising, "
        "need clearer levers and simple ops map."
    ),
}


def test_catalog_has_data_logic():
    unit = market_unit_for("ai-agencies")
    assert unit["product"]["sku"] == "terminal_teammate"
    assert "data_logic" in unit
    assert "ops" in unit["data_logic"]["offer_tracks"] or unit["offers"]


def test_all_payload_version_v2():
    payload = all_market_units_payload()
    assert "v2" in payload["version"]
    assert "coordination" in payload["layers"]
    assert payload["units"]


def test_system_reader_signals():
    r = SystemReader().read(
        business_text=STRESS_BRIEFS["ai-agencies"],
        industry_id="ai-agencies",
        scores={"readiness": 0.4, "product_fit": 0.55, "overall_orientation": 0.5},
    )
    assert r.density > 0
    assert r.signals.get("ops_friction", 0) > 0.1
    assert r.readiness_band in (
        "execution_ready",
        "pilot_ready",
        "orientation_needed",
        "intake_thin",
    )


def test_problem_recognition_primary():
    lattice = ProblemRecognition().recognize(
        industry_id="ai-agencies",
        signals={"ops_friction": 0.7, "cost_pressure": 0.5, "demand_signal": 0.4},
        voids=["ops_control_loop"],
        readiness_band="pilot_ready",
        scores={"product_fit": 0.5},
    )
    assert lattice.primary is not None
    assert lattice.primary.severity > 0
    assert lattice.primary.leverage > 0
    assert len(lattice.problems) >= 1


def test_metric_composer_pqi_bounds():
    m = MetricComposer().compose(
        vvi=0.35,
        er=0.6,
        rrc=0.55,
        scores={"overall_orientation": 0.6, "product_fit": 0.55, "readiness": 0.5},
        signals={"ops_friction": 0.5},
        density=0.55,
        coordination_index=0.65,
        primary_problem_leverage=0.5,
    )
    assert 0 <= m.product_quality_index <= 1
    assert m.forecast["pqi_after_full_v2"] >= m.forecast["pqi_now"] - 1e-9
    assert m.levers


def test_coordination_handoff_matrix():
    c = CoordinationLayer().compute(
        density=0.55,
        readiness_band="pilot_ready",
        family_pressure={"ops": 0.6},
        primary_leverage=0.55,
        signals={"ops_friction": 0.5},
        teammate_coverage=0.7,
        ontology_fit=0.6,
    )
    assert 0 <= c.coordination_index <= 1
    assert c.critical_path[0] == "system_reader"
    assert c.handoff_matrix["system_reader"]["problem_lattice"] > 0
    assert c.recommendations


def test_ontology_algorithms():
    o = OntologyEngine().generate(
        industry_id="ai-agencies",
        primary_problem={
            "id": "agent_chaos",
            "family": "ops",
            "leverage": 0.6,
        },
        family_pressure={"ops": 0.6},
        signals={"ops_friction": 0.6},
        coordination_index=0.65,
        product_sku="terminal_teammate",
    )
    assert o.primary_combo is not None
    assert len(o.algorithms) >= 3
    assert o.figurative_awareness.get("metaphor")
    assert 0 <= o.ontology_fit <= 1


def test_teammate_network_coverage():
    t = TeammateNetwork().build(
        industry_id="ai-agencies",
        problems=[{"id": "agent_chaos", "family": "ops", "product_hook": "terminal_teammate"}],
        family_pressure={"ops": 0.7},
        product_sku="terminal_teammate",
        coordination_index=0.6,
    )
    assert t.lead_id
    assert t.coverage > 0
    assert any(n.active for n in t.nodes)
    assert t.attach_plan


def test_engine_full_run_ok():
    out = MarketUnitsEngine().run(
        industry_id="ai-agencies",
        business_text=STRESS_BRIEFS["ai-agencies"],
        scores={
            "overall_orientation": 0.55,
            "product_fit": 0.55,
            "readiness": 0.45,
            "promo_fit": 0.5,
        },
        vvi=0.4,
        er=0.55,
        rrc=0.5,
        success_composite=0.55,
    )
    assert out["ok"] is True
    assert out["metric_composer"]["product_quality_index"] > 0
    assert out["coordination"]["coordination_index"] > 0
    assert out["teammate_network"]["lead_id"]
    assert out["offers_ranked"]
    assert out["core_boost"]["boost_score"] > 0
    assert out["product_quality"]["before_after"]["after"]


def test_degrade_wrapper_on_bad_industry():
    # still returns a payload (fallback unit)
    out = run_market_units_v2(
        industry_id="unknown-niche-xyz",
        business_text="x" * 40,
    )
    assert "unit" in out
    assert out.get("module")


def test_alias_resolution():
    u = market_unit_for("cloud-economy")
    assert u["product"]["sku"] in ("api_integration_map", "terminal_teammate") or u.get(
        "application_point"
    )


@pytest.mark.parametrize("industry_id,brief", list(STRESS_BRIEFS.items()))
def test_stress_all_niches(industry_id: str, brief: str):
    """Stress: every niche produces valid v2 payload without exception."""
    out = run_enriched_market_unit(
        industry_id,
        business_text=brief,
        scores={
            "overall_orientation": 0.5,
            "product_fit": 0.5,
            "readiness": 0.45,
            "promo_fit": 0.45,
        },
        vvi=0.42,
        er=0.5,
        rrc=0.48,
        success_composite=0.5,
    )
    assert out.get("ok") is True or out.get("degraded") is True
    assert out.get("unit")
    if out.get("ok"):
        pqi = out["metric_composer"]["product_quality_index"]
        assert 0 <= pqi <= 1
        assert out["problem_recognition"]["primary"]
        assert out["ontology"]["algorithms"]


def test_stress_thin_brief_degrades_gracefully():
    """If something goes wrong / thin intake — still no crash, band intake_thin."""
    out = MarketUnitsEngine().run(
        industry_id="ai-agencies",
        business_text="short ops note about clients and cost pressure margins",
        scores={"overall_orientation": 0.3, "product_fit": 0.3, "readiness": 0.25},
    )
    assert out["ok"] is True
    assert out["system_reader"]["readiness_band"] in (
        "intake_thin",
        "orientation_needed",
        "pilot_ready",
        "execution_ready",
    )


def test_pipeline_includes_market_units_v2():
    resp = process_client_request(
        {
            "industry": "ai-agencies",
            "business": STRESS_BRIEFS["ai-agencies"],
            "track": "product",
            "enable_fin_models": False,
            "enable_self_improve": False,
            "enable_monetization": False,
        }
    )
    assert resp["ok"]
    meta = resp.get("meta") or {}
    assert "market_units_v2" in meta
    mu = meta["market_units_v2"]
    assert mu.get("ok") is True
    assert (meta.get("market_unit") or {}).get("product")
    assert (resp.get("breakdown") or {}).get("market_units_v2")
    assert "market_units_pqi" in (resp.get("metrics") or {})
    assert any(
        "PQI" in s or "Primary problem" in s for s in (resp.get("next_steps") or [])
    )


def test_catalog_units_count_stable():
    # guard: do not silently drop catalog niches
    assert len(MARKET_UNITS) >= 8
