"""
Author Personality product — reveals the business author's identity.

Concepts adapted from context-engineering / harness discourse
(ref: Yersham · «Новые правила контекстной инженерии…» / Claude Opus-class autonomy):

- Intent & end goals over long instruction dumps
- Success criteria the author actually holds
- Autonomy band (what the system may do alone)
- Golden examples (aesthetic / quality preferences)
- Stance / voice (how the author shows up in market)
- Trust surface (what must stay human-signed)

This is a sellable product surface inside Generate, not a cosmetic badge.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def _clip(t: str, n: int = 160) -> str:
    t = re.sub(r"\s+", " ", (t or "").strip())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


# Archetype axes (0..1) — used for routing + R&D stance
AXES = (
    "builder",       # ships systems / packs
    "operator",      # ops, margin, rework
    "storyteller",   # brand / audience
    "analyst",       # metrics, risk, assets
    "craftsman",     # quality, editorial, design
    "connector",     # network, coop, marketplace
)


def build_author_personality(
    business_text: str,
    *,
    profile: dict[str, Any] | None = None,
    project_name: str = "",
    answers: dict[str, str] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """Derive a stable author personality product from brief + profile."""
    L = _lang(lang)
    t = (business_text or "").lower()
    prof = profile or {}
    ans = answers or {}
    name = project_name or _clip(business_text, 48) or "Author"

    scores = {a: 0.12 for a in AXES}
    rules: list[tuple[str, tuple[str, ...], float]] = [
        ("builder", ("билдер", "builder", "архитект", "architecture", "pack", "карточ", "product", "saas"), 0.22),
        ("operator", ("rework", "handoff", "марж", "ops", "delivery", "логист", "cost", "агент"), 0.22),
        ("storyteller", ("бренд", "brand", "контент", "audience", "creator", "story"), 0.2),
        ("analyst", ("метрик", "kpi", "risk", "актив", "asset", "unit econ", "себестоим"), 0.2),
        ("craftsman", ("дизайн", "design", "quality", "editorial", "craft", "schema"), 0.18),
        ("connector", ("network", "marketplace", "кооп", "coop", "партнёр", "match", "community"), 0.18),
    ]
    for axis, kws, w in rules:
        if any(k in t for k in kws):
            scores[axis] = min(1.0, scores[axis] + w)
    if prof.get("is_library"):
        scores["builder"] = min(1.0, scores["builder"] + 0.25)
        scores["craftsman"] = min(1.0, scores["craftsman"] + 0.18)
        scores["connector"] = min(1.0, scores["connector"] + 0.1)

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    primary = ranked[0][0]
    secondary = ranked[1][0]

    archetypes = {
        "builder": (_d(L, "Системный билдер", "Systems builder"), _d(L, "Собирает геометрию и pack'и", "Assembles geometry and packs")),
        "operator": (_d(L, "Оператор маржи", "Margin operator"), _d(L, "Режет rework и leakage", "Cuts rework and leakage")),
        "storyteller": (_d(L, "Носитель угла", "Angle carrier"), _d(L, "Держит narrative и trust", "Holds narrative and trust")),
        "analyst": (_d(L, "Аналитик риска", "Risk analyst"), _d(L, "Метрики раньше hype", "Metrics before hype")),
        "craftsman": (_d(L, "Ремесленник качества", "Quality craftsman"), _d(L, "Schema, ship gate, WIP", "Schema, ship gate, WIP")),
        "connector": (_d(L, "Связной рынка", "Market connector"), _d(L, "Match, coop, settlement", "Match, coop, settlement")),
    }
    p_label, p_blurb = archetypes[primary]
    s_label, _ = archetypes[secondary]

    # Context-engineering style: goals / intent / success criteria (not long prompt)
    intent = ans.get("non_goals") and _d(
        L,
        f"Двигать unit «{ans.get('unit_of_value') or prof.get('unit')}» в окне {ans.get('constraint_time', '21d')}, не раздувая scope.",
        f"Move unit «{ans.get('unit_of_value') or prof.get('unit')}» inside {ans.get('constraint_time', '21d')} without scope bloat.",
    ) or _d(
        L,
        "Собрать доказуемое ядро и один paid path.",
        "Ship a provable core and one paid path.",
    )
    goals = [
        _d(L, "Зафиксировать identity и unit", "Lock identity and unit"),
        _d(L, "1 channel log с artifact", "1 channel log with artifact"),
        _d(L, "Calendar kill на T1", "Calendar kill on T1"),
    ]
    success_criteria = [
        ans.get("success_metric") or prof.get("metric") or _d(L, "1 paid unit / 21d", "1 paid unit / 21d"),
        _d(L, "Evidence grade ≥ B на ключевых warrants", "Evidence grade ≥ B on key warrants"),
        _d(L, "Нет auto-yield claims", "No auto-yield claims"),
    ]
    golden = [
        _d(
            L,
            "Карточка с context · blocks · boundary · failure · proof — одна schema.",
            "Card with context · blocks · boundary · failure · proof — one schema.",
        ),
        _d(
            L,
            "Решение S* с kill и owner, не «варианты на подумать».",
            "S* decision with kill and owner, not open-ended options.",
        ),
    ]

    # Stable fingerprint for memory
    fp = hashlib.sha1(f"{primary}|{secondary}|{_clip(business_text, 80)}".encode()).hexdigest()[:12]

    summary = _d(
        L,
        f"**{name}** — {p_label} (+ {s_label}). {p_blurb}. "
        f"Intent: {intent} "
        f"Система работает в режиме **context engineering**: цели и критерии, не микро-инструкции.",
        f"**{name}** — {p_label} (+ {s_label}). {p_blurb}. "
        f"Intent: {intent} "
        f"System runs in **context engineering** mode: goals and criteria, not micro-instructions.",
    )

    rd_paragraph = _d(
        L,
        f"Author stance: primary=`{primary}` secondary=`{secondary}`. "
        f"Полоса автономии harness: AI собирает memo/cards/skills; signer держит cash, approval, live touches. "
        f"Golden examples задают aesthetic floor без длинного system prompt.",
        f"Author stance: primary=`{primary}` secondary=`{secondary}`. "
        f"Harness autonomy band: AI assembles memo/cards/skills; signer owns cash, approval, live touches. "
        f"Golden examples set the aesthetic floor without a long system prompt.",
    )

    product = {
        "id": "author_personality",
        "sku": "author_personality_reveal",
        "name": _d(L, "Личность автора бизнеса", "Business author personality"),
        "tagline": _d(
            L,
            "Кто вы как билдер: intent · критерии · stance · golden examples",
            "Who you are as a builder: intent · criteria · stance · golden examples",
        ),
        "price_note": _d(L, "Входит в Generate · free surface", "Included in Generate · free surface"),
        "free": True,
    }

    return {
        "module": "AuthorPersonality",
        "version": "1.0",
        "fingerprint": fp,
        "product": product,
        "display_name": name,
        "primary_axis": primary,
        "secondary_axis": secondary,
        "primary_label": p_label,
        "secondary_label": s_label,
        "axes": {k: round(v, 3) for k, v in ranked},
        "intent": intent,
        "goals": goals,
        "success_criteria": success_criteria,
        "golden_examples": golden,
        "autonomy_band": {
            "ai_may": _d(
                L,
                "Маршрутизация, R&D memo, карточки, skill distill, assist draft steps",
                "Routing, R&D memo, cards, skill distill, assist draft steps",
            ),
            "human_must": _d(
                L,
                "Cash ceiling, implementation approval, live channel, final pay decision",
                "Cash ceiling, implementation approval, live channel, final pay decision",
            ),
        },
        "trust_surface": _d(
            L,
            "Доверие = критерии успеха + kill dates, не «поверь модели».",
            "Trust = success criteria + kill dates, not “believe the model”.",
        ),
        "summary": summary,
        "rd_paragraph": rd_paragraph,
        "ref_concepts": [
            "context_engineering",
            "intent_over_instructions",
            "success_criteria",
            "harness_memory_tools",
            "dynamic_skills",
            "golden_examples",
            "high_level_oversight",
        ],
        "source_ref": "https://youtu.be/wT0LOkQVgNc",
        "lang": L,
    }
