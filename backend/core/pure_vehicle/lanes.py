"""Four lanes instead of the fifth step. Not a rewrite of contour 2.7.

1. Autonomy is ready. It travels by outsource of named work.
2. Trading is only the real sector and innovations. No exchange order, no yield.
3. Ideas are a separate shelf. IT ideas do not sit inside the trade.
4. The push is its own act. It does not mix the shelves.
"""

from __future__ import annotations

from typing import Any

from backend.core.product_eval import THRESHOLD

VERSION = "2.9.0"
INSTEAD_OF = "fifth"

REAL = frozenset(
    {
        "energy",
        "food",
        "chemical",
        "goods",
        "hardware",
        "cold_chain",
        "innovation",
    }
)
REFUSED_MARKETS = frozenset(
    {
        "exchange",
        "crypto",
        "signal",
        "yield",
        "forex",
        "token",
    }
)


def _text(value: Any, limit: int = 160) -> str:
    return str(value or "").strip()[:limit]


def autonomy(body: dict[str, Any] | None) -> dict[str, Any]:
    """Ready. Outsource may carry named work. It does not carry the trade."""
    row = body or {}
    named = bool(_text(row.get("work")))
    carries_trade = bool(row.get("carries_trade"))
    return {
        "lane": "autonomy",
        "ready": True,
        "via": "outsource",
        "project": "finance",
        "named_work": named,
        "accepted": named and not carries_trade,
        "reason": "" if named and not carries_trade else ("unnamed" if not named else "outsource_does_not_trade"),
    }


def trading(body: dict[str, Any] | None) -> dict[str, Any]:
    """Real sector and innovations only. The core does not place an order."""
    row = body or {}
    market = _text(row.get("market")).lower()
    if bool(row.get("place_orders")) or market in REFUSED_MARKETS:
        return {
            "lane": "trading",
            "open": False,
            "reason": "not_this_market",
            "orders_placed": 0,
            "yield_promised": False,
        }
    if market not in REAL:
        return {
            "lane": "trading",
            "open": False,
            "reason": "market_not_named",
            "orders_placed": 0,
            "yield_promised": False,
        }
    return {
        "lane": "trading",
        "open": True,
        "market": market,
        "kind": "innovation" if market == "innovation" else "real_sector",
        "orders_placed": 0,
        "yield_promised": False,
    }


def ideas(body: dict[str, Any] | None) -> dict[str, Any]:
    """A separate shelf. An IT idea is not a trade."""
    row = body or {}
    text = _text(row.get("text"))
    if bool(row.get("inside_trade")):
        return {"lane": "ideas", "open": False, "reason": "ideas_stay_separate", "text": text}
    if not text:
        return {"lane": "ideas", "open": False, "reason": "empty", "text": ""}
    return {"lane": "ideas", "open": True, "shelf": "it", "separate": True, "text": text}


def place(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload or {}
    asked = data.get("eval_floor")
    ignored = False
    if asked is not None:
        try:
            ignored = float(asked) < THRESHOLD
        except (TypeError, ValueError):
            ignored = True
    lanes = {
        "autonomy": autonomy(data.get("autonomy") if isinstance(data.get("autonomy"), dict) else {}),
        "trading": trading(data.get("trading") if isinstance(data.get("trading"), dict) else {}),
        "ideas": ideas(data.get("ideas") if isinstance(data.get("ideas"), dict) else {}),
    }
    return {
        "ok": True,
        "version": VERSION,
        "instead_of": INSTEAD_OF,
        "does_not_rewrite": "2.7",
        "eval_floor": THRESHOLD,
        "floor_lowered": False,
        "floor_request_ignored": ignored,
        "yield_promised": False,
        "exchange_orders": False,
        "orders_placed": 0,
        "lanes": ["autonomy", "trading", "ideas", "push"],
        "autonomy": lanes["autonomy"],
        "trading": lanes["trading"],
        "ideas": lanes["ideas"],
        "push": "separate",
    }
