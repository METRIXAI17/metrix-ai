"""
Probabilistic originality injections into content-rich sections of three directions.

Replaces generic turns of phrase with unique Metrix-voice variants by probability.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


# Direction → phrase banks (generic → unique variants)
BANKS: dict[str, list[dict[str, Any]]] = {
    "product_pack": [
        {
            "pattern": r"\bготовое решение\b",
            "alts_ru": [
                "собранный контур под scope",
                "исполняемый pack, не витрина",
                "result pack с границами",
            ],
            "pattern_en": r"\bready[- ]made solution\b",
            "alts_en": [
                "scoped executable contour",
                "result pack — not a storefront",
                "bounded shippable pack",
            ],
            "p": 0.72,
        },
        {
            "pattern": r"\bуникальн\w*\b",
            "alts_ru": [
                "нешаблонный",
                "с собственной осью автора",
                "hash-уникальный под бриф",
            ],
            "pattern_en": r"\bunique\b",
            "alts_en": [
                "non-template",
                "author-axis native",
                "hash-unique to the brief",
            ],
            "p": 0.45,
        },
        {
            "pattern": r"\bмасштабир\w*\b",
            "alts_ru": ["расти по unit, не по шуму", "расширять после proof"],
            "pattern_en": r"\bscalable\b",
            "alts_en": ["grow by unit, not noise", "expand after proof"],
            "p": 0.55,
        },
    ],
    "unit_pack": [
        {
            "pattern": r"\bмонетизац\w*\b",
            "alts_ru": [
                "оплата за unit, не за воздух",
                "paid unit с COGS-временем",
                "unit margin после time-COGS",
            ],
            "pattern_en": r"\bmonetiz\w*\b",
            "alts_en": [
                "pay for unit, not air",
                "paid unit with time-COGS",
                "unit margin after time-COGS",
            ],
            "p": 0.7,
        },
        {
            "pattern": r"\bценност\w*\b",
            "alts_ru": ["реализованная mid-ценность", "value vs tariff gap"],
            "pattern_en": r"\bvalue proposition\b",
            "alts_en": ["realized mid-value", "value vs tariff gap"],
            "p": 0.5,
        },
        {
            "pattern": r"\bKPI\b",
            "alts_ru": ["одна pilot-метрика", "scoreboard, не 12 KPI"],
            "pattern_en": r"\bKPIs?\b",
            "alts_en": ["one pilot metric", "scoreboard, not 12 KPIs"],
            "p": 0.65,
        },
    ],
    "ch_network": [
        {
            "pattern": r"\bсетев\w*\s+эффект\w*\b",
            "alts_ru": [
                "тёплый DM-лист + 1 proof-артефакт",
                "12 касаний / 7 дней, не «сеть»",
            ],
            "pattern_en": r"\bnetwork effects?\b",
            "alts_en": [
                "warm DM list + 1 proof artifact",
                "12 touches / 7 days — not «network»",
            ],
            "p": 0.8,
        },
        {
            "pattern": r"\bмаркетинг\w*\b",
            "alts_ru": ["channel log, не SMM-подписка", "proof раньше обещаний"],
            "pattern_en": r"\bmarketing\b",
            "alts_en": ["channel log, not SMM retainer", "proof before promises"],
            "p": 0.55,
        },
        {
            "pattern": r"\bаудитори\w*\b",
            "alts_ru": ["lookalike касания", "точный список builders"],
            "pattern_en": r"\baudience\b",
            "alts_en": ["lookalike touches", "precise builder list"],
            "p": 0.5,
        },
    ],
}

# Generic filler replacements (all directions)
GLOBAL_BANK: list[dict[str, Any]] = [
    {
        "pattern": r"\bв современном мире\b",
        "alts_ru": ["в вашем контуре", "на текущем unit-цикле"],
        "pattern_en": r"\bin today's world\b",
        "alts_en": ["in your contour", "on the current unit cycle"],
        "p": 0.9,
    },
    {
        "pattern": r"\bкомплексн\w*\s+подход\w*\b",
        "alts_ru": ["составной edge mesh", "Orient → pick → ship"],
        "pattern_en": r"\bholistic approach\b",
        "alts_en": ["compound edge mesh", "Orient → pick → ship"],
        "p": 0.85,
    },
    {
        "pattern": r"\bсинерг\w*\b",
        "alts_ru": ["составная функция модулей", "edge-эффект"],
        "pattern_en": r"\bsynerg\w*\b",
        "alts_en": ["compound module function", "edge effect"],
        "p": 0.8,
    },
]


def _seed_prob(seed: str, key: str) -> float:
    h = hashlib.sha256(f"{seed}:{key}".encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _pick(alts: list[str], seed: str, key: str) -> str:
    if not alts:
        return ""
    idx = int(_seed_prob(seed, key + ":i") * len(alts)) % len(alts)
    return alts[idx]


def inject_originality(
    text: str,
    *,
    direction: str = "product_pack",
    lang: str = "ru",
    seed: str = "",
    force_p: float | None = None,
) -> dict[str, Any]:
    """Apply probabilistic replacements; return text + stats."""
    if not text:
        return {"text": text or "", "replacements": 0, "originality": 0.0, "direction": direction}

    L = "en" if (lang or "").lower().startswith("en") else "ru"
    seed = seed or text[:64]
    banks = list(GLOBAL_BANK) + list(BANKS.get(direction) or [])
    out = text
    reps: list[dict[str, str]] = []

    for i, rule in enumerate(banks):
        pat = rule.get("pattern_en") if L == "en" else rule.get("pattern")
        alts = rule.get("alts_en") if L == "en" else rule.get("alts_ru")
        if not pat or not alts:
            continue
        p = float(force_p if force_p is not None else rule.get("p", 0.5))
        # deterministic roll
        roll = _seed_prob(seed, f"{direction}:{i}:{pat}")
        if roll > p:
            continue

        def _sub(m: re.Match[str], _alts=alts, _i=i, _pat=pat) -> str:
            repl = _pick(_alts, seed, f"repl:{_i}:{m.group(0)}")
            reps.append({"from": m.group(0), "to": repl, "direction": direction})
            return repl

        out, n = re.subn(pat, _sub, out, count=2, flags=re.IGNORECASE)
        if n == 0 and L == "ru":
            # try en patterns on mixed text lightly
            pass

    # originality score from replacement density
    density = min(1.0, len(reps) / 6.0 + (0.15 if len(out) > 200 else 0.05))
    return {
        "text": out,
        "replacements": len(reps),
        "log": reps[:12],
        "originality": round(0.4 + 0.6 * density, 4),
        "direction": direction,
        "lang": L,
    }


def inject_three_directions(
    sections: dict[str, str],
    *,
    lang: str = "ru",
    seed: str = "",
) -> dict[str, Any]:
    """
    sections keys ideally: product_pack, unit_pack, ch_network
    (or any mapping direction → rich text)
    """
    results: dict[str, Any] = {}
    total_reps = 0
    orig_scores: list[float] = []
    for direction, body in (sections or {}).items():
        dkey = direction if direction in BANKS else _guess_direction(direction)
        r = inject_originality(body or "", direction=dkey, lang=lang, seed=f"{seed}:{dkey}")
        results[direction] = r
        total_reps += int(r["replacements"])
        orig_scores.append(float(r["originality"]))
    mean_o = sum(orig_scores) / len(orig_scores) if orig_scores else 0.5
    return {
        "module": "OriginalityInject",
        "version": "1.0.0",
        "by_direction": results,
        "total_replacements": total_reps,
        "originality": round(mean_o, 4),
        "message": f"Injected {total_reps} uniqueness swaps across {len(results)} directions",
    }


def _guess_direction(key: str) -> str:
    k = (key or "").lower()
    if "unit" in k:
        return "unit_pack"
    if "channel" in k or "ch_" in k or "network" in k or "log" in k:
        return "ch_network"
    return "product_pack"


def enrich_core_sections(
    core_report: dict[str, Any],
    *,
    lang: str = "ru",
    seed: str = "",
) -> dict[str, Any]:
    """Pull richest text from core_report into three directions and inject."""
    cr = core_report or {}
    md = cr.get("markdown") or ""
    # Split-ish: use decision cards / architecture / channel
    arch = " ".join(
        f"{c.get('title','')}. {c.get('claim','') or c.get('proof','')}"
        for c in (cr.get("architecture_cards") or [])[:6]
    )
    unit = " ".join(
        f"{d.get('id','')}: {d.get('chosen','') or d.get('title','')}"
        for d in (cr.get("decision_cards") or [])[:6]
    )
    clog = cr.get("channel_log_7d") or {}
    ch = f"{clog.get('rule','')} " + " ".join(
        f"{d.get('label','')}: {d.get('action','')}" for d in (clog.get("days") or [])[:7]
    )
    # fallback to markdown slices
    if len(arch) < 40:
        arch = md[:900]
    if len(unit) < 40:
        unit = md[400:1300] if len(md) > 400 else md
    if len(ch) < 40:
        ch = md[-900:] if len(md) > 900 else md

    return inject_three_directions(
        {
            "product_pack": arch,
            "unit_pack": unit,
            "ch_network": ch,
        },
        lang=lang,
        seed=seed or (cr.get("title") or "metrix"),
    )
