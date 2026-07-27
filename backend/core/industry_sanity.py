"""Load industry sanity packs for judgment checks + originality depth."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.config import BACKEND_ROOT

SANITY_DIR = BACKEND_ROOT / "data" / "industry_sanity"


@lru_cache(maxsize=16)
def load_sanity(industry_id: str) -> dict[str, Any]:
    path = SANITY_DIR / f"{industry_id}.json"
    if not path.exists():
        return {"industry_id": industry_id, "business_variants": [], "sane_patterns": []}
    return json.loads(path.read_text(encoding="utf-8"))


def match_variant(industry_id: str, business: str) -> dict[str, Any] | None:
    pack = load_sanity(industry_id)
    text = (business or "").lower()
    best = None
    best_hits = 0
    for v in pack.get("business_variants") or []:
        hits = sum(1 for s in v.get("signals") or [] if s.lower() in text)
        if hits > best_hits:
            best_hits = hits
            best = v
    if best and best_hits > 0:
        return {**best, "signal_hits": best_hits}
    return None


def sanity_check_mechanism(industry_id: str, mechanism_title: str, business: str) -> dict[str, Any]:
    pack = load_sanity(industry_id)
    title = (mechanism_title or "").lower()
    flags = []
    for bad in pack.get("insane_patterns") or []:
        # soft: if key words of insane pattern all appear — flag
        keys = [w for w in bad.lower().split() if len(w) > 4][:4]
        if keys and sum(1 for k in keys if k in title or k in (business or "").lower()) >= 3:
            flags.append({"type": "insane_pattern_risk", "pattern": bad})
    variant = match_variant(industry_id, business)
    return {
        "industry_id": industry_id,
        "variant": variant,
        "module_map": pack.get("module_map_for_change_owner") or [],
        "sane_patterns": pack.get("sane_patterns") or [],
        "flags": flags,
        "ok": len(flags) == 0,
        "track_priors": pack.get("track_priors") or {},
    }
