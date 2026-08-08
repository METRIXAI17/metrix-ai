"""
Funding pack — fourth public mode / capital tariff.

Three pillars:
  1. Structural auto-income — OUTPUT + instant revenue levers
  2. Assets 1:1 — rental or % on configured sales
  3. Capital cooperation — partner loops with placed capital
"""

from __future__ import annotations

from typing import Any

from backend.monetization.structural_income import StructuralIncomeEngine
from backend.monetization.asset_attach import AssetAttachEngine
from backend.monetization.capital_coop import CapitalCoopEngine


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def build_funding_pack(
    business_text: str,
    *,
    project_name: str = "",
    capital_usd: float | None = None,
    partner_role: str = "hybrid",
    asset_mode: str = "auto",
    industry_id: str = "",
    lang: str = "ru",
) -> dict[str, Any]:
    L = _lang(lang)
    name = project_name or (business_text or "")[:60] or "Funding"

    p1 = StructuralIncomeEngine().build(
        business_text,
        project_name=name,
        capital_hint_usd=capital_usd,
        lang=L,
    )
    p2 = AssetAttachEngine().build(
        business_text,
        project_name=name,
        preferred_mode=asset_mode,
        lang=L,
    )
    p3 = CapitalCoopEngine().build(
        business_text,
        project_name=name,
        capital_usd=capital_usd,
        partner_role=partner_role,
        lang=L,
    )

    launch = _launch_path(L, p1, p2, p3)
    pillars_ui = [
        {
            "id": "p1_structural",
            "title": _d(L, "1. Структурный авто-доход", "1. Structural auto-income"),
            "promise": p1["thesis"],
            "steps": p1.get("setup_steps") or [],
            "kpi": _d(
                L,
                f"Band ${p1['income_band']['monthly_structural_low']}–"
                f"${p1['income_band']['monthly_structural_high']}/mo (механика, не promise)",
                f"Band ${p1['income_band']['monthly_structural_low']}–"
                f"${p1['income_band']['monthly_structural_high']}/mo (mechanics, not promise)",
            ),
            "kill": (p1.get("anti_promises") or [""])[0],
            "levers": p1.get("instant_levers") or [],
            "meta": p1.get("output_map") or {},
        },
        {
            "id": "p2_assets",
            "title": _d(L, "2. Активы 1:1", "2. Assets 1:1"),
            "promise": p2["thesis"],
            "steps": p2.get("playbook") or [],
            "kpi": _d(
                L,
                f"Mode={p2.get('mode')} · {len(p2.get('attachments') or [])} attach",
                f"Mode={p2.get('mode')} · {len(p2.get('attachments') or [])} attaches",
            ),
            "kill": _d(
                L,
                "Нет auto-yield; idle >40% → cut attach",
                "No auto-yield; idle >40% → cut attach",
            ),
            "attachments": p2.get("attachments") or [],
            "rules": p2.get("rules") or [],
        },
        {
            "id": "p3_coop",
            "title": _d(L, "3. Кооперация капитала", "3. Capital cooperation"),
            "promise": p3["thesis"],
            "steps": [
                step
                for loop in (p3.get("coop_loops") or [])
                for step in (loop.get("steps") or [])
            ][:8],
            "kpi": _d(
                L,
                f"Ready {p3['readiness']['score']:.0%} · gate={p3['readiness']['gate']}",
                f"Ready {p3['readiness']['score']:.0%} · gate={p3['readiness']['gate']}",
            ),
            "kill": p3["readiness"].get("message") or "",
            "slots": p3.get("placement_slots") or [],
            "partner_pack": p3.get("partner_pack") or {},
            "next_actions": p3.get("next_actions") or [],
        },
    ]

    return {
        "module": "FundingPack",
        "status": "live",
        "project": name,
        "industry_id": industry_id or "",
        "lang": L,
        "tariff": {
            "id": "capital",
            "name": _d(L, "Фандинг · 3 столпа", "Funding · 3 pillars"),
            "tagline": _d(
                L,
                "Структурный доход · активы 1:1 · кооперация размещённого капитала",
                "Structural income · assets 1:1 · placed-capital cooperation",
            ),
            "price_label": _d(L, "Партнёрский контур", "Partner contour"),
        },
        "pillars": pillars_ui,
        "raw": {"structural": p1, "assets": p2, "capital_coop": p3},
        "launch_path": launch,
        "paid_quickstart": _paid_quickstart(L),
        "summary": _d(
            L,
            f"Funding · {name}: 3 столпа · top lever="
            f"{(p1.get('instant_levers') or [{}])[0].get('id', '—')} · "
            f"gate={p3['readiness']['gate']}",
            f"Funding · {name}: 3 pillars · top lever="
            f"{(p1.get('instant_levers') or [{}])[0].get('id', '—')} · "
            f"gate={p3['readiness']['gate']}",
        ),
    }


