"""Vision 2.9. A concept, real data, a legal bridge. No door price."""

from backend.core.pure_vehicle.vision import run_vision


def test_solution_waits_for_real_data_and_the_bridge_stays_legal():
    out = run_vision(
        {
            "eval_floor": 0.2,
            "concept": "Объём, который можно принять",
            "solution": "Закупка тремя партиями",
            "ideas": "Следующая партия короче",
            "data": [
                {"name": "партия", "value": "400 единиц", "real": True},
                {"name": "слух", "value": "кажется много", "real": False},
            ],
            "table": [{"label": "человек", "in": 100, "due": 40, "payable": 60}],
            "bridge": {
                "contract": "договор 14",
                "invoice": "счёт 14",
                "bank": "расчётный счёт",
                "tax": "в книге",
            },
            "purchase": {
                "parties": "две названные стороны",
                "scope": "партия 400",
                "legal": True,
            },
        }
    )
    assert out["version"] == "2.9.0"
    assert out["public_price"] is None
    assert out["door_retired"] is True
    assert out["eval_floor"] == 0.72
    assert out["floor_lowered"] is False
    assert out["yield_promised"] is False
    assert out["exchange_orders"] is False
    assert out["orders_placed"] == 0
    assert out["solution_admitted"] is True
    assert out["engineering_closed_on"] == ["партия"]
    assert out["ideas"] == "Следующая партия короче"
    assert out["table"]["yield_column"] is False
    assert out["bridge"]["open"] is True
    assert out["bridge"]["tax_visible"] is True
    assert out["purchase"]["open"] is True


def test_off_book_cash_and_empty_data_do_not_open():
    out = run_vision(
        {
            "concept": "Просто идея",
            "solution": "Купить всё",
            "ideas": "Ещё идея",
            "data": [],
            "bridge": {"path": "obnal", "off_book": True},
            "purchase": {"parties": "скрытые", "scope": "пакет", "legal": True, "hidden_from_law": True},
        }
    )
    assert out["solution_admitted"] is False
    assert out["engineering_open"] is False
    assert out["ideas"] == ""
    assert out["bridge"]["open"] is False
    assert out["purchase"]["open"] is False
    assert out["yield_promised"] is False
