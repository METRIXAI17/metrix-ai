"""Fin model endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.fin_models.registry import get_fin_model_registry
from backend.fin_models.template import FinModelTemplate

router = APIRouter(prefix="/fin-models", tags=["fin-models"])


class FinRunBody(BaseModel):
    industry_id: str = "ai-agencies"
    scores: dict[str, float] = Field(default_factory=dict)
    axes: dict[str, float] = Field(default_factory=dict)
    operating_mode: str = "balanced_product_path"
    business: str = ""


@router.get("")
def list_fin_models() -> dict[str, Any]:
    reg = get_fin_model_registry()
    return {
        "models": reg.list_models(),
        "creation_template_prompt": reg.creation_prompt(),
    }


@router.get("/template")
def get_template() -> dict[str, str]:
    return {
        "name": FinModelTemplate.name,
        "prompt": FinModelTemplate.prompt(),
        "stages": "1 Definition | 2 General Paid | 3 Custom Paid",
    }


@router.post("/{model_id}/run")
def run_model(model_id: str, body: FinRunBody) -> dict[str, Any]:
    reg = get_fin_model_registry()
    try:
        return reg.run(
            model_id,
            {
                "industry_id": body.industry_id,
                "scores": body.scores
                or {
                    "product_fit": 0.55,
                    "model_fit": 0.6,
                    "promo_fit": 0.5,
                    "readiness": 0.55,
                    "overall_orientation": 0.55,
                },
                "axes": body.axes
                or {
                    "value_density": 0.55,
                    "time_pressure": 0.4,
                    "complexity": 0.5,
                    "monetization_fit": 0.55,
                    "risk": 0.25,
                },
                "operating_mode": body.operating_mode,
                "business": body.business,
            },
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
