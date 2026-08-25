"""Demand — crypto. Window first, name second. Local names that fire inside a window."""

from __future__ import annotations

from robots.core.ta import atr, median
from robots.core.types import Bar, Signal, Side


class Demand:
    name = "demand"
    market = "crypto"

    def __init__(self, window_bars: int = 12, vol_k: float = 2.2) -> None:
        self.window_bars = window_bars
        self.vol_k = vol_k

    def on_bars(self, bars: list[Bar], symbol: str) -> Signal:
        if len(bars) < 40:
            return Signal(Side.FLAT, symbol, "мало баров", bars[-1].close if bars else 0.0, 0.0, 0.0)
        closed = bars[:-1]
        bar = closed[-1]
        vols = [b.volume for b in closed[-21:-1]]
        med = median(vols)
        if med <= 0:
            return Signal(Side.FLAT, symbol, "нет объёма", bar.close, 0.0, 0.0)
        spike_idx = None
        look = closed[-self.window_bars :]
        for i, b in enumerate(look):
            if b.volume >= self.vol_k * med:
                spike_idx = i
                break
        if spike_idx is None:
            return Signal(Side.FLAT, symbol, "окна спроса нет", bar.close, 0.0, 0.0)

        window = look[spike_idx:]
        window_high = max(x.high for x in window)
        window_low = min(x.low for x in window)
        moved = (window_high - window_low) / bar.close if bar.close else 0
        if moved > 0.18:
            return Signal(Side.FLAT, symbol, "спрос уже снят (>18% окна)", bar.close, 0.0, 0.0)

        a = atr(closed, 14)
        base = min(x.low for x in closed[-8:])
        hold = bar.close > base and bar.close >= (bar.high + bar.low) / 2
        vol_now = bar.volume >= med
        if not (hold and vol_now):
            return Signal(Side.FLAT, symbol, "окно есть, спроса в цене нет", bar.close, 0.0, 0.0)

        sl = min(base, bar.low) - a * 0.2
        tp = bar.close + max(2.0 * (bar.close - sl), a * 1.5)
        bars_left = self.window_bars - (len(look) - spike_idx)
        return Signal(
            Side.BUY,
            symbol,
            f"спрос в окне, осталось ~{max(bars_left, 1)} баров",
            bar.close,
            sl,
            tp,
            tag="demand_window",
            meta={"vol_med": med, "vol": bar.volume, "window_move": moved},
        )

    def still_alive(self, bars: list[Bar], entry_ts: int) -> bool:
        after = [b for b in bars if b.ts >= entry_ts]
        return len(after) <= self.window_bars
