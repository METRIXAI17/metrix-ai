"""Engine A — Metrix Eval Protocol & Orientation Core (C2).

Reproducible offline eval. Four axes on every run.
One primary knob change per experimental run.
"""

from __future__ import annotations

import time
from typing import Any

from backend.contours import store
from backend.contours.flags import llm_assist_enabled

AXES = ("error_rate", "latency_ms", "cost_usd", "escalation_rate")
REQUIRED_GOLD = ("outcome_class",)

OUTCOME_LEXICON: dict[str, tuple[str, str]] = {
    "lead": ("process_qualify", "process_rails"),
    "заявк": ("process_qualify", "process_rails"),
    "sla": ("process_sla", "process_rails"),
    "eval": ("eval_run", "eval_flight_recorder"),
    "ориент": ("orient", "eval_flight_recorder"),
    "agent": ("flight_trace", "eval_flight_recorder"),
    "агент": ("flight_trace", "eval_flight_recorder"),
    "on-prem": ("onprem_audit", "onprem_pipeline"),
    "онпрем": ("onprem_audit", "onprem_pipeline"),
    "air-gap": ("onprem_audit", "onprem_pipeline"),
    "rag": ("onprem_rag", "onprem_pipeline"),
    "spot": ("compute_spread", "compute_broker"),
    "gpu": ("compute_spread", "compute_broker"),
    "vast": ("compute_spread", "compute_broker"),
    "runpod": ("compute_spread", "compute_broker"),
    "cold": ("cold_alert", "cold_chain"),
    "температур": ("cold_alert", "cold_chain"),
    "chip": ("cold_capacity", "cold_chain"),
    "чип": ("cold_capacity", "cold_chain"),
    "pilot": ("custom_spec", "custom_spec_pilot"),
    "пилот": ("custom_spec", "custom_spec_pilot"),
    "cross": ("cross_pack", "cross_assist"),
    "касс": ("finance_indicator", "access_month"),
    "понедельник": ("finance_indicator", "access_month"),
}


def _tenant(tid: str | None) -> str:
    return (tid or "public").strip() or "public"


def seed_dataset(tenant_id: str = "public") -> dict[str, Any]:
    """Fixed seed. Same cases → same metrics."""
    ds = store.upsert(
        tenant_id,
        "eval_datasets",
        {
            "id": "ds_access_v1",
            "name": "Access basic eval",
            "version": "v1",
            "notes": "Reproducible Access-tier orientation cases.",
        },
    )
    cases = [
        {
            "id": "c1",
            "dataset_id": ds["id"],
            "input_json": {"text": "заявки горят, нет хозяина, нет цифры понедельника"},
            "gold_json": {
                "outcome_class": "process_qualify",
                "recommended_offer_sku": "process_rails",
                "escalate": False,
            },
            "tags": ["c1", "access"],
        },
        {
            "id": "c2",
            "dataset_id": ds["id"],
            "input_json": {"text": "нужен on-prem RAG за воздушным зазором"},
            "gold_json": {
                "outcome_class": "onprem_audit",
                "recommended_offer_sku": "onprem_pipeline",
                "escalate": False,
            },
            "tags": ["c3"],
        },
        {
            "id": "c3",
            "dataset_id": ds["id"],
            "input_json": {"text": "spot GPU дорого, хотим брокер с маржой"},
            "gold_json": {
                "outcome_class": "compute_spread",
                "recommended_offer_sku": "compute_broker",
                "escalate": False,
            },
            "tags": ["c4"],
        },
        {
            "id": "c4",
            "dataset_id": ds["id"],
            "input_json": {"text": "холодная цепь, удар и температура по рейсу"},
            "gold_json": {
                "outcome_class": "cold_alert",
                "recommended_offer_sku": "cold_chain",
                "escalate": False,
            },
            "tags": ["c5"],
        },
        {
            "id": "c5",
            "dataset_id": ds["id"],
            "input_json": {"text": "непонятно, эскалируйте человеку"},
            "gold_json": {
                "outcome_class": "STATE_ESCALATED",
                "recommended_offer_sku": "custom_spec_pilot",
                "escalate": True,
            },
            "tags": ["escalate"],
        },
    ]
    existing = {c["id"]: c for c in store.load_all(tenant_id, "eval_cases")}
    for c in cases:
        existing[c["id"]] = {**existing.get(c["id"], {}), **c}
    store.save_all(tenant_id, "eval_cases", list(existing.values()))
    store.audit(tenant_id, "eval.seed", {"dataset_id": ds["id"], "cases": len(cases)})
    return {"dataset": ds, "cases": len(cases)}


def orient(text: str) -> dict[str, Any]:
    raw = (text or "").strip().lower()
    hits: list[tuple[str, str, str]] = []
    for needle, (cls, sku) in OUTCOME_LEXICON.items():
        if needle in raw:
            hits.append((needle, cls, sku))
    escalate = any(w in raw for w in ("эскал", "человеку", "непонятно", "не знаю"))
    if escalate and not hits:
        cls, sku, conf = "STATE_ESCALATED", "custom_spec_pilot", 0.42
    elif hits:
        cls, sku = hits[0][1], hits[0][2]
        conf = min(0.93, 0.55 + 0.08 * len(hits))
    else:
        cls, sku, conf = "orient", "access_month", 0.48
    if escalate:
        cls = "STATE_ESCALATED"
    out = {
        "outcome_class": cls,
        "confidence": round(conf, 3),
        "recommended_offer_sku": sku,
        "escalate": bool(escalate or cls == "STATE_ESCALATED"),
        "hits": [h[0] for h in hits],
        "llm_assist": False,
        "axes": {
            "error_rate": 0.0,
            "latency_ms": 1,
            "cost_usd": 0.0,
            "escalation_rate": 1.0 if escalate else 0.0,
        },
    }
    if llm_assist_enabled():
        out["llm_assist"] = True
        out["llm_note"] = "flag on; deterministic layer remains primary"
    return out


