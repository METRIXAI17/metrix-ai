from __future__ import annotations

from robots.core.types import Bar


def atr(bars: list[Bar], n: int = 14) -> float:
    if len(bars) < 2:
        return 0.0
    trs: list[float] = []
    for i in range(1, len(bars)):
        p, b = bars[i - 1], bars[i]
        trs.append(max(b.high - b.low, abs(b.high - p.close), abs(b.low - p.close)))
    w = trs[-n:]
    return sum(w) / len(w) if w else 0.0


def median(xs: list[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    m = len(s) // 2
    if len(s) % 2:
        return s[m]
    return (s[m - 1] + s[m]) / 2.0


def round_level(price: float, step: float) -> float:
    if step <= 0:
        return price
    return round(price / step) * step
