"""
Informatics business metrics — situation analysis for the paid layer.

Style: plain, lever-oriented, “where money leaks” — matches Metrix / founder
narrative (control of revenue levers, custom cloud, delivery friction).

Not accounting software: transparent formulas from text signals + optional
numeric fields the client can fill later (OPEN: live billing feed).
"""

from __future__ import annotations

import re
from typing import Any

from backend.paid.types import clamp01, safe_float

# Optional numeric fields (extra_params or success_metrics.business_numbers)
KNOWN_NUMBER_KEYS = (
    "monthly_revenue",
    "monthly_cost",
    "arpu",
    "utilization",  # 0..1
    "churn",  # 0..1
    "active_clients",
    "gpu_hour_price",
    "cost_per_gpu_hour",
    "dev_rework_rate",  # 0..1
    "gross_margin",  # 0..1
)


def _text_hits(text: str, words: tuple[str, ...]) -> int:
    t = text.lower()
    return sum(1 for w in words if w in t)


def _extract_soft_numbers(text: str) -> dict[str, float]:
    """Very light regex hints from free text (not full NLP)."""
    out: dict[str, float] = {}
    # "utilization 40%" / "загрузка 40%"
    m = re.search(r"(?:util|загруз)\w*\s*[:=]?\s*(\d{1,3})\s*%", text, re.I)
    if m:
        out["utilization"] = clamp01(int(m.group(1)) / 100.0)
    m = re.search(r"(?:churn|отток)\w*\s*[:=]?\s*(\d{1,3})\s*%", text, re.I)
    if m:
        out["churn"] = clamp01(int(m.group(1)) / 100.0)
    m = re.search(r"(?:margin|марж)\w*\s*[:=]?\s*(\d{1,3})\s*%", text, re.I)
    if m:
        out["gross_margin"] = clamp01(int(m.group(1)) / 100.0)
    return out


