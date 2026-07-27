"""Registry of the 6 Fin Models."""

from __future__ import annotations

from typing import Any

from backend.config import INDUSTRIES
from backend.fin_models.chipforge import ChipForgeMetrics
from backend.fin_models.edgeforge import EdgeForgeCalculator
from backend.fin_models.marketforge import MarketForgeOptimizer
from backend.fin_models.metaobject import MetaObjectSimulator
from backend.fin_models.orientationforge import OrientationForgeEngine
from backend.fin_models.prologforge import PrologForgeLogicEngine
from backend.fin_models.template import FinModelTemplate


class FinModelRegistry:
    def __init__(self) -> None:
        self._models = {
            m.model_id: m
            for m in (
                ChipForgeMetrics(),
                OrientationForgeEngine(),
                EdgeForgeCalculator(),
                MetaObjectSimulator(),
                PrologForgeLogicEngine(),
                MarketForgeOptimizer(),
            )
        }

    def list_models(self) -> list[dict[str, str]]:
        return [
            {"id": m.model_id, "name": m.model_name}
            for m in self._models.values()
        ]

    def get(self, model_id: str):
        if model_id not in self._models:
            raise KeyError(f"Unknown fin model: {model_id}")
        return self._models[model_id]

    def run(self, model_id: str, context: dict[str, Any]) -> dict[str, Any]:
        return self.get(model_id).run(context).to_dict()

    def creation_prompt(self) -> str:
        return FinModelTemplate.prompt()


_reg: FinModelRegistry | None = None


def get_fin_model_registry() -> FinModelRegistry:
    global _reg
    if _reg is None:
        _reg = FinModelRegistry()
    return _reg


def run_fin_models_for_industry(
    industry_id: str,
    context: dict[str, Any],
    limit: int = 3,
) -> list[dict[str, Any]]:
    reg = get_fin_model_registry()
    industry = INDUSTRIES.get(industry_id) or {}
    ids = list(industry.get("default_fin_models") or ["orientationforge", "marketforge"])
    ids = ids[:limit]
    out = []
    for mid in ids:
        try:
            out.append(reg.run(mid, context))
        except KeyError:
            continue
    return out
