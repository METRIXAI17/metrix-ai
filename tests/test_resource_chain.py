from __future__ import annotations

from backend.core.circle_system.resource_chain import ResourceAssemblyEngine, chain_seed_of


FULL = [
    {"id": "note_goal", "type": "human_note", "human_note": "goal: cut ops chaos", "slots": ["outcome_frame"], "confidence": 0.85},
    {"artefact_id": "ta_sleep_gate_s", "confidence": 0.8},
    {"artefact_id": "ta_written_terms_s", "confidence": 0.8},
    {"artefact_id": "ta_circle_check_s", "confidence": 0.8},
    {"market_unit_id": "mu_ai_agencies", "confidence": 0.7},
]

LEAKY = [
    {"artefact_id": "ta_handshake_only_c"},
    {"artefact_id": "ta_crowd_wisdom_c"},
    {"artefact_id": "ta_always_on_c"},
]


def test_full_bind_assembly_can_pass():
    ra = ResourceAssemblyEngine().bind(
        FULL,
        request_payload={"industry_id": "ai-agencies", "business": "AI agency ops map with written terms and a named owner for the weak link, pilot 21 days."},
        voids={"vvi": 0.5},
        persist=True,
    )
    assert ra["chain_id"]
    assert ra["chain_seed"]
    assert "outcome_frame" in ra["bound_slots"]
    assert ra["compatibility"] >= 0.45
    assert ra["void_delta"] >= 0


def test_leaky_bind_vvi_rises_pilot_closed():
    ra = ResourceAssemblyEngine().bind(
        LEAKY,
        request_payload={"industry_id": "ai-agencies", "business": "maybe something vague without a metric or offer"},
        voids={"vvi": 0.4},
        persist=True,
    )
    assert ra["unbound_critical"]
    assert ra["void_delta"] < 0
    assert ra["vvi_after_bind"] > 0.4
    assert ra["compatibility"] < 0.45


def test_bind_idempotent_seed():
    a = ResourceAssemblyEngine().bind(FULL, request_payload={"industry_id": "ai-agencies", "business": "x" * 24}, persist=False)
    b = ResourceAssemblyEngine().bind(FULL, request_payload={"industry_id": "ai-agencies", "business": "x" * 24}, persist=False)
    assert a["chain_seed"] == b["chain_seed"]
    assert a["chain_id"] == b["chain_id"]


def test_no_invented_matrix():
    ra = ResourceAssemblyEngine().bind(FULL, request_payload={"industry_id": "ai-agencies", "business": "y" * 24}, persist=False)
    assert "deadlock_risk" in ra["coordination"]
    assert "load_balance" in ra["coordination"]
