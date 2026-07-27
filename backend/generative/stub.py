"""
Generativity stub — interface only until block 19.

Decision Core / OAE call this when mode is generative_development.
"""

from __future__ import annotations

from typing import Any


class GenerativityStub:
    name = "Generativity Concept (block 19 — pending)"

    def expand(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Placeholder: returns structured ack without inventing final method."""
        return {
            "module": self.name,
            "status": "awaiting_block_19_implementation",
            "received_keys": list(payload.keys()),
            "note": (
                "OAE abstract_coordinates + embedding + pragma will feed "
                "your generativity concept on July 19."
            ),
            "ideas": payload.get("demo_ideas") or [],
        }


def generative_ready_payload(
    oae: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "embedding": oae.get("embedding"),
        "abstract_coordinates": oae.get("abstract_coordinates"),
        "pragma": oae.get("pragma"),
        "demo_ideas": oae.get("demo_ideas"),
        "active_mode": decision.get("active_mode"),
        "reduced_to_request": oae.get("reduced_to_request"),
    }
