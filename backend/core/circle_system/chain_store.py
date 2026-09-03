"""Persist assembled chains. No chain_id without a resource bind."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR

CHAINS_DIR = DATA_DIR / "chains"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(chain_id: str) -> Path:
    CHAINS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in chain_id if c.isalnum() or c in "-_")[:80]
    return CHAINS_DIR / f"{safe}.json"


def save_chain(record: dict[str, Any]) -> dict[str, Any]:
    cid = str(record.get("chain_id") or "")
    if not cid:
        raise ValueError("no chain_id")
    rec = {**record, "updated": _now()}
    rec.setdefault("created", rec["updated"])
    p = _path(cid)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    return rec


def load_chain(chain_id: str) -> dict[str, Any] | None:
    p = _path(chain_id)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text("utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def list_chain_ids(limit: int = 50) -> list[str]:
    CHAINS_DIR.mkdir(parents=True, exist_ok=True)
    names = sorted(CHAINS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    return [p.stem for p in names[:limit]]
