"""TYPE_A packs and AI-ops. No Metrix platform in prompts."""

from __future__ import annotations

from backend.core.freelance_packs import attach_pack, apply_order_type_to_ideas
from backend.core.freelance_packs.type_a_programs import PACKS, select_type_a_pack
from backend.core.freelance_packs.ai_ops.packs import AI_OPS, select_ai_ops
from backend.core.coop import run_coop_lane


def test_six_type_a_packs():
    for key in ("A1", "A2", "A3", "A4", "A5", "A6"):
        p = PACKS[key]
        assert p["id"]
        assert p["prompt"]
        assert p["acceptance"]
        assert "Metrix платформ" not in p["prompt"]
        assert len(p["prompt"].splitlines()) <= 40


def test_select_inbox():
    p = select_type_a_pack("заявки из трёх чатов в один список")
    assert p["id"] == "lead_inbox"


def test_ai_ops_no_sell_first():
    blob = " ".join(
        (p.get("rule") or "") + " " + (p.get("prompt") or "") + " " + (p.get("anti") or "")
        for p in AI_OPS.values()
    ).lower()
    assert "не продаёт первым" in blob or "не отправлять клиенту" in blob
    assert "продающее первым" in blob or "человек отправляет" in blob


def test_attach_pack_type_a():
    lane = run_coop_lane("Собери контур заявок в таблицу и отчёт понедельника с хозяином")
    lane = attach_pack(lane, "Собери контур заявок в таблицу и отчёт понедельника с хозяином")
    assert lane["pack"]["id"]
    assert lane["support"]["kind"] == "stabilize"


def test_filter_marketplace_ideas():
    ideas = [
        {"role": "marketplace_lattice", "title": "PragmaVault marketplace"},
        {"role": "consultation", "title": "Контур заявок"},
        {"role": "solution_bridge", "title": "Один список"},
    ]
    kept = apply_order_type_to_ideas(ideas, {"order_type": "TYPE_A", "advanced_only": False})
    assert all(i["role"] != "marketplace_lattice" for i in kept)
    assert len(kept) <= 3
