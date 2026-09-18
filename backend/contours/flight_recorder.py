"""Engine B — Agent Flight Recorder / log-audit plane (C2)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from backend.contours import store

STEP_TYPES = ("thought", "tool", "llm", "error")
HALT = "STATE_HALTED"


def _tenant(tid: str | None) -> str:
    return (tid or "public").strip() or "public"


def log_event(
    *,
    tenant_id: str = "public",
    agent_id: str,
    trace_id: str | None = None,
    step_type: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: float = 0,
    cost_usd: float = 0,
    payload_json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    st = step_type if step_type in STEP_TYPES else "tool"
    row = store.upsert(
        tenant_id,
        "flight_logs",
        {
            "id": store.new_id("fl_"),
            "agent_id": agent_id,
            "trace_id": trace_id or store.new_id("tr_"),
            "step_type": st,
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "latency_ms": float(latency_ms),
            "cost_usd": float(cost_usd),
            "payload_json": payload_json or {},
            "ts": store.now_iso(),
        },
    )
    store.audit(tenant_id, "flight.log", {"id": row["id"], "step_type": st})
    return row


def window_cost(tenant_id: str, hours: float = 1.0) -> float:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    total = 0.0
    for r in store.load_all(tenant_id, "flight_logs"):
        ts = r.get("ts") or ""
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt >= cutoff:
            total += float(r.get("cost_usd") or 0)
    return round(total, 6)


def kill_switch(
    tenant_id: str,
    *,
    threshold_usd: float = 25.0,
    webhook: str | None = None,
) -> dict[str, Any]:
    spent = window_cost(tenant_id, 1.0)
    halted = spent >= threshold_usd
    state = HALT if halted else "STATE_OK"
    row = store.upsert(
        tenant_id,
        "kill_switch",
        {
            "id": "ks_current",
            "state": state,
            "spent_1h_usd": spent,
            "threshold_usd": threshold_usd,
            "webhook": webhook,
            "telegram_stub": {"sent": halted, "channel": "stub"},
        },
    )
    if halted:
        store.audit(tenant_id, "flight.halt", {"spent": spent, "threshold": threshold_usd})
    return row


def validate_output(
    output: dict[str, Any] | None,
    schema_keys: list[str] | None = None,
    rag_ids: list[str] | None = None,
) -> dict[str, Any]:
    obj = output if isinstance(output, dict) else {}
    keys = schema_keys or ["outcome_class"]
    missing = [k for k in keys if k not in obj]
    refs = list(rag_ids or [])
    cited = obj.get("citations") or obj.get("rag_ids") or []
    if not isinstance(cited, list):
        cited = []
    boundary_ok = not missing
    if refs:
        boundary_ok = boundary_ok and any(r in cited for r in refs)
    return {
        "ok": boundary_ok and not missing,
        "missing": missing,
        "hallucination_risk": (not boundary_ok),
        "citations": cited,
        "required": keys,
    }


def export_pack(tenant_id: str, trace_id: str | None = None) -> dict[str, Any]:
    logs = store.load_all(tenant_id, "flight_logs")
    if trace_id:
        logs = [r for r in logs if r.get("trace_id") == trace_id]
    body = {
        "tenant_id": tenant_id,
        "trace_id": trace_id,
        "n": len(logs),
        "steps": logs,
        "kill": store.get(tenant_id, "kill_switch", "ks_current"),
        "exported": store.now_iso(),
        "format": "json_compliance_pack",
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    body["sha256"] = digest
    return body


def track_agent(agent_id: str, tenant_id: str = "public") -> Callable:
    """SDK surface: @track_agent('my-agent')."""

    def deco(fn: Callable) -> Callable:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            t0 = datetime.now(timezone.utc)
            err = None
            try:
                return fn(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 — recorder must not hide, only log
                err = e
                raise
            finally:
                ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
                log_event(
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    step_type="error" if err else "tool",
                    latency_ms=ms,
                    payload_json={"fn": getattr(fn, "__name__", "fn"), "error": str(err) if err else None},
                )

        wrapped.__name__ = getattr(fn, "__name__", "tracked")
        return wrapped

    return deco
