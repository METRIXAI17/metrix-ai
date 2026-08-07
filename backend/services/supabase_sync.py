"""
Supabase sync — persist Metrix AI responses (runs, live_log, skills).

Best-effort: never break the main request path if Supabase is down/missing.
Uses service role on server only.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("metrix.supabase")

try:
    from backend.config import (
        SUPABASE_ENABLED,
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )
except Exception:  # pragma: no cover
    SUPABASE_ENABLED = False
    SUPABASE_URL = ""
    SUPABASE_SERVICE_ROLE_KEY = ""


# Keys that must never land in Supabase payload
_REDACT_KEYS = frozenset(
    {
        "price_usd",
        "ops_price_usd",
        "tariff_price_usd",
        "ops_commercial",
        "service_role",
        "service_role_key",
        "authorization",
        "password",
        "secret",
        "api_key",
        "apikey",
        "token",
        "contact",  # PII soft-redact unless explicit
    }
)


def is_enabled() -> bool:
    return bool(SUPABASE_ENABLED and SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


def _headers() -> dict[str, str]:
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_for_store(obj: Any, *, depth: int = 0) -> Any:
    """Deep-copy-ish redact of commercial + secret fields."""
    if depth > 12:
        return None
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in _REDACT_KEYS or any(s in lk for s in ("password", "secret", "token", "api_key")):
                continue
            if lk in ("price", "pricing") and isinstance(v, (int, float)):
                continue
            out[k] = redact_for_store(v, depth=depth + 1)
        return out
    if isinstance(obj, list):
        # Cap huge lists
        return [redact_for_store(x, depth=depth + 1) for x in obj[:200]]
    if isinstance(obj, str) and len(obj) > 120_000:
        return obj[:120_000] + "…[truncated]"
    return obj


def _summarize(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact summary for list views — not full blob."""
    out = payload.get("output") if isinstance(payload.get("output"), dict) else payload
    if not isinstance(out, dict):
        return {"keys": list(payload.keys())[:20] if isinstance(payload, dict) else []}
    gencore = out.get("gencore") or {}
    wayd = out.get("wayd") or {}
    terminal = wayd.get("terminal") if isinstance(wayd, dict) else {}
    acc = out.get("acceptance_forecast") or {}
    seg = (out.get("client_segmentation") or {}).get("primary") or {}
    path = (out.get("user_path") or {}).get("path") or {}
    live = out.get("live_log") or {}
    return {
        "module": payload.get("module") or out.get("module"),
        "version": payload.get("version") or out.get("version"),
        "segment_id": seg.get("id"),
        "path_id": path.get("id"),
        "acceptance_p": acc.get("acceptance_p") or (terminal or {}).get("acceptance_p"),
        "ship_gate": (terminal or {}).get("ship_gate"),
        "gencore_gen": gencore.get("generation"),
        "slots_ready": gencore.get("slots_ready"),
        "live_log_id": live.get("id"),
        "originality": (out.get("originality") or {}).get("originality"),
        "message": (payload.get("message") or out.get("message") or "")[:240],
    }


def _client():
    import httpx

    return httpx.Client(timeout=10.0)


def rest_upsert(table: str, rows: dict[str, Any] | list[dict[str, Any]]) -> bool:
    if not is_enabled():
        return False
    try:
        with _client() as client:
            r = client.post(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers=_headers(),
                json=rows,
            )
            if r.status_code >= 400:
                logger.warning("supabase upsert %s → %s %s", table, r.status_code, r.text[:200])
                return False
            return True
    except Exception as e:
        logger.warning("supabase upsert %s failed: %s", table, e)
        return False


