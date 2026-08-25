from __future__ import annotations

from robots.bots.runner import loop, manage_position, maybe_enter, paper_or, us_qty_spec
from robots.config import US_BROKER, US_OR_MINUTES, US_SYMBOL, US_TF, is_live
from robots.core.engine import scan_line
from robots.core.risk import RiskGate
from robots.datafeed.yahoo import fetch_yahoo
from robots.strategies.ampli import Ampli


def _make_broker():
    if US_BROKER == "alpaca" and is_live():
        from robots.brokers.alpaca import AlpacaBroker

        return AlpacaBroker("ampli")
    from robots.brokers.paper import PaperBroker

    return PaperBroker("ampli")


def tick() -> None:
    strat = Ampli(US_SYMBOL, or_minutes=US_OR_MINUTES)
    bars = fetch_yahoo(US_SYMBOL, US_TF, "5d")
    if not bars:
        print("нет котировок", US_SYMBOL)
        return
    sig = strat.on_bars(bars)
    print(scan_line(sig))
    broker = tick.broker  # type: ignore[attr-defined]
    risk = tick.risk  # type: ignore[attr-defined]
    pos = broker.position(US_SYMBOL)
    extra = None
    if pos and strat.amplitude_dead(bars, pos.side):
        extra = "amplitude_dead"
    manage_position(broker, risk, pos, bars[-1], extra_exit=extra)
    min_qty, step, contract = us_qty_spec()
    maybe_enter(broker, risk, sig, min_qty=min_qty, qty_step=step, contract=contract)


def main() -> None:
    tick.broker = paper_or(_make_broker, "ampli")  # type: ignore[attr-defined]
    tick.risk = RiskGate(tick.broker.equity())  # type: ignore[attr-defined]
    loop("ampli", tick)
