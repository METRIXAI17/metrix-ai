"""Engine C — Process Contour OS (C1). Lead → owner → SLA → Monday report."""

from __future__ import annotations

from typing import Any

from backend.contours import store

STAGES = ("new", "qualified", "in_progress", "waiting", "done", "escalated")
TRANSITIONS = {
    "new": ("qualified", "escalated"),
    "qualified": ("in_progress", "escalated"),
    "in_progress": ("waiting", "done", "escalated"),
    "waiting": ("in_progress", "done", "escalated"),
    "done": (),
    "escalated": ("in_progress", "done"),
}


def _tid(t: str | None) -> str:
    return (t or "public").strip() or "public"


def require_outcome(tenant_id: str, project_id: str) -> dict[str, Any] | None:
    for row in store.load_all(tenant_id, "outcome_contracts"):
        if row.get("project_id") == project_id:
            return row
    return None


def bind_outcome(
    *,
    tenant_id: str,
    project_id: str,
    named_observable: str,
    baseline: str,
    target: str,
    measurement: str,
    exclusions: str,
    acceptance_test: str,
) -> dict[str, Any]:
    row = store.upsert(
        tenant_id,
        "outcome_contracts",
        {
            "id": f"oc_{project_id}",
            "project_id": project_id,
            "named_observable": named_observable,
            "baseline": baseline,
            "target": target,
            "measurement": measurement,
            "exclusions": exclusions,
            "acceptance_test": acceptance_test,
        },
    )
    store.audit(tenant_id, "process.outcome_bound", {"project_id": project_id})
    return row


def ingest_lead(
    *,
    tenant_id: str,
    source: str,
    text: str,
    owner: str | None = None,
    sla_minutes: int = 30,
    project_id: str = "default",
) -> dict[str, Any]:
    if not require_outcome(tenant_id, project_id):
        return {
            "ok": False,
            "error": "outcome_contract_required",
            "hint": "Bind OutcomeContract before Stage 1.",
            "project_id": project_id,
        }
    row = store.upsert(
        tenant_id,
        "leads",
        {
            "id": store.new_id("ld_"),
            "source": source or "webhook",
            "text": (text or "")[:2000],
            "owner": owner,
            "stage": "new",
            "sla_minutes": int(sla_minutes),
            "project_id": project_id,
            "discrepancy": None,
        },
    )
    store.audit(tenant_id, "process.lead", {"id": row["id"], "source": source})
    return {"ok": True, "lead": row}


def set_stage(tenant_id: str, lead_id: str, stage: str) -> dict[str, Any]:
    lead = store.get(tenant_id, "leads", lead_id)
    if not lead:
        return {"ok": False, "error": "unknown_lead"}
    cur = lead.get("stage") or "new"
    if stage not in STAGES:
        return {"ok": False, "error": "bad_stage", "allowed": STAGES}
    if stage != cur and stage not in TRANSITIONS.get(cur, ()):
        return {"ok": False, "error": "illegal_transition", "from": cur, "to": stage}
    lead["stage"] = stage
    store.upsert(tenant_id, "leads", lead)
    return {"ok": True, "lead": lead}


def mark_discrepancy(tenant_id: str, lead_id: str, a: str, b: str) -> dict[str, Any]:
    lead = store.get(tenant_id, "leads", lead_id)
    if not lead:
        return {"ok": False, "error": "unknown_lead"}
    lead["discrepancy"] = {"source_a": a, "source_b": b, "ts": store.now_iso()}
    store.upsert(tenant_id, "leads", lead)
    return {"ok": True, "lead": lead}


def monday_report(tenant_id: str, project_id: str = "default") -> dict[str, Any]:
    leads = [l for l in store.load_all(tenant_id, "leads") if l.get("project_id") == project_id]
    n = max(1, len(leads))
    ownerless = sum(1 for l in leads if not l.get("owner"))
    sla_breach = sum(1 for l in leads if l.get("stage") == "escalated")
    mismatch = sum(1 for l in leads if l.get("discrepancy"))
    done = sum(1 for l in leads if l.get("stage") == "done")
    metrics = {
        "leads": len(leads),
        "ownerless_pct": round(100 * ownerless / n, 1),
        "sla_breach_pct": round(100 * sla_breach / n, 1),
        "source_mismatch_pct": round(100 * mismatch / n, 1),
        "done_pct": round(100 * done / n, 1),
    }
    md = (
        f"# Monday report · {project_id}\n\n"
        f"- leads: {metrics['leads']}\n"
        f"- ownerless: {metrics['ownerless_pct']}%\n"
        f"- SLA / escalated: {metrics['sla_breach_pct']}%\n"
        f"- source mismatch: {metrics['source_mismatch_pct']}%\n"
        f"- done: {metrics['done_pct']}%\n"
    )
    row = store.upsert(
        tenant_id,
        "weekly_reports",
        {"id": store.new_id("wr_"), "project_id": project_id, "metrics": metrics, "markdown": md},
    )
    return {**row, "markdown": md}
