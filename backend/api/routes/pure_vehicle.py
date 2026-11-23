"""PURE VEHICLE routes. Door price stays on the existing board."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.pure_vehicle import (
    alice_signal,
    constructor,
    contribute,
    creative_room,
    directing,
    grant_tokens,
    green_request,
    science_base,
    separated_circle,
)
from backend.core.pure_vehicle.catalog import OPS, recurse_status
from backend.core.pure_vehicle.npodp import run_npodp
from backend.core.pure_vehicle.sandbox import close_sandbox, release_line
from backend.core.pure_vehicle.lanes import place as place_lanes
from backend.core.pure_vehicle.vision import run_vision

router = APIRouter(prefix="/pure", tags=["pure-vehicle"])


class ConstructBody(BaseModel):
    text: str = ""
    sku: str = "allo_month"
    door: str = ""
    op: int | None = None
    consequence: str = ""
    base_asset: dict[str, Any] | None = None


class GreenBody(BaseModel):
    text: str = ""
    ticker: str = ""
    owner: str = ""


class DirectBody(BaseModel):
    text: str = ""
    sku: str = "allo_month"
    paid: bool = False
    choice: str = ""


class ContributeBody(BaseModel):
    kind: str = "template"
    body: Any = ""
    subject: str = ""
    ticker: str = ""
    owner: str = ""
    creative: bool = False


class TokenBody(BaseModel):
    subject: str = ""
    sku: str = "allo_month"


class CircleBody(BaseModel):
    subject: str = ""
    template: Any = ""
    sku: str = ""


class AliceBody(BaseModel):
    rank: dict[str, Any] = Field(default_factory=dict)


class SandboxBody(BaseModel):
    agents: list[dict[str, Any]] = Field(default_factory=list)
    eval_floor: float | None = None


@router.get("/line")
def pure_line() -> dict[str, Any]:
    return release_line()


@router.post("/sandbox")
def pure_sandbox(body: SandboxBody) -> dict[str, Any]:
    return close_sandbox({"agents": body.agents, "eval_floor": body.eval_floor})


class VisionBody(BaseModel):
    concept: str = ""
    solution: str = ""
    ideas: str = ""
    data: list[dict[str, Any]] = Field(default_factory=list)
    table: list[dict[str, Any]] = Field(default_factory=list)
    bridge: dict[str, Any] = Field(default_factory=dict)
    purchase: dict[str, Any] = Field(default_factory=dict)
    eval_floor: float | None = None


@router.post("/vision")
def pure_vision(body: VisionBody) -> dict[str, Any]:
    return run_vision(body.model_dump())


class LanesBody(BaseModel):
    autonomy: dict[str, Any] = Field(default_factory=dict)
    trading: dict[str, Any] = Field(default_factory=dict)
    ideas: dict[str, Any] = Field(default_factory=dict)
    eval_floor: float | None = None


@router.post("/lanes")
def pure_lanes(body: LanesBody) -> dict[str, Any]:
    return place_lanes(body.model_dump())


class NpodpBody(BaseModel):
    children: list[dict[str, Any]] = Field(default_factory=list)
    zone: dict[str, Any] = Field(default_factory=dict)
    support: dict[str, Any] = Field(default_factory=dict)
    book: list[dict[str, Any]] = Field(default_factory=list)
    exponent: dict[str, Any] = Field(default_factory=dict)
    radar: dict[str, Any] = Field(default_factory=dict)
    eval_floor: float | None = None


@router.post("/npodp")
def pure_npodp(body: NpodpBody) -> dict[str, Any]:
    return run_npodp(body.model_dump())


@router.get("/ops")
def pure_ops() -> dict[str, Any]:
    return {"ok": True, "version": "2.1.0", "codename": "PURE VEHICLE", "ops": OPS, "eighth": False}


@router.get("/science")
def pure_science() -> dict[str, Any]:
    base = science_base()
    return {"ok": True, **base, "eighth_product": False}


@router.get("/contributions")
def pure_read() -> dict[str, Any]:
    return {"ok": True, "rows": public_contributions()}


@router.post("/construct")
def pure_construct(body: ConstructBody) -> dict[str, Any]:
    situation: dict[str, Any] = {"text": body.text, "sku": body.sku, "door": body.door, "consequence": body.consequence}
    if body.op is not None:
        situation["op"] = body.op
    if body.base_asset is not None:
        situation["base_asset"] = body.base_asset
    return constructor(situation)


@router.post("/green")
def pure_green(body: GreenBody) -> dict[str, Any]:
    return green_request(body.text, ticker=body.ticker, owner=body.owner)


@router.post("/direct")
def pure_direct(body: DirectBody) -> dict[str, Any]:
    return directing({"text": body.text, "sku": body.sku}, paid=body.paid, choice=body.choice or None)


@router.post("/contribute")
def pure_contribute(body: ContributeBody) -> dict[str, Any]:
    if body.creative:
        return creative_room(body.body, body.subject, kind=body.kind if body.kind in ("template", "db_row") else "template", ticker=body.ticker, owner=body.owner)
    return contribute(body.kind, body.body, body.subject)


@router.post("/tokens")
def pure_tokens(body: TokenBody) -> dict[str, Any]:
    return grant_tokens(body.subject, sku=body.sku)


@router.post("/circle")
def pure_circle(body: CircleBody) -> dict[str, Any]:
    return separated_circle(body.subject, body.template, sku=body.sku)


@router.post("/alice")
def pure_alice(body: AliceBody) -> dict[str, Any]:
    return alice_signal(body.rank)


@router.get("/game")
def pure_game() -> dict[str, Any]:
    pack = game_pack()
    pack["recurse"] = recurse_status("game_pack")
    return {"ok": True, **pack}


@router.post("/freelance")
def pure_freelance(pack_id: str = "freelance", subject: str = "") -> dict[str, Any]:
    return purchase_isolated(pack_id, subject)
