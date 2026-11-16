"""Freelance packs TYPE_A + AI-ops + magistrals + support."""

from __future__ import annotations

import os
from typing import Any

from backend.core.freelance_packs.ai_ops.packs import AI_OPS, select_ai_ops
from backend.core.freelance_packs.magistrals import MAGISTRALS, pick_magistral
from backend.core.freelance_packs.support import support_offer
from backend.core.freelance_packs.type_a_programs import (
    PACKS as TYPE_A_PACKS,
    render_pack_prompt,
    select_type_a_pack,
)


def _isolated_pay_url() -> str:
    own = os.getenv("TRIBUTE_FREELANCE_URL", "").strip()
    if own:
        return own
    base = os.getenv("TRIBUTE_ACCESS_URL", "").strip() or "https://t.me/tribute"
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}start=isolated_freelance"


ADVANCED_ROLES = {
    "marketplace_lattice",
    "insight_chat",
    "client_geometry_deep",
    "demand_heat_overlay",
    "ads_weave",
    "post_lead_topology",
}


def apply_order_type_to_ideas(
    ideas: list[dict[str, Any]],
    lane: dict[str, Any],
) -> list[dict[str, Any]]:
    if not ideas:
        return ideas
    order = lane.get("order_type") or "TYPE_A"
    adv = bool(lane.get("advanced_only"))
    if order == "TYPE_A" and not adv:
        kept = [
            i
            for i in ideas
            if i.get("role") not in ADVANCED_ROLES
            and not any(
                w in (str(i.get("title") or "") + str(i.get("label") or "")).lower()
                for w in ("marketplace", "store", "token", "chip", "pdm", "маркетплейс")
            )
        ]
        if not kept:
            kept = ideas[:1]
        for i in kept:
            i["portfolio_cap"] = "type_a_default"
        return kept[:3]
    return ideas


def attach_pack(lane: dict[str, Any], brief: str) -> dict[str, Any]:
    order = lane.get("order_type") or "TYPE_A"
    flags = lane.get("thinking_flags") or []
    if order == "TYPE_B":
        pack = {
            "id": "style_series",
            "prompt": "Собери первый кусок в style_lock. Не новое направление.",
        }
        ai = None
    else:
        pack = select_type_a_pack(brief, flags)
        ai = select_ai_ops(brief)
    lane["pack"] = {
        "id": pack.get("id"),
        "when": pack.get("when"),
        "output": pack.get("output"),
        "anti": pack.get("anti"),
        "acceptance": pack.get("acceptance"),
        "prompt": render_pack_prompt(pack, brief) if "prompt" in pack else pack.get("prompt"),
        "isolated": True,
        "pay_url": _isolated_pay_url(),
        "grants_allo_month": False,
        "grants_access": False,
        "grants_flagship": False,
    }
    if ai:
        lane["ai_ops"] = {"id": ai["id"], "prompt": ai["prompt"].format(brief=brief[:600])}
    lane["support"] = support_offer(
        order,
        style_lock=(lane.get("brief") or {}).get("style_lock"),
    )
    sales = False
    lane["magistral"] = pick_magistral(order, sales=sales)
    return lane
