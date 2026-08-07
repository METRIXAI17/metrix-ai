"""
Precise B2B client segmentation — wayD L.segment.* labels.

Maps brief signals → one primary segment + secondary tags + implement fit.
"""

from __future__ import annotations

from typing import Any


SEGMENTS: list[dict[str, Any]] = [
    {
        "id": "b2b_ops",
        "label": "L.segment.b2b_ops",
        "name_ru": "B2B операции / delivery",
        "name_en": "B2B ops / delivery",
        "keywords": (
            "handoff",
            "rework",
            "операц",
            "margin",
            "марж",
            "delivery",
            "доставк",
            "процесс",
            "sla",
            "scoreboard",
            "утеч",
        ),
        "implement_fit": {"product_pack": 0.55, "unit_pack": 0.7, "ch_network": 0.65},
        "persona": "ops_lead",
    },
    {
        "id": "b2b_product",
        "label": "L.segment.b2b_product",
        "name_ru": "B2B product / SaaS builders",
        "name_en": "B2B product / SaaS builders",
        "keywords": (
            "saas",
            "product",
            "продукт",
            "billing",
            "api",
            "feature",
            "roadmap",
            "интегр",
            "webhook",
            "builder",
            "билдер",
        ),
        "implement_fit": {"product_pack": 0.85, "unit_pack": 0.75, "ch_network": 0.55},
        "persona": "product_founder",
    },
    {
        "id": "b2b_knowledge",
        "label": "L.segment.b2b_knowledge",
        "name_ru": "Knowledge / library / expert packs",
        "name_en": "Knowledge / library / expert packs",
        "keywords": (
            "библиотек",
            "library",
            "карточ",
            "архитект",
            "architecture",
            "expert",
            "эксперт",
            "knowledge",
            "дизайн",
            "concept",
            "концепт",
            "ниш",
        ),
        "implement_fit": {"product_pack": 0.9, "unit_pack": 0.85, "ch_network": 0.7},
        "persona": "knowledge_publisher",
    },
    {
        "id": "agency",
        "label": "L.segment.agency",
        "name_ru": "Агентства и студии",
        "name_en": "Agencies & studios",
        "keywords": (
            "агентств",
            "agency",
            "студи",
            "studio",
            "клиент",
            "retainer",
            "пилот",
            "проектн",
        ),
        "implement_fit": {"product_pack": 0.6, "unit_pack": 0.65, "ch_network": 0.8},
        "persona": "agency_pm",
    },
    {
        "id": "founder_solo",
        "label": "L.segment.founder_solo",
        "name_ru": "Founder solo / micro-team",
        "name_en": "Founder solo / micro-team",
        "keywords": (
            "founder",
            "фаундер",
            "solo",
            "один",
            "сам",
            "micro",
            "стартап",
            "startup",
            "bootstr",
        ),
        "implement_fit": {"product_pack": 0.7, "unit_pack": 0.75, "ch_network": 0.75},
        "persona": "solo_founder",
    },
    {
        "id": "platform",
        "label": "L.segment.platform",
        "name_ru": "Platform / marketplace",
        "name_en": "Platform / marketplace",
        "keywords": (
            "platform",
            "платформ",
            "marketplace",
            "маркетплейс",
            "two-sided",
            "network effect",
            "ликвидн",
        ),
        "implement_fit": {"product_pack": 0.75, "unit_pack": 0.7, "ch_network": 0.85},
        "persona": "platform_ops",
    },
]


def segment_client(
    business_text: str,
    *,
    industry_id: str = "",
    profile: dict[str, Any] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """Score all segments; return primary + secondary + wayD labels."""
    t = f"{business_text or ''} {industry_id or ''}".lower()
    prof = profile or {}
    scores: list[tuple[float, dict[str, Any]]] = []

    for seg in SEGMENTS:
        s = 0.0
        hits = []
        for kw in seg["keywords"]:
            if kw in t:
                s += 1.0
                hits.append(kw)
        # profile priors
        if prof.get("is_library") and seg["id"] == "b2b_knowledge":
            s += 3.0
        if prof.get("profile") == "agency_ops" and seg["id"] == "agency":
            s += 2.5
        if industry_id in ("ai-agencies",) and seg["id"] == "agency":
            s += 1.5
        if industry_id in ("api-for-devs", "automation-builders") and seg["id"] == "b2b_product":
            s += 1.5
        if industry_id in ("expert-services",) and seg["id"] == "b2b_knowledge":
            s += 1.5
        scores.append((s, {**seg, "hits": hits, "raw_score": s}))

    scores.sort(key=lambda x: -x[0])
    primary = scores[0][1] if scores and scores[0][0] > 0 else {
        **SEGMENTS[4],  # founder_solo default
        "hits": [],
        "raw_score": 0.0,
    }
    secondary = [s[1] for s in scores[1:4] if s[0] > 0][:3]

    # normalize fit
    max_raw = max(scores[0][0], 1.0) if scores else 1.0
    segment_fit = min(1.0, 0.45 + 0.12 * min(primary.get("raw_score", 0), 5) + 0.05 * len(primary.get("hits") or []))

    L = "en" if (lang or "").lower().startswith("en") else "ru"
    return {
        "module": "ClientSegmentation",
        "version": "1.0.0",
        "primary": {
            "id": primary["id"],
            "label": primary["label"],
            "name": primary["name_en"] if L == "en" else primary["name_ru"],
            "persona": primary["persona"],
            "implement_fit": primary["implement_fit"],
            "hits": primary.get("hits") or [],
            "score": round(primary.get("raw_score", 0) / max_raw, 4),
        },
        "secondary": [
            {
                "id": s["id"],
                "label": s["label"],
                "name": s["name_en"] if L == "en" else s["name_ru"],
                "score": round(s.get("raw_score", 0) / max_raw, 4),
            }
            for s in secondary
        ],
        "segment_fit": round(segment_fit, 4),
        "all_ranked": [
            {"id": s[1]["id"], "score": round(s[0], 3), "label": s[1]["label"]} for s in scores[:6]
        ],
        "wayd_labels": [primary["label"]] + [s["label"] for s in secondary[:2]],
        "precision_note": (
            "Exact B2B segmentation from brief signals + industry + profile priors"
            if L == "en"
            else "Точная B2B-сегментация по сигналам брифа + industry + profile priors"
        ),
    }
