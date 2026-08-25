from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"
    FLAT = "flat"


@dataclass(frozen=True)
class Bar:
    ts: int  # unix ms
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @property
    def range(self) -> float:
        return self.high - self.low


@dataclass
class Signal:
    side: Side
    symbol: str
    reason: str
    entry: float
    sl: float
    tp: float
    tag: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def risk(self) -> float:
        return abs(self.entry - self.sl)

    @property
    def rr(self) -> float:
        r = self.risk
        if r <= 0:
            return 0.0
        return abs(self.tp - self.entry) / r


@dataclass
class Position:
    symbol: str
    side: Side
    qty: float
    entry: float
    sl: float
    tp: float
    tag: str = ""
    opened_ts: int = 0


@dataclass
class Fill:
    symbol: str
    side: Side
    qty: float
    price: float
    ts: int
    tag: str = ""
    paper: bool = True
    raw: dict[str, Any] = field(default_factory=dict)
