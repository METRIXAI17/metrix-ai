"""
Hook plan — short human plan card (not engineer jargon).

Shown as clean structured HTML-ready fields for UI redesign.
"""

from __future__ import annotations

from typing import Any

CORE_PRICE_USD = 790
X_DM = "https://x.com/karimmetrix"


def build_hook_plan(
    *,
    project_name: str,
    profile: dict[str, Any],
    value: dict[str, Any] | None = None,
    counts: dict[str, Any] | None = None,
    signer_numbers: dict[str, Any] | None = None,
    channel_log: dict[str, Any] | None = None,
    concept_tests: list[dict[str, str]] | None = None,
    assist: dict[str, Any] | None = None,
    open_questions: list[str] | None = None,
    lang: str = "ru",
    personality: dict[str, Any] | None = None,
) -> dict[str, Any]:
    is_en = (lang or "").lower().startswith("en")
    title = project_name or profile.get("title_hint") or ("Your project" if is_en else "Ваш проект")
    unit = profile.get("unit") or "—"
    payer = profile.get("payer") or "—"
    metric = profile.get("metric") or "—"
    axis = (personality or {}).get("primary_label") or ""
    n_cards = int((counts or {}).get("total_cards") or 0)

    if is_en:
        headline = f"What you get for «{title}»"
        lines_cards = [
            {"k": "Ready now", "v": f"Filling · analytical report · main PDF · {n_cards} decision cards"},
            {"k": "Who pays", "v": payer},
            {"k": "What you sell", "v": unit},
            {"k": "Pilot of success", "v": metric},
            {"k": "Author stance", "v": axis or "Systems builder angle from your brief"},
            {
                "k": "After payment",
                "v": "Author uniqueness pack + deploy agent · clarifying questions in DM",
            },
        ]
        pitch = (
            "You already have the map. Pay when you want the hands-on path: "
            "we refine uniqueness and run deployment with you."
        )
        cta = f"Pay & continue · DM @{X_DM.split('/')[-1]}"
        next_step = f"Write on X: {X_DM} — “Core · {title[:40]}”"
        markdown = (
            f"## {headline}\n\n"
            f"{pitch}\n\n"
            + "\n".join(f"- **{c['k']}:** {c['v']}" for c in lines_cards)
            + f"\n\n**Next:** {next_step}\n"
        )
    else:
        headline = f"Что готово по «{title}»"
        lines_cards = [
            {"k": "Уже сейчас", "v": f"Наполнение · аналитический отчёт · основной PDF · {n_cards} карточек решений"},
            {"k": "Кто платит", "v": payer},
            {"k": "Что продаёте", "v": unit},
            {"k": "Мера успеха", "v": metric},
            {"k": "Угол автора", "v": axis or "Системный билдер — из вашего брифа"},
            {
                "k": "После оплаты",
                "v": "Авторская уникальность + агент деплоя · уточняющие вопросы в переписке",
            },
        ]
        pitch = (
            "Карта уже собрана. Оплата — когда нужны руки: "
            "усиливаем уникальность и ведём внедрение вместе."
        )
        cta = "Оплатить и приступить · написать в X"
        next_step = f"Напишите в X: {X_DM} — «Ядро · {title[:40]}»"
        markdown = (
            f"## {headline}\n\n"
            f"{pitch}\n\n"
            + "\n".join(f"- **{c['k']}:** {c['v']}" for c in lines_cards)
            + f"\n\n**Дальше:** {next_step}\n"
        )

    return {
        "module": "HookPlan",
        "version": "2.0",
        "headline": headline,
        "pitch": pitch,
        "cards": lines_cards,
        "markdown": markdown,
        "cta": cta,
        "next_step": next_step,
        "x_dm": X_DM,
        "price_usd": CORE_PRICE_USD,
        "lang": "en" if is_en else "ru",
        # keep fields for old clients
        "bullets": [c["v"] for c in lines_cards],
        "sub_cta": next_step,
        "value_mid_usd": (value or {}).get("realized_mid_usd"),
        "gap_usd": (value or {}).get("gap_usd"),
        "band": (value or {}).get("band"),
        "open_questions_left": 0,
        "why_buy_now": [c["v"] for c in lines_cards[:3]],
    }
