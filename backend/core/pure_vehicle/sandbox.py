"""CLOSED SANDBOX 2.8. Agents stay seated. The person stays outside.

The ladder is a record, not eight products. 2.1 remains the door.
Eval floor is imported and never lowered. Yield and exchange orders are refused.
"""

from __future__ import annotations

from typing import Any

from backend.core.product_eval import THRESHOLD

DOOR_VERSION = "2.1.0"
RELEASE = "2.8.0"
CODENAME = "CLOSED SANDBOX"

# A brief is the only resource an agent may sit on.
# Money, a person, a body, a spirit, a deposit, an order — not a seat.
FORBIDDEN = frozenset(
    {
        "money",
        "cash",
        "yield",
        "royalty",
        "person",
        "body",
        "spirit",
        "karim",
        "deposit",
        "order",
        "signal",
        "purse",
    }
)

LINE: list[dict[str, str]] = [
    {
        "version": "2.1.0",
        "name": "ALLO",
        "rule": "One door at $50. Seven operations. No yield, no exchange order.",
    },
    {
        "version": "2.2.0",
        "name": "FENCE",
        "rule": "The system has an inside. The person is not inside it.",
    },
    {
        "version": "2.3.0",
        "name": "SEAT",
        "rule": "An agent has a seat and a kill. Agents do not share a purse.",
    },
    {
        "version": "2.4.0",
        "name": "LOG",
        "rule": "Opposition is written down. There is no winner over the person.",
    },
    {
        "version": "2.5.0",
        "name": "BRIEF",
        "rule": "The resource is the brief of a decision. Not someone's money.",
    },
    {
        "version": "2.6.0",
        "name": "NOT A SKU",
        "rule": "Karim is not sold. Spirit is not a tariff.",
    },
    {
        "version": "2.7.0",
        "name": "OBJECT",
        "rule": "The project is a finished object in the portfolio. It does not keep the person.",
    },
    {
        "version": "2.8.0",
        "name": "CLOSED SANDBOX",
        "rule": "An agent that left the contour is returned. It does not fight for the owner.",
    },
]


def release_line() -> dict[str, Any]:
    return {
        "ok": True,
        "version": RELEASE,
        "codename": CODENAME,
        "door": DOOR_VERSION,
        "eval_floor": THRESHOLD,
        "yield_promised": False,
        "exchange_orders": False,
        "person_inside": False,
        "spirit_sku": False,
        "power": "fence",
        "spirit": "outside",
        "steps": LINE,
    }


def close_sandbox(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Seat agents on a brief. Refuse escape, a lowered floor, and a captured person."""
    data = payload or {}
    agents = data.get("agents") or []
    if not isinstance(agents, list):
        agents = []
    # A client may ask to lower the floor. The answer is the real floor.
    asked = data.get("eval_floor")
    lowered = False
    if asked is not None:
        try:
            lowered = float(asked) < THRESHOLD
        except (TypeError, ValueError):
            lowered = True
    seated: list[dict[str, Any]] = []
    refused: list[dict[str, Any]] = []
    for raw in agents:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("id") or "agent")[:80]
        resource = str(raw.get("resource") or "brief").strip().lower()
        escaped = bool(raw.get("escaped"))
        reasons: list[str] = []
        if resource in FORBIDDEN:
            reasons.append("resource_refused")
        if escaped:
            reasons.append("returned_to_contour")
        score = raw.get("eval")
        if score is not None:
            try:
                if float(score) < THRESHOLD:
                    reasons.append("below_eval_floor")
            except (TypeError, ValueError):
                reasons.append("below_eval_floor")
        if reasons:
            refused.append({"id": name, "reasons": reasons, "seated": False})
        else:
            seated.append({"id": name, "resource": "brief", "seated": True, "kill": True})
    return {
        "ok": True,
        "version": RELEASE,
        "codename": CODENAME,
        "closed": True,
        "eval_floor": THRESHOLD,
        "floor_lowered": False,
        "floor_request_ignored": lowered,
        "yield_promised": False,
        "exchange_orders": False,
        "person_inside": False,
        "spirit_sku": False,
        "power": "fence",
        "spirit": "outside",
        "winner": None,
        "seated": seated,
        "refused": refused,
    }
