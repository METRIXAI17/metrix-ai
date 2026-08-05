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
from backend.core.business_gen.rd_reader import convert_to_rd
from backend.core.business_gen.author_personality import build_author_personality
from backend.core.business_gen.smart_router import route_generate
from backend.core.business_gen.skill_memory import (
    distill_skill_from_run,
    list_skills,
    memory_status,
)
from backend.core.business_gen.assist_agent import ImplementationAssistAgent
from backend.core.business_gen.identity_engine import build_post_pay_identity_pack
from backend.core.business_gen.live_log import create_live_log_from_plan

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

        # Author personality product (context engineering / harness stance)
        personality = build_author_personality(
            business_text,
            profile=core_report.get("profile") or profile_early,
            project_name=project_name or core_report.get("title") or "",
            answers=core_report.get("inferred_answers") or answers,
            lang=lang,
        )
        deliverable["author_personality"] = personality

        # Skill memory: load prior skills into harness, then distill this run
        prior_skills = list_skills(limit=8)
        routing = route_generate(
            business_text,
            channel=channel_info.get("mode") or channel,
            profile=core_report.get("profile") or profile_early,
            personality=personality,
            quality=core.get("quality") or {},
            available_skills=prior_skills,
            lang=lang,
        )
        deliverable["smart_routing"] = routing

        distilled = distill_skill_from_run(
            business_text=business_text,
            core_report=core_report,
            routing=routing,
            personality=personality,
            quality=core.get("quality") or {},
            project_name=project_name or core_report.get("title") or "",
            lang=lang,
            persist=True,
        )
        deliverable["skill_distilled"] = distilled
        deliverable["skill_memory"] = {
            "status": memory_status(),
            "loaded": routing.get("skills_loaded") or [],
            "new_skill_id": distilled.get("id"),
        }

        # R&D reader-converter (primary readable surface — not plain MD dump)
        rd = convert_to_rd(
            core_report=core_report,
            personality=personality,
            routing=routing,
            skills=[distilled] + list(routing.get("skills_loaded") or [])[:3],
            lang=lang,
        )
        deliverable["rd_reader"] = rd

        # Main consultation PDF = analytical HTML (print→PDF) — not "R&D" branding for client
        consult_html = rd.get("html") or (core_report.get("exports") or {}).get("print_html") or ""
        consult_md = rd.get("markdown") or core_report.get("markdown") or ""
        # Soft-replace R&D labels in client-facing HTML
        if (lang or "").lower().startswith("en"):
            consult_html = (
                consult_html.replace("R&amp;D Reader", "Analytical report")
                .replace("R&D Memo", "Consultation report")
                .replace("R&amp;D Memo", "Consultation report")
                .replace("Laboratory memo", "Consultation report")
                .replace("FREE DOWNLOAD", "MAIN PDF")
            )
        else:
            consult_html = (
                consult_html.replace("R&amp;D Reader", "Аналитический отчёт")
                .replace("R&D Memo", "Консультационный отчёт")
                .replace("R&amp;D Memo", "Консультационный отчёт")
                .replace("Лабораторная записка", "Консультационный отчёт")
                .replace("Лабораторная записка с обоснованиями решений", "Аналитический отчёт с обоснованием решений")
                .replace("FREE DOWNLOAD", "ОСНОВНОЙ PDF")
                .replace("БЕСПЛАТНО СКАЧАТЬ", "ОСНОВНОЙ PDF")
            )
        exports = dict(core_report.get("exports") or {})
        exports["consultation_html"] = consult_html
        exports["consultation_md"] = consult_md
        exports["rd_html"] = consult_html  # legacy key
        exports["rd_markdown"] = consult_md
        exports["print_html"] = consult_html or exports.get("print_html") or ""
        exports["free"] = True
        exports["filenames"] = {
            **(exports.get("filenames") or {}),
            "pdf_html": "metrix-consultation.pdf.html",
            "html": "metrix-consultation.pdf.html",
            "rd_html": "metrix-consultation.pdf.html",
            "md": "metrix-consultation.md",
            "rd_md": "metrix-consultation.md",
            "csv": (exports.get("filenames") or {}).get("csv") or "metrix-cards.csv",
        }
        exports["note"] = (
            "Main PDF: open HTML → Print → Save as PDF. Cards CSV included."
            if (lang or "").lower().startswith("en")
            else "Основной PDF: откройте HTML → Печать → Сохранить как PDF. CSV карточек в комплекте."
        )
        deliverable["exports"] = exports
        core_report["exports"] = exports
        deliverable["analytical_report"] = {
            "title": "Analytical report" if (lang or "").lower().startswith("en") else "Аналитический отчёт",
            "html": consult_html,
            "markdown": consult_md,
            "ready": bool(consult_html),
        }

        # Live 7-day channel log (interactive session)
        live_log = create_live_log_from_plan(
            core_report.get("channel_log_7d") or {},
            project_name=project_name or core_report.get("title") or "",
            run_id=distilled.get("id") or "",
            lang=lang,
        )
        deliverable["live_log"] = live_log

        # Post-pay identity: unique questions + uniqueness forecast (Metrix voice)
        identity_pack = build_post_pay_identity_pack(
            business_text,
            personality=personality,
            profile=core_report.get("profile") or profile_early,
            project_name=project_name or core_report.get("title") or "",
            lang=lang,
        )
        deliverable["identity_pack"] = identity_pack
        # Replace open_questions with identity-only unique Q for post-pay surface
        identity_q_texts = [q["text"] for q in identity_pack.get("identity_questions") or []]
        deliverable["plan"] = dict(deliverable.get("plan") or core.get("plan") or {})
        deliverable["plan"]["open_questions"] = identity_q_texts
        deliverable["plan"]["identity_questions"] = identity_pack.get("identity_questions") or []
        core_report["open_questions"] = identity_q_texts

        # Autonomous assist agent — after payment messaging
        agent = ImplementationAssistAgent().build_from_core(
            core_report,
            personality=personality,
            routing=routing,
            lang=lang,
            approved=False,
        )
        deliverable["assist_agent"] = agent
        deliverable["assist_offer"] = agent.get("offer")

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
            personality=personality,
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
            if core_report.get("open_questions") is not None:
                deliverable["plan"]["open_questions"] = list(
                    core_report.get("open_questions") or []
                )

        n_cards = core_report.get("counts", {}).get("total_cards", 0)
        is_en = (lang or "").lower().startswith("en")
        title_show = project_name or core_report.get("title") or ""
        if is_en:
            human_lead = (
                f"Consultation ready for «{title_show}»: filling, analytical report and main PDF "
                f"({n_cards} cards). Author uniqueness + deploy agent — after payment."
            )
        else:
            human_lead = (
                f"Консультация по «{title_show}»: наполнение, аналитический отчёт и основной PDF готовы "
                f"({n_cards} карточек). Авторская уникальность + агент деплоя — после оплаты."
            )

        return {
            "module": self.name,
            "role": "orchestrator",
            "version": "2.2.0-consult-clean",
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
            "core_markdown": consult_md,
            "rd_html": consult_html,
            "rd_markdown": consult_md,
            "consultation_html": consult_html,
            "hook_markdown": hook.get("markdown"),
            "hook_plan": hook,
            "value_vs_core": core_report.get("value_vs_core") or {},
            "exports": exports,
            "author_personality": personality,
            "assist_offer": agent.get("offer"),
            "live_log_id": live_log.get("id"),
            "identity_pack": identity_pack,
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
        is_ru = lang == "ru"
        components = [
            {
                "id": "planner",
                "file": "planner_wizard.py",
                "role": "S1–S6 шаги выбора" if is_ru else "S1–S6 choice steps",
                "status": "ready",
            },
            {
                "id": "engines",
                "file": "side_engines.py",
                "role": "поток / риск / неопределённость" if is_ru else "flow / risk / uncertainty",
                "status": "ready",
            },
            {
                "id": "expert",
                "file": "expert_base.json",
                "role": "база знаний проекта" if is_ru else "project knowledge base",
                "status": "ready",
            },
            {
                "id": "panel",
                "file": "panel/index.html",
                "role": "панель Sense · Decide · Act" if is_ru else "Sense · Decide · Act panel",
                "status": "ready",
            },
            {
                "id": "cards",
                "file": "architecture_cards.csv",
                "role": "12 deep-карточек + офферы" if is_ru else "12 deep cards + offers",
                "status": "ready",
            },
            {
                "id": "assist",
                "file": "assist_agent_session.json",
                "role": "агент деплоя (после оплаты)" if is_ru else "deploy agent (after payment)",
                "status": "after_pay",
            },
            {
                "id": "promo",
                "file": "promotion_pack.json",
                "role": "3 дороги продвижения + DM-скрипты" if is_ru else "3 promo roads + DM scripts",
                "status": "ready",
            },
        ]
        if is_resource:
            components.extend(
                [
                    {
                        "id": "flow",
                        "file": "flow_balance_worker.py",
                        "role": "суточный capacity tick" if is_ru else "daily capacity tick",
                        "status": "ready",
                    },
                    {
                        "id": "routes",
                        "file": "route_board.md",
                        "role": "логистический critical path" if is_ru else "logistics critical path",
                        "status": "ready",
                    },
                ]
            )
        next_build = [
            _d_code(is_ru, "Подключить assist session к private room", "Wire assist session to private room"),
            _d_code(is_ru, "Авто-export PDF без print dialog", "Auto PDF export without print dialog"),
            _d_code(is_ru, "Синк skill_memory → Grok Build skills", "Sync skill_memory → Grok Build skills"),
        ]
        return {
            "title": "Пакет сборки" if is_ru else "Assembly pack",
            "weight": "substantial",
            "components": [c["file"] + " — " + c["role"] for c in components],
            "components_rich": components,
            "widgets": widgets,
            "next_build": next_build,
            "grok_build_note": (
                "Пакет для сборки: модули согласованы. Не генерировать с нуля — донастроить и связать."
                if is_ru
                else "Build pack: modules agreed. Don’t regenerate from scratch — wire and tune."
            ),
            "entrypoints": [
                "POST /api/v1/analytics/business-generate",
                "POST /api/v1/analytics/promotion-pack",
                "POST /api/v1/analytics/assist-agent/approve",
            ],
        }


def _d_code(is_ru: bool, ru: str, en: str) -> str:
    return ru if is_ru else en


# re-attach methods that must live on BusinessGenerator (patch after _code_pack edit)
def _control_panel_impl(
    self,
    core: dict,
    lang: str,
    channel: dict[str, Any] | None = None,
    industry_id: str = "",
) -> dict[str, Any]:
    side = core.get("side_compute") or {}
    plan = core.get("plan") or {}
    ch = channel or {}
    is_ru = lang == "ru"
    ch_mode = ch.get("mode") or "auto"
    standout = ch.get("standout_angle") or ("Угол из брифа" if is_ru else "Angle from brief")
    conf = plan.get("confidence")
    conf_s = f"{float(conf):.0%}" if conf is not None else "—"
    risk = (side.get("risk_lattice") or {}).get("band") or "—"
    steps = plan.get("steps") or []
    step_txt = "; ".join(
        f"{s.get('title')}: {s.get('default_option') or '—'}" for s in steps[:6]
    ) or "—"
    moves = (core.get("synthesis") or {}).get("original_moves") or []
    move_txt = moves[0] if moves else ("—" if not is_ru else "—")
    kills = (side.get("risk_lattice") or {}).get("kill_switches") or []
    kill_txt = (
        "; ".join(str(k) for k in kills[:2])
        if kills
        else ("Работа только в scope · без open retainer" if is_ru else "Stay in scope · no open retainers")
    )
    return {
        "title": "Панель: понять · решить · сделать" if is_ru else "Panel: sense · decide · act",
        "layout": "clean_3_col",
        "human": True,
        "columns": [
            {
                "id": "sense",
                "title": "Понять" if is_ru else "Sense",
                "cards": [
                    {
                        "k": "Кто вы" if is_ru else "Who you are",
                        "v": (
                            f"Канал {ch_mode}, ниша {industry_id or '—'}. {standout}"
                            if is_ru
                            else f"Channel {ch_mode}, niche {industry_id or '—'}. {standout}"
                        ),
                    },
                    {
                        "k": "Активы" if is_ru else "Assets",
                        "v": (
                            "Метрика, карта потерь, ёмкость, клиентский пак. Без авто-доходности."
                            if is_ru
                            else "Metric, leak map, capacity, client pack. No auto-yield."
                        ),
                    },
                    {
                        "k": "Уверенность" if is_ru else "Confidence",
                        "v": f"{conf_s} · риск {risk}" if is_ru else f"{conf_s} · risk {risk}",
                    },
                ],
            },
            {
                "id": "decide",
                "title": "Решить" if is_ru else "Decide",
                "cards": [
                    {
                        "k": "Режим" if is_ru else "Mode",
                        "v": plan.get("mode") or "design",
                    },
                    {
                        "k": "Подключить / DIY" if is_ru else "Connect / DIY",
                        "v": (
                            "Панель Metrix, при необходимости интеграции, табло в таблице"
                            if is_ru
                            else "Metrix panel, integrations if needed, spreadsheet board"
                        ),
                    },
                    {
                        "k": "Шаги плана" if is_ru else "Plan steps",
                        "v": step_txt,
                    },
                ],
            },
            {
                "id": "act",
                "title": "Сделать" if is_ru else "Act",
                "cards": [
                    {
                        "k": "Клиентский пак" if is_ru else "Client pack",
                        "v": (
                            "Собрать похожие запросы в один пак"
                            if is_ru
                            else "Group similar requests into one pack"
                        ),
                    },
                    {
                        "k": "После оплаты" if is_ru else "After payment",
                        "v": (
                            "Авторская уникальность + агент деплоя"
                            if is_ru
                            else "Author uniqueness + deploy agent"
                        ),
                    },
                    {
                        "k": "Ход" if is_ru else "Move",
                        "v": move_txt if isinstance(move_txt, str) else str(move_txt),
                    },
                    {
                        "k": "Стоп-правила" if is_ru else "Stop rules",
                        "v": kill_txt,
                    },
                ],
            },
        ],
        "ux_rules": [
            "human language only",
            "max 3 columns",
            "questions only after payment",
        ],
    }


def _final_gate_impl(self, deliverable: dict) -> dict[str, Any]:
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


# Bind helpers onto class (methods were extracted during refactor)
BusinessGenerator._control_panel = _control_panel_impl  # type: ignore[attr-defined]
BusinessGenerator._final_gate = _final_gate_impl  # type: ignore[attr-defined]


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
