"""Contour 2.7 · NPODP. From the Karim Metrix plan, not a new price.

Non-pure object directing protocol. The only shared clock is the terminal:
a named outcome, a wider range the person can direct and sustain, and
influence that stays bounded. Intermediate scores are not the game.
The book does not record yield. The core does not place an exchange order.
Eval floor is imported and never lowered.
"""

from __future__ import annotations

from typing import Any

from backend.core.product_eval import THRESHOLD

VERSION = "2.7.0"
CODENAME = "NPODP"

# Scores the white paper names as the teenage high-score screen.
LUXURY = frozenset(
    {
        "views",
        "conversion",
        "payday",
        "yield",
        "royalty",
        "volume",
        "continuation",
        "agent_count",
        "distribution",
        "efficiency_show",
    }
)

EXTERNAL_CLOCKS = frozenset(
    {"platform", "market", "monday", "agent", "network", "external", "open"}
)

HARDWARE = frozenset(
    {
        "edge",
        "sensor",
        "actuator",
        "state_machine",
        "energy",
        "chemical",
        "food",
        "cold_chain",
    }
)

BOOK_KINDS = frozenset({"supporting_amount", "terminal_indicator"})


def _text(value: Any, limit: int = 160) -> str:
    return str(value or "").strip()[:limit]


def terminal_check(body: dict[str, Any]) -> dict[str, Any]:
    """Three parts, or the process is not admitted."""
    outcome = _text(body.get("outcome"))
    capacity = _text(body.get("capacity"))
    bounded = body.get("influence_bounded")
    reasons: list[str] = []
    if not outcome:
        reasons.append("no_named_outcome")
    if not capacity:
        reasons.append("capacity_not_named")
    if bounded is not True:
        reasons.append("influence_not_bounded")
    return {
        "admitted": not reasons,
        "reasons": reasons,
        "outcome": outcome,
        "capacity": capacity,
        "influence_bounded": bounded is True,
    }


def admit_child(raw: dict[str, Any] | None) -> dict[str, Any]:
    """A child of asynchrony is hardware, local, and silent. Not an agent."""
    row = raw or {}
    name = _text(row.get("id") or "child", 80) or "child"
    hardware = _text(row.get("hardware")).lower()
    clock = _text(row.get("clock")).lower()
    score = _text(row.get("score")).lower()
    reasons: list[str] = []
    if hardware not in HARDWARE:
        reasons.append("not_hardware")
    if clock in EXTERNAL_CLOCKS or bool(row.get("external_clock")):
        reasons.append("external_clock")
    if score in LUXURY:
        reasons.append("luxury_score")
    if row.get("influence_bounded") is not True:
        reasons.append("influence_not_bounded")
    if not _text(row.get("outcome")):
        reasons.append("no_named_outcome")
    if not _text(row.get("capacity")):
        reasons.append("capacity_not_named")
    if bool(row.get("poll")) or bool(row.get("announce")):
        reasons.append("not_silent")
    if bool(row.get("optimize_continuation")):
        reasons.append("agent_continuation")
    killed = False
    if bool(row.get("boundary_threatened")):
        reasons.append("local_kill")
        killed = True
    eval_score = row.get("eval")
    if eval_score is not None:
        try:
            if float(eval_score) < THRESHOLD:
                reasons.append("below_eval_floor")
                killed = True
        except (TypeError, ValueError):
            reasons.append("below_eval_floor")
            killed = True
    admitted = not reasons
    return {
        "id": name,
        "admitted": admitted,
        "killed": killed,
        "silent": admitted,
        "local": admitted,
        "hardware": hardware if admitted else None,
        "reasons": reasons,
        "agent": False,
        "polls": False,
    }


def shark_collapse(processes: list[Any] | None) -> dict[str, Any]:
    """Cease to address what needs an outside clock. Do not seize it."""
    addressed: list[dict[str, Any]] = []
    ceased: list[dict[str, Any]] = []
    for raw in processes or []:
        if not isinstance(raw, dict):
            continue
        child = admit_child(raw)
        if child["admitted"]:
            addressed.append({"id": child["id"], "addressed": True})
        else:
            ceased.append(
                {
                    "id": child["id"],
                    "addressed": False,
                    "reasons": child["reasons"],
                    "seized": False,
                    "negotiated": False,
                }
            )
    return {
        "addressed": addressed,
        "ceased": ceased,
        "seized": False,
        "winner": None,
    }


