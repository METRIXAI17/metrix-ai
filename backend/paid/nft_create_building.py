"""
NFT Create-Building — query construction via keyword combinations.

Strange generations from system vocabulary + library of prior attempts.
Tertiary nets form rare words/groups from gaps. Scaffold only — no chain mint.
"""

from __future__ import annotations

import hashlib
import itertools
import re
from typing import Any

from backend.paid.types import clamp01, safe_float


# Expanded English terminology library for success-building tokens
VOCAB_CORE = (
    "orientation", "lever", "void", "ricochet", "pragma", "campus", "contour",
    "vector", "framework", "phase", "basis", "metric", "assembly", "adaptation",
    "stewardship", "frontier", "opportuner", "objectly", "harness", "live",
    "narrowing", "amplitude", "coherence", "anti-down", "sequence", "interlink",
    "yield", "utilization", "margin", "cycle-time", "ARPU", "churn", "rework",
    "edge", "placement", "batch", "precision", "replica", "cache", "signal",
    "noise", "protocol", "zone", "overlay", "superstructure", "embedding",
    "constructor", "fly-out", "double-bottom", "refragmentation", "virtual-asset",
    "token", "mint", "library", "gap", "tertiary", "strange-gen", "success-unit",
)

VOCAB_FOUNDER = (
    "system-design", "product-idea", "capital-efficiency", "sell-ops",
    "startup-success", "delivery-spine", "unit-economics", "blue-ocean",
    "meta-reality", "intelligence-platform", "asset-class", "create-building",
)


