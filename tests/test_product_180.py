from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.access import consume, mint_token, redeem, subject_hash, token_hash
from backend.core.artefacts import analytical_panel, offer_generator
from backend.core.product_180 import FLAGSHIP, PRICING, VERSION
from backend.core.sales_offer import ACCESS_RUB, BOT_LAND_MAX_USD, METRIX_AI_USD, access_offer, sales_readiness
from backend.core.risk_engine import r_after_close, size
from backend.core.strategies import list_strategies, run_strategy
from backend.core.teammates import build_teammate, list_teammates
from robots.core.types import Bar, Side
from robots.strategies.two_leg_tape import TwoLegTape
from telegram_app.menu import menu_action


def test_version_and_flagship():
    assert VERSION.startswith("1.8")
    assert FLAGSHIP["name"] == "In-Out Chain"
    assert PRICING["access"]["rub"] == 3290
    assert ACCESS_RUB == 3290
    assert BOT_LAND_MAX_USD <= 1990
    assert PRICING["bot_land"]["usd"] <= BOT_LAND_MAX_USD
    assert METRIX_AI_USD == 2490
    assert PRICING["metrix_ai"]["usd"] == 2490
    assert PRICING["access"]["usd"] != 5
    offer = access_offer(lang="ru")
    assert "3290" in offer["cta_ru"]
    assert "гарантир" not in offer["copy"]["text"].lower()
    ready = sales_readiness()
    assert ready["access"]["rub"] == 3290
    assert ready["main_package_ready"] is False


def test_menu_three_formal_tabs():
    assert menu_action("In-Out Chain") == "chain"
    assert menu_action("AI Teammates") == "teammates"
    assert menu_action("Artefacts") == "artefacts"
    assert menu_action("Лендинг") == "chain"
    assert menu_action("Движок") == "teammates"
    assert menu_action("Мейкинг") == "artefacts"
    assert menu_action("/chain") == "chain"
    assert menu_action("/teammates@karimmetrixbot") == "teammates"


def test_four_models_and_legal_copy():
    ids = {s["id"] for s in list_strategies()}
    assert ids == {"target_place", "demand", "ampli", "two_leg_tape"}
    art = run_strategy("two_leg_tape", "хайп в ленте, хочу x20 плечо")
    blob = (art["one_liner"] + art["move"] + art["title"]).lower()
    assert "плеч" in blob or "ног" in blob
    assert "сигнал" not in art["title"].lower()
    assert art["meta"]["legal"].startswith("код")


def test_risk_does_not_confuse_r_with_leverage():
    ok = size(equity=10_000, entry=100, stop=99, risk_pct=0.5, max_leverage=1.0)
    assert ok["ok"] is True
    assert ok["r_multiple"] is None
    assert ok["leverage"] <= 1.0
    tight = size(equity=10_000, entry=100, stop=99.9, risk_pct=0.5, max_leverage=1.0)
    assert tight["ok"] is True
    assert tight["leverage"] <= 1.0 + 1e-6
    assert r_after_close(entry=100, exit_px=103, stop=99, side="buy") == 3.0


def test_teammates_user_facing():
    ids = {t["id"] for t in list_teammates()}
    assert ids == {"saas", "agency", "edu", "ecom"}
    art = build_teammate("edu", "онлайн-школа, уроки не продают следующий шаг")
    assert art["niche_id"] == "edu"
    assert "Cohort" in art["title"] or "когорт" in art["user_facing"].lower()
    assert art["meta"]["money_unit"]
    assert art["meta"]["silence"]


def test_access_token_is_hashed():
    minted = mint_token(days=31, sku="access_month")
    raw = minted["token"]
    assert raw.startswith("mx_")
    assert token_hash(raw) != raw
    out = redeem(raw, bind_subject=subject_hash(42))
    assert out["ok"] is True
    gate = consume(subject_hash(42), "strategy")
    assert gate["allowed"] is True
    anon = consume(None, "strategy")
    assert anon["allowed"] is False
    import uuid

    sid = subject_hash(f"free-{uuid.uuid4()}")
    assert consume(sid, "strategy")["allowed"] is True
    assert consume(sid, "strategy")["allowed"] is True
    third = consume(sid, "strategy")
    assert third["allowed"] is False
    assert third.get("reason") == "free_done"


def test_artefacts_panel_readable():
    panel = analytical_panel("касса как туман, онбординг жрёт маржу")
    assert panel["kind"] == "artefact.panel"
    assert panel["readable"]
    assert "vvi" in panel["meta"]["metrics"]
    offer = offer_generator("собери пакет на 14 дней для агентства")
    assert offer["kind"] == "artefact.offer"


def test_two_leg_tape_quiet_without_legs():
    from datetime import datetime, timedelta, timezone

    t0 = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    bars = []
    for i in range(50):
        t = t0 + timedelta(minutes=15 * i)
        bars.append(
            Bar(
                ts=int(t.timestamp() * 1000),
                open=10,
                high=10.1,
                low=9.9,
                close=10.05,
                volume=100,
            )
        )
    sig = TwoLegTape().on_bars(bars, "SOLUSDT")
    assert sig.side == Side.FLAT
    assert sig.meta.get("leverage") is None
