"""Metrix AI auto-rewrites cards into a prompt for the main engine.

Input: abstract idea + function cards + screened trend + event vision.
Output: a master prompt the main engine (demo highway / request pipeline /
build_prompt_engine) can execute — adapted to the screened trend,
considering the task-card that came from the abstract idea.
"""

from __future__ import annotations

from typing import Any

from backend.core.business_gen.build_prompt_engine import build_project_prompt


def _card_rails(cards: list[dict[str, Any]]) -> str:
    lines = []
    for c in cards:
        lines.append(
            f"- {c['code']} `{c['designation']}` · fn={c['function']} · obj={c['object']}\n"
            f"  TASK: {c['action']}\n"
            f"  UNIT: {c['unit']}\n"
            f"  KILL: {c['kill']}\n"
            f"  MONEY: {c['money']}"
        )
    return "\n".join(lines)


def rewrite_prompt(
    *,
    brief: str,
    essay: dict[str, Any],
    cards: dict[str, Any],
    event: dict[str, Any],
    trends: dict[str, Any],
    lang: str = "ru",
) -> dict[str, Any]:
    ru = not (lang or "").lower().startswith("en")
    items = cards.get("items") or []
    trend = trends.get("primary") or {}
    arch = essay.get("archetype") or ""
    title = event.get("title") or arch
    codes = [c.get("code") for c in items]

    rails = _card_rails(items)
    trend_block = (
        f"id={trend.get('id')} · {trend.get('name_ru')}\n"
        f"family={trend.get('family')} · layer={trend.get('layer')}\n"
        f"adapt: {trend.get('adapt')}\n"
        f"rhyme: {trend.get('crypto_rhyme')}\n"
        f"NOT a trading signal. {trends.get('disclaimer') or ''}"
    )
    abstract = essay.get("essay") or ""

    master = f"""# Engine prompt · {title}
# Source: abstraction → function cards → screened trend
# Do not flatten the abstraction into slogans. Execute the cards.

## Abstract idea (keep density, do not summarise into a pitch)
Archetype: {arch} / {essay.get('secondary')}
Register: {essay.get('register')}
Cadence: {essay.get('cadence')}

{abstract}

## Event vision (this IS the landing)
{event.get('vision_text') or ''}

Invitation (not a CTA): {event.get('invitation') or ''}
Anti-CTA: {event.get('anti_cta') or ''}

## Screened trend to implement (GROWTH AI)
{trend_block}

## Task-cards (the assignment — execute every code)
{rails}

## Hard rails for the main engine
1. Lead with abstraction. The first human-visible layer is the essay, not a SaaS hero.
2. Then the card table with functional designations (code, fn, obj, unit, kill, money).
3. Adapt implementation to the screened trend `{trend.get('id')}` on the client's project.
   Derivative product, not a new brand.
4. Landing = vision of an event. No studio button. A room.
5. Engine top module = quiet assistant (ideas + growth points, no pulse spike).
6. Last section = Making (камера сборки). Day 1 of any calendar = event entry, never «research».
7. Money: success fee / share of a changed revenue structure. No retainer for presence.
8. Founder warmth (X + Telegram) uses inversion, not ROI argument.
9. Fear protocol before financial-structure change is mandatory if money_structure is live.
10. Kill the pack if it promises a state, sells signals, spawns extra objects, or climbs the impossible.

## Deliverable the engine must emit
- abstraction essay (register preserved)
- card table (all codes: {", ".join(codes)})
- event landing copy
- rewritten engine brief (this document, executable)
- making chamber input (FN-MAKE)
- satellite brief if FN-SAT present
- close-into-integration script if FN-CLOSE present

## Anti-patterns
- «Ещё один AI-чат»
- Landing as pricing page
- Studio as a hamburger button
- Trend as buy/sell signal
- Comfort assistant that cheers
- Making as a Gantt of research
- Success fee charged before structure moved

## Original situation (raw)
{(brief or '')[:1500]}
"""

    engine_brief = (
        f"{arch}. Событие: {title}. "
        f"Тренд: {trend.get('name_ru')}. "
        f"Задание-карточки: {', '.join(codes)}. "
        f"Ситуация: {(brief or '')[:400]} "
        f"Реализовать как видение события + производный продукт под тренд, "
        f"единица share, без обещания состояния."
    )

    # reuse existing build-prompt rails so the main engine recognises the shape
    wrapped = build_project_prompt(
        project_name=title,
        business_text=engine_brief,
        path={"id": "closer_event", "unit": "one entered event + one share unit", "spine": ["event", "cards", "making"]},
        segment={"id": "founder_motion"},
        unit="one entered event + share of moved structure",
        lang=lang,
        extra={
            "abstraction_archetype": arch,
            "trend_id": trend.get("id"),
            "card_codes": codes,
            "section": "engine",
        },
    )

    quoted_codes = [c for c in codes if c and c in master]
    strength = round(
        min(
            1.0,
            0.2
            + 0.08 * min(8, len(items))
            + 0.15 * (1.0 if trend.get("id") else 0.0)
            + 0.15 * (1.0 if abstract else 0.0)
            + 0.1 * (1.0 if event.get("vision_text") else 0.0)
            + 0.02 * min(20, len(quoted_codes)),
        ),
        3,
    )

    return {
        "module": "PromptRewrite",
        "version": "1.0.0",
        "title": title,
        "master": master,
        "engine_brief": engine_brief,
        "system": wrapped.get("system"),
        "wrapped": wrapped,
        "codes_quoted": quoted_codes,
        "trend_id": trend.get("id"),
        "strength": strength,
        "lang": "ru" if ru else "en",
        "message": (
            f"Промпт для основного движка · strength={strength} · trend={trend.get('id')}"
            if ru
            else f"Main-engine prompt · strength={strength} · trend={trend.get('id')}"
        ),
    }
