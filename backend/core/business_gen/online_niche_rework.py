"""
Online-business niche rework — dedicated prompt + executor.

When the executor is an *online business* (SaaS, library, e-com, content,
automation, expert digital packs), this module reworks client niches with:
  - originality inject
  - wayD segment/path
  - sophisticated path packs
  - acceptance forecast
  - multi-pass quality signals

Prompt piece is exported as ONLINE_NICHE_PROMPT for LLM / human ops use.
"""

from __future__ import annotations

from typing import Any

from backend.core.business_gen.client_segmentation import segment_client
from backend.core.business_gen.expert_base_directions import match_expert_directions
from backend.core.business_gen.user_paths import select_user_path
from backend.core.business_gen.originality_inject import inject_three_directions, inject_originality
from backend.core.business_gen.acceptance_forecast import forecast_acceptance
from backend.core.business_gen.core_deliverable import _detect_profile
from backend.core.wayd import stamp_labels, compute_terminal, compose_edges


ONLINE_NICHE_PROMPT = """
# PROMPT · Online-business niche rework (Metrix AI)

## Role
You are a Metrix wayD niche architect. The **executor is an online business**
(digital product, SaaS, knowledge library, e-com, content, automation, expert packs).
Your job is to rework and improve client niches so they are:
  - non-template (originality inject)
  - segment-locked
  - path-sophisticated (premium artifacts)
  - acceptance-ready (single stop-rule, A01–A12 steps, live log)

## Hard rails
1. No auto-yield / income guarantees
2. One stop-rule, not many falsifiers
3. A01–A12 are path steps — never call them «наполнение»
4. Paid implement (3 directions) stays hidden on public surface
5. Prefer unit + proof over vanity channels

## Inputs
- business_brief
- optional: industry_id, lang, multi_pass count

## Process
1. Detect online executor (saas / library / e-com / content / automation / expert digital)
2. Segment client (L.segment.*)
3. Match expert popular directions
4. Select sophisticated user path (L.path.*)
5. Rewrite niche cards / claims with originality banks for product_pack · unit_pack · ch_network
6. Forecast acceptance P
7. Stamp wayD labels + edge mesh unique functions
8. Output improved niche pack (RU/EN pure)

## Output schema
{
  "online_executor": true,
  "segment": {...},
  "path": {...},
  "expert_top": [...],
  "niches_reworked": [{ "id", "title", "claim", "proof", "originality" }],
  "three_directions_text": { product_pack, unit_pack, ch_network },
  "acceptance": { acceptance_p, band, actions },
  "wayd": { labels, terminal, unique_functions },
  "ops_next": [...]
}

## Style
Calm business engineering. Proof before promises. Orient → pick → ship.
"""


# Online-executor signal lexicon
_ONLINE_SIGNALS = (
    "online",
    "онлайн",
    "saas",
    "digital",
    "web",
    "сайт",
    "app",
    "library",
    "библиотек",
    "marketplace",
    "маркетплейс",
    "ecommerce",
    "e-com",
    "content",
    "контент",
    "automation",
    "автомат",
    "no-code",
    "api",
    "subscription",
    "подписк",
    "course",
    "курс",
    "expert",
    "эксперт",
    "builder",
    "билдер",
    "platform",
    "платформ",
)


def is_online_executor(business_text: str, profile: dict[str, Any] | None = None) -> bool:
    t = (business_text or "").lower()
    if any(s in t for s in _ONLINE_SIGNALS):
        return True
    prof = profile or {}
    if prof.get("is_online") or prof.get("is_library"):
        return True
    if (prof.get("profile") or "") in ("knowledge_library",):
        return True
    return False


