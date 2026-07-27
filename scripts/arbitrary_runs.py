#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arbitrary realistic process runs → docs/ARBITRARY_RUNS_REPORT.json + .md"""

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
        "success_metrics": {
            "priority": ["iroi", "impact", "clarity"],
            "targets": {"iroi": 0.6, "clarity": 0.65},
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
    },
    {
        "industry": "cost-engineering",
        "name": "Sofia Brand",
        "contact": "sofia@brandpro.example",
        "track": "promotion",
        "business": (
            "Brand and performance studio for DTC. Clients ask for AI content factories but gross margin "
            "collapses when every account is fully staffed. Need productized packages, campaign success "
            "metrics, and an orientation kit freelancers can resell at 1–3k ticket size."
        ),
        "extra_params": {
            "utilization": 0.62,
            "gross_margin": 0.28,
            "cycle_days": 14,
            "monthly_revenue": 39000,
            "rework_rate": 0.18,
        },
    },
    {
        "industry": "chipmaking",
        "name": "Elena Park",
        "contact": "elena@chipforge.example",
        "track": "product",
        "business": (
            "Fabless semiconductor design house for edge AI accelerators. Yield sensitivity and long "
            "verification cycles kill schedule. Need orientation on design-loop metrics, vulnerability "
            "voids in verification, and how to sell semi-custom IP blocks with clearer unit economics."
        ),
        "extra_params": {
            "utilization": 0.71,
            "gross_margin": 0.45,
            "cycle_days": 90,
            "monthly_revenue": 210000,
            "rework_rate": 0.15,
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
    },
    {
        "industry": "device-assembly",
        "name": "Kirill Assemble",
        "contact": "kirill@assemble.example",
        "track": "product",
        "business": (
            "Contract manufacturer for IoT devices: SMT line plus enclosure assembly. Cycle time and "
            "rework rate dominate costs. Want a robotics-assisted stages roadmap and how to package "
            "configuration services for small OEM clients with 1–3k ticket size."
        ),
        "extra_params": {
            "utilization": 0.74,
            "gross_margin": 0.22,
            "cycle_days": 12,
            "monthly_revenue": 155000,
            "rework_rate": 0.09,
        },
    },
]


def extract(out: dict) -> dict:
    paid = (out.get("meta") or {}).get("paid_product_core") or {}
    comm = paid.get("commercial") or {}
    offer = comm.get("commercial_offer") or paid.get("commercial_offer") or {}
    tariff = offer.get("tariff") or {}
    idea = out.get("demo_idea") or {}
    ui = paid.get("ui_status") or comm.get("ui_status") or {}
    anti = paid.get("anti_down_sorter") or comm.get("anti_down_sorter") or {}
    seq = paid.get("sequence_assembler") or comm.get("sequence_assembler") or {}
    prin = paid.get("principles_engine") or comm.get("principles_engine") or {}
    cap = paid.get("capital_efficiency") or comm.get("capital_efficiency") or {}
    harness = paid.get("harness_showcase") or comm.get("harness_showcase") or {}
    must = paid.get("must_ask") or comm.get("must_ask") or {}
    sm = paid.get("situation_metrics") or comm.get("situation_metrics") or {}
    pkg = paid.get("package") or {}
    oae = out.get("operational_analytics") or {}
    dec = out.get("decision_core") or {}
    return {
        "ok": out.get("ok"),
        "request_id": out.get("request_id"),
        "industry": out.get("industry"),
        "operating_mode": out.get("operating_mode"),
        "idea_title": idea.get("title") or idea.get("name"),
        "idea_summary": (idea.get("summary") or idea.get("description") or "")[:220],
        "paid_status": paid.get("status") or (out.get("meta") or {}).get("block_18_status"),
        "paid_score": paid.get("paid_score") or (out.get("meta") or {}).get("block_18_score"),
        "ui_status": ui.get("label") if isinstance(ui, dict) else ui,
        "sellable": ui.get("sellable") if isinstance(ui, dict) else None,
        "anti_down_gate": anti.get("gate") if isinstance(anti, dict) else None,
        "anti_down_best": (anti.get("best") or {}).get("rank_label")
        if isinstance(anti, dict)
        else None,
        "plan_code": seq.get("plan_code") if isinstance(seq, dict) else None,
        "plan_key": seq.get("plan_key") if isinstance(seq, dict) else None,
        "meanings_count": prin.get("meanings_count") if isinstance(prin, dict) else None,
        "coherence": prin.get("coherence") if isinstance(prin, dict) else None,
        "top_lever": pkg.get("top_lever")
        or (paid.get("function_engine") or {}).get("top_lever"),
        "situation_score": sm.get("situation_score") if isinstance(sm, dict) else None,
        "top_leak": (sm.get("top_leak") or {}).get("label")
        if isinstance(sm, dict)
        else None,
        "tariff_id": tariff.get("id"),
        "tariff_name": tariff.get("name"),
        "tariff_usd": tariff.get("price_usd"),
        "portal_url": (comm.get("portal") or paid.get("portal") or {}).get("url"),
        "must_ask_count": must.get("must_count")
        if isinstance(must, dict)
        else len(must.get("must_ask") or [])
        if isinstance(must, dict)
        else None,
        "block_rerun": must.get("block_rerun") if isinstance(must, dict) else None,
        "harness_live_score": harness.get("live_score")
        if isinstance(harness, dict)
        else None,
        "harness_hit": ((harness.get("alignment") or {}).get("hit_success"))
        if isinstance(harness, dict)
        else None,
        "savings_C_vs_A_pct": (cap.get("comparisons") or {}).get("savings_C_vs_A_pct")
        if isinstance(cap, dict)
        else None,
        "decision_mode": dec.get("active_mode"),
        "oae_shift": ((oae.get("answer_shift") or {}) if isinstance(oae, dict) else {}),
        "next_steps": (out.get("next_steps") or [])[:4],
        "errors": out.get("errors") or [],
        "zones": out.get("zones_touched") or [],
        "fin_models_count": len(out.get("fin_models") or []),
    }


