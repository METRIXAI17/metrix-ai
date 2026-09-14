"""Coop open-opp: consult slot, flags, brief normalizer, deadlock, hand-off."""

from __future__ import annotations

import os
from typing import Any

from backend.core.coop.brief_normalizer import classify_order, normalize_brief
from backend.core.coop.consult_slot import build_consult
from backend.core.coop.consult_patterns.flags import detect_flags, has_flag
from backend.core.coop.deadend import DeadendRouter, is_deadlock


def advanced_only(extra: dict[str, Any] | None = None) -> bool:
    if extra and (
        extra.get("advanced_only")
        or extra.get("advanced")
        or str(extra.get("mode") or "") == "advanced_only"
    ):
        return True
    return os.getenv("METRIX_ADVANCED_ONLY", "").strip() in ("1", "true", "yes")


def run_coop_lane(
    brief: str,
    *,
    extra_params: dict[str, Any] | None = None,
    prior_style: dict[str, str] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    _ = lang
    consult = build_consult(brief, prior_style=prior_style)
    flags = consult["thinking_flags"]
    adv = advanced_only(extra_params)
    if consult["order_type"] == "TYPE_A" and not adv:
        forbidden = ("marketplace", "store", "token", "маркетплейс", "токен", "chip", "PdM")
        consult["forbid_surface"] = list(forbidden)
    consult["advanced_only"] = adv
    consult["handoff"] = {
        "to": "consult-questions" if has_flag(flags, "P6") else "pack-select",
        "allow_codegen": consult["allow_codegen"] and not has_flag(flags, "P6"),
        "reason": "P6 NO_NUMBER" if has_flag(flags, "P6") else "ok",
    }
    return consult


__all__ = [
    "DeadendRouter",
    "advanced_only",
    "build_consult",
    "classify_order",
    "detect_flags",
    "has_flag",
    "is_deadlock",
    "normalize_brief",
    "run_coop_lane",
]
