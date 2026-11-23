"""PURE VEHICLE · ALLO. Exact prices, closed recursion, no fake landing."""

from __future__ import annotations

import uuid

from backend import __codename__, __version__
from backend.config import MONETIZATION
from backend.core.coop.consult_patterns.flags import _FLAG_SPEC
from backend.core.freelance_packs import attach_pack
from backend.core.pricing_lanes import SKUS, map_tribute_amount
from backend.core.product_file import generate_paid_file
from backend.core.pure_vehicle import (
    constructor,
    contribute,
    directing,
    grant_tokens,
    green_request,
    purchase_isolated,
    science_base,
    self_improve,
    separated_circle,
)
from backend.core.pure_vehicle.catalog import FREE12, OPS
from backend.core.pure_vehicle.community import alice_signal, game_pack
from backend.core.coop import run_coop_lane
from robots.config import is_live


def test_version_and_policy():
    assert __version__ == "2.9.0"
    assert __codename__ == "VISION"
    policy = MONETIZATION["policy"]
    assert policy.get("no_subscriptions") is not True
    assert "no_subscriptions" not in policy
    assert policy["only_subscription"] == "allo_month"
    assert policy["yield_subscriptions_forbidden"] is True


def test_map_50_is_allo_not_sku_100():
    assert map_tribute_amount(50, "") == "allo_month"
    assert map_tribute_amount(50, "monthly") == "allo_month"
    assert map_tribute_amount(100, "") == "sku_100"
    assert map_tribute_amount(490, "") == "sku_490"
    assert map_tribute_amount(1000, "") == "sku_1000"
    assert map_tribute_amount(10000, "standard 1000") == "sku_10000"
    assert map_tribute_amount(None, "10000") == "sku_10000"
    assert map_tribute_amount("10,000", "pack 1000") == "sku_10000"
    assert map_tribute_amount(3290, "", "RUB") == "access_month"
    assert map_tribute_amount(3290, "") == "access_month"
    assert map_tribute_amount(75, "") != "sku_100"
    assert map_tribute_amount(50, "создание игры") == "game_pack"
    assert SKUS["directing_fee"]["name_en"].lower().find("directologist") < 0
    assert "директолог" not in SKUS["directing_fee"]["name_ru"]
    assert any("директолог" in row["wrong_move"] for row in _FLAG_SPEC)


def test_refusal_without_asset_and_recurse_closed_on_allo():
    rec = constructor(
        {
            "text": "касса как туман, хозяина нет",
            "sku": "allo_month",
            "consequence": "recurse_spec",
        }
    )
    assert rec["realize"]["ok"] is False
    assert rec["realize"]["refusal"] == "no_base_asset"
    assert rec["realize"]["landed"] is False
    assert rec["realize"]["chat"] is False
    assert rec["new_product"] is False
    assert rec["recurse_spec"]["open"] is False
    assert "sku_490" in rec["recurse_spec"]["why"]
    paid = generate_paid_file("MX-ALLO", sku_id="allo_month")
    assert paid["file"] is False
    assert paid["reason"] == "no_recursion_file"


def test_stub_line_not_sold_as_landing():
    assert len(OPS) == 7
    assert [row["n"] for row in OPS] == [1, 2, 3, 4, 5, 6, 7]
    assert OPS[1]["landed"] is True and OPS[1]["engine"]
    assert OPS[3]["stub"] is True and OPS[3]["landed"] is False
    assert OPS[4]["stub"] is True and OPS[4]["sell_as_ready"] is False
    rec = constructor(
        {
            "text": "библиотечный пак",
            "sku": "sku_1000",
            "op": 4,
            "base_asset": {"id": "orientationforge", "pays": True},
        }
    )
    assert rec["realize"]["landed"] is False
    assert rec["realize"]["stub"] is True
    assert rec["realize"]["sell_as_ready"] is False
    assert rec["recurse_spec"]["open"] is True


def test_green_directing_tokens_improve(monkeypatch):
    monkeypatch.delenv("ENABLE_COMPUTE_BROKER", raising=False)
    src = "AI-powered unlock.\nЕщё одна комната и ESG слайд.\nОставить только слот {ticker}."
    out = green_request(src, ticker="MX-1", owner="слот")
    assert out["shorter"] is True
    assert len(out["text"]) < len(src)
    assert "esg" not in out["text"].lower()
    unpaid = directing({"sku": "allo_month"}, paid=False, choice="green")
    assert unpaid["recorded"] is False and unpaid["done"] is False
    assert unpaid["directologist"] is False
    paid = directing({"sku": "sku_490"}, paid=True, choice="green")
    assert paid["done"] is True and paid["kill"]
    grant = grant_tokens("allo-subject")
    assert grant["recorded"] is True
    assert grant["status"] == 200
    assert grant["broker"] == "closed_by_flag"
    assert grant["cold_chain_enabled_by_grant"] is False
    assert self_improve("free")["reason"] == "free_category_rejected"
    assert self_improve("greening")["ok"] is True


def test_isolated_contribution_and_layers(monkeypatch):
    monkeypatch.setenv("ROBOT_MODE", "paper")
    bought = purchase_isolated("lead_inbox", "buyer-1")
    assert bought["entitlements"]["allo_month"] is False
    assert bought["entitlements"]["access"] is False
    assert bought["entitlements"]["flagship"] is False
    lane = run_coop_lane("Собери контур заявок в таблицу и отчёт понедельника с хозяином")
    lane = attach_pack(lane, "Собери контур заявок в таблицу и отчёт понедельника с хозяином")
    assert lane["pack"]["isolated"] is True
    assert lane["pack"]["grants_allo_month"] is False
    body = f"Шаблон входа: один список, один kill. {uuid.uuid4().hex}"
    first = contribute("template", body, "author-a")
    second = contribute("template", body, "author-b")
    assert first["created"] is True
    assert second["duplicate"] is True
    assert first["author"] != "author-a"
    assert "name" not in first and "phone" not in first
    assert "Karim Metrix" in first["license"]
    assert "Commercial use forbidden" in first["license"]
    leaked = contribute("template", {"name": "Ada", "body": "x"}, "author-a")
    assert leaked["ok"] is False
    base = science_base()
    assert base["eighth_product"] is False
    assert len(base["entries"]) >= 12
    assert all(row["consequence"] in FREE12 for row in base["entries"])
    alice = alice_signal({"place": 3})
    assert alice["opens_door"] is False and alice["price_changed"] is False and alice["product"] is False
    circle = separated_circle("author-a", "бумажный круг", sku="allo_month")
    assert circle["open"] is False and circle["grants_allo"] is False
    opened = separated_circle("author-a", "бумажный круг отдельный", sku="game_pack")
    assert opened["open"] is True and opened["recurse_spec"] is False and opened["merged_with_allo"] is False
    pack = game_pack()
    assert pack["allo_month"] is False and pack["recurse_spec"] is False and pack["paper"] is True
    assert is_live() is False
