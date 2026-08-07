"""
Expert base of most popular directions (tasks) — priors for GenCore + paths.
"""

from __future__ import annotations

from typing import Any


POPULAR_DIRECTIONS: list[dict[str, Any]] = [
    {
        "id": "arch_library",
        "rank": 1,
        "name_ru": "Библиотека архитектурных дизайнов",
        "name_en": "Architecture design library",
        "direction_keys": ["product_pack", "unit_pack"],
        "tasks": [
            {"id": "T01", "ru": "Карточки ниш A01–A12", "en": "Niche cards A01–A12"},
            {"id": "T02", "ru": "Concept tests T1–T3", "en": "Concept tests T1–T3"},
            {"id": "T03", "ru": "Unit pack → paid design-review", "en": "Unit pack → paid design-review"},
        ],
        "playbooks": [
            "Ship 3 deep niches before platform talk",
            "One proof artifact / 7d, not 5 channels",
        ],
        "anti_patterns": ["auto-yield", "open retainer v0", "wiki bulk without unit"],
        "keywords": ("библиотек", "library", "архитект", "architecture", "карточ"),
    },
    {
        "id": "agency_rework",
        "rank": 2,
        "name_ru": "Снижение rework в AI-агентстве",
        "name_en": "Cut rework in AI agency",
        "direction_keys": ["unit_pack", "ch_network"],
        "tasks": [
            {"id": "T01", "ru": "Handoff scoreboard", "en": "Handoff scoreboard"},
            {"id": "T02", "ru": "One delivery metric", "en": "One delivery metric"},
            {"id": "T03", "ru": "Warm referral 7d log", "en": "Warm referral 7d log"},
        ],
        "playbooks": ["Margin first, volume second", "Kill scope creep at T1"],
        "anti_patterns": ["5 parallel channels", "guaranteed income"],
        "keywords": ("агентств", "agency", "rework", "handoff", "студи"),
    },
    {
        "id": "api_cost_cut",
        "rank": 3,
        "name_ru": "Резание API/LLM spend без потери качества",
        "name_en": "Cut API/LLM spend without quality loss",
        "direction_keys": ["product_pack", "unit_pack"],
        "tasks": [
            {"id": "T01", "ru": "Route cheap vs premium models", "en": "Route cheap vs premium models"},
            {"id": "T02", "ru": "Cache + template spine", "en": "Cache + template spine"},
            {"id": "T03", "ru": "Cost unit on every SKU", "en": "Cost unit on every SKU"},
        ],
        "playbooks": ["Measure $/accepted outcome, not $/token vanity"],
        "anti_patterns": ["blind model downgrade"],
        "keywords": ("api", "openai", "anthropic", "token", "llm", "cost", "затрат"),
    },
    {
        "id": "expert_sku",
        "rank": 4,
        "name_ru": "Экспертный SKU / 90-day pack",
        "name_en": "Expert SKU / 90-day pack",
        "direction_keys": ["product_pack", "unit_pack"],
        "tasks": [
            {"id": "T01", "ru": "Promise · boundary · pack", "en": "Promise · boundary · pack"},
            {"id": "T02", "ru": "Acceptance criteria page", "en": "Acceptance criteria page"},
            {"id": "T03", "ru": "Single stop-rule", "en": "Single stop-rule"},
        ],
        "playbooks": ["One paid step, no infogypsy ladder"],
        "anti_patterns": ["hourly forever"],
        "keywords": ("expert", "эксперт", "consult", "sku", "пакет", "90"),
    },
    {
        "id": "automation_builder",
        "rank": 5,
        "name_ru": "Automation / product builder desk",
        "name_en": "Automation / product builder desk",
        "direction_keys": ["product_pack", "ch_network"],
        "tasks": [
            {"id": "T01", "ru": "WIP=3 from architecture cards", "en": "WIP=3 from architecture cards"},
            {"id": "T02", "ru": "Pilot widgets ×3", "en": "Pilot widgets ×3"},
            {"id": "T03", "ru": "Builder DM list", "en": "Builder DM list"},
        ],
        "playbooks": ["Orient → pick → ship"],
        "anti_patterns": ["40 KPI dashboard"],
        "keywords": ("automat", "автомат", "builder", "билдер", "workflow", "no-code"),
    },
    {
        "id": "content_proof",
        "rank": 6,
        "name_ru": "Proof-контент + lookalike касания",
        "name_en": "Proof content + lookalike touches",
        "direction_keys": ["ch_network"],
        "tasks": [
            {"id": "T01", "ru": "1 proof post / week", "en": "1 proof post / week"},
            {"id": "T02", "ru": "12 touches / 7d", "en": "12 touches / 7d"},
            {"id": "T03", "ru": "Artifact ship gate", "en": "Artifact ship gate"},
        ],
        "playbooks": ["Same product · better ops analytics · different money"],
        "anti_patterns": ["hype without decision lock"],
        "keywords": ("content", "контент", "proof", "x.com", "audience"),
    },
    {
        "id": "asset_decision",
        "rank": 7,
        "name_ru": "Asset decision / risk criteria",
        "name_en": "Asset decision / risk criteria",
        "direction_keys": ["unit_pack"],
        "tasks": [
            {"id": "T01", "ru": "Risk criteria without yield promise", "en": "Risk criteria without yield promise"},
            {"id": "T02", "ru": "Decision card genome", "en": "Decision card genome"},
        ],
        "playbooks": ["No auto-yield hard rail"],
        "anti_patterns": ["guaranteed APY language"],
        "keywords": ("asset", "актив", "yield", "risk", "капитал"),
    },
    {
        "id": "integration_tz",
        "rank": 8,
        "name_ru": "Интеграции: scope + приёмка",
        "name_en": "Integrations: scope + acceptance",
        "direction_keys": ["product_pack", "unit_pack"],
        "tasks": [
            {"id": "T01", "ru": "1-page TZ + 3 accept scenarios", "en": "1-page TZ + 3 accept scenarios"},
            {"id": "T02", "ru": "Non-goals list", "en": "Non-goals list"},
        ],
        "playbooks": ["Hand to executor today"],
        "anti_patterns": ["open-ended scope"],
        "keywords": ("integrat", "интегр", "webhook", "feature", "тз"),
    },
]


