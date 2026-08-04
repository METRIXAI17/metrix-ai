"""Decision Core + Operational Analytics + Success Metrics + Paid Core endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.decision_core import DecisionMakingCore
from backend.core.market_units import (
    all_market_units_payload,
    market_unit_for,
    package_cost_report,
    run_enriched_market_unit,
)
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
from backend.core.circle_system import (
    DeepTechMetrixPipeline,
    circle_system_overview,
    lexicon_catalog,
    run_deep_tech_pipeline,
)
from backend.core.circle_system.support_system import SupportSystem
from backend.core.circle_system.knowledge_libs import ExpertKnowledgePlatform
from backend.core.circle_system.niche_answer_base import NicheAnswerBase
from backend.core.circle_system.free_work_flow import FreeWorkFlow
from backend.core.knowledge_synthesis import KnowledgeSynthesisEngine, run_knowledge_synthesis
from backend.core.business_gen import BusinessGenerator, BUSINESS_SERVICES, service_demo
from backend.core.business_gen.services_catalog import list_services
from backend.core.workers import PayoutTrustLayer
from backend.monetization.distribution import DistributionEngine

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsBody(BaseModel):
    industry: str
    business: str = Field(..., min_length=20)
    track: str | None = None
    success_metrics: dict = Field(default_factory=dict)
    info_roi_hint: float = 2.0
    force_paid: bool = True


class CircleBody(BaseModel):
    business: str = Field(..., min_length=20)
    industry: str = "ai-agencies"
    lang: str = "ru"
    test_answers: dict = Field(default_factory=dict)
    product_name: str = "Metrix Circle Runtime"
    client_label: str = "client"
    days_elapsed: int = 0
    pilot_horizon_days: int = 21


class FreeWorkStartBody(BaseModel):
    business: str = Field(..., min_length=20)
    industry: str = "ai-agencies"
    track: str = "all"
    name: str = ""
    contact: str = ""
    lang: str = "ru"
    natural_direction: str | None = None
    numbers: dict = Field(default_factory=dict)
    request_id: str | None = None
    include_founders_lane: bool = False


class FreeWorkClarifyBody(BaseModel):
    work_id: str
    answers: dict = Field(default_factory=dict)
    lang: str | None = None


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


@router.post("/market-units/run")
def market_units_run(body: AnalyticsBody) -> dict[str, Any]:
    """
    Market Units v2 live run:
    system reader → problem recognition → metric composer →
    coordination → ontology algorithms → teammate network → offer routing.
    """
    orient = OrientationEngine().orient(
        body.business, body.industry, track=body.track
    )
    orientation = orient.to_dict()
    scores = dict(orientation.get("scores") or {})
    um = orientation.get("metrics") or {}
    return run_enriched_market_unit(
        body.industry,
        business_text=body.business,
        orientation=orientation,
        scores=scores,
        vvi=float(um.get("vvi") or 0.4),
        er=float(um.get("er") or 0.5),
        rrc=float(um.get("rrc") or 0.5),
        health=float(um.get("health_score") or um.get("health") or 0.5),
        success_composite=float(scores.get("overall_orientation") or 0.5),
        decision_mode="scoring",
    )


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


@router.get("/circle-system")
def circle_system_info() -> dict[str, Any]:
    """Circle-System overview + lexicon catalog (read/write words)."""
    return {
        **circle_system_overview(),
        "lexicon": lexicon_catalog(),
        "endpoints": {
            "POST /analytics/deep-tech": "Full 3 global steps + product surfaces",
            "GET /analytics/circle-system": "Overview + modules",
            "GET /analytics/support-system": "How support works + refs",
            "GET /analytics/knowledge": "Expert knowledge libraries",
        },
    }


@router.post("/deep-tech")
def deep_tech_run(body: CircleBody) -> dict[str, Any]:
    """
    Deep Tech Metrix — 3 global steps:
      A params + indirect certainty
      B super-speed tests + assembly + super program + warmth answers
      C circle autopilot stack (pilot, support, white-label prompts)
    """
    return run_deep_tech_pipeline(
        body.business,
        industry_id=body.industry,
        lang=body.lang,
        test_answers=body.test_answers or None,
        product_name=body.product_name,
        client_label=body.client_label,
        days_elapsed=body.days_elapsed,
        pilot_horizon_days=body.pilot_horizon_days,
    )


@router.get("/support-system")
def support_system_doc() -> dict[str, Any]:
    """Support system behaviour + references (standalone empty tick)."""
    # Demo feed with mild anomaly so structure is visible
    demo_fw = {
        "anomalies": [
            {
                "metric": "ASM",
                "level": "warn",
                "msg": "Assembly below pilot gate (demo)",
            }
        ],
        "support_feed": {"values": {"ASM": 0.3, "SFI": 0.4}},
        "values": {"ASM": 0.3},
    }
    return SupportSystem().run(demo_fw)


@router.get("/knowledge")
def knowledge_libs(q: str = "pilot metrics assembly") -> dict[str, Any]:
    """Life-app expert knowledge libraries search."""
    return ExpertKnowledgePlatform().search(q)


@router.get("/lexicon")
def circle_lexicon() -> dict[str, Any]:
    """Words the program uses for read-in and answer-out."""
    return lexicon_catalog()


@router.get("/niche-answers")
def niche_answers(industry: str = "", track: str = "ops", lang: str = "ru") -> dict[str, Any]:
    """Answer base for niches × directions."""
    base = NicheAnswerBase()
    if not industry:
        return {
            "catalog": base.catalog(),
            "phases": base.free_work_phases(lang),
        }
    return {
        "resolved": base.resolve(industry, track=track, lang=lang),
        "phases": base.free_work_phases(lang),
    }


@router.post("/free-work/start")
def free_work_start(body: FreeWorkStartBody) -> dict[str, Any]:
    """After consult: start free work — phases, clarifications, quality niche answer."""
    return FreeWorkFlow().start(
        business=body.business,
        industry_id=body.industry,
        track=body.track,
        name=body.name,
        contact=body.contact,
        lang=body.lang,
        natural_direction=body.natural_direction,
        numbers=body.numbers or None,
        request_id=body.request_id,
        include_founders_lane=body.include_founders_lane,
    )


@router.post("/free-work/clarify")
def free_work_clarify(body: FreeWorkClarifyBody) -> dict[str, Any]:
    """Submit clarifications → system re-resolves quality answer + assembly."""
    return FreeWorkFlow().submit_clarifications(
        body.work_id,
        body.answers or {},
        lang=body.lang,
    )


@router.post("/free-work/advance")
def free_work_advance(work_id: str) -> dict[str, Any]:
    """Advance free-work phase (D0-1 → D1-4 → D3-10)."""
    return FreeWorkFlow().advance_phase(work_id)


@router.get("/free-work/{work_id}")
def free_work_get(work_id: str) -> dict[str, Any]:
    return FreeWorkFlow().get(work_id)


# ── Knowledge synthesis · business gen · workers · distribution (2026-08-02) ──


class KnowledgeSynthBody(BaseModel):
    business: str = Field(..., min_length=20)
    industry: str = "ai-agencies"
    lang: str = "ru"
    answers: dict = Field(default_factory=dict)
    choices: dict = Field(default_factory=dict)
    numbers: dict = Field(default_factory=dict)
    project_name: str = ""


class BusinessGenBody(BaseModel):
    business: str = Field(..., min_length=20)
    industry: str = "automation-builders"
    lang: str = "ru"
    answers: dict = Field(default_factory=dict)
    choices: dict = Field(default_factory=dict)
    numbers: dict = Field(default_factory=dict)
    project_name: str = ""
    channel: str = "auto"  # auto | online | offline | hybrid
    multi_pass: bool = True
    passes: int = 7


class WorkerTaskBody(BaseModel):
    title: str = Field(..., min_length=3)
    niche: str = "general"
    worker_id: str = "open"
    client_ref: str = ""
    purse_units: float = 100.0
    platform_cut: float | None = None


class WorkerProofBody(BaseModel):
    task_id: str
    milestone_id: str
    proof: dict = Field(default_factory=dict)


class WorkerReleaseBody(BaseModel):
    task_id: str
    milestone_id: str


class DistributionBody(BaseModel):
    industry: str = "ai-agencies"
    industry_name: str = ""
    idea_title: str = "Metrix pilot"
    domain: str = ""
    promo_fit: float = 0.55
    lang: str = "ru"


@router.post("/knowledge-synthesis")
def knowledge_synthesis_run(body: KnowledgeSynthBody) -> dict[str, Any]:
    """Multi-layer knowledge synthesis: side engines · planner · methods · expert base."""
    return run_knowledge_synthesis(
        body.business,
        industry_id=body.industry,
        lang=body.lang,
        answers=body.answers or None,
        choices=body.choices or None,
        numbers={k: float(v) for k, v in (body.numbers or {}).items() if _is_number(v)},
        project_name=body.project_name,
    )


@router.post("/business-generate")
def business_generate_run(body: BusinessGenBody) -> dict[str, Any]:
    """
    Generate business system: autonomous pack + expert base + control panel.
    Asks TZ-style choices; self-tests; forecasts human reaction; pre-corrects.
    """
    return BusinessGenerator().generate(
        body.business,
        industry_id=body.industry,
        lang=body.lang,
        answers=body.answers or None,
        choices=body.choices or None,
        numbers={k: float(v) for k, v in (body.numbers or {}).items() if _is_number(v)},
        project_name=body.project_name,
        channel=body.channel or "auto",
        multi_pass=bool(body.multi_pass),
        passes=max(3, min(int(body.passes or 7), 12)),
    )


@router.get("/business-services")
def business_services(lang: str = "ru") -> dict[str, Any]:
    """10 Business Tasks services + short wow demos (no hard prices)."""
    return {
        "surface": "Global Ru Workers · Business Tasks",
        "pricing_language": "fair / adequate / non-hype — no inflated info-marketer prices",
        "services": list_services(lang),
        "count": len(BUSINESS_SERVICES),
    }


@router.get("/business-services/{service_id}/demo")
def business_service_demo(service_id: str, lang: str = "ru") -> dict[str, Any]:
    return service_demo(service_id, lang=lang)


@router.post("/distribution")
def distribution_plan(body: DistributionBody) -> dict[str, Any]:
    """3D distribution: brand · platforms · networking."""
    from backend.config import INDUSTRIES

    ind = INDUSTRIES.get(body.industry) or {}
    name = body.industry_name or ind.get("name") or body.industry
    plan = DistributionEngine().build(
        industry_id=body.industry,
        industry_name=name,
        idea_title=body.idea_title,
        domain=body.domain,
        promo_fit=body.promo_fit,
        lang=body.lang,
    )
    return {"module": "DistributionEngine", "plan": plan.to_dict()}


@router.post("/workers/tasks")
def workers_create_task(body: WorkerTaskBody) -> dict[str, Any]:
    """Create escrow-style worker task (safe payout trust)."""
    return PayoutTrustLayer().create_task(
        title=body.title,
        niche=body.niche,
        worker_id=body.worker_id,
        client_ref=body.client_ref,
        purse_units=body.purse_units,
        platform_cut=body.platform_cut,
    )


@router.post("/workers/proof")
def workers_submit_proof(body: WorkerProofBody) -> dict[str, Any]:
    return PayoutTrustLayer().submit_proof(body.task_id, body.milestone_id, body.proof or {})


@router.post("/workers/release")
def workers_release(body: WorkerReleaseBody) -> dict[str, Any]:
    return PayoutTrustLayer().release_milestone(body.task_id, body.milestone_id)


@router.get("/workers/dashboard")
def workers_dashboard(worker_id: str = "open") -> dict[str, Any]:
    return PayoutTrustLayer().worker_dashboard(worker_id)


@router.get("/workers/rationale")
def workers_payout_rationale() -> dict[str, Any]:
    return PayoutTrustLayer().rationale()


def _is_number(v: Any) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False
