"""Compact identifier canon. Numbers are firmware, not destiny.

21 principles · 6 Super Program layers · 3 Circle steps · 12-dim embedding ·
slots 18/19 · 490 meanings. Public copy never treats these as luck.
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.paid.types import clamp01

# number → layer → public meaning → forbidden reading
CANON: list[dict[str, str]] = [
    {"n": "21", "layer": "Synthesis", "code": "SY", "means": "21-principle firmware", "forbid": "luck, destiny, natal chart"},
    {"n": "6", "layer": "Reality", "code": "RE", "means": "six Super Program layers", "forbid": "hexagram fortune"},
    {"n": "3", "layer": "Symmetry", "code": "SM", "means": "three Circle global steps", "forbid": "mystical trinity"},
    {"n": "12", "layer": "Value", "code": "VA", "means": "12-dim embedding assembly", "forbid": "zodiac houses"},
    {"n": "18", "layer": "Engage", "code": "EN", "means": "paid product core slot", "forbid": "magic price"},
    {"n": "19", "layer": "Ledger", "code": "LE", "means": "generativity slot", "forbid": "fate of the client"},
    {"n": "490", "layer": "Synthesis", "code": "SY", "means": "210 edges × meanings", "forbid": "lucky invoice number"},
]

LAYER_CODES = {
    "synthesis": "SY",
    "reality": "RE",
    "symmetry": "SM",
    "value": "VA",
    "engage": "EN",
    "ledger": "LE",
}
ZONE_CODES = {"infra_sol": "I", "cloud_sol": "C", "structure_fi": "S", "product_sol": "P"}
KIND_CODES = {
    "chain": "CH",
    "artefact": "AR",
    "case": "CS",
    "resource": "RS",
    "handoff": "HO",
    "pack": "PK",
}

FORBIDDEN_GLOSS = (
    "удача",
    "судьба",
    "гороскоп",
    "наталь",
    "luck",
    "destiny",
    "zodiac",
    "fortune",
)


def canon_table() -> list[dict[str, str]]:
    return [dict(r) for r in CANON]


def _h(*parts: str, n: int = 4) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:n].upper()


def pick_canon_number(layer: str) -> str:
    layer_l = (layer or "synthesis").lower()
    for row in CANON:
        if row["layer"].lower() == layer_l or row["code"] == LAYER_CODES.get(layer_l):
            return row["n"]
    return "3"


def sigil(
    *,
    kind: str,
    layer: str = "symmetry",
    zone: str = "product_sol",
    fragments: list[str] | None = None,
    canon_n: str | None = None,
) -> str:
    """Short public name. Stable if RRC fragments stay the same."""
    lc = LAYER_CODES.get((layer or "").lower(), "SM")
    zc = ZONE_CODES.get(zone, "P")
    kc = KIND_CODES.get(kind, "CH")
    n = canon_n or pick_canon_number(layer)
    stem = _h(*(sorted(fragments or []) or [kind, layer, zone]), n=4)
    return f"{lc}{zc}-{kc}{n}-{stem}"


def chain_sigil(chain_seed: str, fragments: list[str] | None = None) -> str:
    fr = list(fragments or []) or [chain_seed]
    return sigil(kind="chain", layer="symmetry", zone="product_sol", fragments=fr, canon_n="3")


def artefact_sigil(artefact_id: str, domain: str = "hybrid") -> str:
    layer = "value" if domain == "qol" else "reality" if domain == "safety" else "engage"
    return sigil(kind="artefact", layer=layer, zone="product_sol", fragments=[artefact_id], canon_n="12")


def case_sigil(chain_seed: str, closed_slots: list[str]) -> str:
    return sigil(
        kind="case",
        layer="ledger",
        zone="product_sol",
        fragments=[chain_seed, *sorted(closed_slots)],
        canon_n="19",
    )


def public_gloss(sig: str, lang: str = "en") -> str:
    if lang.startswith("ru"):
        return f"Короткое имя слоя ({sig}). Число — канон прошивки, не удача."
    return f"Short layer name ({sig}). The number is firmware canon, not luck."


def reject_esoteric(text: str) -> bool:
    low = (text or "").lower()
    return any(w in low for w in FORBIDDEN_GLOSS)


def sort_key(name: str, metrics: dict[str, Any] | None = None) -> tuple:
    """Assembler / Anti-Down: metrics first, then canon name."""
    m = metrics or {}
    assembly = clamp01(float(m.get("assembly") or m.get("assembly_score") or 0))
    consistency = clamp01(float(m.get("consistency") or 0))
    return (-assembly, -consistency, str(name or ""))
