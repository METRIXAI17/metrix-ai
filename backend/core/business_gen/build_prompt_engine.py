"""
Stronger project build-prompts from Metrix.

Problem observed: thin prompts → weak analysis, opaque executive, siloed promo/funding.
This module emits a full master prompt for any product build (Grok Build / human / agent).
"""

from __future__ import annotations

from typing import Any


def build_project_prompt(
    *,
    project_name: str,
    business_text: str,
    path: dict[str, Any] | None = None,
    segment: dict[str, Any] | None = None,
    unit: str = "",
    lang: str = "ru",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    is_ru = not (lang or "").lower().startswith("en")
    path = path or {}
    segment = segment or {}
    name = project_name or "Project"
    unit = unit or path.get("unit") or "one billable unit with kill"
    spine = path.get("spine") or ["product_pack", "unit_pack", "ch_network"]
    path_id = path.get("id") or "library_ship"
    seg_id = segment.get("id") or (segment.get("primary") or {}).get("id") or "b2b_knowledge"

    system = (
        (
            f"Ты собираешь продукт «{name}». Не чат-обёртка. "
            f"Unit = {unit}. Path={path_id}. Segment={seg_id}. "
            "Обязательные системные ворота (иначе fail): "
            "(1) полный анализ: diagnosis+friction+evidence+gaps; "
            "(2) явный executive S0–S10 с approve gate; "
            "(3) promo и funding вшиты в situation, не отдельными «вкладками-сиротами». "
            "Детерминированное ядро предпочтительнее LLM-магии. "
            "Выход всегда: unique title + report shape + automations after approve."
        )
        if is_ru
        else (
            f"You are shipping product «{name}». Not a chat wrapper. "
            f"Unit={unit}. Path={path_id}. Segment={seg_id}. "
            "Hard gates: (1) full analysis (2) executive S0–S10+approve (3) promo+funding woven into situation. "
            "Prefer deterministic core over LLM fog. Output: unique title + report + post-approve automations."
        )
    )

    master = f"""# Master build prompt · {name}

## Brief
{(business_text or '')[:1200]}

## Path & segment
- path: {path_id}
- spine: {', '.join(spine)}
- segment: {seg_id}
- unit: {unit}

## Hard rails (systemic — never skip)
1. ANALYSIS DEPTH
   - Terminal snapshot of persona / work / situation (or B2B analogs)
   - friction_map (named, severity, evidence)
   - evidence_chain (claim ← quote)
   - diagnosis.working_theory + confidence
   - completeness.gaps listed

2. EXECUTIVE ALGORITHM (visible)
   S0 INTAKE → S1 SNAPSHOT → S2 DIAGNOSE → S3 MEASURE → S4 MODEL →
   S5 DERIVE (+ promo∪funding into situation) → S6 PROPOSE →
   S7 AWAIT_APPROVE (human eyes) → S8 EXECUTE scheme → S9 REPORT → S10 AUTOMATE
   Every step: id, title, algo note, status, output_summary.
   User must approve before execute. API: analyze + approve-and-run.

3. SITUATION ← PROMO + FUNDING
   - Map top friction → promo angle + 1 DM/post copy
   - Map situation → funding primary lever + gate (structure_first)
   - situation_report_addon string used in impact axis #1
   - No auto-yield promises

## Deliverable shape
- Catalog or pack of rule/offer cards (executable, not advice)
- Client packs by segment (weights + defaults)
- Promo board: platforms / networking / social — copy buttons
- Funding board: 3 pillars + quickstart
- Ship plan: one-button advance
- Landing + app UI expressing the core (not generic SaaS)

## Acceptance
- analysis_completeness ≥ 0.6
- executive_clarity ≥ 0.6
- situation_promo_funding ≥ 0.6
- originality ≥ 0.45
- User can: see steps → approve → get report + automations without reading source code

## Anti-patterns
- «Ещё один AI-чат»
- Analysis = only density scores without narrative diagnosis
- Hidden pipeline (no S0–S10)
- Promo/funding only as orphan tabs
- Passive yield / hype pricing
"""

    constraints = [
        "no_auto_yield",
        "single_stop_kill",
        "one_lever_per_run",
        "approve_before_execute",
        "promo_funding_in_situation",
        "deterministic_core_preferred",
        "copy_paste_promo",
        "structure_first_capital",
    ]

    executive_spec = {
        "steps": [
            "S0_INTAKE",
            "S1_SNAPSHOT",
            "S2_DIAGNOSE",
            "S3_MEASURE",
            "S4_MODEL",
            "S5_DERIVE_ENRICH",
            "S6_PROPOSE",
            "S7_AWAIT_APPROVE",
            "S8_EXECUTE",
            "S9_REPORT",
            "S10_AUTOMATE",
        ],
        "gate": "S7",
        "api": ["POST /analyze", "POST /approve-and-run"],
    }

    anti = [
        "generic coaching chat",
        "analysis without friction map",
        "magic execute without scheme trace",
        "promo silo / funding silo",
        "subscription-only without unit",
    ]

    acceptance = {
        "metrics": [
            "analysis_completeness",
            "executive_clarity",
            "situation_promo_funding",
            "path_fidelity",
            "essence_clarity",
            "originality",
            "acceptance_p",
            "code_build_readiness",
        ],
        "min_systemic": 0.6,
        "report_axes": ["situation", "persona_or_ops", "work_or_product"],
    }

    scenarios = _scenarios_for_path(path_id, is_ru)

    return {
        "module": "BuildPromptEngine",
        "version": "1.1.0",
        "project": name,
        "system": system,
        "master": master,
        "constraints": constraints,
        "executive_spec": executive_spec,
        "anti_patterns": anti,
        "acceptance": acceptance,
        "scenarios": scenarios,
        "path_id": path_id,
        "segment_id": seg_id,
        "unit": unit,
        "extra": extra or {},
        "prompt_strength_hint": "6/6 sections present",
        "message": (
            "Master prompt ready — hard rails include systemic 3"
            if not is_ru
            else "Master prompt готов — жёсткие рельсы = 3 системных ворот"
        ),
    }


def _scenarios_for_path(path_id: str, is_ru: bool) -> list[dict[str, str]]:
    catalog = {
        "library_ship": [
            {"id": "sc_first_card", "ru": "Первая карточка каталога → free run → proof post", "en": "First catalog card → free run → proof post"},
            {"id": "sc_pack_sell", "ru": "Niche pack sale после 1 public artifact", "en": "Niche pack sale after 1 public artifact"},
            {"id": "sc_kill", "ru": "0 DM 14d → сменить angle, не расширять catalog", "en": "0 DM 14d → change angle, don't expand catalog"},
        ],
        "agency_margin": [
            {"id": "sc_rework", "ru": "Rework% → handoff scoreboard → margin unit", "en": "Rework% → handoff board → margin unit"},
            {"id": "sc_pilot", "ru": "14d pilot one lever only", "en": "14d pilot one lever only"},
        ],
        "builder_pack": [
            {"id": "sc_sku", "ru": "SKU boundary → pilot widgets → builder DM", "en": "SKU boundary → pilot widgets → builder DM"},
            {"id": "sc_api", "ru": "API surface: analyze + approve-and-run", "en": "API surface: analyze + approve-and-run"},
        ],
        "creator_shift": [
            {"id": "sc_triple", "ru": "Persona+work+situation → triple impact report", "en": "Persona+work+situation → triple impact"},
            {"id": "sc_approve", "ru": "User eyes on S0–S6 → one approve → automations", "en": "User eyes S0–S6 → approve → automations"},
        ],
        "api_cost": [
            {"id": "sc_route", "ru": "Model routing matrix → $/accepted outcome", "en": "Routing matrix → $/accepted"},
        ],
        "expert_sku": [
            {"id": "sc_boundary", "ru": "Promise boundary pack → acceptance page", "en": "Promise boundary → acceptance page"},
        ],
        "hobby_lattice": [
            {"id": "sc_run", "ru": "Rule environment run → unique title + 3 impacts", "en": "Rule env run → title + 3 impacts"},
            {"id": "sc_promo_sit", "ru": "Friction maps to promo angle inside situation", "en": "Friction → promo angle in situation"},
        ],
    }
    rows = catalog.get(path_id) or catalog["library_ship"]
    return [
        {"id": r["id"], "text": r["ru"] if is_ru else r["en"]} for r in rows
    ]
