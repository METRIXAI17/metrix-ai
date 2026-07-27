#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Один текстовый запрос в основную программу Metrix AI.

Запуск (рекомендуется):
  run_one_request.bat
  или
  py -3 scripts\\one_request.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Windows console UTF-8 (чтобы русский текст не ломался)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.config import INDUSTRIES
from backend.core.request_pipeline import process_client_request


INDUSTRY_LIST = list(INDUSTRIES.keys())


def read_line(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def ask_industry() -> str:
    print()
    print("Choose industry (type number 1-6 OR the id):")
    for i, key in enumerate(INDUSTRY_LIST, 1):
        name = INDUSTRIES[key]["name"]
        print(f"  {i}. {key}")
        print(f"     ({name})")
    print()
    raw = read_line("Your choice: ")
    if not raw:
        print("Empty. Using: ai-agencies")
        return "ai-agencies"
    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= len(INDUSTRY_LIST):
            return INDUSTRY_LIST[n - 1]
        print(f"Bad number. Using: ai-agencies")
        return "ai-agencies"
    if raw in INDUSTRIES:
        return raw
    # partial match
    for key in INDUSTRY_LIST:
        if raw.lower() in key.lower() or raw.lower() in INDUSTRIES[key]["name"].lower():
            return key
    print(f"Unknown '{raw}'. Using: ai-agencies")
    return "ai-agencies"


def ask_business() -> str:
    print()
    print("Describe the business (2-5 sentences).")
    print("Example: We are an MVNO integrator. We care about QoS, ARPU and churn.")
    print("Type text and press Enter:")
    print()
    text = read_line("> ")
    while len(text) < 20:
        print()
        print(f"Too short ({len(text)} chars). Need at least 20 characters.")
        text = read_line("> ")
        if not text:
            print("Cancelled.")
            sys.exit(1)
    return text


def ask_track() -> str:
    print()
    print("Track: 1=all  2=product  3=models  4=promotion")
    raw = read_line("Your choice [1]: ") or "1"
    mapping = {
        "1": "all",
        "2": "product",
        "3": "models",
        "4": "promotion",
        "all": "all",
        "product": "product",
        "models": "models",
        "promotion": "promotion",
    }
    return mapping.get(raw.lower(), "all")


def _clip(text: object, n: int = 200) -> str:
    s = str(text or "").strip()
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def print_paid_core(out: dict) -> None:
    """
    Block 18 — always show paid layer in console (not only inside full JSON).

    Distinguishes:
      iroi_recommend  — old «paid?» (idea profitability gate)
      paid_core       — actual Paid Product Core run (16 steps)
    """
    meta = out.get("meta") or {}
    paid = meta.get("paid_product_core") or {}
    bd = (out.get("breakdown") or {}).get("paid_product_core") or {}
    dec = out.get("decision_core") or {}
    handoff = dec.get("handoff_flags") or {}

    # Prefer full meta payload; fall back to breakdown summary
    status = paid.get("status") or bd.get("status") or meta.get("block_18_status")
    score = paid.get("paid_score")
    if score is None:
        score = bd.get("paid_score", meta.get("block_18_score"))
    pkg = paid.get("package") or bd.get("package") or {}
    reader = paid.get("reader") or {}
    plain = reader.get("plain_summary") or bd.get("reader_plain")
    sections = reader.get("sections") or []
    fe = (paid.get("critical_thinking") or {}).get("founder_error") or bd.get(
        "founder_error"
    ) or {}
    fn = paid.get("function_engine") or {}
    top_lever = fn.get("top_lever") or bd.get("top_lever") or pkg.get("top_lever")
    mega_cmp = (paid.get("mega_map") or {}).get("comparison") or bd.get(
        "mega_map_comparison"
    ) or {}
    best_hyp = (
        pkg.get("best_hypothesis")
        or mega_cmp.get("best_label")
        or mega_cmp.get("best_hypothesis_id")
    )
    metrics_overall = (paid.get("metric_tests") or {}).get("overall_score")
    if metrics_overall is None:
        metrics_overall = bd.get("metric_tests_overall")
    flow = paid.get("flow") or {}
    step_count = flow.get("step_count") or bd.get("flow_step_count")
    entanglement = (paid.get("energy_flow") or {}).get("total_entanglement")
    if entanglement is None:
        entanglement = bd.get("entanglement")
    chips = (paid.get("virtual_chips") or {}).get("chip_count")
    readiness = pkg.get("paid_readiness")
    if readiness is None and isinstance(pkg.get("result_plane"), dict):
        readiness = pkg["result_plane"].get("paid_readiness")

    print("Paid Product Core (block 18):")
    if not paid and not bd:
        print("  (not present in this response)")
        print()
        return

    print(f"  status        : {status}")
    print(f"  paid_score    : {score}")
    print(f"  handoff_ready : {handoff.get('ready_for_paid_block_18')}")
    print(f"  steps         : {step_count}")
    if chips is not None:
        print(f"  chips         : {chips}")
    if metrics_overall is not None:
        print(f"  metric_tests  : overall={metrics_overall}")
    if entanglement is not None:
        print(f"  entanglement  : {entanglement}")
    print()
    print("  Package:")
    print(f"    title           : {_clip(pkg.get('title') or '—', 100)}")
    print(f"    package_status  : {pkg.get('status') or status}")
    print(f"    paid_readiness  : {readiness}")
    print(f"    top_lever       : {top_lever}")
    print(f"    best_hypothesis : {_clip(best_hyp or '—', 100)}")
    nav = pkg.get("navigator_pick")
    if nav:
        print(f"    navigator_pick  : {_clip(nav, 100)}")
    root_al = pkg.get("root_alignment") or mega_cmp.get("root_alignment_score")
    if root_al is not None:
        print(f"    root_alignment  : {root_al}")
    competing = mega_cmp.get("competing_pairs")
    if competing is not None:
        print(f"    competing_pairs : {competing}")
    print()
    print("  Reader:")
    if plain:
        print(f"    plain : {_clip(plain, 240)}")
    else:
        print("    plain : —")
    # One-line topics if sections exist
    for sec in sections[:4]:
        topic = sec.get("topic") or ""
        text = _clip(sec.get("text"), 120)
        if topic:
            print(f"    · {topic}: {text}")
    actions = pkg.get("recommended_actions") or reader.get("action_bullets") or []
    if actions:
        print("  Package actions:")
        for a in actions[:5]:
            print(f"    - {_clip(a, 120)}")
    print()
    print("  Critical / honesty:")
    if fe:
        print(f"    founder_error   : suspected={fe.get('suspected')}")
        print(f"    error_class     : {fe.get('error_class')}")
        print(f"    confidence      : {fe.get('confidence')}")
        if fe.get("rationale"):
            print(f"    rationale       : {_clip(fe.get('rationale'), 180)}")
        if fe.get("suspected") and fe.get("recommended_correction"):
            print(f"    correction      : {_clip(fe.get('recommended_correction'), 160)}")
    else:
        print("    founder_error   : —")
    ct = paid.get("critical_thinking") or {}
    disc_n = ct.get("discrepancy_count")
    if disc_n is None and ct.get("discrepancies") is not None:
        disc_n = len(ct.get("discrepancies") or [])
    if disc_n is not None:
        print(f"    discrepancies   : {disc_n}")
    trust = (ct.get("resolved_variant") or {}).get("trust")
    if trust:
        print(f"    trust_variant   : {trust}")
    print()
    print("  Note: full 16-step trace → meta.paid_product_core in JSON file")
    print()

    # Commercial / earn layer
    metrics = paid.get("business_metrics") or {}
    questions = paid.get("clarifying_questions") or {}
    offer = paid.get("commercial_offer") or {}
    tangible = paid.get("tangible") or {}
    portal = paid.get("portal") or {}
    tz = paid.get("pilot_tz_draft") or {}

    if metrics or offer or questions:
        print("  Situation (business metrics):")
        if metrics:
            print(f"    situation_score : {metrics.get('situation_score')}")
            idx = metrics.get("indices") or {}
            print(
                f"    revenue_control : {idx.get('revenue_control_index')}  "
                f"friction={idx.get('delivery_friction')}  "
                f"margin_pressure={idx.get('margin_pressure')}"
            )
            leak = metrics.get("top_leak") or {}
            print(f"    top_leak        : {_clip(leak.get('label'), 80)}")
            print(
                f"    numbers_known   : {len(metrics.get('numbers_known') or {})}  "
                f"missing={len(metrics.get('numbers_missing') or [])}"
            )
            if metrics.get("narrative"):
                print(f"    narrative       : {_clip(metrics.get('narrative'), 200)}")
        print()
        print("  Earn / tangible:")
        tariff = offer.get("tariff") or {}
        print(f"    tariff          : {tariff.get('name')}  ${tariff.get('price_usd')}")
        print(f"    payment_link    : {(offer.get('payment') or {}).get('checkout_url')}")
        print(f"    portal_url      : {portal.get('url')}")
        print(f"    blocked_until_$ : {tangible.get('blocked_until_numbers')}")
        for a in (tangible.get("what_you_can_sell_now") or [])[:4]:
            print(f"    · {_clip(a.get('title'), 70)} — {a.get('earn')}")
        print()
        print("  Must-ask (before re-run):")
        must = questions.get("must_ask") or []
        if not must:
            print("    (none — can quote)")
        for i, q in enumerate(must[:6], 1):
            print(f"    {i}. {_clip(q.get('question'), 110)}")
        if questions.get("re_run_recommended"):
            print(
                f"    → re-run recommended; answers → "
                f"extra_params / success_metrics.business_numbers"
            )
        print()
        if tz.get("title"):
            print("  Pilot TZ draft:")
            print(f"    {_clip(tz.get('title'), 80)}")
            print(f"    hypothesis : {_clip(tz.get('solution_hypothesis'), 90)}")
            print(f"    lever      : {tz.get('top_lever')}")
            print()


def print_result(out: dict) -> None:
    idea = out.get("demo_idea") or {}
    profit = (out.get("breakdown") or {}).get("profitability") or {}
    um = (out.get("metrics") or {}).get("unified") or {}
    health = um.get("health_score")
    if health is None and isinstance(um.get("core"), dict):
        health = um["core"].get("health_score")

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"request_id : {out.get('request_id')}")
    print(f"industry   : {out.get('industry')}")
    print(f"mode       : {out.get('operating_mode')}")
    print()
    print("IDEA:")
    print(f"  {idea.get('title')}")
    summary = (idea.get("summary") or "").strip()
    if summary:
        print(f"  {summary[:500]}")
    print()
    print(f"health : {health}")
    print(f"IROI   : {profit.get('info_roi')}  ({profit.get('score_band')})")
    # Clarify: this is idea-profitability gate, NOT paid-core status
    print(
        f"iroi_recommend_paid : {profit.get('recommended')}  "
        f"(idea IROI gate — not paid-core status)"
    )
    print()
    # v2: Decision + OAE + Success
    dec = out.get("decision_core") or {}
    if dec:
        print("Decision Core:")
        print(f"  mode      : {dec.get('active_mode')}")
        print(f"  awareness : {dec.get('awareness_score')}")
        sw = dec.get("mode_switch") or {}
        if sw:
            print(f"  switch    : {sw.get('from_mode')} -> {sw.get('to_mode')}")
            print(f"  reason    : {sw.get('reason')}")
        handoff = dec.get("handoff_flags") or {}
        if handoff:
            print(
                f"  handoff   : paid_block_18={handoff.get('ready_for_paid_block_18')}  "
                f"gen_19={handoff.get('needs_generative_19')}  "
                f"demo={handoff.get('ready_for_demo')}"
            )
        print()
    sm = out.get("success_metrics") or {}
    if sm:
        print("Success metrics:")
        print(f"  composite : {sm.get('weighted_composite')}  hit={sm.get('hits_target')}")
        print()
    oae = out.get("operational_analytics") or {}
    if oae:
        print("Operational Analytics:")
        print(f"  logic     : {oae.get('processing_logic')}")
        print(f"  constructors: {len(oae.get('constructors') or [])}")
        emb = oae.get("embedding") or {}
        print(f"  embed_norm: {emb.get('norm')}")
        print(f"  abstract  : {len(oae.get('abstract_coordinates') or [])}")
        ric = oae.get("ricochet") or {}
        print(f"  ricochet  : events={ric.get('events_count')} delta_rrc={ric.get('total_rrc_delta')}")
        red = oae.get("reduced_to_request") or {}
        if red.get("client_facing_bridge"):
            print(f"  bridge    : {str(red['client_facing_bridge'])[:160]}...")
        print()
    fins = out.get("fin_models") or []
    if fins:
        print("Fin models:")
        for f in fins:
            print(f"  - {f.get('model_name')}  IROI={f.get('info_roi')}")
    print()
    mono = out.get("monetization") or {}
    if mono.get("summary"):
        print(f"Monetization: {mono['summary']}")
    print()

    # Block 18 — visible paid layer
    print_paid_core(out)

    print("Next steps:")
    for s in out.get("next_steps") or []:
        print(f"  * {s}")
    print("=" * 60)


