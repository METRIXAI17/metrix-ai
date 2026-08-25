from __future__ import annotations

from robots.bots.runner import gold_qty_spec, loop, manage_position, maybe_enter, paper_or
from robots.config import GOLD_BROKER, GOLD_SYMBOL, GOLD_TF, GOLD_YAHOO, is_live
from robots.core.engine import scan_line
from robots.core.risk import RiskGate
from robots.datafeed.yahoo import fetch_yahoo
from robots.strategies.target_place import TargetPlace


def _make_broker():
    if GOLD_BROKER == "mt5" and is_live():
        from robots.brokers.mt5 import MT5Broker

        return MT5Broker("target_place")
    from robots.brokers.paper import PaperBroker

    return PaperBroker("target_place")


def tick() -> None:
    strat = TargetPlace(GOLD_SYMBOL)
    bars = fetch_yahoo(GOLD_YAHOO, GOLD_TF, "10d")
    if not bars:
        print("нет котировок золота (Yahoo GC=F). Проверьте сеть.")
        return
    sig = strat.on_bars(bars)
    print(scan_line(sig))
    broker = tick.broker  # type: ignore[attr-defined]
    risk = tick.risk  # type: ignore[attr-defined]
    pos = broker.position(GOLD_SYMBOL)
    manage_position(broker, risk, pos, bars[-1])
    min_qty, step, contract = gold_qty_spec()
    maybe_enter(broker, risk, sig, min_qty=min_qty, qty_step=step, contract=contract)


def main() -> None:
    tick.broker = paper_or(_make_broker, "target_place")  # type: ignore[attr-defined]
    tick.risk = RiskGate(tick.broker.equity())  # type: ignore[attr-defined]
    loop("target_place", tick)
