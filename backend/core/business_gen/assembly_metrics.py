"""
Assembly quality metrics beyond originality + acceptance.

Systemic gates so future projects don't ship with:
  1) weak / incomplete analysis
  2) opaque executive algorithm
  3) situation without promo+funding weave

Also scores:
  - path_fidelity
  - essence_clarity (product essence presentation)
  - prompt_strength (build-prompt quality)
  - meaning_density
  - code_build_readiness
"""

from __future__ import annotations

from typing import Any


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def score_analysis_completeness(payload: dict[str, Any]) -> dict[str, Any]:
    """Is analysis deep enough (not thin density-only)?"""
    checks = {
        "has_diagnosis": bool(
            payload.get("diagnosis")
            or payload.get("working_theory")
            or (payload.get("deep_analysis") or {}).get("diagnosis")
            or (payload.get("plan") or {}).get("narrative")
        ),
        "has_friction_or_leak": bool(
            payload.get("friction_map")
            or payload.get("leak_map")
            or (payload.get("deep_analysis") or {}).get("friction_map")
            or ((payload.get("business_metrics") or {}).get("leak_map"))
        ),
        "has_evidence": bool(
            payload.get("evidence_chain")
            or (payload.get("deep_analysis") or {}).get("evidence_chain")
            or payload.get("evidence")
        ),
        "has_axis_or_entities": bool(
            payload.get("axis_narratives")
            or payload.get("entities")
            or (payload.get("tmdr") or {}).get("data_model")
            or payload.get("orientation")
        ),
        "has_completeness_gaps": bool(
            payload.get("completeness")
            or (payload.get("deep_analysis") or {}).get("completeness")
            or payload.get("open_questions")
            or (payload.get("plan") or {}).get("open_questions")
        ),
    }
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    return {
        "id": "analysis_completeness",
        "score": round(score, 3),
        "checks": checks,
        "band": "pass" if score >= 0.6 else "fail",
        "fix": "Слабый/неполный анализ" if score < 0.6 else "Analysis depth OK",
    }


def score_executive_clarity(payload: dict[str, Any]) -> dict[str, Any]:
    """Is the executive algorithm visible and approvable?"""
    ex = payload.get("executive") or payload.get("executive_algorithm") or {}
    implement = payload.get("implement_model") or {}
    code = payload.get("autonomous_code_pack") or payload.get("code_pack") or {}
    checks = {
        "has_steps": bool(ex.get("steps") or payload.get("scheme_steps") or implement.get("directions")),
        "has_plain_how": bool(
            ex.get("plain_how_it_works")
            or payload.get("how_it_works")
            or code.get("grok_build_note")
        ),
        "has_approve_gate": bool(
            ex.get("approve_gate") is not None
            or ex.get("current_step")
            or "approve" in str(payload.get("assist_offer") or {}).lower()
            or payload.get("agree_prompt")
        ),
        "has_deterministic_note": bool(
            ex.get("deterministic")
            or ex.get("no_llm")
            or "deterministic" in str(code.get("grok_build_note") or "").lower()
            or code.get("components_rich")
        ),
        "has_progress": bool(ex.get("progress") or payload.get("progress")),
    }
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    return {
        "id": "executive_clarity",
        "score": round(score, 3),
        "checks": checks,
        "band": "pass" if score >= 0.6 else "fail",
        "fix": "Неясно как работает исполнительный алгос" if score < 0.6 else "Executive clear",
    }


