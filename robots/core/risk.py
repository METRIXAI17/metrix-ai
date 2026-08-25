from __future__ import annotations

from robots.config import MAX_DAILY_LOSS_PCT, RISK_PCT
from robots.core.types import Signal, Side


class RiskGate:
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
        steps = max(0, int(raw / qty_step))
        qty = steps * qty_step
        if qty < min_qty:
            return 0.0
        return qty
