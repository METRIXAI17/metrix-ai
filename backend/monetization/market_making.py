"""Market Making Simulation — positioning, attention liquidity, market dynamics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from backend.config import MONETIZATION


@dataclass
class MarketMakingResult:
    position: str
    attention_liquidity: float
    spread: float
    scenarios: dict[str, float]
    dynamics: list[str]
    price_usd: float
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MarketMakingSimulator:
    name = "Market Making Simulation"

    def simulate(
        self,
        idea_title: str,
        value_density: float,
        promo_fit: float,
        competition_hint: float = 0.4,
    ) -> MarketMakingResult:
        cfg = MONETIZATION["market_making"]
        liquidity = min(1.0, value_density * 0.5 + promo_fit * 0.5)
        spread = max(0.04, 0.4 - liquidity * 0.28 + competition_hint * 0.1)
        scenarios = {
            "base": round(liquidity, 4),
            "bull": round(min(1.0, liquidity * 1.35), 4),
            "bear": round(max(0.05, liquidity * 0.65), 4),
        }
        if liquidity >= 0.65:
            position = "category_maker"
        elif liquidity >= 0.45:
            position = "sharp_challenger"
        else:
            position = "niche_precision"

        dynamics = [
            f"Position: {position} for «{idea_title[:60]}»",
            f"Attention bid-ask spread≈{spread:.2f} (lower is tighter market)",
            "Seed demand with free demo; provide liquidity via Full Package tour",
            "Market-make ideas: always two-sided (demo free / implement paid)",
        ]
        summary = (
            f"{self.name}: position={position}, liquidity={liquidity:.2f}, "
            f"spread={spread:.2f}."
        )
        return MarketMakingResult(
            position=position,
            attention_liquidity=round(liquidity, 4),
            spread=round(spread, 4),
            scenarios=scenarios,
            dynamics=dynamics,
            price_usd=float(cfg["base_price_usd"]),
            summary=summary,
        )
