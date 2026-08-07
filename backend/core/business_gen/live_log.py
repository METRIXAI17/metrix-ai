"""
Live 7-day channel log — interactive, not a static word "network".

Local: file sessions under data/live_logs/
Production upgrade path: Supabase tables (see docs/SUPABASE_LIVE_LOG.md)
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    from backend.config import DATA_DIR as _DATA
    from backend.config import SUPABASE_ENABLED, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
except Exception:  # pragma: no cover
    _DATA = Path(__file__).resolve().parents[2] / "data"
    SUPABASE_ENABLED = False
    SUPABASE_URL = ""
    SUPABASE_SERVICE_ROLE_KEY = ""

LOG_DIR = Path(_DATA) / "live_logs"


def _ensure() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def create_live_log_from_plan(
    channel_plan: dict[str, Any],
    *,
    project_name: str = "",
    run_id: str = "",
    lang: str = "ru",
) -> dict[str, Any]:
    """Materialize interactive log session from core_report.channel_log_7d."""
    plan = channel_plan or {}
    sid = f"log_{uuid.uuid4().hex[:10]}"
    days = []
    for d in plan.get("days") or []:
        days.append(
            {
                "day": d.get("day"),
                "day_offset": d.get("day_offset"),
                "label": d.get("label"),
                "action": d.get("action"),
                "owner": d.get("owner") or "Founder",
                "done": False,
                "note": d.get("note") or "",
                "touched_at": None,
            }
        )
    session = {
        "id": sid,
        "module": "LiveChannelLog",
        "version": "1.0",
        "project_name": project_name,
        "run_id": run_id,
        "created_at": time.time(),
        "start_date": plan.get("start_date") or date.today().isoformat(),
        "end_date": plan.get("end_date")
        or (date.today() + timedelta(days=6)).isoformat(),
        "channel_name": plan.get("channel_name"),
        "touch_target": plan.get("touch_target") or 12,
        "touches_done": 0,
        "artifact": plan.get("artifact") or {},
        "artifact_shipped": False,
        "days": days,
        "ledger": [],
        "rule": plan.get("rule"),
        "lang": _lang(lang),
        "status": "live",
        "backend": "supabase" if SUPABASE_ENABLED else "local_file",
        "supabase_ready": True,
        "supabase_enabled": bool(SUPABASE_ENABLED),
    }
    _save(session)
    if SUPABASE_ENABLED:
        _supabase_upsert_session(session)
    return session


def get_log(session_id: str) -> dict[str, Any]:
    path = _ensure() / f"{session_id}.json"
    if not path.exists():
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "session": json.loads(path.read_text(encoding="utf-8"))}


def tick_log(
    session_id: str,
    *,
    day_offset: int | None = None,
    day: str | None = None,
    note: str = "",
    mark_artifact: bool = False,
    who: str = "",
    response: str = "",
) -> dict[str, Any]:
    path = _ensure() / f"{session_id}.json"
    if not path.exists():
        return {"ok": False, "error": "not_found"}
    data = json.loads(path.read_text(encoding="utf-8"))
    matched = False
    for row in data.get("days") or []:
        if day_offset is not None and row.get("day_offset") == day_offset:
            row["done"] = True
            row["note"] = note or row.get("note") or ""
            row["touched_at"] = time.time()
            matched = True
        elif day and row.get("day") == day:
            row["done"] = True
            row["note"] = note or row.get("note") or ""
            row["touched_at"] = time.time()
            matched = True
    if mark_artifact:
        data["artifact_shipped"] = True
    if who or response or note:
        data.setdefault("ledger", []).append(
            {
                "ts": time.time(),
                "who": who,
                "response": response,
                "note": note,
                "day": day,
                "day_offset": day_offset,
            }
        )
    done_n = sum(1 for r in data.get("days") or [] if r.get("done"))
    data["touches_done"] = done_n
    if done_n >= len(data.get("days") or []) and data.get("artifact_shipped"):
        data["status"] = "complete"
    _save(data)
    if SUPABASE_ENABLED:
        _supabase_upsert_session(data)
    return {"ok": True, "matched": matched, "session": data}


def _save(session: dict[str, Any]) -> None:
    sid = session.get("id") or f"log_{uuid.uuid4().hex[:10]}"
    session["id"] = sid
    path = _ensure() / f"{sid}.json"
    path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def _supabase_upsert_session(session: dict[str, Any]) -> None:
    """Best-effort REST upsert via unified sync. Failures never break generate."""
    if not SUPABASE_ENABLED:
        return
    try:
        from backend.services.supabase_sync import sync_live_log_session

        sync_live_log_session(session)
    except Exception:
        # stay local-file resilient
        pass
