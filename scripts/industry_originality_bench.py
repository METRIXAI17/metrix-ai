"""
Run free-consult style packs across industries × variants.
Goals: originality (low cross-brief overlap) + context fill (claims, mechanism, tangibility).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.request_pipeline import process_client_request

# (industry, tag, brief, numbers)
CASES = [
    (
        "ai-agencies",
        "A1",
        "Boutique AI agency for mid-market ops. Free discovery then scope explodes. Retainers dilute delivery. Need ops efficiency.",
        {"utilization": 0.55, "rework": 0.22, "gross_margin": 0.32, "monthly_revenue": 48000, "cycle_days": 18},
    ),
    (
        "ai-agencies",
        "A2",
        "We sell AI content packages for Instagram brands. Revision loops eat margin. Token costs high. Need a productized SKU not hourly chaos and better ads angle.",
        {"gross_margin": 0.28, "monthly_revenue": 31000},
    ),
    (
        "ai-agencies",
        "A3",
        "iPaaS automation agency integrating CRM and support bots. Unscoped integrations create support sink. Want productized attach SKUs for bots.",
        {"utilization": 0.62, "monthly_revenue": 72000},
    ),
    (
        "cloud-economy",
        "C1",
        "Founder creative studio burns OpenAI and Anthropic on every custom job. API bill 3x, quality flat. Cut third-party API cost keep quality.",
        {"monthly_revenue": 22000, "gross_margin": 0.25},
    ),
    (
        "cloud-economy",
        "C2",
        "Cloud FinOps consultancy for startups on AWS. Clients waste 30% on idle GPU and wrong regions. Productized FinOps board needed for leads.",
        {"monthly_revenue": 90000, "churn": 0.04},
    ),
    (
        "cost-engineering",
        "K1",
        "Industrial cost engineer. Fat specs and gold-plated parameters. Need one-page waste map and resellable Void Scanner for clients.",
        {"rework": 0.11, "monthly_revenue": 55000},
    ),
    (
        "cost-engineering",
        "K2",
        "Plant rework cost rising. Tolerance stack-ups unclear. Parameter void scanner for procurement and design teams who buy clarity.",
        {"rework": 0.19, "gross_margin": 0.21},
    ),
    (
        "chipmaking",
        "H1",
        "Design team pre-tapeout. Design-loop voids appear late. NRE vs iteration decisions fuzzy. Yield geometry twin before next gate.",
        {"cycle_days": 45, "monthly_revenue": 200000},
    ),
    (
        "chipmaking",
        "H2",
        "IP block group. DFT late. Need clarity pack not buzzwords for internal semiconductor buyers and promo events.",
        {"cycle_days": 30},
    ),
    (
        "telecom",
        "T1",
        "MVNO SME plans. ARPU flat, churn high. Care cost high. SLA-native SKUs and intent signal for support.",
        {"churn": 0.08, "arpu": 12.5, "monthly_revenue": 150000},
    ),
    (
        "telecom",
        "T2",
        "Carrier partner channel. Tariff launches confuse partners. Need outreach and content angle for feature launches.",
        {"churn": 0.03, "arpu": 18.0},
    ),
    (
        "device-assembly",
        "D1",
        "Device assembly line. Station rework loops. Config is tribal knowledge. Need config SKU matrix and station timer.",
        {"rework": 0.16, "utilization": 0.7, "monthly_revenue": 110000},
    ),
    (
        "device-assembly",
        "D2",
        "Guided setup product for integrators. Throughput stuck. Marketing leads are weak; need promo stories for makers.",
        {"utilization": 0.58, "monthly_revenue": 40000},
    ),
]


def _tokens(text: str) -> set[str]:
    import re
    return {t.lower() for t in re.findall(r"[A-Za-zА-Яа-я]{4,}", text or "")}


def main() -> None:
    results = []
    bodies = []
    for industry, tag, brief, numbers in CASES:
        res = process_client_request(
            {
                "industry": industry,
                "business": brief + " Need a clear next move in 14 days.",
                "name": f"Bench-{tag}",
                "success_metrics": {"business_numbers": numbers},
            }
        )
        pc = res["meta"]["paid_product_core"]
        pkg = pc.get("package_deliverable") or {}
        path = (pkg.get("package_result") or {}).get("markdown")
        text = Path(path).read_text(encoding="utf-8") if path else ""
        # Core content only (diagnosis + mechanism) — ignore shared pricing/DoD shell
        core = text
        for marker in ("## 5. Technical", "## 6. Next 14", "## 7. Constraints", "## Package pricing"):
            if marker in core:
                core = core.split(marker)[0]
        if "## 1. Diagnosis" in core:
            core = core.split("## 1. Diagnosis", 1)[-1]
        tang = pkg.get("tangibility") or {}
        cat = {}
        # load from QA if present
        qa = Path(path).parent / "TANGIBILITY_QA.json" if path else None
        if qa and qa.exists():
            cat = (json.loads(qa.read_text(encoding="utf-8")).get("category_router") or {})
        results.append(
            {
                "tag": tag,
                "industry": industry,
                "ok": res.get("ok"),
                "tangibility": tang.get("score"),
                "ready": tang.get("ready_for_paid_send"),
                "primary_track": cat.get("primary"),
                "chars": len(text),
                "core_chars": len(core),
                "has_ru": (Path(path).parent / "YOUR_RESULT_ru.md").exists() if path else False,
            }
        )
        bodies.append(core)

    # pairwise originality
    overlaps = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = _tokens(bodies[i]), _tokens(bodies[j])
            if not a or not b:
                continue
            o = len(a & b) / len(a | b)
            overlaps.append(o)
    mean_overlap = sum(overlaps) / max(1, len(overlaps))
    # Same-industry pairs should still diverge (different briefs)
    same_ind = []
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            if results[i]["industry"] == results[j]["industry"]:
                a, b = _tokens(bodies[i]), _tokens(bodies[j])
                if a and b:
                    same_ind.append(len(a & b) / len(a | b))
    mean_same = sum(same_ind) / max(1, len(same_ind))

    out = {
        "cases": results,
        "mean_jaccard_overlap": round(mean_overlap, 4),
        "mean_same_industry_overlap": round(mean_same, 4),
        # Core sections only (diagnosis+mechanism); shell is shared by design
        "originality_pass": mean_same < 0.65 and mean_overlap < 0.55,
        "all_ready": all(r.get("ready") for r in results),
        "n": len(results),
        "tracks": sorted({r.get("primary_track") for r in results}),
    }
    dest = ROOT / "docs" / "INDUSTRY_ORIGINALITY_BENCH.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
