"""Promo Automation — marketing automation + 3D distribution (brand/platforms/networks)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import MONETIZATION
from backend.monetization.distribution import DistributionEngine


@dataclass
class PromoPlan:
    sequence: list[dict[str, str]]
    channels: list[str]
    hooks: list[str]
    sample_messages: list[str]
    price_usd: float
    summary: str
    distribution: dict[str, Any] = field(default_factory=dict)

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
        domain: str = "",
        lang: str = "ru",
    ) -> PromoPlan:
        cfg = MONETIZATION["promo"]
        phrases = phrases or []
        dist = DistributionEngine().build(
            industry_id=industry_id,
            industry_name=industry_name,
            idea_title=idea_title,
            domain=domain,
            promo_fit=promo_fit,
            lang=lang,
        )
        dist_d = dist.to_dict()

        # Prefer distribution week plan over rigid template
        sequence = [
            {"day": w["day"], "action": f"[{w['channel']}] {w['action']}"}
            for w in dist_d.get("week_plan") or []
        ]
        if not sequence:
            sequence = [
                {"day": "0", "action": "Publish free demo idea + breakdown teaser"},
                {"day": "1", "action": "Reverse outreach to 10 lookalike businesses"},
                {"day": "3", "action": "Share Full Package tour invite"},
                {"day": "5", "action": "Case-style metrics post (VVI/ER/RRC delta)"},
                {"day": "7", "action": "Close to paid implement / showcase"},
            ]

        channels = [p.get("name", p.get("id", "")) for p in dist_d.get("platforms") or []]
        channels += [n.get("name", "") for n in dist_d.get("networks") or []]
        if industry_id == "telecom":
            channels.append("Carrier partner lists")
        if industry_id == "chipmaking":
            channels.append("Semiconductor community threads")

        hooks = list(dist_d.get("niche_hooks") or [])
        hooks.extend(
            [
                f"Industry-locked: {industry_name}",
                f"Idea spine: {idea_title}",
                f"Promo fit={promo_fit:.2f}",
                "Brand · Platforms · Networking (3D)",
            ]
        )
        messages = [
            f"[{industry_name}] {idea_title} — демо-артефакт, не «давай созвонимся в пустоту».",
            "Не generic AI-колода: геометрия вашей операции + метрика пилота.",
            "Дистрибуция: бренд-proof + площадка + тёплый нетворкинг — один ход в каждом.",
        ]
        messages.extend(phrases[:2])
        for anti in (dist_d.get("anti_patterns") or [])[:1]:
            messages.append(f"Анти-паттерн: {anti}")

        intensity = "high" if promo_fit >= 0.6 else "medium" if promo_fit >= 0.4 else "seed"
        summary = (
            f"{self.name} ({intensity}): 3D distribution + {len(sequence)}-day plan for "
            f"«{idea_title[:50]}» in {industry_name}."
        )
        return PromoPlan(
            sequence=sequence,
            channels=channels,
            hooks=hooks,
            sample_messages=messages,
            price_usd=float(cfg["base_price_usd"]),
            summary=summary,
            distribution=dist_d,
        )
