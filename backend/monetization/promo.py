"""Promo Automation — marketing automation and idea promotion."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import MONETIZATION


@dataclass
class PromoPlan:
    sequence: list[dict[str, str]]
    channels: list[str]
    hooks: list[str]
    sample_messages: list[str]
    price_usd: float
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PromoAutomation:
    name = "Promo Automation"

    def build(
        self,
        idea_title: str,
        industry_id: str,
        industry_name: str,
        promo_fit: float,
        phrases: list[str] | None = None,
    ) -> PromoPlan:
        cfg = MONETIZATION["promo"]
        phrases = phrases or []
        sequence = [
            {"day": "0", "action": "Publish free demo idea + breakdown teaser"},
            {"day": "1", "action": "Reverse outreach to 10 lookalike businesses"},
            {"day": "3", "action": "Share Full Package tour invite"},
            {"day": "5", "action": "Case-style metrics post (VVI/ER/RRC delta)"},
            {"day": "7", "action": "Close to paid implement / showcase"},
        ]
        channels = ["X/Twitter DM", "X public posts", "Landing marketplace", "Email"]
        if industry_id == "telecom":
            channels.append("Carrier partner lists")
        if industry_id == "chipmaking":
            channels.append("Semiconductor community threads")

        hooks = [
            f"Industry-locked: {industry_name}",
            f"Idea spine: {idea_title}",
            "Orientation without training dump — relevance now",
            f"Promo fit score={promo_fit:.2f}",
        ]
        messages = [
            f"Quick idea for {industry_name}: {idea_title}. Want the free breakdown?",
            "Not another generic AI deck — geometry of YOUR operation, oriented live.",
            "Try Product → Models → Promotion as a Full Package tour.",
        ]
        messages.extend(phrases[:2])

        intensity = "high" if promo_fit >= 0.6 else "medium" if promo_fit >= 0.4 else "seed"
        summary = (
            f"{self.name} ({intensity}): {len(sequence)}-step sequence for "
            f"«{idea_title[:50]}» in {industry_name}."
        )
        return PromoPlan(
            sequence=sequence,
            channels=channels,
            hooks=hooks,
            sample_messages=messages,
            price_usd=float(cfg["base_price_usd"]),
            summary=summary,
        )
