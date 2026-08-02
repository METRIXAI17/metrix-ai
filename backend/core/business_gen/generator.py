"""
Smart business generator.

Evaluates uncertainty, self-tests mid-flight, forecasts human reaction,
pre-corrects errors, assembles expert base + panel + code pack hints.
Specialized depth for resource recycling + logistics.
"""

from __future__ import annotations

from typing import Any

from backend.core.knowledge_synthesis.synthesis_core import KnowledgeSynthesisEngine
from backend.core.business_gen.services_catalog import list_services, service_demo


class BusinessGenerator:
    name = "BusinessGenerator"

    def __init__(self) -> None:
        self.ks = KnowledgeSynthesisEngine()

    def generate(
        self,
        business_text: str,
        *,
        industry_id: str = "automation-builders",
        lang: str = "ru",
        answers: dict[str, str] | None = None,
        choices: dict[str, str] | None = None,
        numbers: dict[str, float] | None = None,
        project_name: str = "",
    ) -> dict[str, Any]:
        # Default numbers for resource-ish businesses if empty
        numbers = dict(numbers or {})
        text_l = (business_text or "").lower()
        is_resource = any(
            w in text_l
            for w in (
                "переработ",
                "вторсырь",
                "отход",
                "логист",
                "recycl",
                "scrap",
                "waste",
                "металлолом",
            )
        )
        if is_resource and "inflow" not in numbers:
            numbers.setdefault("inflow", 120.0)
            numbers.setdefault("capacity", 90.0)
            numbers.setdefault("leak", 0.16)
            numbers.setdefault("focus", "logistics")

        stages = None
        if is_resource:
            stages = [
                "intake",
                "sort_quality",
                "process",
                "store",
                "logistics",
                "buyer",
                "cash",
                "feedback",
            ]

        constraints = {
            "cash_ceiling": float(numbers.get("cash_ceiling", 5000)),
            "days": int(numbers.get("days", 21)),
            "team": int(numbers.get("team", 1)),
        }

        core = self.ks.run(
            business_text,
            industry_id=industry_id,
            lang=lang,
            answers=answers,
            choices=choices,
            numbers=numbers,
            constraints=constraints,
            project_name=project_name or ("Resource+Logistics OS" if is_resource else ""),
            stages=stages,
        )

        autonomous_code = self._code_pack(core, is_resource=is_resource, lang=lang)
        control_panel = self._control_panel(core, lang=lang)
        deliverable = {
            "autonomous_code_pack": autonomous_code,
            "expert_base": core["expert_base"],
            "control_panel": control_panel,
            "interaction": core["tz_style_interaction"],
            "plan": core["plan"],
            "quality": core["quality"],
            "human_reaction_forecast": core["human_reaction_forecast"],
            "self_test": core["self_test"],
            "pre_corrected": core["pre_corrected"],
            "side_compute": core["side_compute"],
            "synthesis_highlights": {
                "original_moves": core["synthesis"].get("original_moves"),
                "anti_template_score": core["synthesis"].get("anti_template_score"),
                "methods_run": core["synthesis"].get("methods_run"),
            },
            "domain": core["domain"],
            "resource_logistics_mode": is_resource,
        }

        # Mid-flight second self-test after assembly
        deliverable["final_gate"] = self._final_gate(deliverable)
        return {
            "module": self.name,
            "input": {
                "business": business_text[:500],
                "industry_id": industry_id,
                "lang": lang,
            },
            "output": deliverable,
            "message": core["pre_corrected"].get("opening_line"),
        }

    def _code_pack(self, core: dict, is_resource: bool, lang: str) -> dict[str, Any]:
        widgets = (core.get("expert_base") or {}).get("panel_widgets") or []
        components = [
            "planner_wizard.py — HumanLightPlanner steps S1–S6",
            "side_engines.py — flow / risk / graph / uncertainty",
            "expert_base.json — project knowledge pack",
            "panel/index.html — control surface",
            "distribution_plan.json — brand/platforms/networks",
        ]
        if is_resource:
            components.extend(
                [
                    "flow_balance_worker.py — daily capacity tick",
                    "route_board.md — logistics critical path",
                    "buyer_dual_list.csv — dual-source hedge",
                ]
            )
        return {
            "title": "Autonomous assembly pack",
            "weight": "substantial",
            "components": components,
            "widgets": widgets,
            "grok_build_note": (
                "Пакет для конечной сборки в Grok Build: компоненты уже согласованы; "
                "не генерировать с нуля — донастроить ядро автосборки."
                if lang == "ru"
                else "Grok Build pack: components pre-agreed; wire assembly core, don't regenerate from scratch."
            ),
            "entrypoints": [
                "POST /api/v1/analytics/business-generate",
                "POST /api/v1/analytics/knowledge-synthesis",
                "GET /api/v1/analytics/business-services",
            ],
        }

    def _control_panel(self, core: dict, lang: str) -> dict[str, Any]:
        side = core.get("side_compute") or {}
        plan = core.get("plan") or {}
        return {
            "title": "Панель управления бизнесом" if lang == "ru" else "Business control panel",
            "layout": "clean_3_col",
            "columns": [
                {
                    "id": "sense",
                    "title": "Sense",
                    "cards": [
                        {"k": "confidence", "v": plan.get("confidence")},
                        {"k": "uncertainty", "v": (side.get("uncertainty") or {})},
                        {"k": "risk_band", "v": (side.get("risk_lattice") or {}).get("band")},
                    ],
                },
                {
                    "id": "decide",
                    "title": "Decide",
                    "cards": [
                        {"k": "mode", "v": plan.get("mode")},
                        {"k": "steps", "v": [
                            {"id": s["id"], "title": s["title"], "default": s.get("default_option")}
                            for s in (plan.get("steps") or [])
                        ]},
                        {"k": "open_questions", "v": plan.get("open_questions")},
                    ],
                },
                {
                    "id": "act",
                    "title": "Act",
                    "cards": [
                        {"k": "original_moves", "v": (core.get("synthesis") or {}).get("original_moves")},
                        {"k": "kill_switches", "v": (side.get("risk_lattice") or {}).get("kill_switches")},
                        {"k": "flow", "v": side.get("flow_balance")},
                    ],
                },
            ],
            "ux_rules": [
                "no clutter — max 3 columns",
                "secondary detail collapsed",
                "primary CTA: confirm next plan step",
            ],
        }

    def _final_gate(self, deliverable: dict) -> dict[str, Any]:
        st = deliverable.get("self_test") or {}
        q = deliverable.get("quality") or {}
        ok = bool(st.get("prod_ready_hint")) and float(q.get("anti_template_score") or 0) >= 0.6
        return {
            "go_prod": ok,
            "score": st.get("score"),
            "verdict": "GO" if ok else "CONDITIONAL_GO",
            "note": (
                "Кандидат в прод: originality + self-test gates"
                if ok
                else "Условный go: усилить originality/matrix или закрыть uncertainty с человеком"
            ),
        }


def generate_business(business_text: str, **kwargs: Any) -> dict[str, Any]:
    return BusinessGenerator().generate(business_text, **kwargs)


def catalog_and_demo(lang: str = "ru") -> dict[str, Any]:
    return {
        "services": list_services(lang),
        "demos": {s["id"]: service_demo(s["id"], lang) for s in list_services(lang)},
    }
