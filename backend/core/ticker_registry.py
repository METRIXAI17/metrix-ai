"""Unique tickers. One ticker = one chain in the system."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALPH = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _dir() -> Path:
    from backend.config import DATA_DIR

    p = DATA_DIR / "tickers"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _code(seed: str, n: int = 5) -> str:
    h = hashlib.sha256(seed.encode("utf-8")).digest()
    out = []
    acc = int.from_bytes(h[:8], "big")
    for _ in range(n):
        out.append(ALPH[acc % len(ALPH)])
        acc //= len(ALPH)
    return "".join(out)


def mint_ticker(problem: str, *, prefix: str = "MX") -> str:
    """Mint MX-XXXXX. Retry on collision."""
    base = re.sub(r"\s+", " ", (problem or "contour").strip())[:180]
    for i in range(24):
        code = _code(f"{base}:{_now()}:{i}", 5)
        ticker = f"{prefix}-{code}"
        path = _dir() / f"{ticker}.json"
        if not path.exists():
            rec = {"ticker": ticker, "problem": base, "created": _now()}
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(path)
            return ticker
    # last-resort: longer code
    ticker = f"{prefix}-{_code(base + _now(), 8)}"
    path = _dir() / f"{ticker}.json"
    path.write_text(
        json.dumps({"ticker": ticker, "problem": base, "created": _now()}, ensure_ascii=False),
        encoding="utf-8",
    )
    return ticker


def bind_ticker(ticker: str, **extra: Any) -> dict[str, Any]:
    path = _dir() / f"{ticker}.json"
    rec: dict[str, Any] = {}
    if path.exists():
        try:
            rec = json.loads(path.read_text("utf-8"))
            if not isinstance(rec, dict):
                rec = {}
        except (OSError, json.JSONDecodeError):
            rec = {}
    rec.update(extra)
    rec["ticker"] = ticker
    rec["updated"] = _now()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return rec


def load_ticker(ticker: str) -> dict[str, Any] | None:
    path = _dir() / f"{(ticker or '').strip()}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text("utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None
