"""DeadendRouter UNBLOCK modes."""

from __future__ import annotations

from backend.core.coop.deadend import DeadendRouter, is_deadlock
from backend.core.market_units_v2.coordination import CoordinationLayer
from backend.monetization.sales_pointer import build_pointer


def test_missing_metric_unblock():
    r = DeadendRouter().route("сделай бота и автоматизируй всё без цифр")
    assert r["mode"] == "UNBLOCK"
    assert "MISSING_METRIC" in r["codes"]
    assert r["next_question"]
    assert r["allow_codegen"] is False


def test_multi_loco_silent_picks_cash():
    r = DeadendRouter().route(
        "игры+edu+видео+чипы+стор платформа сразу",
        silent=True,
    )
    assert "MULTI_LOCO" in r["codes"]
    assert "заявки/касса" in (r["assumed"].get("chosen_stream") or "")


def test_magic_sales():
    r = DeadendRouter().route("сделайте контур и увеличьте продажи в три раза, прод ×3")
    assert "MAGIC_SALES" in r["codes"]
    assert r["mode"] == "UNBLOCK"


def test_coordination_deadlock_reasons():
    c = CoordinationLayer().compute(missing_metric=True, multi_loco=True, magic_sales_kpi=True)
    assert c.unblock_mode == "UNBLOCK"
    assert c.deadlock_risk >= 0.72
    assert "MISSING_METRIC" in c.deadlock_reasons
    d = c.to_dict()
    assert d["unblock_mode"] == "UNBLOCK"


def test_is_deadlock_helper():
    assert is_deadlock("сделай бота без цифр и без хозяина")


def test_sales_pointer_dry():
    p = build_pointer("заявки из телеги теряются, бот за 30к предлагают")
    assert "трафик" in p["talk"].lower() or "минус" in p["talk"].lower()
    assert p["method_named_to_client"] is False
    assert p["banned"] == []
    assert "локомотив" not in p["talk"]
    assert "!" not in p["talk"]
