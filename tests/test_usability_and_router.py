"""Text usability + category router + industry sanity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.category_router import route_categories
from backend.core.industry_sanity import load_sanity, match_variant
from backend.core.text_usability import polish_document, underhood_coverage


def test_dedupe_and_water():
    sections = {
        "diagnosis": (
            "You have free discovery. Free discovery burns margin. "
            "It is important to note free discovery burns margin. "
            "Utilization 55% leaves a gap. At $48000 revenue and 22% rework drag is $4752/mo "
            "which is order-of-magnitude and also utilization gap another calculation $6100."
        ),
        "situation": "Work flows from free discovery into scope explosion.",
    }
    out, rep = polish_document(sections, client_tokens={"discovery", "utilization", "margin"})
    assert rep["pass"] is True or rep["mean_score"] >= 0.65
    # diagnosis should not thrice repeat free discovery sentence-identical
    assert out["diagnosis"].lower().count("free discovery burns margin") <= 1


def test_router_ops_vs_promo():
    ops = route_categories(
        business="rework 22% utilization 50% free discovery scope explode margin",
        industry_id="ai-agencies",
        nums={"rework": 0.22, "utilization": 0.5, "gross_margin": 0.32},
    )
    assert ops["primary"] == "ops"
    promo = route_categories(
        business="we need more leads ads content outreach funnel audience growth",
        industry_id="ai-agencies",
        nums={},
    )
    assert promo["primary"] == "promotion"


def test_sanity_variant_match():
    pack = load_sanity("ai-agencies")
    assert pack.get("business_variants")
    v = match_variant(
        "ai-agencies",
        "Boutique custom agents for mid-market ops teams with retainers",
    )
    assert v is not None
    assert v.get("sane_primary")


def test_underhood_keys():
    cov = underhood_coverage(
        {
            "business": "x" * 30,
            "nums": {"a": 1},
            "demo_idea": {"title": "t"},
            "paid": {"package": {}, "function_engine": {}},
            "memo_convert": {"x": 1},
            "market_unit": {"product": {}},
        }
    )
    assert cov["used"] >= 5
