"""Alpaca adapter for Ampli (US stocks/ETFs). Paper URL by default."""

from __future__ import annotations

import httpx

from robots.config import env
from robots.core.journal import log
from robots.core.types import Fill, Position, Side, Signal


class AlpacaBroker:
    def __init__(self, name: str = "ampli") -> None:
        self.key = env("ALPACA_KEY")
        self.secret = env("ALPACA_SECRET")
        paper = env("ALPACA_PAPER", "1") != "0"
        self.paper = paper
        if not self.key or not self.secret:
            raise RuntimeError("Задайте ALPACA_KEY и ALPACA_SECRET в robots/.env")
        self.base = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.name = name
        self._pos: dict[str, Position] = {}
        self.client = httpx.Client(
            timeout=30,
            headers={"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret},
        )

    def equity(self) -> float:
        r = self.client.get(self.base + "/v2/account")
        r.raise_for_status()
        return float(r.json().get("equity") or 0)

    def position(self, symbol: str) -> Position | None:
        r = self.client.get(self.base + f"/v2/positions/{symbol}")
        if r.status_code == 404:
            return self._pos.get(symbol)
        r.raise_for_status()
        p = r.json()
        side = Side.BUY if p.get("side") == "long" else Side.SELL
        pos = Position(
            symbol=symbol,
            side=side,
            qty=abs(float(p.get("qty") or 0)),
            entry=float(p.get("avg_entry_price") or 0),
            sl=self._pos.get(symbol).sl if self._pos.get(symbol) else 0.0,
            tp=self._pos.get(symbol).tp if self._pos.get(symbol) else 0.0,
            tag="alpaca",
        )
        self._pos[symbol] = pos
        return pos

    def market(self, signal: Signal, qty: float) -> Fill:
        body = {
            "symbol": signal.symbol,
            "qty": str(int(qty) if qty >= 1 else 1),
            "side": "buy" if signal.side == Side.BUY else "sell",
            "type": "market",
            "time_in_force": "day",
        }
        r = self.client.post(self.base + "/v2/orders", json=body)
        r.raise_for_status()
        raw = r.json()
        fill = Fill(
            symbol=signal.symbol,
            side=signal.side,
            qty=float(body["qty"]),
            price=signal.entry,
            ts=0,
            tag=signal.tag,
            paper=self.paper,
            raw=raw,
        )
        self._pos[signal.symbol] = Position(
            symbol=signal.symbol, side=signal.side, qty=fill.qty, entry=signal.entry, sl=signal.sl, tp=signal.tp, tag=signal.tag
        )
        log(self.name, {"event": "open", "broker": "alpaca", "paper": self.paper, "why": signal.reason, "symbol": signal.symbol, "qty": fill.qty})
        return fill

    def close(self, pos: Position, price: float, ts: int, reason: str) -> Fill:
        r = self.client.delete(self.base + f"/v2/positions/{pos.symbol}")
        if r.status_code not in (200, 204, 404):
            r.raise_for_status()
        self._pos.pop(pos.symbol, None)
        fill = Fill(symbol=pos.symbol, side=Side.SELL if pos.side == Side.BUY else Side.BUY, qty=pos.qty, price=price, ts=ts, tag=pos.tag, paper=self.paper)
        log(self.name, {"event": "close", "broker": "alpaca", "reason": reason, "price": price})
        return fill
