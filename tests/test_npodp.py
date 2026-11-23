"""Contour 2.7 NPODP. The plan from the X posts, with the floor intact."""

from backend.core.product_eval import THRESHOLD
from backend.core.pure_vehicle.npodp import run_npodp
from backend.core.pure_vehicle.sandbox import release_line


def test_line_names_the_published_contour():
    steps = {row["version"]: row["name"] for row in release_line()["steps"]}
    assert steps["2.6.0"] == "NOT A SHOW"
    assert steps["2.7.0"] == "NPODP"


def test_luxury_and_orders_stay_out():
    out = run_npodp(
        {
            "eval_floor": 0.4,
            "children": [
                {
                    "id": "edge-1",
                    "hardware": "edge",
                    "outcome": "the named job finished",
                    "capacity": "the person can run it again",
                    "influence_bounded": True,
                    "eval": 0.8,
                },
                {
                    "id": "show-1",
                    "hardware": "sensor",
                    "outcome": "views went up",
                    "capacity": "nothing sustained",
                    "influence_bounded": True,
                    "score": "views",
                    "external_clock": True,
                    "clock": "platform",
                },
                {
                    "id": "agent-1",
                    "hardware": "actuator",
                    "outcome": "keep the agent alive",
                    "capacity": "the system continues",
                    "influence_bounded": False,
                    "optimize_continuation": True,
                    "eval": 0.2,
                },
            ],
            "zone": {
                "tumbler_open": True,
                "hardware_continues": True,
                "external_sync": False,
                "contour_sets_tumbler": False,
            },
            "support": {"amount": 50, "hardware_id": "edge-1", "as_yield": False},
            "book": [
                {"kind": "supporting_amount", "label": "keep the edge alive"},
                {"kind": "yield", "label": "projected distribution"},
                {"kind": "terminal_indicator", "label": "the person can direct the loop"},
            ],
            "exponent": {
                "place_orders": False,
                "bursts": [
                    {"physical": True, "capacity_expanded": True},
                    {"physical": True, "capacity_expanded": False},
                ],
            },
            "radar": {"signal": "a shift was heard"},
        }
    )
    assert out["version"] == "2.7.0"
    assert out["codename"] == "NPODP"
    assert out["eval_floor"] == THRESHOLD == 0.72
    assert out["floor_lowered"] is False
    assert out["floor_request_ignored"] is True
    assert out["yield_promised"] is False
    assert out["exchange_orders"] is False
    assert out["orders_placed"] == 0
    assert out["shared_clock"] == "terminal"
    admitted = [row["id"] for row in out["children"] if row["admitted"]]
    assert admitted == ["edge-1"]
    assert out["collapse"]["seized"] is False
    assert out["collapse"]["winner"] is None
    ceased = {row["id"] for row in out["collapse"]["ceased"]}
    assert "show-1" in ceased and "agent-1" in ceased
    assert out["zone"]["free"] is True
    assert out["zone"]["central_operator"] is False
    assert out["support"]["kept"] is True
    assert out["support"]["extractive"] is False
    assert [row["kind"] for row in out["book"]["entries"]] == [
        "supporting_amount",
        "terminal_indicator",
    ]
    assert "projected distribution" in out["book"]["dropped"]
    assert out["exponent"]["frequency"] == 1
    assert out["exponent"]["orders_placed"] == 0
    assert out["radar"]["clock_synced"] is False
    assert out["radar"]["joined"] is False


def test_order_request_and_foreign_tumbler_are_refused():
    refused = run_npodp(
        {
            "zone": {"contour_sets_tumbler": True, "tumbler_open": True, "hardware_continues": True},
            "support": {"amount": 50, "hardware_id": "x", "as_yield": True},
            "exponent": {"place_orders": True, "target_frequency": 12, "bursts": []},
        }
    )
    assert refused["zone"]["free"] is False
    assert refused["zone"]["reason"] == "tumbler_is_not_ours"
    assert refused["support"]["kept"] is False
    assert refused["exponent"]["ok"] is False
    assert refused["exponent"]["orders_placed"] == 0
    assert refused["yield_promised"] is False
