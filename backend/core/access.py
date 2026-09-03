"""One opaque access token. No PII at rest.

Subject is HMAC-SHA256(telegram_user_id or token), never the raw id.
Tribute is merchant of record. We persist entitlement, not a questionnaire.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR

ENT_DIR = DATA_DIR / "entitlements"
QUOTA_DIR = DATA_DIR / "quota"
# Free: two results, then Access. Access: monthly cap (not unlimited scrape).
FREE_RUNS = int(os.getenv("METRIX_FREE_RUNS", "2"))
ACCESS_RUNS_MONTH = int(os.getenv("METRIX_ACCESS_RUNS", "40"))
PAID_FEATURES = frozenset(
    {
        "strategy",
        "risk",
        "teammate",
        "artefact_panel",
        "offer_gen",
        "code_live",
        "two_leg_tape",
    }
)


def _secret() -> bytes:
    raw = (os.getenv("METRIX_TOKEN_SECRET") or os.getenv("TELEGRAM_BOT_TOKEN") or "dev-only").encode()
    return hashlib.sha256(raw).digest()


def subject_hash(raw: str | int) -> str:
    """One-way id for a Telegram user or any external subject. Not reversible."""
    msg = str(raw).encode()
    return hmac.new(_secret(), b"sub:" + msg, hashlib.sha256).hexdigest()


def token_hash(token: str) -> str:
    return hmac.new(_secret(), b"tok:" + token.encode(), hashlib.sha256).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text("utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _ent_path(key: str) -> Path:
    ENT_DIR.mkdir(parents=True, exist_ok=True)
    return ENT_DIR / f"{key[:64]}.json"


def mint_token(*, days: int = 31, sku: str = "access_month", bind_subject: str | None = None) -> dict[str, Any]:
    """Return the raw token once. Only the hash is stored."""
    raw = "mx_" + secrets.token_urlsafe(24)
    rec = {
        "token_hash": token_hash(raw),
        "sku": sku,
        "tier": "access",
        "issued": _iso(_now()),
        "expires": _iso(_now() + timedelta(days=days)),
        "subject_hash": bind_subject,
    }
    _save(_ent_path(rec["token_hash"]), rec)
    if bind_subject:
        _save(_ent_path("sub_" + bind_subject), {**rec, "bound": True})
    return {"token": raw, "expires": rec["expires"], "sku": sku}


def redeem(token: str, *, bind_subject: str | None = None) -> dict[str, Any]:
    th = token_hash((token or "").strip())
    rec = _load(_ent_path(th))
    if not rec:
        return {"ok": False, "error": "unknown_token"}
    if rec.get("expires") and rec["expires"] < _iso(_now()):
        return {"ok": False, "error": "expired"}
    if bind_subject:
        rec["subject_hash"] = bind_subject
        _save(_ent_path(th), rec)
        _save(_ent_path("sub_" + bind_subject), rec)
    return {"ok": True, "tier": rec.get("tier") or "access", "expires": rec.get("expires"), "sku": rec.get("sku")}


def entitle_subject(subject: str, *, days: int = 31, sku: str = "access_month") -> dict[str, Any]:
    rec = {
        "sku": sku,
        "tier": "access",
        "issued": _iso(_now()),
        "expires": _iso(_now() + timedelta(days=days)),
        "subject_hash": subject,
        "via": "tribute",
    }
    _save(_ent_path("sub_" + subject), rec)
    return rec


def is_entitled(subject: str | None) -> dict[str, Any]:
    if not subject:
        return {"ok": False, "tier": "free"}
    rec = _load(_ent_path("sub_" + subject))
    if not rec:
        return {"ok": False, "tier": "free"}
    exp = rec.get("expires") or ""
    if exp and exp < _iso(_now()):
        return {"ok": False, "tier": "expired", "expires": exp}
    return {"ok": True, "tier": rec.get("tier") or "access", "expires": exp, "sku": rec.get("sku")}


def _free_path(subject: str) -> Path:
    QUOTA_DIR.mkdir(parents=True, exist_ok=True)
    return QUOTA_DIR / f"free_{subject[:40]}.json"


def _month_path(subject: str) -> Path:
    QUOTA_DIR.mkdir(parents=True, exist_ok=True)
    return QUOTA_DIR / f"mo_{subject[:40]}_{_now().strftime('%Y-%m')}.json"


def quota_status(subject: str | None) -> dict[str, Any]:
    entitled = is_entitled(subject)
    if entitled.get("ok") and subject:
        used = int(_load(_month_path(subject)).get("used") or 0)
        remaining = max(0, ACCESS_RUNS_MONTH - used)
        return {
            **entitled,
            "used": used,
            "limit": ACCESS_RUNS_MONTH,
            "remaining": remaining,
            "gated": remaining <= 0,
            "unit": "result",
        }
    used = 0
    if subject:
        used = int(_load(_free_path(subject)).get("used") or 0)
    remaining = max(0, FREE_RUNS - used)
    return {
        "ok": False,
        "tier": "free",
        "used": used,
        "limit": FREE_RUNS,
        "remaining": remaining,
        "gated": remaining <= 0,
        "unit": "result",
    }


def consume(subject: str | None, feature: str) -> dict[str, Any]:
    """Free: 2 results then Access wall. Access: ACCESS_RUNS_MONTH results / calendar month."""
    st = quota_status(subject)
    if feature not in PAID_FEATURES:
        return {**st, "allowed": True, "feature": feature, "note": "catalog_free"}
    if not subject:
        return {
            **st,
            "allowed": False,
            "feature": feature,
            "wall": True,
            "cta": "Metrix Access",
            "sku": "access_month",
            "reason": "need_telegram_or_token",
        }
    if st.get("gated"):
        kind = "month_cap" if st.get("tier") == "access" else "free_done"
        return {
            **st,
            "allowed": False,
            "feature": feature,
            "wall": True,
            "cta": "Metrix Access",
            "sku": "access_month",
            "reason": kind,
        }
    p = _month_path(subject) if st.get("tier") == "access" and st.get("ok") else _free_path(subject)
    cur = _load(p)
    cur["used"] = int(cur.get("used") or 0) + 1
    _save(p, cur)
    st = quota_status(subject)
    return {**st, "allowed": True, "feature": feature}


def verify_tribute_signature(body: bytes, signature: str, api_key: str) -> bool:
    if not api_key or not signature:
        return False
    digest = hmac.new(api_key.encode(), body, hashlib.sha256)
    hexed = digest.hexdigest()
    got = (signature or "").strip()
    if got.lower().startswith("sha256="):
        got = got.split("=", 1)[1]
    if hmac.compare_digest(hexed, got) or hmac.compare_digest(hexed, got.lower()):
        return True
    # some Tribute builds send base64
    import base64

    b64 = base64.b64encode(digest.digest()).decode()
    return hmac.compare_digest(b64, got)


def apply_tribute_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Bind entitlement from a Tribute webhook. Never store name/phone/email."""
    event = str(payload.get("name") or payload.get("type") or payload.get("event") or "").lower()
    data = payload.get("payload") or payload.get("data") or payload
    if not isinstance(data, dict):
        data = payload
    telegram_id = (
        data.get("telegram_user_id")
        or data.get("telegramId")
        or (data.get("user") or {}).get("telegram_id")
        or (data.get("telegram_user") or {}).get("id")
    )
    period = data.get("period") or data.get("interval") or "month"
    days = 366 if "year" in str(period).lower() else 31
    sku = "access_year" if days > 60 else "access_month"
    if "cancel" in event:
        if telegram_id:
            rec = _load(_ent_path("sub_" + subject_hash(telegram_id)))
            rec["expires"] = _iso(_now())
            rec["cancelled"] = True
            _save(_ent_path("sub_" + subject_hash(telegram_id)), rec)
        return {"ok": True, "action": "cancel"}
    if telegram_id:
        sub = subject_hash(telegram_id)
        entitle_subject(sub, days=days, sku=sku)
        return {"ok": True, "action": "entitle", "bound": True, "sku": sku}
    minted = mint_token(days=days, sku=sku)
    return {"ok": True, "action": "mint_unbound", "sku": sku, "token": minted["token"]}
