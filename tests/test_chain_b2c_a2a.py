from __future__ import annotations

from backend.core.circle_system.chain_topologies import B2CChain, detect_topology
from backend.core.market_units import run_enriched_market_unit
from backend.monetization.outreach_massmarket_a2a import A2AMassmarketOutreach


AGENCY = (
    "Two digital agencies need a handoff matrix and teammate mesh on a shared Market Unit, "
    "deadlock risk on ops/product lanes, A2A coordination not a shop consult."
)
CONSUMER = (
    "I need a free consult for my small online shop, pick a direction and a 14-day pilot, "
    "then maybe the main package after gates."
)


def test_topology_split():
    assert detect_topology(AGENCY) == "a2a"
    assert detect_topology(CONSUMER) == "b2c"


def test_b2c_start_creates_chain_seed():
    out = B2CChain().start(
        business=CONSUMER,
        industry_id="ecommerce",
        lang="en",
        resources=[{"type": "human_note", "human_note": "shop consult", "slots": ["outcome_frame"], "confidence": 0.7}],
    )
    assert out["ok"] is True
    assert out["chain_id"]
    assert out["chain_seed"]
    assert out["topology"] == "b2c"
    assert out["phases"][0]["id"] == "D0-1"


def test_agency_does_not_get_b2c_stepper():
    mu = run_enriched_market_unit(
        "ai-agencies",
        business_text=AGENCY,
        orientation={"scores": {"overall_orientation": 0.6}},
        chain_mode="a2a",
    )
    assert mu.get("a2a_chain")
    assert mu.get("b2c_stepper") is False
    assert "artefact_handoffs" in mu["a2a_chain"]


def test_consumer_not_handoff_matrix():
    out = B2CChain().start(business=CONSUMER, industry_id="ecommerce", lang="en")
    assert "handoff_matrix" not in out
    assert "a2a_chain" not in out


def test_massmarket_a2a_no_lead_promise():
    out = A2AMassmarketOutreach().run(industry_id="ai-agencies", business_text=AGENCY, lang="en")
    assert out["lead_promise"] is False
    assert out["flag"] == "massmarket_a2a"
    assert len(out["outreach_artefacts"]) == 3
    assert out["flag"] != "d2c-offramp"
