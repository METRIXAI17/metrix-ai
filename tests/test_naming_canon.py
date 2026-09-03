from __future__ import annotations

from backend.core.circle_system.miniapp_cases import pack_miniapp_case
from backend.core.circle_system.resource_chain import ResourceAssemblyEngine
from backend.core.naming_canon import CANON, chain_sigil, reject_esoteric, sigil


FULL = [
    {"id": "note_goal", "type": "human_note", "slots": ["outcome_frame"], "confidence": 0.9},
    {"artefact_id": "ta_sleep_gate_s"},
    {"artefact_id": "ta_written_terms_s"},
    {"artefact_id": "ta_circle_check_s"},
    {"market_unit_id": "mu_ai"},
]


def test_canon_table_and_forbid():
    assert len(CANON) >= 6
    assert reject_esoteric("this is luck and destiny")
    assert not reject_esoteric("assembly score 0.45")


def test_sigil_stable_on_same_fragments():
    fr = ["outcome_frame", "void_membrane"]
    a = chain_sigil("seed1", fr)
    b = chain_sigil("seed1", fr)
    assert a == b
    c = chain_sigil("seed1", ["revenue_hinge"])
    assert a != c


def test_miniapp_case_requires_gates():
    ra = ResourceAssemblyEngine().bind(
        FULL,
        request_payload={"industry_id": "ai-agencies", "business": "ops map with terms and owner and pilot gate"},
        voids={"vvi": 0.3},
        persist=True,
    )
    # default stored record has no consistency ≥ 0.62 → pack refused
    packed = pack_miniapp_case(ra["chain_id"])
    assert packed["ok"] is False
    assert packed["error"] == "gates_closed"
