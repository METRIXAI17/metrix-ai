"""CLI: python -m robots scan|paper|live|backtest <target_place|demand|ampli|two_leg_tape>"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _scan_target() -> None:
    from robots.config import GOLD_SYMBOL, GOLD_TF, GOLD_YAHOO
    from robots.core.engine import scan_line
    from robots.datafeed.yahoo import fetch_yahoo
    from robots.strategies.target_place import TargetPlace

    bars = fetch_yahoo(GOLD_YAHOO, GOLD_TF, "10d")
    sig = TargetPlace(GOLD_SYMBOL).on_bars(bars)
    print("places", (sig.meta or {}).get("places"))
    print(scan_line(sig))


def _scan_demand() -> None:
    from robots.config import CRYPTO_TF, CRYPTO_WATCH
    from robots.core.engine import scan_line
    from robots.datafeed.binance_pub import fetch_binance
    from robots.strategies.demand import Demand

    strat = Demand()
    for symbol in CRYPTO_WATCH:
        bars = fetch_binance(symbol, CRYPTO_TF, 200)
        print(scan_line(strat.on_bars(bars, symbol)))


def _scan_ampli() -> None:
    from robots.config import US_OR_MINUTES, US_SYMBOL, US_TF
    from robots.core.engine import scan_line
    from robots.datafeed.yahoo import fetch_yahoo
    from robots.strategies.ampli import Ampli

    bars = fetch_yahoo(US_SYMBOL, US_TF, "5d")
    print(scan_line(Ampli(US_SYMBOL, US_OR_MINUTES).on_bars(bars)))


def _scan_tape() -> None:
    from robots.config import CRYPTO_TF, CRYPTO_WATCH
    from robots.core.engine import scan_line
    from robots.datafeed.binance_pub import fetch_binance
    from robots.strategies.two_leg_tape import TwoLegTape

    strat = TwoLegTape()
    for symbol in CRYPTO_WATCH:
        bars = fetch_binance(symbol, CRYPTO_TF, 200)
        print(scan_line(strat.on_bars(bars, symbol)))


def _backtest_target() -> None:
    from robots.brokers.paper import PaperBroker
    from robots.config import GOLD_SYMBOL, GOLD_TF, GOLD_YAHOO
    from robots.core.engine import exit_price, hit_stop_or_target
    from robots.core.risk import RiskGate
    from robots.datafeed.yahoo import fetch_yahoo
    from robots.strategies.target_place import TargetPlace

    bars = fetch_yahoo(GOLD_YAHOO, GOLD_TF, "1mo")
    strat = TargetPlace(GOLD_SYMBOL)
    broker = PaperBroker("bt_target")
    risk = RiskGate(broker.equity())
    trades = 0
    for i in range(50, len(bars)):
        window = bars[: i + 1]
        bar = window[-1]
        pos = broker.position(GOLD_SYMBOL)
        if pos:
            why = hit_stop_or_target(pos, bar)
            if why:
                px = exit_price(pos, bar, why)
                fill = broker.close(pos, px, bar.ts, why)
                risk.mark_pnl(float((fill.raw or {}).get("pnl") or 0))
                trades += 1
                continue
        if broker.position(GOLD_SYMBOL):
            continue
        sig = strat.on_bars(window)
        if sig.side.value == "flat":
            continue
        qty = risk.size(sig, min_qty=0.01, qty_step=0.01, contract=100.0)
        if qty:
            broker.market(sig, qty)
    print(f"backtest Target Place  bars={len(bars)} closes={trades} equity={broker.equity():.2f}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Target Place / Demand / Ampli robots")
    p.add_argument("cmd", choices=["scan", "paper", "live", "backtest"])
    p.add_argument("robot", choices=["target_place", "demand", "ampli", "two_leg_tape", "all"])
    args = p.parse_args(argv)

    if args.cmd == "live":
        os.environ["ROBOT_MODE"] = "live"
    elif args.cmd in ("paper", "scan", "backtest"):
        os.environ["ROBOT_MODE"] = "paper"

    if args.cmd == "scan":
        {
            "target_place": _scan_target,
            "demand": _scan_demand,
            "ampli": _scan_ampli,
            "two_leg_tape": _scan_tape,
            "all": lambda: (_scan_target(), _scan_demand(), _scan_ampli(), _scan_tape()),
        }[args.robot]()
        return 0
    if args.cmd == "backtest":
        if args.robot not in ("target_place", "all"):
            print("backtest сейчас: target_place")
        _backtest_target()
        return 0

    if args.robot in ("target_place", "all"):
        from robots.bots.target_place_bot import main as g

        if args.robot != "all":
            g()
            return 0
        print("all: запускайте три окна — run_target_place.bat / run_demand.bat / run_ampli.bat")
        return 0
    if args.robot == "demand":
        from robots.bots.demand_bot import main as d

        d()
        return 0
    if args.robot == "two_leg_tape":
        print("two_leg_tape: scan-only в 1.8.0 (без автоордера). py -m robots scan two_leg_tape")
        _scan_tape()
        return 0
    from robots.bots.ampli_bot import main as a

    a()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