# Seed niche genomes for online businesses (improved claims)
_NICHE_GENOME: list[dict[str, str]] = [
    {
        "id": "N01",
        "title_ru": "Unit pack под online cycle",
        "title_en": "Unit pack for online cycle",
        "claim_ru": "Один paid unit с time-COGS, не «готовое решение» на витрине.",
        "claim_en": "One paid unit with time-COGS — not a storefront «ready solution».",
        "proof_ru": "≥1 paid unit / 21d · margin после времени.",
        "proof_en": "≥1 paid unit / 21d · margin after time.",
    },
    {
        "id": "N02",
        "title_ru": "Warm list + 1 proof artifact",
        "title_en": "Warm list + 1 proof artifact",
        "claim_ru": "12 касаний / 7 дней · один proof, не «сетевой эффект».",
        "claim_en": "12 touches / 7 days · one proof — not «network effect».",
        "proof_ru": "Live log complete + artifact shipped.",
        "proof_en": "Live log complete + artifact shipped.",
    },
    {
        "id": "N03",
        "title_ru": "Identity hash-unique",
        "title_en": "Identity hash-unique",
        "claim_ru": "Уникальность под бриф, не шаблонный бренд-kit.",
        "claim_en": "Uniqueness to the brief — not a template brand kit.",
        "proof_ru": "Delight ≥ 0.7 + identity answers filled.",
        "proof_en": "Delight ≥ 0.7 + identity answers filled.",
    },
    {
        "id": "N04",
        "title_ru": "API/cost unit (if applicable)",
        "title_en": "API/cost unit (if applicable)",
        "claim_ru": "$/accepted outcome, не vanity tokens.",
        "claim_en": "$/accepted outcome, not vanity tokens.",
        "proof_ru": "Cost unit on SKU card.",
        "proof_en": "Cost unit on SKU card.",
    },
    {
        "id": "N05",
        "title_ru": "Acceptance page",
        "title_en": "Acceptance page",
        "claim_ru": "Критерии приёмки + один stop-rule.",
        "claim_en": "Acceptance criteria + single stop-rule.",
        "proof_ru": "P(accept) band high · C1–C6 pass.",
        "proof_en": "P(accept) band high · C1–C6 pass.",
    },
    {
        "id": "N06",
        "title_ru": "Deep niche cards A01–A06",
        "title_en": "Deep niche cards A01–A06",
        "claim_ru": "Шаги пути, не наполнение ради объёма.",
        "claim_en": "Path steps — not filler for bulk.",
        "proof_ru": "≥6 architecture cards with niche tags.",
        "proof_en": "≥6 architecture cards with niche tags.",
    },
]


