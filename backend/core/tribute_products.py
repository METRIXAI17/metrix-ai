"""Create a Tribute (or local) product named {ticker} · {solution}."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.core.pricing_lanes import sku_of


def _dir() -> Path:
    from backend.config import DATA_DIR

    p = DATA_DIR / "tribute_products"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_product(
    *,
    ticker: str,
    solution: str,
    sku_id: str = "sku_490",
    problem: str = "",
) -> dict[str, Any]:
    sku = sku_of(sku_id)
    name = f"{ticker} · {(solution or problem or 'overlay')[:72]}"
    rec = {
        "ticker": ticker,
        "name": name,
        "solution": solution,
        "problem": problem,
        "sku": sku_id,
        "usd": sku.get("usd"),
        "rub": sku.get("rub"),
        "file": bool(sku.get("file")),
        "pay_url": sku.get("pay_url") or "",
        "created": _now(),
        "provider": "tribute",
        "remote_id": None,
        "note": "Tribute merchant of record. Local registry always written. Remote create is best-effort.",
    }
    rec.update(_try_remote(rec))
    path = _dir() / f"{ticker}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return rec


def _try_remote(rec: dict[str, Any]) -> dict[str, Any]:
    import os

    key = (os.getenv("TRIBUTE_API_KEY") or "").strip()
    if not key:
        return {"remote": False, "remote_reason": "no_api_key"}
    try:
        import httpx

        r = httpx.post(
            "https://tribute.tg/api/v1/merchant/products",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "name": rec["name"],
                "price": rec.get("usd") or rec.get("rub"),
                "currency": "USD" if rec.get("usd") else "RUB",
                "description": rec.get("solution") or rec.get("problem") or rec["ticker"],
                "external_id": rec["ticker"],
            },
            timeout=8.0,
        )
        if r.status_code >= 400:
            return {"remote": False, "remote_reason": f"http_{r.status_code}"}
        data = r.json() if r.content else {}
        return {
            "remote": True,
            "remote_id": (data.get("id") if isinstance(data, dict) else None),
            "remote_payload": data if isinstance(data, dict) else {"raw": str(data)[:200]},
        }
    except Exception as exc:  # noqa: BLE001
        return {"remote": False, "remote_reason": type(exc).__name__}


def load_product(ticker: str) -> dict[str, Any] | None:
    path = _dir() / f"{(ticker or '').strip()}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text("utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None
