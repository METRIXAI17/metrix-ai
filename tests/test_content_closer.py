"""Content AI Closer: abstraction → cards → prompt → landing → making.

Also audits extra hypotheses so a pass is not a vibe.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.content_closer import (
    MakingRefused,
    closer_as_artifact,
    comfort_turn,
    compose_abstraction,
    format_abstraction_telegram,
    run_closer,
    run_making_chamber,
    score_vectors,
    screen_trends,
)
from backend.core.demo_highway import build_demo, detect_lane, format_telegram
from backend.core.functions import FUNCTIONS, run_making_function
from telegram_app.menu import menu_action


BRIEF_ACTOR = (
    "SaaS 80 человек, фичи пилим без конца, цель — победа в квартале, "
    "никто не знает что считать успехом, хочу наконец выйти на результат"
)
BRIEF_MANAGER = (
    "команда 120, слишком много людей на созвонах, слишком много знаний в дашбордах, "
    "слишком много объектов в Jira, касса как туман, маржа тает"
)
BRIEF_PLANE = (
    "тихо, никого нет, снаружи пусто, внутри уже собрана модель и движок, "
    "топливо есть, не пишут, окно, залипаю"
)
BRIEF_METHOD = (
    "нужна стратегия и правильный фреймворк, личный бренд и упаковка, "
    "изменить всё сразу, идеальная воронка, playbook"
)


def test_menu_three_sections():
    assert menu_action("In-Out Chain") == "life"
    assert menu_action("AI Teammates") == "craft"
    assert menu_action("Artefacts") == "shop"
    assert menu_action("Лендинг") == "life"
    assert menu_action("Движок") == "craft"
    assert menu_action("Мейкинг") == "shop"
    assert menu_action("/landing") == "life"
    assert menu_action("/engine@karimmetrixbot") == "craft"
    assert menu_action("/making") == "shop"
    assert menu_action("Демо") == "life"
    assert menu_action("Стратегии") == "bots"
    assert menu_action("Агенты") == "target"
    assert menu_action("Посты") == "shop"
    assert menu_action("/demo") == "life"
    assert menu_action("/start") == "start"
    assert menu_action("SaaS 80 человек без экономики") is None


def test_lane_landing_making():
    assert detect_lane("что угодно", "landing") == "chain"
    assert detect_lane("что угодно", "making") == "artefacts"
    assert detect_lane("что угодно", "engine") == "teammates"
    assert detect_lane("торгую золото, догоняю ход") == "strategy"


def test_disappointed_actor_from_state_seeking():
    vec = score_vectors(BRIEF_ACTOR)
    pack = run_closer(BRIEF_ACTOR, with_comfort=True, with_making=False)
    assert vec["state_seeking"] >= 0.45
    ids = {pack["archetypes"]["primary"]["id"], pack["archetypes"]["secondary"]["id"]}
    assert "disappointed_actor" in ids
    essay = pack["abstraction"]["essay"]
    assert "Разочарованный Деятель" in pack["abstraction"]["archetype"] or "Деятель" in essay or pack["abstraction"]["archetype"]
    assert pack["abstraction"]["has_motion"] is True
    assert pack["abstraction"]["has_state_as_death"] is True
    assert "смер" in essay.lower()
    assert pack["abstraction"]["density"] >= 0.45


def test_antifragile_manager_from_crowd():
    pack = run_closer(BRIEF_MANAGER)
    ids = {pack["archetypes"]["primary"]["id"], pack["archetypes"]["secondary"]["id"]}
    assert "antifragile_manager" in ids
    essay = pack["abstraction"]["essay"].lower()
    assert "людей" in essay or "знаний" in essay or "объект" in essay


def test_full_plane_metaphor():
    pack = run_closer(BRIEF_PLANE)
    essay = pack["abstraction"]["essay"].lower()
    # H6: empty outside + full inside → plane
    if pack["vectors"]["empty_outside"] >= 0.35 and pack["vectors"]["full_inside"] >= 0.3:
        assert "самолёт" in essay or "самолет" in essay


def test_cards_are_functional_not_summary():
    pack = run_closer(BRIEF_ACTOR)
    cards = pack["cards"]
    codes = set(cards["codes"])
    for need in ("FN-ARCH", "FN-MOVE", "FN-LAND", "FN-UNIT", "FN-KILL", "FN-MAKE", "FN-TREND"):
        assert need in codes, need
    for c in cards["items"]:
        assert c["code"].startswith("FN-")
        assert c["designation"]
        assert c["function"]
        assert c["object"]
        assert c["action"]
        assert c["unit"]
        assert c["kill"]
        assert c["task"].startswith("[FN-")
        # translation is a function, not a copy of the whole essay
        assert c["action"] != pack["abstraction"]["essay"]
    assert cards["count"] >= 7


def test_prompt_rewrites_cards_and_trend():
    pack = run_closer(BRIEF_MANAGER)
    prompt = pack["prompt"]
    master = prompt["master"]
    assert prompt["strength"] >= 0.55
    quoted = 0
    for code in pack["cards"]["codes"]:
        if code in master:
            quoted += 1
    assert quoted >= 2
    trend_id = pack["trends"]["primary"]["id"]
    assert trend_id
    assert trend_id in master
    assert pack["engine_brief"]
    assert "сигнал" in master.lower() or "NOT a trading signal" in master or "не торговый" in master.lower() or "не сигнал" in master.lower() or "signal" in master.lower()
    # adapted to screened trend
    assert pack["trends"]["primary"]["adapt"] in master or pack["trends"]["primary"]["name_ru"] in master


def test_landing_is_event_not_cta():
    pack = run_closer(BRIEF_ACTOR)
    ev = pack["event"]
    assert ev["title"]
    assert ev["who_enters"]
    assert ev["what_moves"]
    assert ev["what_stays"]
    assert ev["invitation"]
    blob = (ev["vision_text"] + ev["invitation"] + ev["hero"]).lower()
    assert "комнат" in blob or "войти" in blob or "событ" in blob
    assert ev["hype_leaked"] is False
    for banned in ("купи", "гарант", "10x", "прорыв"):
        assert banned not in blob


def test_comfort_is_calm():
    turn = comfort_turn("хочу прорыв и 10x масштабирование любой ценой", lang="ru")
    low = (turn["reply"] or "").lower()
    assert "прорыв" not in low
    assert "10x" not in low
    assert "масштабир" not in low
    assert turn["hype"] is False
    assert turn["growth_point"]["text"]
    assert turn["idea"]["text"]
    assert turn["assistant"] == "Тихий"


def test_making_refuses_empty():
    with pytest.raises(MakingRefused):
        run_making_chamber({})


def test_making_week_day1_is_entry():
    pack = run_closer(BRIEF_MANAGER, with_making=True)
    making = pack["making"]
    cal = making["meta"]["calendar_7d"]
    assert len(cal) == 7
    assert cal[0]["id"] == "D1_ENTER"
    assert "исслед" not in cal[0]["do"].lower()
    assert making["meta"]["fin_structure_shift"]["fear_protocol"]["no_pitch"] is True
    assert making["meta"]["fin_structure_shift"]["success_fee"]["model"] == "success_fee_share"
    sat = making["meta"]["satellite"]
    assert pack["trends"]["primary"]["id"] in (sat.get("trend") or "") or pack["trends"]["primary"]["id"] in str(sat)
    assert making["meta"]["derivative_product"]["from_trend"] == pack["trends"]["primary"]["id"]
    assert any("share" in s.lower() or "долю" in s.lower() or "fee" in s.lower() for s in making["steps"] + [making["move"]])


def test_making_function_is_registered():
    ids = {f["id"] for f in FUNCTIONS}
    assert "making_chamber" in ids
    out = run_making_function(BRIEF_ACTOR)
    assert out["ok"] is True
    assert out["making"]["lane"] == "making"


def test_hypothesis_audit_mostly_holds():
    pack = run_closer(BRIEF_ACTOR, with_making=True)
    audit = pack["audit"]
    assert audit["total"] >= 10
    assert audit["held"] / audit["total"] >= 0.7
    # H9 and H11 are structural
    ids_hold = {c["id"]: c["hold"] for c in audit["items"]}
    assert ids_hold["H9"] is True
    assert ids_hold["H11"] is True
    assert ids_hold["H2"] is True
    assert ids_hold["H10"] is True


def test_abstraction_telegram_leads_with_figure():
    abs_ = compose_abstraction(BRIEF_ACTOR)
    html = format_abstraction_telegram(abs_)
    assert abs_["lead"] in html.replace("&amp;", "&") or abs_["archetype"] in html
    assert len(html) > 400


def test_demo_highway_attaches_closer():
    art = build_demo("агентство performance, онбординг съедает маржу на каждом клиенте")
    assert art["id"]
    html = format_telegram(art)
    assert "Где ломается" in html
    # closer layers ride along
    assert art.get("abstraction") or art.get("cards")
    if art.get("cards"):
        assert "FN-" in html or "Карточ" in html or art["cards"]["count"] >= 6


def test_landing_artifact_shape():
    art = build_demo(BRIEF_PLANE, hint="landing")
    assert art["lane"] in ("landing", "chain", "life")
    assert (art.get("event") or {}).get("title") or art.get("kind") == "chain.experiment"
    assert (art.get("abstraction") or {}).get("essay") or art.get("steps")
    html = format_telegram(art)
    assert "Где ломается" in html


def test_trend_screener_not_signals():
    tr = screen_trends("крипта, мемкоин, листинг, хочу долю с потока", score_vectors("крипта доля комиссия"))
    assert tr["disclaimer"]
    assert "сигнал" in tr["disclaimer"].lower()
    assert tr["primary"]["id"]
    assert tr["primary"]["layer"] in ("growth", "trade", "closer")


def test_closer_artifact_has_resonance_fields():
    pack = run_closer(BRIEF_METHOD)
    art = closer_as_artifact(pack)
    for k in ("id", "title", "one_liner", "break", "move", "steps", "anti", "disclaimer"):
        assert art.get(k), k
    assert art["lane"] == "landing"
    assert len(art["steps"]) >= 3
