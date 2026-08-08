"""Funding pack · 3 pillars + API shape."""

from __future__ import annotations

from backend.core.business_gen.funding_pack import build_funding_pack
from backend.monetization.structural_income import StructuralIncomeEngine
from backend.monetization.asset_attach import AssetAttachEngine
from backend.monetization.capital_coop import CapitalCoopEngine


BRIEF = (
    "AI agency ops core: sell orientation and pilots for cloud FinOps. "
    "Have unit margin notes, one pilot case, 25k USD capital for distribution. "
    "Want rental slots and partner scoreboard."
)


def test_structural_income_levers():
    out = StructuralIncomeEngine().build(BRIEF, project_name="Ops Core", lang="en")
    assert out["pillar"] == 1
    assert out["instant_levers"]
    assert out["income_band"]["monthly_structural_mid"] > 0
    assert "setup_steps" in out


def test_asset_attach_modes():
    out = AssetAttachEngine().build(BRIEF, preferred_mode="hybrid", lang="en")
    assert out["pillar"] == 2
    assert out["attachments"]
    assert out["mode"] in ("hybrid", "rental", "percent", "auto")
    assert "playbook" in out


def test_capital_coop_slots():
    out = CapitalCoopEngine().build(
        BRIEF, capital_usd=25_000, partner_role="hybrid", lang="en"
    )
    assert out["pillar"] == 3
    assert len(out["placement_slots"]) == 3
    assert out["readiness"]["gate"] in (
        "structure_first",
        "build_evidence",
        "partner_ready",
    )
    total = sum(s["usd"] for s in out["placement_slots"])
    assert abs(total - 25_000) < 1.0


def test_funding_pack_full():
    pack = build_funding_pack(
        BRIEF,
        project_name="Ops Core",
        capital_usd=25_000,
        lang="en",
    )
    assert pack["module"] == "FundingPack"
    assert len(pack["pillars"]) == 3
    assert pack["launch_path"]
    assert pack["paid_quickstart"]["steps"]
    assert pack["raw"]["structural"]
    assert pack["raw"]["assets"]
    assert pack["raw"]["capital_coop"]


def test_funding_pack_ru():
    pack = build_funding_pack(
        "Агентство: консультации и пилоты, капитал 10k, маржа unit, kill rules",
        project_name="Агентство",
        lang="ru",
    )
    assert "столп" in pack["summary"].lower() or "Funding" in pack["summary"] or "·" in pack["summary"]
    assert pack["pillars"][0]["title"]


def test_api_funding_route():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    res = client.post(
        "/api/v1/analytics/funding-pack",
        json={
            "business": BRIEF,
            "project_name": "Ops Core",
            "capital_usd": 10000,
            "lang": "en",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["module"] == "FundingPack"
    assert data["output"]["pillars"]
    assert data["paid_quickstart"]