def _launch_path(
    L: str,
    p1: dict[str, Any],
    p2: dict[str, Any],
    p3: dict[str, Any],
) -> list[dict[str, str]]:
    gate = (p3.get("readiness") or {}).get("gate") or "structure_first"
    top = (p1.get("instant_levers") or [{}])[0].get("id", "orient_run")
    return [
        {
            "n": "01",
            "title": _d(L, "Бесплатно · карта", "Free · map"),
            "text": _d(
                L,
                "Эта форма уже собрала 3 столпа. Сохрани summary + top lever.",
                "This form already built 3 pillars. Save summary + top lever.",
            ),
            "cta": "funding",
        },
        {
            "n": "02",
            "title": _d(L, "Включить lever", "Wire lever"),
            "text": _d(
                L,
                f"Primary lever «{top}»: CTA на сайте / в DM = Generate или Consult.",
                f"Primary lever «{top}»: site/DM CTA = Generate or Consult.",
            ),
            "cta": "generate" if top in ("orient_run", "consult_tech") else "request",
        },
        {
            "n": "03",
            "title": _d(L, "1:1 attach", "1:1 attach"),
            "text": _d(
                L,
                f"После первой продажи — attach mode={p2.get('mode')} "
                f"({len(p2.get('attachments') or [])} кандидатов).",
                f"After first sale — attach mode={p2.get('mode')} "
                f"({len(p2.get('attachments') or [])} candidates).",
            ),
            "cta": "request",
        },
        {
            "n": "04",
            "title": _d(L, "Капитал / партнёр", "Capital / partner"),
            "text": _d(
                L,
                f"Gate={gate}. "
                + (
                    "Сначала evidence (orient + numbers)."
                    if gate != "partner_ready"
                    else "Можно открывать partner pack."
                ),
                f"Gate={gate}. "
                + (
                    "Evidence first (orient + numbers)."
                    if gate != "partner_ready"
                    else "Open partner pack."
                ),
            ),
            "cta": "partner" if gate == "partner_ready" else "request",
        },
    ]


def _paid_quickstart(L: str) -> dict[str, Any]:
    return {
        "title": _d(L, "Платная часть — простой запуск", "Paid part — simple launch"),
        "one_liner": _d(
            L,
            "Бесплатно собираешь карту → платишь только когда утверждаешь внедрение / orientation.",
            "Free map first → pay only when you approve implementation / orientation.",
        ),
        "steps": [
            {
                "id": "free_map",
                "label": _d(L, "1. Funding form (сейчас)", "1. Funding form (now)"),
                "action": _d(
                    L,
                    "POST /api/v1/analytics/funding-pack — 3 столпа + launch path",
                    "POST /api/v1/analytics/funding-pack — 3 pillars + launch path",
                ),
                "result": _d(
                    L,
                    "JSON: pillars, levers, slots, next actions",
                    "JSON: pillars, levers, slots, next actions",
                ),
                "price": "free",
            },
            {
                "id": "free_surfaces",
                "label": _d(L, "2. Generate / Consult / Promo", "2. Generate / Consult / Promo"),
                "action": _d(
                    L,
                    "Кнопки в шапке — multi-pass ideas, tech-TZ, promo roads",
                    "Header buttons — multi-pass ideas, tech-TZ, promo roads",
                ),
                "result": _d(L, "Public pack + free-work phases", "Public pack + free-work phases"),
                "price": "free",
            },
            {
                "id": "paid_orient",
                "label": _d(L, "3. Orientation Run", "3. Orientation Run"),
                "action": _d(
                    L,
                    "После go-ahead: paid core / orientation · DM @karimmetrix",
                    "After go-ahead: paid core / orientation · DM @karimmetrix",
                ),
                "result": _d(
                    L,
                    "Axes + situation metrics + commercial offer card",
                    "Axes + situation metrics + commercial offer card",
                ),
                "price": "$290 seed",
            },
            {
                "id": "paid_pilot",
                "label": _d(L, "4. Pilot 14–30d", "4. Pilot 14–30d"),
                "action": _d(
                    L,
                    "Hypothesis locked + numbers → pilot gate (ops)",
                    "Hypothesis locked + numbers → pilot gate (ops)",
                ),
                "result": _d(L, "Live assist + mid checkpoint", "Live assist + mid checkpoint"),
                "price": "$1490 seed",
            },
            {
                "id": "attach_coop",
                "label": _d(L, "5. Attach + capital coop", "5. Attach + capital coop"),
                "action": _d(
                    L,
                    "Активы 1:1 и partner pack — только после 1 proof cycle",
                    "Assets 1:1 and partner pack — only after 1 proof cycle",
                ),
                "result": _d(L, "Rental/% ledger + capital slots", "Rental/% ledger + capital slots"),
                "price": _d(L, "по attach / партнёрский контур", "per attach / partner contour"),
            },
        ],
        "how_to_read_results": [
            _d(
                L,
                "Смотри pillars[].steps — это твой чеклист на неделю.",
                "Read pillars[].steps — your weekly checklist.",
            ),
            _d(
                L,
                "instant_levers: role=primary — что ставить в CTA.",
                "instant_levers: role=primary — what to put in CTA.",
            ),
            _d(
                L,
                "readiness.gate: structure_first | build_evidence | partner_ready.",
                "readiness.gate: structure_first | build_evidence | partner_ready.",
            ),
            _d(
                L,
                "launch_path + paid_quickstart — порядок без догадок.",
                "launch_path + paid_quickstart — order without guessing.",
            ),
        ],
        "ops_endpoints": [
            "POST /api/v1/analytics/funding-pack",
            "POST /api/v1/analytics/promotion-pack",
            "POST /api/v1/analytics/business-generate",
            "POST /api/v1/process",
            "POST /api/v1/analytics/paid-core",
            "GET  /api/v1/analytics/capital-efficiency",
        ],
        "contact": "https://x.com/karimmetrix",
    }
