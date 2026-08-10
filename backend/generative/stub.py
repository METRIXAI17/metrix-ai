"""
Generativity — block 19 live via MeaningEngine + expansion hooks.

Decision Core / OAE call this when mode is generative_development.
"""

from __future__ import annotations

from typing import Any

from backend.generative.meaning_engine import expand_meanings


class GenerativityStub:
    name = "Generativity · MeaningEngine (block 19 live)"

    def expand(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = (
            payload.get("business")
            or payload.get("reduced_to_request")
            or " ".join(str(x) for x in (payload.get("demo_ideas") or [])[:2])
            or ""
        )
        if isinstance(text, dict):
            text = str(text.get("text") or text.get("summary") or text)[:800]
        meaning = expand_meanings(
            str(text),
            path_id=str(payload.get("path_id") or ""),
            segment_id=str(payload.get("segment_id") or ""),
            unit=str(payload.get("unit") or "unit pack"),
            lang=str(payload.get("lang") or "ru"),
        )
        return {
            "module": self.name,
            "status": "live",
            "received_keys": list(payload.keys()),
            "meaning": meaning,
            "ideas": payload.get("demo_ideas") or [],
            "moves": meaning.get("moves"),
            "essence": meaning.get("essence_one_liner"),
            "note": "MeaningEngine expands OAE/decision payload into dense original moves.",
        }


def generative_ready_payload(
    oae: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "embedding": oae.get("embedding"),
        "abstract_coordinates": oae.get("abstract_coordinates"),
        "pragma": oae.get("pragma"),
        "demo_ideas": oae.get("demo_ideas"),
        "active_mode": decision.get("active_mode"),
        "reduced_to_request": oae.get("reduced_to_request"),
    }
    # Pre-expand meanings so callers get denser generative surface
    gen = GenerativityStub().expand(base)
    base["meaning_engine"] = gen.get("meaning")
    base["generative_status"] = "live"
    return base
