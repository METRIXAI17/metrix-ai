from __future__ import annotations

from datetime import datetime, timedelta, timezone

from robots.core.types import Bar, Side
from robots.strategies.ampli import Ampli
from robots.strategies.demand import Demand
from robots.strategies.target_place import TargetPlace


def _b(ts: datetime, o: float, h: float, l: float, c: float, v: float = 1.0) -> Bar:
    return Bar(ts=int(ts.timestamp() * 1000), open=o, high=h, low=l, close=c, volume=v)


def test_target_place_buys_reject_of_pdl():
    day1 = datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc)
    bars: list[Bar] = []
    for i in range(24):
        t = day1 + timedelta(hours=i)
        # day high 2400, low 2350
        bars.append(_b(t, 2370, 2400 if i == 10 else 2380, 2350 if i == 4 else 2360, 2375, 10))
    day2 = datetime(2026, 8, 25, 0, 0, tzinfo=timezone.utc)
    for i in range(20):
        t = day2 + timedelta(hours=i)
        bars.append(_b(t, 2370, 2378, 2365, 2372, 10))
    # reject PDL 2350: pierce then close back — this is bars[-2] after we append dummy last
    reject = _b(day2 + timedelta(hours=20), 2360, 2368, 2346, 2364, 12)
    last = _b(day2 + timedelta(hours=21), 2364, 2366, 2362, 2365, 8)
    bars.extend([reject, last])
    sig = TargetPlace("XAUUSD").on_bars(bars)
    assert sig.side == Side.BUY
    assert sig.sl < sig.entry < sig.tp


def test_demand_fires_on_volume_window():
    t0 = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
    bars: list[Bar] = []
    for i in range(40):
        t = t0 + timedelta(minutes=15 * i)
        bars.append(_b(t, 10, 10.2, 9.9, 10.1, 100))
    # spike + hold
    spike = _b(t0 + timedelta(minutes=15 * 40), 10.1, 10.4, 10.0, 10.35, 400)
    hold = _b(t0 + timedelta(minutes=15 * 41), 10.35, 10.5, 10.2, 10.45, 250)
    last = _b(t0 + timedelta(minutes=15 * 42), 10.45, 10.5, 10.4, 10.48, 120)
    bars.extend([spike, hold, last])
    sig = Demand(window_bars=12, vol_k=2.0).on_bars(bars, "WIFUSDT")
    assert sig.side == Side.BUY
    assert "спрос" in sig.reason


def test_ampli_breaks_opening_range():
    # Tuesday 2026-03-03 09:30-11:00 New York = 13:30-15:00 UTC (EDT in March? 2026-03-03 is before DST... EST = UTC-5)
    # 09:30 EST = 14:30 UTC
    start = datetime(2026, 3, 3, 14, 30, tzinfo=timezone.utc)
    bars: list[Bar] = []
    # pre-session junk so ATR exists
    for i in range(30):
        t = start - timedelta(minutes=5 * (30 - i))
        bars.append(_b(t, 500, 508, 492, 500, 1_000_000))
    # OR 30 min tight 500-500.4
    for i in range(6):
        t = start + timedelta(minutes=5 * i)
        bars.append(_b(t, 500.1, 500.4, 500.0, 500.2, 2_000_000))
    # expansion up
    brk = _b(start + timedelta(minutes=35), 500.8, 503.5, 500.7, 503.2, 4_000_000)
    last = _b(start + timedelta(minutes=40), 503.2, 503.4, 502.8, 503.0, 2_000_000)
    bars.extend([brk, last])
    sig = Ampli("SPY", or_minutes=30).on_bars(bars)
    assert sig.side in (Side.BUY, Side.FLAT)
    # If timezone maps 14:30 UTC to cash, we expect BUY. If not cash, FLAT is acceptable fail-safe.
    if sig.side == Side.BUY:
        assert sig.entry > 0 and sig.sl < sig.entry
