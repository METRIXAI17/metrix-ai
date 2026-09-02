from __future__ import annotations

from robots.config import MAX_DAILY_LOSS_PCT, RISK_PCT
from robots.core.types import Signal, Side

# Cash default. R-multiple is never an input to size().
MAX_LEVERAGE = 1.0
MAX_NOTIONAL_MULT = 2.0


class RiskGate:
    """Size from stop distance. Never from a desired R. Never by cranking leverage."""

    def __init__(self, equity: float) -> None:
        self.start_equity = equity
        self.equity = equity
        self.day_pnl = 0.0
        self.killed = False
        self.kill_reason = ""

    def mark_pnl(self, pnl: float) -> None:
        self.day_pnl += pnl
        self.equity += pnl
        if self.start_equity > 0:
            dd = -self.day_pnl / self.start_equity * 100.0
            if dd >= MAX_DAILY_LOSS_PCT:
                self.killed = True
                self.kill_reason = f"дневной стоп {dd:.2f}% >= {MAX_DAILY_LOSS_PCT}%"

    def size(self, signal: Signal, *, min_qty: float, qty_step: float, contract: float = 1.0) -> float:
        if self.killed or signal.side == Side.FLAT or signal.risk <= 0:
            return 0.0
        risk_cash = self.equity * (RISK_PCT / 100.0)
        raw = risk_cash / (signal.risk * contract)
        notional = raw * signal.entry * contract
        implied = notional / self.equity if self.equity else 0.0
        if implied > MAX_LEVERAGE:
            raw = (self.equity * MAX_LEVERAGE) / (signal.entry * contract) if signal.entry else 0.0
            if raw * signal.risk * contract > risk_cash:
                return 0.0
        notional = raw * signal.entry * contract
        if self.equity and (notional / self.equity) > MAX_NOTIONAL_MULT:
            raw = (self.equity * MAX_NOTIONAL_MULT) / (signal.entry * contract)
        steps = max(0, int(raw / qty_step)) if qty_step else 0
        qty = steps * qty_step if qty_step else raw
        if qty < min_qty:
            return 0.0
        return qty
