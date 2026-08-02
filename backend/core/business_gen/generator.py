"""
Smart business generator — orchestration brain.

Plans multi-niche runs, service stack, side compute, self-test,
human-reaction forecast, expert base + panel + code pack.
"""

from __future__ import annotations

from typing import Any

from backend.core.knowledge_synthesis.synthesis_core import KnowledgeSynthesisEngine
from backend.core.business_gen.services_catalog import list_services

# 10 public client niches (distribution surface)
PUBLIC_NICHES: list[dict[str, Any]] = [
    {
        "id": "ai-agencies",
        "keywords": ("ai", "агент", "studio", "студи", "rework", "передел", "handoff", "сдач"),
        "label_ru": "AI-агентства и студии",
        "label_en": "AI agencies & studios",
    },
    {
        "id": "api-for-devs",
        "keywords": ("api", "integrat", "интегр", "webhook", "feature", "фич"),
        "label_ru": "Интеграции и фичи",
        "label_en": "Integrations & features",
    },
    {
        "id": "freelace-d2c",
        "keywords": ("freelance", "фриланс", "outreach", "заказ", "gigs"),
        "label_ru": "Фриланс",
        "label_en": "Freelance",
    },
    {
        "id": "expert-services",
        "keywords": ("expert", "эксперт", "consult", "консульт", "coaching"),
        "label_ru": "Экспертные услуги",
        "label_en": "Expert services",
    },
    {
        "id": "content-monetize",
        "keywords": ("content", "контент", "audience", "аудитор", "creator", "монетиз"),
        "label_ru": "Контент и аудитория",
        "label_en": "Content & audience",
    },
    {
        "id": "education",
        "keywords": ("educat", "обучен", "курс", "course", "cohort", "школ"),
        "label_ru": "Обучение",
        "label_en": "Education",
    },
    {
        "id": "automation-builders",
        "keywords": ("automat", "автомат", "no-code", "nocode", "workflow", "воркфлоу"),
        "label_ru": "Автоматизация и no-code",
        "label_en": "Automation & no-code",
    },
    {
        "id": "cost-ops",
        "keywords": ("unit", "себестоим", "margin", "марж", "cost", "leak", "утеч"),
        "label_ru": "Unit-economics",
        "label_en": "Unit economics",
    },
    {
        "id": "device-assembly",
        "keywords": ("device", "устрой", "сборк", "hardware", "config", "конфиг"),
        "label_ru": "Сборка устройств",
        "label_en": "Device assembly",
    },
    {
        "id": "asset-decisions",
        "keywords": ("asset", "актив", "risk", "риск", "портфел", "capital"),
        "label_ru": "Решения по активам",
        "label_en": "Asset decisions",
    },
]


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
        # ── Orchestration pass: rank all 10 niches + service stack ─────────
        orchestration = self._orchestrate(
            business_text,
            industry_id=industry_id,
            lang=lang,
        )
        # Prefer highest-scoring public niche if caller sent generic / empty
        ranked = orchestration.get("niche_ranking") or []
        # No public niche picker: always prefer orchestrator primary when generic/empty
        if ranked and industry_id in ("", "generic", "all", "none", "auto"):
            top = ranked[0].get("id")
            if top:
                industry_id = top
        elif ranked and industry_id not in {n["id"] for n in PUBLIC_NICHES}:
            top = ranked[0].get("id")
            if top:
                industry_id = top

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
            "orchestration": orchestration,
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
            "primary_industry": industry_id,
        }

        deliverable["final_gate"] = self._final_gate(deliverable)
        return {
            "module": self.name,
            "role": "orchestrator",
            "input": {
                "business": business_text[:500],
                "industry_id": industry_id,
                "lang": lang,
            },
            "output": deliverable,
            "message": core["pre_corrected"].get("opening_line"),
        }

    def _orchestrate(
        self,
        business_text: str,
        *,
        industry_id: str,
        lang: str,
    ) -> dict[str, Any]:
        """Plan runs across 10 niches + map distribution services to execute."""
        text = (business_text or "").lower()
        ranking: list[dict[str, Any]] = []
        for n in PUBLIC_NICHES:
            hits = sum(1 for kw in n["keywords"] if kw in text)
            boost = 0.35 if n["id"] == industry_id else 0.0
            score = min(1.0, 0.22 + hits * 0.18 + boost)
            ranking.append(
                {
                    "id": n["id"],
                    "label": n["label_ru"] if lang == "ru" else n["label_en"],
                    "score": round(score, 3),
                    "keyword_hits": hits,
                }
            )
        ranking.sort(key=lambda x: (-x["score"], x["id"]))

        # Service stack from public Business Tasks (distribution-facing)
        services = list_services(lang)
        # Order: offer → dist → ops → tz → agent → base → panel → full gen
        preferred = [
            "offer_pack",
            "distribution_engine",
            "ops_reframe",
            "tech_tz",
            "ai_agent_desk",
            "expert_base_gen",
            "control_panel",
            "full_business_gen",
        ]
        by_id = {s["id"]: s for s in services}
        stack = []
        for i, sid in enumerate(preferred):
            if sid not in by_id:
                continue
            s = by_id[sid]
            stack.append(
                {
                    "order": i + 1,
                    "service_id": sid,
                    "name": s["name"],
                    "role": (
                        "primary_run"
                        if sid in ("distribution_engine", "offer_pack", "full_business_gen")
                        else "supporting"
                    ),
                    "tagline": s.get("tagline"),
                }
            )

        top3 = ranking[:3]
        run_plan = [
            {
                "phase": 1,
                "title": "Ориентация по 10 нишам" if lang == "ru" else "Orient across 10 niches",
                "action": "rank_niches",
                "niches": [r["id"] for r in ranking],
            },
            {
                "phase": 2,
                "title": "Выбор первичной ниши" if lang == "ru" else "Pick primary niche",
                "action": "commit_primary",
                "primary": top3[0]["id"] if top3 else industry_id,
                "alternates": [r["id"] for r in top3[1:]],
            },
            {
                "phase": 3,
                "title": "Стек услуг (дистрибуция)" if lang == "ru" else "Service stack (distribution)",
                "action": "queue_services",
                "services": [s["service_id"] for s in stack],
            },
            {
                "phase": 4,
                "title": "Синтез + расчёты" if lang == "ru" else "Synthesis + compute",
                "action": "knowledge_synthesis",
                "engines": ["side_compute", "planner", "methods", "expert_base", "self_test"],
            },
            {
                "phase": 5,
                "title": "Артефакты" if lang == "ru" else "Artifacts",
                "action": "assemble",
                "outputs": ["plan", "expert_base", "control_panel", "code_pack"],
            },
        ]

        return {
            "mode": "multi_niche_orchestrator",
            "niches_total": len(PUBLIC_NICHES),
            "niche_ranking": ranking,
            "primary_niche": top3[0] if top3 else None,
            "alternate_niches": top3[1:] if len(top3) > 1 else [],
            "service_stack": stack,
            "run_plan": run_plan,
            "note": (
                "Генерация оркестрирует прогоны по 10 клиентским нишам и стек дистрибутивных услуг."
                if lang == "ru"
                else "Generate orchestrates runs across 10 client niches and the distribution service stack."
            ),
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
