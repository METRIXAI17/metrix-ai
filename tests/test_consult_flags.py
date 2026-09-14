"""Consult thinking flags P1–P10 and golden briefs."""

from __future__ import annotations

import json
from pathlib import Path

from backend.core.coop import run_coop_lane
from backend.core.coop.consult_patterns.flags import detect_flags, has_flag
from backend.core.output_editor import banned_hits

FIXTURES = Path(__file__).parent / "fixtures" / "briefs.json"


def test_p1_universe():
    flags = detect_flags("игры+edu+видео+чипы+стор соберём супер-платформу")
    assert has_flag(flags, "P1")


def test_p3_surface_bot():
    flags = detect_flags("Сделай бота с кнопками telegram и меню")
    assert has_flag(flags, "P3")


def test_p4_price():
    flags = detect_flags("Конкуренты делают бота за 30к, давайте так же")
    assert has_flag(flags, "P4")


def test_p6_no_number():
    flags = detect_flags("Сделайте автоматизацию заявок без цифр и без хозяина")
    assert has_flag(flags, "P6")


def test_consult_slot_has_abcd():
    out = run_coop_lane("Сделай бота чтобы заявки из телеги не терялись у менеджеров")
    text = out["client_text"]
    assert "A. ДИАГНОЗ" in text or "ДИАГНОЗ" in text
    assert "B. РЕШЕНИЕ" in text or "контур" in text.lower()
    assert out["thinking_flags"]
    assert banned_hits(text) == []


def test_golden_briefs_no_universe():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    for row in data["type_a"] + data["type_b"]:
        lane = run_coop_lane(row["text"])
        text = (lane.get("client_text") or "").lower()
        assert "вселенн" not in text
        assert "локомотив" not in text
        assert "7 направлен" not in text
        assert lane.get("order_type") in ("TYPE_A", "TYPE_B", "MIXED")
        assert isinstance(lane.get("thinking_flags"), list)


def test_p6_blocks_codegen():
    lane = run_coop_lane("Сделай бота, автоматизируй, чтобы не терялись заявки")
    assert has_flag(lane["thinking_flags"], "P6")
    assert lane["handoff"]["allow_codegen"] is False
