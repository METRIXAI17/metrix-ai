"""
Tangible extract from paid core — what you can sell / ship / show.

Maps abstract paid analysis into concrete artifacts for earning:
  orientation pack, pilot TZ, commercial offer, portal payload, etc.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


# Default Metrix showcase tariffs (seed; override via config later)
TARIFF_CATALOG = [
    {
        "id": "orient_run",
        "name": "Orientation Run (paid unit)",
        "price_usd": 290,
        "includes": [
            "Axes + demo idea + OAE bridge",
            "Paid core 16-step preview",
            "Must-ask questions + situation metrics",
        ],
        "best_for": "First paid contact / diagnose revenue levers",
    },
    {
        "id": "pilot_14",
        "name": "Paid Pilot 14–30d",
        "price_usd": 1490,
        "includes": [
            "Chosen hypothesis locked",
            "FinOps or margin-band implement scaffold",
            "Integration standards in TZ",
            "Mid-pilot checkpoint",
        ],
        "best_for": "When candidate_preview → ready with numbers filled",
    },
    {
        "id": "full_package",
        "name": "Full Package (Product · Models · Promo)",
        "price_usd": 2490,
        "includes": [
            "All fin-model general paid stages",
            "Promo + market-making spine",
            "Custom positioning + portal offer",
        ],
        "best_for": "Showcase / agency delivery stack",
    },
    {
        "id": "custom_cloud_finops",
        "name": "Custom Cloud FinOps Board",
        "price_usd": 1890,
        "includes": [
            "Signal board + decision owners",
            "Margin bands reserved/on-demand/edge",
            "Billing metering hooks (standard spec)",
        ],
        "best_for": "cloud-economy specialty hosts (your style)",
    },
]


class TangibleExtractor:
    """Build sellable / shippable list from paid + metrics + offer context."""

    name = "Tangible Paid Extract"

    def extract(
        self,
        *,
        industry_id: str,
        idea_title: str,
        paid: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        questions: dict[str, Any] | None = None,
        specs: dict[str, Any] | None = None,
        monetization: dict[str, Any] | None = None,
        fin_models: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        metrics = metrics or {}
        questions = questions or {}
        specs = specs or {}
        monetization = monetization or {}
        fin_models = fin_models or []
        pkg = paid.get("package") or {}
        status = paid.get("status") or pkg.get("status") or "preview"
        score = safe_float(paid.get("paid_score"), 0.0)
        readiness = safe_float(pkg.get("paid_readiness"), 0.0)
        top_lever = pkg.get("top_lever") or (paid.get("function_engine") or {}).get(
            "top_lever"
        )
        best = pkg.get("best_hypothesis") or "—"
        leak = (metrics.get("top_leak") or {}).get("label") or "—"

        # Recommend tariff
        if industry_id == "cloud-economy" and (
            "finops" in str(best).lower() or "margin" in idea_title.lower()
        ):
            primary_tariff = "custom_cloud_finops"
        elif status in ("packageable", "ready") and readiness >= 0.55:
            primary_tariff = "pilot_14"
        elif score >= 0.55:
            primary_tariff = "orient_run"
        else:
            primary_tariff = "orient_run"

        tariff = next(t for t in TARIFF_CATALOG if t["id"] == primary_tariff)

        # Payment link placeholder (no real PSP yet)
        payment = {
            "provider": "placeholder",
            "checkout_url": f"/app/paid-portal.html?tariff={tariff['id']}&pay=1",
            "status": "link_ready_ui_only",
            "note": "OPEN: Stripe/YooKassa keys — wire when commercial go-live",
        }

        artifacts = [
            {
                "id": "art_demo_idea",
                "kind": "document",
                "title": f"Demo idea: {idea_title}",
                "how_to_use": "Показать клиенту как free spine; upsell orientation/pilot",
                "earn": "Lead magnet → paid orientation",
            },
            {
                "id": "art_situation",
                "kind": "analysis",
                "title": "Situation metrics + leak map",
                "payload_ref": "business_metrics",
                "how_to_use": "Диагностика «где течёт деньги» на созвоне",
                "earn": "Justification for pilot price",
            },
            {
                "id": "art_paid_package",
                "kind": "package",
                "title": pkg.get("title") or "Paid package",
                "status": status,
                "how_to_use": "Каркас commercial offer + portal",
                "earn": f"Sell {tariff['name']} @ ${tariff['price_usd']}",
            },
            {
                "id": "art_best_hyp",
                "kind": "decision",
                "title": f"Best hypothesis: {best}",
                "how_to_use": "Зафиксировать scope пилота",
                "earn": "Reduces discounting from competing narratives",
            },
            {
                "id": "art_lever",
                "kind": "parameter",
                "title": f"Top lever: {top_lever}",
                "how_to_use": "План работ на 2 недели — крутить один рычаг",
                "earn": "Faster time-to-value → easier close",
            },
            {
                "id": "art_questions",
                "kind": "tz_loop",
                "title": f"Must-ask × {questions.get('must_count', 0)}",
                "how_to_use": "Собрать answers → re-run process → packageable",
                "earn": "Higher conversion after numbers exist",
            },
            {
                "id": "art_specs",
                "kind": "tz",
                "title": "Integration / product standards block",
                "payload_ref": "integration_specs.tz_block",
                "how_to_use": "Вставить в ТЗ пилота as acceptance",
                "earn": "Less scope creep; billable implement",
            },
            {
                "id": "art_reader",
                "kind": "narrative",
                "title": "Reader plain summary",
                "how_to_use": "Email / portal human text",
                "earn": "Trust; lower sales friction",
            },
        ]

        # Fin model deliverables as sellable lines
        for fm in fin_models[:3]:
            ts = fm.get("three_stage") or {}
            gen = ts.get("stage2_general_paid") or {}
            artifacts.append(
                {
                    "id": f"art_fm_{fm.get('model_id')}",
                    "kind": "fin_model",
                    "title": fm.get("model_name"),
                    "deliverables": gen.get("deliverables") or gen.get("bullets") or [],
                    "how_to_use": "General paid line items in offer",
                    "earn": f"Attach to package (model IROI={fm.get('info_roi')})",
                }
            )

        earn_playbook = [
            {
                "step": 1,
                "action": "Продать Orientation Run",
                "price_usd": 290,
                "uses": ["art_demo_idea", "art_situation", "art_questions"],
            },
            {
                "step": 2,
                "action": "Закрыть must-ask + numbers → re-run",
                "price_usd": 0,
                "uses": ["art_questions"],
            },
            {
                "step": 3,
                "action": f"Закрыть {tariff['name']}",
                "price_usd": tariff["price_usd"],
                "uses": ["art_paid_package", "art_best_hyp", "art_specs", "art_lever"],
            },
            {
                "step": 4,
                "action": "Full package / retainers if promo+MM fit",
                "price_usd": 2490,
                "uses": ["art_fm_*", "monetization"],
            },
        ]

        commercial = {
            "headline": pkg.get("title") or f"Paid path · {idea_title}",
            "status": status,
            "paid_score": score,
            "client_problem": leak,
            "proposed_solution": best,
            "top_lever": top_lever,
            "tariff": tariff,
            "tariff_catalog": TARIFF_CATALOG,
            "payment": payment,
            "stack_hint": monetization.get("summary"),
            "next_human_step": (
                (questions.get("must_ask") or [{}])[0].get("question")
                if questions.get("re_run_recommended")
                else "Open paid portal and send offer link"
            ),
            "validity_note": "Seed pricing for Metrix showcase — adjust per client.",
        }

        return {
            "module": self.name,
            "artifacts": artifacts,
            "earn_playbook": earn_playbook,
            "commercial_offer": commercial,
            "primary_tariff_id": primary_tariff,
            "what_you_can_sell_now": [
                a for a in artifacts if a["id"] in (
                    "art_demo_idea",
                    "art_situation",
                    "art_paid_package",
                    "art_questions",
                )
            ],
            "blocked_until_numbers": readiness < 0.55 or status in (
                "preview",
                "candidate_preview",
            ),
            "summary": (
                f"Sell-now: orientation + diagnosis; primary tariff={tariff['id']} "
                f"${tariff['price_usd']}; blocked_until_numbers={readiness < 0.55}."
            ),
        }
