"""Niche answer base + free work flow."""

from __future__ import annotations

from backend.core.circle_system.free_work_flow import FreeWorkFlow
from backend.core.circle_system.niche_answer_base import NicheAnswerBase, NICHE_BASE


def test_niche_all_industries_all_directions():
    base = NicheAnswerBase()
    for ind in NICHE_BASE:
        for track in ("ops", "product", "promotion"):
            r = base.resolve(ind, track=track, lang="ru", business="x" * 40)
            assert r["answer"]
            assert r["direction"] == track
            assert r["success_metric"]


def test_founders_lane():
    f = NicheAnswerBase().founders_lane("ru")
    assert "@andrewsmm1" in f["for"]
    assert len(f["joint_deliverables_free"]) >= 3
    assert f["display_hook"]


def test_free_work_start_and_clarify():
    fw = FreeWorkFlow()
    start = fw.start(
        business=(
            "AI agency: delivery chaos, 12 clients, want Terminal Teammate, "
            "budget 5000 USD, pilot 21 days, margin pressure, branding VA ready."
        ),
        industry_id="ai-agencies",
        track="ops",
        name="Test",
        lang="ru",
    )
    assert start["ok"]
    assert start["work_id"]
    assert start["phases"]
    assert start["quality_answer"]["answer"]
    assert start["founders_lane"]
    assert start["cta"]["label"]

    clar = fw.submit_clarifications(
        start["work_id"],
        {
            "weekly_delivery_count": "8",
            "margin_per_engagement": "35%",
            "rework_percent": "22",
            "who_owns_client_success": "Anna",
        },
        lang="ru",
    )
    assert clar["ok"]
    assert clar["quality_answer"]["quality_score"] >= start["quality_answer"]["quality_score"]

    adv = fw.advance_phase(start["work_id"])
    assert adv["ok"]
    assert adv["current_phase"]