def score_situation_promo_funding(payload: dict[str, Any]) -> dict[str, Any]:
    """Situation layer must weave promo + funding (not siloed tabs only)."""
    sit = (
        payload.get("situation_enrich")
        or payload.get("situation")
        or {}
    )
    promo = payload.get("promotion") or payload.get("promo") or sit.get("promo_into_situation")
    fund = payload.get("funding") or sit.get("funding_into_situation")
    surface = payload.get("surface_directions") or {}
    growth = payload.get("growth_yield_core") or {}
    checks = {
        "promo_present": bool(promo or surface.get("promo") or payload.get("promo_pack")),
        "funding_present": bool(fund or growth or payload.get("funding_pack")),
        "woven_into_situation": bool(
            sit.get("promo_into_situation")
            or sit.get("funding_into_situation")
            or sit.get("situation_report_addon")
            or payload.get("situation_promo_funding_weave")
        ),
        "has_enrichment_score": sit.get("enrichment_score") is not None
        or payload.get("situation_enrichment_score") is not None,
        "has_cta_lever": bool(
            (fund or {}).get("primary_lever")
            if isinstance(fund, dict)
            else False
            or (growth.get("primary_lever") if isinstance(growth, dict) else False)
            or payload.get("primary_lever")
        ),
    }
    # soft credit if both promo and funding modules exist on deliverable even if not woven
    if checks["promo_present"] and checks["funding_present"] and not checks["woven_into_situation"]:
        checks["woven_into_situation"] = False  # explicit fail mode for systemic fix
    score = sum(1 for v in checks.values() if v) / max(1, len(checks))
    return {
        "id": "situation_promo_funding",
        "score": round(score, 3),
        "checks": checks,
        "band": "pass" if score >= 0.6 else "fail",
        "fix": "Promo/funding не вшиты в ситуацию" if score < 0.6 else "Situation weave OK",
    }


def score_path_fidelity(payload: dict[str, Any]) -> dict[str, Any]:
    path = (payload.get("user_path") or {}).get("path") or payload.get("path") or {}
    spine = path.get("spine") or []
    sections = path.get("result_sections") or []
    fit = _f((payload.get("user_path") or {}).get("path_fit"), 0.5)
    score = round(
        min(
            1.0,
            0.35 * fit
            + 0.25 * min(1.0, len(spine) / 3)
            + 0.25 * min(1.0, len(sections) / 5)
            + (0.15 if path.get("id") else 0),
        ),
        3,
    )
    return {
        "id": "path_fidelity",
        "score": score,
        "path_id": path.get("id"),
        "band": "pass" if score >= 0.55 else "fail",
    }


def score_essence_clarity(payload: dict[str, Any]) -> dict[str, Any]:
    """Product essence: one-liner, unit, anti, report shape."""
    hook = payload.get("hook_plan") or {}
    core = payload.get("core_report") or {}
    identity = payload.get("identity_pack") or {}
    lines = 0
    blob = " ".join(
        [
            str(hook.get("pitch") or ""),
            str(hook.get("headline") or ""),
            str((core.get("identity") or {}) if isinstance(core.get("identity"), dict) else core.get("title") or ""),
            str((identity.get("forecast") or {}).get("headline") or ""),
            str(payload.get("message") or ""),
        ]
    ).lower()
    for kw in ("unit", "не ", "not ", "kill", "pack", "оффер", "offer", "result"):
        if kw in blob:
            lines += 1
    score = round(min(1.0, 0.3 + lines * 0.1 + (0.2 if len(blob) > 80 else 0)), 3)
    return {
        "id": "essence_clarity",
        "score": score,
        "band": "pass" if score >= 0.55 else "fail",
    }


def score_prompt_strength(prompt_pack: dict[str, Any] | None) -> dict[str, Any]:
    p = prompt_pack or {}
    parts = [
        p.get("system"),
        p.get("master"),
        p.get("constraints"),
        p.get("acceptance"),
        p.get("executive_spec"),
        p.get("anti_patterns"),
    ]
    filled = sum(1 for x in parts if x and len(str(x)) > 40)
    score = round(filled / max(1, len(parts)), 3)
    return {
        "id": "prompt_strength",
        "score": score,
        "band": "pass" if score >= 0.66 else "fail",
        "sections_filled": filled,
    }


def score_meaning_density(payload: dict[str, Any]) -> dict[str, Any]:
    meaning = payload.get("meaning_engine") or payload.get("meaning") or {}
    moves = (
        payload.get("original_moves")
        or (payload.get("synthesis_highlights") or {}).get("original_moves")
        or meaning.get("moves")
        or []
    )
    n = len(moves) if isinstance(moves, list) else 0
    dens = _f(meaning.get("density"), min(1.0, n / 5) if n else 0.4)
    score = round(min(1.0, dens * 0.6 + min(1.0, n / 4) * 0.4), 3)
    return {"id": "meaning_density", "score": score, "band": "pass" if score >= 0.5 else "fail"}


