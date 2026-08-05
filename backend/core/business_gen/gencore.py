"""
GenCore — second flagship generative engine.

Compiles gen_v2+ artifacts from consult spine + identity answers + skill memory.
Does not replace Consultation Core — extends it after pay / answers.
"""

from __future__ import annotations

from datetime import date
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def run_gencore(
    *,
    business_text: str,
    project_name: str = "",
    core_report: dict[str, Any] | None = None,
    personality: dict[str, Any] | None = None,
    identity_pack: dict[str, Any] | None = None,
    skill_distilled: dict[str, Any] | None = None,
    skills_loaded: list[dict[str, Any]] | None = None,
    answers: dict[str, str] | None = None,
    generation: str = "v1",
    lang: str = "ru",
) -> dict[str, Any]:
    """
    generation:
      v1 — spine already in consult (default)
      v2 — uniqueness 1-pager from identity
      v3 — voice / golden examples
      v4 — proof post draft
      v5 — client result-pack template
    """
    L = _lang(lang)
    gen = (generation or "v1").lower().replace("gen_", "")
    cr = core_report or {}
    pers = personality or {}
    ident = identity_pack or {}
    forecast = (ident.get("forecast") or {}) if ident else {}
    ans = answers or {}
    title = project_name or cr.get("title") or "Project"
    unit = (cr.get("profile") or {}).get("unit") or "unit"
    skill = skill_distilled or {}
    loaded_n = len(skills_loaded or [])

    slots: dict[str, Any] = {}

    # Always expose pipeline status
    slots["v1_consult"] = {
        "status": "ready",
        "artifact": "consultation_resume_html",
        "note": _d(L, "Ядро консультации уже собрано", "Consult core already assembled"),
    }

    # v2 uniqueness 1-pager
    if gen in ("v2", "v3", "v4", "v5") or ans:
        slots["v2_uniqueness_pager"] = {
            "status": "ready" if (ans or forecast) else "awaiting_answers",
            "title": _d(L, f"1-pager уникальности · {title}", f"Uniqueness 1-pager · {title}"),
            "headline": forecast.get("headline") or title,
            "angle": pers.get("primary_label"),
            "unit": unit,
            "from_answers": list(ans.keys())[:8],
            "body": _d(
                L,
                f"Автор: {pers.get('primary_label', '—')}. Unit: {unit}. "
                f"Не чат — result pack. Will to power: свои правила scope. "
                f"Ответы identity: {len(ans)} полей.",
                f"Author: {pers.get('primary_label', '—')}. Unit: {unit}. "
                f"Not a chat — result pack. Will to power: own scope rules. "
                f"Identity answers: {len(ans)} fields.",
            ),
            "delight": forecast.get("why_you_will_like_this") or [],
        }
    else:
        slots["v2_uniqueness_pager"] = {
            "status": "locked_until_pay_answers",
            "note": _d(L, "Откроется после оплаты + identity answers", "Opens after pay + identity answers"),
        }

    if gen in ("v3", "v4", "v5"):
        slots["v3_voice_pack"] = {
            "status": "ready",
            "golden_examples": (pers.get("golden_examples") or [])[:3],
            "do": _d(
                L,
                "Тон: спокойная инженерия бизнеса, без инфо-хайпа; proof раньше обещаний.",
                "Tone: calm business engineering, no hype; proof before promises.",
            ),
            "dont": _d(L, "Не auto-yield · не «гарантируем доход»", "No auto-yield · no income guarantees"),
        }
    else:
        slots["v3_voice_pack"] = {"status": "queued", "requires": "gen_v3"}

    if gen in ("v4", "v5"):
        slots["v4_proof_post"] = {
            "status": "ready",
            "draft": _d(
                L,
                f"Week · decisions locked.\n\n"
                f"Same product. Better ops analytics → different money.\n\n"
                f"Unit: {unit}.\n"
                f"Orient → pick → ship. Failed hypothesis = cheap cycle.\n\n"
                f"Not another AI chat — a live result pack for «{title}».",
                f"Week · decisions locked.\n\n"
                f"Same product. Better ops analytics → different money.\n\n"
                f"Unit: {unit}.\n"
                f"Orient → pick → ship. Failed hypothesis = cheap cycle.\n\n"
                f"Not another AI chat — a live result pack for «{title}».",
            ),
            "channel": "X / @karimmetrix style",
        }
    else:
        slots["v4_proof_post"] = {"status": "queued", "requires": "gen_v4"}

    if gen == "v5":
        steps = (skill.get("executive_algorithm") or {}).get("steps") or []
        slots["v5_result_pack_template"] = {
            "status": "ready",
            "sections": [
                "identity",
                "unit",
                "path_steps_A01_A12",
                "live_log_7d",
                "stop_rule",
                "next_act",
            ],
            "executive_phases": steps[:5],
            "note": _d(
                L,
                "Шаблон клиентского result pack — отдать как HTML/PDF после assist.",
                "Client result-pack template — ship as HTML/PDF after assist.",
            ),
        }
    else:
        slots["v5_result_pack_template"] = {"status": "queued", "requires": "gen_v5"}

    return {
        "module": "GenCore",
        "version": "0.1.0",
        "flagship": 2,
        "generation": gen,
        "project": title,
        "date": date.today().isoformat(),
        "skills_in_context": loaded_n,
        "skill_id": skill.get("id"),
        "slots": slots,
        "pipeline": [
            "router",
            "spine_compiler",
            "skill_memory",
            "consult_pack",
            "live_log",
            "identity",
            "gencore_slots",
            "distill",
        ],
        "hard_rails": [
            "no_auto_yield",
            "no_open_retainer_v0",
            "single_stop_rule",
            "A01_A12_are_path_steps",
        ],
        "lang": L,
        "message": _d(
            L,
            f"GenCore {gen}: слоты собраны. skills_in_context={loaded_n}.",
            f"GenCore {gen}: slots assembled. skills_in_context={loaded_n}.",
        ),
    }
