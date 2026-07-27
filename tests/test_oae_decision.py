"""Tests for Decision Core, OAE, Success Metrics, pipeline v2."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.decision_core import DecisionMakingCore
from backend.core.operational_analytics import OperationalAnalyticsEngine
from backend.core.orientation_engine import OrientationEngine
from backend.core.request_pipeline import process_client_request
from backend.core.success_metrics import SuccessMetricsPositioner
from backend.core.pragma_phenomena import evaluate_pragma_phenomena
from backend.paid.meaning_vectors import get_standard_paid_vectors


BIZ = (
    "We are a boutique AI agency building custom agents for mid-market ops teams "
    "with project packs and retainers. We need ready-made solutions and reverse outreach."
)


def test_success_metrics_custom_weights():
    sm = SuccessMetricsPositioner()
    tz = sm.build_tz(
        "t1",
        "ai-agencies",
        {"weights": {"iroi": 0.5, "clarity": 0.2}, "priority": ["iroi", "clarity"]},
    )
    assert tz.is_custom
    wm = tz.weight_map()
    assert abs(sum(wm.values()) - 1.0) < 1e-6
    assert wm["iroi"] > wm.get("er_leverage", 0)


def test_pragma_splitting():
    r = evaluate_pragma_phenomena(
        vvi=0.55,
        er=0.6,
        rrc=0.4,
        health=0.5,
        readiness=0.4,
        overall=0.4,
        info_roi=2.0,
        success_composite=0.4,
        success_target=0.62,
        product_fit=0.4,
        promo_fit=0.6,
    )
    assert r.triggered
    assert r.scoring_failed or r.demo_fast_path


def test_oae_embedding_and_ricochet():
    orient = OrientationEngine().orient(BIZ, "ai-agencies")
    od = orient.to_dict()
    sm = SuccessMetricsPositioner()
    tz = sm.build_tz("t2", "ai-agencies", {})
    card = sm.score(
        tz,
        readiness=0.5,
        overall=0.55,
        info_roi=2.5,
        vvi=orient.metrics.vvi,
        er=orient.metrics.er,
        rrc=orient.metrics.rrc,
        promo_fit=0.55,
        monetization_axis=0.5,
    )
    oae = OperationalAnalyticsEngine().run(
        business_text=BIZ,
        industry_id="ai-agencies",
        orientation=od,
        idea_title="Orientation-first delivery kit",
        vvi=orient.metrics.vvi,
        er=orient.metrics.er,
        rrc=orient.metrics.rrc,
        health=orient.metrics.health_score,
        info_roi=2.5,
        success_card=card.to_dict(),
        decision_mode="recursive_refinement",
    )
    d = oae.to_dict()
    assert len(d["embedding"]["vector"]) == 12
    assert d["processing_logic"]
    assert "paid_hook" in d and d["paid_hook"]["block"] == 18
    assert d["generative_hook"]["block"] == 19


def test_decision_core_mode():
    orient = OrientationEngine().orient(BIZ, "ai-agencies")
    dec = DecisionMakingCore().analyze(
        industry_id="ai-agencies",
        orientation=orient.to_dict(),
        vvi=0.5,
        er=0.55,
        rrc=0.4,
        health=0.55,
        info_roi=2.0,
        success_composite=0.45,
        success_target=0.62,
        success_influence={"prefer_generative": True},
        pragma_splits=[
            {
                "id": "x",
                "phenomenon": "scoring_fail_generative",
                "branch_mode": "generative_development",
                "severity": 0.6,
            }
        ],
        idea_title="test",
    )
    assert dec.active_mode in (
        "scoring",
        "generative_development",
        "recursive_refinement",
        "dual_ricochet",
    )
    assert dec.awareness_score > 0
    assert dec.thinking_process


def test_pipeline_v2_fields():
    out = process_client_request(
        {
            "industry": "ai-agencies",
            "business": BIZ,
            "track": "all",
            "success_metrics": {
                "weights": {"iroi": 0.35, "impact": 0.25},
                "composite_target": 0.55,
            },
        }
    )
    assert out["ok"] is True
    assert out.get("decision_core")
    assert out.get("operational_analytics")
    assert out.get("success_metrics")
    assert "operational_analytics" in out["zones_touched"]
    assert out["meta"].get("pipeline_version", "").startswith("2.")
    oae = out["operational_analytics"]
    assert oae.get("embedding")
    assert oae.get("reduced_to_request")


def test_paid_vectors_standard():
    vecs = get_standard_paid_vectors()
    assert len(vecs) >= 3
    assert any(v["stage"] == "custom_paid" for v in vecs)
