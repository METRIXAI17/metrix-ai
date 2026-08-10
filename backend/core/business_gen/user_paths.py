"""
Popular user paths with sophisticated (навороченные) result packs.
"""

from __future__ import annotations

from typing import Any


PATHS: list[dict[str, Any]] = [
    {
        "id": "library_ship",
        "label": "L.path.library_ship",
        "name_ru": "Library → unit → ship",
        "name_en": "Library → unit → ship",
        "match": ("библиотек", "library", "архитект", "карточ", "architecture"),
        "segment_pref": ("b2b_knowledge", "b2b_product"),
        "sophistication": 0.92,
        "spine": ["product_pack", "unit_pack", "ch_network"],
        "result_sections": [
            "identity_1pager",
            "A01_A12_deep_niches",
            "concept_tests_T1_T3",
            "unit_economics_card",
            "live_log_7d",
            "stop_rule_single",
            "gen_v2_v5_slots",
            "acceptance_forecast",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "Genome mix: 3 niche cards × warrants S1–S4 без полной переписи",
                "en": "Genome mix: 3 niche cards × warrants S1–S4 without full rewrite",
            },
            {
                "id": "PA2",
                "ru": "Delight forecast + identity Q hash-unique",
                "en": "Delight forecast + identity Q hash-unique",
            },
            {
                "id": "PA3",
                "ru": "Proof post draft с locked decisions week",
                "en": "Proof post draft with locked decisions week",
            },
        ],
    },
    {
        "id": "agency_margin",
        "label": "L.path.agency_margin",
        "name_ru": "Agency margin recovery",
        "name_en": "Agency margin recovery",
        "match": ("агентств", "agency", "rework", "handoff", "студи"),
        "segment_pref": ("agency", "b2b_ops"),
        "sophistication": 0.88,
        "spine": ["unit_pack", "ch_network", "product_pack"],
        "result_sections": [
            "leak_map",
            "handoff_scoreboard",
            "margin_unit",
            "referral_7d_log",
            "assist_queue",
            "acceptance_forecast",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "Before/after rework hours на одной карточке",
                "en": "Before/after rework hours on one card",
            },
            {
                "id": "PA2",
                "ru": "WIP=3 desk + T-gates calendar",
                "en": "WIP=3 desk + T-gates calendar",
            },
        ],
    },
    {
        "id": "builder_pack",
        "label": "L.path.builder_pack",
        "name_ru": "Builder product pack",
        "name_en": "Builder product pack",
        "match": ("builder", "билдер", "saas", "product", "automat", "workflow"),
        "segment_pref": ("b2b_product", "founder_solo"),
        "sophistication": 0.9,
        "spine": ["product_pack", "unit_pack", "ch_network"],
        "result_sections": [
            "sku_boundary",
            "pilot_widgets_x3",
            "cost_unit",
            "builder_dm_list",
            "gen_voice_pack",
            "robotics_queue",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "Pilot cockpit: uncertainty / risk / next — не 40 KPI",
                "en": "Pilot cockpit: uncertainty / risk / next — not 40 KPIs",
            },
            {
                "id": "PA2",
                "ru": "Robotics harness AG0–AG5 ready for implement",
                "en": "Robotics harness AG0–AG5 ready for implement",
            },
        ],
    },
    {
        "id": "api_cost",
        "label": "L.path.api_cost",
        "name_ru": "API cost cut path",
        "name_en": "API cost cut path",
        "match": ("api", "token", "openai", "anthropic", "llm", "cost"),
        "segment_pref": ("b2b_product", "founder_solo"),
        "sophistication": 0.86,
        "spine": ["product_pack", "unit_pack"],
        "result_sections": [
            "model_routing_matrix",
            "cache_spine",
            "cost_per_accepted",
            "acceptance_forecast",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "$/accepted outcome unit, not vanity tokens",
                "en": "$/accepted outcome unit, not vanity tokens",
            },
        ],
    },
    {
        "id": "expert_sku",
        "label": "L.path.expert_sku",
        "name_ru": "Expert SKU path",
        "name_en": "Expert SKU path",
        "match": ("expert", "эксперт", "consult", "коуч", "пакет"),
        "segment_pref": ("b2b_knowledge", "founder_solo"),
        "sophistication": 0.87,
        "spine": ["product_pack", "unit_pack", "ch_network"],
        "result_sections": [
            "promise_boundary_pack",
            "acceptance_page",
            "single_stop_rule",
            "identity_delight",
            "proof_post",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "90-day pack вместо почасовки — boundaries locked",
                "en": "90-day pack instead of hourly — boundaries locked",
            },
        ],
    },
    {
        "id": "creator_shift",
        "label": "L.path.creator_shift",
        "name_ru": "Creator shift · triple impact",
        "name_en": "Creator shift · triple impact",
        "match": (
            "увлеч",
            "творч",
            "creator",
            "хобби",
            "hobby",
            "произведен",
            "персона",
            "craft",
        ),
        "segment_pref": ("b2b_knowledge", "founder_solo", "b2b_product"),
        "sophistication": 0.93,
        "spine": ["product_pack", "unit_pack", "ch_network"],
        "result_sections": [
            "tmdr_or_analog_core",
            "deep_analysis_friction",
            "executive_s0_s10",
            "situation_promo_funding_weave",
            "triple_impact_report",
            "approve_and_run_api",
            "automations_after_approve",
            "acceptance_forecast",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "Executive S0–S10 + approve gate в UI",
                "en": "Executive S0–S10 + approve gate in UI",
            },
            {
                "id": "PA2",
                "ru": "Situation←promo+funding hooks в axis #1 report",
                "en": "Situation←promo+funding hooks in axis #1 report",
            },
            {
                "id": "PA3",
                "ru": "POST /approve-and-run automations pack",
                "en": "POST /approve-and-run automations pack",
            },
        ],
        "scenarios": ["sc_triple", "sc_approve", "sc_promo_sit"],
    },
    {
        "id": "hobby_lattice",
        "label": "L.path.hobby_lattice",
        "name_ru": "Hobby lattice · rule environments",
        "name_en": "Hobby lattice · rule environments",
        "match": (
            "карточ",
            "каталог",
            "правил",
            "оффер",
            "окружен",
            "catalog",
            "rule env",
            "lattice",
        ),
        "segment_pref": ("b2b_knowledge", "platform"),
        "sophistication": 0.94,
        "spine": ["product_pack", "unit_pack", "ch_network"],
        "result_sections": [
            "rule_environment_catalog",
            "client_packs_weights",
            "deep_analysis",
            "executive_algorithm",
            "promo_copy_board",
            "funding_three_pillars",
            "ship_plan_button",
            "landing_plus_app",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "10+ executable cards: offer + rules + kill + scheme",
                "en": "10+ executable cards: offer + rules + kill + scheme",
            },
            {
                "id": "PA2",
                "ru": "Assembly metrics gate (systemic 3) before ship",
                "en": "Assembly metrics gate (systemic 3) before ship",
            },
        ],
        "scenarios": ["sc_run", "sc_promo_sit", "sc_kill"],
    },
    {
        "id": "api_surface",
        "label": "L.path.api_surface",
        "name_ru": "API surface · approve-and-run",
        "name_en": "API surface · approve-and-run",
        "match": ("api", "webhook", "automat", "approve", "endpoint", "sdk"),
        "segment_pref": ("b2b_product", "platform"),
        "sophistication": 0.91,
        "spine": ["product_pack", "unit_pack"],
        "result_sections": [
            "openapi_surface",
            "analyze_endpoint",
            "approve_and_run",
            "executive_spec_endpoint",
            "webhook_complete",
            "acceptance_forecast",
        ],
        "premium_artifacts": [
            {
                "id": "PA1",
                "ru": "User eyes → approve → automations without reading code",
                "en": "User eyes → approve → automations without reading code",
            },
        ],
        "scenarios": ["sc_api", "sc_approve"],
    },
]


