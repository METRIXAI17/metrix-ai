#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Realistic runs through full pipeline + narrative client packs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.request_pipeline import process_client_request

CASES = [
    {
        "industry": "ai-agencies",
        "name": "Anna Kovaleva",
        "contact": "@anna_ops",
        "track": "all",
        "business": (
            "AI agency, 12 people. We build custom GPT agents and RAG bots for mid-market SaaS. "
            "Average delivery 4–8 weeks, senior utilization about 55%, rework after client feedback is high. "
            "Need clearer packaging of orientation-first pilots and pricing levers without burning margin "
            "on free discovery calls."
        ),
        "extra_params": {
            "utilization": 0.55,
            "gross_margin": 0.32,
            "cycle_days": 35,
            "monthly_revenue": 48000,
            "rework_rate": 0.22,
        },
        # fill modeling so must-ask may clear
        "success_metrics": {
            "modeling_answers": {
                "entities": "client SaaS, agency pod, senior builders",
                "flows": "cash from retainers, compute, content drafts",
                "levers": "pricing map, discovery scope, utilization",
                "jobs": "ship working agent packs with clear pilots",
                "metrics": "utilization, gross_margin, cycle_days, rework_rate, monthly_revenue",
            }
        },
    },
    {
        "industry": "cloud-economy",
        "name": "Dmitry Orlov",
        "contact": "dmitry@finops.example",
        "track": "models",
        "business": (
            "Cloud cost consultancy for startups on AWS and GCP. Clients waste 30–40% on idle GPU "
            "and wrong region placement. We want a productized FinOps board with reserved vs on-demand "
            "bands, edge placement advice, and monthly retainer ARPU growth around 2–3k USD."
        ),
        "extra_params": {
            "utilization": 0.48,
            "gross_margin": 0.41,
            "cycle_days": 21,
            "monthly_revenue": 62000,
            "churn": 0.08,
        },
        "success_metrics": {
            "modeling_answers": {
                "entities": "startup client, FinOps analyst, cloud account",
                "flows": "cloud spend, reserved commitments, advisory retainers",
                "levers": "placement, reserved bands, retainer packaging",
                "jobs": "cut idle waste without killing product latency",
                "metrics": "utilization, gross_margin, cycle_days, monthly_revenue, churn",
            }
        },
    },
    {
        "industry": "telecom",
        "name": "Igor Netsky",
        "contact": "@igor_net",
        "track": "promotion",
        "business": (
            "Regional telecom MVNO with B2B SME plans. Churn after month three is painful, ARPU flat. "
            "Want linguistic ops for support scripts, network zone offers, and a pilot to lift retention "
            "without heavy CAPEX. Median delivery of new tariff features is 45 days."
        ),
        "extra_params": {
            "utilization": 0.67,
            "gross_margin": 0.38,
            "cycle_days": 45,
            "ARPU": 18.5,
            "churn": 0.11,
        },
        "success_metrics": {
            "modeling_answers": {
                "entities": "SME subscriber, support desk, MVNO core",
                "flows": "ARPU, churn signals, tariff changes",
                "levers": "support scripts, zone offers, feature cycle",
                "jobs": "keep SME plans sticky without CAPEX spike",
                "metrics": "ARPU, churn, cycle_days, gross_margin, utilization",
            }
        },
    },
]


def extract(out: dict) -> dict:
    paid = (out.get("meta") or {}).get("paid_product_core") or {}
    comm = paid.get("commercial") or {}
    narr = paid.get("narrative_engine") or comm.get("narrative_engine") or {}
    memo = narr.get("memo") or {}
    q = narr.get("quality") or {}
    pack = comm.get("client_pack") or paid.get("client_pack") or {}
    ui = paid.get("ui_status") or comm.get("ui_status") or {}
    offer = comm.get("commercial_offer") or {}
    return {
        "ok": out.get("ok"),
        "request_id": out.get("request_id"),
        "industry": out.get("industry"),
        "idea_title": (out.get("demo_idea") or {}).get("title"),
        "paid_score": paid.get("paid_score"),
        "paid_status": paid.get("status"),
        "ui_status": ui.get("label") if isinstance(ui, dict) else ui,
        "sellable": ui.get("sellable") if isinstance(ui, dict) else None,
        "must_ask": (comm.get("must_ask") or {}).get("must_count"),
        "block_rerun": (comm.get("must_ask") or {}).get("block_rerun"),
        "tariff": (offer.get("tariff") or {}).get("name"),
        "tariff_usd": (offer.get("tariff") or {}).get("price_usd"),
        "exec_summary": (memo.get("executive_summary") or "")[:400],
        "template_index": q.get("template_index"),
        "anchor_rate": q.get("client_anchor_rate"),
        "consistency": q.get("consistency_score"),
        "anticlone_pass": q.get("anticlone_pass"),
        "values": [v.get("label") for v in (narr.get("values") or {}).get("values_present") or []][:6],
        "products": [
            f"{p.get('name')} ${p.get('price_usd')}"
            for p in (narr.get("product_templates") or [])[:4]
        ],
        "client_pack_html": pack.get("html"),
        "client_pack_url": pack.get("url"),
        "portal": (comm.get("portal") or {}).get("url"),
        "generic_geometry": "Oriented to your geometry"
        in (memo.get("executive_summary") or ""),
    }


def main() -> int:
    rows = []
    for i, case in enumerate(CASES, 1):
        print(f"[{i}/{len(CASES)}] {case['industry']} …", flush=True)
        out = process_client_request(case)
        row = {"case": i, "client": case["name"], **extract(out)}
        rows.append(row)
        print(
            f"  score={row['paid_score']} ui={row['ui_status']} "
            f"cons={row['consistency']} pack={bool(row['client_pack_html'])}",
            flush=True,
        )
        if row.get("exec_summary"):
            print(f"  memo: {row['exec_summary'][:160]}…", flush=True)

    path = ROOT / "docs" / "NARRATIVE_REALISTIC_RUNS.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Narrative realistic runs",
        "",
        f"Cases: {len(rows)}",
        "",
        "| # | Industry | Score | UI | Consistency | Anchor | Pack | Tariff |",
        "|---|----------|------:|----|------------:|-------:|:----:|--------|",
    ]
    for r in rows:
        md.append(
            f"| {r['case']} | {r.get('industry')} | {r.get('paid_score')} | "
            f"{r.get('ui_status')} | {r.get('consistency')} | {r.get('anchor_rate')} | "
            f"{'yes' if r.get('client_pack_html') else 'no'} | "
            f"${r.get('tariff_usd')} |"
        )
    md += ["", "## Executive summaries", ""]
    for r in rows:
        md += [
            f"### {r['client']} ({r.get('industry')})",
            "",
            r.get("exec_summary") or "—",
            "",
            f"Values: {', '.join(r.get('values') or [])}",
            "",
            f"Products: {', '.join(r.get('products') or [])}",
            "",
            f"Pack: `{r.get('client_pack_html')}`",
            "",
        ]
    md_path = ROOT / "docs" / "NARRATIVE_REALISTIC_RUNS.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print("Wrote", path)
    print("Wrote", md_path)
    return 0 if all(r.get("ok") for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
