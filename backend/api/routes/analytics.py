"""Decision Core + Operational Analytics + Success Metrics + Paid Core endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.decision_core import DecisionMakingCore
from backend.core.market_units import all_market_units_payload, market_unit_for, package_cost_report
from backend.core.memo_convert import MemoConvertEngine
from backend.core.operational_analytics import OperationalAnalyticsEngine
from backend.core.orientation_engine import OrientationEngine
from backend.core.success_metrics import SuccessMetricsPositioner
from backend.core.system_log import SystemLogAnalyst
from backend.paid.meaning_vectors import get_standard_paid_vectors
from backend.paid.capital_efficiency import CapitalEfficiencyEngine, MONTHLY_SCENARIOS
from backend.paid.commercial_layer import CommercialLayer
from backend.paid.final_layer import FinalProductLayer
from backend.paid.orchestrator import PaidProductCore, flow_overview
from backend.paid.principles_engine import get_principles_engine
from backend.paid.system_design_library import get_system_design_library
from backend.paid.virtual_chips import get_virtual_chip_library

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsBody(BaseModel):
    industry: str
    business: str = Field(..., min_length=20)
    track: str | None = None
    success_metrics: dict = Field(default_factory=dict)
    info_roi_hint: float = 2.0
    force_paid: bool = True


@router.get("/system-log")
def system_log() -> dict[str, Any]:
    return SystemLogAnalyst().analyze().to_dict()


@router.get("/paid-vectors")
def paid_vectors() -> dict[str, Any]:
    return {
        "block": 18,
        "status": "standard_vectors_ready",
        "vectors": get_standard_paid_vectors(),
    }


@router.get("/paid-catalog")
def paid_catalog() -> dict[str, Any]:
    """System Design Library + Virtual Chip templates overview."""
    lib = get_system_design_library()
    chips = get_virtual_chip_library()
    return {
        "block": 18,
        "module": "Paid Product Core catalog",
        "flow": flow_overview(),
        "directions": lib.list_directions(),
        "categories": lib.list_categories(),
        "template_count": len(lib.list_all()),
        "chip_templates": chips.list_templates(),
        "components": [
            "system_design_library",
            "virtual_chips",
            "function_calculation_engine",
            "energy_flow_disentangler",
            "calm_point_image_generator",
            "mega_map_builder",
            "hypothesis_modules",
            "hypothesis_library",
            "reader",
            "critical_thinking_layer",
            "metric_tests",
        ],
    }


@router.get("/paid-flow")
def paid_flow() -> dict[str, Any]:
    """16-step staged flow overview (corrected)."""
    return flow_overview()


@router.get("/capital-efficiency")
def capital_efficiency(scenario: str = "traction_200") -> dict[str, Any]:
    """LLM vs Hybrid vs Metrix ops economics + chart series."""
    if scenario not in MONTHLY_SCENARIOS and scenario != "all":
        scenario = "traction_200"
    eng = CapitalEfficiencyEngine()
    if scenario == "all":
        return eng.all_scenarios()
    return eng.run(scenario_key=scenario)


@router.get("/market-units")
def market_units(industry: str = "") -> dict[str, Any]:
    """Market Units application points + simple offers + package pricing."""
    if industry:
        return {
            "unit": market_unit_for(industry),
            "package_cost_report": package_cost_report(),
        }
    return all_market_units_payload()


@router.get("/package-costs")
def package_costs() -> dict[str, Any]:
    """Client price of consult + tech-write full package and ladder."""
    return package_cost_report()


@router.post("/memo-convert")
def memo_convert_preview(body: AnalyticsBody) -> dict[str, Any]:
    """Memo Convert preview: system → open opp → analog function → tech tasks."""
    orient = OrientationEngine().orient(
        body.business, body.industry, track=body.track
    )
    orientation = orient.to_dict()
    return MemoConvertEngine().convert(
        business_text=body.business,
        industry_id=body.industry,
        orientation=orientation,
        system_features=SystemLogAnalyst().analyze().to_dict(),
        success=body.success_metrics or {},
        ideas=[
            {
                "title": "preview-primary",
                "track": body.track or "product",
                "score": float((orientation.get("scores") or {}).get("overall_orientation", 0.5)),
            }
        ],
    ).to_dict()


@router.get("/principles")
def principles_graph(industry: str = "") -> dict[str, Any]:
    """21 principles graph + meaning counts + reader groups."""
    eng = get_principles_engine()
    return {
        "graph": eng.graph(),
        "meanings_count": eng.meaning_count(),
        "run": eng.run(industry_id=industry),
        "reader": eng.read_groups(industry),
    }


@router.post("/final-layer")
def final_layer_preview(body: AnalyticsBody) -> dict[str, Any]:
    """Principles + assembler + anti-down + NFT + harness + capital (no full pipeline)."""
    core = PaidProductCore().run(
        industry_id=body.industry,
        business=body.business,
        track=body.track,
        request_id="final-preview",
        idea_title="final-layer-preview",
        scores={"clarity": 0.55, "impact": 0.55, "readiness": 0.5},
        info_roi=body.info_roi_hint,
    )
    return FinalProductLayer().run(
        industry_id=body.industry,
        business=body.business,
        idea_title="final-layer-preview",
        request_id="final-preview",
        paid=core,
        scores=core.get("package") and {"clarity": 0.55, "impact": 0.55} or {},
    )


@router.post("/success-tz")
def build_success_tz(body: AnalyticsBody) -> dict[str, Any]:
    pos = SuccessMetricsPositioner()
    tz = pos.build_tz("preview", body.industry, body.success_metrics)
    return tz.to_dict()


@router.post("/oae-preview")
def oae_preview(body: AnalyticsBody) -> dict[str, Any]:
    """Demo-ready preview: orient → success → decision → OAE."""
    orient = OrientationEngine().orient(
        body.business, body.industry, track=body.track
    )
    orientation = orient.to_dict()
    scores = orientation.get("scores") or {}
    axes = (orientation.get("frame") or {}).get("axes") or {}
    m = orient.metrics

    sm = SuccessMetricsPositioner()
    tz = sm.build_tz("preview", body.industry, body.success_metrics)
    card = sm.score(
        tz,
        readiness=float(scores.get("readiness", 0.5)),
        overall=float(scores.get("overall_orientation", 0.5)),
        info_roi=body.info_roi_hint,
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        promo_fit=float(scores.get("promo_fit", 0.5)),
        monetization_axis=float(axes.get("monetization_fit", 0.5)),
    )
    sys_f = SystemLogAnalyst().analyze().to_dict()
    dec = DecisionMakingCore().analyze(
        industry_id=body.industry,
        orientation=orientation,
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        health=m.health_score,
        info_roi=body.info_roi_hint,
        success_composite=card.weighted_composite,
        success_target=tz.composite_target,
        success_influence=card.influence,
        pragma_splits=[],
        system_features=sys_f,
        idea_title="preview",
    )
    oae = OperationalAnalyticsEngine().run(
        business_text=body.business,
        industry_id=body.industry,
        orientation=orientation,
        idea_title="preview-seed",
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        health=m.health_score,
        info_roi=body.info_roi_hint,
        success_card=card.to_dict(),
        system_features=sys_f,
        decision_mode=dec.active_mode,
    )
    # second decision pass with pragma
    dec2 = DecisionMakingCore().analyze(
        industry_id=body.industry,
        orientation=orientation,
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        health=m.health_score,
        info_roi=body.info_roi_hint,
        success_composite=card.weighted_composite,
        success_target=tz.composite_target,
        success_influence=card.influence,
        pragma_splits=(oae.to_dict().get("pragma") or {}).get("triggered") or [],
        system_features=sys_f,
        idea_title="preview",
    )
    return {
        "success_metrics": card.to_dict(),
        "decision_core": dec2.to_dict(),
        "operational_analytics": oae.to_dict(),
        "system_log": sys_f,
    }


@router.post("/paid-core")
def paid_core_preview(body: AnalyticsBody) -> dict[str, Any]:
    """
    Run Paid Product Core (block 18) with orientation + decision + OAE context.
    """
    orient = OrientationEngine().orient(
        body.business, body.industry, track=body.track
    )
    orientation = orient.to_dict()
    scores = orientation.get("scores") or {}
    axes = (orientation.get("frame") or {}).get("axes") or {}
    m = orient.metrics

    sm = SuccessMetricsPositioner()
    tz = sm.build_tz("preview", body.industry, body.success_metrics)
    card = sm.score(
        tz,
        readiness=float(scores.get("readiness", 0.5)),
        overall=float(scores.get("overall_orientation", 0.5)),
        info_roi=body.info_roi_hint,
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        promo_fit=float(scores.get("promo_fit", 0.5)),
        monetization_axis=float(axes.get("monetization_fit", 0.5)),
    )
    sys_f = SystemLogAnalyst().analyze().to_dict()
    dec = DecisionMakingCore().analyze(
        industry_id=body.industry,
        orientation=orientation,
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        health=m.health_score,
        info_roi=body.info_roi_hint,
        success_composite=card.weighted_composite,
        success_target=tz.composite_target,
        success_influence=card.influence,
        pragma_splits=[],
        system_features=sys_f,
        idea_title="paid-preview",
    )
    oae = OperationalAnalyticsEngine().run(
        business_text=body.business,
        industry_id=body.industry,
        orientation=orientation,
        idea_title="paid-preview-seed",
        vvi=m.vvi,
        er=m.er,
        rrc=m.rrc,
        health=m.health_score,
        info_roi=body.info_roi_hint,
        success_card=card.to_dict(),
        system_features=sys_f,
        decision_mode=dec.active_mode,
    )
    paid = PaidProductCore().run(
        industry_id=body.industry,
        business=body.business,
        track=body.track or "all",
        request_id="paid-preview",
        idea_title="paid-preview-seed",
        axes=axes,
        scores=scores,
        info_roi=body.info_roi_hint,
        decision=dec.to_dict(),
        oae=oae.to_dict(),
        product={"demo_idea": {"title": "paid-preview-seed"}},
        fin_models=[],
        success=card.to_dict(),
        force=body.force_paid,
    )
    commercial = CommercialLayer().run(
        industry_id=body.industry,
        business=body.business,
        idea_title="paid-preview-seed",
        request_id="paid-preview",
        paid=paid,
        scores=scores,
        axes=axes,
        decision=dec.to_dict(),
        oae=oae.to_dict(),
        success=card.to_dict(),
        write_portal=True,
    )
    paid = {
        **paid,
        "commercial": commercial,
        "business_metrics": commercial.get("business_metrics"),
        "clarifying_questions": commercial.get("clarifying_questions"),
        "tangible": commercial.get("tangible"),
        "commercial_offer": commercial.get("commercial_offer"),
        "portal": commercial.get("portal"),
        "pilot_tz_draft": commercial.get("pilot_tz_draft"),
    }
    return {
        "block": 18,
        "orientation_mode": orient.operating_mode,
        "decision_mode": dec.active_mode,
        "paid_product_core": paid,
        "portal_url": (commercial.get("portal") or {}).get("url"),
    }
