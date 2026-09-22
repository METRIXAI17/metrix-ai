"""Owner admin: tickers, chains, tribute products. Gate: METRIX_OPS_KEY / METRIX_ADMIN_KEY."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException

from backend.core.circle_system.chain_store import list_chain_ids, load_chain
from backend.core.ticker_registry import load_ticker
from backend.core.tribute_products import load_product

router = APIRouter(prefix="/admin", tags=["admin"])


def _authorized(x_metrix_ops_key: str | None) -> bool:
    key = (os.getenv("METRIX_ADMIN_KEY") or os.getenv("METRIX_OPS_KEY") or "").strip()
    if not key:
        return True
    return (x_metrix_ops_key or "").strip() == key


@router.get("/overview")
def overview(x_metrix_ops_key: str | None = Header(default=None)) -> dict[str, Any]:
    if not _authorized(x_metrix_ops_key):
        raise HTTPException(401, "admin key")
    ids = list_chain_ids(limit=40)
    chains = []
    for cid in ids:
        rec = load_chain(cid) or load_ticker(cid) or {}
        chains.append(
            {
                "ticker": rec.get("ticker") or cid,
                "problem": (rec.get("problem") or "")[:160],
                "solution": (rec.get("solution") or "")[:160],
                "sku": rec.get("sku") or rec.get("recommended_sku") or "",
                "updated": rec.get("updated") or rec.get("created") or "",
                "answers": len(rec.get("answers") or {}),
                "file": bool(rec.get("paid_file") or rec.get("file")),
            }
        )
        tribute = load_product(cid)
        if tribute:
            chains[-1]["tribute"] = tribute.get("name")
    return {
        "ok": True,
        "module": "AdminOverview",
        "count": len(chains),
        "chains": chains,
        "note": "Первый срез админки: цепочки и тикеры. Eval и касса — следующие слои.",
    }


@router.get("/specs")
def specs_index(x_metrix_ops_key: str | None = Header(default=None)) -> dict[str, Any]:
    from backend.core.owner_specs import owner_specs_open

    if not (_authorized(x_metrix_ops_key) or owner_specs_open()):
        raise HTTPException(401, "admin key")
    ids = list_chain_ids(limit=40)
    rows = []
    for cid in ids:
        rec = load_chain(cid) or {}
        custom = rec.get("custom_spec") or {}
        paid = rec.get("paid_file") or {}
        if not custom and not paid and not rec.get("variants"):
            continue
        rows.append(
            {
                "ticker": rec.get("ticker") or cid,
                "problem": rec.get("problem") or "",
                "solution": rec.get("solution") or "",
                "cycle_section": rec.get("cycle_section") or "",
                "question_level": rec.get("question_level") or "",
                "variants": rec.get("variants") or [],
                "custom_spec": bool(custom),
                "recursive_file": bool(paid),
                "paths": (custom.get("paths") or {}) | ((paid.get("paths") or {}) if isinstance(paid, dict) else {}),
            }
        )
    return {"ok": True, "open": True, "count": len(rows), "specs": rows}
