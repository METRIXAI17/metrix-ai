"""Tenant-isolated JSON store + append-only audit log.

Production on Railway stays file-backed (same as the rest of Metrix).
SQL schema lives in docs/CONTOURS_SQL.sql for the optional compose stack.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR

ROOT = DATA_DIR / "contours"
_LOCK = threading.Lock()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    raw = uuid.uuid4().hex[:16]
    return f"{prefix}{raw}" if prefix else raw


def tenant_dir(tenant_id: str) -> Path:
    tid = (tenant_id or "public").strip()[:64] or "public"
    p = ROOT / tid
    p.mkdir(parents=True, exist_ok=True)
    return p


def _path(tenant_id: str, collection: str) -> Path:
    safe = "".join(ch for ch in collection if ch.isalnum() or ch in "-_")[:48]
    return tenant_dir(tenant_id) / f"{safe}.json"


def load_all(tenant_id: str, collection: str) -> list[dict[str, Any]]:
    path = _path(tenant_id, collection)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_all(tenant_id: str, collection: str, rows: list[dict[str, Any]]) -> None:
    path = _path(tenant_id, collection)
    tmp = path.with_suffix(".tmp")
    with _LOCK:
        tmp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)


def upsert(tenant_id: str, collection: str, row: dict[str, Any], key: str = "id") -> dict[str, Any]:
    rows = load_all(tenant_id, collection)
    rid = str(row.get(key) or new_id())
    row[key] = rid
    row.setdefault("tenant_id", tenant_id or "public")
    row["updated"] = now_iso()
    out = []
    found = False
    for r in rows:
        if str(r.get(key)) == rid:
            merged = {**r, **row}
            out.append(merged)
            row = merged
            found = True
        else:
            out.append(r)
    if not found:
        row.setdefault("created", now_iso())
        out.append(row)
    save_all(tenant_id, collection, out)
    return row


def get(tenant_id: str, collection: str, rid: str, key: str = "id") -> dict[str, Any] | None:
    for r in load_all(tenant_id, collection):
        if str(r.get(key)) == str(rid):
            return r
    return None


def audit(tenant_id: str, event: str, payload: dict[str, Any] | None = None) -> None:
    line = {
        "ts": now_iso(),
        "tenant_id": tenant_id or "public",
        "event": event,
        "payload": payload or {},
    }
    path = tenant_dir(tenant_id) / "audit.jsonl"
    with _LOCK:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
