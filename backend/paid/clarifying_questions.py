"""
Clarifying questions → re-run TZ loop.

Based on missing data from:
  · demo idea
  · paid package / levers / map
  · business structure (modeling language: entities · flows · levers · constraints)
  · informatics business metrics gaps

Natural behaviour: ask only what is needed before re-process, not a fixed form.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


# Modeling language axes for business representation
MODELING_AXES = (
    "entities",  # who: client, developer, platform
    "flows",  # money / compute / content
    "levers",  # what you can turn
    "constraints",  # SLA, custom cloud limits
    "jobs",  # job-to-be-done (write post, ship agent…)
    "metrics",  # numbers that prove control
)


class ClarifyingQuestionEngine:
    """Build prioritized questions + re-run checklist."""

    name = "Clarifying Questions (TZ loop)"

    def build(
        self,
        *,
        business: str,
        industry_id: str,
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        oae: dict[str, Any] | None = None,
        scores: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        metrics = metrics or {}
        decision = decision or {}
        oae = oae or {}
        scores = scores or {}
        # Already-known answers (natural: don't re-ask)
        answered = set()
        for src in (
            metrics.get("numbers_known") or {},
            (metrics.get("_modeling_answers") or {}),
        ):
            answered.update(k for k, v in src.items() if v not in (None, "", []))
        # modeling answers may be passed via paid commercial pre-attach
        ma = (paid.get("_modeling_answers") or {}) if isinstance(paid, dict) else {}
        if isinstance(ma, dict):
            answered.update(k for k, v in ma.items() if v not in (None, "", []))

        pkg = paid.get("package") or {}
        plane = (paid.get("function_engine") or {}).get("output_plane") or {}
        mega = (paid.get("mega_map") or {}).get("comparison") or {}
        missing_nums = list(metrics.get("numbers_missing") or [])
        top_lever = (
            (paid.get("function_engine") or {}).get("top_lever")
            or pkg.get("top_lever")
            or "model_fit"
        )
        top_leak = (metrics.get("top_leak") or {}).get("id") or ""
        readiness = safe_float(plane.get("paid_readiness") or pkg.get("paid_readiness"), 0.4)
        competing = int(mega.get("competing_pairs") or 0)
        status = paid.get("status") or pkg.get("status") or "preview"

        questions: list[dict[str, Any]] = []

        def q(
            qid: str,
            axis: str,
            text: str,
            why: str,
            field: str,
            priority: int,
            required_for: str,
        ) -> None:
            if field in answered:
                return
            questions.append(
                {
                    "id": qid,
                    "modeling_axis": axis,
                    "question": text,
                    "why": why,
                    "answer_field": field,
                    "priority": priority,
                    "required_for": required_for,
                }
            )

        # ── Always: entities ─────────────────────────────────────────────
        q(
            "ent_buyer",
            "entities",
            "Кто платит вам напрямую: разработчик, инфлюенсер, агентство или студия?",
            "Unit economics и оффер зависят от плательщика.",
            "buyer_persona",
            1,
            "commercial_offer",
        )
        q(
            "ent_user",
            "entities",
            "Кто ежедневно жмёт кнопки на вашем cloud (роль, не бренд)?",
            "Delivery friction и rework считаются по реальному user.",
            "end_user_role",
            2,
            "situation_analysis",
        )

        # ── Jobs vs compute ──────────────────────────────────────────────
        if "demand" in top_leak or safe_float(
            (metrics.get("indices") or {}).get("demand_clarity"), 0.5
        ) < 0.55:
            q(
                "job_primary",
                "jobs",
                "Главный job клиента: «получить GPU/compute» или «закрыть workflow "
                "(например, понять/написать пост)»? Можно оба — укажите % выручки.",
                "Demo spine и product surface расходятся без этого.",
                "primary_job_split",
                1,
                "demo_alignment",
            )

        # ── Numbers (style: concrete levers) ─────────────────────────────
        num_priority = {
            "monthly_revenue": (1, "Какая выручка в месяц сейчас (примерно, ₽ или $)?"),
            "monthly_cost": (1, "Себестоимость инфраструктуры в месяц?"),
            "utilization": (1, "Средняя загрузка мощностей 0–100%?"),
            "arpu": (2, "Средний чек / ARPU на клиента в месяц?"),
            "gross_margin": (2, "Грубая валовая маржа 0–100%?"),
            "churn": (2, "Отток клиентов в месяц 0–100%?"),
            "active_clients": (3, "Сколько активных платящих клиентов?"),
            "gpu_hour_price": (2, "Цена за GPU-hour (или unit) для клиента?"),
            "cost_per_gpu_hour": (2, "Ваша cost за GPU-hour?"),
            "dev_rework_rate": (
                2,
                "Какая доля работ уходит в переделки из‑за разработчиков/процесса 0–100%?",
            ),
        }
        for key in missing_nums:
            if key in num_priority:
                pr, text = num_priority[key]
                q(
                    f"num_{key}",
                    "metrics",
                    text,
                    "Без цифр paid package остаётся candidate_preview.",
                    key,
                    pr,
                    "business_numbers",
                )

        # ── Levers ───────────────────────────────────────────────────────
        q(
            "lever_control",
            "levers",
            f"Какие 1–3 рычага дохода вы *реально* крутите сейчас "
            f"(цена, reserved/on-demand, лимиты, SLA)? "
            f"Система сейчас толкает lever «{top_lever}».",
            "Связка FinOps board ↔ ваш биллинг.",
            "active_revenue_levers",
            1,
            "finops_map",
        )
        if top_leak == "revenue_levers_opaque" or revenue_weak(metrics):
            q(
                "lever_blind",
                "levers",
                "Где слепая зона: не видите ROI клиента, не видите utilization, "
                "или не можете менять цену без оттока?",
                "Утечка #1 в situation analysis.",
                "blind_spot",
                1,
                "situation_analysis",
            )

        # ── Flows / constraints ──────────────────────────────────────────
        q(
            "flow_money",
            "flows",
            "Как деньги идут: prepaid compute / monthly reserved / success-share / retainer?",
            "Тариф и payment link в portal.",
            "billing_model",
            1,
            "commercial_offer",
        )
        q(
            "const_custom",
            "constraints",
            "Чем custom cloud жёстче обычного: регион, стек, изоляция, compliance, "
            "шаблоны под creator workflow?",
            "Premium tier и architecture в ТЗ.",
            "custom_constraints",
            2,
            "integration_tz",
        )

        # ── Demo / paid alignment ────────────────────────────────────────
        if idea_title:
            q(
                "demo_fit",
                "jobs",
                f"Идея «{idea_title[:80]}» — это ваш оффер №1 или только демо-набросок? "
                f"Если набросок — как звучит оффер своими словами в 1 фразе?",
                "Package title и portal offer.",
                "offer_one_liner",
                1,
                "commercial_offer",
            )
        if readiness < 0.55 or status in (
            "preview",
            "candidate_preview",
            "preview_founder_review",
        ):
            q(
                "pilot_scope",
                "constraints",
                "Что войдёт в платный пилот на 14–30 дней (результат, метрика успеха, цена)?",
                "Custom paid stage + acceptance criteria.",
                "pilot_definition",
                1,
                "paid_pilot_tz",
            )
        if competing >= 4:
            q(
                "hyp_choose",
                "jobs",
                f"На Mega Map {competing} конкурирующих гипотез. Какая ближе вам: "
                f"«{mega.get('best_label') or pkg.get('best_hypothesis') or 'best'}» "
                f"или своя формулировка?",
                "Снять competing pairs перед quote.",
                "chosen_hypothesis",
                1,
                "mega_map_lock",
            )

        # Integration (standards)
        q(
            "int_stack",
            "constraints",
            "Нужна ли интеграция: billing API, Telegram/CRM, auth SSO, "
            "GPU orchestrator (k8s/slurm), webhooks?",
            "Standard integration specs в ТЗ.",
            "integration_targets",
            2,
            "integration_tz",
        )

        # Sort by priority then keep unique
        questions.sort(key=lambda x: (x["priority"], x["id"]))
        seen: set[str] = set()
        uniq: list[dict[str, Any]] = []
        for item in questions:
            if item["id"] in seen:
                continue
            seen.add(item["id"])
            uniq.append(item)

        # Cap for natural UX — top 8 must-ask, rest optional
        must = [x for x in uniq if x["priority"] == 1][:8]
        nice = [x for x in uniq if x["priority"] > 1][:6]

        coverage = metrics.get("numbers_coverage")
        if coverage is None:
            coverage = 0.0
        # Questions gap ≠ package readiness (readiness is a separate paid gate)
        answers_complete = len(must) == 0 and safe_float(coverage) >= 0.5
        re_run_recommended = len(must) > 0 or safe_float(coverage) < 0.35
        re_run_ready = answers_complete  # ready to re-run for better score, not "done selling"

        return {
            "module": self.name,
            "modeling_axes": list(MODELING_AXES),
            "must_ask": must,
            "optional": nice,
            "all_questions": uniq,
            "must_count": len(must),
            "re_run_recommended": re_run_recommended,
            "re_run_ready": re_run_ready,
            "answers_complete": answers_complete,
            "paid_readiness_gate": readiness,
            "re_run_instruction": (
                "Ответьте на must_ask (можно JSON business_numbers + extra fields), "
                "затем POST /api/v1/process с теми же industry/business + answers "
                "в extra_params / success_metrics.business_numbers."
            ),
            "answer_template": {
                "extra_params": {
                    "utilization": 0.0,
                    "gross_margin": 0.0,
                    "churn": 0.0,
                },
                "success_metrics": {
                    "business_numbers": {
                        "monthly_revenue": None,
                        "monthly_cost": None,
                        "arpu": None,
                        "active_clients": None,
                        "gpu_hour_price": None,
                        "cost_per_gpu_hour": None,
                        "dev_rework_rate": None,
                    }
                },
                "modeling_answers": {
                    "buyer_persona": "",
                    "end_user_role": "",
                    "primary_job_split": "",
                    "active_revenue_levers": "",
                    "billing_model": "",
                    "offer_one_liner": "",
                    "pilot_definition": "",
                    "chosen_hypothesis": "",
                    "integration_targets": "",
                    "custom_constraints": "",
                },
            },
            "summary": (
                f"Must-ask={len(must)}, optional={len(nice)}; "
                f"re_run_recommended={not re_run_ready}; top_lever={top_lever}."
            ),
        }


def revenue_weak(metrics: dict[str, Any]) -> bool:
    idx = metrics.get("indices") or {}
    return safe_float(idx.get("revenue_control_index"), 0.5) < 0.45
