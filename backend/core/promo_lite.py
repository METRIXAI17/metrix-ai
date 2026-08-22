"""Promo-lite — mass Metrix business builder (cards, reels, consulting prompts)."""

from __future__ import annotations

from typing import Any

from backend.core.task_reader import assemble_query
from backend.monetization.promo import PromoAutomation


def run_promo_lite(
    brief: str,
    *,
    kind: str = "cards",
    industry_id: str = "content-monetize",
    lang: str = "ru",
) -> dict[str, Any]:
    packed = assemble_query(brief, lang=lang, surface_hint="promo_lite")
    title = (brief or "offer")[:72]
    promo = PromoAutomation().build(
        idea_title=title,
        industry_id=industry_id,
        industry_name="Контент и аудитория",
        promo_fit=0.62,
        phrases=[title],
        lang=lang,
    )
    cards = [
        {
            "kicker": "Оффер",
            "title": title,
            "body": "Не чат. Артефакт, который можно купить сегодня.",
        },
        {
            "kicker": "Для кого",
            "title": "Индивидуал / студия / агентство",
            "body": "Тем, кто продаёт работу, а не подписку на воздух.",
        },
        {
            "kicker": "Почему Metrix",
            "title": "Читалка + режим сами",
            "body": "Несколько концов считывания. Платите, когда утвердите.",
        },
    ]
    reels = [
        {"sec": "0–3", "shot": "Один предмет крупно", "text": "Правило, не мотивация"},
        {"sec": "3–8", "shot": "Процесс руками / экран Mini App", "text": title},
        {"sec": "8–12", "shot": "Карточка SKU", "text": "Купить в боте"},
    ]
    prompts = [
        "Разложи бриф клиента на 3 конца считывания. Не выбирай лучший. Назови умолчания.",
        "Собери пакет: продукт / лингвистика / монетизация — три колонки, без смешивания.",
        "Предложи 5 карточек описания оффера по 18 слов. Без прилагательных-пустышек.",
        "Дай 3 хука для ролика 12с, где продукт виден без голоса.",
    ]
    kind = (kind or "cards").lower()
    payload = {"cards": cards, "reels": reels, "prompts": prompts}.get(kind) or {
        "cards": cards,
        "reels": reels,
        "prompts": prompts,
    }
    return {
        "module": "Promo Lite",
        "kind": kind,
        "items": payload,
        "promo_plan": promo.to_dict(),
        "assembly": packed,
        "summary": f"promo-lite kind={kind} for «{title}»",
    }
