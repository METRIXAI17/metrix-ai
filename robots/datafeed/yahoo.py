from __future__ import annotations

import time

import httpx

from robots.core.types import Bar

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def fetch_yahoo(symbol: str, interval: str = "15m", range_: str = "5d") -> list[Bar]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"interval": interval, "range": range_, "includePrePost": "false"}
    with httpx.Client(timeout=30, headers={"User-Agent": _UA}) as c:
        r = c.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        return []
    node = result[0]
    ts = node.get("timestamp") or []
    q = ((node.get("indicators") or {}).get("quote") or [{}])[0]
    out: list[Bar] = []
    for i, t in enumerate(ts):
        o, h, l, cl, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, cl):
            continue
        out.append(
            Bar(
                ts=int(t) * 1000,
                open=float(o),
                high=float(h),
                low=float(l),
                close=float(cl),
                volume=float(v or 0),
            )
        )
    return out


def sleep_until_next(seconds: int) -> None:
    time.sleep(max(1, seconds))
