"""
GenCore — second flagship generative engine (wayD-native).

Compiles gen_v2+ artifacts from:
  consult spine + identity + skill memory + expert directions
  + segment/path + originality + acceptance + edge mesh

Does not replace Consultation Core — extends it. Paid implement surface stays hidden.
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
    # wayD / compound inputs
    segment: dict[str, Any] | None = None,
    user_path: dict[str, Any] | None = None,
    expert_directions: dict[str, Any] | None = None,
    originality: dict[str, Any] | None = None,
    acceptance: dict[str, Any] | None = None,
    wayd: dict[str, Any] | None = None,
    edge_mesh: dict[str, Any] | None = None,
    implement_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    generation:
      v1 — spine already in consult (default)
      v2 — uniqueness 1-pager from identity (+ segment/path)
      v3 — voice / golden examples (+ originality)
      v4 — proof post draft
      v5 — client result-pack template (sophisticated path)
      v6 — compound edge functions + acceptance gate (new)
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

    seg_p = (segment or {}).get("primary") or {}
    path_p = (user_path or {}).get("path") or {}
    expert_top = (expert_directions or {}).get("top") or []
    orig = originality or {}
    acc = acceptance or {}
    terminal = (wayd or {}).get("terminal") or wayd or {}
    mesh = edge_mesh or {}
    uniq_fns = mesh.get("unique_functions") or []

    slots: dict[str, Any] = {}

    # ── v1 consult ──────────────────────────────────────────────────────────
    slots["v1_consult"] = {
        "status": "ready",
        "artifact": "consultation_resume_html",
        "note": _d(L, "Ядро консультации уже собрано", "Consult core already assembled"),
        "wayd": {"labels": (wayd or {}).get("labels", {}).get("ids") if isinstance((wayd or {}).get("labels"), dict) else []},
    }

    # ── v2 uniqueness ───────────────────────────────────────────────────────
    if gen in ("v2", "v3", "v4", "v5", "v6") or ans:
        orig_body = ""
        by_dir = orig.get("by_direction") or {}
        if by_dir.get("product_pack"):
            orig_body = (by_dir["product_pack"].get("text") or "")[:420]
        slots["v2_uniqueness_pager"] = {
            "status": "ready" if (ans or forecast or seg_p) else "awaiting_answers",
            "title": _d(L, f"1-pager уникальности · {title}", f"Uniqueness 1-pager · {title}"),
            "headline": forecast.get("headline") or title,
            "angle": pers.get("primary_label") or seg_p.get("name"),
            "unit": unit,
            "segment": seg_p.get("id"),
            "path": path_p.get("id"),
            "from_answers": list(ans.keys())[:8],
            "expert_priors": [e.get("id") for e in expert_top[:3]],
            "body": _d(
                L,
                f"Автор: {pers.get('primary_label', '—')}. Сегмент: {seg_p.get('name', '—')}. "
                f"Путь: {path_p.get('name', '—')}. Unit: {unit}. "
                f"Не чат — result pack. Will to power: свои правила scope. "
                f"Ответы identity: {len(ans)} полей. "
                f"Оригинальность: {orig.get('originality', '—')}.",
                f"Author: {pers.get('primary_label', '—')}. Segment: {seg_p.get('name', '—')}. "
                f"Path: {path_p.get('name', '—')}. Unit: {unit}. "
                f"Not a chat — result pack. Will to power: own scope rules. "
                f"Identity answers: {len(ans)} fields. "
                f"Originality: {orig.get('originality', '—')}.",
            ),
            "originality_excerpt": orig_body,
            "delight": forecast.get("why_you_will_like_this") or [],
        }
    else:
        slots["v2_uniqueness_pager"] = {
            "status": "locked_until_identity",
            "note": _d(
                L,
                "Откроется после identity answers (внедрение — отдельный ops-контур)",
                "Opens after identity answers (implement is separate ops contour)",
            ),
        }

    # ── v3 voice ────────────────────────────────────────────────────────────
    if gen in ("v3", "v4", "v5", "v6"):
        golden = list(pers.get("golden_examples") or [])[:3]
        # inject expert playbook lines
        for e in expert_top[:2]:
            for pb in (e.get("playbooks") or [])[:1]:
                golden.append(pb)
        slots["v3_voice_pack"] = {
            "status": "ready",
            "golden_examples": golden[:5],
            "do": _d(
                L,
                "Тон: спокойная инженерия бизнеса, без инфо-хайпа; proof раньше обещаний; wayD-метки в терминале.",
                "Tone: calm business engineering, no hype; proof before promises; wayD labels in terminal.",
            ),
            "dont": _d(
                L,
                "Не auto-yield · не «гарантируем доход» · не 5 каналов сразу",
                "No auto-yield · no income guarantees · no 5 channels at once",
            ),
            "originality": orig.get("originality"),
            "replacements": orig.get("total_replacements"),
        }
    else:
        slots["v3_voice_pack"] = {"status": "queued", "requires": "gen_v3"}

    # ── v4 proof post ───────────────────────────────────────────────────────
    if gen in ("v4", "v5", "v6"):
        gate = terminal.get("ship_gate") or "near_core"
        ap = acc.get("acceptance_p") or terminal.get("acceptance_p")
        slots["v4_proof_post"] = {
            "status": "ready",
            "draft": _d(
                L,
                f"Week · decisions locked.\n\n"
                f"Same product. Better ops analytics → different money.\n\n"
                f"Unit: {unit}. Segment: {seg_p.get('id', '—')}. Path: {path_p.get('id', '—')}.\n"
                f"Orient → pick → ship. Failed hypothesis = cheap cycle.\n"
                f"Terminal: gate={gate} · P(accept)={ap if ap is not None else '—'}.\n\n"
                f"Not another AI chat — a live result pack for «{title}».",
                f"Week · decisions locked.\n\n"
                f"Same product. Better ops analytics → different money.\n\n"
                f"Unit: {unit}. Segment: {seg_p.get('id', '—')}. Path: {path_p.get('id', '—')}.\n"
                f"Orient → pick → ship. Failed hypothesis = cheap cycle.\n"
                f"Terminal: gate={gate} · P(accept)={ap if ap is not None else '—'}.\n\n"
                f"Not another AI chat — a live result pack for «{title}».",
            ),
            "channel": "X / @karimmetrix style",
            "wayd_gate": gate,
        }
    else:
        slots["v4_proof_post"] = {"status": "queued", "requires": "gen_v4"}

    # ── v5 result pack ──────────────────────────────────────────────────────
    if gen in ("v5", "v6"):
        steps = (skill.get("executive_algorithm") or {}).get("steps") or []
        path_sections = path_p.get("result_sections") or [
            "identity",
            "unit",
            "path_steps_A01_A12",
            "live_log_7d",
            "stop_rule",
            "next_act",
        ]
        premium = path_p.get("premium_artifacts") or []
        slots["v5_result_pack_template"] = {
            "status": "ready",
            "sections": path_sections,
            "executive_phases": steps[:5],
            "premium_artifacts": premium,
            "sophistication": path_p.get("sophistication"),
            "three_directions": (implement_model or {}).get("spine_order")
            or ["product_pack", "unit_pack", "ch_network"],
            "note": _d(
                L,
                "Навороченный client result pack — HTML/PDF после assist / robotics.",
                "Sophisticated client result pack — HTML/PDF after assist / robotics.",
            ),
        }
    else:
        slots["v5_result_pack_template"] = {"status": "queued", "requires": "gen_v5"}

    # ── v6 compound edges (new) ─────────────────────────────────────────────
    if gen == "v6":
        slots["v6_compound_edges"] = {
            "status": "ready",
            "unique_functions": uniq_fns[:8],
            "acceptance": {
                "p": acc.get("acceptance_p"),
                "band": acc.get("band"),
                "actions": (acc.get("actions") or [])[:4],
            },
            "terminal": {
                "density": terminal.get("density"),
                "signal": terminal.get("signal"),
                "mesh_score": terminal.get("mesh_score"),
                "ship_gate": terminal.get("ship_gate"),
            },
            "implement_model": {
                "sku": (implement_model or {}).get("sku_id"),
                "directions": (implement_model or {}).get("spine_order"),
                "price_hidden": True,
            },
            "note": _d(
                L,
                "Составные функции из mesh модулей — только на пересечении edges.",
                "Compound functions from module mesh — only at edge intersections.",
            ),
        }
    else:
        slots["v6_compound_edges"] = {"status": "queued", "requires": "gen_v6"}

    ready_n = sum(1 for s in slots.values() if isinstance(s, dict) and s.get("status") == "ready")

    return {
        "module": "GenCore",
        "version": "0.2.0-wayd",
        "flagship": 2,
        "generation": gen,
        "project": title,
        "date": date.today().isoformat(),
        "skills_in_context": loaded_n,
        "skill_id": skill.get("id"),
        "slots": slots,
        "slots_ready": ready_n,
        "pipeline": [
            "router",
            "spine_compiler",
            "skill_memory",
            "consult_pack",
            "live_log",
            "identity",
            "segment",
            "user_path",
            "expert_base",
            "originality",
            "acceptance",
            "wayd_terminal",
            "edge_mesh",
            "gencore_slots",
            "robotics_harness",
            "distill",
        ],
        "hard_rails": [
            "no_auto_yield",
            "no_open_retainer_v0",
            "single_stop_rule",
            "A01_A12_are_path_steps",
            "hide_paid_implement_surface",
        ],
        "context": {
            "segment_id": seg_p.get("id"),
            "path_id": path_p.get("id"),
            "originality": orig.get("originality"),
            "acceptance_p": acc.get("acceptance_p"),
            "ship_gate": terminal.get("ship_gate"),
            "edge_count": mesh.get("edge_count"),
            "unique_function_count": len(uniq_fns),
        },
        "lang": L,
        "message": _d(
            L,
            f"GenCore {gen}: слоты={ready_n}/6 · skills={loaded_n} · wayD mesh активен.",
            f"GenCore {gen}: slots={ready_n}/6 · skills={loaded_n} · wayD mesh active.",
        ),
    }
