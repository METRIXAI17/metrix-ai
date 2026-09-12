from backend.core.a2a_screener import steer
from backend.core.ai_mgmt import pack as ai_mgmt_pack
from backend.core.complexity_boundary import lattice, think_more
from backend.core.craftshift_x import run as craftshift_run
from backend.core.door import load, mint, public_view
from backend.core.seven_lines import run_line
from backend.core.store_catalog import catalog_payload, category_by_id
from backend.core.terminal_ai import place
from telegram_app.menu import menu_action


def test_door_roundtrip():
    rec = mint("касса в тумане", room="talk")
    assert rec["code"] and len(rec["code"]) == 6
    got = load(rec["code"])
    assert got and got["brief"]
    view = public_view(got)
    assert view["ok"] is True


def test_lattice_then_think_more_kills_combinations():
    brief = "саморазвитие, тыл, операционка, хватает ли денег, кризис фрагментации чипов FPGA"
    a = lattice(brief)
    assert a["depth"] >= 3
    assert a["table"]
    b = think_more(brief, a)
    assert b["remaining"] <= a["remaining"]
    assert b["think_more"] == 1


def test_store_seven_rooms():
    cats = catalog_payload()["categories"]
    assert len(cats) == 7
    assert cats[0]["id"] == "a2a"
    assert cats[6]["id"] == "placements"
    assert category_by_id("7")["id"] == "placements"


def test_line_objects_without_engine():
    brief = "нужно посадить агента в поток оплаты пилота и резать эссе скринером"
    a1 = run_line(1, brief, with_engine=False)
    assert a1["line"] == 1
    assert a1.get("screener") or a1.get("lattice")
    a7 = run_line(7, brief, with_engine=False)
    assert a7["line"] == 7
    assert a7.get("seat")
    assert a7.get("ai_mgmt")
    cs = craftshift_run(brief)
    assert "CraftShift" in (cs.get("promo_line") or "") or "производного" in (cs.get("promo_line") or "")
    assert cs.get("post")
    assert cs.get("video_prompt")
    mg = ai_mgmt_pack(brief)
    assert len(mg["artefacts"]) == 4
    t = place(brief)
    assert t["line"] == 7


def test_menu_store_and_legacy():
    assert menu_action("Стор") == "store"
    assert menu_action("CraftShift") == "shift"
    assert menu_action("Разговор") == "life"
    assert menu_action("Идеи для жизни") == "life"
    assert menu_action("Торговые боты") == "bots"
    assert menu_action("/store") == "store"
    assert menu_action("/shift") == "shift"


def test_a2a_screener_flags_essay():
    art = steer("Intent-Driven Hardware Orchestrator middleware SaaS fee $10,000 platform")
    leaks = [x["id"] for x in art["screener"]["leaks"]]
    assert "essay" in leaks or "price_fantasy" in leaks