def main() -> int:
    print()
    print("Metrix AI - main program (one request)")
    print("No batch quoting. Answer the questions below.")
    print()

    # Optional: args still work if user wants CLI
    # py -3 scripts/one_request.py 5
    # then only asks business
    argv = sys.argv[1:]

    if len(argv) >= 2:
        industry = argv[0]
        business = argv[1]
        track = argv[2] if len(argv) >= 3 else "all"
        if industry.isdigit():
            n = int(industry)
            industry = INDUSTRY_LIST[n - 1] if 1 <= n <= len(INDUSTRY_LIST) else "ai-agencies"
    else:
        industry = ask_industry()
        business = ask_business()
        track = ask_track()

    if industry not in INDUSTRIES:
        print(f"ERROR: bad industry {industry}")
        return 1
    if len(business) < 20:
        print("ERROR: business text too short")
        return 1

    print()
    print("Processing...")
    print(f"  industry = {industry}")
    print(f"  track    = {track}")
    print()

    out = process_client_request(
        {
            "industry": industry,
            "business": business,
            "track": track,
            "name": "Manual request",
            "contact": "",
        }
    )

    out_path = ROOT / "docs" / "last_request_result.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    if not out.get("ok"):
        print("ok: False")
        print("errors:", out.get("errors"))
        return 1

    print_result(out)
    print()
    print(f"Full JSON saved: {out_path}")
    print(f"Workspace: {ROOT / 'backend' / 'workspace' / str(out.get('request_id'))}")
    print()
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        code = 1
    except Exception as exc:
        print()
        print("ERROR:", type(exc).__name__, exc)
        import traceback

        traceback.print_exc()
        code = 1
    # keep window open if double-clicked... bat already pauses
    raise SystemExit(code)
