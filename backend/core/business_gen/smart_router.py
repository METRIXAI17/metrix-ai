"""
Smart routers — multi-path routing for Generate / Core assembly.

Routes (parallel, scored):
  domain_router      → knowledge_library | agency_ops | resource | generic
  surface_router     → online | offline | hybrid
  depth_router       → explore | design | execute
  product_router     → which product cards to surface (core, personality, assist, packs)
  skill_router       → which stored skills to load into harness
  assist_router      → whether assist agent should draft implementation steps

Context-engineering style: route on goals/criteria, not giant prompts.
"""

from __future__ import annotations

import re
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def route_generate(
    business_text: str,
    *,
    channel: str = "auto",
    profile: dict[str, Any] | None = None,
    personality: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
    available_skills: list[dict[str, Any]] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    t = (business_text or "").lower()
    prof = profile or {}
    pers = personality or {}
    q = quality or {}
    conf = float(q.get("confidence") or 0.45)

    # Domain
    if prof.get("is_library") or any(
        w in t for w in ("библиотек", "library", "карточ", "архитект", "builder")
    ):
        domain = "knowledge_library"
    elif any(w in t for w in ("агентств", "agency", "rework", "handoff", "студи")):
        domain = "agency_ops"
    elif any(w in t for w in ("переработ", "recycl", "waste", "логист", "scrap")):
        domain = "resource_logistics"
    else:
        domain = "generic_ops"

    # Surface
    ch = (channel or "auto").lower()
    if ch in ("online", "offline", "hybrid"):
        surface = ch
    elif any(w in t for w in ("онлайн", "online", "saas", "web")):
        surface = "online"
    elif any(w in t for w in ("офлайн", "offline", "кафе", "store", "магазин")):
        surface = "offline"
    else:
        surface = "hybrid" if prof.get("is_online") else "auto"

    # Depth
    words = len(re.findall(r"\w+", t))
    if words < 25 or conf < 0.4:
        depth = "explore"
    elif conf < 0.65:
        depth = "design"
    else:
        depth = "execute"

    # Product surface mix
    products = [
        {"id": "rd_reader", "weight": 1.0, "free": True},
        {"id": "author_personality", "weight": 0.95, "free": True},
        {"id": "core_cards", "weight": 0.9, "free": True},
        {"id": "exports_free", "weight": 0.9, "free": True},
        {"id": "assist_agent", "weight": 0.85, "free": False, "unlock": "implementation_approval"},
        {"id": "client_pack", "weight": 0.55 if domain == "agency_ops" else 0.4, "free": False},
    ]
    products.sort(key=lambda x: -x["weight"])

    # Skills to load (harness dynamic skills)
    skills = list(available_skills or [])
    primary_axis = pers.get("primary_axis") or "builder"
    loaded = []
    for sk in skills:
        tags = set(sk.get("tags") or [])
        if domain in tags or primary_axis in tags or "universal" in tags:
            loaded.append(sk)
    loaded = loaded[:4]

    # Assist readiness
    assist_ready = depth in ("design", "execute") and conf >= 0.4
    path = [
        f"domain:{domain}",
        f"surface:{surface}",
        f"depth:{depth}",
        f"products:{','.join(p['id'] for p in products[:4])}",
        f"skills_loaded:{len(loaded)}",
        f"assist:{'ready' if assist_ready else 'hold'}",
    ]

    narrative = _d(
        lang,
        (
            f"Умный маршрут: домен **{domain}**, поверхность **{surface}**, глубина **{depth}**. "
            f"Harness подгружает {len(loaded)} skill(s); free surfaces: R&D reader + personality + exports. "
            f"Assist agent: {'готов к draft после approval' if assist_ready else 'ждёт criteria'}."
        ),
        (
            f"Smart route: domain **{domain}**, surface **{surface}**, depth **{depth}**. "
            f"Harness loads {len(loaded)} skill(s); free surfaces: R&D reader + personality + exports. "
            f"Assist agent: {'draft-ready after approval' if assist_ready else 'waiting on criteria'}."
        ),
    )

    return {
        "module": "SmartRouter",
        "version": "1.0",
        "domain": domain,
        "surface": surface,
        "depth": depth,
        "products": products,
        "skills_loaded": loaded,
        "assist_ready": assist_ready,
        "path": path,
        "narrative": narrative,
        "summary": narrative,
        "confidence": round(conf, 3),
        "lang": _lang(lang),
    }