class NFTCreateBuilding:
    name = "NFT Create-Building"
    status = "live_scaffold"
    asset_class_name = "Intelligence Platform for Management of New Asset Class"

    def build(
        self,
        *,
        industry_id: str = "",
        business: str = "",
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        principles: dict[str, Any] | None = None,
        objectly: dict[str, Any] | None = None,
        prior_attempts: list[str] | None = None,
    ) -> dict[str, Any]:
        paid = paid or {}
        principles = principles or {}
        objectly = objectly or {}
        prior = list(prior_attempts or [])

        seeds = self._extract_keywords(business, idea_title, industry_id)
        # Stage-based keyword combo (each stage adds system words)
        stages = self._stage_supplies(paid, principles)
        generations = self._strange_generations(seeds, stages, prior)
        tertiary = self._tertiary_nets(generations, prior)

        token_id = hashlib.sha1(
            f"{idea_title}|{industry_id}|{generations[0] if generations else 'x'}".encode()
        ).hexdigest()[:12]

        price_anchor = safe_float(
            (objectly.get("objects") or [{}])[0].get("price_signal_usd")
            if objectly.get("objects")
            else 0,
            290 * safe_float(paid.get("paid_score"), 0.5),
        )

        return {
            "module": self.name,
            "status": self.status,
            "asset_class": self.asset_class_name,
            "token_draft": {
                "id": f"nftcb_{token_id}",
                "name": self._token_name(idea_title, industry_id),
                "keywords": seeds[:12],
                "price_anchor_usd": round(price_anchor, 2),
                "mint_ready": False,
                "class": "success_building_nft",
            },
            "query_construction": {
                "stages": stages,
                "method": (
                    "Each stage adds system supply keywords; combinations produce "
                    "strange generations; gaps feed tertiary nets."
                ),
            },
            "strange_generations": generations[:16],
            "tertiary_nets": tertiary,
            "library_touch": {
                "prior_attempts_used": len(prior),
                "vocab_core_size": len(VOCAB_CORE),
                "vocab_founder_size": len(VOCAB_FOUNDER),
            },
            "commercial_note": (
                "Not only code-building: founders can monetize system design, "
                "product ideas, and thinking as a managed asset class."
            ),
            "open_points": [
                "OPEN: wallet mint & royalty split",
                "OPEN: marketplace listing (Data Market handoff)",
            ],
            "honesty": "Draft token metadata only — no blockchain write in this layer.",
        }

    def _extract_keywords(
        self, business: str, idea_title: str, industry_id: str
    ) -> list[str]:
        text = f"{idea_title} {business} {industry_id}".lower()
        words = re.findall(r"[a-zа-яё]{4,}", text, flags=re.I)
        # Prefer longer unique
        seen: set[str] = set()
        out: list[str] = []
        for w in words:
            wl = w.lower()
            if wl not in seen and len(wl) >= 4:
                seen.add(wl)
                out.append(wl)
        # Inject industry + founder vocab hits
        for v in VOCAB_FOUNDER:
            if v.split("-")[0] in text or industry_id.replace("-", " ") in v:
                if v not in out:
                    out.append(v)
        if industry_id and industry_id not in out:
            out.insert(0, industry_id)
        return out[:20] or ["orientation", "lever", "success-unit"]

    def _stage_supplies(
        self, paid: dict[str, Any], principles: dict[str, Any]
    ) -> list[dict[str, Any]]:
        active = principles.get("active_principles") or []
        supplies = [
            {"stage": 1, "supply": "perception", "keywords": ["intake", "sector", "sign"]},
            {"stage": 2, "supply": "notation", "keywords": ["metric", "name", "boundary"]},
            {
                "stage": 3,
                "supply": "objectification",
                "keywords": ["virtual-asset", "weight", "owner"],
            },
            {
                "stage": 4,
                "supply": "interpretation",
                "keywords": ["energy", "zone", "pattern"],
            },
            {
                "stage": 5,
                "supply": "application",
                "keywords": ["sequence", "anti-down", "live"],
            },
        ]
        # Enrich from active principles
        for i, p in enumerate(active[:5]):
            if isinstance(p, dict) and p.get("key"):
                supplies[min(i, 4)]["keywords"].append(p["key"])
        return supplies

    def _strange_generations(
        self,
        seeds: list[str],
        stages: list[dict[str, Any]],
        prior: list[str],
    ) -> list[dict[str, Any]]:
        gens: list[dict[str, Any]] = []
        stage_words = []
        for s in stages:
            stage_words.extend(s.get("keywords") or [])
        pool = list(dict.fromkeys(seeds[:6] + stage_words[:8] + list(VOCAB_CORE[:10])))
        # Combinations of 2–3
        for combo in itertools.combinations(pool[:10], 2):
            phrase = " · ".join(combo)
            gens.append(
                {
                    "phrase": phrase,
                    "kind": "pair_combo",
                    "rarity": round(0.3 + 0.05 * len(phrase) % 7, 3),
                }
            )
            if len(gens) >= 10:
                break
        for combo in itertools.combinations(pool[:8], 3):
            phrase = " / ".join(combo)
            gens.append(
                {
                    "phrase": phrase,
                    "kind": "triple_strange",
                    "rarity": round(0.55 + 0.03 * abs(hash(phrase)) % 10 / 10, 3),
                }
            )
            if len(gens) >= 16:
                break
        # Self-library: recombine with prior
        for p in prior[:3]:
            gens.append(
                {
                    "phrase": f"{p} ⊕ {pool[0] if pool else 'orientation'}",
                    "kind": "library_recombine",
                    "rarity": 0.7,
                }
            )
        return gens

    def _tertiary_nets(
        self, generations: list[dict[str, Any]], prior: list[str]
    ) -> dict[str, Any]:
        """Gaps in common meaning groups form rare word clusters."""
        tokens: list[str] = []
        for g in generations:
            tokens.extend(re.split(r"[\s·/⊕]+", g.get("phrase", "")))
        tokens = [t for t in tokens if t and len(t) > 2]
        # Group by first letter / length band (simple gap clustering)
        groups: dict[str, list[str]] = {}
        for t in tokens:
            key = f"L{min(9, len(t))}_{t[0].lower()}"
            groups.setdefault(key, [])
            if t not in groups[key]:
                groups[key].append(t)
        # Rare = groups with 1–2 members
        rare = {k: v for k, v in groups.items() if 1 <= len(v) <= 2}
        common = {k: v for k, v in groups.items() if len(v) >= 3}
        # Gaps between common groups → synthetic rare
        synthetic = []
        common_keys = list(common.keys())
        for i in range(min(4, max(0, len(common_keys) - 1))):
            a = common[common_keys[i]][0]
            b = common[common_keys[i + 1]][0]
            synthetic.append(f"{a[:3]}-{b[-3:]}-gap")
        return {
            "common_groups": {k: v[:5] for k, v in list(common.items())[:6]},
            "rare_groups": {k: v for k, v in list(rare.items())[:8]},
            "synthetic_from_gaps": synthetic,
            "prior_gap_links": prior[:3],
            "note": "Tertiary net: common groups leave gaps; gaps form rare words/clusters.",
        }

    def _token_name(self, idea_title: str, industry_id: str) -> str:
        base = (idea_title or "Success Unit").strip()[:40]
        ind = (industry_id or "meta").split("-")[0]
        return f"SB-{ind}-{base}".replace(" ", "_")
