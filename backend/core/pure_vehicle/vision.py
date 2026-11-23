"""Vision 2.9. Concept, then a solution only where the data is real.

The public order is: volume as the aim, your own table,
a bridge you can show a friend, a build closed on that data, ideas after.
A purchase names two people and the amount. It is not a lecture.
Yield is not promised. An exchange order is not placed.
"""

from __future__ import annotations

from typing import Any

from backend.core.product_eval import THRESHOLD
from backend.core.pure_vehicle.traction import pull as traction_pull

VERSION = "2.9.0"
CODENAME = "VISION"

# Ways of moving money that are not a legal bridge.
REFUSED_PATHS = frozenset(
    {
        "envelope",
        "cash_envelope",
        "no_docs",
        "mixer",
        "off_book",
        "obnal",
    }
)


def _text(value: Any, limit: int = 240) -> str:
    return str(value or "").strip()[:limit]


def _rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def valuable_data(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    kept: list[dict[str, str]] = []
    for row in rows:
        name = _text(row.get("name"), 80)
        value = _text(row.get("value"), 120)
        if not name or not value:
            continue
        if row.get("real") is not True:
            continue
        kept.append({"name": name, "value": value})
    return kept


def cash_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """A person's till. In, due, payable. No yield column."""
    lines: list[dict[str, Any]] = []
    for row in rows:
        label = _text(row.get("label"), 80)
        if not label:
            continue
        try:
            came = float(row.get("in") or 0)
            due = float(row.get("due") or 0)
            payable = float(row.get("payable") or 0)
        except (TypeError, ValueError):
            continue
        lines.append(
            {
                "label": label,
                "in": came,
                "due": due,
                "payable": payable,
            }
        )
    return {
        "lines": lines,
        "for_a_person": True,
        "yield_column": False,
    }


def bridge(body: dict[str, Any] | None) -> dict[str, Any]:
    """Who gave, who took, what number. A hidden envelope is not a bridge."""
    row = body or {}
    path = _text(row.get("path")).lower()
    if path in REFUSED_PATHS or bool(row.get("off_book")):
        return {"open": False, "reason": "not_a_bridge", "path": "refused"}
    giver = _text(row.get("from") or row.get("giver"), 80)
    taker = _text(row.get("to") or row.get("taker"), 80)
    amount = _text(row.get("amount"), 80)
    if not giver or not taker or not amount:
        return {"open": False, "reason": "bridge_incomplete", "missing": [
            key for key, val in (("from", giver), ("to", taker), ("amount", amount)) if not val
        ]}
    return {
        "open": True,
        "path": "show_a_friend",
        "from": giver,
        "to": taker,
        "amount": amount,
        "showable": True,
    }


def semi_closed_purchase(body: dict[str, Any] | None) -> dict[str, Any]:
    """Two names and an amount. No stage, no lecture."""
    row = body or {}
    parties = _text(row.get("parties"), 160)
    scope = _text(row.get("scope"), 200)
    if not parties or not scope:
        return {"open": False, "reason": "names_or_amount_missing"}
    if bool(row.get("hidden")) or bool(row.get("off_book")):
        return {"open": False, "reason": "not_showable"}
    return {
        "open": True,
        "parties": parties,
        "scope": scope,
        "showable": True,
    }


def run_vision(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload or {}
    concept = _text(data.get("concept"))
    real = valuable_data(_rows(data.get("data")))
    solution = ""
    if concept and real:
        solution = _text(data.get("solution")) or concept
    engineering_open = bool(real)
    ideas = _text(data.get("ideas")) if engineering_open else ""
    asked = data.get("eval_floor")
    ignored = False
    if asked is not None:
        try:
            ignored = float(asked) < THRESHOLD
        except (TypeError, ValueError):
            ignored = True
    return {
        "ok": True,
        "version": VERSION,
        "codename": CODENAME,
        "public_price": None,
        "door_retired": True,
        "eval_floor": THRESHOLD,
        "floor_lowered": False,
        "floor_request_ignored": ignored,
        "yield_promised": False,
        "exchange_orders": False,
        "orders_placed": 0,
        "order": [
            "aim",
            "volume_purchase",
            "tables",
            "bridge",
            "engineering",
            "ideas",
        ],
        "aim": "volume_purchase",
        "concept": concept,
        "concept_holds_the_build": bool(concept),
        "data": real,
        "solution": solution if real else "",
        "solution_admitted": bool(solution) and bool(real),
        "engineering_open": engineering_open,
        "engineering_closed_on": [row["name"] for row in real],
        "ideas": ideas,
        "table": cash_table(_rows(data.get("table"))),
        "bridge": bridge(data.get("bridge") if isinstance(data.get("bridge"), dict) else {}),
        "purchase": semi_closed_purchase(
            data.get("purchase") if isinstance(data.get("purchase"), dict) else {}
        ),
        "traction": traction_pull(data),
    }
