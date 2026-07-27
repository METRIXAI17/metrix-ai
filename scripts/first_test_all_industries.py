#!/usr/bin/env python3
"""
Первый тест по каждому из 6 направлений сайта.

Запуск:
  cd Desktop/metrix-ai
  python scripts/first_test_all_industries.py

Не требует поднятого HTTP-сервера — бьёт прямо в RequestPipeline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.request_pipeline import process_client_request

SAMPLES = {
    "ai-agencies": (
        "We are a boutique AI agency delivering custom agents for mid-market ops teams. "
        "Our edge is semi-manual delivery with strong client handoff. We struggle to "
        "package ready-made solutions instead of reinventing each project, and need "
        "clearer pricing and reverse outreach."
    ),
    "cloud-economy": (
        "We run multi-cloud workloads for SaaS clients and sell FinOps advisory. "
        "Latency-sensitive features need edge placement, but spend is chaotic. "
        "We want unit economics per workload and a productized optimization offer."
    ),
    "cost-engineering": (
        "Industrial cost engineering firm. We cut waste in manufacturing parameters "
        "without killing performance. Clients drown in spreadsheets. We need a "
        "parameter map product and a clear paid pilot that pays back fast."
    ),
    "chipmaking": (
        "Semiconductor design services: RTL to tapeout support for specialty chips. "
        "Yield risk and NRE dominate decisions. We want a vulnerability void index "
        "for design loops and a simulation layer before expensive fab commits."
    ),
    "telecom": (
        "Telecom BSS/OSS integrator for MVNOs. We care about QoS, ARPU, churn, and "
        "intent-driven care. Need linguistic cooperation between NLU agents and "
        "network signals, plus SLA-native product SKUs."
    ),
    "device-assembly": (
        "We design assembly and configuration workflows for IoT device makers. "
        "Stations, fixtures, firmware setup, rework loops. Want intellectual "
        "work instructions and config SKUs that scale without tribal knowledge."
    ),
}


def main() -> int:
    print("=" * 72)
    print("METRIX AI — first test round · 6 industry directions")
    print("=" * 72)
    results = []
    for industry, business in SAMPLES.items():
        print(f"\n>>> {industry}")
        out = process_client_request(
            {
                "industry": industry,
                "business": business,
                "track": "all",
                "name": "First Test",
                "contact": "@karimmetrix",
            }
        )
        ok = out.get("ok")
        idea = (out.get("demo_idea") or {}).get("title", "?")
        mode = out.get("operating_mode")
        health = (
            ((out.get("metrics") or {}).get("unified") or {}).get("health_score")
            or ((out.get("metrics") or {}).get("unified") or {}).get("core", {}).get("health_score")
        )
        # unified metrics structure
        um = (out.get("metrics") or {}).get("unified") or {}
        if "health_score" not in um and "core" in um:
            health = um["core"].get("health_score")
        elif "health_score" in um:
            health = um["health_score"]
        else:
            health = um.get("health_score")
        # CoreMetrics.to_dict has health_score at top level of core
        if isinstance(um, dict) and "vvi" in um:
            health = um.get("health_score")
        iroi = (out.get("breakdown") or {}).get("profitability", {}).get("info_roi")
        fins = [f.get("model_id") for f in out.get("fin_models") or []]
        print(f"    ok={ok} mode={mode}")
        print(f"    idea: {idea[:90]}")
        print(f"    health={health} IROI={iroi} fins={fins}")
        print(f"    request_id={out.get('request_id')}")
        results.append(
            {
                "industry": industry,
                "ok": ok,
                "mode": mode,
                "idea": idea,
                "health": health,
                "info_roi": iroi,
                "fin_models": fins,
                "request_id": out.get("request_id"),
            }
        )

    out_path = ROOT / "docs" / "first_test_results.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 72)
    print(f"Saved: {out_path}")
    failed = [r for r in results if not r["ok"]]
    if failed:
        print(f"FAILED: {len(failed)}")
        return 1
    print("ALL 6 DIRECTIONS OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
