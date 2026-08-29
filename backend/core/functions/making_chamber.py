"""Making chamber — first-class Mini App function (section 3).

Weaves abstraction + cards + rewritten engine prompt + screened trend
into a week that can be lived. Not a plan.
"""

from __future__ import annotations

from typing import Any

from backend.core.content_closer.making import MakingRefused, run_making_chamber
from backend.core.content_closer.pipeline import run_closer


def run_making_function(
    brief: str,
    *,
    lang: str = "ru",
    closer: dict[str, Any] | None = None,
    extra: str = "",
) -> dict[str, Any]:
    pack = closer
    if pack is None:
        pack = run_closer(brief, lang=lang, with_comfort=True, with_making=False)
    try:
        making = run_making_chamber(pack, extra=extra, lang=lang)
    except MakingRefused as exc:
        return {
            "ok": False,
            "function": "making_chamber",
            "error": str(exc),
            "need": "landing_first",
        }
    return {
        "ok": True,
        "function": "making_chamber",
        "making": making,
        "closer_id": pack.get("id"),
        "audit": pack.get("audit"),
        "cards": (pack.get("cards") or {}).get("codes"),
        "trend": ((pack.get("trends") or {}).get("primary") or {}).get("id"),
        "message": making.get("message"),
    }
