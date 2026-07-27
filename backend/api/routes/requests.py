"""
Client request processing endpoints.

POST /api/v1/process  — главный вход (как форма на сайте)
POST /api/v1/orient   — только ориентация
GET  /api/v1/requests/{id} — сохранённый результат
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config import DATA_DIR
from backend.core.orientation_engine import OrientationEngine
from backend.core.request_pipeline import get_pipeline
from backend.schemas.requests import ClientRequest

router = APIRouter(tags=["requests"])


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
    path = Path(DATA_DIR) / "requests" / f"{request_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="request not found")
    return json.loads(path.read_text(encoding="utf-8"))
