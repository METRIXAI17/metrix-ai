"""
Multi-pass eval on top-5 user paths + online niche rework.

Usage (from repo root):
  py -3 scripts/multi_pass_path_eval.py
  py -3 scripts/multi_pass_path_eval.py --passes 5
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.business_gen.user_paths import PATHS, select_user_path
from backend.core.business_gen.online_niche_rework import rework_online_niches
from backend.core.business_gen.acceptance_forecast import forecast_acceptance
from backend.core.business_gen.originality_inject import inject_three_directions
from backend.core.wayd import compute_terminal, compose_edges


# Representative briefs for top paths
TOP5_BRIEFS = [
    {
        "path_hint": "library_ship",
        "name": "Architecture Design Library",
        "brief": (
            "Online architecture design library for IT product builders: "
            "niche cards, concept tests, unit packs, warm builder channel log."
        ),
    },
    {
        "path_hint": "agency_margin",
        "name": "AI Agency Rework Desk",
        "brief": (
            "AI agency studio with handoff chaos and rework. Need delivery margin "
            "scoreboard and warm referral channel for 21 days."
        ),
    },
    {
        "path_hint": "builder_pack",
        "name": "Automation Builder SaaS",
        "brief": (
            "Online automation builder / no-code product. WIP limits, pilot widgets, "
            "builder DM list and unit SKU for early SaaS founders."
        ),
    },
    {
        "path_hint": "api_cost",
        "name": "API Cost Cut Studio",
        "brief": (
            "Founder studio burns OpenAI and Anthropic tokens. Need API cost cut "
            "without quality loss, model routing, cost per accepted outcome."
        ),
    },
    {
        "path_hint": "expert_sku",
        "name": "Expert 90-day Pack",
        "brief": (
            "Expert consulting online: replace hourly with 90-day pack, clear "
            "boundaries, acceptance page, single stop-rule, proof content."
        ),
    },
]


def eval_one(item: dict, passes: int = 3) -> dict:
    brief = item["brief"]
    name = item["name"]
    path = select_user_path(brief, lang="ru", sophisticated=True)
    rework = rework_online_niches(
        brief, lang="ru", multi_pass=passes, project_name=name, industry_id="saas-founders"
    )
    three = rework.get("originality") or {}
    acc = rework.get("acceptance") or {}
    terminal = (rework.get("wayd") or {}).get("terminal") or {}
    return {
        "name": name,
        "path_hint": item["path_hint"],
        "path_selected": (path.get("path") or {}).get("id"),
        "path_fit": path.get("path_fit"),
        "sophistication": (path.get("path") or {}).get("sophistication"),
        "online_executor": rework.get("online_executor"),
        "segment": (rework.get("segment") or {}).get("primary", {}).get("id"),
        "originality": three.get("originality"),
        "acceptance_p": acc.get("acceptance_p"),
        "band": acc.get("band"),
        "ship_gate": terminal.get("ship_gate"),
        "mesh": terminal.get("mesh_score"),
        "niches": len(rework.get("niches_reworked") or []),
        "unique_functions": len((rework.get("wayd") or {}).get("unique_functions") or []),
        "passes": passes,
        "score": round(
            0.35 * float(acc.get("acceptance_p") or 0)
            + 0.25 * float(three.get("originality") or 0)
            + 0.20 * float(path.get("path_fit") or 0)
            + 0.20 * float(terminal.get("mesh_score") or 0),
            4,
        ),
    }


def main() -> int:
    passes = 3
    if "--passes" in sys.argv:
        i = sys.argv.index("--passes")
        if i + 1 < len(sys.argv):
            passes = max(1, min(int(sys.argv[i + 1]), 7))

    rows = [eval_one(b, passes=passes) for b in TOP5_BRIEFS]
    rows.sort(key=lambda r: -float(r["score"]))
    report = {
        "module": "MultiPassPathEval",
        "passes": passes,
        "count": len(rows),
        "rows": rows,
        "mean_score": round(sum(r["score"] for r in rows) / len(rows), 4),
        "mean_acceptance": round(
            sum(float(r["acceptance_p"] or 0) for r in rows) / len(rows), 4
        ),
        "mean_originality": round(
            sum(float(r["originality"] or 0) for r in rows) / len(rows), 4
        ),
    }

    out_dir = ROOT / "docs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "MULTI_PASS_TOP5_PATHS_2026-08-07.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Multi-pass eval · top-5 paths",
        "",
        f"Passes: **{passes}** · mean score: **{report['mean_score']}** · "
        f"mean P(accept): **{report['mean_acceptance']}** · "
        f"mean originality: **{report['mean_originality']}**",
        "",
        "| Path | Selected | Segment | P(accept) | Orig | Ship | Score |",
        "|------|----------|---------|-----------|------|------|-------|",
    ]
    for r in rows:
        md.append(
            f"| {r['name']} | `{r['path_selected']}` | `{r['segment']}` | "
            f"{r['acceptance_p']} | {r['originality']} | {r['ship_gate']} | **{r['score']}** |"
        )
    md_path = out_dir / "MULTI_PASS_TOP5_PATHS_2026-08-07.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nWrote {out_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
