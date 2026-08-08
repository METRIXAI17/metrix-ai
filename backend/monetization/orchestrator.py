"""Combine Promo + Market Making + Auto Orders + Funding pillars into one layer."""

from __future__ import annotations

from typing import Any

from backend.config import MONETIZATION
from backend.monetization.auto_orders import AutoOrdersEngine
from backend.monetization.market_making import MarketMakingSimulator
from backend.monetization.promo import PromoAutomation
from backend.monetization.structural_income import StructuralIncomeEngine
from backend.monetization.asset_attach import AssetAttachEngine
from backend.monetization.capital_coop import CapitalCoopEngine


class MonetizationOrchestrator:
    name = "Monetization Layer"

    def __init__(self) -> None:
        self.promo = PromoAutomation()
        self.mm = MarketMakingSimulator()
        self.orders = AutoOrdersEngine()
        self.structural = StructuralIncomeEngine()
        self.assets = AssetAttachEngine()
        self.capital_coop = CapitalCoopEngine()

    def run(
        self,
        *,
        idea_title: str,
        industry_id: str,
        industry_name: str,
        scores: dict[str, float],
        axes: dict[str, float],
        info_roi: float,
        health: float,
        track: str,
        phrases: list[str] | None = None,
    ) -> dict[str, Any]:
        promo = self.promo.build(
            idea_title,
            industry_id,
            industry_name,
            promo_fit=float(scores.get("promo_fit", 0.5)),
            phrases=phrases,
            domain=str((scores or {}).get("_domain", "") or ""),
            lang="ru",
        )
        mm = self.mm.simulate(
            idea_title,
            value_density=float(axes.get("value_density", 0.5)),
            promo_fit=float(scores.get("promo_fit", 0.5)),
        )
        orders = self.orders.build(
            idea_title,
            info_roi=info_roi,
            readiness=float(scores.get("readiness", 0.5)),
            health=health,
            track=track,
        )

        brief = " ".join(
            [idea_title or "", industry_name or "", " ".join(phrases or [])]
        ).strip()
        structural = self.structural.build(brief or idea_title, project_name=idea_title)
        assets = self.assets.build(brief or idea_title, project_name=idea_title)
        capital = self.capital_coop.build(brief or idea_title, project_name=idea_title)

        stack_price = (
            promo.price_usd + mm.price_usd + orders.price_usd
            if orders.enabled
            else promo.price_usd + mm.price_usd
        )
        full = MONETIZATION["full_package"]

        return {
            "layer": self.name,
            "promo": promo.to_dict(),
            "market_making": mm.to_dict(),
            "auto_orders": orders.to_dict(),
            "funding": {
                "structural_income": structural,
                "assets_1to1": assets,
                "capital_coop": capital,
            },
            "pricing": {
                "promo_usd": promo.price_usd,
                "market_making_usd": mm.price_usd,
                "auto_orders_usd": orders.price_usd if orders.enabled else 0,
                "stack_estimate_usd": stack_price,
                "full_package_usd": full["base_price_usd"],
                "note": "Showcase list prices — quote after Full Package tour.",
            },
            "summary": (
                f"Monetization: promo + MM"
                f"{' + auto-orders' if orders.enabled else ''} + funding×3 | "
                f"stack≈${stack_price:.0f}, full package=${full['base_price_usd']}."
            ),
        }
