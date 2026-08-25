"""Ampli — US. Collect amplitude. Do not predict direction."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from robots.core.ta import atr
from robots.core.types import Bar, Signal, Side


def _ny_tz():
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo("America/New_York")
    except Exception:
        # Windows without tzdata: US Eastern, DST second Sun Mar → first Sun Nov
        return timezone(timedelta(hours=-5))


NY = _ny_tz()


def _ny(ts_ms: int) -> datetime:
    return datetime.fromtimestamp(ts_ms / 1000, tz=NY)


def _is_cash(ts_ms: int) -> bool:
    t = _ny(ts_ms)
    if t.weekday() >= 5:
        return False
    minutes = t.hour * 60 + t.minute
    return 9 * 60 + 30 <= minutes < 16 * 60


class Ampli:
    name = "ampli"
    market = "us"

    def __init__(self, symbol: str, or_minutes: int = 30) -> None:
        self.symbol = symbol
        self.or_minutes = or_minutes

    def _opening_range(self, bars: list[Bar]) -> tuple[float, float, int] | None:
        cash = [b for b in bars if _is_cash(b.ts)]
        if not cash:
            return None
        day = _ny(cash[-1].ts).date()
        today = [b for b in cash if _ny(b.ts).date() == day]
        if not today:
            return None
        start = _ny(today[0].ts)
        end_min = start.hour * 60 + start.minute + self.or_minutes
        or_bars = []
        for b in today:
            m = _ny(b.ts).hour * 60 + _ny(b.ts).minute
            if m < end_min:
                or_bars.append(b)
            else:
                break
        if len(or_bars) < 3:
            return None
        return max(x.high for x in or_bars), min(x.low for x in or_bars), or_bars[-1].ts

    def on_bars(self, bars: list[Bar]) -> Signal:
        if len(bars) < 50:
            return Signal(Side.FLAT, self.symbol, "мало баров", bars[-1].close if bars else 0.0, 0.0, 0.0)
        bar = bars[-2]
        if not _is_cash(bar.ts):
            return Signal(Side.FLAT, self.symbol, "вне US cash", bar.close, 0.0, 0.0)
        t = _ny(bar.ts)
        minutes = t.hour * 60 + t.minute
        # first OR minutes: only mark, do not trade
        open_min = 9 * 60 + 30
        if minutes < open_min + self.or_minutes:
            return Signal(Side.FLAT, self.symbol, "сжатие: только метим opening range", bar.close, 0.0, 0.0)

        rng = self._opening_range(bars[:-1])
        if not rng:
            return Signal(Side.FLAT, self.symbol, "opening range не собрался", bar.close, 0.0, 0.0)
        or_h, or_l, _ = rng
        or_w = or_h - or_l
        a = atr(bars[:-1], 14)
        if a <= 0:
            return Signal(Side.FLAT, self.symbol, "нет ATR", bar.close, 0.0, 0.0)
        compressed = or_w <= 0.45 * a
        if not compressed:
            return Signal(Side.FLAT, self.symbol, f"нет сжатия OR={or_w:.2f} ATR={a:.2f}", bar.close, 0.0, 0.0, meta={"or_h": or_h, "or_l": or_l})

        if bar.close > or_h:
            sl = or_l
            tp = bar.close + 1.6 * (bar.close - sl)
            return Signal(Side.BUY, self.symbol, f"расширение вверх из OR {or_l:.2f}-{or_h:.2f}", bar.close, sl, tp, tag="or_break_up", meta={"or_h": or_h, "or_l": or_l})
        if bar.close < or_l:
            sl = or_h
            tp = bar.close - 1.6 * (sl - bar.close)
            return Signal(Side.SELL, self.symbol, f"расширение вниз из OR {or_l:.2f}-{or_h:.2f}", bar.close, sl, tp, tag="or_break_down", meta={"or_h": or_h, "or_l": or_l})
        return Signal(Side.FLAT, self.symbol, "сжатие живо, выстрела нет", bar.close, 0.0, 0.0, meta={"or_h": or_h, "or_l": or_l})

    def amplitude_dead(self, bars: list[Bar], side: Side, look: int = 6) -> bool:
        chunk = bars[-look:]
        if len(chunk) < look:
            return False
        highs = [b.high for b in chunk]
        lows = [b.low for b in chunk]
        if side == Side.BUY:
            return max(highs) == max(highs[:-1])  # no new high on last bar vs previous
        return min(lows) == min(lows[:-1])