def score_code_build_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    code = payload.get("autonomous_code_pack") or payload.get("code_pack") or {}
    rich = code.get("components_rich") or []
    entry = code.get("entrypoints") or []
    has_exec = any(
        "executive" in str(c).lower() or "approve" in str(c).lower()
        for c in (rich or code.get("components") or [])
    )
    score = round(
        min(
            1.0,
            0.25 * min(1.0, len(rich or code.get("components") or []) / 6)
            + 0.25 * min(1.0, len(entry) / 3)
            + (0.25 if code.get("grok_build_note") else 0)
            + (0.25 if has_exec or code.get("build_rails") else 0.1),
        ),
        3,
    )
    return {
        "id": "code_build_readiness",
        "score": score,
        "band": "pass" if score >= 0.55 else "fail",
    }


def evaluate_assembly(
    payload: dict[str, Any],
    *,
    originality: float | None = None,
    acceptance_p: float | None = None,
    prompt_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full assembly scorecard + systemic 3-gate."""
    metrics = [
        score_analysis_completeness(payload),
        score_executive_clarity(payload),
        score_situation_promo_funding(payload),
        score_path_fidelity(payload),
        score_essence_clarity(payload),
        score_prompt_strength(prompt_pack or payload.get("build_prompt")),
        score_meaning_density(payload),
        score_code_build_readiness(payload),
    ]
    if originality is not None:
        metrics.append(
            {
                "id": "originality",
                "score": round(_f(originality), 3),
                "band": "pass" if _f(originality) >= 0.45 else "fail",
            }
        )
    if acceptance_p is not None:
        metrics.append(
            {
                "id": "acceptance_p",
                "score": round(_f(acceptance_p), 3),
                "band": "pass" if _f(acceptance_p) >= 0.5 else "fail",
            }
        )

    by_id = {m["id"]: m for m in metrics}
    systemic = [
        by_id["analysis_completeness"],
        by_id["executive_clarity"],
        by_id["situation_promo_funding"],
    ]
    systemic_ok = all(m["band"] == "pass" for m in systemic)
    overall = round(sum(m["score"] for m in metrics) / max(1, len(metrics)), 3)

    fails = [m for m in metrics if m.get("band") == "fail"]
    repairs = []
    for m in fails:
        repairs.append(
            {
                "metric": m["id"],
                "fix": m.get("fix") or m["id"],
                "action": {
                    "analysis_completeness": "Добавить diagnosis + friction_map + evidence_chain + gaps",
                    "executive_clarity": "Добавить S0–S10 executive steps + plain_how + approve gate",
                    "situation_promo_funding": "Вшить promo hooks + funding lever в situation_enrich",
                    "path_fidelity": "Расширить user_path spine + result_sections",
                    "essence_clarity": "Усилить hook pitch: unit + anti + kill",
                    "prompt_strength": "Собрать master prompt с constraints + executive_spec",
                    "meaning_density": "Meaning engine: ≥3 original moves",
                    "code_build_readiness": "Code pack: components_rich + entrypoints + rails",
                    "originality": "originality_inject re-run",
                    "acceptance_p": "Close gaps / boost path fit",
                }.get(m["id"], "Improve metric surface"),
            }
        )

    return {
        "module": "AssemblyMetrics",
        "version": "1.0.0",
        "overall": overall,
        "band": (
            "ideal"
            if overall >= 0.78 and systemic_ok
            else "ship"
            if overall >= 0.62 and systemic_ok
            else "repair"
        ),
        "systemic_three": {
            "ok": systemic_ok,
            "gates": systemic,
            "labels": [
                "1 analysis completeness",
                "2 executive clarity",
                "3 situation←promo+funding",
            ],
        },
        "metrics": metrics,
        "repairs": repairs,
        "message": (
            "Assembly ideal — systemic 3 pass"
            if overall >= 0.78 and systemic_ok
            else "Systemic gates failed — apply repairs"
            if not systemic_ok
            else "Shipable with upgrades"
        ),
    }