def match_expert_directions(
    business_text: str,
    *,
    lang: str = "ru",
    top_k: int = 4,
) -> dict[str, Any]:
    t = (business_text or "").lower()
    L = "en" if (lang or "").lower().startswith("en") else "ru"
    ranked: list[dict[str, Any]] = []
    for d in POPULAR_DIRECTIONS:
        hits = [kw for kw in d["keywords"] if kw in t]
        score = float(len(hits)) + (0.15 if d["rank"] <= 3 else 0.0)
        if hits or d["rank"] <= 3:
            ranked.append({**d, "match_score": score, "hits": hits})
    ranked.sort(key=lambda x: (-x["match_score"], x["rank"]))
    if not any(r["hits"] for r in ranked):
        # default top popular
        ranked = [{**d, "match_score": 0.2, "hits": []} for d in POPULAR_DIRECTIONS[:top_k]]
    top = ranked[:top_k]

    tasks = []
    for d in top:
        for task in d.get("tasks") or []:
            tasks.append(
                {
                    "direction_id": d["id"],
                    "task_id": task["id"],
                    "text": task["en"] if L == "en" else task["ru"],
                }
            )

    return {
        "module": "ExpertBaseDirections",
        "version": "1.0.0",
        "top": [
            {
                "id": d["id"],
                "rank": d["rank"],
                "name": d["name_en"] if L == "en" else d["name_ru"],
                "direction_keys": d["direction_keys"],
                "match_score": round(d["match_score"], 3),
                "hits": d["hits"],
                "playbooks": d["playbooks"],
                "anti_patterns": d["anti_patterns"],
                "tasks": [
                    {"id": t["id"], "text": t["en"] if L == "en" else t["ru"]}
                    for t in d.get("tasks") or []
                ],
            }
            for d in top
        ],
        "flat_tasks": tasks[:16],
        "catalog_size": len(POPULAR_DIRECTIONS),
        "message": (
            f"Expert base: top {len(top)} popular directions matched"
            if L == "en"
            else f"Экспертная база: top {len(top)} популярных направлений"
        ),
    }


def list_all_directions(lang: str = "ru") -> list[dict[str, Any]]:
    L = "en" if (lang or "").lower().startswith("en") else "ru"
    return [
        {
            "id": d["id"],
            "rank": d["rank"],
            "name": d["name_en"] if L == "en" else d["name_ru"],
            "direction_keys": d["direction_keys"],
        }
        for d in sorted(POPULAR_DIRECTIONS, key=lambda x: x["rank"])
    ]
