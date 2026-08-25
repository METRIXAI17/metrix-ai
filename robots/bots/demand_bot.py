from __future__ import annotations

from robots.bots.runner import loop, manage_position, maybe_enter, paper_or
from robots.config import CRYPTO_QUOTE, CRYPTO_TF, CRYPTO_WATCH, is_live
from robots.core.engine import scan_line
from robots.core.risk import RiskGate
from robots.core.types import Side
from robots.datafeed.binance_pub import fetch_binance
from robots.strategies.demand import Demand


def _make_broker():
    if is_live():
        from robots.brokers.binance import BinanceBroker

        return BinanceBroker("demand")
    from robots.brokers.paper import PaperBroker

    return PaperBroker("demand")


def tick() -> None:
    strat = Demand()
    broker = tick.broker  # type: ignore[attr-defined]
    risk = tick.risk  # type: ignore[attr-defined]
    for symbol in CRYPTO_WATCH:
        try:
            bars = fetch_binance(symbol, CRYPTO_TF, 200)
        except Exception as exc:  # noqa: BLE001
            print(symbol, "feed error", exc)
            continue
        if not bars:
            continue
        sig = strat.on_bars(bars, symbol)
        print(scan_line(sig))
        pos = broker.position(symbol)
        extra = None
        if pos and pos.tag == "demand_window" and not strat.still_alive(bars, pos.opened_ts or bars[-1].ts):
            extra = "window_end"
        manage_position(broker, risk, pos, bars[-1], extra_exit=extra)
        maybe_enter(
            broker,
            risk,
            sig,
            min_qty=10.0,
            qty_step=1.0,
            contract=1.0,
            quote_override=CRYPTO_QUOTE if sig.side != Side.FLAT else None,
        )


def main() -> None:
    tick.broker = paper_or(_make_broker, "demand")  # type: ignore[attr-defined]
    tick.risk = RiskGate(tick.broker.equity())  # type: ignore[attr-defined]
    loop("demand", tick)