def sync_run(
    *,
    endpoint: str,
    payload: dict[str, Any],
    request_meta: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """
    Sync a full Metrix AI response to metrix_runs.
    Returns {ok, run_id, stored}.
    """
    rid = run_id or f"run_{uuid.uuid4().hex[:14]}"
    if not is_enabled():
        return {"ok": False, "run_id": rid, "stored": False, "reason": "supabase_disabled"}

    meta = request_meta or {}
    safe = redact_for_store(payload if isinstance(payload, dict) else {"data": payload})
    summary = _summarize(safe if isinstance(safe, dict) else {})

    # Hash for dedupe / integrity
    blob = json.dumps(safe, ensure_ascii=False, sort_keys=True, default=str)
    content_hash = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]

    row = {
        "id": rid,
        "endpoint": (endpoint or "")[:120],
        "project_name": (meta.get("project_name") or summary.get("module") or "")[:200],
        "industry_id": (meta.get("industry_id") or meta.get("industry") or "")[:80],
        "lang": (meta.get("lang") or "ru")[:8],
        "segment_id": summary.get("segment_id"),
        "path_id": summary.get("path_id"),
        "acceptance_p": summary.get("acceptance_p"),
        "ship_gate": summary.get("ship_gate"),
        "summary": summary,
        "payload": safe,
        "content_hash": content_hash,
        "business_excerpt": (meta.get("business") or "")[:500],
        "created_at": _now_iso(),
    }
    ok = rest_upsert("metrix_runs", row)
    return {"ok": ok, "run_id": rid, "stored": ok, "content_hash": content_hash}


def sync_skill(skill: dict[str, Any]) -> bool:
    if not is_enabled() or not skill:
        return False
    safe = redact_for_store(skill)
    if not isinstance(safe, dict):
        return False
    row = {
        "id": safe.get("id") or f"sk_{uuid.uuid4().hex[:10]}",
        "name": (safe.get("name") or "")[:120],
        "domain": safe.get("domain"),
        "tags": safe.get("tags") or [],
        "success": bool(safe.get("success")),
        "confidence": safe.get("confidence"),
        "band": safe.get("band"),
        "conceptual_algorithm": safe.get("conceptual_algorithm") or {},
        "executive_algorithm": safe.get("executive_algorithm") or {},
        "lang": safe.get("lang") or "ru",
        "version": safe.get("version") or "1.0",
        "payload": safe,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    return rest_upsert("skill_memory", row)


def sync_live_log_session(session: dict[str, Any]) -> bool:
    """Upsert session + days + ledger rows (used by live_log.py)."""
    if not is_enabled() or not session:
        return False
    try:
        row = {
            "id": session.get("id"),
            "project_name": session.get("project_name"),
            "run_id": session.get("run_id"),
            "start_date": session.get("start_date"),
            "end_date": session.get("end_date"),
            "touch_target": session.get("touch_target"),
            "touches_done": session.get("touches_done"),
            "artifact": session.get("artifact") or {},
            "artifact_shipped": session.get("artifact_shipped"),
            "channel_name": session.get("channel_name"),
            "status": session.get("status"),
            "lang": session.get("lang"),
            "updated_at": _now_iso(),
        }
        days = [
            {
                "session_id": session.get("id"),
                "day_offset": d.get("day_offset"),
                "day": d.get("day"),
                "label": d.get("label"),
                "action": d.get("action"),
                "owner": d.get("owner"),
                "done": d.get("done"),
                "note": d.get("note") or "",
                "touched_at": (
                    datetime.fromtimestamp(d["touched_at"], tz=timezone.utc).isoformat()
                    if d.get("touched_at")
                    else None
                ),
            }
            for d in session.get("days") or []
        ]
        ledger = [
            {
                "session_id": session.get("id"),
                "ts": (
                    datetime.fromtimestamp(e["ts"], tz=timezone.utc).isoformat()
                    if e.get("ts")
                    else _now_iso()
                ),
                "who": e.get("who"),
                "response": e.get("response"),
                "note": e.get("note"),
                "day_offset": e.get("day_offset"),
            }
            for e in (session.get("ledger") or [])[-50:]
        ]
        ok = rest_upsert("live_log_sessions", row)
        if days:
            # Prefer upsert on unique(session_id, day_offset)
            rest_upsert("live_log_days", days)
        if ledger:
            rest_upsert("live_log_ledger", ledger)
        return ok
    except Exception as e:
        logger.warning("sync_live_log_session failed: %s", e)
        return False


def attach_sync_meta(result: dict[str, Any], sync_info: dict[str, Any]) -> dict[str, Any]:
    """Add non-breaking sync metadata to API response."""
    if not isinstance(result, dict):
        return result
    out = dict(result)
    out["supabase_sync"] = {
        "enabled": is_enabled(),
        "stored": bool(sync_info.get("stored")),
        "run_id": sync_info.get("run_id"),
        "ok": bool(sync_info.get("ok")),
        "ts": time.time(),
    }
    return out
