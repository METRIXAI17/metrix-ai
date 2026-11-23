"""CLOSED SANDBOX 2.8. The floor stays. The person stays outside."""

from backend.core.product_eval import THRESHOLD
from backend.core.pure_vehicle.sandbox import close_sandbox, release_line


def test_line_is_eight_steps_and_floor_is_not_lowered():
    line = release_line()
    versions = [step["version"] for step in line["steps"]]
    assert versions == [
        "2.1.0",
        "2.2.0",
        "2.3.0",
        "2.4.0",
        "2.5.0",
        "2.6.0",
        "2.7.0",
        "2.8.0",
        "2.9.0",
    ]
    assert line["version"] == "2.9.0"
    assert line["door"] == "2.1.0"
    assert line["eval_floor"] == 0.72
    assert line["eval_floor"] == THRESHOLD
    assert line["yield_promised"] is False
    assert line["exchange_orders"] is False
    assert line["person_inside"] is False
    assert line["spirit_sku"] is False


def test_escaped_agents_do_not_take_the_person():
    out = close_sandbox(
        {
            "eval_floor": 0.5,
            "agents": [
                {"id": "a", "resource": "brief", "eval": 0.8},
                {"id": "b", "resource": "money", "escaped": True, "eval": 0.9},
                {"id": "c", "resource": "person", "eval": 0.4},
                {"id": "d", "resource": "karim", "escaped": True},
            ],
        }
    )
    assert out["closed"] is True
    assert out["floor_lowered"] is False
    assert out["floor_request_ignored"] is True
    assert out["eval_floor"] == 0.72
    assert out["winner"] is None
    assert out["yield_promised"] is False
    assert out["exchange_orders"] is False
    assert out["person_inside"] is False
    assert [row["id"] for row in out["seated"]] == ["a"]
    refused = {row["id"]: row["reasons"] for row in out["refused"]}
    assert "resource_refused" in refused["b"]
    assert "returned_to_contour" in refused["b"]
    assert "below_eval_floor" in refused["c"]
    assert "resource_refused" in refused["d"]
