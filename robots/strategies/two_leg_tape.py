"""Two-Leg Tape — Tape Land core.

Leg A: attention (volume surprise) leads price.
Leg B: money confirms (range expansion vs ATR, hold).
LIVE only when both legs are on. No leverage. Not a signal — code of the model.
"""

from __future__ import annotations

import math

from robots.core.ta import atr, median
from robots.core.types import Bar, Signal, Side


def _z(xs: list[float], x: float) -> float:
    if len(xs) < 4:
        return 0.0
    mu = sum(xs) / len(xs)
    var = sum((v - mu) ** 2 for v in xs) / len(xs)
    sd = math.sqrt(var) if var > 1e-12 else 0.0
    if sd <= 0:
        return 0.0
    return (x - mu) / sd


class TwoLegTape:
    name = "two_leg_tape"
    market = "tape"

    def __init__(self, vol_look: int = 30, confirm_bars: int = 6) -> None:
        self.vol_look = vol_look
        self.confirm_bars = confirm_bars

    def on_bars(self, bars: list[Bar], symbol: str) -> Signal:
        if len(bars) < self.vol_look + 5:
            return Signal(Side.FLAT, symbol, "мало баров для двух ног", bars[-1].close if bars else 0.0, 0.0, 0.0)
        closed = bars[:-1]
        bar = closed[-1]
        vols = [b.volume for b in closed[-self.vol_look :]]
        rets = []
        for i in range(-self.vol_look, 0):
            prev = closed[i - 1].close if abs(i - 1) < len(closed) else closed[i].open
            if prev:
                rets.append((closed[i].close - prev) / prev)
        vol_z = _z(vols[:-1], bar.volume)
        px_z = _z(rets[:-1], rets[-1] if rets else 0.0)
        a = atr(closed, 14)
        rng = bar.range
        rng_vs_atr = (rng / a) if a else 0.0
        med_v = median(vols[:-1])
        hold = bar.close >= (bar.high + bar.low) / 2

        # A: attention leads price — volume surprise without matching price z
        a_score = vol_z - 0.35 * max(px_z, 0.0)
        # C: money — range expansion + volume vs median, not funding (bars-only port)
        c_score = 0.55 * (rng_vs_atr - 0.8) + 0.45 * ((bar.volume / med_v) - 1.0 if med_v else 0)

        mode = "QUIET_ENGINE"
        if a_score >= 0.75 and c_score < 0.15:
            mode = "EMPTY_NARRATIVE"
        elif a_score >= 0.75 and c_score >= 0.25 and hold:
            mode = "LIVE_MULTIPLIER"
        elif rng_vs_atr > 1.8 and vol_z < 0.2:
            mode = "EXHAUSTION"

        meta = {
            "a_score": round(a_score, 4),
            "c_score": round(c_score, 4),
            "mode": mode,
            "vol_z": round(vol_z, 4),
            "px_z": round(px_z, 4),
            "leverage": None,
            "leverage_note": "плечо не рекомендуется и не считается",
        }

        if mode != "LIVE_MULTIPLIER":
            return Signal(
                Side.FLAT,
                symbol,
                f"{mode}: нога A={a_score:.2f} нога C={c_score:.2f}",
                bar.close,
                0.0,
                0.0,
                tag=mode,
                meta=meta,
            )

        sl = min(x.low for x in closed[-self.confirm_bars :]) - a * 0.2
        tp = bar.close + max(2.0 * (bar.close - sl), a * 1.4)
        return Signal(
            Side.BUY,
            symbol,
            f"LIVE: внимание обгоняет цену, деньги подтверждают (A={a_score:.2f} C={c_score:.2f})",
            bar.close,
            sl,
            tp,
            tag="two_leg_live",
            meta=meta,
        )
