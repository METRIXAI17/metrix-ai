from __future__ import annotations

from backend.core.circle_system.copy_firmware import CopyFirmware, FORBIDDEN
from backend.core.circle_system.linguistic_warmth import LinguisticWarmthEngine


def test_warmth_does_not_change_certainty():
    fw = CopyFirmware()
    out = fw.render(
        status="uncertain",
        body_fact="slot outcome_frame empty",
        next_action="bind a resource",
        assembly_score=0.8,
        voice="b2c",
        lang="en",
        certain_yes_ratio=0.9,
    )
    assert out["answer"]["status"] == "uncertain"
    assert out["answer"]["certainty_untouched"] is True


def test_forbidden_stripped():
    fw = CopyFirmware()
    t = fw.strip_forbidden("We guarantee results and risk-free Main without a pilot")
    low = t.lower()
    assert "guarantee" not in low
    assert "risk-free" not in low


def test_three_voices():
    fw = CopyFirmware()
    b2c = fw.offer_block(who="shop", void="ops void", gate="assembly≥0.45", price="free", not_included="Main $2490", voice="b2c")
    a2a = fw.offer_block(who="agency", void="handoff", gate="sync", price="coord", not_included="B2C ads", voice="a2a")
    tw = fw.offer_block(who="spec", void="terminal", gate="ASM", price="n/a", not_included="warmth", voice="tech_write")
    assert b2c["who"] and a2a["who"] and tw["text"].startswith("SPEC")
    assert len(FORBIDDEN) >= 10
    freeze = fw.freeze_corpus()
    assert len(freeze["canonical"]) >= 10


def test_warmth_engine_independent():
    w = LinguisticWarmthEngine().score(assembly_score=0.2, certain_yes_ratio=0.9)
    assert w["cap_reason"] == "assembly_weak"
    assert "certainty status is independent" in w["note"].lower() or "independent" in w["note"].lower()
