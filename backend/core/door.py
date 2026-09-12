"""Metrix Door — one pass, many rooms.

Friendship rule: a friend does not ask for a passport twice.
A 6-character code from the first sentence opens Store, CraftShift, bot, site.
No account. No phone. Code is the object you keep.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR
from backend.core.voice import clip

DIR = DATA_DIR / "doors"
ALPH = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def mint(brief: str = "", *, room: str = "talk") -> dict[str, Any]:
    DIR.mkdir(parents=True, exist_ok=True)
    code = "".join(secrets.choice(ALPH) for _ in range(6))
    while (DIR / f"{code}.json").exists():
        code = "".join(secrets.choice(ALPH) for _ in range(6))
    rec = {
        "code": code,
        "brief": clip(brief, 800),
        "room": room,
        "rooms": [room],
        "created": _now(),
        "updated": _now(),
        "artifact_ids": [],
        "think_more": 0,
    }
    _save(rec)
    return rec


def load(code: str) -> dict[str, Any] | None:
    c = _norm(code)
    if not c:
        return None
    p = DIR / f"{c}.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def bind(code: str, *, brief: str = "", room: str = "", artifact_id: str = "") -> dict[str, Any]:
    rec = load(code) or mint(brief, room=room or "talk")
    if brief:
        rec["brief"] = clip(brief, 800)
    if room:
        rec["room"] = room
        rooms = list(rec.get("rooms") or [])
        if room not in rooms:
            rooms.append(room)
        rec["rooms"] = rooms
    if artifact_id:
        ids = list(rec.get("artifact_ids") or [])
        if artifact_id not in ids:
            ids.append(artifact_id)
        rec["artifact_ids"] = ids[-24:]
    rec["updated"] = _now()
    rec["code"] = rec.get("code") or _norm(code)
    _save(rec)
    return rec


def bump_think(code: str) -> dict[str, Any] | None:
    rec = load(code)
    if not rec:
        return None
    rec["think_more"] = int(rec.get("think_more") or 0) + 1
    rec["updated"] = _now()
    _save(rec)
    return rec


def fingerprint(brief: str) -> str:
    h = hashlib.sha256((brief or "").encode("utf-8")).hexdigest()[:8]
    return h.upper()


def public_view(rec: dict[str, Any] | None) -> dict[str, Any]:
    if not rec:
        return {"ok": False, "reason": "no_door"}
    return {
        "ok": True,
        "code": rec.get("code"),
        "room": rec.get("room") or "talk",
        "rooms": list(rec.get("rooms") or []),
        "brief": rec.get("brief") or "",
        "think_more": int(rec.get("think_more") or 0),
        "one_liner": f"Дверь {rec.get('code')}. Друг не спрашивает паспорт дважды.",
    }


def _norm(code: str) -> str:
    c = (code or "").strip().upper().replace(" ", "")
    c = c.replace("О", "0").replace("I", "1").replace("L", "1")
    if len(c) != 6:
        return ""
    if any(ch not in ALPH for ch in c):
        return ""
    return c


def _save(rec: dict[str, Any]) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    code = rec.get("code") or ""
    if not code:
        return
    path = DIR / f"{code}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
