"""MetaTrader 5 adapter for gold (XAUUSD). Optional: pip install MetaTrader5."""

from __future__ import annotations

from robots.config import env, env_int
from robots.core.journal import log
from robots.core.types import Fill, Position, Side, Signal


class MT5Broker:
    paper = False

    def __init__(self, name: str = "target_place") -> None:
        try:
            import MetaTrader5 as mt5  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Поставьте MetaTrader5: pip install MetaTrader5. Терминал MT5 должен быть запущен.") from exc
        self.mt5 = mt5
        if not mt5.initialize():
            login = env_int("MT5_LOGIN", 0)
            password = env("MT5_PASSWORD")
            server = env("MT5_SERVER")
            if login and password and server:
                ok = mt5.initialize(login=login, password=password, server=server)
            else:
                ok = False
            if not ok:
                raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
        self.name = name
        self._pos: dict[str, Position] = {}

    def equity(self) -> float:
        info = self.mt5.account_info()
        return float(info.equity) if info else 0.0

    def position(self, symbol: str) -> Position | None:
        got = self.mt5.positions_get(symbol=symbol)
        if not got:
            return self._pos.get(symbol)
        p = got[0]
        side = Side.BUY if p.type == self.mt5.POSITION_TYPE_BUY else Side.SELL
        pos = Position(symbol=symbol, side=side, qty=float(p.volume), entry=float(p.price_open), sl=float(p.sl), tp=float(p.tp), tag="mt5")
        self._pos[symbol] = pos
        return pos

    def market(self, signal: Signal, qty: float) -> Fill:
        mt5 = self.mt5
        symbol = signal.symbol
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"MT5 symbol_select failed {symbol} {mt5.last_error()}")
        tick = mt5.symbol_info_tick(symbol)
        info = mt5.symbol_info(symbol)
        if not tick or not info:
            raise RuntimeError("no tick")
        order_type = mt5.ORDER_TYPE_BUY if signal.side == Side.BUY else mt5.ORDER_TYPE_SELL
        price = float(tick.ask if signal.side == Side.BUY else tick.bid)
        filling = info.filling_mode
        type_filling = mt5.ORDER_FILLING_IOC
        if filling & 1:
            type_filling = mt5.ORDER_FILLING_FOK
        elif filling & 2:
            type_filling = mt5.ORDER_FILLING_IOC
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(qty),
            "type": order_type,
            "price": price,
            "sl": float(signal.sl),
            "tp": float(signal.tp),
            "deviation": 40,
            "magic": 260825,
            "comment": (signal.tag or "target_place")[:31],
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": type_filling,
        }
        res = mt5.order_send(req)
        if res is None or res.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"MT5 order_send {getattr(res, 'retcode', None)} {getattr(res, 'comment', None)} {mt5.last_error()}")
        fill = Fill(symbol=symbol, side=signal.side, qty=qty, price=float(res.price or price), ts=0, tag=signal.tag, paper=False, raw={"order": res.order})
        self._pos[symbol] = Position(symbol=symbol, side=signal.side, qty=qty, entry=fill.price, sl=signal.sl, tp=signal.tp, tag=signal.tag)
        log(self.name, {"event": "open", "paper": False, "broker": "mt5", "why": signal.reason, **{k: v for k, v in fill.__dict__.items() if k != "raw"}})
        return fill

    def close(self, pos: Position, price: float, ts: int, reason: str) -> Fill:
        mt5 = self.mt5
        tick = mt5.symbol_info_tick(pos.symbol)
        close_type = mt5.ORDER_TYPE_SELL if pos.side == Side.BUY else mt5.ORDER_TYPE_BUY
        px = float(tick.bid if pos.side == Side.BUY else tick.ask) if tick else price
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": float(pos.qty),
            "type": close_type,
            "price": px,
            "deviation": 40,
            "magic": 260825,
            "comment": reason[:31],
            "type_time": mt5.ORDER_TIME_GTC,
            "position": 0,
        }
        got = mt5.positions_get(symbol=pos.symbol)
        if got:
            req["position"] = got[0].ticket
        res = mt5.order_send(req)
        if res is None or res.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"MT5 close failed {getattr(res, 'comment', None)}")
        fill = Fill(symbol=pos.symbol, side=Side.SELL if pos.side == Side.BUY else Side.BUY, qty=pos.qty, price=float(res.price or px), ts=ts, tag=pos.tag, paper=False)
        self._pos.pop(pos.symbol, None)
        log(self.name, {"event": "close", "paper": False, "broker": "mt5", "reason": reason, "price": fill.price})
        return fill