# Scenario library (path-aware)
SCENARIOS: dict[str, dict[str, Any]] = {
    "sc_triple": {
        "ru": "Intake 3 оси → deep analysis → triple impact",
        "en": "3-axis intake → deep analysis → triple impact",
    },
    "sc_approve": {
        "ru": "Preview S0–S6 → human approve → execute S8–S10",
        "en": "Preview S0–S6 → human approve → execute S8–S10",
    },
    "sc_promo_sit": {
        "ru": "Top friction → promo angle + funding lever inside situation",
        "en": "Top friction → promo angle + funding lever inside situation",
    },
    "sc_run": {
        "ru": "Rule card run → unique title + report",
        "en": "Rule card run → unique title + report",
    },
    "sc_kill": {
        "ru": "Kill 14d no proof → rollback angle",
        "en": "Kill 14d no proof → rollback angle",
    },
    "sc_api": {
        "ru": "POST analyze + POST approve-and-run as product surface",
        "en": "POST analyze + POST approve-and-run as product surface",
    },
    "sc_first_card": {
        "ru": "First catalog card free run → proof",
        "en": "First catalog card free run → proof",
    },
    "sc_pack_sell": {
        "ru": "Sell pack after 1 public artifact",
        "en": "Sell pack after 1 public artifact",
    },
    "sc_rework": {
        "ru": "Rework hours → handoff board",
        "en": "Rework hours → handoff board",
    },
    "sc_pilot": {
        "ru": "14d pilot one lever",
        "en": "14d pilot one lever",
    },
    "sc_sku": {
        "ru": "SKU boundary → pilot widgets",
        "en": "SKU boundary → pilot widgets",
    },
    "sc_route": {
        "ru": "Model routing → $/accepted",
        "en": "Model routing → $/accepted",
    },
    "sc_boundary": {
        "ru": "Promise boundary → acceptance page",
        "en": "Promise boundary → acceptance page",
    },
}


