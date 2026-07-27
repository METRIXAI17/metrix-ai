"""Tangibility gates for paid Consult + Tech Write deliverable."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.request_pipeline import process_client_request
from backend.paid.narrative.package_deliverable import (
    ConsultationSynthesizer,
    PackageDeliverableWriter,
)

ANNA = {
    "industry": "ai-agencies",
    "business": (
        "Boutique AI agency for mid-market ops teams. Utilization 55%, rework 22%, "
        "gross margin 32%. Clients get free discovery then scope explodes. "
        "Retainers dilute delivery. Need ops efficiency and something clients pay for "
        "without free discovery chaos."
    ),
    "name": "Anna Kovaleva",
    "contact": "@anna",
    "success_metrics": {
        "business_numbers": {
            "utilization": 0.55,
            "rework": 0.22,
            "gross_margin": 0.32,
            "monthly_revenue": 48000,
            "cycle_days": 18,
        }
    },
}

DMITRY = {
    "industry": "cloud-economy",
    "business": (
        "Founder studio building creative tools. We burn OpenAI and Anthropic tokens "
        "on every custom operation. API bill grew 3x while quality of replies stayed flat. "
        "Need to cut third-party API spend without killing creative quality."
    ),
    "name": "Dmitry Orlov",
    "success_metrics": {
        "business_numbers": {
            "monthly_revenue": 22000,
            "gross_margin": 0.28,
            "utilization": 0.48,
        }
    },
}


def _load_result_md(res: dict) -> str:
    pc = res["meta"]["paid_product_core"]
    pkg = pc.get("package_deliverable") or {}
    path = (pkg.get("package_result") or {}).get("markdown") or pkg.get("primary")
    if path and str(path).endswith(".html"):
        path = str(path).replace("YOUR_RESULT.html", "YOUR_RESULT.md")
    assert path and Path(path).exists(), pkg
    return Path(path).read_text(encoding="utf-8")


def test_anna_tangibility_ready():
    res = process_client_request(ANNA)
    assert res["ok"]
    pkg = res["meta"]["paid_product_core"]["package_deliverable"]
    tang = pkg.get("tangibility") or {}
    assert tang.get("score", 0) >= 0.8, tang
    assert tang.get("ready_for_paid_send") is True, tang

    md = _load_result_md(res)
    # Unique / grounded
    assert "Anna" in md
    assert "55%" in md or "0.55" in md
    assert "rework" in md.lower()
    assert "free discovery" in md.lower()
    assert "48,000" in md or "48000" in md or "$48" in md
    # Not the old shame
    assert "размыт" not in md
    assert "hub actor" not in md.lower()
    assert "What you got today" not in md or "What you actually received" in md
    # Diagnosis not duplicated as same block
    assert md.count("this is the diagnosis for *this* brief") <= 1
    # Mechanism + pilot + short notes (client pack; tech WP lives in TECH_SPEC)
    assert "Change mechanism" in md or "mechanism" in md.lower()
    assert "Short notes" in md or "next steps" in md.lower()
    assert "Recommended pilot" in md or "pilot" in md.lower()
    assert "1290" not in md
    assert "Solution Bridge" not in md
    tech_path = Path(
        res["meta"]["paid_product_core"]["package_deliverable"]["tech_write"]["markdown"]
    )
    tech = tech_path.read_text(encoding="utf-8")
    assert "WP1" in tech or "Work package" in tech


def test_dmitry_different_mechanism_from_anna():
    a = process_client_request(ANNA)
    d = process_client_request(DMITRY)
    ma = (a["meta"]["paid_product_core"]["package_deliverable"].get("summary") or "")
    md_a = _load_result_md(a)
    md_d = _load_result_md(d)
    # Different mechanisms / products
    assert "API" in md_d or "api" in md_d.lower() or "token" in md_d.lower()
    assert "Expert" in md_d or "third-party" in md_d.lower() or "API" in md_d
    # Anna pack should talk free discovery; Dmitry should not be copy-paste of Anna diagnosis
    assert "free discovery" in md_a.lower()
    # Documents must not be nearly identical
    ratio = len(set(md_a.split()) & set(md_d.split())) / max(1, len(set(md_a.split())))
    assert ratio < 0.75, f"packs too similar overlap={ratio:.2f}"


def test_synth_no_duplicate_diagnosis_block():
    synth = ConsultationSynthesizer()
    doc = synth.synthesize(
        industry_id="ai-agencies",
        business=ANNA["business"],
        idea_title="Solution Bridge for boutique agency",
        client_name="Anna Kovaleva",
        nums={
            "utilization": 0.55,
            "rework": 0.22,
            "gross_margin": 0.32,
            "monthly_revenue": 48000,
            "cycle_days": 18,
        },
        paid={
            "paid_score": 0.7,
            "package": {
                "status": "ready",
                "top_lever": "model_fit",
                "paid_readiness": 0.6,
                "founder_error_suspected": False,
            },
            "situation_metrics": {"numbers_coverage": 0.8},
            "function_engine": {"top_lever": "model_fit"},
        },
        memo_convert={
            "analog_engine": {
                "function_meta": {
                    "title": "Buyer financial-model proof",
                    "out": "terminal_teammate_sale",
                }
            }
        },
        market_unit={
            "product": {
                "name": "Terminal Teammate",
                "one_liner": "Teammate console that raises ops efficiency without agent chaos",
            },
            "offers": [],
        },
        demo_idea={
            "title": "Solution Bridge for boutique agency",
            "deliverables_seed": ["Orient→SKU map", "Pick list", "Handoff"],
        },
        demo_ideas=[
            {"title": "Terminal Teammate for agency ops efficiency", "role": "product"},
            {"title": "Buyer financial model for Teammate", "role": "models"},
        ],
        oae={
            "reduced_to_request": {
                "primary_idea": "Solution Bridge for boutique agency",
                "double_bottom_flyouts": [
                    "Buyer financial model that proves Terminal Teammate payback",
                    "Terminal Teammate for agency ops efficiency",
                ],
            }
        },
    )
    assert doc["tangibility"]["ready_for_paid_send"] is True, doc["tangibility"]
    assert "free discovery" in doc["diagnosis"].lower()
    assert doc["diagnosis"][:100] not in doc["situation"]
    assert len(doc["tech"]["work_packages"]) >= 3
    assert len(doc["tech"]["acceptance"]) >= 4
    assert "Kill unpaid discovery" in doc["mechanism"]["title"] or "discovery" in doc[
        "mechanism"
    ]["title"].lower()


def test_writer_files_and_qa_json():
    w = PackageDeliverableWriter()
    out = w.write(
        request_id="tangible-qa-run-001",
        industry_id="ai-agencies",
        business=ANNA["business"],
        idea_title="Solution Bridge for boutique agency",
        client_name="Anna Kovaleva",
        paid={
            "paid_score": 0.72,
            "package": {
                "status": "ready",
                "top_lever": "model_fit",
                "paid_readiness": 0.62,
            },
            "situation_metrics": {},
            "function_engine": {"top_lever": "model_fit"},
        },
        memo_convert={
            "analog_engine": {
                "function_meta": {"title": "Ops efficiency map", "out": "terminal_teammate_attach"}
            }
        },
        extra_params={
            "utilization": 0.55,
            "rework": 0.22,
            "gross_margin": 0.32,
            "monthly_revenue": 48000,
            "cycle_days": 18,
        },
        demo_idea={"title": "Solution Bridge for boutique agency"},
        demo_ideas=[{"title": "Terminal Teammate for agency ops efficiency"}],
    )
    assert out["tangibility"]["ready_for_paid_send"] is True
    ws = Path(out["workspace"])
    assert (ws / "10_consult_metareality" / "CONSULTATION.md").exists()
    assert (ws / "11_tech_write_specsforge" / "TECH_SPEC.md").exists()
    assert (ws / "12_package_result" / "YOUR_RESULT.md").exists()
    assert (ws / "12_package_result" / "TANGIBILITY_QA.json").exists()
    tech = (ws / "11_tech_write_specsforge" / "TECH_SPEC.md").read_text(encoding="utf-8")
    assert "WP1" in tech or "Work package" in tech
    assert "Acceptance criteria" in tech
    assert "Definition of done" in tech
    assert "scope explodes" in tech.lower() or "free discovery" in tech.lower() or "55%" in tech
