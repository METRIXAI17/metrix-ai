"""
Order terminal — path to pending orders / mining orders.

Strategic idea: chains of decisions not bound to formal thinking,
leading to liquidity. Uses existing Market Making + Auto Orders.
Not a broker. Not exchange execution.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from backend.core.task_reader import assemble_query
from backend.monetization.auto_orders import AutoOrdersEngine
from backend.monetization.market_making import MarketMakingSimulator


def _chain(brief: str, assembly: dict[str, Any]) -> list[dict[str, str]]:
    """Non-formal decision chain: ricochet, not syllogism."""
    mode = (assembly.get("mode") or {}).get("surface_mode") or "consult_qa"
    ling = ((assembly.get("three_sides") or {}).get("linguistic") or {}).get("report") or {}
    unnamed = list(ling.get("unnamed_phenomena") or [])
    steps = [
        {
            "id": "sense",
            "kind": "nonformal",
            "move": "Hold the brief as a field, not as a proposition to prove.",
        },
        {
            "id": "split",
            "kind": "nonformal",
            "move": "Keep several end-readings. Liquidity often sits in the discarded one.",
        },
        {
            "id": "ricochet",
            "kind": "nonformal",
            "move": f"Ricochet off mode={mode}: if product stalls, ask money; if money stalls, unfold ling.",
        },
        {
            "id": "index",
            "kind": "indexical",
            "move": "Look for a trace (number, repeated error, named counterparty). No trace → no order.",
        },
        {
            "id": "pending",
            "kind": "order",
            "move": "Mint a *pending* order (human gate). Never auto-fire into the market.",
        },
    ]
    if unnamed:
        steps.insert(
            3,
            {
                "id": "withheld",
                "kind": "linguistic",
                "move": f"Name withheld phenomenon: {unnamed[0]}. That may be the real SKU.",
            },
        )
    return steps


def _order_id(brief: str) -> str:
    h = hashlib.sha1((brief or uuid4().hex).encode("utf-8")).hexdigest()[:10]
    return f"ord_{h}"


def mine_orders(
    brief: str,
    *,
    lang: str = "ru",
    readiness: float = 0.5,
    health: float = 0.55,
    info_roi: float = 1.6,
    journal_usefulness: float | None = None,
) -> dict[str, Any]:
    packed = assemble_query(brief, lang=lang, surface_hint="terminal_liquidity")
    mm = MarketMakingSimulator().simulate(
        idea_title=(brief or "Metrix order")[:80],
        value_density=min(1.0, 0.4 + readiness * 0.4),
        promo_fit=0.45,
        competition_hint=0.35,
    )
    ao = AutoOrdersEngine().build(
        idea_title=(brief or "Metrix order")[:80],
        info_roi=info_roi,
        readiness=readiness,
        health=health,
        track="product",
    )
    chain = _chain(brief, packed)
    ju = journal_usefulness
    # mining: convert traces into pending tickets
    tickets: list[dict[str, Any]] = []
    oid = _order_id(brief)
    gate_ok = ao.enabled and (ju is None or ju >= 0.55)
    tickets.append(
        {
            "id": oid,
            "status": "pending_approval" if gate_ok else "mined_hold",
            "sku": (packed.get("mode") or {}).get("sku") or "request_deep",
            "title": (brief or "")[:72] or "Untitled order",
            "requires_human": True,
            "why": "Trace present and auto-order policy passed"
            if gate_ok
            else "Mined but held — formal thinking would fire; Metrix waits for a gate",
        }
    )
    if mm.position == "category_maker":
        tickets.append(
            {
                "id": f"{oid}_liq",
                "status": "seed_liquidity",
                "sku": "market_making",
                "title": "Two-sided quote: demo free / implement paid",
                "requires_human": True,
                "why": "Attention spread tight enough to quote both sides",
            }
        )

    viability = {
        "idea": "terminal_with_nonformal_chains_to_liquidity",
        "verdict": "viable_as_pending_layer_not_as_broker",
        "why": [
            "Existing Auto Orders + Market Making already score readiness vs threshold.",
            "Task reader supplies multiple end-readings — the chain is not a syllogism.",
            "Liquidity here = attention + payable SKU, not exchange fill.",
            "Failure mode: pretending this is a trading venue. It is an order *desk* for Metrix work.",
        ],
        "kill": "If you auto-send money to a market without a licensed venue and a human gate.",
    }
    return {
        "module": "Metrix Order Terminal",
        "disclaimer": "Not a broker. Pending / mined Metrix orders only.",
        "chain": chain,
        "tickets": tickets,
        "market_making": mm.to_dict(),
        "auto_orders": ao.to_dict(),
        "assembly": packed,
        "viability": viability,
        "mined_at": datetime.now(timezone.utc).isoformat(),
        "summary": f"tickets={len(tickets)} auto={ao.enabled} liq={mm.attention_liquidity:.2f}",
    }
