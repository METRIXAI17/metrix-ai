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
from backend.core.access import (
    apply_tribute_event,
    consume,
    quota_status,
    redeem,
    subject_hash,
    verify_tribute_signature,
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


def _try_auth(x_telegram_init_data: str | None) -> dict[str, Any]:
    try:
        return validate_init_data(x_telegram_init_data or "")
    except HTTPException:
        return {"ok": False, "user": None}


def _subject(auth: dict[str, Any]) -> str | None:
    user = auth.get("user") or {}
    uid = user.get("id") if isinstance(user, dict) else None
    return subject_hash(uid) if uid else None


def _gate(subject: str | None, feature: str) -> dict[str, Any]:
    return consume(subject, feature)


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


class DemoBody(BaseModel):
    brief: str = Field(default="", min_length=0)
    hint: str = ""
    strategy: str = ""
    niche: str = ""
    lang: str = "ru"


class ResonateBody(BaseModel):
    artifact_id: str
    verdict: str
    note: str = ""
    who: str = ""


class ComfortBody(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[dict] = Field(default_factory=list)
    brief: str = ""
    lang: str = "ru"


class MakingBody(BaseModel):
    brief: str = Field(default="", min_length=0)
    extra: str = ""
    lang: str = "ru"
    closer: dict | None = None


def _wall(gate: dict[str, Any]) -> dict[str, Any]:
    from backend.config import HUMAN_CONTACT_URL, TRIBUTE_ACCESS_URL
    from backend.core.product_180 import PRICING

    return {
        "ok": False,
        "wall": True,
        "cta": "Metrix Access · 3 290 ₽ / месяц · 40 результатов",
        "tribute": TRIBUTE_ACCESS_URL,
        "human": HUMAN_CONTACT_URL,
        "pricing": PRICING["access"],
        **gate,
    }


@router.get("/catalog")
def catalog(
    lang: str = "ru",
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    payload = catalog_payload(lang)
    from backend.config import HUMAN_CONTACT_URL, TELEGRAM_PAYMENTS, TRIBUTE_ACCESS_URL, TRIBUTE_CUSTOM_URL

    payload["payments"] = bool(TELEGRAM_PAYMENTS)
    payload["payments_note"] = (
        "free_launch" if not TELEGRAM_PAYMENTS else "invoices_on"
    )
    auth = _try_auth(x_telegram_init_data)
    payload["access"] = quota_status(_subject(auth))
    payload["tribute"] = TRIBUTE_ACCESS_URL
    payload["tribute_custom"] = TRIBUTE_CUSTOM_URL
    payload["human"] = HUMAN_CONTACT_URL
    return {"ok": True, **payload}


@router.get("/access")
def access_get(x_telegram_init_data: str | None = Header(default=None)) -> dict[str, Any]:
    return {"ok": True, **quota_status(_subject(_try_auth(x_telegram_init_data)))}


class RedeemBody(BaseModel):
    token: str = Field(..., min_length=8)


@router.post("/access/redeem")
def access_redeem(
    body: RedeemBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    sub = _subject(_try_auth(x_telegram_init_data))
    out = redeem(sanitize_text(body.token, max_len=128), bind_subject=sub)
    return out


@router.post("/tribute/webhook")
async def tribute_webhook(request: Request) -> dict[str, Any]:
    body = await request.body()
    sig = request.headers.get("trbt-signature") or request.headers.get("Trbt-Signature") or ""
    key = os.getenv("TRIBUTE_API_KEY", "")
    if key and not verify_tribute_signature(body, sig, key):
        raise HTTPException(401, "bad tribute signature")
    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "bad json") from exc
    if not isinstance(payload, dict):
        raise HTTPException(400, "bad payload")
    return apply_tribute_event(payload)


@router.post("/hit/{item_id}")
def hit(item_id: str) -> dict[str, Any]:
    safe = sanitize_text(item_id, max_len=64)
    return {"ok": True, "hits": bump_hit(safe)}


@router.post("/landing")
def landing(body: DemoBody) -> dict[str, Any]:
    """Landing studio: situation → event vision + abstraction + cards + rewritten prompt."""
    from backend.core.content_closer import closer_as_artifact, run_closer
    from backend.core.demo_highway import format_telegram
    from backend.core.resonance import remember

    brief = sanitize_text(body.brief, max_len=12_000)
    if len(brief) < 8:
        raise HTTPException(400, "Напишите, что сейчас движется — хотя бы одно предложение.")
    pack = run_closer(brief, lang=body.lang or "ru", with_comfort=True, with_making=False)
    art = closer_as_artifact(pack)
    remember(art)
    bump_hit("landing_studio")
    return {
        "ok": True,
        "section": "landing",
        "closer": pack,
        "artifact": art,
        "telegram_html": format_telegram(art),
    }


@router.post("/comfort")
def comfort(body: ComfortBody) -> dict[str, Any]:
    """Quiet assistant — top module of the engine section."""
    from backend.core.content_closer import comfort_turn, run_closer

    msg = sanitize_text(body.message, max_len=8_000)
    brief = sanitize_text(body.brief, max_len=8_000)
    closer = None
    seed = brief or msg
    if len(seed) >= 8:
        try:
            closer = run_closer(seed, lang=body.lang or "ru", with_comfort=False)
        except Exception:  # noqa: BLE001
            closer = None
    hist = body.history[-8:] if isinstance(body.history, list) else []
    turn = comfort_turn(msg, history=hist, closer=closer, lang=body.lang or "ru")
    bump_hit("comfort_studio")
    return {"ok": True, "section": "engine", **turn, "closer_id": (closer or {}).get("id")}


@router.post("/making")
def making(body: MakingBody) -> dict[str, Any]:
    """Making chamber — last section. New function."""
    from backend.core.demo_highway import format_telegram
    from backend.core.functions.making_chamber import run_making_function
    from backend.core.resonance import remember

    brief = sanitize_text(body.brief or body.extra or "собери неделю", max_len=12_000)
    if len(brief) < 8:
        raise HTTPException(400, "Сначала войдите в событие на лендинге — или опишите, что движется.")
    out = run_making_function(
        brief,
        lang=body.lang or "ru",
        closer=body.closer,
        extra=sanitize_text(body.extra, max_len=2_000),
    )
    if not out.get("ok"):
        return out
    making_art = out["making"]
    remember(making_art)
    bump_hit("making_chamber")
    return {
        "ok": True,
        "section": "making",
        **out,
        "artifact": making_art,
        "telegram_html": format_telegram(making_art),
    }


@router.post("/closer")
def closer_full(body: DemoBody) -> dict[str, Any]:
    """Full closer: abstraction → cards → prompt → making."""
    from backend.core.content_closer import closer_as_artifact, run_closer
    from backend.core.resonance import remember

    brief = sanitize_text(body.brief, max_len=12_000)
    if len(brief) < 8:
        raise HTTPException(400, "Напишите, что сейчас движется — хотя бы одно предложение.")
    pack = run_closer(brief, lang=body.lang or "ru", with_comfort=True, with_making=True)
    art = closer_as_artifact(pack)
    remember(art)
    bump_hit("content_closer")
    return {"ok": True, "closer": pack, "artifact": art}


@router.get("/trends")
def trends(q: str = "", lang: str = "ru") -> dict[str, Any]:
    from backend.core.content_closer import score_vectors, screen_trends

    vec = score_vectors(q)
    return {"ok": True, **screen_trends(q, vec, limit=3)}


@router.post("/demo")
def demo(body: DemoBody) -> dict[str, Any]:
    """Demo highway: situation → named artifact. Value miner starts here."""
    from backend.core.demo_highway import build_demo, format_telegram

    brief = sanitize_text(body.brief, max_len=12_000)
    if len(brief) < 8:
        raise HTTPException(400, "Напишите ситуацию чуть живее — хотя бы одно предложение.")
    try:
        art = build_demo(
            brief,
            hint=sanitize_text(body.hint, max_len=40),
            strategy=sanitize_text(body.strategy, max_len=40) or None,
            niche=sanitize_text(body.niche, max_len=40) or None,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    bump_hit("demo_highway")
    if art.get("strategy_id"):
        bump_hit(art["strategy_id"])
    if art.get("niche_id"):
        bump_hit("agent_studio")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.post("/resonate")
def resonate_route(body: ResonateBody) -> dict[str, Any]:
    from backend.core.resonance import resonate as _resonate

    out = _resonate(
        sanitize_text(body.artifact_id, max_len=32),
        sanitize_text(body.verdict, max_len=20),
        note=sanitize_text(body.note, max_len=500),
        who=sanitize_text(body.who, max_len=80),
    )
    return out


@router.get("/strategies")
def strategies() -> dict[str, Any]:
    from backend.core.strategies import list_strategies

    return {"ok": True, "items": list_strategies()}


@router.post("/strategy")
def strategy_run(
    body: DemoBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    from backend.core.demo_highway import format_telegram
    from backend.core.strategies import run_strategy
    from backend.core.resonance import remember

    gate = _gate(_subject(_try_auth(x_telegram_init_data)), "strategy")
    if not gate.get("allowed"):
        return _wall(gate)
    brief = sanitize_text(body.brief or body.strategy or "карта мест", max_len=8_000)
    art = run_strategy(body.strategy or body.hint, brief)
    remember(art)
    bump_hit(art.get("strategy_id") or "target_place")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.post("/risk")
def risk_run(
    body: DemoBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    from backend.core.demo_highway import format_telegram
    from backend.core.resonance import remember
    from backend.core.risk_engine import demo_card

    gate = _gate(_subject(_try_auth(x_telegram_init_data)), "risk")
    if not gate.get("allowed"):
        return _wall(gate)
    art = demo_card(sanitize_text(body.brief, max_len=4_000))
    remember(art)
    bump_hit("risk_engine")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.post("/panel")
def panel_run(
    body: DemoBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    from backend.core.artefacts import analytical_panel
    from backend.core.demo_highway import format_telegram
    from backend.core.resonance import remember

    gate = _gate(_subject(_try_auth(x_telegram_init_data)), "artefact_panel")
    if not gate.get("allowed"):
        return _wall(gate)
    art = analytical_panel(sanitize_text(body.brief, max_len=8_000), lang=body.lang or "ru")
    remember(art)
    bump_hit("artefact_panel")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.post("/offer")
def offer_run(
    body: DemoBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    from backend.core.artefacts import offer_generator
    from backend.core.demo_highway import format_telegram
    from backend.core.resonance import remember

    gate = _gate(_subject(_try_auth(x_telegram_init_data)), "offer_gen")
    if not gate.get("allowed"):
        return _wall(gate)
    art = offer_generator(sanitize_text(body.brief, max_len=8_000), lang=body.lang or "ru")
    remember(art)
    bump_hit("offer_gen")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.post("/teammate")
def teammate_run(
    body: DemoBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    from backend.core.demo_highway import format_telegram
    from backend.core.resonance import remember
    from backend.core.teammates import build_teammate

    gate = _gate(_subject(_try_auth(x_telegram_init_data)), "teammate")
    if not gate.get("allowed"):
        return _wall(gate)
    brief = sanitize_text(body.brief, max_len=8_000)
    art = build_teammate(body.niche or body.hint, brief)
    remember(art)
    bump_hit("agent_studio")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.get("/niches")
def niches() -> dict[str, Any]:
    from backend.core.agent_studio import list_niches

    return {"ok": True, "items": list_niches()}


@router.post("/agent")
def agent_run(
    body: DemoBody,
    x_telegram_init_data: str | None = Header(default=None),
) -> dict[str, Any]:
    from backend.core.demo_highway import format_telegram
    from backend.core.resonance import remember
    from backend.core.teammates import build_teammate

    gate = _gate(_subject(_try_auth(x_telegram_init_data)), "teammate")
    if not gate.get("allowed"):
        return _wall(gate)
    brief = sanitize_text(body.brief, max_len=8_000)
    art = build_teammate(body.niche or body.hint, brief)
    remember(art)
    bump_hit("agent_studio")
    return {"ok": True, "artifact": art, "telegram_html": format_telegram(art)}


@router.get("/posts")
def posts(limit: int = 14) -> dict[str, Any]:
    from backend.core.x_posts import HANDLE, X_URL, list_posts

    return {"ok": True, "handle": HANDLE, "url": X_URL, "items": list_posts(limit)}


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
