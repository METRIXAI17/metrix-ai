"""
Operational sense — purge writing distortions using true-relation groups.

Distortions: overclaim, generic JTBD, parameter-without-source,
template-loop, sellable-without-must-ask, reverse-without-direct.
"""

from __future__ import annotations

import re
from typing import Any

from backend.paid.types import clamp01, safe_float


GENERIC_MARKERS = (
    "oriented to your geometry",
    "job-to-be-done покупателя размыт",
    "job-to-be-done is unclear",
    "reader5:",
    "proceed to pilot tz",
    "open paid portal",
    "without relying on any database",
    "we build something alive",
)


class DistortionPurge:
    name = "Distortion Purge"

    def run(
        self,
        *,
        draft_sentences: list[str],
        relations: dict[str, Any] | None = None,
        probability_map: dict[str, Any] | None = None,
        must_ask_open: int = 0,
        paid_status: str = "",
        client_tokens: list[str] | None = None,
    ) -> dict[str, Any]:
        relations = relations or {}
        probability_map = probability_map or {}
        client_tokens = [t.lower() for t in (client_tokens or []) if t]

        true_hubs = {g["hub"].lower() for g in (relations.get("true_groups") or [])}
        rails = set(probability_map.get("writing_rails") or [])

        kept: list[dict[str, Any]] = []
        removed: list[dict[str, Any]] = []
        narrowed_variants: list[str] = []

        for s in draft_sentences:
            reasons: list[str] = []
            sl = s.lower().strip()
            if not sl or len(sl) < 12:
                reasons.append("empty_or_thin")
            for g in GENERIC_MARKERS:
                if g in sl:
                    reasons.append("generic_template")
                    break
            # must stay near true hubs or client tokens or rails language
            hub_hit = any(h in sl for h in true_hubs) if true_hubs else True
            tok_hit = any(t in sl for t in client_tokens[:12]) if client_tokens else False
            if not hub_hit and not tok_hit and "lever" not in sl and "pilot" not in sl:
                reasons.append("untethered_from_true_relations")
            if must_ask_open > 0 and any(
                x in sl for x in ("packageable", "ready to ship full", "guaranteed")
            ):
                reasons.append("oversell_with_open_must_ask")
            if paid_status in ("candidate_preview", "preview") and "full package delivered" in sl:
                reasons.append("status_mismatch")

            if reasons:
                removed.append({"sentence": s, "reasons": reasons})
                # Narrowed rewrite stub
                if "generic_template" in reasons and client_tokens:
                    narrowed_variants.append(
                        self._narrow(s, client_tokens, true_hubs, probability_map)
                    )
            else:
                kept.append({"sentence": s, "reasons": []})

        # If too few kept, inject top probability conclusions as forced rails
        if len(kept) < 3:
            for c in (probability_map.get("top_positive") or [])[:5]:
                kept.append(
                    {
                        "sentence": c["text"],
                        "reasons": [],
                        "forced_from_map": True,
                        "rail": c["id"],
                    }
                )

        return {
            "module": self.name,
            "kept": kept,
            "removed": removed,
            "narrowed_variants": narrowed_variants,
            "kept_count": len(kept),
            "removed_count": len(removed),
            "true_hubs": sorted(true_hubs),
            "writing_rails": list(rails),
            "distortion_rate": round(
                len(removed) / max(1, len(removed) + len(kept)), 4
            ),
        }

    def _narrow(
        self,
        s: str,
        tokens: list[str],
        hubs: set[str],
        pmap: dict[str, Any],
    ) -> str:
        spine = (pmap.get("top_positive") or [{}])[0].get("text") or s
        tok = ", ".join(tokens[:4]) if tokens else "the stated operation"
        hub = next(iter(hubs), "operator")
        return (
            f"Given {tok}, the operational story centers on «{hub}» and the highest-probability "
            f"claim: {spine[:180]}"
        )
