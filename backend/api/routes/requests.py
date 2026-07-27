"""
Client request processing endpoints.

POST /api/v1/process  — главный вход (как форма на сайте)
POST /api/v1/orient   — только ориентация
GET  /api/v1/requests/{id} — сохранённый результат
GET  /api/v1/packages/{id}/result|consult|tech — HTML packs (Railway-hosted)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.config import DATA_DIR, WORKSPACE_ROOT
from backend.core.orientation_engine import OrientationEngine
from backend.core.request_pipeline import get_pipeline
from backend.schemas.requests import ClientRequest

router = APIRouter(tags=["requests"])

_REQ_ID_RE = re.compile(r"^[0-9a-fA-F-]{8,64}$")


def _safe_request_id(request_id: str) -> str:
    rid = (request_id or "").strip()
    if not _REQ_ID_RE.match(rid) or ".." in rid or "/" in rid or "\\" in rid:
        raise HTTPException(status_code=400, detail="invalid request_id")
    return rid


def _first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None


class ProcessBody(BaseModel):
    industry: str = Field(..., description="One of 6 industry directions")
    business: str = Field(..., min_length=20, description="Business description")
    track: str = Field(default="all", description="product|models|promotion|all")
    name: str = ""
    contact: str = ""
    program_id: str | None = None
    extra_params: dict[str, float] = Field(default_factory=dict)
    success_metrics: dict = Field(
        default_factory=dict,
        description=(
            "Custom success metrics positioning (TZ). "
            "Example: {weights:{iroi:0.4}, targets:{clarity:0.7}, priority:['iroi']}"
        ),
    )
    enable_self_improve: bool = True
    enable_fin_models: bool = True
    enable_monetization: bool = True


class OrientBody(BaseModel):
    industry: str
    business: str = Field(..., min_length=10)
    track: str | None = None
    extra_params: dict[str, float] = Field(default_factory=dict)


@router.post("/process")
def process_request(body: ProcessBody) -> dict[str, Any]:
    """
    Полная обработка клиентского запроса.

    Простой контракт:
      { industry, business, track? } → demo idea + breakdown + metrics + ...
    """
    req = ClientRequest(
        industry=body.industry,
        business=body.business,
        track=body.track,
        name=body.name,
        contact=body.contact,
        program_id=body.program_id,
        extra_params=body.extra_params,
        success_metrics=dict(body.success_metrics or {}),
        enable_self_improve=body.enable_self_improve,
        enable_fin_models=body.enable_fin_models,
        enable_monetization=body.enable_monetization,
    )
    result = get_pipeline().process(req)
    return result.to_dict()


@router.post("/orient")
def orient_only(body: OrientBody) -> dict[str, Any]:
    """Только OrientationForge — быстрый smoke-test ориентации."""
    try:
        res = OrientationEngine().orient(
            business_text=body.business,
            industry_id=body.industry,
            track=body.track,
            extra_params=body.extra_params,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return res.to_dict()


@router.get("/requests/{request_id}")
def get_request(request_id: str) -> dict[str, Any]:
    rid = _safe_request_id(request_id)
    path = Path(DATA_DIR) / "requests" / f"{rid}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="request not found")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/packages/{request_id}/result", response_class=HTMLResponse)
def package_result_html(request_id: str) -> HTMLResponse:
    """Primary client pack (consult + tech write result)."""
    rid = _safe_request_id(request_id)
    ws = WORKSPACE_ROOT / rid
    path = _first_existing(
        [
            ws / "12_package_result" / "YOUR_RESULT.html",
            ws / "12_package_result" / "PACKAGE.html",
            ws / "10_consult_metareality" / "CONSULTATION.html",
            ws / "10_client_pack" / "CLIENT_ORIENTATION.html",
        ]
    )
    if path is None:
        raise HTTPException(
            status_code=404,
            detail="package not found — run POST /api/v1/process first; workspace may be ephemeral after redeploy",
        )
    return HTMLResponse(
        content=path.read_text(encoding="utf-8"),
        headers={"Cache-Control": "private, max-age=60"},
    )


@router.get("/packages/{request_id}/consult", response_class=HTMLResponse)
def package_consult_html(request_id: str) -> HTMLResponse:
    rid = _safe_request_id(request_id)
    ws = WORKSPACE_ROOT / rid
    path = _first_existing(
        [
            ws / "10_consult_metareality" / "CONSULTATION.html",
            ws / "12_package_result" / "YOUR_RESULT.html",
        ]
    )
    if path is None:
        raise HTTPException(status_code=404, detail="consultation not found")
    return HTMLResponse(
        content=path.read_text(encoding="utf-8"),
        headers={"Cache-Control": "private, max-age=60"},
    )


@router.get("/packages/{request_id}/tech", response_class=HTMLResponse)
def package_tech_html(request_id: str) -> HTMLResponse:
    rid = _safe_request_id(request_id)
    ws = WORKSPACE_ROOT / rid
    path = _first_existing(
        [
            ws / "11_tech_write_specsforge" / "TECH_SPEC.html",
            ws / "12_package_result" / "YOUR_RESULT.html",
        ]
    )
    if path is None:
        raise HTTPException(status_code=404, detail="tech write not found")
    return HTMLResponse(
        content=path.read_text(encoding="utf-8"),
        headers={"Cache-Control": "private, max-age=60"},
    )
