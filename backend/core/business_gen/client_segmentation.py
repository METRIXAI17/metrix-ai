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
    {
        "id": "own_contour",
        "label": "L.segment.own_contour",
        "name_ru": "Свой контур",
        "name_en": "Own contour",
        "keywords": ("свой", "моя", "мне", "контур", "касса", "понедельник"),
        "implement_fit": {"product_pack": 0.8, "unit_pack": 0.75, "ch_network": 0.4},
        "persona": "owner",
    },
    {
        "id": "web3_order",
        "label": "L.segment.web3_order",
        "name_ru": "Web3 заказ своего контура",
        "name_en": "Web3 order on their contour",
        "keywords": ("web3", "жертв", "ончейн", "on-chain", "токен", "wallet", "nft"),
        "implement_fit": {"product_pack": 0.72, "unit_pack": 0.7, "ch_network": 0.55},
        "persona": "web3_owner",
    },
    {
        "id": "b2c_person",
        "label": "L.segment.b2c_person",
        "name_ru": "Человек, не агентство",
        "name_en": "Person, not an agency",
        "keywords": ("мне", "я ", "жизнь", "день", "один"),
        "implement_fit": {"product_pack": 0.6, "unit_pack": 0.55, "ch_network": 0.35},
        "persona": "person",
    },
]


# Explicit "we sell to other companies" — only then B2B stays primary.
_SERVES_OTHERS = (
    "b2b",
    "агентств",
    "agency",
    "чужой бизнес",
    "чужих клиент",
    "для чужих",
    "handoff",
    "retainer",
)

_WEB3 = ("web3", "жертв", "ончейн", "on-chain", "токен", "wallet", "nft", "смарт-контракт")

MODERN_OWN = (
    {"id": "rooms", "ru": "Комнаты его двери, не новая линейка.", "en": "Rooms of their door, not a new line."},
    {"id": "b2c", "ru": "Если это человек — цепочка B2C, не матрица передач.", "en": "A person gets the B2C chain, not a handoff matrix."},
    {"id": "web3", "ru": "Понятие и заказ садятся в Web3 Store.", "en": "The notion and the order sit in Web3 Store."},
    {"id": "spec100", "ru": "$100 — кастом спека и варианты мелких задач.", "en": "$100 — custom spec and small-task variants."},
    {"id": "recurse490", "ru": "$490 — рекурсия на том же слоте.", "en": "$490 — recursion on the same slot."},
    {"id": "kill_b2b", "ru": "Не собирать бизнес для чужих клиентов.", "en": "Do not assemble a business for someone else's clients."},
)


def serves_other_businesses(text: str) -> bool:
    """True only when the brief asks to serve other companies.

    A kill line («не бизнес для чужих») is the opposite signal.
    """
    t = (text or "").lower()
    if any(w in t for w in ("b2b", "агентств", "agency", "handoff", "retainer")):
        return True
    if any(w in t for w in ("не для чуж", "не бизнес для", "не в бизнес", "свой контур", "вечный b2b")):
        return False
    return any(w in t for w in ("чужой бизнес", "чужих клиент", "для чужих"))


def _seg_by_id(sid: str) -> dict[str, Any]:
    for seg in SEGMENTS:
        if seg["id"] == sid:
            return seg
    return SEGMENTS[-3]


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
    others = serves_other_businesses(t)
    web3 = any(w in t for w in _WEB3)
    if others:
        primary = scores[0][1] if scores and scores[0][0] > 0 else {
            **_seg_by_id("founder_solo"),
            "hits": [],
            "raw_score": 0.0,
        }
    else:
        # Eternal B2B is off. Own contour / Web3 order / person — not a business for other people.
        picked = _seg_by_id("web3_order" if web3 else "own_contour")
        primary = {**picked, "hits": [h for h in picked["keywords"] if h in t], "raw_score": 3.0}
    secondary = [s[1] for s in scores if s[0] > 0 and s[1]["id"] != primary["id"]][:3]

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
        "eternal_b2b": others,
        "frame": "b2b_service" if others else ("web3_order" if web3 else "own_contour"),
        "modern": [] if others else [dict(m) for m in MODERN_OWN],
        "precision_note": (
            "Explicit B2B: they serve other businesses."
            if others and L == "en"
            else "Явный B2B: они обслуживают чужие бизнесы."
            if others
            else "Own contour. Eternal B2B is off — rooms, B2C, Web3, custom spec, recursion."
            if L == "en"
            else "Свой контур. Вечный B2B снят: комнаты, B2C, Web3, кастом спека, рекурсия."
        ),
    }
