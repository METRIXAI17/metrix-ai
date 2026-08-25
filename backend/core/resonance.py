"""Value miner: artifacts that resonated.

Not pageviews. Not «engagement». A hit is a person marking an artifact
as зашло / почти / мимо — that becomes the paid highway.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR

STORE = DATA_DIR / "resonance"
HITS = STORE / "hits.json"
EVENTS = STORE / "events.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_hits() -> dict[str, Any]:
    if not HITS.exists():
        return {"artifacts": {}, "verdicts": {"hit": 0, "almost": 0, "miss": 0}}
    try:
        return json.loads(HITS.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"artifacts": {}, "verdicts": {"hit": 0, "almost": 0, "miss": 0}}


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def remember(artifact: dict[str, Any]) -> dict[str, Any]:
    """Persist a produced artifact so later resonance can attach to it."""
    STORE.mkdir(parents=True, exist_ok=True)
    aid = artifact.get("id") or new_id()
    artifact = {**artifact, "id": aid, "saved_at": artifact.get("saved_at") or _now()}
    path = STORE / f"{aid}.json"
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    return artifact


def load(artifact_id: str) -> dict[str, Any] | None:
    path = STORE / f"{artifact_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def resonate(
    artifact_id: str,
    verdict: str,
    *,
    note: str = "",
    who: str = "",
) -> dict[str, Any]:
    v = (verdict or "").strip().lower()
    if v in ("зашло", "yes", "like", "ok"):
        v = "hit"
    elif v in ("почти", "close", "almost"):
        v = "almost"
    elif v in ("мимо", "no", "miss"):
        v = "miss"
    if v not in ("hit", "almost", "miss"):
        v = "almost"

    hits = _load_hits()
    hits.setdefault("verdicts", {"hit": 0, "almost": 0, "miss": 0})
    hits["verdicts"][v] = int(hits["verdicts"].get(v) or 0) + 1
    row = hits.setdefault("artifacts", {}).setdefault(
        artifact_id, {"hit": 0, "almost": 0, "miss": 0, "title": ""}
    )
    row[v] = int(row.get(v) or 0) + 1
    art = load(artifact_id) or {}
    if art.get("title"):
        row["title"] = art["title"]
    STORE.mkdir(parents=True, exist_ok=True)
    HITS.write_text(json.dumps(hits, ensure_ascii=False, indent=2), encoding="utf-8")

    event = {
        "ts": _now(),
        "artifact_id": artifact_id,
        "verdict": v,
        "note": (note or "")[:500],
        "who": (who or "")[:80],
        "kind": art.get("kind"),
        "title": art.get("title"),
    }
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    paid = None
    if v == "hit":
        paid = {
            "sku": "pilot_14",
            "title": "Пилот: посадка этого артефакта",
            "why": "Оплата за внедрение того, что уже зашло — не за ещё один разговор.",
        }
    elif v == "almost":
        paid = {
            "sku": "request_deep",
            "title": "Дожать артефакт",
            "why": "Скажите, чего не хватает — соберём вторую версию под ваш контур.",
        }
    else:
        paid = {
            "sku": None,
            "title": "Другая дверь",
            "why": "Мимо — нормально. Возьмём стратегию, агента или другой угол.",
        }

    return {
        "ok": True,
        "verdict": v,
        "artifact": art or {"id": artifact_id},
        "counts": row,
        "global": hits["verdicts"],
        "paid_path": paid,
        "miner": "resonance",
    }


def top_resonated(limit: int = 8) -> list[dict[str, Any]]:
    hits = _load_hits()
    rows = []
    for aid, row in (hits.get("artifacts") or {}).items():
        rows.append({"id": aid, **row, "score": int(row.get("hit") or 0) * 2 + int(row.get("almost") or 0)})
    rows.sort(key=lambda r: -r["score"])
    return rows[:limit]
