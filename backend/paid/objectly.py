"""
Objectly — turn phenomena into Virtual Assets (weight · price · owner).

Scaffold for success-building tokens / new asset class management.
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.paid.types import clamp01, safe_float


class ObjectlyEngine:
    name = "Objectly"
    status = "live_scaffold"

    def materialize(
        self,
        *,
        industry_id: str = "",
        business: str = "",
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        reader: dict[str, Any] | None = None,
        principles: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        reader = reader or paid.get("reader") or {}
        principles = principles or {}

        # Prefer virtual assets already from chips / reader
        existing = list(paid.get("virtual_assets") or [])
        objects: list[dict[str, Any]] = []

        for i, va in enumerate(existing[:8]):
            if not isinstance(va, dict):
                continue
            objects.append(self._normalize_va(va, i, industry_id))

        # Build objects from active principles if thin
        for pid in (principles.get("active_principle_ids") or [])[:6]:
            if len(objects) >= 10:
                break
            objects.append(
                {
                    "id": f"obj_p{pid}",
                    "kind": "principle_object",
                    "title": f"Principle-{pid} Virtual Asset",
                    "weight": round(0.4 + 0.05 * (pid % 7), 4),
                    "price_signal_usd": round(40 + pid * 12 + safe_float(paid.get("paid_score"), 0.5) * 80, 2),
                    "owner": "metrix_system",
                    "transferable": True,
                    "industry_id": industry_id or None,
                    "class": "success_building_unit",
                }
            )

        if idea_title:
            seed = hashlib.sha1(f"{idea_title}|{industry_id}".encode()).hexdigest()[:8]
            objects.insert(
                0,
                {
                    "id": f"obj_idea_{seed}",
                    "kind": "idea_object",
                    "title": (idea_title or "Untitled")[:80],
                    "weight": round(
                        clamp01(0.5 + 0.3 * safe_float(paid.get("paid_score"), 0.5)), 4
                    ),
                    "price_signal_usd": round(
                        290 * safe_float(paid.get("paid_score"), 0.55), 2
                    ),
                    "owner": "founder_pending",
                    "transferable": True,
                    "industry_id": industry_id or None,
                    "class": "success_building_unit",
                    "business_excerpt": (business or "")[:120],
                },
            )

        total_weight = sum(safe_float(o.get("weight"), 0) for o in objects) or 1.0
        portfolio_value = sum(safe_float(o.get("price_signal_usd"), 0) for o in objects)

        return {
            "module": self.name,
            "status": self.status,
            "objects": objects[:12],
            "count": min(12, len(objects)),
            "total_weight": round(total_weight, 4),
            "portfolio_price_signal_usd": round(portfolio_value, 2),
            "asset_class": "Intelligence Platform — New Asset Class (ideas · system design · product concepts)",
            "next_step": "Token-Building NFTs can mint from idea_object when commercial go-live",
            "honesty": (
                "Price signals are internal orientation units, not market quotes. "
                "No chain settlement until wallet keys are wired."
            ),
            "open_points": [
                "OPEN: on-chain mint / wallet ownership",
                "OPEN: secondary market for success-building tokens",
            ],
        }

    def _normalize_va(self, va: dict[str, Any], i: int, industry_id: str) -> dict[str, Any]:
        return {
            "id": va.get("id") or f"obj_va_{i}",
            "kind": va.get("kind") or "virtual_asset",
            "title": va.get("title") or va.get("name") or f"Asset {i+1}",
            "weight": round(safe_float(va.get("weight"), 0.45 + 0.03 * i), 4),
            "price_signal_usd": round(
                safe_float(va.get("price_signal") or va.get("price_signal_usd"), 50 + 15 * i),
                2,
            ),
            "owner": va.get("owner") or "metrix_system",
            "transferable": bool(va.get("transferable", True)),
            "industry_id": industry_id or None,
            "class": "success_building_unit",
            "branding": va.get("branding"),
        }
