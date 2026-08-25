from __future__ import annotations

from typing import Protocol

from robots.core.types import Fill, Position, Side, Signal


class Broker(Protocol):
    paper: bool

    def equity(self) -> float: ...
    def position(self, symbol: str) -> Position | None: ...
    def market(self, signal: Signal, qty: float) -> Fill: ...
    def close(self, pos: Position, price: float, ts: int, reason: str) -> Fill: ...
