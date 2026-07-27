"""
Harness Showcase + automatic live mode (self-cycling).

When demo path randomly aligns with a generated run → success signal.
One component pulls the other; third cycle = co-working mode.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from backend.paid.types import clamp01, safe_float


class HarnessShowcase:
    name = "Harness Showcase"
    status = "live"
    default_live = True

    def run(
        self,
        *,
        industry_id: str = "",
        paid: dict[str, Any] | None = None,
        sequence: dict[str, Any] | None = None,
        principles: dict[str, Any] | None = None,
        anti_down: dict[str, Any] | None = None,
        nft: dict[str, Any] | None = None,
        objectly: dict[str, Any] | None = None,
        opening_edge: dict[str, Any] | None = None,
        request_id: str = "",
    ) -> dict[str, Any]:
        paid = paid or {}
        sequence = sequence or {}
        principles = principles or {}
        anti_down = anti_down or {}
        nft = nft or {}
        objectly = objectly or {}
        opening_edge = opening_edge or {}

        # Component pull strengths
        components = {
            "paid_core": safe_float(paid.get("paid_score"), 0.5),
            "sequence": safe_float(sequence.get("quality"), 0.5),
            "principles": safe_float(principles.get("coherence"), 0.5),
            "anti_down": 0.8
            if anti_down.get("gate") in ("pass", "strong_pass", "pass_with_warnings")
            else 0.35,
            "nft": 0.55 if nft.get("token_draft") else 0.3,
            "objectly": clamp01(safe_float(objectly.get("count"), 0) / 8),
            "opening_edge": safe_float(opening_edge.get("edge_score"), 0.5),
        }

        # Self-cycle detection: random-ish alignment of demo vs generated
        seed = f"{request_id}|{industry_id}|{sequence.get('plan_code', '')}"
        h = int(hashlib.sha1(seed.encode()).hexdigest()[:8], 16)
        demo_roll = (h % 1000) / 1000.0
        gen_center = sum(components.values()) / max(1, len(components))
        align = 1.0 - abs(demo_roll - gen_center)
        hit = align >= 0.72  # "randomly hits generated run"

        # Cycles
        cycle_1 = {
            "name": "component_pull",
            "active": True,
            "driver": max(components, key=components.get),
            "pull": round(max(components.values()), 4),
        }
        cycle_2 = {
            "name": "mutual_pull",
            "active": components["paid_core"] > 0.45 and components["sequence"] > 0.4,
            "pair": ["paid_core", "sequence"],
            "strength": round(
                (components["paid_core"] + components["sequence"]) / 2, 4
            ),
        }
        cycle_3 = {
            "name": "co_working",
            "active": hit and anti_down.get("gate") != "block_down",
            "meaning": "Third cycle: system works jointly when demo aligns with generated run",
            "alignment": round(align, 4),
            "success_signal": hit,
        }

        live_mode = self.default_live
        live_score = clamp01(
            0.25 * components["paid_core"]
            + 0.2 * components["sequence"]
            + 0.2 * components["anti_down"]
            + 0.15 * components["opening_edge"]
            + 0.2 * (1.0 if hit else align)
        )

        return {
            "module": self.name,
            "status": self.status,
            "live_mode": live_mode,
            "live_score": round(live_score, 4),
            "components": {k: round(v, 4) for k, v in components.items()},
            "cycles": [cycle_1, cycle_2, cycle_3],
            "alignment": {
                "demo_roll": round(demo_roll, 4),
                "gen_center": round(gen_center, 4),
                "align": round(align, 4),
                "hit_success": hit,
            },
            "showcase": {
                "headline": "Harness live — automatic self-cycle",
                "industry_id": industry_id or None,
                "plan_code": sequence.get("plan_code"),
                "ts": int(time.time()),
            },
            "sell_ops_hook": (
                "Live mode feeds low-touch sales execution surface "
                "(metric-driven, no heavy manual overhead)."
            ),
            "honesty": (
                "Alignment is deterministic hash of request context — "
                "reproducible demo of self-cycle, not magic randomness."
            ),
        }
