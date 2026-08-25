from __future__ import annotations

from robots.core.types import Bar, Position, Side, Signal


def hit_stop_or_target(pos: Position, bar: Bar) -> str | None:
    if pos.side == Side.BUY:
        if pos.sl and bar.low <= pos.sl:
            return "sl"
        if pos.tp and bar.high >= pos.tp:
            return "tp"
    elif pos.side == Side.SELL:
        if pos.sl and bar.high >= pos.sl:
            return "sl"
        if pos.tp and bar.low <= pos.tp:
            return "tp"
    return None


def exit_price(pos: Position, bar: Bar, reason: str) -> float:
    if reason == "sl":
        return pos.sl
    if reason == "tp":
        return pos.tp
    return bar.close


def scan_line(signal: Signal) -> str:
    if signal.side == Side.FLAT:
        return f"[{signal.symbol}] FLAT  {signal.entry:.4g}  {signal.reason}"
    return (
        f"[{signal.symbol}] {signal.side.value.upper()}  "
        f"in {signal.entry:.4g}  sl {signal.sl:.4g}  tp {signal.tp:.4g}  "
        f"R={signal.rr:.2f}  {signal.reason}"
    )
