"""Four lanes instead of the fifth step."""

from backend.core.pure_vehicle.lanes import place


def test_ready_autonomy_real_trade_and_separate_ideas():
    out = place(
        {
            "eval_floor": 0.5,
            "autonomy": {"work": "таблица кассы"},
            "trading": {"market": "energy"},
            "ideas": {"text": "айти-идея про таблицу"},
        }
    )
    assert out["instead_of"] == "fifth"
    assert out["does_not_rewrite"] == "2.7"
    assert out["lanes"] == ["autonomy", "trading", "ideas", "push"]
    assert out["autonomy"]["ready"] is True
    assert out["autonomy"]["accepted"] is True
    assert out["trading"]["open"] is True
    assert out["trading"]["kind"] == "real_sector"
    assert out["trading"]["orders_placed"] == 0
    assert out["ideas"]["separate"] is True
    assert out["push"] == "separate"
    assert out["yield_promised"] is False
    assert out["exchange_orders"] is False
    assert out["floor_lowered"] is False
    assert out["eval_floor"] == 0.72


def test_exchange_and_ideas_inside_the_trade_are_refused():
    out = place(
        {
            "autonomy": {"work": "таблица", "carries_trade": True},
            "trading": {"market": "crypto", "place_orders": True},
            "ideas": {"text": "идея", "inside_trade": True},
        }
    )
    assert out["autonomy"]["accepted"] is False
    assert out["trading"]["open"] is False
    assert out["trading"]["orders_placed"] == 0
    assert out["ideas"]["open"] is False
    assert out["yield_promised"] is False
