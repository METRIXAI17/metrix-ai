"""A2A mass-market outreach. Distribution 3D — not B2C ads, not spam scripts."""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.copy_firmware import CopyFirmware
from backend.monetization.distribution import DistributionEngine
from backend.paid.types import clamp01


class A2AMassmarketOutreach:
    name = "A2A Massmarket Outreach"
    flag = "massmarket_a2a"

    def run(
        self,
        *,
        industry_id: str = "ai-agencies",
        business_text: str = "",
        a2a_chain: dict[str, Any] | None = None,
        lang: str = "en",
    ) -> dict[str, Any]:
        try:
            built = DistributionEngine().build(
                industry_id=industry_id,
                industry_name=industry_id,
                idea_title=(business_text or "A2A massmarket")[:72],
                lang=lang,
            )
            dist_d = built.to_dict()
        except Exception:
            dist_d = {"brand": {}, "platforms": [], "networks": []}

        fw = CopyFirmware()
        ru = lang.startswith("ru")
        artefacts = [
            fw.offer_block(
                who="agency partner" if not ru else "агентство-партнёр",
                void="attention liquidity on a simple market",
                gate="sync_score≥0.5 and deadlock≠high",
                price="outreach artefact, not a lead promise",
                not_included="B2C ads, spam sequences, D2C offramp badge",
                voice="a2a",
                lang=lang,
            ),
            {
                "id": "mm_meaning_pack",
                "title": "Mass-market meaning pack" if not ru else "Пакет смыслов массрынка",
                "body": (
                    "Sell the simple thing to a simple market without killing RRC of the original product."
                    if not ru
                    else "Продавать простое простому рынку, не убивая RRC оригинального продукта."
                ),
                "voice": "a2a",
            },
            {
                "id": "mm_teammate_seq",
                "title": "Outreach as teammate algorithm",
                "steps": [
                    "Name the slot owner",
                    "Hand the artefact, not a pitch deck",
                    "Stop if deadlock_risk is high",
                ],
                "not": "spam-script",
            },
        ]
        graph = {
            "nodes": ["brand", "platforms", "networking", "a2a_chain"],
            "edges": [
                {"from": "brand", "to": "platforms", "kind": "meaning"},
                {"from": "platforms", "to": "networking", "kind": "attention"},
                {"from": "networking", "to": "a2a_chain", "kind": "liquidity"},
            ],
            "flag": self.flag,
            "not_mixed_with": "d2c-offramp",
        }
        iroi_delta = clamp01(0.04 + 0.06 * float((a2a_chain or {}).get("sync_score") or 0.4))
        return {
            "module": self.name,
            "flag": self.flag,
            "surface": "Shift · Assistant · Interface",
            "networking_graph": graph,
            "outreach_artefacts": artefacts,
            "distribution": dist_d,
            "iroi_delta": round(iroi_delta, 4),
            "lead_promise": False,
            "a2a_chain_id": (a2a_chain or {}).get("chain_id"),
        }
