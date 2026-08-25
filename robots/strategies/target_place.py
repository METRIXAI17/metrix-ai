"""Target Place — gold. Trade places, not the air between them."""

from __future__ import annotations

from datetime import datetime, timezone

from robots.core.ta import atr, round_level
from robots.core.types import Bar, Signal, Side


def _day_key(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def _prev_day_hl(bars: list[Bar]) -> tuple[float, float] | None:
    if len(bars) < 20:
        return None
    last_day = _day_key(bars[-1].ts)
    days: dict[str, list[Bar]] = {}
    for b in bars:
        days.setdefault(_day_key(b.ts), []).append(b)
    keys = sorted(days)
    prev = None
    for k in keys:
        if k < last_day:
            prev = k
    if not prev:
        return None
    chunk = days[prev]
    return max(x.high for x in chunk), min(x.low for x in chunk)


def _session_hl(bars: list[Bar], hour_from: int, hour_to: int) -> tuple[float, float] | None:
    today = _day_key(bars[-1].ts)
    chunk = []
    for b in bars:
        if _day_key(b.ts) != today:
            continue
        h = datetime.fromtimestamp(b.ts / 1000, tz=timezone.utc).hour
        if hour_from <= h < hour_to:
            chunk.append(b)
    if len(chunk) < 3:
        return None
    return max(x.high for x in chunk), min(x.low for x in chunk)


def _reject(bar: Bar, level: float, side: Side, buffer: float) -> bool:
    if bar.range <= 0:
        return False
    if side == Side.BUY:
        pierced = bar.low <= level + buffer and bar.low < level
        closed_back = bar.close > level and (bar.close - bar.low) >= 0.55 * bar.range
        return pierced and closed_back
    pierced = bar.high >= level - buffer and bar.high > level
    closed_back = bar.close < level and (bar.high - bar.close) >= 0.55 * bar.range
    return pierced and closed_back


class TargetPlace:
    name = "target_place"
    market = "gold"

    def __init__(self, symbol: str, round_step: float = 5.0) -> None:
        self.symbol = symbol
        self.round_step = round_step

    def places(self, bars: list[Bar]) -> dict[str, float]:
        out: dict[str, float] = {}
        pd = _prev_day_hl(bars)
        if pd:
            out["PDH"], out["PDL"] = pd
        asia = _session_hl(bars, 0, 7)
        if asia:
            out["ASIA_H"], out["ASIA_L"] = asia
        london = _session_hl(bars, 7, 12)
        if london:
            out["LON_H"], out["LON_L"] = london
        out["ROUND"] = round_level(bars[-1].close, self.round_step)
        return out

    def on_bars(self, bars: list[Bar]) -> Signal:
        flat = Signal(Side.FLAT, self.symbol, "нет места", bars[-1].close, 0.0, 0.0)
        if len(bars) < 40:
            return Signal(Side.FLAT, self.symbol, "мало баров", bars[-1].close, 0.0, 0.0)
        bar = bars[-2]  # last closed
        a = atr(bars[:-1], 14)
        if a <= 0:
            return flat
        buffer = a * 0.15
        pts = self.places(bars[:-1])
        if len(pts) < 2:
            return Signal(Side.FLAT, self.symbol, "места не собрались", bar.close, 0.0, 0.0)

        longs = [(n, lv) for n, lv in pts.items() if n.endswith("L") or n == "ROUND"]
        shorts = [(n, lv) for n, lv in pts.items() if n.endswith("H") or n == "ROUND"]

        mid = (max(pts.values()) + min(pts.values())) / 2
        if abs(bar.close - mid) < 0.25 * (max(pts.values()) - min(pts.values()) or 1):
            # still allow reject if sitting on a place
            on_place = any(abs(bar.close - lv) <= buffer for lv in pts.values())
            if not on_place:
                return Signal(Side.FLAT, self.symbol, "между местами — воздух", bar.close, 0.0, 0.0, meta={"places": pts})

        for name, lv in longs:
            if abs(bar.close - lv) > a * 1.2:
                continue
            if _reject(bar, lv, Side.BUY, buffer):
                sl = min(bar.low, lv) - a * 0.25
                tp = pts.get("PDH") or pts.get("LON_H") or (bar.close + 2 * (bar.close - sl))
                if tp <= bar.close:
                    tp = bar.close + 2 * (bar.close - sl)
                return Signal(Side.BUY, self.symbol, f"отбой от {name} {lv:.2f}", bar.close, sl, tp, tag=name, meta={"places": pts})

        for name, lv in shorts:
            if abs(bar.close - lv) > a * 1.2:
                continue
            if _reject(bar, lv, Side.SELL, buffer):
                sl = max(bar.high, lv) + a * 0.25
                tp = pts.get("PDL") or pts.get("LON_L") or (bar.close - 2 * (sl - bar.close))
                if tp >= bar.close:
                    tp = bar.close - 2 * (sl - bar.close)
                return Signal(Side.SELL, self.symbol, f"отбой от {name} {lv:.2f}", bar.close, sl, tp, tag=name, meta={"places": pts})

        return Signal(Side.FLAT, self.symbol, "ждём прихода в место", bar.close, 0.0, 0.0, meta={"places": pts})
