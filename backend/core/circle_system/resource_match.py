"""
Business resource recognition + compatibility with client asks.
Configures collaborative authors (merged project knowledge) and ledger fields.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.lexicon import RESOURCE_MARKERS, detect_markers
from backend.paid.types import clamp01


LEDGER_FIELDS = (
    "resource_id",
    "type",
    "owner",
    "capacity",
    "unit_cost",
    "availability",
    "linked_client_need",
    "collab_author_ids",
    "last_verified",
)


class ResourceMatchEngine:
    name = "Resource Match Engine"

    def run(
        self,
        text: str,
        certainty_result: dict[str, Any] | None = None,
        collab_authors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        hits = detect_markers(text or "", RESOURCE_MARKERS)
        authors = collab_authors or [
            {
                "id": "author_branding_va",
                "role": "branding_and_virtual_assets",
                "handle": "@andrewsmm1",
                "status": "active",
                "covers": ["identity", "va_objects", "naming"],
            },
            {
                "id": "author_deep_tech",
                "role": "deep_tech_architecture",
                "handle": "@karimmetrix",
                "status": "active",
                "covers": ["product", "metrics", "pilot", "tech_write"],
            },
        ]

        inventory: list[dict[str, Any]] = []
        for rtype, strength in hits.items():
            inventory.append(
                {
                    "resource_id": f"res_{rtype}",
                    "type": rtype,
                    "strength": round(strength, 3),
                    "availability": "detected" if strength >= 0.3 else "weak",
                    "ledger": {
                        "type": rtype,
                        "capacity": "unknown",
                        "unit_cost": None,
                        "linked_client_need": None,
                    },
                }
            )

        # Compatibility: map client param slots to resources
        params = (certainty_result or {}).get("parameters") or []
        matches: list[dict[str, Any]] = []
        need_map = {
            "integration": ("data", "compute"),
            "resource": ("human", "capital", "compute"),
            "metric": ("data",),
            "pilot_scope": ("human", "capital", "channel"),
            "offer": ("ip", "human"),
            "client_segment": ("channel",),
        }
        for p in params:
            slot = p.get("slot")
            needed = need_map.get(slot, ())
            have = [i for i in inventory if i["type"] in needed]
            score = clamp01(len(have) / max(1, len(needed))) if needed else 0.5
            matches.append(
                {
                    "param_id": p.get("id"),
                    "slot": slot,
                    "needed_resources": list(needed),
                    "matched": [h["resource_id"] for h in have],
                    "compatibility": round(score, 3),
                    "status": p.get("status"),
                }
            )

        # Attach collab authors by coverage
        for a in authors:
            a["assigned_layers"] = list(a.get("covers") or [])

        compat = (
            sum(m["compatibility"] for m in matches) / max(1, len(matches)) if matches else 0.4
        )

        return {
            "module": self.name,
            "inventory": inventory,
            "matches": matches,
            "compatibility_score": round(compat, 4),
            "collab_authors": authors,
            "ledger_schema": list(LEDGER_FIELDS),
            "ledger_seed_rows": [
                {
                    "resource_id": i["resource_id"],
                    "type": i["type"],
                    "owner": "client_or_metrix",
                    "capacity": i["ledger"]["capacity"],
                    "unit_cost": i["ledger"]["unit_cost"],
                    "availability": i["availability"],
                    "linked_client_need": None,
                    "collab_author_ids": [a["id"] for a in authors],
                    "last_verified": "runtime",
                }
                for i in inventory
            ],
        }
