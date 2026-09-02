"""Risk engine. R-multiple is an outcome. Leverage is a size decision.

They are not the same number. Sizing from a desired R is how accounts die.
"""

from __future__ import annotations

from typing import Any

from backend.core.code_event import CodeEvent, Trigger
from backend.core.resonance import new_id


DEFAULTS = {
    "risk_pct": 0.5,  # % of equity at the stop, not at the target
    "max_leverage": 1.0,  # 1.0 = cash. Never "crank to make 3R worth it"
    "max_notional_mult": 2.0,  # hard cap vs equity even if stop is tight
    "max_daily_loss_pct": 2.0,
    "min_rr_to_arm": 1.2,  # skip if close trigger is closer than stop — not a size input
}


def explain() -> dict[str, Any]:
    return {
        "id": "risk_engine",
        "title": "Risk Engine",
        "accent": "#fb7185",
        "one_liner": "R — мера исхода. Плечо — решение о размере. Движок их не путает.",
        "break": (
            "Люди видят «хочу 3R» и крутят плечо, чтобы пункт стоил дороже. "
            "Это не контроль риска. Это неконтролируемое плечо под видом мультипликатора."
        ),
        "move": (
            "Размер считается только от стоп-триггера: risk_cash = equity × risk_pct, "
            "qty = risk_cash / |entry − stop|. "
            "Если получившийся нотионал / equity > max_leverage — размер режется, "
            "а не стоп двигается и не плечо растёт. "
            "Плановый R нигде не входит в формулу размера."
        ),
        "rules": [
            "R считается после закрытия: (exit − entry) / |entry − stop|.",
            "Плечо = notional / equity. Касса по умолчанию: max_leverage = 1.0.",
            "Дневной стоп — отдельный kill, не «ещё одна попытка в том же R».",
            "Нет стоп-триггера — нет размера. Нет исключения «ну очень уверен».",
        ],
        "anti": [
            "Не считать размер от цели («чтобы 3R дали N долларов»).",
            "Не двигать стоп, чтобы влезло плечо.",
            "Не называть плечо мультипликатором модели.",
            "Не усредняться: это скрытое плечо.",
        ],
        "defaults": DEFAULTS,
        "legal": "код согласованной модели, не сигнал",
    }


def size(
    *,
    equity: float,
    entry: float,
    stop: float,
    risk_pct: float | None = None,
    max_leverage: float | None = None,
    max_notional_mult: float | None = None,
    contract: float = 1.0,
    min_qty: float = 0.0,
    qty_step: float = 0.0,
) -> dict[str, Any]:
    rp = DEFAULTS["risk_pct"] if risk_pct is None else float(risk_pct)
    lev_cap = DEFAULTS["max_leverage"] if max_leverage is None else float(max_leverage)
    notion_cap = DEFAULTS["max_notional_mult"] if max_notional_mult is None else float(max_notional_mult)

    if equity <= 0 or entry <= 0:
        return _reject("нет капитала или цены входа")
    stop_dist = abs(entry - stop)
    if stop_dist <= 0:
        return _reject("нет стоп-триггера — нет размера")

    risk_cash = equity * (rp / 100.0)
    raw_qty = risk_cash / (stop_dist * contract)
    notional = raw_qty * entry * contract
    implied = notional / equity if equity else 0.0

    notes: list[str] = []
    qty = raw_qty
    if implied > lev_cap:
        qty = (equity * lev_cap) / (entry * contract)
        notes.append(
            f"плечо {implied:.2f}× обрезано до {lev_cap:.2f}×. "
            "Не увеличиваем плечо, чтобы «окупить» R."
        )
        if qty * stop_dist * contract > risk_cash + 1e-9:
            return _reject(
                "стоп слишком широкий для разрешённого плеча. "
                "Не добавляем плечо и не двигаем стоп."
            )
    notional = qty * entry * contract
    if equity and (notional / equity) > notion_cap:
        qty = (equity * notion_cap) / (entry * contract)
        notes.append(f"нотионал обрезан до {notion_cap:.1f}× капитала")

    if qty_step > 0:
        qty = max(0.0, int(qty / qty_step) * qty_step)
    if qty < min_qty:
        return _reject("размер меньше минимального лота — пропуск, не набор плеча")

    implied = (qty * entry * contract) / equity if equity else 0.0
    r_at_stop = -1.0  # by construction: stop loss = 1R of risk_cash, if not clipped
    return {
        "ok": True,
        "qty": round(qty, 8),
        "risk_cash": round(qty * stop_dist * contract, 4),
        "risk_pct_used": round((qty * stop_dist * contract) / equity * 100.0, 4) if equity else 0,
        "notional": round(qty * entry * contract, 4),
        "leverage": round(implied, 4),
        "r_multiple": None,
        "r_note": "R не используется для размера. Появится после закрытия.",
        "stop_distance": round(stop_dist, 8),
        "planned_loss_if_stop": round(qty * stop_dist * contract, 4),
        "notes": notes or ["размер от стоп-триггера, не от цели"],
        "rejected": False,
    }


