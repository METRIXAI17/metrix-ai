from __future__ import annotations

from backend.core.circle_system.certainty_analyzer import CertaintyAnalyzer
from backend.core.circle_system.knowledge_libs import (
    TRADITIONAL_ARTEFACTS,
    get_traditional_artefact,
    list_traditional_artefacts,
)
from backend.core.circle_system.resource_chain import ResourceAssemblyEngine


def test_library_24():
    assert len(TRADITIONAL_ARTEFACTS) == 24
    assert list_traditional_artefacts("safety")
    assert list_traditional_artefacts("qol")


def test_contested_does_not_raise_assembly():
    art = get_traditional_artefact("ta_handshake_only_c")
    assert art["evidence_grade"] == "contested"
    ra = ResourceAssemblyEngine().bind(
        [{"artefact_id": "ta_handshake_only_c", "confidence": 0.99}],
        request_payload={"industry_id": "ai-agencies", "business": "handshake only deal maybe"},
        voids={"vvi": 0.35},
        persist=False,
    )
    # contested confidence is 0 → does not close critical slots honestly
    rh = ra["bound_slots"].get("revenue_hinge")
    if rh:
        assert float(rh["confidence"]) == 0.0
    assert ra["compatibility"] < 0.45


def test_safety_contra_raises_risk():
    art = get_traditional_artefact("ta_pain_push_c")
    assert "healthcare" in art["contra_indications"]
    assert art["risk_delta"] > 0


def test_qol_only_claimed_slots():
    art = get_traditional_artefact("ta_notice_batch_q")
    assert "signal_port" in art["affects"]
    assert "void_membrane" not in art["affects"]


def test_artefact_prior_does_not_force_cy():
    prior = get_traditional_artefact("ta_written_terms_s")
    r = CertaintyAnalyzer().run(
        "может быть оффер, примерно, неясно",
        industry_id="ai-agencies",
        artefact_priors=[prior],
    )
    # hedge-heavy text stays U even with CY prior
    statuses = {p["slot"]: p["status"] for p in r["parameters"]}
    assert "certain_yes" not in statuses.values() or any(
        p.get("status") == "uncertain" for p in r["parameters"]
    )
