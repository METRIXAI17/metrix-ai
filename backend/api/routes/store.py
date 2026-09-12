"""Store, Door, CraftShift, seven lines, think-more."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.ai_mgmt import pack as ai_mgmt_pack
from backend.core.complexity_boundary import lattice, table_telegram, think_more
from backend.core.craftshift_x import run as craftshift_run
from backend.core.door import bind, load, mint, public_view
from backend.core.seven_lines import run_all, run_line
from backend.core.store_catalog import catalog_payload, category_by_id

router = APIRouter(tags=["store"])


class BriefBody(BaseModel):
    brief: str = Field(default="", min_length=0)
    door: str = ""
    category: str = ""
    line: int | None = None
    lang: str = "ru"
    with_engine: bool = False
    state: dict[str, Any] | None = None


def _door_of(body: BriefBody, room: str) -> dict[str, Any]:
    rec = load(body.door) if body.door else None
    if rec:
        return bind(rec["code"], brief=body.brief, room=room)
    if body.brief.strip():
        return mint(body.brief, room=room)
    return mint(room=room)


@router.get("/store")
def store_catalog(lang: str = "ru") -> dict[str, Any]:
    return catalog_payload(lang=lang)


@router.post("/store/run")
def store_run(body: BriefBody) -> dict[str, Any]:
    cat = category_by_id(body.category or str(body.line or 1)) or category_by_id("1")
    n = int((cat or {}).get("n") or 1)
    brief = (body.brief or "").strip() or (cat or {}).get("placeholder") or "контур"
    rec = _door_of(body, f"store:{cat.get('id') if cat else n}")
    art = run_line(n, brief, with_engine=body.with_engine)
    bind(rec["code"], artifact_id=str(art.get("id") or ""), room=f"store:{cat.get('id') if cat else n}")
    return {
        "ok": True,
        "door": public_view(rec),
        "category": cat,
        "artifact": art,
        "telegram_html": table_telegram(art.get("lattice") or lattice(brief)),
    }


@router.post("/store/think-more")
def store_think_more(body: BriefBody) -> dict[str, Any]:
    brief = (body.brief or "").strip() or "контур"
    rec = _door_of(body, "think")
    nxt = think_more(brief, body.state)
    from backend.core.door import bump_think

    bump_think(rec["code"])
    rec = load(rec["code"]) or rec
    return {"ok": True, "door": public_view(rec), "lattice": nxt, "telegram_html": table_telegram(nxt)}


@router.post("/door")
def door_mint(body: BriefBody) -> dict[str, Any]:
    rec = load(body.door) if body.door else None
    if rec:
        rec = bind(rec["code"], brief=body.brief, room="talk")
    else:
        rec = mint(body.brief, room="talk")
    return public_view(rec)


@router.get("/door/{code}")
def door_get(code: str) -> dict[str, Any]:
    return public_view(load(code))


@router.post("/craftshift")
def craftshift(body: BriefBody) -> dict[str, Any]:
    brief = (body.brief or "").strip() or "нужен пост и кадр"
    rec = _door_of(body, "craftshift")
    art = craftshift_run(brief)
    bind(rec["code"], artifact_id=str(art.get("id") or ""), room="craftshift")
    return {"ok": True, "door": public_view(rec), "artifact": art}


@router.post("/lines/run")
def lines_run(body: BriefBody) -> dict[str, Any]:
    brief = (body.brief or "").strip()
    if len(brief) < 16:
        return {"ok": False, "reason": "brief_short"}
    rec = _door_of(body, "lines")
    if body.line:
        art = run_line(int(body.line), brief, with_engine=body.with_engine)
        return {"ok": True, "door": public_view(rec), "line": body.line, "artifact": art}
    out = run_all(brief, with_engine=body.with_engine)
    return {"ok": True, "door": public_view(rec), **out}


@router.get("/ai-mgmt")
def ai_mgmt() -> dict[str, Any]:
    return ai_mgmt_pack("менеджмент работы с ИИ как посадка, не чат")
