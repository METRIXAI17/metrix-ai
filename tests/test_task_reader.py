"""Task reader, assembly, auto-mode, linguistic spaces, Mini App surfaces."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.functions import run_creative_assistant, run_digital_mockup, run_solution_logger
from backend.core.miniapp_catalog import catalog_payload
from backend.core.order_terminal import mine_orders
from backend.core.promo_lite import run_promo_lite
from backend.core.task_reader import assemble_query, read_task, unfold_linguistic_spaces
from backend.monetization.tg_scheme import scheme_payload


BRIEF = (
    "Нужно собрать систему работы по сложному запросу для соло-эксперта: "
    "карточки, промо для роликов и путь к ордерам, но цифры пока не называю, "
    "просто как бы развернём и потом разберёмся."
)


def test_reader_keeps_several_end_states():
    out = read_task(BRIEF, lang="ru")
    assert len(out["variants"]) >= 6
    assert len(out["selected_end_states"]) >= 3
    ids = {e["id"] for e in out["selected_end_states"]}
    assert "gen_territory" in ids or any(v["reader_id"] == "generative" for v in out["variants"])
    assert out["disagreement"] >= 0
    assert "single_reading" not in (out["bias_audit"]["failed"] or [])


def test_unbiased_bias_audit_exists():
    out = read_task(BRIEF, lang="ru")
    checks = out["bias_audit"]["checks"]
    for key in ("recency", "authority", "confirmation", "gap_filling", "sku_first"):
        assert key in checks


def test_linguistic_concealment_and_unnamed():
    ling = unfold_linguistic_spaces(BRIEF, lang="ru").to_dict()
    assert ling["concealment"]["score"] > 0.2
    assert ling["concealment"]["hedges"] or ling["concealment"]["flags"]
    assert ling["unnamed_phenomena"]
    assert len(ling["spaces"]) >= 8


def test_assembler_three_sides_and_auto_mode():
    packed = assemble_query(BRIEF, lang="ru")
    sides = packed["three_sides"]
    assert set(sides) == {"product", "linguistic", "monetization"}
    mode = packed["mode"]
    assert mode["surface_mode"]
    assert mode["metrix_mode"]
    assert packed["files"]
    assert packed["end_readings"]


def test_mode_promo_and_logger():
    promo = assemble_query(
        "Сделай промо: карточки описаний и идеи для роликов про консалтинг-промпты",
        lang="ru",
    )
    assert promo["mode"]["surface_mode"] == "promo_lite"
    log = assemble_query(
        "Разбор моего трейдинга: журнал сделок, ошибки FOMO, путь к ордерам",
        lang="ru",
    )
    assert log["mode"]["surface_mode"] in ("solution_logger", "terminal_liquidity")


def test_functions_and_terminal():
    c = run_creative_assistant("ограничение: 12 секунд, один предмет, без лица", lang="ru")
    assert c["ideas"] and c["prompts"]
    L = run_solution_logger(thesis="Вход вдогонку за импульсом без инвалидации", result="loss")
    assert "chase_after_move" in L["error_families"]
    m = run_digital_mockup("Я консультант, работаю в телеграме сессиями, пакеты клиентам")
    assert m["likeness"]["channel"] == "telegram"
    t = mine_orders("Майнинг ордеров из повторяемого тезиса на ликвидность карточек")
    assert t["tickets"]
    assert t["viability"]["verdict"]


def test_catalog_and_scheme():
    cat = catalog_payload("ru")
    titles = [f["title"] for f in cat["flagships"]]
    assert any("Работа по запросу" in (t or "") or f.get("section") == "работа по запросу" for f, t in zip(cat["flagships"], titles))
    assert len(cat["functions"]) == 3
    assert cat["nav"][1]["title"] == "Работа по запросу"
    assert cat["nav"][2]["title"] == "Флагманские карточки"
    sch = scheme_payload()
    assert sch["rails"]["rf_cards"]["possible"] is True
    assert sch["unit_90d_conservative"]["gmv_rub"] > 0


def test_promo_lite_kinds():
    out = run_promo_lite("Metrix AI соло-консалтинг", kind="cards")
    assert out["items"]