class BusinessMetricsAnalyzer:
    """
    Main situation analysis for paid path.

    Outputs:
      · revenue_control_index  — do you control client/dev income levers?
      · delivery_friction      — rework / “dumb developer” / process noise
      · cloud_fit_premium      — specialty cloud vs generic hyperscaler
      · margin_pressure        — cost vs price pressure
      · demand_clarity         — is buyer job clear (e.g. write a post)?
      · situation_score        — composite health of the money machine
      · leak_map               — ranked where money leaks
    """

    name = "Informatics Business Metrics"

    def analyze(
        self,
        *,
        business: str,
        industry_id: str,
        scores: dict[str, float] | None = None,
        axes: dict[str, float] | None = None,
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
        success: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scores = {k: safe_float(v) for k, v in (scores or {}).items()}
        axes = {k: safe_float(v) for k, v in (axes or {}).items()}
        paid = paid or {}
        extra = dict(extra_params or {})
        # numbers may live under success.business_numbers
        success = success or {}
        bn = dict(success.get("business_numbers") or {})
        for k, v in bn.items():
            extra.setdefault(k, v)
        soft = _extract_soft_numbers(business)
        for k, v in soft.items():
            extra.setdefault(k, v)

        text = f"{business} {idea_title}".lower()

        # Signal packs (RU + EN) — style: levers, income, custom cloud, devs
        ctrl_hits = _text_hits(
            text,
            (
                "рычаг",
                "lever",
                "контрол",
                "control",
                "доход",
                "revenue",
                "марж",
                "margin",
                "arpu",
                "unit",
                "finops",
            ),
        )
        fric_hits = _text_hits(
            text,
            (
                "туп",
                "передел",
                "rework",
                "баг",
                "bug",
                "срыв",
                "delay",
                "не понимаю",
                "хаос",
                "chaos",
                "разработ",
            ),
        )
        cloud_hits = _text_hits(
            text,
            (
                "облак",
                "cloud",
                "gpu",
                "compute",
                "мощност",
                "workload",
                "edge",
                "hosting",
                "кастом",
            ),
        )
        demand_hits = _text_hits(
            text,
            (
                "пост",
                "post",
                "креатив",
                "creative",
                "инфлюен",
                "influencer",
                "workflow",
                "процесс",
                "контент",
            ),
        )
        pain_income = _text_hits(
            text,
            ("мало", "падает", "пада", "low", "drop", "убыт", "loss", "дешев"),
        )

        # Base from orientation
        readiness = scores.get("readiness", 0.5)
        product_fit = scores.get("product_fit", 0.5)
        model_fit = scores.get("model_fit", 0.5)
        promo_fit = scores.get("promo_fit", 0.5)
        risk = axes.get("risk", 0.35)
        mon = axes.get("monetization_fit", 0.5)
        complexity = axes.get("complexity", 0.45)

        # Explicit numbers if present
        util = extra.get("utilization")
        if util is not None:
            util = clamp01(safe_float(util))
        else:
            util = clamp01(0.35 + 0.3 * product_fit - 0.1 * pain_income)

        churn = extra.get("churn")
        if churn is not None:
            churn = clamp01(safe_float(churn))
        else:
            churn = clamp01(0.15 + 0.1 * fric_hits / 4 + 0.15 * risk)

        gm = extra.get("gross_margin")
        if gm is not None:
            gm = clamp01(safe_float(gm))
        else:
            # custom cloud premium vs cost opacity
            gm = clamp01(0.25 + 0.15 * cloud_hits / 4 + 0.2 * mon - 0.1 * pain_income)

        arpu = extra.get("arpu")
        rev = extra.get("monthly_revenue")
        cost = extra.get("monthly_cost")
        if rev is not None and cost is not None and safe_float(rev) > 0:
            gm = clamp01(1.0 - safe_float(cost) / max(1e-6, safe_float(rev)))

        rework = extra.get("dev_rework_rate")
        if rework is not None:
            rework = clamp01(safe_float(rework))
        else:
            rework = clamp01(0.2 + 0.12 * fric_hits / 3 + 0.15 * complexity)

        # Core indices
        revenue_control = clamp01(
            0.25 * (ctrl_hits / 5)
            + 0.25 * model_fit
            + 0.2 * mon
            + 0.15 * (1.0 - churn)
            + 0.15 * readiness
            - 0.1 * pain_income / 3
        )
        delivery_friction = clamp01(
            0.35 * rework + 0.25 * (fric_hits / 5) + 0.2 * complexity + 0.2 * risk
        )
        cloud_fit_premium = clamp01(
            0.3 * (cloud_hits / 5)
            + 0.25 * product_fit
            + 0.2 * util
            + 0.15 * gm
            + 0.1 * (1.0 if industry_id in ("cloud-economy", "chipmaking") else 0.4)
        )
        margin_pressure = clamp01(
            0.4 * (1.0 - gm) + 0.25 * (1.0 - util) + 0.2 * pain_income / 3 + 0.15 * risk
        )
        demand_clarity = clamp01(
            0.35 * (demand_hits / 5)
            + 0.25 * product_fit
            + 0.2 * promo_fit
            + 0.2 * readiness
        )

        # Paid plane feedback
        plane = (paid.get("function_engine") or {}).get("output_plane") or {}
        paid_ready = safe_float(plane.get("paid_readiness"), 0.4)
        top_lever = (paid.get("function_engine") or {}).get("top_lever") or "model_fit"

        situation = clamp01(
            0.22 * revenue_control
            + 0.18 * (1.0 - delivery_friction)
            + 0.18 * cloud_fit_premium
            + 0.15 * (1.0 - margin_pressure)
            + 0.15 * demand_clarity
            + 0.12 * paid_ready
        )

        leaks = [
            {
                "id": "revenue_levers_opaque",
                "label": "Рычаги дохода непрозрачны",
                "severity": round(1.0 - revenue_control, 4),
                "fix": (
                    "Нет явной связки: действие клиента/разработчика → метрика → ваш счёт"
                ),
            },
            {
                "id": "delivery_friction",
                "label": "Трение поставки / качество dev",
                "severity": round(delivery_friction, 4),
                "fix": "Rework и хаос процессов съедают маржу specialty cloud",
            },
            {
                "id": "margin_pressure",
                "label": "Давление на маржу",
                "severity": round(margin_pressure, 4),
                "fix": "Utilization / price / cost не сведены в margin bands",
            },
            {
                "id": "demand_job_unclear",
                "label": "Job-to-be-done покупателя размыт",
                "severity": round(1.0 - demand_clarity, 4),
                "fix": "«Написать пост» vs «аренда GPU» — разные product surfaces",
            },
            {
                "id": "specialty_cloud_underpriced",
                "label": "Specialty cloud недооценён",
                "severity": round(
                    clamp01(0.5 * cloud_fit_premium * margin_pressure + 0.2 * pain_income / 3),
                    4,
                ),
                "fix": "Кастом под workflow не упакован в premium tier + FinOps board",
            },
        ]
        leaks.sort(key=lambda x: x["severity"], reverse=True)

        numbers_known = {
            k: extra[k] for k in KNOWN_NUMBER_KEYS if k in extra and extra[k] is not None
        }
        numbers_missing = [k for k in KNOWN_NUMBER_KEYS if k not in numbers_known]

        narrative = (
            f"Ситуация score={situation:.0%}. "
            f"Контроль рычагов дохода={revenue_control:.0%}, "
            f"трение поставки={delivery_friction:.0%}, "
            f"cloud fit premium={cloud_fit_premium:.0%}, "
            f"давление маржи={margin_pressure:.0%}. "
            f"Главная утечка: {leaks[0]['label']}. "
            f"Paid lever сейчас: «{top_lever}»."
        )

        return {
            "module": self.name,
            "situation_score": round(situation, 4),
            "indices": {
                "revenue_control_index": round(revenue_control, 4),
                "delivery_friction": round(delivery_friction, 4),
                "cloud_fit_premium": round(cloud_fit_premium, 4),
                "margin_pressure": round(margin_pressure, 4),
                "demand_clarity": round(demand_clarity, 4),
                "paid_readiness_echo": round(paid_ready, 4),
            },
            "estimated_operating": {
                "utilization": round(util, 4),
                "churn": round(churn, 4),
                "gross_margin": round(gm, 4),
                "dev_rework_rate": round(rework, 4),
                "arpu": arpu,
                "monthly_revenue": rev,
                "monthly_cost": cost,
                "source": "mixed_explicit_and_estimated",
            },
            "leak_map": leaks,
            "top_leak": leaks[0],
            "top_lever_from_paid": top_lever,
            "numbers_known": numbers_known,
            "numbers_missing": numbers_missing,
            "numbers_coverage": round(
                len(numbers_known) / max(1, len(KNOWN_NUMBER_KEYS)), 4
            ),
            "signal_hits": {
                "control": ctrl_hits,
                "friction": fric_hits,
                "cloud": cloud_hits,
                "demand": demand_hits,
                "income_pain": pain_income,
            },
            "narrative": narrative,
            "open_point": (
                "OPEN: подключить live billing / utilization API — "
                "сейчас soft extract + estimates"
            ),
            "summary": narrative,
        }