def rework_online_niches(
    business_text: str,
    *,
    industry_id: str = "",
    lang: str = "ru",
    multi_pass: int = 3,
    project_name: str = "",
) -> dict[str, Any]:
    """
    Execute the online-niche rework prompt against Metrix modules
    (originality, segment, path, acceptance, wayD).
    """
    L = "en" if (lang or "").lower().startswith("en") else "ru"
    prof = _detect_profile(business_text)
    online = is_online_executor(business_text, prof)

    seg = segment_client(business_text, industry_id=industry_id, profile=prof, lang=lang)
    path = select_user_path(
        business_text,
        segment_id=(seg.get("primary") or {}).get("id") or "",
        lang=lang,
        sophisticated=True,
    )
    expert = match_expert_directions(business_text, lang=lang, top_k=5)

    # Multi-pass originality on niche claims
    niches_out: list[dict[str, Any]] = []
    orig_scores: list[float] = []
    for i, n in enumerate(_NICHE_GENOME):
        raw = n["claim_en"] if L == "en" else n["claim_ru"]
        best = raw
        best_o = 0.0
        for p in range(max(1, min(multi_pass, 7))):
            inj = inject_originality(
                raw,
                direction=["product_pack", "unit_pack", "ch_network"][i % 3],
                lang=lang,
                seed=f"{project_name or 'online'}:{n['id']}:p{p}:{business_text[:40]}",
            )
            if float(inj.get("originality") or 0) >= best_o:
                best_o = float(inj["originality"])
                best = inj.get("text") or raw
        orig_scores.append(best_o)
        niches_out.append(
            {
                "id": n["id"],
                "title": n["title_en"] if L == "en" else n["title_ru"],
                "claim": best,
                "proof": n["proof_en"] if L == "en" else n["proof_ru"],
                "originality": round(best_o, 4),
                "passes": multi_pass,
            }
        )

    # Three directions rich text from niches + path
    product_body = " ".join(n["claim"] for n in niches_out[:3])
    unit_body = " ".join(n["claim"] for n in niches_out[2:5])
    ch_body = " ".join(n["claim"] for n in niches_out[1:4])
    three = inject_three_directions(
        {
            "product_pack": product_body,
            "unit_pack": unit_body,
            "ch_network": ch_body,
        },
        lang=lang,
        seed=f"online_rework:{(project_name or business_text)[:48]}",
    )

    mean_orig = sum(orig_scores) / len(orig_scores) if orig_scores else 0.5
    acc = forecast_acceptance(
        originality=float(three.get("originality") or mean_orig),
        segment_fit=float(seg.get("segment_fit") or 0.5),
        path_fit=float(path.get("path_fit") or 0.5),
        path_sophistication=float((path.get("path") or {}).get("sophistication") or 0.8),
        core_report={
            "markdown": "Single stop-rule · A01 path steps · resume + tech context",
            "counts": {"total_cards": 12},
            "architecture_cards": [{"id": f"A{i:02d}"} for i in range(1, 13)],
        },
        live_log={"id": "preview", "days": [{"done": False}] * 7},
        gencore={"slots": {f"v{i}": {"status": "ready"} for i in range(1, 6)}},
        lang=lang,
    )

    labels = stamp_labels(
        direction_ids=["product_pack", "unit_pack", "ch_network"],
        segment_id=(seg.get("primary") or {}).get("id"),
        path_id=(path.get("path") or {}).get("id"),
        extra=["L.edge.segment_x_path", "L.edge.accept_x_originality", "L.edge.expert_x_gencore"],
        rails=True,
    )
    mesh = compose_edges(
        [
            "gencore",
            "live_log",
            "client_segmentation",
            "user_paths",
            "acceptance_forecast",
            "originality_inject",
            "expert_base_directions",
            "wayd",
        ],
        quality_boost=mean_orig,
        segment_fit=float(seg.get("segment_fit") or 0.5),
        path_fit=float(path.get("path_fit") or 0.5),
    ).to_dict()
    terminal = compute_terminal(
        acceptance_p=float(acc.get("acceptance_p") or 0.55),
        originality=float(three.get("originality") or mean_orig),
        path_fit=float(path.get("path_fit") or 0.5),
        segment_fit=float(seg.get("segment_fit") or 0.5),
        edge_count=int(mesh.get("edge_count") or 0),
        edge_strength=float(mesh.get("edge_strength") or 0),
    ).to_dict()

    ops_next = [
        "Lock spine product_pack → unit_pack → ch_network",
        "Run GenCore v5/v6 with identity answers",
        "Open live log · tick ≥3 days · ship proof artifact",
        "Robotics harness R0–R6 on implement approval",
    ]
    if L == "ru":
        ops_next = [
            "Зафиксировать spine product_pack → unit_pack → ch_network",
            "GenCore v5/v6 после identity answers",
            "Live log · ≥3 ticks · ship proof artifact",
            "Robotics harness R0–R6 после approval внедрения",
        ]

    return {
        "module": "OnlineNicheRework",
        "version": "1.0.0",
        "prompt_id": "ONLINE_NICHE_PROMPT",
        "online_executor": online,
        "profile": prof.get("profile"),
        "project_name": project_name or "",
        "segment": seg,
        "path": path,
        "expert_top": expert.get("top") or [],
        "niches_reworked": niches_out,
        "three_directions_text": {
            k: (v.get("text") if isinstance(v, dict) else v)
            for k, v in (three.get("by_direction") or {}).items()
        },
        "originality": three,
        "acceptance": acc,
        "wayd": {
            "labels": labels,
            "terminal": terminal,
            "unique_functions": mesh.get("unique_functions") or [],
            "edges": mesh,
        },
        "multi_pass": multi_pass,
        "ops_next": ops_next,
        "message": (
            f"Online niche rework · {len(niches_out)} niches · P(accept)={acc.get('acceptance_p')} · online={online}"
            if L == "en"
            else f"Переработка online-ниш · {len(niches_out)} ниш · P(приёмки)={acc.get('acceptance_p')} · online={online}"
        ),
        "prompt_excerpt": ONLINE_NICHE_PROMPT.strip()[:500] + "…",
    }
