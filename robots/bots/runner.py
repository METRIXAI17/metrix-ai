from __future__ import annotations

import time
from typing import Callable

from robots.brokers.paper import PaperBroker
from robots.config import (
    CRYPTO_QUOTE,
    GOLD_SYMBOL,
    POLL_SEC,
    US_SYMBOL,
    is_live,
)
from robots.core.engine import exit_price, hit_stop_or_target, scan_line
from robots.core.journal import log
from robots.core.risk import RiskGate
from robots.core.types import Bar, Position, Side, Signal


def manage_position(broker, risk: RiskGate, pos: Position | None, bar: Bar, extra_exit: str | None = None) -> None:
    if not pos:
        return
    reason = extra_exit or hit_stop_or_target(pos, bar)
    if not reason:
        return
    px = exit_price(pos, bar, reason)
    fill = broker.close(pos, px, bar.ts, reason)
    pnl = (fill.raw or {}).get("pnl")
    if pnl is None:
        sign = 1.0 if pos.side == Side.BUY else -1.0
        pnl = (px - pos.entry) * pos.qty * sign
    risk.mark_pnl(float(pnl))


def maybe_enter(broker, risk: RiskGate, signal: Signal, *, min_qty: float, qty_step: float, contract: float, quote_override: float | None = None) -> None:
    if risk.killed:
        print("KILL:", risk.kill_reason)
        return
    if signal.side == Side.FLAT:
        return
    if broker.position(signal.symbol):
        return
    if quote_override:
        qty = quote_override
    else:
        qty = risk.size(signal, min_qty=min_qty, qty_step=qty_step, contract=contract)
    if qty <= 0:
        print("size=0, пропуск", signal.symbol, signal.reason)
        return
    broker.market(signal, qty)


def loop(name: str, tick: Callable[[], None]) -> None:
    print(f"робот {name}  mode={'LIVE' if is_live() else 'PAPER'}  poll={POLL_SEC}s")
    print("стоп: Ctrl+C")
    while True:
        try:
            tick()
        except KeyboardInterrupt:
            print("stop")
            return
        except Exception as exc:  # noqa: BLE001
            log(name, {"event": "error", "error": str(exc)[:400]})
        time.sleep(POLL_SEC)


def paper_or(factory, name: str):
    if is_live():
        return factory()
    return PaperBroker(name)


def gold_qty_spec() -> tuple[float, float, float]:
    # min lot, step, contract $ per point for XAU (paper: 1)
    return 0.01, 0.01, 100.0


def us_qty_spec() -> tuple[float, float, float]:
    return 1.0, 1.0, 1.0
