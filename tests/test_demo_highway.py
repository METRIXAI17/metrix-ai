"""Demo highway, named strategies, agent studio, resonance miner."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.agent_studio import build_agent, list_niches, resolve_niche
from backend.core.demo_highway import build_demo, detect_lane, format_telegram
from backend.core.resonance import resonate
from backend.core.strategies import list_strategies, run_strategy
from backend.core.x_posts import list_posts


def test_lane_detection():
    assert detect_lane("торгую золото, догоняю ход") == "strategy"
    assert detect_lane("SaaS 120 человек, фичи без экономики") == "agent"
    assert detect_lane("хочу упаковать оффер консультанта") == "model"


def test_target_place_has_entry_exit():
    art = run_strategy("target_place", "золото, вхожу когда уже ушло")
    assert art["strategy_id"] == "target_place"
    assert art["meta"]["entry"]
    assert art["meta"]["exit"]
    assert "воздух" in (art["one_liner"] + art["move"]).lower() or "места" in art["move"]
    assert "сигнал" not in art["title"].lower()


def test_demand_window_before_name():
    art = run_strategy("demand", "местный мемкоин, листинг на днях")
    assert art["meta"]["window"]
    assert "окно" in (art["one_liner"] + art["move"]).lower()


def test_ampli_does_not_predict():
    art = run_strategy("ampli", "nasdaq, хочу угадать лонг")
    blob = (art["one_liner"] + art["move"] + art["title"]).lower()
    assert "амплитуд" in blob
    assert any("не угад" in a.lower() or "не направление" in a.lower() for a in [art["title"], art["one_liner"], *art["anti"]])


def test_three_strategies_listed():
    ids = {s["id"] for s in list_strategies()}
    assert ids == {"target_place", "demand", "ampli"}


def test_agent_niches_and_why_builder():
    assert {n["id"] for n in list_niches()} == {"saas", "agency", "edu", "ecom"}
    assert resolve_niche(None, "онлайн-школа, уроки не продают") == "edu"
    art = build_agent("saas", "IT компания 180 человек, фичи пилим из Slack")
    assert art["niche_id"] == "saas"
    assert art["meta"]["why_builder"]
    assert "финмодел" in (art["move"] + art["one_liner"]).lower() or "unit" in art["one_liner"].lower()


def test_demo_highway_and_resonance():
    art = build_demo("агентство performance, онбординг съедает маржу на каждом клиенте")
    assert art["id"]
    assert art["lane"] in ("agent", "model")
    html = format_telegram(art)
    assert "Где ломается" in html
    hit = resonate(art["id"], "зашло")
    assert hit["verdict"] == "hit"
    assert hit["paid_path"]["sku"] == "pilot_14"
    miss = resonate(art["id"], "мимо")
    assert miss["verdict"] == "miss"


def test_x_posts_are_postable():
    posts = list_posts()
    assert len(posts) >= 12
    for p in posts:
        assert 80 < len(p["body"]) < 1200
        assert "гарантир" not in p["body"].lower()
        assert "🚀" not in p["body"]
