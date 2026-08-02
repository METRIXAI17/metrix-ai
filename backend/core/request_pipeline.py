"""
Request Pipeline — «бекенд» обработки запросов.

Цепочка v2 (17 июля — Decision + OAE + Success TZ):

  1. Validate
  2. Orient                    (OrientationForge)
  3. Superstructure            (zones → product result)
  4. Profitability             (IROI)
  5. Success Metrics TZ        (custom positioning → scoring influence)
  6. System log features       (global request memory)
  7. Pragma + Decision Core    (mode: scoring / generative / recursive)
  8. Operational Analytics     (constructor form, embedding, ricochet…)
  9. Fin Models
 10. Idea structure
 11. Monetization
 12. Self-improve
 13. Package response

Slots:
  - backend/paid/        → block 18 paid product core (6 components + supporting)
  - backend/generative/  → block 19 generativity concept
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from backend.config import DATA_DIR, INDUSTRIES, resolve_industry_id
from backend.core.decision_core import DecisionMakingCore
from backend.core.category_router import route_categories
from backend.core.industry_sanity import load_sanity
from backend.core.market_units import market_unit_for, package_cost_report
from backend.core.memo_convert import MemoConvertEngine
from backend.core.operational_analytics import OperationalAnalyticsEngine
from backend.core.orientation_engine import OrientationEngine
from backend.core.self_improve import self_improve_loop
from backend.core.success_metrics import SuccessMetricsPositioner
from backend.core.superstructure import SuperstructureOverlay
from backend.core.system_log import SystemLogAnalyst
from backend.fin_models.registry import run_fin_models_for_industry
from backend.generative.stub import GenerativityStub, generative_ready_payload
from backend.modules.folder_synthesizer import IdeaStructureSynthesizer
from backend.modules.profitability_oracle import InformationalProfitabilityOracle
from backend.monetization.orchestrator import MonetizationOrchestrator
from backend.paid.commercial_layer import CommercialLayer
from backend.paid.orchestrator import PaidProductCore
from backend.schemas.requests import ClientRequest, ProcessResponse

logger = logging.getLogger("metrix.pipeline")


class RequestPipeline:
    """Главный обработчик клиентских запросов Metrix AI."""

    def __init__(self) -> None:
        self.orientation = OrientationEngine()
        self.overlay = SuperstructureOverlay()
        self.profit = InformationalProfitabilityOracle()
        self.structure = IdeaStructureSynthesizer()
        self.monetization = MonetizationOrchestrator()
        self.success_metrics = SuccessMetricsPositioner()
        self.decision_core = DecisionMakingCore()
        self.oae = OperationalAnalyticsEngine()
        self.system_log = SystemLogAnalyst()
        self.generativity = GenerativityStub()
        self.paid_core = PaidProductCore()
        self.commercial = CommercialLayer()
        self.memo_convert = MemoConvertEngine()
        self._store = DATA_DIR / "requests"
        self._store.mkdir(parents=True, exist_ok=True)

    def process(self, req: ClientRequest) -> ProcessResponse:
        errors = req.validate()
        if errors:
            return self._fail(req, errors, "invalid")

        raw_industry = req.industry.strip()
        industry_id = resolve_industry_id(raw_industry)
        if industry_id not in INDUSTRIES:
            from backend.config import PUBLIC_INDUSTRY_IDS

            return self._fail(
                req,
                [f"Unknown industry: {raw_industry}"],
                "invalid",
                next_steps=[f"Choose industry from: {', '.join(PUBLIC_INDUSTRY_IDS)}"],
            )

        industry = INDUSTRIES[industry_id]
        track = (req.track or "all").lower()
        track_arg = None if track in ("all", "") else track

        # ── 2. Orient ─────────────────────────────────────────────────────
        logger.info("orient request_id=%s industry=%s", req.request_id, industry_id)
        orient = self.orientation.orient(
            business_text=req.business,
            industry_id=industry_id,
            track=track_arg,
            extra_params=req.extra_params,
        )
        orientation = orient.to_dict()

        # ── 3. Superstructure ─────────────────────────────────────────────
        composed = self.overlay.compose(
            business_text=req.business,
            industry_id=industry_id,
            orientation=orientation,
            info_roi=1.0,
        )
        product = composed.product_result
        idea_title = product.get("title") or "Metrix oriented idea"
        primary = product.get("primary_track") or "product"

        # ── 4. Profitability ──────────────────────────────────────────────
        scores = orientation.get("scores") or {}
        axes = (orientation.get("frame") or {}).get("axes") or {}
        profit_idea = self.profit.evaluate_idea(
            idea_title,
            impact=float(scores.get("overall_orientation", 0.5)),
            scalability=0.55 + float(scores.get("product_fit", 0.4)) * 0.3,
            long_term_value=0.5 + float(axes.get("value_density", 0.4)) * 0.4,
            implementation_cost=max(
                0.15, 0.55 - float(scores.get("readiness", 0.4)) * 0.3
            ),
            risk_factor=float(axes.get("risk", 0.2)),
            novelty_bonus=0.15,
        )
        product = {
            **product,
            "info_roi": profit_idea.info_roi,
            "profit_band": profit_idea.score_band,
        }

        um = composed.unified_metrics
        vvi, er, rrc, health = um.vvi, um.er, um.rrc, um.health_score

        # ── 5. Success Metrics TZ (custom positioning) ────────────────────
        tz = self.success_metrics.build_tz(
            req.request_id,
            industry_id,
            custom=req.success_metrics or None,
        )
        success_card = self.success_metrics.score(
            tz,
            readiness=float(scores.get("readiness", 0.5)),
            overall=float(scores.get("overall_orientation", 0.5)),
            info_roi=profit_idea.info_roi,
            vvi=vvi,
            er=er,
            rrc=rrc,
            promo_fit=float(scores.get("promo_fit", 0.5)),
            monetization_axis=float(axes.get("monetization_fit", 0.5)),
        )
        success_dict = success_card.to_dict()

        # apply scoring multiplier lightly to product meta
        mult = float(success_card.influence.get("scoring_multiplier") or 1.0)
        product = {
            **product,
            "success_composite": success_card.weighted_composite,
            "success_hits_target": success_card.hits_target,
            "scoring_multiplier": mult,
        }

        # ── 6. System log features ────────────────────────────────────────
        sys_feat = self.system_log.analyze()
        sys_dict = sys_feat.to_dict()

        # ── 7. Decision Core (needs pragma splits preview via light call) ──
        # Pragma evaluated inside OAE too; Decision gets splits after OAE
        # First pass decision with empty splits, refined after OAE
        decision_pre = self.decision_core.analyze(
            industry_id=industry_id,
            orientation=orientation,
            vvi=vvi,
            er=er,
            rrc=rrc,
            health=health,
            info_roi=profit_idea.info_roi,
            success_composite=success_card.weighted_composite,
            success_target=tz.composite_target,
            success_influence=success_card.influence,
            pragma_splits=[],
            system_features=sys_dict,
            specs_ready=bool(product.get("specs_ready")),
            idea_title=idea_title,
        )

        # ── 8. Operational Analytics Engine ───────────────────────────────
        portfolio_ideas = list(product.get("demo_ideas") or [])
        oae_result = self.oae.run(
            business_text=req.business,
            industry_id=industry_id,
            orientation=orientation,
            idea_title=idea_title,
            vvi=vvi,
            er=er,
            rrc=rrc,
            health=health,
            info_roi=profit_idea.info_roi,
            success_card=success_dict,
            system_features=sys_dict,
            decision_mode=decision_pre.active_mode,
            missing_params=list(
                (orientation.get("parameter_map") or {}).get("missing") or []
            ),
            portfolio_ideas=portfolio_ideas,
        )
        oae_dict = oae_result.to_dict()

        # refine decision with real pragma splits
        pragma_splits = (oae_dict.get("pragma") or {}).get("triggered") or []
        decision = self.decision_core.analyze(
            industry_id=industry_id,
            orientation=orientation,
            vvi=float(
                (oae_dict.get("metrics_delta") or {}).get("vvi_after", vvi)
            ),
            er=er,
            rrc=float(
                (oae_dict.get("metrics_delta") or {}).get("rrc_after", rrc)
            ),
            health=float(
                (oae_dict.get("metrics_delta") or {}).get("health_after", health)
            ),
            info_roi=profit_idea.info_roi,
            success_composite=success_card.weighted_composite,
            success_target=tz.composite_target,
            success_influence=success_card.influence,
            pragma_splits=pragma_splits,
            system_features=sys_dict,
            specs_ready=bool(product.get("specs_ready")),
            idea_title=idea_title,
        )
        decision_dict = decision.to_dict()

        # Generativity stub if mode needs it (block 19 slot)
        gen_out: dict[str, Any] = {}
        if decision.active_mode in (
            "generative_development",
            "dual_ricochet",
        ) or (oae_dict.get("generative_hook") or {}).get("should_run"):
            gen_out = self.generativity.expand(
                generative_ready_payload(oae_dict, decision_dict)
            )

        # Enrich primary demo idea + full multi-idea portfolio
        demo_idea = dict(
            product.get("demo_idea")
            or {"title": idea_title, "track": primary, "industry": industry_id}
        )
        reduced = oae_dict.get("reduced_to_request") or {}
        if reduced.get("client_facing_bridge"):
            demo_idea["oae_bridge"] = reduced["client_facing_bridge"]
        demo_idea["answer_shift"] = oae_dict.get("answer_shift")
        demo_idea["processing_mode"] = decision.active_mode

        # Full list: OAE-merged portfolio (Product Sol + abstract flyouts)
        demo_ideas: list[dict[str, Any]] = list(oae_dict.get("demo_ideas") or [])
        if not demo_ideas:
            demo_ideas = list(product.get("demo_ideas") or [demo_idea])
        # Ensure primary is rank-1 and enriched
        if demo_ideas:
            demo_ideas[0] = {
                **demo_ideas[0],
                **{k: v for k, v in demo_idea.items() if k not in ("rank", "id")},
                "rank": 1,
                "is_primary": True,
                "title": demo_ideas[0].get("title") or demo_idea.get("title"),
            }
            demo_idea = dict(demo_ideas[0])
            for i, idea in enumerate(demo_ideas, start=1):
                idea["rank"] = i
                idea["is_primary"] = i == 1
        alt = demo_ideas[1:] if len(demo_ideas) > 1 else []
        if alt:
            demo_idea["double_bottom_alternatives"] = alt
        demo_idea["portfolio_count"] = len(demo_ideas)
        demo_idea["portfolio_roles"] = [i.get("role") for i in demo_ideas if i.get("role")]
        product = {
            **product,
            "demo_idea": demo_idea,
            "demo_ideas": demo_ideas,
            "idea_count": len(demo_ideas),
        }

        # ── 9. Fin models ─────────────────────────────────────────────────
        fin_models: list[dict[str, Any]] = []
        if req.enable_fin_models:
            ctx = {
                "industry_id": industry_id,
                "scores": scores,
                "axes": axes,
                "operating_mode": decision.active_mode,
                "business": req.business,
            }
            fin_models = run_fin_models_for_industry(industry_id, ctx, limit=3)
            for fm in fin_models:
                fm["profitability"] = self.profit.evaluate_fin_model(
                    fm.get("model_name") or fm.get("model_id") or "model",
                    impact=float((fm.get("calculations") or {}).get("impact", 0.5)),
                    scalability=float(
                        (fm.get("calculations") or {}).get("scalability", 0.5)
                    ),
                    long_term_value=float(
                        (fm.get("calculations") or {}).get("long_term_value", 0.5)
                    ),
                    implementation_cost=float(
                        (fm.get("calculations") or {}).get("implementation_cost", 0.4)
                    ),
                    risk_factor=float(
                        (fm.get("calculations") or {}).get("risk_factor", 0.2)
                    ),
                ).to_dict()

        # ── 9b. Paid Product Core (block 18) — single 16-step pass ────────
        # After OAE + fin models so hypotheses see full parallel detail.
        paid_out: dict[str, Any] = self.paid_core.run(
            industry_id=industry_id,
            business=req.business,
            track=req.track or primary,
            request_id=req.request_id,
            idea_title=idea_title,
            axes=axes,
            scores=scores,
            info_roi=profit_idea.info_roi,
            decision=decision_dict,
            oae=oae_dict,
            product={**product, "demo_idea": demo_idea},
            fin_models=fin_models,
            success=success_dict,
            force=bool(decision.handoff_flags.get("ready_for_paid_block_18")),
        )
        commercial_out: dict[str, Any] = {}

        # ── 10. Idea structure workspace (all portfolio ideas) ────────────
        ideas_for_ws: list[dict[str, Any]] = []
        for idea in demo_ideas:
            rid = idea.get("id") or f"demo_idea_{idea.get('rank', 1)}"
            ideas_for_ws.append(
                {
                    "id": str(rid),
                    "title": idea.get("title") or idea_title,
                    "kind": "idea",
                    "score": float(idea.get("score") or scores.get("overall_orientation", 0.5))
                    * mult,
                    "tags": [
                        idea.get("track") or primary,
                        industry_id,
                        decision.active_mode,
                        idea.get("role") or "idea",
                        f"stage_{idea.get('ops_stage', 1)}",
                    ],
                }
            )
        if not ideas_for_ws:
            ideas_for_ws.append(
                {
                    "id": "demo_idea",
                    "title": idea_title,
                    "kind": "idea",
                    "score": float(scores.get("overall_orientation", 0.5)) * mult,
                    "tags": [primary, industry_id, decision.active_mode],
                }
            )
        ideas_for_ws.extend(
            [
                {
                    "id": "orientation",
                    "title": f"Orientation {orient.frame.seed}",
                    "kind": "orientation",
                    "score": float(scores.get("readiness", 0.5)),
                    "tags": ["orientation"],
                },
                {
                    "id": "specs",
                    "title": "SpecsForge tree",
                    "kind": "spec",
                    "score": 0.7 if product.get("specs_ready") else 0.4,
                    "tags": ["spec"],
                },
                {
                    "id": "oae_embed",
                    "title": "OAE embedding spine",
                    "kind": "note",
                    "score": float(success_card.weighted_composite),
                    "tags": ["oae", "embedding"],
                },
            ]
        )
        for fm in fin_models:
            ideas_for_ws.append(
                {
                    "id": f"fm_{fm.get('model_id')}",
                    "title": fm.get("model_name") or fm.get("model_id"),
                    "kind": "fin_model",
                    "score": min(1.0, float(fm.get("info_roi", 1.0)) / 4.0),
                    "tags": ["fin_model", fm.get("model_id", "")],
                }
            )
        ideas_for_ws.append(
            {
                "id": "promo_spine",
                "title": "Promo spine",
                "kind": "promo",
                "score": float(scores.get("promo_fit", 0.5)),
                "tags": ["promo"],
            }
        )
        structure = self.structure.manage(
            workspace_id=req.request_id,
            ideas=ideas_for_ws,
            industry_id=industry_id,
            auto_apply=True,
        )

        # ── 11. Monetization ──────────────────────────────────────────────
        mono: dict[str, Any] = {}
        if req.enable_monetization:
            ling = (composed.zone_outputs.get("cloud_sol") or {}).get("linguistic") or {}
            mono = self.monetization.run(
                idea_title=idea_title,
                industry_id=industry_id,
                industry_name=industry["name"],
                scores=scores,
                axes=axes,
                info_roi=profit_idea.info_roi,
                health=float(
                    (oae_dict.get("metrics_delta") or {}).get("health_after", health)
                ),
                track=primary,
                phrases=list(ling.get("optimized_phrases") or []),
            )

        # ── 11b. Memo Convert (before commercial so package docs use it) ─
        success_for_commercial = {
            **success_dict,
            "business_numbers": dict(
                (req.success_metrics or {}).get("business_numbers") or {}
            ),
            "modeling_answers": dict(
                (req.success_metrics or {}).get("modeling_answers") or {}
            ),
        }
        memo_out = self.memo_convert.convert(
            business_text=req.business,
            industry_id=industry_id,
            orientation=orientation,
            oae=oae_dict,
            decision=decision_dict,
            product=product,
            paid=paid_out,
            system_features=sys_dict,
            success=success_for_commercial,
            ideas=demo_ideas,
        ).to_dict()
        market_unit = market_unit_for(industry_id)
        package_costs = package_cost_report()
        tech_tasks = memo_out.get("technical_tasks") or []
        if tech_tasks:
            product = {
                **product,
                "memo_tech_task": tech_tasks[0],
                "selected_function": (memo_out.get("analog_engine") or {}).get(
                    "selected_function"
                ),
            }
            if demo_ideas:
                demo_ideas[0] = {
                    **demo_ideas[0],
                    "memo_function": (memo_out.get("analog_engine") or {}).get(
                        "selected_function"
                    ),
                    "open_opportunity": (memo_out.get("open_opportunities") or [{}])[0],
                    "market_unit_product": (market_unit.get("product") or {}).get(
                        "name"
                    ),
                }
                demo_idea = dict(demo_ideas[0])
                product = {**product, "demo_idea": demo_idea, "demo_ideas": demo_ideas}

        # ── 11c. Commercial layer (metrics · questions · offer · portal · package docs)
        commercial_out = self.commercial.run(
            industry_id=industry_id,
            business=req.business,
            idea_title=idea_title,
            request_id=req.request_id,
            paid=paid_out,
            scores=scores,
            axes=axes,
            decision=decision_dict,
            oae=oae_dict,
            success=success_for_commercial,
            extra_params=dict(req.extra_params or {}),
            monetization=mono,
            fin_models=fin_models,
            modeling_answers=success_for_commercial.get("modeling_answers"),
            write_portal=True,
            memo_convert=memo_out,
            market_unit=market_unit,
            client_name=req.name or "",
            demo_idea=demo_idea,
            demo_ideas=demo_ideas,
        )
        paid_out = {
            **paid_out,
            "commercial": commercial_out,
            "business_metrics": commercial_out.get("business_metrics")
            or paid_out.get("business_metrics"),
            "situation_metrics": commercial_out.get("situation_metrics")
            or paid_out.get("situation_metrics"),
            "clarifying_questions": commercial_out.get("clarifying_questions"),
            "must_ask": commercial_out.get("must_ask")
            or commercial_out.get("clarifying_questions"),
            "tangible": commercial_out.get("tangible"),
            "commercial_offer": commercial_out.get("commercial_offer"),
            "pilot_tz_draft": commercial_out.get("pilot_tz_draft"),
            "portal": commercial_out.get("portal"),
            "integration_specs": commercial_out.get("integration_specs"),
            "product_building_library": commercial_out.get(
                "product_building_library"
            ),
            "final_layer": commercial_out.get("final_layer"),
            "principles_engine": commercial_out.get("principles_engine"),
            "sequence_assembler": commercial_out.get("sequence_assembler"),
            "anti_down_sorter": commercial_out.get("anti_down_sorter"),
            "objectly": commercial_out.get("objectly"),
            "opening_edge": commercial_out.get("opening_edge"),
            "nft_create_building": commercial_out.get("nft_create_building"),
            "harness_showcase": commercial_out.get("harness_showcase"),
            "capital_efficiency": commercial_out.get("capital_efficiency"),
            "ui_status": commercial_out.get("ui_status"),
            "package_deliverable": commercial_out.get("package_deliverable"),
            "client_pack": commercial_out.get("client_pack"),
        }
        if isinstance(oae_dict.get("paid_hook"), dict):
            oae_dict = {
                **oae_dict,
                "paid_hook": {
                    **oae_dict["paid_hook"],
                    "status": paid_out.get("status", "active"),
                    "paid_score": paid_out.get("paid_score"),
                    "module": paid_out.get("module"),
                    "flow_steps": (paid_out.get("flow") or {}).get("step_count"),
                    "portal_url": (commercial_out.get("portal") or {}).get("url"),
                    "summary": paid_out.get("summary"),
                },
            }

        # ── 12. Self-improve ──────────────────────────────────────────────
        improve: dict[str, Any] = {}
        metrics_bundle = {
            "orientation": orient.metrics.to_dict(),
            "unified": um.to_dict(),
            "idea_profitability": profit_idea.to_dict(),
            "success_metrics": success_dict,
            "oae_metrics_delta": oae_dict.get("metrics_delta"),
            "business_situation": (commercial_out.get("business_metrics") or {}).get(
                "situation_score"
            ),
        }
        if req.enable_self_improve:
            improve = self_improve_loop(um, product)
            product = {**product, **(improve.get("product_result_patch") or {})}
            metrics_bundle["after_self_improve"] = improve.get("metrics_after")

        # ── 13. Breakdown + next steps ────────────────────────────────────
        breakdown = {
            "method": "dynamic_orientation+oae+decision_core",
            "steps": [
                "Place / mine / calculate (OrientationForge)",
                "Superstructure unifies zones",
                "Custom success metrics TZ → scoring influence",
                "System log features",
                "Decision Core mode switch",
                "OAE: constructor form → embedding → deep → shift → ricochet",
                "Pragma splitting for demo-fast generative path",
                "Paid Product Core: design library → chips → functions → energy → calm → mega map",
                "Commercial: situation metrics · questions · offer · portal",
                "Memo Convert: system intake → coop open-opp → analog function → reverse categories → tech tasks",
                "Market Units: application point + simple offers",
                "Fin Models + Monetization + self-improve",
            ],
            "orientation_narrative": orient.narrative,
            "superstructure_summary": composed.summary,
            "specs_summary": (composed.zone_outputs.get("infa_sol") or {}).get(
                "summary"
            ),
            "cloud_summary": (composed.zone_outputs.get("cloud_sol") or {}).get(
                "summary"
            ),
            "structure_summary": (composed.zone_outputs.get("structure_fi") or {}).get(
                "summary"
            ),
            "passages": [p.to_dict() for p in composed.passages],
            "profitability": profit_idea.to_dict(),
            "success_metrics": success_dict,
            "decision_core": decision_dict,
            "operational_analytics": oae_dict,
            "system_log_features": sys_dict,
            "generativity": gen_out,
            "paid_product_core": {
                "status": paid_out.get("status"),
                "paid_score": paid_out.get("paid_score"),
                "summary": paid_out.get("summary"),
                "package": paid_out.get("package"),
                "components": paid_out.get("components"),
                "flow_stages": list(
                    ((paid_out.get("flow") or {}).get("stages") or {}).keys()
                ),
                "flow_step_count": (paid_out.get("flow") or {}).get("step_count"),
                "reader_plain": (paid_out.get("reader") or {}).get("plain_summary"),
                "mega_map_comparison": (paid_out.get("mega_map") or {}).get(
                    "comparison"
                ),
                "top_lever": (paid_out.get("function_engine") or {}).get("top_lever"),
                "entanglement": (paid_out.get("energy_flow") or {}).get(
                    "total_entanglement"
                ),
                "founder_error": (paid_out.get("critical_thinking") or {}).get(
                    "founder_error"
                ),
                "metric_tests_overall": (paid_out.get("metric_tests") or {}).get(
                    "overall_score"
                ),
                "meaning_vectors": paid_out.get("meaning_vectors"),
                "situation_score": (
                    (paid_out.get("business_metrics") or {}).get("situation_score")
                ),
                "portal_url": (paid_out.get("portal") or {}).get("url"),
                "primary_tariff": (
                    (paid_out.get("commercial_offer") or {}).get("tariff") or {}
                ).get("id"),
                "must_ask_count": (
                    (paid_out.get("clarifying_questions") or {}).get("must_count")
                ),
            },
            "memo_convert": {
                "summary": memo_out.get("summary"),
                "selected_function": (memo_out.get("analog_engine") or {}).get(
                    "selected_function"
                ),
                "open_opp_count": len(memo_out.get("open_opportunities") or []),
                "tech_task_count": len(memo_out.get("technical_tasks") or []),
                "dominant_category": (memo_out.get("categorical_data") or {}).get(
                    "dominant_category"
                ),
                "same_arch_engine": (memo_out.get("engine_on_same_arch") or {}).get(
                    "feasible"
                ),
            },
            "market_unit": {
                "application_point": market_unit.get("application_point"),
                "product": market_unit.get("product"),
                "promotion": market_unit.get("promotion"),
                "offers": market_unit.get("offers"),
            },
            "package_costs": package_costs.get("primary_package"),
        }

        next_steps = [
            "Review free demo idea portfolio + OAE bridge with the client",
            "Walk Full Package tour: Product → Teammate → Angle",
        ]
        mu_product = (market_unit.get("product") or {}).get("name")
        if mu_product:
            next_steps.append(
                f"Market Unit product for this industry: {mu_product} "
                f"({market_unit.get('application_point')})"
            )
        if tech_tasks:
            next_steps.append(
                "Memo Convert tech task ready → SpecsForge / consult+tech-write pack ($1290)"
            )
        pkg_url = (commercial_out.get("package_deliverable") or {}).get("url")
        if pkg_url:
            next_steps.insert(
                0,
                f"Open your result pack: {pkg_url} (folder 12_package_result)",
            )
        if profit_idea.recommended:
            next_steps.append(
                "Propose paid implement — informational ROI is attractive"
            )
        if decision.handoff_flags.get("ready_for_paid_block_18"):
            next_steps.append(
                "Block 18 active: review Paid Product Core package + Mega Map best hypothesis"
            )
        elif paid_out.get("status") in (
            "preview",
            "candidate_preview",
            "preview_founder_review",
        ):
            next_steps.append(
                "Paid core preview available — raise IROI/success TZ for full packageable status"
            )
        fe = (paid_out.get("critical_thinking") or {}).get("founder_error") or {}
        if fe.get("suspected"):
            next_steps.append(
                f"Founder review: {fe.get('recommended_correction') or fe.get('error_class')}"
            )
        cq = paid_out.get("clarifying_questions") or {}
        if cq.get("re_run_recommended"):
            next_steps.insert(
                0,
                f"Ответьте на {cq.get('must_count', 0)} must-ask вопросов → re-run "
                f"(см. meta.paid_product_core.clarifying_questions)",
            )
        portal_url = (paid_out.get("portal") or {}).get("url")
        if portal_url:
            next_steps.append(f"Paid portal / offer: {portal_url}")
        nat = (paid_out.get("commercial") or {}).get("natural_next")
        if nat and nat not in next_steps:
            next_steps.append(nat)
        for action in (paid_out.get("package") or {}).get("recommended_actions") or []:
            if action not in next_steps:
                next_steps.append(action)
        if decision.handoff_flags.get("needs_generative_19"):
            next_steps.append(
                "Block 19 path: generative expansion of abstract coordinates"
            )
        if mono.get("auto_orders", {}).get("enabled"):
            next_steps.append("Auto Orders ready — human approval gate then queue")
        else:
            next_steps.append(
                "Nurture with Promo sequence; re-orient when more detail arrives"
            )
        for d in decision.improving_decisions[:2]:
            next_steps.append(f"Decision: {d.title}")

        zones_touched = [
            "orientation",
            "infa_sol",
            "product_sol",
            "cloud_sol",
            "structure_fi",
            "superstructure",
            "success_metrics",
            "decision_core",
            "operational_analytics",
        ]
        if fin_models:
            zones_touched.append("fin_models")
        if mono:
            zones_touched.append("monetization")
        if gen_out:
            zones_touched.append("generative_stub")
        if paid_out:
            zones_touched.extend(
                [
                    "paid_product_core",
                    "virtual_chips",
                    "calm_point",
                    "mega_map",
                ]
            )
        zones_touched.extend(["memo_convert", "market_units"])

        # ── Circle-System / Deep Tech Metrix (3 global steps) ─────────────
        circle_out: dict[str, Any] = {}
        niche_answer: dict[str, Any] = {}
        free_work_cta: dict[str, Any] = {}
        _lang_explicit = (getattr(req, "lang", None) or "").strip().lower()
        if _lang_explicit in ("en", "ru"):
            _lang = _lang_explicit
        else:
            _lang = "ru" if any(ord(c) > 127 for c in (req.business or "")[:80]) else "en"
        try:
            from backend.core.circle_system import run_deep_tech_pipeline
            from backend.core.circle_system.niche_answer_base import NicheAnswerBase

            circle_out = run_deep_tech_pipeline(
                req.business,
                industry_id=industry_id,
                lang=_lang,
                core_metrics={"vvi": vvi, "er": er, "rrc": rrc},
                product_name="Metrix Circle Runtime",
                client_label=req.name or "client",
            )
            zones_touched.extend(["circle_system", "deep_tech_metrix", "support_system"])
            cat_for_niche = route_categories(
                business=req.business,
                industry_id=industry_id,
                nums={},
                sanity_hints={},
                preferred_track=track,
            )
            natural_dir = cat_for_niche.get("primary") or track or "ops"
            niche_answer = NicheAnswerBase().resolve(
                industry_id,
                track=track if track in ("ops", "product", "promotion") else natural_dir,
                natural_direction=natural_dir if natural_dir in ("ops", "product", "promotion") else "ops",
                lang=_lang,
                business=req.business,
                numbers=(req.success_metrics or {}).get("business_numbers") or {},
            )
            free_work_cta = {
                "label_ru": "Начать работу бесплатно",
                "label_en": "Start free work",
                "label": "Начать работу бесплатно" if _lang == "ru" else "Start free work",
                "endpoint": "/api/v1/analytics/free-work/start",
                "phases_hint": "D0–1 start · D1–4 tests · D3–10 tech write",
            }
        except Exception as exc:  # noqa: BLE001 — never break main path
            logger.warning("circle_system failed: %s", exc)
            circle_out = {"ok": False, "error": str(exc)}

        # operating mode = decision active mode (richer than orientation alone)
        operating_mode = f"{orient.operating_mode}|{decision.active_mode}"
        if paid_out.get("status") in ("ready", "packageable"):
            operating_mode = f"{operating_mode}|paid_core"
        if circle_out.get("product_surfaces"):
            operating_mode = f"{operating_mode}|circle_system"

        # Portfolio-aware next step
        if len(demo_ideas) > 1:
            next_steps.insert(
                0,
                f"Review idea portfolio ({len(demo_ideas)} ideas) — pick primary + 1–2 complements for ops success",
            )

        response = ProcessResponse(
            ok=True,
            request_id=req.request_id,
            industry=industry_id,
            operating_mode=operating_mode,
            orientation=orientation,
            demo_idea=demo_idea,
            demo_ideas=demo_ideas,
            breakdown=breakdown,
            metrics=metrics_bundle,
            zones_touched=zones_touched,
            fin_models=fin_models,
            monetization=mono,
            structure=structure.to_dict(),
            self_improve=improve,
            decision_core=decision_dict,
            operational_analytics=oae_dict,
            success_metrics=success_dict,
            next_steps=next_steps,
            errors=[],
            meta={
                "brand": "Metrix AI",
                "codename": "KARIM METRIX",
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "client_name": req.name,
                "contact": req.contact,
                "program_id": req.program_id,
                "product_result": product,
                "industry_name": industry["name"],
                "pipeline_version": "2.4-circle-system",
                "idea_count": len(demo_ideas),
                "idea_portfolio": (product.get("portfolio") or {}),
                "block_18_slot": "backend/paid",
                "block_18_status": paid_out.get("status"),
                "block_18_score": paid_out.get("paid_score"),
                "block_19_slot": "backend/generative",
                "paid_product_core": paid_out,
                "memo_convert": memo_out,
                "market_unit": market_unit,
                "package_costs": package_costs,
                "circle_system": circle_out,
                "deep_tech_product_surfaces": (circle_out or {}).get("product_surfaces") or {},
                "circle_assertions": (circle_out or {}).get("assertions") or [],
                "niche_answer": niche_answer,
                "free_work_cta": free_work_cta,
                "category_router": route_categories(
                    business=req.business,
                    industry_id=industry_id,
                    nums={
                        k: float(v)
                        for k, v in (
                            (req.success_metrics or {}).get("business_numbers") or {}
                        ).items()
                        if isinstance(v, (int, float))
                    },
                    sanity_hints={
                        "track_priors": (load_sanity(industry_id).get("track_priors") or {})
                    },
                    preferred_track=track,
                ),
                "free_consult": True,
                "public_pricing": {
                    "free_usd": 0,
                    "pilot_ops_usd": 690,
                    "pilot_product_usd": 790,
                    "pilot_promotion_usd": 490,
                    "main_after_pilot_usd": 2490,
                    "rule": "main package only after pilot success",
                },
            },
        )

        # Client-facing free consult card (clean URLs + short copy)
        from backend.config import public_api_url

        cat = response.meta.get("category_router") or {}
        pd = (commercial_out or {}).get("package_deliverable") or {}
        pack_url = pd.get("url") or public_api_url(
            f"/api/v1/packages/{req.request_id}/result"
        )
        consult_url = pd.get("consult_url") or public_api_url(
            f"/api/v1/packages/{req.request_id}/consult"
        )
        narrative_memo = (
            ((commercial_out or {}).get("narrative_engine") or {}).get("memo") or {}
        )
        blurb = (
            narrative_memo.get("executive_summary")
            or (demo_idea or {}).get("summary")
            or (req.business or "")[:220]
        )
        if isinstance(blurb, str) and len(blurb) > 280:
            blurb = blurb[:277].rsplit(" ", 1)[0] + "…"
        headline = (
            (demo_idea or {}).get("label")
            or (demo_idea or {}).get("title")
            or "Free orientation ready"
        )
        if isinstance(headline, str) and len(headline) > 100:
            headline = headline[:97].rsplit(" ", 1)[0] + "…"
        response.meta["free_consult_card"] = {
            "headline": headline,
            "blurb": blurb,
            "direction": cat.get("primary") or "ops",
            "direction_label": cat.get("primary_label")
            or str(cat.get("primary") or "ops"),
            "natural_direction": cat.get("natural_primary"),
            "natural_label": cat.get("natural_label"),
            "user_track": track,
            "pack_url": pack_url,
            "consult_url": consult_url,
            "reason": next(
                (
                    t.get("reason")
                    for t in (cat.get("tracks") or [])
                    if t.get("id") == cat.get("primary")
                ),
                "",
            ),
        }
        # Rewrite next_steps that still point at dead /app/*.html paths
        fixed_steps: list[str] = []
        for step in response.next_steps:
            s = str(step)
            if "/app/client-package-latest.html" in s or "result pack" in s.lower():
                fixed_steps.append(f"Open your result pack: {pack_url}")
            elif "/app/paid-portal.html" in s:
                fixed_steps.append(f"Paid portal (preview): {public_api_url(f'/api/v1/packages/{req.request_id}/result')}")
            else:
                fixed_steps.append(s)
        response.next_steps = fixed_steps

        self._persist(req, response)
        return response

    def _fail(
        self,
        req: ClientRequest,
        errors: list[str],
        mode: str,
        next_steps: list[str] | None = None,
    ) -> ProcessResponse:
        return ProcessResponse(
            ok=False,
            request_id=req.request_id,
            industry=req.industry,
            operating_mode=mode,
            orientation={},
            demo_idea={},
            demo_ideas=[],
            breakdown={},
            metrics={},
            zones_touched=[],
            fin_models=[],
            monetization={},
            structure={},
            self_improve={},
            decision_core={},
            operational_analytics={},
            success_metrics={},
            next_steps=next_steps or ["Fix validation errors and resubmit"],
            errors=errors,
        )

    def _persist(self, req: ClientRequest, resp: ProcessResponse) -> None:
        path = self._store / f"{req.request_id}.json"
        payload = {"request": req.to_dict(), "response": resp.to_dict()}
        try:
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("persist failed: %s", exc)


_pipeline: RequestPipeline | None = None


def get_pipeline() -> RequestPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RequestPipeline()
    return _pipeline


def process_client_request(data: dict[str, Any]) -> dict[str, Any]:
    req = ClientRequest.from_dict(data)
    return get_pipeline().process(req).to_dict()
