"""
Identity engine — post-pay author uniqueness processor.

Voice & principles distilled from @karimmetrix public posts (2026-07):
- Will to power: own decisions, against imposed rules
- Orient → pick solution → ship (ops first, promo separate)
- Same product + different analytics → different money
- Failed hypothesis ≠ dead code; cheap token cycles
- Not another AI chat — result pack that ships
- Structural leverage vs sedentary job path
- Return to true self after empty experiments

Second-wave questions are UNIQUE per request (hash of brief + project)
and only about author identity — never generic regulatory noise.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


def _clip(t: str, n: int = 140) -> str:
    t = re.sub(r"\s+", " ", (t or "").strip())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


_Q_BANK: list[dict[str, Any]] = [
    {
        "id": "will_power",
        "tags": ("builder", "agency", "library", "generic"),
        "ru": "Какое решение вы уже приняли «против всех советов» — и оно остаётся вашим?",
        "en": "Which decision did you make against all advice — and still own?",
        "why": "will_to_power",
    },
    {
        "id": "true_self",
        "tags": ("builder", "storyteller", "generic", "content"),
        "ru": "После пустых экспериментов — к чему вы реально хотите вернуться в работе?",
        "en": "After empty experiments — what work do you actually want to return to?",
        "why": "return_to_self",
    },
    {
        "id": "ops_vs_promo",
        "tags": ("operator", "agency", "saas", "generic"),
        "ru": "Если ops настроен правильно, а промо ещё нет — что в вашем unit уже меняет деньги?",
        "en": "If ops is right and promo is not — what in your unit already changes money?",
        "why": "ops_first",
    },
    {
        "id": "same_product_diff_money",
        "tags": ("analyst", "operator", "library", "saas"),
        "ru": "Один и тот же продукт: какие 2–3 аналитики сделали бы из него «другие деньги»?",
        "en": "Same product: which 2–3 analytics would make different money from it?",
        "why": "analytics_delta",
    },
    {
        "id": "orient_pick_ship",
        "tags": ("builder", "generic", "library"),
        "ru": "Что вы уже ориентировали, что выбрали, а что ещё не «зашиппили»?",
        "en": "What have you oriented, what picked, and what still not shipped?",
        "why": "orient_pick_ship",
    },
    {
        "id": "failed_hypothesis",
        "tags": ("builder", "craftsman", "generic"),
        "ru": "Какая failed hypothesis у вас уже «дешёвый цикл», а не трагедия — и что из неё оставили?",
        "en": "Which failed hypothesis is already a cheap cycle, not a tragedy — and what stayed?",
        "why": "cheap_cycles",
    },
    {
        "id": "not_chat",
        "tags": ("builder", "library", "saas"),
        "ru": "Какой live result-pack вы хотите отдавать клиенту вместо «ещё одного чата»?",
        "en": "What live result-pack do you want to ship instead of another chat?",
        "why": "result_pack",
    },
    {
        "id": "leverage",
        "tags": ("operator", "connector", "generic"),
        "ru": "Где у вас рычаг над результатом (не только «сидячая работа за часы»)?",
        "en": "Where do you have leverage over results (not only sedentary hours)?",
        "why": "leverage",
    },
    {
        "id": "aesthetic_floor",
        "tags": ("craftsman", "storyteller", "library"),
        "ru": "Какой «золотой образец» качества вы не готовы опустить — даже ради скорости?",
        "en": "What golden quality sample will you never lower — even for speed?",
        "why": "golden_example",
    },
    {
        "id": "voice_angle",
        "tags": ("storyteller", "content", "generic"),
        "ru": "Каким одним предложением вас должны узнавать в рынке (не слоган, а угол)?",
        "en": "In one sentence — how should the market recognize your angle (not a slogan)?",
        "why": "voice",
    },
    {
        "id": "structural_income",
        "tags": ("analyst", "operator", "agency"),
        "ru": "Какой expert-контур вы хотите продать вместо «чистого LLM API»?",
        "en": "Which expert contour do you want to sell instead of pure LLM API?",
        "why": "structural_income",
    },
    {
        "id": "fear_kill",
        "tags": ("generic", "builder", "storyteller"),
        "ru": "Какой страх (аудитория / продажи / «не то») вы сознательно убиваете в этом пилоте?",
        "en": "Which fear (audience / sales / “wrong path”) are you consciously killing this pilot?",
        "why": "no_fear",
    },
]


def _fingerprint(business_text: str, project_name: str) -> str:
    raw = f"{project_name}|{(business_text or '').strip().lower()}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def pick_identity_questions(
    business_text: str,
    project_name: str,
    *,
    primary_axis: str = "builder",
    lang: str = "ru",
    n: int = 5,
) -> list[dict[str, str]]:
    """Deterministic unique set per request."""
    fp = _fingerprint(business_text, project_name)
    t = (business_text or "").lower()
    scored: list[tuple[float, dict[str, Any]]] = []
    for i, q in enumerate(_Q_BANK):
        tags = q.get("tags") or ()
        score = 0.2
        if primary_axis in tags:
            score += 0.5
        if any(tag in t for tag in tags if len(str(tag)) > 3):
            score += 0.25
        byte = int(fp[(i * 2) % 38 : (i * 2) % 38 + 2], 16) / 255.0
        score += byte * 0.35
        scored.append((score, q))
    scored.sort(key=lambda x: -x[0])
    L = _lang(lang)
    out = []
    for _, q in scored[:n]:
        out.append(
            {
                "id": q["id"],
                "text": q["ru"] if L == "ru" else q["en"],
                "why": q["why"],
                "unique_key": f"{fp[:8]}_{q['id']}",
            }
        )
    return out


def forecast_author_uniqueness(
    business_text: str,
    *,
    personality: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    project_name: str = "",
    lang: str = "ru",
) -> dict[str, Any]:
    """
    Forecast the founder should *like*: affirming stance, concrete differentiator,
    pleasurable path — not a cold audit. Metrix voice from public posts.
    """
    L = _lang(lang)
    pers = personality or {}
    prof = profile or {}
    name = project_name or pers.get("display_name") or _clip(business_text, 40)
    primary = pers.get("primary_label") or (
        "Системный билдер" if L == "ru" else "Systems builder"
    )
    secondary = pers.get("secondary_label") or ""
    unit = prof.get("unit") or "unit"
    fp = _fingerprint(business_text, name)

    if L == "ru":
        headline = (
            f"«{name}» — не «ещё один AI-чат». "
            "Ваш слой ориентации, который отдаёт live pack."
        )
        pleasurable = [
            f"Вам близко **решать самому** (will to power): unit «{unit}» — ваше правило, не чужой playbook.",
            f"Угол **{primary}**"
            + (f" (+ {secondary})" if secondary else "")
            + " звучит как вы: ops и angle разделены, деньги из аналитики, не из hype.",
            "Failed hypothesis не стыд — дешёвый цикл. Система оставляет core живым.",
            "Клиент получает result pack, не болтовню. Это приятно отдавать.",
            "Можно шиппить маленькими циклами и чувствовать рычаг, не «сидячую работу».",
        ]
        risks_soft = [
            "Если скопировать чужой tone — уникальность тускнеет (лечится identity Q после оплаты).",
            "Если смешать ops и promo в один шум — пропадёт «same product → different money».",
        ]
        next_gens = [
            "gen_v2: uniqueness 1-pager после ответов на identity Q",
            "gen_v3: voice samples / golden examples pack",
            "gen_v4: public proof-пост в вашем угле",
            "gen_v5: client result-pack template под ваш unit",
        ]
        delight_note = (
            "Прогноз сделан так, чтобы **хотелось** быть этим автором: "
            "сила выбора, свой angle, ship без стыда за прошлые циклы."
        )
    else:
        headline = (
            f"«{name}» — not another AI chat. "
            "Your orientation layer that ships a live pack."
        )
        pleasurable = [
            f"You already lean **will to power**: unit «{unit}» is your rule, not an imposed playbook.",
            f"Angle **{primary}**"
            + (f" (+ {secondary})" if secondary else "")
            + " feels like you: ops ≠ promo; money from analytics, not hype.",
            "Failed hypothesis is a cheap cycle — core stays alive.",
            "Clients get a result pack, not chatter. That feels good to ship.",
            "Small ship cycles + leverage — not sedentary hours.",
        ]
        risks_soft = [
            "Copying someone else’s voice dulls uniqueness (fixed by post-pay identity Q).",
            "Mixing ops and promo kills “same product → different money”.",
        ]
        next_gens = [
            "gen_v2: uniqueness 1-pager after identity answers",
            "gen_v3: voice samples / golden examples pack",
            "gen_v4: public proof post draft in your angle",
            "gen_v5: client result-pack template for your unit",
        ]
        delight_note = (
            "Forecast is built so you **want** to be this author: "
            "owned choice, your angle, ship without shame for past cycles."
        )

    score = 0.55
    if pers.get("primary_axis") in ("builder", "operator", "craftsman"):
        score += 0.12
    if prof.get("is_library"):
        score += 0.08
    if len(business_text or "") > 80:
        score += 0.08
    score = min(0.94, score)

    return {
        "module": "AuthorUniquenessForecast",
        "version": "1.0",
        "fingerprint": fp[:16],
        "headline": headline,
        "delight_score": round(score, 2),
        "delight_note": delight_note,
        "why_you_will_like_this": pleasurable,
        "soft_risks": risks_soft,
        "metrix_principles_used": [
            "will_to_power",
            "orient_pick_ship",
            "same_product_diff_analytics",
            "ops_vs_promo",
            "failed_hypothesis_cheap_cycle",
            "not_another_chat_result_pack",
            "return_to_true_self",
        ],
        "source_voice": "@karimmetrix",
        "next_generations": next_gens,
        "generation_slots_open": True,
        "lang": L,
    }


def build_post_pay_identity_pack(
    business_text: str,
    *,
    personality: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    project_name: str = "",
    lang: str = "ru",
    answers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Full post-payment identity surface: forecast + unique Q + re-gen hooks."""
    pers = personality or {}
    forecast = forecast_author_uniqueness(
        business_text,
        personality=pers,
        profile=profile,
        project_name=project_name,
        lang=lang,
    )
    questions = pick_identity_questions(
        business_text,
        project_name or pers.get("display_name") or "",
        primary_axis=pers.get("primary_axis") or "builder",
        lang=lang,
        n=5,
    )
    ans = answers or {}
    filled = {k: v for k, v in ans.items() if v}
    L = _lang(lang)
    return {
        "module": "PostPayIdentity",
        "unlock": "after_payment",
        "forecast": forecast,
        "identity_questions": questions,
        "answers_received": filled,
        "answers_complete": len(filled) >= 3,
        "regen": {
            "enabled": True,
            "note": _d(
                L,
                "После ответов можно запросить gen_v2+ (uniqueness card, voice pack, proof post) — слоты открыты.",
                "After answers you can request gen_v2+ (uniqueness card, voice pack, proof post) — slots open.",
            ),
            "endpoints": [
                "POST /api/v1/analytics/identity/answers",
                "POST /api/v1/analytics/business-generate (re-run with answers)",
            ],
        },
        "x_dm": "https://x.com/karimmetrix",
        "cta": _d(
            L,
            "Ответьте на 5 вопросов идентичности в DM @karimmetrix или через API — затем gen_v2.",
            "Answer 5 identity questions in DM @karimmetrix or via API — then gen_v2.",
        ),
        "lang": L,
    }
