"""Auto Orders Engine — automated decision and ordering systems."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from backend.config import MONETIZATION


@dataclass
class AutoOrderPolicy:
    enabled: bool
    threshold: float
    triggers: list[dict[str, Any]]
    approval_gates: list[str]
    sample_orders: list[dict[str, Any]]
    price_usd: float
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AutoOrdersEngine:
    name = "Auto Orders Engine"

    def build(
        self,
        idea_title: str,
        info_roi: float,
        readiness: float,
        health: float,
        track: str,
    ) -> AutoOrderPolicy:
        cfg = MONETIZATION["auto_orders"]
        # порог: чем выше readiness/health/roi — тем смелее auto
        threshold = max(0.45, 0.85 - readiness * 0.25 - min(info_roi, 4) * 0.05)
        score = readiness * 0.4 + health * 0.35 + min(1.0, info_roi / 4.0) * 0.25
        enabled = score >= threshold

        triggers = [
            {
                "name": "high_info_roi",
                "when": f"info_roi >= {threshold + 0.2:.2f}",
                "action": "queue_paid_implement_offer",
            },
            {
                "name": "full_package_complete",
                "when": "client_finished_tour == true",
                "action": "open_order_for_full_package",
            },
            {
                "name": "promo_hot",
                "when": "promo_fit >= 0.65 and readiness >= 0.5",
                "action": "start_promo_sequence",
            },
        ]
        gates = [
            "Human confirms price & scope",
            "Industry direction locked",
            "Client contact present",
            "VVI not critical after SpecsForge",
        ]
        samples = []
        if enabled:
            samples.append(
                {
                    "sku": f"implement_{track}",
                    "title": f"Implement: {idea_title[:80]}",
                    "status": "queued_simulation",
                    "requires_approval": True,
                }
            )
            samples.append(
                {
                    "sku": "full_orientation_package",
                    "title": MONETIZATION["full_package"]["name"],
                    "status": "suggested",
                    "requires_approval": True,
                }
            )
        else:
            samples.append(
                {
                    "sku": "nurture_demo",
                    "title": "Keep free demo + re-orient later",
                    "status": "hold",
                    "requires_approval": False,
                }
            )

        summary = (
            f"{self.name}: score={score:.2f} vs threshold={threshold:.2f} → "
            f"{'AUTO-READY' if enabled else 'HOLD'}."
        )
        return AutoOrderPolicy(
            enabled=enabled,
            threshold=round(threshold, 4),
            triggers=triggers,
            approval_gates=gates,
            sample_orders=samples,
            price_usd=float(cfg["base_price_usd"]),
            summary=summary,
        )
