"""Content AI Closer pipeline.

abstraction → cards → prompt rewrite → (engine) → making

Also audits extra hypotheses at runtime so the pack carries its own
proof, not a promise.
"""

from __future__ import annotations

from typing import Any

from backend.core.content_closer.abstraction import compose_abstraction
from backend.core.content_closer.archetypes import pick_archetypes, score_vectors
from backend.core.content_closer.cards import translate_cards
from backend.core.content_closer.comfort import HYPE, comfort_turn
from backend.core.content_closer.landing import compose_event
from backend.core.content_closer.making import MakingRefused, run_making_chamber
from backend.core.content_closer.prompt_rewrite import rewrite_prompt
from backend.core.content_closer.trends import screen_trends
from backend.core.resonance import new_id
from backend.core.voice import DISCLAIMER, clip


def audit_hypotheses(pack: dict[str, Any]) -> dict[str, Any]:
    """Check extra hypotheses against the live pack. Failures are data, not shame."""
    vec = pack.get("vectors") or {}
    arch = pack.get("archetypes") or {}
    essay = pack.get("abstraction") or {}
    cards = pack.get("cards") or {}
    prompt = pack.get("prompt") or {}
    event = pack.get("event") or {}
    trends = pack.get("trends") or {}
    comfort = pack.get("comfort") or {}
    making = pack.get("making") or {}
    primary_id = (arch.get("primary") or {}).get("id")
    secondary_id = (arch.get("secondary") or {}).get("id")
    codes = set(cards.get("codes") or [])
    master = prompt.get("master") or ""
    vision = (event.get("vision_text") or "") + " " + (event.get("invitation") or "")
    cal = ((making.get("meta") or {}).get("calendar_7d") or []) if making else []
    d1 = next((d for d in cal if d.get("day") == 1), None)

    checks = [
        {
            "id": "H1",
            "claim": "state_seeking ≥ 0.6 ⇒ disappointed_actor is primary or secondary",
            "hold": (
                vec.get("state_seeking", 0) < 0.6
                or primary_id == "disappointed_actor"
                or secondary_id == "disappointed_actor"
            ),
        },
        {
            "id": "H2",
            "claim": "cards must contain FN-KILL and FN-UNIT or making quality drops",
            "hold": "FN-KILL" in codes and "FN-UNIT" in codes,
        },
        {
            "id": "H3",
            "claim": "prompt that does not quote ≥ 2 card codes is weak",
            "hold": sum(1 for c in codes if c and c in master) >= 2,
        },
        {
            "id": "H4",
            "claim": "event invitation must not contain CTA/hype words",
            "hold": not any(
                w in vision.lower()
                for w in ("купи", "гарант", "прорыв", "масштабир", "10x", "запустить roi")
            ),
        },
        {
            "id": "H5",
            "claim": "comfort replies must not contain hype",
            "hold": not any(w in (comfort.get("reply") or "").lower() for w in HYPE),
        },
        {
            "id": "H6",
            "claim": "empty-outside + full-inside should produce the plane metaphor",
            "hold": (
                not (vec.get("empty_outside", 0) >= 0.35 and vec.get("full_inside", 0) >= 0.3)
                or ("самолёт" in (essay.get("essay") or "").lower())
                or ("plane" in (essay.get("essay") or "").lower())
            ),
        },
        {
            "id": "H7",
            "claim": "screened trend must appear in prompt AND making satellite",
            "hold": (
                not trends.get("primary")
                or (
                    (trends["primary"].get("id") or "") in master
                    and (
                        not making
                        or (trends["primary"].get("id") or "")
                        in str((making.get("meta") or {}).get("satellite") or {})
                        or (trends["primary"].get("id") or "") in str(making)
                    )
                )
            ),
        },
        {
            "id": "H8",
            "claim": "fear protocol required if money/structure is live",
            "hold": (
                vec.get("money_structure", 0) < 0.2
                or "FN-FEAR" in codes
                or bool((making.get("meta") or {}).get("fin_structure_shift", {}).get("fear_protocol"))
            ),
        },
        {
            "id": "H9",
            "claim": "abstraction without a movement verb is failed",
            "hold": bool(essay.get("has_motion")),
        },
        {
            "id": "H10",
            "claim": "making calendar day 1 must be the event entry, never research",
            "hold": (
                not d1
                or (
                    "исслед" not in (d1.get("do") or "").lower()
                    and "research" not in (d1.get("do") or "").lower()
                    and d1.get("id") == "D1_ENTER"
                )
            ),
        },
        {
            "id": "H11",
            "claim": "abstraction density should stay ≥ 0.45 (not watery copy)",
            "hold": (essay.get("density") or 0) >= 0.45,
        },
        {
            "id": "H12",
            "claim": "prompt strength ≥ 0.55 when cards ≥ 6",
            "hold": (cards.get("count") or 0) < 6 or (prompt.get("strength") or 0) >= 0.55,
        },
    ]
    held = sum(1 for c in checks if c["hold"])
    return {
        "module": "HypothesisAudit",
        "total": len(checks),
        "held": held,
        "ratio": round(held / max(1, len(checks)), 3),
        "failed": [c["id"] for c in checks if not c["hold"]],
        "items": checks,
    }


