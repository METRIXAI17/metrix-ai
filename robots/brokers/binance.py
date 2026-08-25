"""Binance spot adapter for Demand. Keys in .env. Optional live."""

from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import urlencode

import httpx

from robots.config import env
from robots.core.journal import log
from robots.core.types import Fill, Position, Side, Signal

BASE = "https://api.binance.com"


class BinanceBroker:
    paper = False

    def __init__(self, name: str = "demand") -> None:
        self.key = env("BINANCE_KEY")
        self.secret = env("BINANCE_SECRET")
        if not self.key or not self.secret:
            raise RuntimeError("Задайте BINANCE_KEY и BINANCE_SECRET в robots/.env")
        self.name = name
        self._pos: dict[str, Position] = {}
        self.client = httpx.Client(timeout=30)

    def _sign(self, params: dict) -> dict:
        params = {**params, "timestamp": int(time.time() * 1000), "recvWindow": 5000}
        q = urlencode(params)
        sig = hmac.new(self.secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    def _signed(self, method: str, path: str, params: dict) -> dict:
        params = self._sign(params)
        headers = {"X-MBX-APIKEY": self.key}
        r = self.client.request(method, BASE + path, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    def equity(self) -> float:
        acc = self._signed("GET", "/api/v3/account", {})
        for b in acc.get("balances") or []:
            if b.get("asset") == "USDT":
                return float(b.get("free") or 0) + float(b.get("locked") or 0)
        return 0.0

    def position(self, symbol: str) -> Position | None:
        return self._pos.get(symbol)

    def market(self, signal: Signal, qty: float) -> Fill:
        side = "BUY" if signal.side == Side.BUY else "SELL"
        # qty is quote USDT for demand bot; convert via quoteOrderQty
        params = {"symbol": signal.symbol, "side": side, "type": "MARKET", "quoteOrderQty": f"{qty:.2f}"}
        raw = self._signed("POST", "/api/v3/order", params)
        price = float(raw.get("fills", [{}])[0].get("price") or signal.entry) if raw.get("fills") else signal.entry
        filled_qty = float(raw.get("executedQty") or 0)
        fill = Fill(symbol=signal.symbol, side=signal.side, qty=filled_qty, price=price, ts=int(raw.get("transactTime") or 0), tag=signal.tag, paper=False, raw=raw)
        self._pos[signal.symbol] = Position(symbol=signal.symbol, side=signal.side, qty=filled_qty, entry=price, sl=signal.sl, tp=signal.tp, tag=signal.tag)
        log(self.name, {"event": "open", "paper": False, "broker": "binance", "why": signal.reason, "symbol": signal.symbol, "qty": filled_qty, "price": price})
        return fill

    def close(self, pos: Position, price: float, ts: int, reason: str) -> Fill:
        side = "SELL" if pos.side == Side.BUY else "BUY"
        params = {"symbol": pos.symbol, "side": side, "type": "MARKET", "quantity": f"{pos.qty:.8f}".rstrip("0")}
        raw = self._signed("POST", "/api/v3/order", params)
        px = float(raw.get("fills", [{}])[0].get("price") or price) if raw.get("fills") else price
        self._pos.pop(pos.symbol, None)
        fill = Fill(symbol=pos.symbol, side=Side.SELL if pos.side == Side.BUY else Side.BUY, qty=pos.qty, price=px, ts=ts, tag=pos.tag, paper=False)
        log(self.name, {"event": "close", "paper": False, "broker": "binance", "reason": reason, "price": px})
        return fill