def main() -> int:
    rows = []
    for i, case in enumerate(CASES, 1):
        print(f"[{i}/{len(CASES)}] {case['industry']} · {case['name']} …", flush=True)
        out = process_client_request(case)
        row = {
            "case": i,
            "client": case["name"],
            "contact": case["contact"],
            "track": case["track"],
            "business_excerpt": case["business"][:160] + "…",
            **extract(out),
        }
        rows.append(row)
        print(
            f"  → ok={row['ok']} score={row['paid_score']} "
            f"ui={row['ui_status']} anti={row['anti_down_gate']} "
            f"${row['tariff_usd']} lever={row['top_lever']}",
            flush=True,
        )

    out_json = ROOT / "docs" / "ARBITRARY_RUNS_REPORT.json"
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown report
    lines = [
        "# Arbitrary Runs Report — Metrix AI",
        "",
        f"**Runs:** {len(rows)} realistic client requests",
        f"**Date:** 2026-07-23",
        "",
        "## Summary table",
        "",
        "| # | Industry | Client | Idea | Paid score | UI | Anti-down | Tariff | Lever | Situation |",
        "|---|----------|--------|------|------------|----|-----------|--------|-------|-----------|",
    ]
    for r in rows:
        idea = (r.get("idea_title") or "—")[:42].replace("|", "/")
        lines.append(
            f"| {r['case']} | `{r.get('industry')}` | {r.get('client')} | {idea} | "
            f"{r.get('paid_score')} | {r.get('ui_status')} | {r.get('anti_down_gate')} | "
            f"${r.get('tariff_usd')} | {r.get('top_lever')} | {r.get('situation_score')} |"
        )
    lines += ["", "## Per-case detail", ""]
    for r in rows:
        lines += [
            f"### Case {r['case']}: {r.get('industry')} — {r.get('client')}",
            "",
            f"- **Request ID:** `{r.get('request_id')}`",
            f"- **Business:** {r.get('business_excerpt')}",
            f"- **Idea:** {r.get('idea_title')}",
            f"- **Summary:** {r.get('idea_summary')}",
            f"- **Paid status / score:** {r.get('paid_status')} / {r.get('paid_score')}",
            f"- **UI status:** {r.get('ui_status')} (sellable={r.get('sellable')})",
            f"- **Anti-down:** {r.get('anti_down_gate')} · best={r.get('anti_down_best')}",
            f"- **Plan:** `{r.get('plan_code')}` ({r.get('plan_key')})",
            f"- **Meanings / coherence:** {r.get('meanings_count')} / {r.get('coherence')}",
            f"- **Top lever / leak:** {r.get('top_lever')} / {r.get('top_leak')}",
            f"- **Situation score:** {r.get('situation_score')}",
            f"- **Tariff:** {r.get('tariff_name')} **${r.get('tariff_usd')}**",
            f"- **Must-ask / block_rerun:** {r.get('must_ask_count')} / {r.get('block_rerun')}",
            f"- **Harness live:** {r.get('harness_live_score')} (hit={r.get('harness_hit')})",
            f"- **Capital save C vs A:** {r.get('savings_C_vs_A_pct')}%",
            f"- **Decision mode:** {r.get('decision_mode')}",
            f"- **Portal:** {r.get('portal_url')}",
            f"- **Next steps:** {'; '.join(r.get('next_steps') or [])}",
            f"- **Zones:** {', '.join(r.get('zones') or [])}",
            f"- **Fin models:** {r.get('fin_models_count')}",
            "",
        ]
    ok_n = sum(1 for r in rows if r.get("ok"))
    lines += [
        "## Aggregate",
        "",
        f"- Successful: **{ok_n}/{len(rows)}**",
        f"- All UI sellable=false (preview discipline): "
        f"**{all(r.get('sellable') is False for r in rows if r.get('ok'))}**",
        f"- Mean paid_score: "
        f"**{sum(float(r.get('paid_score') or 0) for r in rows)/max(1,len(rows)):.3f}**",
        f"- Meanings always: **{rows[0].get('meanings_count') if rows else 'n/a'}**",
        "",
    ]
    md_path = ROOT / "docs" / "ARBITRARY_RUNS_REPORT.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {out_json}")
    print(f"Wrote {md_path}")
    return 0 if ok_n == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
