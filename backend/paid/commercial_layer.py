"""
Commercial layer on top of Paid Product Core.

Wires: business metrics · clarifying questions · integration specs ·
tangible extract · paid portal.

Called once after the 16-step paid core (no extra heavy cycles).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.config import PROJECT_ROOT
from backend.paid.business_metrics import BusinessMetricsAnalyzer
from backend.paid.clarifying_questions import ClarifyingQuestionEngine
from backend.paid.final_layer import FinalProductLayer
from backend.paid.integration_specs import IntegrationSpecLibrary
from backend.paid.must_ask import MustAskLoop
from backend.paid.narrative.client_pack import ClientPackWriter
from backend.paid.narrative.package_deliverable import PackageDeliverableWriter
from backend.paid.portal import build_portal_payload, write_portal_files
from backend.paid.situation_metrics import SituationMetricsEngine
from backend.paid.system_design_library import get_system_design_library
from backend.paid.tangible import TangibleExtractor


class CommercialLayer:
    name = "Paid Commercial Layer"

    def __init__(self) -> None:
        self.metrics = BusinessMetricsAnalyzer()
        self.situation = SituationMetricsEngine()
        self.questions = ClarifyingQuestionEngine()
        self.must_ask = MustAskLoop()
        self.specs = IntegrationSpecLibrary()
        self.tangible = TangibleExtractor()
        self.sdl = get_system_design_library()
        self.final_layer = FinalProductLayer()
        self.client_pack = ClientPackWriter()
        self.package_deliverable = PackageDeliverableWriter()

    def run(
        self,
        *,
        industry_id: str,
        business: str,
        idea_title: str,
        request_id: str,
        paid: dict[str, Any],
        scores: dict[str, Any] | None = None,
        axes: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        oae: dict[str, Any] | None = None,
        success: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
        monetization: dict[str, Any] | None = None,
        fin_models: list[dict[str, Any]] | None = None,
        modeling_answers: dict[str, Any] | None = None,
        write_portal: bool = True,
        memo_convert: dict[str, Any] | None = None,
        market_unit: dict[str, Any] | None = None,
        client_name: str = "",
        demo_idea: dict[str, Any] | None = None,
        demo_ideas: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        scores = scores or {}
        axes = axes or {}
        # Numeric extras only for metrics; modeling answers from success / explicit
        extra = dict(extra_params or {})
        # Drop non-numeric extras (orientation also expects floats)
        extra_nums = {
            k: v
            for k, v in extra.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        ma = dict(modeling_answers or {})
        if isinstance(success, dict):
            if isinstance(success.get("modeling_answers"), dict):
                ma = {**success["modeling_answers"], **ma}
            # card may nest under different shapes from pipeline
            raw = success.get("raw") if isinstance(success.get("raw"), dict) else {}
            if isinstance(raw.get("modeling_answers"), dict):
                ma = {**raw["modeling_answers"], **ma}
        if "modeling_answers" in extra and isinstance(extra["modeling_answers"], dict):
            ma = {**extra["modeling_answers"], **ma}
        extra = extra_nums

        # Prefer Situation Metrics Engine (energy + function coupled)
        metrics = self.situation.analyze(
            business=business,
            industry_id=industry_id,
            scores=scores,
            axes=axes,
            idea_title=idea_title,
            paid=paid,
            extra_params=extra,
            success=success,
            energy=(paid or {}).get("energy_flow"),
            function_engine=(paid or {}).get("function_engine"),
        )
        # Reader modeling skeleton if 5-stage already ran
        reader_skeleton = (
            ((paid.get("reader") or {}).get("stages") or {})
            .get("2_notation", {})
            .get("modeling_skeleton")
        )
        # Must-Ask Loop (entities · flows · levers · jobs · metrics)
        questions = self.must_ask.run(
            business=business,
            industry_id=industry_id,
            idea_title=idea_title,
            paid=paid,
            metrics=metrics,
            decision=decision,
            oae=oae,
            scores=scores,
            modeling_answers=ma,
            reader_skeleton=reader_skeleton,
        )
        specs = self.specs.select(
            industry_id=industry_id,
            idea_title=idea_title,
            modeling_answers=ma,
            paid=paid,
        )
        pb = self.sdl.product_building_pack(industry_id)
        tangible = self.tangible.extract(
            industry_id=industry_id,
            idea_title=idea_title,
            paid=paid,
            metrics=metrics,
            questions=questions,
            specs=specs,
            monetization=monetization,
            fin_models=fin_models,
        )

        portal_payload = build_portal_payload(
            request_id=request_id,
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            tangible=tangible,
            metrics=metrics,
            questions=questions,
            paid=paid,
        )
        paths: dict[str, str] = {}
        if write_portal and request_id:
            try:
                paths = write_portal_files(
                    Path(PROJECT_ROOT),
                    portal_payload,
                    request_id=request_id,
                )
            except OSError as exc:
                paths = {"error": str(exc)}

        # Lightweight TZ skeleton for pilot (what was missing as «готовое ТЗ»)
        tz = {
            "title": f"TZ pilot · {idea_title[:60]}",
            "goal": idea_title,
            "problem": (metrics.get("top_leak") or {}).get("fix"),
            "solution_hypothesis": (paid.get("package") or {}).get("best_hypothesis"),
            "top_lever": (paid.get("package") or {}).get("top_lever"),
            "success_metric": "Define from pilot_definition answer + situation score lift",
            "scope_in": [
                "Orientation deliverables",
                "Chosen hypothesis implement scaffold",
                "Standards from integration_specs",
            ],
            "scope_out": [
                "Full hyperscaler migration",
                "Open-ended creative agency retainer without metric",
            ],
            "must_answer_before_build": [
                q.get("answer_field") for q in (questions.get("must_ask") or [])
            ],
            "standards": (specs.get("tz_block") or {}).get("specs"),
            "product_building_architecture": pb.get("architecture"),
            "acceptance_draft": [
                s.get("acceptance", [None])[0]
                for s in (specs.get("specs") or [])
                if s.get("acceptance")
            ][:6],
            "open_point": "OPEN: human locks price + legal SoW",
        }

        block_rerun = bool(questions.get("block_rerun"))
        natural = (
            "Must-Ask Loop: answer entities·flows·levers·jobs·metrics → re-run process → "
            "then open portal; Conceptual Engine vision remains OPEN last step"
            if block_rerun or questions.get("must_count", 0) > 0
            else "Open paid portal / commercial offer; reserve Conceptual Engine for supply-chain vision"
        )

        # Final layer: principles · narrative · anticlone · client pack · capital
        paid_for_final = {
            **(paid or {}),
            "situation_metrics": metrics,
            "business_metrics": metrics,
            "status": (paid or {}).get("status"),
            "paid_score": (paid or {}).get("paid_score"),
        }
        must_count = int(questions.get("must_count") or 0)
        final = self.final_layer.run(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            request_id=request_id,
            paid=paid_for_final,
            scores=scores,
            extra_params=extra_nums,
            must_ask_open=must_count,
        )
        # Client pack files (orientation memo) + Consult+TechWrite package folders
        pack_paths: dict[str, str] = {}
        package_paths: dict[str, Any] = {}
        if write_portal and request_id:
            try:
                pack_paths = self.client_pack.write(
                    project_root=Path(PROJECT_ROOT),
                    request_id=request_id,
                    industry_id=industry_id,
                    business=business,
                    idea_title=idea_title,
                    narrative=final.get("narrative_engine") or {},
                    commercial={
                        "commercial_offer": tangible.get("commercial_offer"),
                    },
                    paid=paid_for_final,
                )
            except OSError as exc:
                pack_paths = {"error": str(exc)}
            try:
                package_paths = self.package_deliverable.write(
                    request_id=request_id,
                    industry_id=industry_id,
                    business=business,
                    idea_title=idea_title,
                    narrative=final.get("narrative_engine") or {},
                    commercial={
                        "commercial_offer": tangible.get("commercial_offer"),
                    },
                    paid={
                        **paid_for_final,
                        "oae": oae or {},
                        "decision": decision or {},
                    },
                    memo_convert=memo_convert or {},
                    market_unit=market_unit,
                    success=success if isinstance(success, dict) else {},
                    extra_params=extra_nums,
                    client_name=client_name or "",
                    oae=oae or {},
                    decision=decision or {},
                    demo_idea=demo_idea or {"title": idea_title},
                    demo_ideas=list(demo_ideas or []),
                )
            except OSError as exc:
                package_paths = {"error": str(exc)}

        # Enrich portal with UI status + capital + narrative snippet
        memo = (final.get("narrative_engine") or {}).get("memo") or {}
        portal_payload = {
            **portal_payload,
            "ui_status": final.get("ui_status"),
            "capital_snapshot": final.get("capital_efficiency"),
            "harness_live": (final.get("harness_showcase") or {}).get("live_score"),
            "anti_down_gate": (final.get("anti_down_sorter") or {}).get("gate"),
            "plan_code": (final.get("sequence_assembler") or {}).get("plan_code"),
            "metric_meaning_table": _metric_meaning_table(industry_id),
            "narrative_summary": memo.get("executive_summary"),
            "client_pack_url": pack_paths.get("url"),
            "package_result_url": package_paths.get("url"),
            "narrative_quality": (final.get("narrative_engine") or {}).get("quality"),
        }
        # Prefer narrative problem/solution in offer when generic
        offer = portal_payload.get("offer") or {}
        if isinstance(offer, dict) and memo.get("executive_summary"):
            leak_label = (metrics.get("top_leak") or {}).get("label") or ""
            if "размыт" in leak_label.lower() or "unclear" in leak_label.lower():
                offer = {
                    **offer,
                    "client_problem": (
                        f"Operational friction around "
                        f"{(final.get('narrative_engine') or {}).get('relations', {}).get('true_groups', [{}])[0].get('hub', 'delivery')} "
                        f"— see orientation memo."
                    ),
                    "proposed_solution": idea_title
                    or offer.get("proposed_solution"),
                }
                portal_payload["offer"] = offer

        if write_portal and request_id:
            try:
                paths = write_portal_files(
                    Path(PROJECT_ROOT),
                    portal_payload,
                    request_id=request_id,
                )
            except OSError as exc:
                paths = {**(paths or {}), "error": str(exc)}

        return {
            "module": self.name,
            "business_metrics": metrics,
            "situation_metrics": metrics,
            "clarifying_questions": questions,
            "must_ask": questions,
            "integration_specs": specs,
            "product_building_library": pb,
            "tangible": tangible,
            "commercial_offer": tangible.get("commercial_offer"),
            "pilot_tz_draft": tz,
            "final_layer": final,
            "principles_engine": final.get("principles_engine"),
            "sequence_assembler": final.get("sequence_assembler"),
            "anti_down_sorter": final.get("anti_down_sorter"),
            "objectly": final.get("objectly"),
            "opening_edge": final.get("opening_edge"),
            "nft_create_building": final.get("nft_create_building"),
            "harness_showcase": final.get("harness_showcase"),
            "capital_efficiency": final.get("capital_efficiency"),
            "narrative_engine": final.get("narrative_engine"),
            "client_pack": pack_paths,
            "package_deliverable": package_paths,
            "ui_status": final.get("ui_status"),
            "portal": {
                "payload": portal_payload,
                "paths": paths,
                "url": paths.get("url") or portal_payload.get("portal_path"),
            },
            "ready_for_rerun": bool(questions.get("ready_for_rerun")),
            "block_rerun": block_rerun,
            "natural_next": natural,
            "summary": (
                f"Commercial layer: situation={metrics.get('situation_score')}, "
                f"must_ask={questions.get('must_count')}, "
                f"ready_rerun={questions.get('ready_for_rerun')}, "
                f"tariff={(tangible.get('commercial_offer') or {}).get('tariff', {}).get('id')}, "
                f"anti_down={(final.get('anti_down_sorter') or {}).get('gate')}, "
                f"narrative={(final.get('narrative_engine') or {}).get('quality', {}).get('consistency_score')}, "
                f"portal={paths.get('url') or 'n/a'}."
            ),
        }


def _metric_meaning_table(industry_id: str) -> list[dict[str, str]]:
    """What the number means / what it does NOT mean — portal copy table."""
    base = [
        {
            "metric": "utilization",
            "means": "Share of available capacity actually used this period",
            "does_not_mean": "Revenue quality, margin, or client happiness",
        },
        {
            "metric": "gross_margin",
            "means": "Revenue minus direct delivery cost, as % of revenue",
            "does_not_mean": "Cash in bank or long-term unit economics after CAC",
        },
        {
            "metric": "cycle_delivery_time",
            "means": "Median time from accepted job to delivered outcome",
            "does_not_mean": "Quality of outcome or rework-free delivery",
        },
        {
            "metric": "ARPU / monthly_revenue",
            "means": "Average revenue per account (or monthly top-line)",
            "does_not_mean": "Profitability per account or retention health alone",
        },
        {
            "metric": "rework_rate / churn",
            "means": "Share of work redone / share of clients leaving",
            "does_not_mean": "Root cause (product vs sales vs ops) without diagnosis",
        },
        {
            "metric": "paid_score",
            "means": "Internal readiness of this orientation pass for a paid path",
            "does_not_mean": "Guaranteed client success or packageable delivery alone",
        },
        {
            "metric": "situation_score",
            "means": "How well leaks/levers are grounded in described situation",
            "does_not_mean": "Market size or competitive moat",
        },
    ]
    if industry_id == "cloud-economy":
        base.append(
            {
                "metric": "cost_units (CloudForge)",
                "means": "Relative compute cost under placement/precision plan",
                "does_not_mean": "Your AWS invoice in dollars without calibration",
            }
        )
    return base
