"""GTM & partner module (C1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.contours import store

TYPES = ("integrator", "directologist", "performance_agency", "logistics")
GTM_DIR = Path(__file__).resolve().parent / "gtm"


def upsert_partner(
    tenant_id: str,
    *,
    name: str,
    ptype: str,
    contact: str = "",
) -> dict[str, Any]:
    if ptype not in TYPES:
        return {"ok": False, "error": "bad_type", "allowed": TYPES}
    row = store.upsert(
        tenant_id,
        "partners",
        {
            "id": store.new_id("pt_"),
            "name": name,
            "type": ptype,
            "contact": contact[:120],
        },
    )
    return {"ok": True, "partner": row}


def referral(tenant_id: str, partner_id: str, project_id: str) -> dict[str, Any]:
    row = store.upsert(
        tenant_id,
        "referrals",
        {
            "id": store.new_id("rf_"),
            "partner_id": partner_id,
            "project_id": project_id,
            "contour": "C1",
        },
    )
    return row


def templates() -> dict[str, str]:
    out: dict[str, str] = {}
    if GTM_DIR.exists():
        for p in GTM_DIR.glob("*.md"):
            out[p.stem] = p.read_text(encoding="utf-8")
    return out


def checklist(tenant_id: str, partner_id: str, item: str, done: bool = True) -> dict[str, Any]:
    cid = f"ck_{partner_id}"
    cur = store.get(tenant_id, "checklists", cid) or {"id": cid, "partner_id": partner_id, "items": {}}
    items = dict(cur.get("items") or {})
    items[item] = {"done": bool(done), "ts": store.now_iso()}
    cur["items"] = items
    return store.upsert(tenant_id, "checklists", cur)
