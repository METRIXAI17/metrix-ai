"""Four rooms, free store/hits, Flagship intake, overlay eval, $100 no file."""

from __future__ import annotations

from backend.core.access import FREE_FEATURES, PAID_FEATURES, consume
from backend.core.code_overlay import build_overlay, inspect_overlay
from backend.core.design_contour import analyze
from backend.core.flagship_engine import start
from backend.core.life_intake import intake
from backend.core.pricing_lanes import PUBLIC_TABS, SKUS, tariff_board
from backend.core.product_eval import THRESHOLD, run_suite
from backend.core.product_file import generate_paid_file
from backend.core.workflow_turnaround import turnaround
from telegram_app.menu import menu_action
from telegram_app.bot import main_keyboard, nav_inline, webapp_open


def test_four_tabs_order():
    ids = [t["id"] for t in PUBLIC_TABS]
    assert ids == ["hits", "flagship", "store", "tariffs"]


def test_bot_keyboard_four_rooms():
    labels = [c["text"] for row in main_keyboard()["keyboard"] for c in row]
    assert labels == ["Консультации", "Приватка", "Боты и ядра", "Профиль"]
    assert menu_action("Флагман") == "consult"
    assert menu_action("Консультации") == "consult"
    assert menu_action("Профиль") == "profile"
    nav = str(nav_inline("https://example.test/tg/"))
    assert "m:consult" in nav
    assert "m:private" in nav
    assert "m:work" in nav
    assert "m:profile" in nav
    assert "v=t6" in webapp_open("https://example.test/tg/", "consult")


def test_hits_and_store_never_debit():
    assert "store" in FREE_FEATURES
    assert "hits" in FREE_FEATURES
    assert "store" not in PAID_FEATURES
    g = consume(None, "store")
    assert g.get("allowed") is True
    assert g.get("debited") is False
    h = consume(None, "life_intake")
    assert h.get("allowed") is True


def test_tariffs_copy_names_free_facts():
    board = tariff_board("ru")
    assert "бесплатно" in board["free_facts"].lower()
    ids = [p["id"] for p in board["paid"]]
    assert ids == ["sku_100", "sku_490", "sku_1000", "sku_10000"]
    assert SKUS["sku_100"]["file"] is False
    assert SKUS["sku_490"]["file"] is True
    assert SKUS["sku_10000"]["usd"] == 10000


def test_intake_phrases_questions_ticker_chain():
    pack = intake("Касса как туман, понедельник пустой.\nНужен хозяин.", lang="ru")
    assert 8 <= len(pack["problem"]) <= 160
    assert 8 <= len(pack["solution"]) <= 180
    assert 5 <= pack["question_count"] <= 10
    assert pack["ticker"].startswith("MX-")
    assert pack["chain_id"] == pack["ticker"]
    assert pack["eval"]["score"] <= 0.93
    from backend.core.life_intake import format_telegram

    tg = format_telegram(pack)
    assert "Eval:" not in tg
    assert pack.get("eval_visible") is False
    ids = {c["id"] for c in pack["skus"]["cards"]}
    assert {"sku_100", "sku_490", "sku_1000"} <= ids


def test_overlay_parses_and_recurses():
    ov = build_overlay(
        ticker="MX-TEST1",
        problem="касса без хозяина",
        solution="посадить слот с цифрой понедельника",
        lang="ru",
    )
    q = inspect_overlay(ov["source"], ticker="MX-TEST1")
    assert q["go"] is True
    assert q["score"] >= THRESHOLD
    assert "recurse" in q["reasons"]
    assert "TODO" not in ov["source"]


def test_sku_100_is_custom_spec_not_overlay():
    pack = intake("Мелкие задачи, 120 запросов без файла.", lang="ru")
    paid = generate_paid_file(pack["ticker"], sku_id="sku_100")
    assert paid.get("kind") == "custom_spec"
    assert paid.get("file") is True
    assert len(paid.get("specs") or []) >= 4
    assert len(paid.get("variants") or []) >= 3
    assert "class Overlay" not in (paid.get("source") or "")
    assert SKUS["sku_100"]["file"] is False
    assert SKUS["sku_100"].get("custom_spec") is True


def test_paid_file_for_490():
    pack = intake("Касса пустая.\nСлот с именем.", lang="ru")
    paid = generate_paid_file(pack["ticker"], sku_id="sku_490")
    assert paid.get("ok") is True
    assert paid.get("file") is True
    assert (paid.get("quality") or {}).get("go") is True
    src = paid.get("source") or ""
    assert "class Overlay" in src
    assert "def recurse" in src


def test_design_contour_is_not_yield_pitch():
    pack = analyze("Нужен автономный контур в наш проект за 10k", lang="ru")
    blob = (pack.get("lead") or "") + (pack.get("kill") or "")
    assert "линейк" in blob.lower() or "контур" in blob.lower()
    assert "авто-доход" in (pack.get("kill") or "")
    assert len(pack.get("questions") or []) >= 10
    assert pack["sku"] == "sku_10000"


def test_workflow_turnaround_free():
    wf = turnaround(lang="ru", contour=True)
    assert wf["free"] is True
    assert len(wf["steps"]) == 5
    assert "цепочка" not in " ".join(s.get("do") or "" for s in wf["steps"]).lower()


def test_flagship_start_from_brief():
    pack = start("SaaS 80 человек, фичи пилим, никто не знает победу", lang="ru")
    assert pack.get("ticker")
    assert pack.get("problem")


def test_sacrifice_sits_in_web3_at_normal_questions():
    from backend.core.business_gen.client_segmentation import segment_client
    from backend.core.life_intake import question_system_state

    state = question_system_state()
    assert state["operating_level"] == "normal"
    assert state["max_level"] == "max"
    brief = (
        "Жертвенность: отдаю своё и не называю границу.\n"
        "Это должно сесть в web3, не в бизнес для чужих клиентов."
    )
    pack = intake(brief, lang="ru", section="flagship")
    assert pack["cycle_section"] == "web3"
    assert pack["section_fix"]
    assert pack["question_level"] == "normal"
    assert pack["frame"] == "web3_order"
    assert pack["eternal_b2b"] is False
    assert "Жертвенность" in pack["problem"]
    assert "web3" in pack["solution"].lower()
    assert len(pack["variants"]) >= 4
    assert all(q.get("level") == "normal" for q in pack["questions"])
    seg = segment_client(brief, lang="ru")
    assert seg["primary"]["id"] == "web3_order"
    assert seg["eternal_b2b"] is False
    b2b = segment_client(
        "Online architecture design library for IT product builders with niche cards for B2B studios.",
        lang="ru",
    )
    assert b2b["eternal_b2b"] is True
    assert b2b["primary"]["id"] in ("b2b_knowledge", "b2b_product", "agency")


def test_product_eval_suite_normal_level():
    suite = run_suite()
    assert suite["mean"] >= THRESHOLD
    assert suite["go"] is True
    assert suite["hard_fail"] == []