def free_zone(body: dict[str, Any] | None) -> dict[str, Any]:
    """The other person's tumbler is theirs. The contour does not flip it."""
    row = body or {}
    if bool(row.get("contour_sets_tumbler")):
        return {
            "free": False,
            "reason": "tumbler_is_not_ours",
            "external_sync": False,
        }
    hardware_continues = bool(row.get("hardware_continues"))
    external_sync = bool(row.get("external_sync"))
    tumbler_open = bool(row.get("tumbler_open"))
    free = hardware_continues and not external_sync and tumbler_open
    return {
        "free": free,
        "tumbler_open": tumbler_open,
        "hardware_continues": hardware_continues,
        "external_sync": False if free else external_sync,
        "central_operator": False,
    }


def supporting_ledger(body: dict[str, Any] | None) -> dict[str, Any]:
    """The amount keeps hardware able to serve the terminal. It is not yield."""
    row = body or {}
    if bool(row.get("unlock_features")) or bool(row.get("as_yield")):
        return {
            "kept": False,
            "reason": "not_a_yield_and_not_a_feature_key",
            "accept_moves": False,
            "extractive": False,
        }
    try:
        amount = float(row.get("amount"))
    except (TypeError, ValueError):
        amount = 0.0
    hardware = _text(row.get("hardware_id"))
    alive = amount > 0 and bool(hardware)
    return {
        "kept": alive,
        "amount": amount if alive else 0.0,
        "hardware_id": hardware if alive else "",
        "accept_moves": alive,
        "extractive": False,
        "yield_promised": False,
    }


def finance_book(entries: list[Any] | None) -> dict[str, Any]:
    """Only supporting amounts and terminal indicators. Luxury lines do not appear."""
    kept: list[dict[str, Any]] = []
    dropped: list[str] = []
    for raw in entries or []:
        if not isinstance(raw, dict):
            continue
        kind = _text(raw.get("kind")).lower()
        label = _text(raw.get("label") or kind, 80)
        if kind in BOOK_KINDS:
            kept.append({"kind": kind, "label": label})
        else:
            dropped.append(label or kind or "blank")
    return {
        "entries": kept,
        "dropped": dropped,
        "yield_recorded": False,
        "conversion_recorded": False,
        "distribution_recorded": False,
    }


def efficiency_exponent(body: dict[str, Any] | None) -> dict[str, Any]:
    """Frequency is the count of bursts. It is not a target and not an order."""
    row = body or {}
    if bool(row.get("place_orders")) or row.get("target_frequency") is not None:
        return {
            "ok": False,
            "reason": "frequency_is_not_a_target",
            "orders_placed": 0,
            "frequency": 0,
            "yield_promised": False,
        }
    bursts = row.get("bursts") or []
    count = 0
    if isinstance(bursts, list):
        for item in bursts:
            if not isinstance(item, dict):
                continue
            if bool(item.get("physical")) and bool(item.get("capacity_expanded")):
                count += 1
    return {
        "ok": True,
        "frequency": count,
        "orders_placed": 0,
        "optimized_for_volume": False,
        "yield_promised": False,
    }


def radar_listen(body: dict[str, Any] | None) -> dict[str, Any]:
    """Write a local fact. Do not join the outside clock."""
    row = body or {}
    signal = _text(row.get("signal"))
    return {
        "heard": bool(signal),
        "fact": signal,
        "joined": False,
        "clock_synced": False,
        "owns_public_graph": False,
    }


def run_npodp(payload: dict[str, Any] | None) -> dict[str, Any]:
    """One pass of contour 2.7. Paper stays secondary. Orders stay at zero."""
    data = payload or {}
    asked = data.get("eval_floor")
    lowered = False
    if asked is not None:
        try:
            lowered = float(asked) < THRESHOLD
        except (TypeError, ValueError):
            lowered = True
    children_in = data.get("children") or []
    if not isinstance(children_in, list):
        children_in = []
    children = [admit_child(row) for row in children_in if isinstance(row, dict)]
    collapse = shark_collapse(children_in)
    zone = free_zone(data.get("zone") if isinstance(data.get("zone"), dict) else {})
    support = supporting_ledger(
        data.get("support") if isinstance(data.get("support"), dict) else {}
    )
    book = finance_book(data.get("book") if isinstance(data.get("book"), list) else [])
    exponent = efficiency_exponent(
        data.get("exponent") if isinstance(data.get("exponent"), dict) else {}
    )
    heard = radar_listen(data.get("radar") if isinstance(data.get("radar"), dict) else {})
    return {
        "ok": True,
        "version": VERSION,
        "codename": CODENAME,
        "door": "2.1.0",
        "eval_floor": THRESHOLD,
        "floor_lowered": False,
        "floor_request_ignored": lowered,
        "yield_promised": False,
        "exchange_orders": False,
        "orders_placed": 0,
        "person_inside": False,
        "shared_clock": "terminal",
        "children": children,
        "collapse": collapse,
        "zone": zone,
        "support": support,
        "book": book,
        "exponent": exponent,
        "radar": heard,
    }