def _reject(reason: str) -> dict[str, Any]:
    return {
        "ok": False,
        "qty": 0.0,
        "rejected": True,
        "reason": reason,
        "r_multiple": None,
        "leverage": 0.0,
    }


def r_after_close(*, entry: float, exit_px: float, stop: float, side: str) -> float:
    risk = abs(entry - stop)
    if risk <= 0:
        return 0.0
    sign = 1.0 if side in ("buy", "long") else -1.0
    return round(sign * (exit_px - entry) / risk, 4)


def attach_to_event(event: CodeEvent, equity: float, **kw: Any) -> dict[str, Any]:
    sized = size(equity=equity, entry=event.entry, stop=event.stop.price, **kw)
    return {
        "code_event": event.as_dict(),
        "risk": sized,
        "legal": "код согласованной модели + риск-движок, не сигнал",
    }


def daily_kill(day_pnl: float, start_equity: float, cap_pct: float | None = None) -> dict[str, Any]:
    cap = DEFAULTS["max_daily_loss_pct"] if cap_pct is None else float(cap_pct)
    if start_equity <= 0:
        return {"killed": True, "reason": "нет капитала"}
    dd = -day_pnl / start_equity * 100.0 if day_pnl < 0 else 0.0
    killed = dd >= cap
    return {
        "killed": killed,
        "drawdown_pct": round(dd, 4),
        "cap_pct": cap,
        "reason": f"дневной стоп {dd:.2f}% ≥ {cap}%" if killed else "",
    }


def demo_card(brief: str = "") -> dict[str, Any]:
    """User-facing artefact: risk engine as a named product, not a slider."""
    card = explain()
    example = size(equity=10_000, entry=2400, stop=2388, risk_pct=0.5, max_leverage=1.0)
    bad = size(equity=10_000, entry=2400, stop=2399.5, risk_pct=0.5, max_leverage=1.0)
    return {
        "id": new_id(),
        "kind": "risk.engine",
        "lane": "chain",
        "title": "Risk Engine · не путает R с плечом",
        "one_liner": card["one_liner"],
        "break": card["break"],
        "move": card["move"],
        "steps": card["rules"],
        "anti": card["anti"],
        "artifact_week": (
            "Журнал: на каждую сделку отдельно записать стоп-триггер, размер от стопа, "
            "плечо (должно быть ≤ 1.0 на кассе), и R только после закрытия."
        ),
        "meta": {
            "defaults": DEFAULTS,
            "example_ok": example,
            "example_tight_stop_clipped": bad,
            "brief": (brief or "")[:400],
            "stop_trigger": Trigger("price", "инвалидация тезиса", 0).as_dict(),
            "close_trigger": Trigger("rule", "правило модели, не настроение", 0).as_dict(),
        },
        "disclaimer": (
            "Это код согласованной модели. Обновляется в реальном времени как есть. "
            "Не торговый сигнал и не обещание доходности."
        ),
    }
