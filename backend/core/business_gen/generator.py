"""
Smart business generator — orchestration brain.

Plans multi-niche runs, service stack, side compute, self-test,
human-reaction forecast, expert base + panel + code pack.
"""

from __future__ import annotations

from typing import Any

from backend.core.knowledge_synthesis.synthesis_core import KnowledgeSynthesisEngine
from backend.core.business_gen.services_catalog import list_services
from backend.core.business_gen.core_deliverable import (
    build_core_deliverable,
    merge_signer_numbers,
    _detect_profile,
)
from backend.core.business_gen.hook_plan import build_hook_plan

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
        "keywords": (
            "expert",
            "эксперт",
            "consult",
            "консульт",
            "coaching",
            "библиотек",
            "library",
            "архитект",
            "карточ",
        ),
        "label_ru": "Экспертные услуги / knowledge packs",
        "label_en": "Expert services / knowledge packs",
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
        "keywords": (
            "automat",
            "автомат",
            "no-code",
            "nocode",
            "workflow",
            "воркфлоу",
            "билдер",
            "builder",
            "product build",
            "it-продукт",
            "ай-ти",
            "marketplace",
            "маркетплейс",
            "концепт",
            "ниш",
        ),
        "label_ru": "Билдеры продуктов / automation",
        "label_en": "Product builders / automation",
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
        channel: str = "auto",
        multi_pass: bool = True,
        passes: int = 7,
    ) -> dict[str, Any]:
        channel_info = self._resolve_channel(business_text, channel=channel, lang=lang)
        # ── Orchestration pass: rank all 10 niches + service stack ─────────
        orchestration = self._orchestrate(
            business_text,
            industry_id=industry_id,
            lang=lang,
            channel=channel_info["mode"],
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
        answers = dict(answers or {})
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

        # Signer numbers → answers (constraint_cash, days) before planner runs
        profile_early = _detect_profile(business_text)
        answers, numbers = merge_signer_numbers(
            answers, numbers, profile=profile_early, lang=lang
        )

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
        control_panel = self._control_panel(
            core, lang=lang, channel=channel_info, industry_id=industry_id
        )
        forecast = self._implementation_forecast(
            core,
            channel=channel_info,
            multi_pass=multi_pass,
            passes=passes,
            lang=lang,
        )
        growth_core = self._growth_yield_core(
            business_text, core=core, channel=channel_info, lang=lang, industry_id=industry_id
        )
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
            "channel": channel_info,
            "implementation_forecast": forecast,
            "growth_yield_core": growth_core,
            # Surface-only directions (no marketing/fundraising backend automation)
            "surface_directions": self._surface_directions(lang=lang, channel=channel_info),
        }

        deliverable["final_gate"] = self._final_gate(deliverable)

        # Human-first Core report (primary surface — not raw JSON)
        core_report = build_core_deliverable(
            business_text,
            core=core,
            orchestration=orchestration,
            channel=channel_info,
            forecast=forecast,
            project_name=project_name,
            industry_id=industry_id,
            lang=lang,
            final_gate=deliverable["final_gate"],
            answers=answers,
            numbers=numbers,
        )
        deliverable["core_report"] = core_report

        # Catchy one-screen buy plan
        hook = build_hook_plan(
            project_name=project_name or core_report.get("title") or "",
            profile=core_report.get("profile") or profile_early,
            value=core_report.get("value_vs_core") or {},
            counts=core_report.get("counts") or {},
            signer_numbers=core_report.get("signer_numbers") or numbers,
            channel_log=core_report.get("channel_log_7d"),
            concept_tests=core_report.get("concept_tests"),
            assist=core_report.get("implementation_assistant"),
            open_questions=core_report.get("open_questions"),
            lang=lang,
        )
        deliverable["hook_plan"] = hook

        # Prefer profile-aware defaults for library/builders briefs
        rec = core_report.get("recommended_choices") or {}
        if rec and deliverable.get("plan"):
            for step in deliverable["plan"].get("steps") or []:
                sid = step.get("id")
                if sid in rec and not (choices or {}).get(sid):
                    if profile_should_override_default(
                        business_text, step.get("default_option"), rec[sid]
                    ):
                        step["default_option"] = rec[sid]
            # Reflect closed money-path questions in plan surface
            if core_report.get("open_questions") is not None:
                deliverable["plan"]["open_questions"] = list(
                    core_report.get("open_questions") or []
                )

        opening = core["pre_corrected"].get("opening_line") or ""
        value = core_report.get("value_vs_core") or {}
        n_cards = core_report.get("counts", {}).get("total_cards", 0)
        is_en = (lang or "").lower().startswith("en")
        if is_en:
            human_lead = (
                f"{opening} "
                f"Clean Core report ready ({n_cards} cards). "
                f"Value ~${value.get('realized_mid_usd', '?')} vs ${value.get('tariff_price_usd', 790)} "
                f"({value.get('band', '')}). "
                f"{hook.get('cta', '')}"
            ).strip()
        else:
            human_lead = (
                f"{opening} "
                f"Готов чистый отчёт Ядра ({n_cards} карточек). "
                f"Оценка ценности ~${value.get('realized_mid_usd', '?')} vs тариф $790 "
                f"({value.get('band', '')}). "
                f"{hook.get('cta', '')}"
            ).strip()

        return {
            "module": self.name,
            "role": "orchestrator",
            "input": {
                "business": business_text[:500],
                "industry_id": industry_id,
                "lang": lang,
                "channel": channel_info["mode"],
                "passes": passes if multi_pass else 1,
                "signer_numbers": {
                    "cash_ceiling": float(numbers.get("cash_ceiling", 0)),
                    "days": int(float(numbers.get("days", 21))),
                },
            },
            "output": deliverable,
            "message": human_lead,
            "core_markdown": core_report.get("markdown"),
            "hook_markdown": hook.get("markdown"),
            "value_vs_core": value,
            "exports": core_report.get("exports"),
        }

    def _resolve_channel(
        self, business_text: str, *, channel: str, lang: str
    ) -> dict[str, Any]:
        ch = (channel or "auto").strip().lower()
        text = (business_text or "").lower()
        online_kw = (
            "online",
            "онлайн",
            "saas",
            "ecommerce",
            "e-com",
            "shopify",
            "сайт",
            "web",
            "app",
            "digital",
            "d2c",
            "marketplace",
        )
        offline_kw = (
            "offline",
            "офлайн",
            "оффлайн",
            "кафе",
            "cafe",
            "retail",
            "store",
            "магазин",
            "салон",
            "локац",
            "point of sale",
            "pos",
            "ресторан",
            "clinic",
            "клиник",
            "warehouse",
            "склад",
        )
        online_hits = sum(1 for k in online_kw if k in text)
        offline_hits = sum(1 for k in offline_kw if k in text)
        if ch in ("online", "offline", "hybrid"):
            mode = ch
            detected = "manual"
        elif online_hits and offline_hits:
            mode = "hybrid"
            detected = "auto"
        elif offline_hits > online_hits:
            mode = "offline"
            detected = "auto"
        elif online_hits > offline_hits:
            mode = "online"
            detected = "auto"
        else:
            mode = "hybrid"
            detected = "auto_default"
        labels = {
            "online": ("Online core", "Онлайн-ядро"),
            "offline": ("Offline core", "Офлайн-ядро"),
            "hybrid": ("Hybrid core", "Гибридное ядро"),
        }
        en, ru = labels[mode]
        return {
            "mode": mode,
            "detected": detected,
            "label": ru if lang == "ru" else en,
            "online_hits": online_hits,
            "offline_hits": offline_hits,
            "standout_angle": (
                "Выделиться на рынке или собрать офлайн как у сильного клиентского бренда"
                if lang == "ru"
                else "Stand out in market or shape offline ops like the client’s brand"
            ),
        }

    def _implementation_forecast(
        self,
        core: dict,
        *,
        channel: dict[str, Any],
        multi_pass: bool,
        passes: int,
        lang: str,
    ) -> dict[str, Any]:
        """Simulate multi-pass generation quality for post-approval rollout."""
        n = max(3, min(int(passes or 7), 12)) if multi_pass else 1
        q = core.get("quality") or {}
        st = core.get("self_test") or {}
        synth = core.get("synthesis") or {}
        base = float(q.get("anti_template_score") or 0.62)
        hr = core.get("human_reaction_forecast") or {}
        human = float(hr.get("score") or hr.get("acceptance") or 0.6)
        if human > 1:
            human = human / 100.0
        prod = 1.0 if st.get("prod_ready_hint") else 0.72
        mode_boost = {"online": 0.03, "offline": 0.04, "hybrid": 0.05}.get(
            channel.get("mode"), 0.03
        )
        scores: list[float] = []
        for i in range(n):
            # Deterministic micro-variation (no randomness) across passes
            wobble = ((i * 17) % 11 - 5) * 0.008
            s = min(0.97, max(0.42, base * 0.55 + human * 0.25 + prod * 0.12 + mode_boost + wobble))
            # Later passes slightly tighten (refinement story)
            s = min(0.97, s + i * 0.012)
            scores.append(round(s, 3))
        readiness = round(sum(scores) / len(scores), 3)
        if readiness >= 0.82:
            band = "ultra"
        elif readiness >= 0.7:
            band = "strong"
        elif readiness >= 0.55:
            band = "solid"
        else:
            band = "refine"
        ch = channel.get("mode", "hybrid")
        if lang == "ru":
            summary = (
                f"По {n} прогонам генерации: при утверждении реального внедрения "
                f"({channel.get('label', ch)}) ожидаемое качество ~{int(readiness * 100)}% "
                f"(полоса {band}). Ассистент внедрения + тестировщик-стратег — после go-ahead."
            )
        else:
            summary = (
                f"Across {n} generation passes: if you approve real implementation "
                f"({channel.get('label', ch)}), expected quality ~{int(readiness * 100)}% "
                f"(band {band}). Implementation assistant + tester-strategist after go-ahead."
            )
        return {
            "passes": n,
            "pass_scores": scores,
            "readiness_if_approved": readiness,
            "quality_band": band,
            "channel": ch,
            "summary": summary,
            "critical_levers": [
                "identity_in_panel",
                "asset_structure_no_auto_yield",
                "connect_vs_diy",
                "client_pack_config",
                "final_client_tune_after_confirm",
            ],
            "pay_model": "optional_on_implementation_approval",
        }

    def _growth_yield_core(
        self,
        business_text: str,
        *,
        core: dict,
        channel: dict[str, Any],
        lang: str,
        industry_id: str,
    ) -> dict[str, Any]:
        moves = (core.get("synthesis") or {}).get("original_moves") or []
        identity = (business_text or "").strip()[:160] or industry_id
        if lang == "ru":
            return {
                "title": "Ядро Growth / Yield",
                "for": ["growth_specialists", "system_yield_engineers", "business_owners"],
                "identity": {
                    "unique_angle": identity,
                    "channel": channel.get("mode"),
                    "standout": channel.get("standout_angle"),
                },
                "assets_in_panel": {
                    "structure": ["ops_metric", "leak_map", "capacity", "client_pack_slots"],
                    "note": "Только структура и метрики риска — без авто-обещаний доходности.",
                },
                "connect_recommendations": [
                    "Панель управления (sense / decide / act)",
                    "Карта подключений: что внедрить первым",
                    "Варианты DIY vs готовый коннектор",
                ],
                "diy_options": [
                    "Собрать scoreboard самому по ТЗ",
                    "Подключить 1–2 интеграции вручную",
                    "Описать handoff для команды",
                ],
                "client_pack": {
                    "title": "Пак клиентов с похожими запросами",
                    "config_hint": "Один playbook · общее табло · согласованные handoff",
                },
                "implementation_assistant": "Ассистент внедрения + тестировщик-стратег",
                "final_client_tuning": "Рекомендации конечной настройки — после подтверждения",
                "original_moves": moves[:5],
            }
        return {
            "title": "Growth / Yield core",
            "for": ["growth_specialists", "system_yield_engineers", "business_owners"],
            "identity": {
                "unique_angle": identity,
                "channel": channel.get("mode"),
                "standout": channel.get("standout_angle"),
            },
            "assets_in_panel": {
                "structure": ["ops_metric", "leak_map", "capacity", "client_pack_slots"],
                "note": "Structure & risk metrics only — no automatic yield promises.",
            },
            "connect_recommendations": [
                "Control panel (sense / decide / act)",
                "Connection map: what to wire first",
                "DIY vs ready connector options",
            ],
            "diy_options": [
                "Build scoreboard yourself from TZ",
                "Wire 1–2 integrations manually",
                "Write team handoff notes",
            ],
            "client_pack": {
                "title": "Pack of clients with similar requests",
                "config_hint": "One playbook · shared scoreboard · coordinated handoffs",
            },
            "implementation_assistant": "Implementation assistant + tester-strategist",
            "final_client_tuning": "Final config recommendations — after confirmation",
            "original_moves": moves[:5],
        }

    def _surface_directions(self, *, lang: str, channel: dict[str, Any]) -> dict[str, Any]:
        """Short best-version directions for marketing & capital — no backend automation."""
        if lang == "ru":
            return {
                "marketing": {
                    "status": "surface_only",
                    "note": "Бэкенд маркетинга не трогаем — краткие направления.",
                    "ideas": [
                        "Угол продвижения из ops-фактов пилота",
                        "1 сигнал / 1 канал в неделю",
                        "Кейс: до/после ядра (без hype)",
                    ],
                },
                "external_capital": {
                    "status": "partner_later",
                    "note": "Привлечение финансирования — после согласования с партнёром.",
                    "ideas": [
                        "Доказать 1–2 платных пилота",
                        "Capital narrative: deep-tech runtime + GTM",
                        "Чеклист готовности для партнёра",
                    ],
                },
                "channel": channel.get("mode"),
            }
        return {
            "marketing": {
                "status": "surface_only",
                "note": "Marketing backend untouched — short directions only.",
                "ideas": [
                    "Promotion angle from pilot ops facts",
                    "1 signal / 1 channel per week",
                    "Case: before/after core (no hype)",
                ],
            },
            "external_capital": {
                "status": "partner_later",
                "note": "Fundraising automation after partner approval.",
                "ideas": [
                    "Prove 1–2 paid pilots",
                    "Capital narrative: deep-tech runtime + GTM",
                    "Partner readiness checklist",
                ],
            },
            "channel": channel.get("mode"),
        }

    def _orchestrate(
        self,
        business_text: str,
        *,
        industry_id: str,
        lang: str,
        channel: str = "hybrid",
    ) -> dict[str, Any]:
        """Plan runs across 10 niches + map distribution services to execute."""
        text = (business_text or "").lower()
        ranking: list[dict[str, Any]] = []
        for n in PUBLIC_NICHES:
            hits = sum(1 for kw in n["keywords"] if kw in text)
            boost = 0.35 if n["id"] == industry_id else 0.0
            # Light channel affinity (not niche lock)
            if channel == "offline" and n["id"] in ("device-assembly", "cost-ops", "expert-services"):
                boost += 0.08
            if channel == "online" and n["id"] in ("ai-agencies", "api-for-devs", "content-monetize", "freelace-d2c"):
                boost += 0.08
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
                "outputs": ["plan", "expert_base", "control_panel", "code_pack", "implementation_forecast"],
            },
        ]

        note_ru = (
            f"Генерация оркестрирует прогоны по 10 нишам (канал: {channel}) "
            "и стек услуг. Auto = ранжирование; утверждение внедрения — за вами."
        )
        note_en = (
            f"Generate orchestrates runs across 10 niches (channel: {channel}) "
            "and the service stack. Auto = ranking; implementation approval is yours."
        )
        return {
            "mode": "multi_niche_orchestrator",
            "channel": channel,
            "niches_total": len(PUBLIC_NICHES),
            "niche_ranking": ranking,
            "primary_niche": top3[0] if top3 else None,
            "alternate_niches": top3[1:] if len(top3) > 1 else [],
            "service_stack": stack,
            "run_plan": run_plan,
            "note": note_ru if lang == "ru" else note_en,
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

    def _control_panel(
        self,
        core: dict,
        lang: str,
        channel: dict[str, Any] | None = None,
        industry_id: str = "",
    ) -> dict[str, Any]:
        side = core.get("side_compute") or {}
        plan = core.get("plan") or {}
        ch = channel or {}
        identity_card = {
            "k": "identity",
            "v": {
                "channel": ch.get("mode"),
                "industry": industry_id,
                "standout": ch.get("standout_angle"),
            },
        }
        assets_card = {
            "k": "assets",
            "v": {
                "structure": ["ops_metric", "leak_map", "capacity", "client_pack_slots"],
                "auto_yield": False,
                "note": (
                    "Структура и риск — без авто-доходности"
                    if lang == "ru"
                    else "Structure & risk — no auto-yield"
                ),
            },
        }
        connect_card = {
            "k": "connect_or_diy",
            "v": (
                ["panel", "integrations", "diy_scoreboard"]
                if lang != "ru"
                else ["панель", "интеграции", "diy_табло"]
            ),
        }
        return {
            "title": "Панель управления бизнесом" if lang == "ru" else "Business control panel",
            "layout": "clean_3_col",
            "columns": [
                {
                    "id": "sense",
                    "title": "Sense",
                    "cards": [
                        identity_card,
                        assets_card,
                        {"k": "confidence", "v": plan.get("confidence")},
                        {"k": "risk_band", "v": (side.get("risk_lattice") or {}).get("band")},
                    ],
                },
                {
                    "id": "decide",
                    "title": "Decide",
                    "cards": [
                        {"k": "mode", "v": plan.get("mode")},
                        connect_card,
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
                        {
                            "k": "client_pack",
                            "v": (
                                "config for similar client requests"
                                if lang != "ru"
                                else "конфиг пака похожих запросов"
                            ),
                        },
                        {
                            "k": "implementation_assistant",
                            "v": (
                                "assistant + tester-strategist"
                                if lang != "ru"
                                else "ассистент + тестировщик-стратег"
                            ),
                        },
                        {"k": "original_moves", "v": (core.get("synthesis") or {}).get("original_moves")},
                        {"k": "kill_switches", "v": (side.get("risk_lattice") or {}).get("kill_switches")},
                    ],
                },
            ],
            "ux_rules": [
                "no clutter — max 3 columns",
                "secondary detail collapsed",
                "primary CTA: confirm next plan step",
                "optional pay only on implementation approval",
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


def profile_should_override_default(
    business_text: str, current: str | None, recommended: str
) -> bool:
    """Soft override plan defaults for library/architecture briefs."""
    t = (business_text or "").lower()
    libraryish = any(
        w in t
        for w in (
            "библиотек",
            "library",
            "карточ",
            "архитект",
            "билдер",
            "builder",
            "концепт",
            "ниш",
        )
    )
    if not libraryish:
        return False
    # Don't fight explicit non-empty human choices (handled by caller)
    return bool(recommended) and (not current or current != recommended)


def generate_business(business_text: str, **kwargs: Any) -> dict[str, Any]:
    return BusinessGenerator().generate(business_text, **kwargs)


def catalog_and_demo(lang: str = "ru") -> dict[str, Any]:
    return {
        "services": list_services(lang),
        "demos": {s["id"]: service_demo(s["id"], lang) for s in list_services(lang)},
    }
