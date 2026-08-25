from __future__ import annotations

import time

from robots.config import PAPER_EQUITY
from robots.core.journal import log
from robots.core.types import Fill, Position, Side, Signal


class PaperBroker:
    paper = True

    def __init__(self, name: str, equity: float | None = None) -> None:
        self.name = name
        self._equity = equity if equity is not None else PAPER_EQUITY
        self._pos: dict[str, Position] = {}

    def equity(self) -> float:
        return self._equity

    def position(self, symbol: str) -> Position | None:
        return self._pos.get(symbol)

    def market(self, signal: Signal, qty: float) -> Fill:
        fill = Fill(
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            price=signal.entry,
            ts=0,
            tag=signal.tag,
            paper=True,
        )
        self._pos[signal.symbol] = Position(
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            entry=signal.entry,
            sl=signal.sl,
            tp=signal.tp,
            tag=signal.tag,
            opened_ts=int(time.time() * 1000),
        )
        log(self.name, {"event": "open", "paper": True, **fill.__dict__, "sl": signal.sl, "tp": signal.tp, "why": signal.reason})
        return fill

    def close(self, pos: Position, price: float, ts: int, reason: str) -> Fill:
        sign = 1.0 if pos.side == Side.BUY else -1.0
        pnl = (price - pos.entry) * pos.qty * sign
        self._equity += pnl
        fill = Fill(
            symbol=pos.symbol,
            side=Side.SELL if pos.side == Side.BUY else Side.BUY,
            qty=pos.qty,
            price=price,
            ts=ts,
            tag=pos.tag,
            paper=True,
            raw={"pnl": pnl, "reason": reason},
        )
        self._pos.pop(pos.symbol, None)
        log(self.name, {"event": "close", "paper": True, "pnl": round(pnl, 4), "reason": reason, **{k: v for k, v in fill.__dict__.items() if k != "raw"}})
        return fill
