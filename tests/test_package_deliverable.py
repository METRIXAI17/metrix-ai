"""Consult + Tech Write package deliverable + workspace folders."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.request_pipeline import process_client_request
from backend.paid.narrative.package_deliverable import PackageDeliverableWriter


def test_package_writer_folders(tmp_path, monkeypatch):
    # Use real WORKSPACE under project — writer uses WORKSPACE_ROOT
    writer = PackageDeliverableWriter()
    out = writer.write(
        request_id="test-package-deliverable-001",
        industry_id="ai-agencies",
        business=(
            "Boutique AI agency for mid-market ops teams. Utilization 55%, rework 22%, "
            "gross margin 32%. We need ops efficiency and a teammate clients will buy."
        ),
        idea_title="Terminal Teammate for agency ops efficiency",
        narrative={
            "memo": {
                "title": "Test",
                "executive_summary": "Clean summary for the client.",
                "sections": [],
            },
            "product_templates": [
                {"name": "Consult + Tech Write", "price_usd": 1290, "recommend_score": 0.9}
            ],
            "quality": {"client_anchor_rate": 1.0, "anticlone_pass": True},
        },
        commercial={
            "commercial_offer": {
                "tariff": {"name": "Consult + Tech Write", "price_usd": 1290}
            }
        },
        paid={"status": "packageable", "paid_score": 0.82, "package": {"top_lever": "impact"}},
        memo_convert={
            "analog_engine": {
                "selected_function": "ops_efficiency_map",
                "function_meta": {
                    "title": "Operational efficiency map",
                    "out": "terminal_teammate_attach",
                },
            },
            "technical_tasks": [
                {
                    "acceptance": [
                        "Function named",
                        "Specs handoff ready",
                    ]
                }
            ],
            "open_opportunities": [
                {"title": "Ops efficiency → Terminal Teammate", "coop_score": 0.72}
            ],
            "personalization": {"tone": "operator", "process_cycle": "tight_3_step"},
        },
        client_name="Anna",
        extra_params={
            "utilization": 0.55,
            "rework": 0.22,
            "gross_margin": 0.32,
            "monthly_revenue": 48000,
        },
    )
    assert "package_result" in out
    result_html = Path(out["package_result"]["html"])
    assert result_html.exists()
    text = result_html.read_text(encoding="utf-8")
    assert "Terminal Teammate" in text or "ops" in text.lower()
    assert (
        "What you actually received" in text
        or "actually received" in text.lower()
        or "Change mechanism" in text
        or "Diagnosis" in text
    )
    assert "Job-to-be-done" not in text
    assert "размыт" not in text
    assert "hub actor" not in text.lower()

    ws = Path(out["workspace"])
    assert (ws / "10_consult_metareality" / "CONSULTATION.html").exists()
    assert (ws / "11_tech_write_specsforge" / "TECH_SPEC.html").exists()
    assert (ws / "12_package_result" / "YOUR_RESULT.html").exists()
    assert (ws / "README_CLIENT.md").exists()


def test_pipeline_writes_package_result():
    res = process_client_request(
        {
            "industry": "ai-agencies",
            "business": (
                "We run an AI agency for mid-market ops with 55% utilization, "
                "22% rework, and need operational efficiency with Terminal Teammate"
            ),
            "name": "Anna",
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
    )
    assert res["ok"]
    pkg = (res.get("meta") or {}).get("paid_product_core", {}).get(
        "package_deliverable"
    ) or (res.get("meta") or {}).get("paid_product_core", {}).get("commercial", {})
    # commercial nests package_deliverable
    commercial = (res.get("meta") or {}).get("paid_product_core", {})
    package = commercial.get("package_deliverable") or {}
    if not package:
        # may be on commercial key
        package = (commercial.get("commercial") or {}).get("package_deliverable") or {}
    # After our pipeline merge, package_deliverable is on paid_out top level
    package = commercial.get("package_deliverable") or package
    assert package, f"missing package_deliverable in {list(commercial.keys())[:20]}"
    html_path = package.get("primary") or (package.get("package_result") or {}).get("html")
    assert html_path and Path(html_path).exists()
    body = Path(html_path).read_text(encoding="utf-8")
    assert "Anna" in body or "Your result" in body or "result" in body.lower()
    assert "размыт" not in body
    assert "hub actor" not in body.lower()
