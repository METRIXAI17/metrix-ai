"""
Human-light planner — recognizes situation, branches, commits like a calm operator.
Not a chatbot script: sparse questions, explicit assumptions, reversible commits.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.core.knowledge_synthesis.side_engines import UncertaintyBudgetEngine


@dataclass
class PlanStep:
    id: str
    title: str
    intent: str
    needs_human: bool
    options: list[dict[str, str]] = field(default_factory=list)
    default_option: str = ""
    rationale: str = ""
    reversible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HumanPlan:
    recognition: str
    mode: str
    steps: list[PlanStep]
    open_questions: list[str]
    assumptions: list[str]
    commit_ready: bool
    narrative: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["steps"] = [s.to_dict() if hasattr(s, "to_dict") else s for s in self.steps]
        return d


class HumanLightPlanner:
    """
    Recognize → Branch → Ask sparse → Commit default → Verify.

    Modes: explore | design | execute | recovery
    """

    name = "HumanLightPlanner"

    DOMAIN_PATTERNS: list[tuple[str, list[str]]] = [
        ("resource_logistics", [
            r"переработ", r"вторсырь", r"отход", r"логист", r"recycl", r"scrap",
            r"склад", r"тонн", r"мусор", r"металлолом", r"plastic", r"waste",
        ]),
        ("service_b2c", [
            r"услуг", r"консьерж", r"b2c", r"клиент", r"запис", r"salon", r"service",
        ]),
        ("agency_ops", [
            r"агентств", r"delivery", r"переделк", r"handoff", r"студи", r"agency",
        ]),
        ("content_monetize", [
            r"контент", r"аудитор", r"подпис", r"creator", r"youtube", r"блог",
        ]),
        ("asset_decision", [
            r"актив", r"капитал", r"портфел", r"asset", r"инвест", r"решени",
        ]),
    ]

    def recognize(self, business_text: str) -> tuple[str, str]:
        t = (business_text or "").lower()
        for domain, pats in self.DOMAIN_PATTERNS:
            if any(re.search(p, t) for p in pats):
                return domain, f"Ситуация распознана как «{domain}» по маркерам в брифе."
        words = len(re.findall(r"\w+", t))
        if words < 25:
            return "thin_brief", "Бриф тонкий — режим explore: сначала собрать кости, не строить дворец."
        return "generic_ops", "Общий ops/product контур — планируем как сервисный бизнес с метрикой."

    def plan(
        self,
        business_text: str,
        *,
        lang: str = "ru",
        answers: dict[str, str] | None = None,
        approved_options: dict[str, str] | None = None,
    ) -> HumanPlan:
        answers = answers or {}
        approved = approved_options or {}
        domain, recognition = self.recognize(business_text)
        unc = UncertaintyBudgetEngine().run(business_text, answers=answers)

        # mode selection
        if domain == "thin_brief" or unc.confidence < 0.4:
            mode = "explore"
        elif unc.confidence < 0.65:
            mode = "design"
        elif any(k in answers for k in ("success_metric", "who_pays")):
            mode = "execute"
        else:
            mode = "design"

        steps: list[PlanStep] = []

        # Step 1: direction
        dir_opts = self._direction_options(domain, lang)
        steps.append(
            PlanStep(
                id="S1_direction",
                title="Направление" if lang == "ru" else "Direction",
                intent="Pick primary value chain",
                needs_human=True,
                options=dir_opts,
                default_option=approved.get("S1_direction") or dir_opts[0]["id"],
                rationale="Без направления остальные шаги — шум.",
            )
        )

        # Step 2: unit economics skeleton
        steps.append(
            PlanStep(
                id="S2_unit",
                title="Единица ценности" if lang == "ru" else "Unit of value",
                intent="Define billable unit + first cash path",
                needs_human=True,
                options=self._unit_options(domain, lang),
                default_option=approved.get("S2_unit") or "unit_order",
                rationale="Единица = якорь метрик и оффера.",
            )
        )

        # Step 3: channel
        steps.append(
            PlanStep(
                id="S3_channel",
                title="Первый канал" if lang == "ru" else "First channel",
                intent="One channel that can produce a paid test",
                needs_human=True,
                options=self._channel_options(domain, lang),
                default_option=approved.get("S3_channel") or "ch_network",
                rationale="Один канал лучше пяти «стратегий».",
            )
        )

        # Step 4: pilot metric
        steps.append(
            PlanStep(
                id="S4_metric",
                title="Метрика пилота" if lang == "ru" else "Pilot metric",
                intent="Single success metric + kill criteria",
                needs_human=True,
                options=self._metric_options(domain, lang),
                default_option=approved.get("S4_metric") or "m_margin",
                rationale="Если нельзя измерить за 14–21 день — не пилот.",
            )
        )

        # Step 5: assembly (system)
        steps.append(
            PlanStep(
                id="S5_assembly",
                title="Сборка системы" if lang == "ru" else "System assembly",
                intent="Compose expert base + ops panel + code pack",
                needs_human=False,
                options=[{"id": "auto", "label": "Автосборка из согласованных компонентов"}],
                default_option="auto",
                rationale="После S1–S4 система пишет артефакты без лишних вопросов.",
                reversible=True,
            )
        )

        # Step 6: verify
        steps.append(
            PlanStep(
                id="S6_verify",
                title="Самопроверка" if lang == "ru" else "Self-verify",
                intent="Run uncertainty re-check + human-reaction forecast + fix",
                needs_human=False,
                options=[{"id": "selftest", "label": "Self-test + pre-correct"}],
                default_option="selftest",
                rationale="Лучше исправить до показа человеку.",
            )
        )

        assumptions = [
            "Клиент владеет рисками и решениями; Metrix даёт ТЗ и опору, не гарантию прибыли.",
            "Пилот = один трек, одна метрика, ограниченное окно.",
            "Оплата внедрения — после подтверждённой ценности (модель «после вашей оплаты» где применимо).",
        ]
        if domain == "resource_logistics":
            assumptions.append(
                "Цепочка: intake → quality → process → logistics → buyer → cash; bottleneck ищем до маркетинга."
            )

        open_q = list(unc.ask_next)
        # if human already approved, strip related questions
        if approved.get("S1_direction"):
            open_q = [q for q in open_q if "канал" not in q.lower() or True]

        commit_ready = mode in ("execute", "design") and unc.confidence >= 0.45
        narrative = self._narrative(domain, mode, recognition, unc.confidence, lang)

        return HumanPlan(
            recognition=recognition,
            mode=mode,
            steps=steps,
            open_questions=open_q,
            assumptions=assumptions,
            commit_ready=commit_ready,
            narrative=narrative,
            confidence=unc.confidence,
        )

    def apply_choices(self, plan: HumanPlan, choices: dict[str, str]) -> HumanPlan:
        for step in plan.steps:
            if step.id in choices:
                step.default_option = choices[step.id]
        plan.commit_ready = all(
            s.default_option for s in plan.steps if s.needs_human
        )
        return plan

    def _narrative(
        self, domain: str, mode: str, recognition: str, conf: float, lang: str
    ) -> str:
        if lang == "en":
            return (
                f"{recognition} Mode={mode}, confidence={conf:.0%}. "
                f"We will ask only for choices that change the architecture, "
                f"then assemble the system as if working from a TZ."
            )
        return (
            f"{recognition} Режим={mode}, уверенность={conf:.0%}. "
            f"На каждом этапе — короткие согласования лучших вариантов. "
            f"После выбора направлений система собирает артефакты как работа по ТЗ."
        )

    def _direction_options(self, domain: str, lang: str) -> list[dict[str, str]]:
        if domain == "resource_logistics":
            return [
                {"id": "rl_collect_sort", "label": "Сбор и сортировка → B2B buyer"},
                {"id": "rl_process_sell", "label": "Переработка + продажа фракций"},
                {"id": "rl_logistics_net", "label": "Логистическая сеть / last-mile для сырья"},
                {"id": "rl_marketplace", "label": "Маркетплейс спроса/предложения вторсырья"},
            ]
        if domain == "service_b2c":
            return [
                {"id": "svc_core", "label": "Базовая услуга + повторные визиты"},
                {"id": "svc_concierge", "label": "Консьерж-пакет поверх базового слоя"},
                {"id": "svc_multi", "label": "Мульти-направление (шаблон услуг)"},
            ]
        return [
            {"id": "ops_fix", "label": "Операционка / delivery"},
            {"id": "product_pack", "label": "Продукт / упаковка оффера"},
            {"id": "promo_angle", "label": "Продвижение / угол продажи"},
            {"id": "full_stack", "label": "Ops + product + promo (узкий пилот)"},
        ]

    def _unit_options(self, domain: str, lang: str) -> list[dict[str, str]]:
        if domain == "resource_logistics":
            return [
                {"id": "unit_ton", "label": "Тонна / кг фракции"},
                {"id": "unit_route", "label": "Рейс / маршрут"},
                {"id": "unit_contract", "label": "Месячный контракт на вывоз"},
            ]
        return [
            {"id": "unit_order", "label": "Оплаченный заказ / проект"},
            {"id": "unit_hour", "label": "Час / слот"},
            {"id": "unit_pack", "label": "Пакет / пилот"},
            {"id": "unit_sub", "label": "Подписка (только если уже proven)"},
        ]

    def _channel_options(self, domain: str, lang: str) -> list[dict[str, str]]:
        return [
            {"id": "ch_network", "label": "Нетворкинг / тёплые контакты"},
            {"id": "ch_platform", "label": "Площадка (Avito/Profi/маркетплейс/отраслевой)"},
            {"id": "ch_brand", "label": "Бренд-контент (X / TG / site)"},
            {"id": "ch_partner", "label": "Партнёрский канал / white-label"},
            {"id": "ch_outbound", "label": "Прямой outbound по lookalike"},
        ]

    def _metric_options(self, domain: str, lang: str) -> list[dict[str, str]]:
        if domain == "resource_logistics":
            return [
                {"id": "m_margin", "label": "Маржа на тонну после логистики"},
                {"id": "m_util", "label": "Утилизация ёмкости / reйс load factor"},
                {"id": "m_cycle", "label": "Цикл cash: intake → money (дни)"},
            ]
        return [
            {"id": "m_margin", "label": "Маржа / unit contribution"},
            {"id": "m_cycle", "label": "Время до первой оплаты"},
            {"id": "m_rework", "label": "Rework hours ↓"},
            {"id": "m_conversion", "label": "Конверсия brief → paid"},
        ]
