"""
Dedicated Prompt Template for Creating New Fin Models.

Каждая новая Fin Model ОБЯЗАНА следовать 3-stage structure:

  Stage 1: Definition      — existing knowledge, parameters, context
  Stage 2: General Paid    — core paid functionality common to all clients
  Stage 3: Custom Paid     — deep customization for specific client/product

Этот файл — reusable sub-prompt/template внутри системы.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


FIN_MODEL_CREATION_PROMPT = """
# Metrix AI — Fin Model Creation Template (STRICT)

You are defining a new Financial / Optimization Model for Metrix AI.
Follow ALL three stages. Do not skip. Do not merge stages.

## Stage 1: Definition (existing knowledge, parameters, context)
- Model name (industry-flavored, unique, clickable)
- Domain / industry anchors
- Parameter map (minimal, orientation-compatible)
- Core metrics hooks: VVI, ER, RRC
- Known constraints and voids
- Inputs from OrientationForge Dynamic Compass

## Stage 2: General Paid Part (core paid functionality for ALL clients)
- What every paying client receives
- Standard deliverables
- Base pricing logic / unit economics
- Promo / Market Making / Auto Orders hooks (if any)
- Acceptance criteria shared across clients

## Stage 3: Custom Paid Part (deep customization)
- Client-specific geometry adaptations
- Extra parameters mined only for this client
- Custom simulations / rules / thresholds
- White-label or industry-special modules
- Success metrics unique to this engagement

## Output contract
Return structured JSON with keys:
  definition, general_paid, custom_paid, metrics_hooks, monetization_hooks
""".strip()


@dataclass
class StageBlock:
    title: str
    bullets: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    price_hint_usd: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ThreeStageSpec:
    """Готовый 3-stage артефакт Fin Model."""

    model_id: str
    model_name: str
    stage1_definition: StageBlock
    stage2_general_paid: StageBlock
    stage3_custom_paid: StageBlock
    metrics_hooks: dict[str, str] = field(default_factory=dict)
    monetization_hooks: list[str] = field(default_factory=list)
    prompt_template: str = FIN_MODEL_CREATION_PROMPT

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "stage1_definition": self.stage1_definition.to_dict(),
            "stage2_general_paid": self.stage2_general_paid.to_dict(),
            "stage3_custom_paid": self.stage3_custom_paid.to_dict(),
            "metrics_hooks": self.metrics_hooks,
            "monetization_hooks": self.monetization_hooks,
            "prompt_template_included": True,
        }


class FinModelTemplate:
    """Фабрика 3-stage спецификаций для любой Fin Model."""

    name = "Fin Model 3-Stage Template"

    @staticmethod
    def prompt() -> str:
        return FIN_MODEL_CREATION_PROMPT

    @staticmethod
    def build(
        model_id: str,
        model_name: str,
        *,
        definition_bullets: list[str],
        definition_deliverables: list[str],
        general_bullets: list[str],
        general_deliverables: list[str],
        general_price: float,
        custom_bullets: list[str],
        custom_deliverables: list[str],
        custom_price: float,
        metrics_hooks: dict[str, str] | None = None,
        monetization_hooks: list[str] | None = None,
    ) -> ThreeStageSpec:
        return ThreeStageSpec(
            model_id=model_id,
            model_name=model_name,
            stage1_definition=StageBlock(
                title="Stage 1 · Definition",
                bullets=definition_bullets,
                deliverables=definition_deliverables,
            ),
            stage2_general_paid=StageBlock(
                title="Stage 2 · General Paid Part",
                bullets=general_bullets,
                deliverables=general_deliverables,
                price_hint_usd=general_price,
            ),
            stage3_custom_paid=StageBlock(
                title="Stage 3 · Custom Paid Part",
                bullets=custom_bullets,
                deliverables=custom_deliverables,
                price_hint_usd=custom_price,
            ),
            metrics_hooks=metrics_hooks
            or {
                "VVI": "Measure voids in model parameters",
                "ER": "Turn model errors into pricing improvements",
                "RRC": "Allow reverse refragment of cost layers",
            },
            monetization_hooks=monetization_hooks
            or ["promo", "market_making", "auto_orders"],
        )
