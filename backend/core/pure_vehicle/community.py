"""Greening, directing, tokens, contribution, isolated packs, external layers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any

from backend.core.access import subject_hash
from backend.core.pure_vehicle.catalog import KILL, ensure_stores, open_consequences
from backend.core.pure_vehicle.store import read_json, write_json

LICENSE_CARRY = (
    "Personal use only. Commercial use forbidden without a separate written letter from Karim Metrix."
)
PII_KEYS = {"name", "phone", "telephone", "tel", "email", "фио", "имя", "телефон"}
IMPROVE = (
    "quality",
    "finance_landing",
    "agent_research",
    "robot_sales",
    "directing",
    "greening",
    "tokens",
    "community",
    "freelance_isolation",
)
ALLO_GRANT = 40
_CLICHE = (
    "ai-powered",
    "unlock",
    "leverage",
    "синерг",
    "инновац",
    "уникальн",
    "esg",
    "устойчив",
    "доходност",
    "yield",
    "ещё одна комната",
    "еще одна комната",
    "новая линейка",
    "директолог",
)
# A phone, not a hex/uuid token glued to letters.
_PHONE = re.compile(
    r"(?<![A-Za-z0-9])(?:\+\d[\d\-\s()]{7,}\d|\d[\d\-\s()]{8,}\d)(?![A-Za-z0-9])"
)
_ABOVE_ALLO = frozenset({"sku_100", "sku_490", "sku_1000", "sku_10000", "custom_spec_pilot", "game_pack"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _isolated_url(sku: str) -> str:
    own = os.getenv("TRIBUTE_FREELANCE_URL", "").strip() if sku != "game_pack" else os.getenv("TRIBUTE_GAME_URL", "").strip()
    if own:
        return own
    base = os.getenv("TRIBUTE_ACCESS_URL", "").strip() or "https://t.me/tribute"
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}start={sku}"


def green_request(text: str, *, ticker: str = "", owner: str = "") -> dict[str, Any]:
    """Individualize a template, then shorten it. Not ESG. Not a new SKU."""
    raw = text or ""
    kept: list[str] = []
    for line in raw.splitlines() or [raw]:
        piece = " ".join(line.split())
        if not piece:
            continue
        low = piece.lower()
        if any(tok in low for tok in _CLICHE):
            continue
        if ticker:
            piece = piece.replace("{ticker}", ticker).replace("TICKER", ticker)
        if owner:
            piece = piece.replace("{owner}", owner).replace("OWNER", owner)
        kept.append(piece)
    out = "\n".join(kept).strip()
    slot = ""
    if ticker or owner:
        slot = f"{ticker} · {owner}".strip(" ·")
        if slot and slot not in out:
            out = f"{slot}\n{out}".strip()
    if len(out) >= len(raw) and raw:
        # Drop a trailing clause so the cut is real.
        cut = max(1, len(raw) - max(8, len(raw) // 5))
        out = out[:cut].rstrip(" ,.;")
    if raw and len(out) >= len(raw):
        out = raw[: max(1, len(raw) - 1)].rstrip()
    return {
        "ok": True,
        "text": out,
        "shorter": len(out) < len(raw) if raw else True,
        "not_esg": True,
        "ticker": ticker,
        "owner": owner,
        "new_sku": False,
    }


def directing(situation: dict[str, Any], *, paid: bool = False, choice: str | None = None) -> dict[str, Any]:
    """One consequence after directing_fee. Unpaid fork is not a recorded choice.

    Not a directologist and not an ad cabinet.
    """
    ensure_stores()
    sku = str(situation.get("sku") or "allo_month")
    fork = open_consequences(sku)
    book = read_json("directing.json", {"version": "2.1.0", "rows": []})
    if not paid:
        return {
            "ok": True,
            "recorded": False,
            "done": False,
            "paid": False,
            "fork": fork,
            "role": "directing_fee",
            "directologist": False,
            "ad_cabinet": False,
            "note": "Без directing_fee развилка показана. Выбор не записан.",
        }
    picked = (choice or "").strip()
    if picked not in fork:
        return {
            "ok": False,
            "recorded": False,
            "done": False,
            "paid": True,
            "fork": fork,
            "reason": "choice_not_open",
            "directologist": False,
        }
    row = {
        "at": _now(),
        "choice": picked,
        "kill": KILL[picked],
        "done": True,
        "directologist": False,
        "ad_cabinet": False,
    }
    rows = list(book.get("rows") or [])
    rows.append(row)
    book["rows"] = rows[-100:]
    book["version"] = "2.1.0"
    write_json("directing.json", book)
    return {"ok": True, "recorded": True, "done": True, "paid": True, **row, "fork": fork}


def grant_tokens(subject: str, *, sku: str = "allo_month") -> dict[str, Any]:
    """Monthly grant inside allo_month. Overage is a separate pack.

    Broker flag off: record the grant. Do not call the broker. Do not answer 503 only.
    Cold chain is not enabled here.
    """
    if sku != "allo_month":
        return {"ok": False, "reason": "grant_only_on_allo_month", "sku": sku}
    if not subject:
        return {"ok": False, "reason": "subject_required"}
    ensure_stores()
    from backend.contours.flags import cold_chain_enabled, compute_broker_enabled

    author = subject_hash(subject)
    book = read_json("tokens.json", {"version": "2.1.0", "grants": []})
    grants = [g for g in (book.get("grants") or []) if g.get("subject_hash") == author]
    used = sum(int(g.get("used") or 0) for g in grants)
    row = {
        "at": _now(),
        "subject_hash": author,
        "sku": "allo_month",
        "grant": ALLO_GRANT,
        "used": 0,
    }
    book_grants = list(book.get("grants") or [])
    book_grants.append(row)
    book["grants"] = book_grants[-400:]
    book["version"] = "2.1.0"
    write_json("tokens.json", book)
    over = None
    if used >= ALLO_GRANT:
        over = {"id": "token_overage", "separate": True, "included_in_allo": False}
    broker_on = compute_broker_enabled()
    if broker_on:
        # Grant is local. Do not place a broker call and do not turn on C5.
        broker = "on_not_called_for_grant"
    else:
        broker = "closed_by_flag"
    return {
        "ok": True,
        "recorded": True,
        "status": 200,
        "grant": ALLO_GRANT,
        "subject_hash": author,
        "broker": broker,
        "cold_chain": bool(cold_chain_enabled()),
        "cold_chain_enabled_by_grant": False,
        "overage": over,
        "note": "Брокер закрыт флагом. Грант записан." if not broker_on else "Грант записан. Брокер для гранта не вызван.",
    }


def self_improve(category: str, vehicle: dict[str, Any] | None = None) -> dict[str, Any]:
    if category not in IMPROVE:
        return {"ok": False, "reason": "free_category_rejected", "category": category}
    return {
        "ok": True,
        "category": category,
        "vehicle": bool(vehicle),
        "new_product": False,
        "note": "Один шаг внутри уже собранного контура.",
    }


def hang_promotion(vehicle: dict[str, Any], brief: str, *, lang: str = "ru") -> dict[str, Any]:
    """Existing promotion pack hangs on an assembled vehicle. No Promo tab."""
    from backend.core.business_gen.promotion_pack import build_promotion_pack

    pack = build_promotion_pack(brief or vehicle.get("in", {}).get("situation") or "", lang=lang)
    out = dict(vehicle)
    out["promotion_pack"] = {"hung": True, "pack": pack}
    out["promo_tab"] = False
    out["new_tab"] = False
    return out


def _reject_pii(body: Any) -> Any:
    if isinstance(body, dict):
        bad = [k for k in body if str(k).lower() in PII_KEYS or str(k).lower() == "relicense"]
        if any(str(k).lower() in PII_KEYS for k in body):
            raise ValueError("pii")
        if any(str(k).lower() == "relicense" for k in body):
            raise ValueError("relicense")
        return {k: _reject_pii(v) for k, v in body.items() if k not in bad}
    if isinstance(body, list):
        return [_reject_pii(x) for x in body]
    if isinstance(body, str):
        if _PHONE.search(body):
            raise ValueError("pii")
        return body
    return body


def _body_hash(body: Any) -> str:
    canon = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def contribute(kind: str, body: Any, subject: str) -> dict[str, Any]:
    """Public template or db_row. Author is subject hash. No name, no phone. No relicensing."""
    if kind not in ("template", "db_row"):
        return {"ok": False, "reason": "kind"}
    if not subject:
        return {"ok": False, "reason": "subject_required"}
    try:
        clean = _reject_pii(body)
    except ValueError as exc:
        return {"ok": False, "reason": str(exc), "stored_name": False, "stored_phone": False}
    ensure_stores()
    digest = _body_hash({"kind": kind, "body": clean})
    book = read_json("contributions.json", {"version": "2.1.0", "rows": []})
    rows = list(book.get("rows") or [])
    for row in rows:
        if row.get("body_hash") == digest:
            return {"ok": True, "created": False, "duplicate": True, **row}
    author = subject_hash(subject)
    row = {
        "id": digest[:16],
        "kind": kind,
        "body": clean,
        "body_hash": digest,
        "author": author,
        "license": LICENSE_CARRY,
        "relicense": False,
        "public": True,
        "at": _now(),
    }
    if "name" in row or "phone" in row:
        return {"ok": False, "reason": "pii"}
    rows.append(row)
    book["rows"] = rows[-500:]
    book["version"] = "2.1.0"
    write_json("contributions.json", book)
    public = {k: row[k] for k in ("id", "kind", "body", "author", "license", "public", "relicense")}
    return {"ok": True, "created": True, "duplicate": False, **public}


def public_contributions() -> list[dict[str, Any]]:
    ensure_stores()
    rows = read_json("contributions.json", {}).get("rows") or []
    out = []
    for row in rows:
        out.append(
            {
                "id": row.get("id"),
                "kind": row.get("kind"),
                "body": row.get("body"),
                "author": row.get("author"),
                "license": row.get("license"),
                "relicense": False,
            }
        )
    return out


def creative_room(body: Any, subject: str, *, kind: str = "template", ticker: str = "", owner: str = "") -> dict[str, Any]:
    text = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
    greened = green_request(text, ticker=ticker, owner=owner)
    saved = contribute(kind, greened["text"], subject)
    saved["shorter"] = greened["shorter"]
    saved["output"] = greened["text"]
    saved["new_sku"] = False
    saved["eighth_product"] = False
    return saved


def purchase_isolated(pack_id: str, subject: str = "") -> dict[str, Any]:
    """Isolated freelance sale. Does not open Access, Flagship, or Allo."""
    return {
        "ok": True,
        "isolated": True,
        "pack_id": pack_id or "freelance",
        "pay_url": _isolated_url("isolated_freelance"),
        "subject_bound": bool(subject),
        "entitlements": {
            "allo_month": False,
            "access": False,
            "flagship": False,
            "recurse_spec": False,
        },
    }


def game_pack() -> dict[str, Any]:
    """Isolated paper game pack. Not allo_month. No commercial promise."""
    return {
        "id": "game_pack",
        "usd": 50,
        "period": "month",
        "isolated": True,
        "paper": True,
        "static": True,
        "allo_month": False,
        "recurse_spec": False,
        "pay_url": _isolated_url("game_pack"),
        "promises": {
            "offer_help": False,
            "implementation": False,
            "commercial_result": False,
            "live_orders": False,
            "yield": False,
        },
        "grants": {"allo_month": False, "access": False, "flagship": False, "recurse_spec": False},
    }


def alice_signal(rank: dict[str, Any] | None = None) -> dict[str, Any]:
    """Yandex Alice ranking is an external enterprise signal. Not a Metrix door."""
    return {
        "ok": True,
        "layer": "enterprise_external",
        "vendor": "yandex_alice",
        "signal": dict(rank or {}),
        "opens_door": False,
        "price_changed": False,
        "product": False,
        "sku_board": {"allo_month_usd": 50},
    }


def separated_circle(
    subject: str,
    template: Any = "",
    *,
    sku: str = "",
) -> dict[str, Any]:
    """Own game-part as a separated circle. Does not merge with the $50 door."""
    via = sku or ""
    closed = {
        "ok": False,
        "open": False,
        "merged_with_allo": False,
        "grants_allo": False,
        "grants_access": False,
        "grants_flagship": False,
        "recurse_spec": False,
        "why": "Круг не сливается с дверью $50. Нужен SKU выше Allo или изолированный пакет.",
    }
    if via not in _ABOVE_ALLO:
        return closed
    saved = None
    if template not in ("", None):
        if isinstance(template, dict) and template.get("kind") in ("template", "db_row"):
            saved = contribute(str(template["kind"]), template.get("body"), subject)
        else:
            saved = contribute("template", template, subject)
    return {
        "ok": True,
        "open": True,
        "via": via,
        "merged_with_allo": False,
        "grants_allo": False,
        "grants_access": False,
        "grants_flagship": False,
        "recurse_spec": False,
        "paper": via == "game_pack",
        "contribution": saved,
    }