def select_user_path(
    business_text: str,
    *,
    segment_id: str = "",
    lang: str = "ru",
    sophisticated: bool = True,
) -> dict[str, Any]:
    t = (business_text or "").lower()
    L = "en" if (lang or "").lower().startswith("en") else "ru"
    ranked: list[tuple[float, dict[str, Any]]] = []
    for p in PATHS:
        score = 0.0
        hits = [kw for kw in p["match"] if kw in t]
        score += len(hits) * 1.2
        if segment_id and segment_id in (p.get("segment_pref") or ()):
            score += 2.0
        ranked.append((score, {**p, "hits": hits}))
    ranked.sort(key=lambda x: -x[0])
    best = ranked[0][1] if ranked and ranked[0][0] > 0 else PATHS[0]
    path_fit = min(1.0, 0.5 + 0.15 * len(best.get("hits") or []) + (0.1 if segment_id in (best.get("segment_pref") or ()) else 0))

    arts = best.get("premium_artifacts") or []
    if sophisticated:
        # expand sophistication layer
        extra = {
            "id": "PAX",
            "ru": "Compound function layer: segment×path×acceptance×originality mesh",
            "en": "Compound function layer: segment×path×acceptance×originality mesh",
        }
        arts = list(arts) + [extra]

    # Scenarios for path
    scen_ids = best.get("scenarios") or []
    scenarios = []
    for sid in scen_ids:
        sc = SCENARIOS.get(sid) or {}
        scenarios.append({"id": sid, "text": sc.get("en" if L == "en" else "ru") or sid})
    # Always attach systemic scenarios
    for sid in ("sc_approve", "sc_promo_sit"):
        if sid not in scen_ids:
            sc = SCENARIOS[sid]
            scenarios.append({"id": sid, "text": sc["en" if L == "en" else "ru"]})

    return {
        "module": "UserPaths",
        "version": "1.2.0",
        "path": {
            "id": best["id"],
            "label": best["label"],
            "name": best["name_en"] if L == "en" else best["name_ru"],
            "spine": best["spine"],
            "sophistication": best["sophistication"] if sophisticated else best["sophistication"] * 0.7,
            "result_sections": best["result_sections"],
            "premium_artifacts": [
                {"id": a["id"], "text": a["en"] if L == "en" else a["ru"]} for a in arts
            ],
            "scenarios": scenarios,
            "hits": best.get("hits") or [],
            "systemic_rails": [
                "analysis_completeness",
                "executive_clarity",
                "situation_promo_funding",
            ],
        },
        "path_fit": round(path_fit, 4),
        "alternates": [
            {
                "id": r[1]["id"],
                "name": r[1]["name_en"] if L == "en" else r[1]["name_ru"],
                "score": round(r[0], 3),
            }
            for r in ranked[1:4]
        ],
        "all_paths": [{"id": p["id"], "name": p["name_ru"] if L != "en" else p["name_en"]} for p in PATHS],
        "sophisticated": sophisticated,
        "message": (
            f"Path «{best['name_en']}» — sophisticated result pack + scenarios ready"
            if L == "en"
            else f"Путь «{best['name_ru']}» — pack + сценарии + systemic rails"
        ),
    }
