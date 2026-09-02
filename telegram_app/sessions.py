"""Tiny file-backed sessions. Filename is HMAC of chat_id, never the raw id."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR
from backend.core.access import subject_hash

DIR = DATA_DIR / "bot_sessions"


def _path(chat_id: int) -> Path:
    DIR.mkdir(parents=True, exist_ok=True)
    return DIR / f"{subject_hash(chat_id)}.json"


def load(chat_id: int) -> dict[str, Any]:
    p = _path(chat_id)
    if not p.exists():
        return {"mode": "idle"}
    try:
        data = json.loads(p.read_text("utf-8"))
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"mode": "idle"}


def save(chat_id: int, data: dict[str, Any]) -> dict[str, Any]:
    data = {**data, "updated": datetime.now(timezone.utc).isoformat()}
    p = _path(chat_id)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def set_mode(chat_id: int, mode: str, **extra: Any) -> dict[str, Any]:
    cur = load(chat_id)
    cur.update(extra)
    cur["mode"] = mode
    return save(chat_id, cur)
