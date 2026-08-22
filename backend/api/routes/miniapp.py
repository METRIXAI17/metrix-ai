"""Telegram Mini App + task-reader APIs."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any
from urllib.parse import parse_qsl

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from backend.core.functions import (
    run_creative_assistant,
    run_digital_mockup,
    run_solution_logger,
)
from backend.core.miniapp_catalog import bump_hit, catalog_payload
from backend.core.order_terminal import mine_orders
from backend.core.promo_lite import run_promo_lite
from backend.core.task_reader import assemble_query, read_task
from backend.security.hardening import sanitize_text

router = APIRouter(prefix="/miniapp", tags=["miniapp"])


def _bot_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def validate_init_data(init_data: str, max_age_sec: int = 86400) -> dict[str, Any]:
    """Validate Telegram WebApp initData. If no bot token, accept in DEBUG-ish mode."""
    token = _bot_token()
    if not init_data:
        if not token:
            return {"ok": True, "user": None, "skipped": "no_init_data"}
        raise HTTPException(401, "init_data required")
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    got_hash = parsed.pop("hash", "")
    if not token:
        return {"ok": True, "user": _user(parsed), "skipped": "no_bot_token"}
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, got_hash):
        raise HTTPException(401, "bad init_data hash")
    auth_date = int(parsed.get("auth_date") or 0)
    if auth_date and (time.time() - auth_date) > max_age_sec:
        raise HTTPException(401, "init_data expired")
    return {"ok": True, "user": _user(parsed)}


def _user(parsed: dict[str, str]) -> dict[str, Any] | None:
    raw = parsed.get("user")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


class InitHeaders:
    pass


def _auth(x_telegram_init_data: str | None) -> dict[str, Any]:
    return validate_init_data(x_telegram_init_data or "")


class BriefBody(BaseModel):
    brief: str = Field(..., min_length=8)
    lang: str = "ru"
    industry: str = ""
    surface_hint: str = ""
    kind: str = ""


class LoggerBody(BaseModel):
    thesis: str = Field(..., min_length=4)
    market: str = ""
    side: str = ""
    result: str = ""
    r_multiple: float | None = None
    notes: str = ""
    journal: list[dict] = Field(default_factory=list)
    lang: str = "ru"


class MockupBody(BaseModel):
    portrait: str = Field(..., min_length=8)
    offer: str = ""
    lang: str = "ru"


class InvoiceBody(BaseModel):
    sku: str
    title: str = ""
    pay_in: str = "yookassa"  # yookassa | stars
    lang: str = "ru"


@router.get("/catalog")
def catalog(lang: str = "ru") -> dict[str, Any]:
    payload = catalog_payload(lang)
    from backend.config import TELEGRAM_PAYMENTS

    payload["payments"] = bool(TELEGRAM_PAYMENTS)
    payload["payments_note"] = (
        "free_launch" if not TELEGRAM_PAYMENTS else "invoices_on"
    )
    return {"ok": True, **payload}


@router.post("/hit/{item_id}")
def hit(item_id: str) -> dict[str, Any]:
    safe = sanitize_text(item_id, max_len=64)
    return {"ok": True, "hits": bump_hit(safe)}


@router.post("/read")
def read_brief(
    body: BriefBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    _auth(x_telegram_init_data)
    brief = sanitize_text(body.brief, max_len=12_000)
    return {"ok": True, **read_task(brief, lang=body.lang)}


@router.post("/assemble")
def assemble(
    body: BriefBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    _auth(x_telegram_init_data)
    brief = sanitize_text(body.brief, max_len=12_000)
    packed = assemble_query(
        brief,
        lang=body.lang,
        industry_hint=body.industry,
        surface_hint=body.surface_hint,
    )
    bump_hit("request_work")
    return {"ok": True, **packed}


@router.post("/request")
def work_by_request(
    body: BriefBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    """Работа по запросу — assemble + existing process pipeline if possible."""
    _auth(x_telegram_init_data)
    brief = sanitize_text(body.brief, max_len=12_000)
    packed = assemble_query(
        brief,
        lang=body.lang,
        industry_hint=body.industry,
        surface_hint=body.surface_hint or "consult_qa",
    )
    process_out: dict[str, Any] = {}
    if len(brief) >= 20:
        try:
            from backend.core.request_pipeline import process_client_request

            process_out = process_client_request(
                {
                    "industry": body.industry or "expert-services",
                    "business": brief,
                    "track": "all",
                    "lang": body.lang,
                }
            )
        except Exception as exc:  # noqa: BLE001
            process_out = {"ok": False, "error": str(exc)[:240]}
    bump_hit("request_work")
    return {
        "ok": True,
        "surface": "работа по запросу",
        "assembly": packed,
        "process": process_out,
        "mode": packed.get("mode"),
        "end_readings": packed.get("end_readings"),
    }


@router.post("/creative")
def creative(body: BriefBody) -> dict[str, Any]:
    brief = sanitize_text(body.brief, max_len=8_000)
    bump_hit("creative_assistant")
    return {"ok": True, **run_creative_assistant(brief, lang=body.lang, kind=body.kind or "ideas")}


@router.post("/logger")
def logger(body: LoggerBody) -> dict[str, Any]:
    bump_hit("solution_logger")
    return {
        "ok": True,
        **run_solution_logger(
            thesis=sanitize_text(body.thesis, max_len=4_000),
            market=body.market,
            side=body.side,
            result=body.result,
            r_multiple=body.r_multiple,
            notes=sanitize_text(body.notes, max_len=4_000),
            journal=body.journal,
            lang=body.lang,
        ),
    }


@router.post("/mockup")
def mockup(body: MockupBody) -> dict[str, Any]:
    bump_hit("digital_mockup")
    return {
        "ok": True,
        **run_digital_mockup(
            sanitize_text(body.portrait, max_len=8_000),
            lang=body.lang,
            offer=sanitize_text(body.offer, max_len=4_000),
        ),
    }


@router.post("/promo")
def promo(body: BriefBody) -> dict[str, Any]:
    brief = sanitize_text(body.brief, max_len=8_000)
    kind = body.kind or "all"
    bump_hit({"cards": "promo_cards", "reels": "promo_reels", "prompts": "promo_prompts"}.get(kind, "promo_cards"))
    return {"ok": True, **run_promo_lite(brief, kind=kind, industry_id=body.industry or "content-monetize", lang=body.lang)}


@router.post("/terminal")
def terminal(body: BriefBody) -> dict[str, Any]:
    brief = sanitize_text(body.brief, max_len=8_000)
    bump_hit("terminal_mine")
    return {"ok": True, **mine_orders(brief, lang=body.lang)}


@router.post("/invoice")
async def invoice(body: InvoiceBody, request: Request) -> dict[str, Any]:
    """Create Telegram invoice link (Stars or YooKassa). Off until TELEGRAM_PAYMENTS=1."""
    from backend.config import TELEGRAM_PAYMENTS
    from backend.monetization.tg_scheme import SKUS

    if not TELEGRAM_PAYMENTS:
        meta = SKUS.get(body.sku) or {}
        return {
            "ok": False,
            "disabled": True,
            "sku": body.sku,
            "price": meta,
            "hint": "Оплата выключена на старте. Прогоны бесплатны. Tribute/ЮKassa/Stars — следующим шагом.",
        }

    sku = body.sku
    meta = SKUS.get(sku)
    if not meta:
        raise HTTPException(400, f"unknown sku {sku}")
    token = _bot_token()
    if not token:
        return {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN unset",
            "sku": sku,
            "price": meta,
            "hint": "Set token to mint live invoices. Mini App can still queue the SKU.",
        }
    title = body.title or meta["name"]
    pay_in = (body.pay_in or "yookassa").lower()
    import httpx

    if pay_in == "stars":
        if not meta.get("stars"):
            raise HTTPException(400, "sku not sold in Stars (too large — use card/wire)")
        payload = {
            "title": title[:32],
            "description": meta["name"][:255],
            "payload": sku,
            "currency": "XTR",
            "prices": [{"label": title[:32], "amount": int(meta["stars"])}],
        }
    else:
        provider = os.getenv("TELEGRAM_PROVIDER_TOKEN", "").strip()
        if not provider:
            return {
                "ok": False,
                "error": "TELEGRAM_PROVIDER_TOKEN unset (YooKassa)",
                "sku": sku,
                "price": meta,
                "rf_cards": True,
                "hint": "ЮKassa provider token from BotFather → Payments. Then RF cards work.",
            }
        payload = {
            "title": title[:32],
            "description": meta["name"][:255],
            "payload": sku,
            "provider_token": provider,
            "currency": "RUB",
            "prices": [{"label": title[:32], "amount": int(meta["rub"]) * 100}],
        }
    payload["need_name"] = False
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"https://api.telegram.org/bot{token}/createInvoiceLink",
            json=payload,
        )
        data = r.json()
    if not data.get("ok"):
        return {"ok": False, "telegram": data, "sku": sku}
    return {"ok": True, "invoice_url": data.get("result"), "sku": sku, "pay_in": pay_in, "price": meta}


@router.get("/scheme")
def scheme() -> dict[str, Any]:
    from backend.monetization.tg_scheme import scheme_payload

    return {"ok": True, **scheme_payload()}