def run_closer(
    brief: str,
    *,
    lang: str = "ru",
    with_comfort: bool = True,
    with_making: bool = False,
    extra: str = "",
) -> dict[str, Any]:
    text = (brief or "").strip()
    if len(text) < 8:
        raise ValueError("Напишите, что сейчас движется — хотя бы одно предложение.")

    vectors = score_vectors(text)
    archetypes = pick_archetypes(vectors, text)
    abstraction = compose_abstraction(text, lang=lang, archetypes=archetypes, vectors=vectors)
    event = compose_event(text, archetypes=archetypes, vectors=vectors, lang=lang)
    trends = screen_trends(text, vectors, limit=3)
    cards = translate_cards(
        brief=text,
        essay=abstraction,
        event=event,
        trends=trends,
        vectors=vectors,
        lang=lang,
    )
    prompt = rewrite_prompt(
        brief=text,
        essay=abstraction,
        cards=cards,
        event=event,
        trends=trends,
        lang=lang,
    )
    comfort = (
        comfort_turn(text, closer={"vectors": vectors, "archetypes": archetypes}, lang=lang)
        if with_comfort
        else {}
    )

    pack: dict[str, Any] = {
        "id": new_id(),
        "ok": True,
        "module": "ContentCloser",
        "version": "1.0.0",
        "layers": {
            "top": "GROWTH AI",
            "mid": "METRIX TRADE APP",
            "bottom": "CONTENT AI CLOSER",
        },
        "sections": ("landing", "engine", "making"),
        "brief": clip(text, 800),
        "lang": lang,
        "vectors": vectors,
        "archetypes": archetypes,
        "abstraction": abstraction,
        "event": event,
        "trends": trends,
        "cards": cards,
        "prompt": prompt,
        "comfort": comfort,
        "engine_brief": prompt.get("engine_brief"),
        "disclaimer": DISCLAIMER,
    }

    making = None
    if with_making:
        try:
            making = run_making_chamber(pack, extra=extra, lang=lang)
            pack["making"] = making
        except MakingRefused as exc:
            pack["making_error"] = str(exc)

    pack["audit"] = audit_hypotheses(pack)
    pack["message"] = (
        f"{abstraction.get('lead')} · карточек {cards.get('count')} · "
        f"тренд { (trends.get('primary') or {}).get('id') } · "
        f"аудит {pack['audit']['held']}/{pack['audit']['total']}"
    )
    return pack


def closer_as_artifact(pack: dict[str, Any]) -> dict[str, Any]:
    """Shape the closer pack as a demo-highway artifact (resonance-compatible)."""
    essay = pack.get("abstraction") or {}
    event = pack.get("event") or {}
    cards = pack.get("cards") or {}
    items = cards.get("items") or []
    trend = (pack.get("trends") or {}).get("primary") or {}
    steps = [c.get("task") for c in items[:6] if c.get("task")]
    return {
        "id": pack.get("id") or new_id(),
        "kind": "closer.event",
        "lane": "landing",
        "title": event.get("title") or essay.get("archetype") or "Вход",
        "one_liner": essay.get("lead") or event.get("invitation"),
        "break": (
            "Понятия-антагонисты держат ситуацию как место, в которое надо прийти. "
            "Пока это место — оно уже немного мертво."
        ),
        "move": essay.get("essay") or event.get("vision_text"),
        "steps": steps or ["войти в событие", "прочитать карточки", "отдать промпт движку"],
        "artifact_week": event.get("vision_text") or essay.get("essay"),
        "anti": [
            "Не стремиться к состоянию.",
            "Не продавать сигналы.",
            "Не делать из лендинга кнопку студии.",
        ],
        "meta": {
            "archetype": essay.get("archetype"),
            "entry": event.get("invitation"),
            "exit": "обстоятельства меняются. и всё.",
            "invalidation": next((c.get("kill") for c in items if c.get("code") == "FN-KILL"), ""),
            "window": trend.get("name_ru"),
            "cards": items,
            "event": event,
            "prompt_strength": (pack.get("prompt") or {}).get("strength"),
            "trend_id": trend.get("id"),
            "audit": pack.get("audit"),
        },
        "highway": {
            "free": "видение события + карточки",
            "paid": "мейкинг недели и посадка на share",
            "sku": "pilot_14",
        },
        "closer_id": pack.get("id"),
        "brief": pack.get("brief"),
        "disclaimer": DISCLAIMER,
        "abstraction": essay,
        "cards": cards,
        "prompt": pack.get("prompt"),
        "event": event,
        "trends": pack.get("trends"),
        "comfort": pack.get("comfort"),
        "engine_brief": pack.get("engine_brief"),
        "audit": pack.get("audit"),
        "layers": pack.get("layers"),
    }
