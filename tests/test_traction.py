"""Traction on the 2.9 engine. Does not rewrite contour 2.7."""

from backend.core.product_eval import THRESHOLD
from backend.core.pure_vehicle.npodp import VERSION as NPODP_VERSION
from backend.core.pure_vehicle.traction import pull, pull_brief
from backend.core.pure_vehicle.vision import run_vision


def _full() -> dict:
    return {
        "eval_floor": 0.4,
        "concept": "Объёмная закупка 400",
        "solution": "Собрать партию 400",
        "ideas": "Следующая партия короче",
        "data": [{"name": "партия", "value": "400", "real": True}],
        "table": [{"label": "касса", "in": 400, "due": 100, "payable": 300}],
        "bridge": {"from": "касса", "to": "партия", "amount": "400"},
        "purchase": {"parties": "две стороны", "scope": "партия 400"},
    }


def test_full_pull_holds_and_does_not_touch_2_7():
    out = pull(_full())
    assert out["version"] == "2.9.0"
    assert out["does_not_rewrite"] == "2.7"
    assert out["eval_floor"] == THRESHOLD == 0.72
    assert out["floor_lowered"] is False
    assert out["floor_request_ignored"] is True
    assert out["yield_promised"] is False
    assert out["orders_placed"] == 0
    assert out["held"] == list(out["order"])
    assert out["traction"] == 1.0
    assert out["table_words"] == ["пришло", "должно", "можно заплатить"]
    assert NPODP_VERSION == "2.7.0"


def test_ideas_do_not_open_over_a_slip():
    body = _full()
    body["data"] = [{"name": "слух", "value": "много", "real": False}]
    body["ideas"] = "Идея вместо сборки"
    out = pull(body)
    assert "volume" in out["slipped"]
    assert "engineering" in out["slipped"]
    assert "ideas" in out["slipped"]
    assert out["traction"] < 1


def test_yield_and_hidden_path_slip():
    body = _full()
    body["concept"] = "Объём и гарантированная доходность"
    body["bridge"] = {"path": "obnal", "off_book": True, "from": "a", "to": "b", "amount": "400"}
    out = pull(body)
    assert "aim" in out["slipped"]
    assert "bridge" in out["slipped"]
    assert out["yield_promised"] is False
    assert out["exchange_orders"] is False


def test_engine_brief_and_vision_carry_traction():
    brief = pull_brief("Объёмная закупка 400. Пришло 400, должно 100, можно заплатить 300.")
    assert brief["layer"] == "traction"
    assert brief["orders_placed"] == 0
    vision = run_vision(_full())
    assert vision["traction"]["traction"] == 1.0
    assert vision["version"] == "2.9.0"
