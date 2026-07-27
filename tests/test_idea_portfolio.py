"""Tests for multi-idea portfolio engine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.idea_portfolio import IdeaPortfolioEngine, MIN_IDEAS
from backend.zones.product_sol import IDEA_SEEDS, ProductSolZone


def test_portfolio_builds_multiple_ideas():
    eng = IdeaPortfolioEngine(idea_seeds=IDEA_SEEDS)
    orientation = {
        "scores": {
            "product_fit": 0.45,
            "model_fit": 0.4,
            "promo_fit": 0.5,
            "readiness": 0.48,
            "overall_orientation": 0.5,
        },
        "tracks_recommended": ["product", "models", "promotion"],
        "frame": {"seed": "ab12"},
        "operating_mode": "balanced",
    }
    port = eng.build(
        business_text=(
            "Agency with low utilization, high rework, margin pressure, "
            "needs packaging and pricing without free discovery calls."
        ),
        industry_id="ai-agencies",
        orientation=orientation,
        primary_track="product",
        specs_ready=False,
    )
    assert len(port.ideas) >= MIN_IDEAS
    assert port.primary["title"]
    assert port.coverage["exhaustive_enough"] is True
    assert port.ideas[0]["rank"] == 1


def test_product_sol_returns_demo_ideas_list():
    zone = ProductSolZone()
    out = zone.run(
        business_text=(
            "Cloud cost consultancy for startups on AWS and GCP with idle GPU waste "
            "and need for FinOps board."
        ),
        industry_id="cloud-economy",
        orientation={
            "scores": {
                "product_fit": 0.55,
                "model_fit": 0.5,
                "promo_fit": 0.45,
                "readiness": 0.5,
                "overall_orientation": 0.52,
            },
            "frame": {"seed": "cf01"},
            "operating_mode": "product_focus",
        },
        primary_track="product",
        specs_ready=True,
    )
    d = out.to_dict()
    assert len(d["demo_ideas"]) >= 3
    assert d["demo_idea"]["title"] == d["demo_ideas"][0]["title"]
    assert d["portfolio"]["count"] >= 3
