from __future__ import annotations

import httpx

from robots.core.types import Bar

_TF = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
}


def fetch_binance(symbol: str, interval: str = "15m", limit: int = 300) -> list[Bar]:
    tf = _TF.get(interval, interval)
    url = "https://api.binance.com/api/v3/klines"
    with httpx.Client(timeout=30) as c:
        r = c.get(url, params={"symbol": symbol.upper(), "interval": tf, "limit": limit})
        r.raise_for_status()
        raw = r.json()
    out: list[Bar] = []
    for k in raw:
        out.append(
            Bar(
                ts=int(k[0]),
                open=float(k[1]),
                high=float(k[2]),
                low=float(k[3]),
                close=float(k[4]),
                volume=float(k[5]),
            )
        )
    return out
