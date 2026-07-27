"""Zone & superstructure endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.orientation_engine import OrientationEngine
from backend.core.superstructure import SuperstructureOverlay
from backend.zones.registry import get_zone_registry

router = APIRouter(prefix="/zones", tags=["zones"])


class ComposeBody(BaseModel):
    industry: str
    business: str = Field(..., min_length=20)
    track: str | None = None
    info_roi: float = 1.5


@router.get("")
def list_zones() -> dict[str, Any]:
    return {"zones": get_zone_registry().describe()}


@router.post("/compose")
def compose_overlay(body: ComposeBody) -> dict[str, Any]:
    """Прогон Superstructure / Product Overlay."""
    try:
        orient = OrientationEngine().orient(
            body.business, body.industry, track=body.track
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = SuperstructureOverlay().compose(
        body.business,
        body.industry,
        orient.to_dict(),
        info_roi=body.info_roi,
    )
    return result.to_dict()
