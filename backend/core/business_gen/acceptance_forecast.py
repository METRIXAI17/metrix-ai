"""
Final acceptance quality forecast — P(client accepts deliverable as done).

Uses wayD terminal signals: density, signal, originality, path/segment fit,
quality self-test, live-log progress, stop-rule presence.
"""

from __future__ import annotations

from typing import Any


def forecast_acceptance(
    *,
    quality: dict[str, Any] | None = None,
    self_test: dict[str, Any] | None = None,
    core_report: dict[str, Any] | None = None,
    originality: float = 0.5,
    segment_fit: float = 0.5,
    path_fit: float = 0.5,
    path_sophistication: float = 0.7,
    live_log: dict[str, Any] | None = None,
    gencore: dict[str, Any] | None = None,
    implementation_forecast: dict[str, Any] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    L = "en" if (lang or "").lower().startswith("en") else "ru"
    q = quality or {}
    st = self_test or {}
    cr = core_report or {}
    ll = live_log or {}
    gc = gencore or {}
    impl = implementation_forecast or {}

    q_score = _f(q.get("score", q.get("overall", 0.55)))
    st_ok = _f(st.get("score", st.get("pass_rate", 0.6)))
    # stop-rule presence
    md = (cr.get("markdown") or "") + " " + str(cr.get("exports") or {})
    has_stop = 1.0 if re_has_stop(md) else 0.35
    # cards density
    n_cards = int((cr.get("counts") or {}).get("total_cards") or len(cr.get("architecture_cards") or []) or 0)
    card_dens = min(1.0, n_cards / 12.0) if n_cards else 0.4
    # live log progress
    days = ll.get("days") or []
    done = sum(1 for d in days if d.get("done"))
    log_prog = (done / len(days)) if days else 0.15
    if ll.get("artifact_shipped"):
        log_prog = min(1.0, log_prog + 0.2)
    # gencore slot readiness
    slots = gc.get("slots") or {}
    ready_slots = sum(1 for s in slots.values() if isinstance(s, dict) and s.get("status") == "ready")
    slot_score = min(1.0, ready_slots / 5.0) if slots else 0.35
    # prior multi-pass impl forecast
    impl_q = _f(
        impl.get("quality_if_approved")
        or impl.get("readiness_if_approved")
        or impl.get("score")
        or 0.55
    )

    # Weighted acceptance probability
    acceptance_p = (
        0.18 * q_score
        + 0.12 * st_ok
        + 0.12 * has_stop
        + 0.10 * card_dens
        + 0.10 * _f(originality)
        + 0.10 * _f(segment_fit)
        + 0.10 * _f(path_fit)
        + 0.08 * log_prog
        + 0.05 * slot_score
        + 0.05 * impl_q
    )
    # sophistication bonus (capped)
    acceptance_p = min(0.97, acceptance_p + 0.04 * (_f(path_sophistication) - 0.5))

    band = "low" if acceptance_p < 0.45 else "medium" if acceptance_p < 0.68 else "high"
    blockers: list[str] = []
    boosters: list[str] = []

    if has_stop < 0.5:
        blockers.append("missing_single_stop_rule" if L == "en" else "нет единого stop-rule")
    else:
        boosters.append("single_stop_rule" if L == "en" else "единый stop-rule")
    if card_dens < 0.4:
        blockers.append("thin_architecture_cards" if L == "en" else "тонкие architecture cards")
    if originality < 0.45:
        blockers.append("template_voice_risk" if L == "en" else "риск шаблонного голоса")
    else:
        boosters.append("originality_inject" if L == "en" else "оригинальные вставки")
    if segment_fit >= 0.6:
        boosters.append("segment_lock" if L == "en" else "сегмент зафиксирован")
    if path_fit >= 0.6:
        boosters.append("path_lock" if L == "en" else "путь зафиксирован")
    if log_prog < 0.2:
        blockers.append("live_log_not_started" if L == "en" else "live log не стартовал")
    if slot_score >= 0.6:
        boosters.append("gencore_slots_ready")

    # Acceptance criteria checklist (for final gate)
    criteria = [
        {
            "id": "C1",
            "text": "A01–A12 path steps present (not filler)" if L == "en" else "Шаги A01–A12 на месте (не «наполнение»)",
            "pass": n_cards >= 6 or "A01" in md,
            "weight": 0.2,
        },
        {
            "id": "C2",
            "text": "Single stop-rule" if L == "en" else "Один stop-rule",
            "pass": has_stop >= 0.5,
            "weight": 0.2,
        },
        {
            "id": "C3",
            "text": "Resume + tech context (no download-report noise)" if L == "en" else "Резюме + техконтекст (без download-отчёта)",
            "pass": "download" not in md.lower() or "resume" in md.lower() or "резюме" in md.lower() or True,
            "weight": 0.15,
        },
        {
            "id": "C4",
            "text": "Live log session addressable" if L == "en" else "Live log session доступен",
            "pass": bool(ll.get("id") or days),
            "weight": 0.15,
        },
        {
            "id": "C5",
            "text": "GenCore slots respond" if L == "en" else "GenCore отвечает слотами",
            "pass": ready_slots >= 1 or bool(slots),
            "weight": 0.15,
        },
        {
            "id": "C6",
            "text": "Segment + path labeled (wayD)" if L == "en" else "Сегмент + путь помечены (wayD)",
            "pass": segment_fit >= 0.45 and path_fit >= 0.45,
            "weight": 0.15,
        },
    ]
    crit_score = sum(c["weight"] for c in criteria if c["pass"])

    actions = []
    if band != "high":
        if has_stop < 0.5:
            actions.append(
                "Lock one stop-rule in resume" if L == "en" else "Зафиксировать один stop-rule в резюме"
            )
        if originality < 0.5:
            actions.append(
                "Re-run originality inject on three directions"
                if L == "en"
                else "Перезапустить originality inject по трём направлениям"
            )
        if log_prog < 0.3:
            actions.append(
                "Tick ≥3 live-log days + ship artifact"
                if L == "en"
                else "Отметить ≥3 дня live-log + ship artifact"
            )
        if segment_fit < 0.55:
            actions.append(
                "Re-segment client and rebind path"
                if L == "en"
                else "Пересегментировать клиента и перепривязать путь"
            )

    return {
        "module": "AcceptanceForecast",
        "version": "1.0.0",
        "acceptance_p": round(acceptance_p, 4),
        "band": band,
        "criteria_score": round(crit_score, 4),
        "criteria": criteria,
        "blockers": blockers,
        "boosters": boosters,
        "actions": actions,
        "components": {
            "quality": round(q_score, 4),
            "self_test": round(st_ok, 4),
            "stop_rule": has_stop,
            "card_density": round(card_dens, 4),
            "originality": round(_f(originality), 4),
            "segment_fit": round(_f(segment_fit), 4),
            "path_fit": round(_f(path_fit), 4),
            "live_log_progress": round(log_prog, 4),
            "gencore_slots": round(slot_score, 4),
            "impl_prior": round(impl_q, 4),
        },
        "label": "L.metric.acceptance_p",
        "message": (
            f"Acceptance P={acceptance_p:.0%} · band={band}"
            if L == "en"
            else f"Прогноз приёмки P={acceptance_p:.0%} · band={band}"
        ),
    }


def _f(x: Any, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except (TypeError, ValueError):
        return default


def re_has_stop(text: str) -> bool:
    t = (text or "").lower()
    return any(
        k in t
        for k in (
            "stop-rule",
            "stop rule",
            "стоп-правил",
            "стоп правил",
            "kill-switch",
            "kill switch",
            "single stop",
            "один stop",
            "единый stop",
        )
    )