def _match(pred: dict[str, Any], gold: dict[str, Any]) -> bool:
    if not gold:
        return False
    for k in REQUIRED_GOLD:
        if gold.get(k) != pred.get(k):
            return False
    if "escalate" in gold and bool(gold["escalate"]) != bool(pred.get("escalate")):
        return False
    return True


def _knob_warning(param_snapshot: dict[str, Any], baseline: dict[str, Any] | None) -> str | None:
    if not baseline:
        return None
    changed = [k for k in param_snapshot.keys() | baseline.keys() if param_snapshot.get(k) != baseline.get(k)]
    if len(changed) > 1:
        return f"more than one primary knob changed: {changed}"
    return None


def run(
    *,
    tenant_id: str = "public",
    dataset_id: str,
    engine_version: str = "orient-v1",
    param_snapshot: dict[str, Any] | None = None,
    baseline_id: str | None = None,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    seed_dataset(tenant_id)
    cases = [c for c in store.load_all(tenant_id, "eval_cases") if c.get("dataset_id") == dataset_id]
    if not cases:
        cases = [c for c in store.load_all(tenant_id, "eval_cases")]
    params = dict(param_snapshot or {"engine": engine_version})
    baseline = store.get(tenant_id, "eval_runs", baseline_id) if baseline_id else None
    warn = _knob_warning(params, (baseline or {}).get("param_snapshot") if baseline else None)

    results = []
    latencies: list[float] = []
    errors = 0
    escalations = 0
    cost = 0.0
    for case in cases:
        c0 = time.perf_counter()
        text = str((case.get("input_json") or {}).get("text") or "")
        pred = orient(text)
        ms = (time.perf_counter() - c0) * 1000
        latencies.append(ms)
        gold = case.get("gold_json") or {}
        ok = _match(pred, gold)
        if not ok:
            errors += 1
        if pred.get("escalate"):
            escalations += 1
        cost += float(pred.get("axes", {}).get("cost_usd") or 0.0)
        results.append(
            {
                "case_id": case.get("id"),
                "ok": ok,
                "pred": pred,
                "gold": gold,
                "latency_ms": round(ms, 3),
            }
        )

    n = max(1, len(cases))
    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else 0.0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    axes = {
        "error_rate": round(errors / n, 4),
        "latency_ms": {"p50": round(p50, 3), "p95": round(p95, 3)},
        "cost_usd": round(cost, 6),
        "escalation_rate": round(escalations / n, 4),
    }
    run_row = store.upsert(
        tenant_id,
        "eval_runs",
        {
            "id": store.new_id("run_"),
            "dataset_id": dataset_id,
            "engine_version": engine_version,
            "param_snapshot": params,
            "axes": axes,
            "n": len(cases),
            "warning": warn,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 3),
        },
    )
    store.upsert(
        tenant_id,
        "eval_run_results",
        {"id": run_row["id"] + "_res", "run_id": run_row["id"], "results": results},
    )
    store.audit(tenant_id, "eval.run", {"run_id": run_row["id"], "axes": axes})
    return {**run_row, "results": results}


def compare(tenant_id: str, run_id: str, baseline_id: str) -> dict[str, Any]:
    a = store.get(tenant_id, "eval_runs", run_id) or {}
    b = store.get(tenant_id, "eval_runs", baseline_id) or {}
    da, db = a.get("axes") or {}, b.get("axes") or {}
    delta: dict[str, Any] = {}
    for k in AXES:
        va, vb = da.get(k), db.get(k)
        if isinstance(va, dict) or isinstance(vb, dict):
            delta[k] = {"run": va, "baseline": vb}
        else:
            try:
                delta[k] = round(float(va or 0) - float(vb or 0), 6)
            except (TypeError, ValueError):
                delta[k] = {"run": va, "baseline": vb}
    moved = [k for k, v in delta.items() if not isinstance(v, dict) and abs(float(v or 0)) > 1e-9]
    return {
        "run_id": run_id,
        "baseline_id": baseline_id,
        "delta": delta,
        "axes_moved": moved,
        "cross_effect": len(moved) > 1,
        "max_param_changes_per_transition": 1,
    }


def access_eval(text: str, *, tenant_id: str = "public") -> dict[str, Any]:
    """Eval attached to a basic Access run. Does not claim accuracy."""
    pred = orient(text)
    row = store.upsert(
        tenant_id,
        "access_evals",
        {
            "id": store.new_id("ae_"),
            "text": (text or "")[:400],
            "pred": pred,
            "tier": "access",
        },
    )
    return {
        "eval": pred,
        "id": row["id"],
        "disclaimer": "measured orientation, not a guarantee",
    }
