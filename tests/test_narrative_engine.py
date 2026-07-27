"""Narrative semantic engine — relations, anticlone, 4-pass, client memo."""

from __future__ import annotations

from backend.paid.narrative.anticlone import AnticloneEditor
from backend.paid.narrative.semantic_engine import NarrativeSemanticEngine
from backend.paid.narrative.values_and_templates import VALUE_CATALOG


def test_value_catalog_nonempty():
    assert len(VALUE_CATALOG) >= 10


def test_anticlone_reduces_templates():
    sents = [
        "Oriented to your geometry: we do things.",
        "Oriented to your geometry: we do more things.",
        "Proceed to pilot tz without client words.",
    ]
    out = AnticloneEditor().run(
        sentences=sents,
        client_tokens=["agency", "rework", "utilization"],
        numbers={"utilization": 0.55},
        true_hubs=["agency"],
        void_notes=["must-ask open"],
    )
    assert out["edited_sentences"]
    assert out["template_index_before"] >= 0.3


def test_narrative_engine_full_pass():
    eng = NarrativeSemanticEngine()
    paid = {
        "status": "candidate_preview",
        "paid_score": 0.72,
        "package": {
            "title": "Parameter-map pricing",
            "top_lever": "promo_fit",
            "best_hypothesis": "Pilot orientation kits with metric owners",
            "root_alignment": 0.7,
            "informational_compatibility": 0.75,
            "paid_readiness": 0.65,
        },
        "situation_metrics": {
            "situation_score": 0.55,
            "top_leak": {
                "label": "Free discovery burns senior utilization",
                "severity": 0.62,
                "form": "Unpaid scoping eats 55% senior capacity",
            },
        },
        "function_engine": {"top_lever": "promo_fit", "output_plane": {"paid_readiness": 0.65}},
        "conceptual_trajectory": {"residual_uncertainty": 0.3},
    }
    r = eng.run(
        industry_id="ai-agencies",
        business=(
            "AI agency with 12 people building RAG bots for SaaS. "
            "Senior utilization 55%, high rework, free discovery burns margin."
        ),
        idea_title="Parameter-map pricing instead of bloated retainers",
        paid=paid,
        scores={"clarity": 0.6, "impact": 0.58},
        extra_params={
            "utilization": 0.55,
            "gross_margin": 0.32,
            "cycle_days": 35,
            "rework_rate": 0.22,
            "monthly_revenue": 48000,
        },
        must_ask_open=0,
    )
    assert r["relations"]["true_count"] >= 1
    assert r["probability_map"]["top_positive"]
    assert r["passes"]["3_anticlone"]["edited_sentences"]
    assert r["passes"]["4_product_closure"]["products_closed"] >= 1
    assert r["memo"]["executive_summary"]
    assert "Oriented to your geometry" not in r["memo"]["executive_summary"]
    assert r["values"]["values_present"]
    assert r["product_templates"]
    assert r["quality"]["consistency_score"] is not None
