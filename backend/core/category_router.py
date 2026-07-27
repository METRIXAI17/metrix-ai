"""
Category Router — ops / product / promotion recommendation + mid-flow questions.

Goals:
- Score three tracks from brief + numbers + industry sanity (not random)
- Ask 2–4 clarifying questions in the middle when confidence is low
- Output ranked tracks with plain-language reasons
"""

from __future__ import annotations

import re
from typing import Any


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


TRACK_LABELS = {
    "ops": {"en": "Operational success", "ru": "Операционный успех"},
    "product": {"en": "Product", "ru": "Продукт"},
    "promotion": {"en": "Promotion / angle", "ru": "Продвижение / угол"},
}

# Keyword weights per track
_KW: dict[str, list[str]] = {
    "ops": [
        "rework", "utilization", "margin", "delivery", "ops", "process", "waste",
        "efficiency", "cycle", "scope", "discovery", "retainer", "sla", "churn",
        "api", "token", "cost", "yield", "rework", "операц", "маржа", "переработ",
        "процесс", "себестоим", "загрузк",
    ],
    "product": [
        "product", "sku", "feature", "teammate", "platform", "tool", "spec",
        "build", "mvp", "package", "offer", "attach", "console", "expert",
        "продукт", "функц", "спецификац", "сборк", "оффер",
    ],
    "promotion": [
        "promo", "marketing", "ads", "content", "post", "outreach", "lead",
        "brand", "funnel", "audience", "event", "angle", "dm", "campaign",
        "продвиж", "реклам", "контент", "лид", "бренд", "воронк", "аудитор",
    ],
}


def _score_track(text: str, track: str, nums: dict[str, float]) -> float:
    t = (text or "").lower()
    hits = sum(1 for k in _KW[track] if k in t)
    base = min(1.0, hits / 6.0)
    # Numbers push ops
    if track == "ops":
        if safe_float(nums.get("rework")) >= 0.15:
            base += 0.18
        if safe_float(nums.get("utilization")) and safe_float(nums.get("utilization")) < 0.6:
            base += 0.12
        if safe_float(nums.get("gross_margin")) and safe_float(nums.get("gross_margin")) < 0.4:
            base += 0.1
        if safe_float(nums.get("churn")) >= 0.05:
            base += 0.08
    if track == "product":
        if any(w in t for w in ("sku", "package", "productize", "teammate", "expert")):
            base += 0.15
        if "spec" in t or "build" in t:
            base += 0.08
    if track == "promotion":
        if any(w in t for w in ("lead", "ads", "content", "outreach", "event", "бренд")):
            base += 0.15
        if not nums:
            base += 0.05  # soft briefs often need angle first
    return clamp01(base)


def route_categories(
    *,
    business: str,
    industry_id: str = "",
    nums: dict[str, float] | None = None,
    sanity_hints: dict[str, Any] | None = None,
    lang: str = "en",
    preferred_track: str | None = None,
) -> dict[str, Any]:
    nums = nums or {}
    sanity_hints = sanity_hints or {}
    scores = {
        tr: _score_track(business, tr, nums) for tr in ("ops", "product", "promotion")
    }
    # Industry priors from sanity pack
    priors = (sanity_hints.get("track_priors") or {}) if sanity_hints else {}
    for tr, p in priors.items():
        if tr in scores:
            scores[tr] = clamp01(0.7 * scores[tr] + 0.3 * safe_float(p))

    # Map form track (product|models|promotion) → router tracks
    pref_raw = (preferred_track or "").lower().strip()
    pref_map = {
        "product": "product",
        "models": "product",  # teammate / models surface → product lane
        "promotion": "promotion",
        "ops": "ops",
        "all": "",
    }
    pref = pref_map.get(pref_raw, "")
    if pref and pref in scores:
        scores[pref] = clamp01(scores[pref] + 0.18)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top, top_s = ranked[0]
    second_s = ranked[1][1]
    conf = top_s - second_s
    # Natural recommendation before preference bias (for UI honesty)
    scores_unbiased = {
        tr: _score_track(business, tr, nums) for tr in ("ops", "product", "promotion")
    }
    for tr, p in priors.items():
        if tr in scores_unbiased:
            scores_unbiased[tr] = clamp01(
                0.7 * scores_unbiased[tr] + 0.3 * safe_float(p)
            )
    natural = sorted(scores_unbiased.items(), key=lambda kv: kv[1], reverse=True)[0][0]

    reasons = {
        "ops": {
            "en": "Your brief stresses delivery, cost, rework, or utilization — fix the machine first.",
            "ru": "В брифе упор на поставку, себестоимость, rework или загрузку — сначала чиним машину.",
        },
        "product": {
            "en": "You need a clearer thing to sell or attach (SKU / Teammate / Expert), not only process talk.",
            "ru": "Нужен более ясный объект продажи/attach (SKU / Teammate / Expert), не только процесс.",
        },
        "promotion": {
            "en": "Reach and angle look thinner than the offer — promotion is the bottleneck.",
            "ru": "Охват и угол слабее оффера — узкое место в продвижении.",
        },
    }

    questions: list[dict[str, str]] = []
    if conf < 0.12 or top_s < 0.35:
        questions = [
            {
                "id": "q_bottleneck",
                "en": "What hurts cash more this month: delivery rework, unclear product, or not enough leads?",
                "ru": "Что сильнее бьёт по деньгам в этом месяце: rework в поставке, неясный продукт или мало лидов?",
            },
            {
                "id": "q_owner",
                "en": "Who will own the next 14 days — ops lead, product owner, or marketer?",
                "ru": "Кто владелец следующих 14 дней — ops, продукт или маркетинг?",
            },
            {
                "id": "q_stop",
                "en": "What will you stop doing if we pick one track only?",
                "ru": "От чего откажетесь, если выберем только один трек?",
            },
        ]
        if industry_id == "cloud-economy":
            questions.append(
                {
                    "id": "q_api",
                    "en": "Is third-party API/token spend already a line item you watch weekly?",
                    "ru": "Расход на сторонние API/токены — это уже еженедельная строка в учёте?",
                }
            )
        if industry_id == "ai-agencies":
            questions.append(
                {
                    "id": "q_discovery",
                    "en": "Is free discovery still the default door for new clients?",
                    "ru": "Бесплатный discovery всё ещё дефолтная дверь для новых клиентов?",
                }
            )

    tracks_out = []
    for tr, sc in ranked:
        tracks_out.append(
            {
                "id": tr,
                "label": TRACK_LABELS[tr].get(lang) or TRACK_LABELS[tr]["en"],
                "score": round(sc, 4),
                "reason": reasons[tr].get(lang) or reasons[tr]["en"],
            }
        )

    return {
        "module": "Category Router",
        "primary": top,
        "primary_label": TRACK_LABELS[top].get(lang) or TRACK_LABELS[top]["en"],
        "natural_primary": natural,
        "natural_label": TRACK_LABELS[natural].get(lang) or TRACK_LABELS[natural]["en"],
        "user_preferred": pref or None,
        "confidence": round(conf, 4),
        "needs_clarifying": len(questions) > 0,
        "tracks": tracks_out,
        "mid_questions": questions,
        "pricing_hint": {
            "ops": {"pilot_usd": 690, "attach_usd": 990},
            "product": {"pilot_usd": 790, "attach_usd": 1190},
            "promotion": {"pilot_usd": 490, "attach_usd": 890},
        },
    }
