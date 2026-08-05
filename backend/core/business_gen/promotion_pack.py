"""
Promotion pack — third tariff / third mode.

Three main roads:
  1. Platform placement (площадки)
  2. Networking
  3. Social strategy

Plus separate DM sales scripts & ideas.
Recognizes promo analytics keywords from brief and returns actionable answers.
"""

from __future__ import annotations

import re
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


# Signals for promo analytics recognition
_ANALYTICS_MARKERS = {
    "reach": ("охват", "reach", "impressions", "показы", "views", "просмотр"),
    "engagement": ("er", "engagement", "вовлеч", "лайк", "коммент", "reply", "retweet"),
    "conversion": ("конверс", "conversion", "cvr", "лид", "lead", "заявк", "dm open"),
    "cac": ("cac", "cpl", "цена лида", "стоимость лида", "ad spend", "бюджет реклам"),
    "retention": ("удерж", "retention", "повтор", "return", "churn аудитории"),
    "positioning": ("позицион", "angle", "угол", "оффер", "offer", "уникальн"),
}


def detect_promo_analytics(text: str) -> dict[str, Any]:
    t = (text or "").lower()
    hits = []
    for key, toks in _ANALYTICS_MARKERS.items():
        if any(x in t for x in toks):
            hits.append(key)
    strength = min(1.0, len(hits) / 4.0)
    return {
        "detected": hits,
        "strength": round(strength, 2),
        "mode": "promo_analytics" if hits else "promo_general",
    }


def build_promotion_pack(
    business_text: str,
    *,
    project_name: str = "",
    industry_id: str = "",
    lang: str = "ru",
) -> dict[str, Any]:
    L = _lang(lang)
    name = project_name or (business_text or "")[:60] or "Promo"
    analytics = detect_promo_analytics(business_text)
    t = (business_text or "").lower()

    # Context-aware platform picks
    platforms = []
    if any(w in t for w in ("b2b", "saas", "dev", "api", "агент", "студи", "билдер")):
        platforms = ["X / LinkedIn", "Product Hunt / indie boards", "Niche Telegram / Discord"]
    elif any(w in t for w in ("b2c", "shop", "магазин", "beauty", "food", "кафе")):
        platforms = ["Instagram / Reels", "Local maps + reviews", "Telegram channel"]
    else:
        platforms = ["Primary social of ICP", "1 marketplace / board", "1 community hub"]

    roads = [
        {
            "id": "road_platforms",
            "title": _d(L, "1. Размещение на платформах", "1. Platform placement"),
            "promise": _d(
                L,
                "Один профиль / листинг, где ICP уже ищет решение — не «везде понемногу».",
                "One profile/listing where ICP already looks — not everywhere thin.",
            ),
            "steps": [
                _d(L, f"Выбрать 1–2: {', '.join(platforms)}", f"Pick 1–2: {', '.join(platforms)}"),
                _d(L, "Оффер в 1 строке + 1 proof (карточка / кейс / metric)", "1-line offer + 1 proof (card / case / metric)"),
                _d(L, "CTA: «напишите в DM слово PACK» или ссылка на 15-min", "CTA: DM keyword PACK or 15-min link"),
                _d(L, "Раз в 7 дней — обновление proof, не редизайн всего", "Every 7 days — refresh proof, not full redesign"),
            ],
            "kpi": _d(L, "Профиль visits → DM / lead ≥ 5% за 14 дней", "Profile visits → DM/lead ≥ 5% in 14 days"),
            "kill": _d(L, "0 целевых DM за 14 дней → сменить площадку, не «постить больше»", "0 qualified DMs in 14d → switch platform, not post more"),
        },
        {
            "id": "road_networking",
            "title": _d(L, "2. Нетворкинг", "2. Networking"),
            "promise": _d(
                L,
                "Тёплые касания к 12–15 людям с похожим ICP — не «нетворкинг вообще».",
                "Warm touches to 12–15 people with similar ICP — not networking in abstract.",
            ),
            "steps": [
                _d(L, "Список 15: экс-клиенты, коллеги, основатели из ниши", "List of 15: ex-clients, peers, niche founders"),
                _d(L, "Касание = value first (1 insight / 1 card / 1 intro)", "Touch = value first (1 insight / 1 card / 1 intro)"),
                _d(L, "Просьба: 15 мин или репост proof — не «купи»", "Ask: 15 min or repost proof — not “buy”"),
                _d(L, "Ledger: кто / дата / ответ / next", "Ledger: who / date / reply / next"),
            ],
            "kpi": _d(L, "≥3 deep разговора + ≥1 intro за 7 дней", "≥3 deep talks + ≥1 intro in 7 days"),
            "kill": _d(L, "Список <8 или 0 ответов 7 дней → сузить ICP", "List <8 or 0 replies in 7d → narrow ICP"),
        },
        {
            "id": "road_social",
            "title": _d(L, "3. Стратегия в соцсетях", "3. Social strategy"),
            "promise": _d(
                L,
                "1 канал · 3 формата · 1 оффер. Без «ежедневного контента ради контента».",
                "1 channel · 3 formats · 1 offer. No daily content for content’s sake.",
            ),
            "steps": [
                _d(L, "Канал: тот, где уже сидит ICP (не все сразу)", "Channel: where ICP already is (not all at once)"),
                _d(L, "Форматы: proof-пост · mini-case · open question", "Formats: proof post · mini-case · open question"),
                _d(L, "Ритм: 3 публикации / неделя + daily replies 20 мин", "Rhythm: 3 posts/week + 20 min daily replies"),
                _d(L, "Каждый пост → 1 soft CTA в DM", "Every post → 1 soft DM CTA"),
            ],
            "kpi": _d(L, "Save/share rate + DM from posts ≥ 2 / неделя", "Save/share + DM from posts ≥ 2 / week"),
            "kill": _d(L, "0 DM 14 дней при 6+ постах → сменить угол оффера", "0 DMs in 14d with 6+ posts → change offer angle"),
        },
    ]

    dm_scripts = [
        {
            "id": "dm1",
            "name": _d(L, "Холодный → value", "Cold → value"),
            "script": _d(
                L,
                f"Привет! Видел, что вы в теме «{name[:40]}». Собрал 1 схему, как режут rework / неясный unit — "
                f"могу кинуть 1 карточку без продажи. Ок?",
                f"Hey — saw you’re in «{name[:40]}». I put one simple map for unit clarity / less rework — "
                f"can send 1 card, no pitch. OK?",
            ),
        },
        {
            "id": "dm2",
            "name": _d(L, "Тёплый → созвон", "Warm → call"),
            "script": _d(
                L,
                "Спасибо за ответ. Если коротко: за 15 мин покажу, как выглядит unit + kill criterion "
                "под ваш кейс. Без презентации на 40 слайдов. Когда удобно — 2 слота?",
                "Thanks for the reply. In 15 min I can show unit + kill criterion for your case. "
                "No 40-slide deck. Two slots that work?",
            ),
        },
        {
            "id": "dm3",
            "name": _d(L, "После proof-поста", "After proof post"),
            "script": _d(
                L,
                "Если откликнулось — напишите PACK, пришлю 1-page schema + anti-scope. "
                "Если не ваше — ок, не буду пушить.",
                "If this resonated — reply PACK, I’ll send 1-page schema + anti-scope. "
                "If not for you — all good, no push.",
            ),
        },
        {
            "id": "dm4",
            "name": _d(L, "Закрытие unit", "Close unit"),
            "script": _d(
                L,
                "Итого: pack / review за $X, срок Y дней, kill если нет Z. "
                "Могу выставить счёт сегодня и стартовать со scope note. Идём?",
                "Summary: pack/review for $X, Y days, kill if no Z. "
                "I can invoice today and start with a scope note. Shall we?",
            ),
        },
    ]

    sales_ideas = [
        _d(L, "Один публичный artifact (карточка A01) + 10 DM со ссылкой на него", "One public artifact (A01 card) + 10 DMs linking it"),
        _d(L, "«Open office» 40 мин в community — 1 раз / 2 недели", "40-min open office in community — 1× / 2 weeks"),
        _d(L, "Совместный post с peer (не конкурент) — 1 mutual intro", "Co-post with a peer (not competitor) — 1 mutual intro"),
        _d(L, "Мини-оффер: design review 48h — низкий friction entry", "Mini-offer: 48h design review — low friction entry"),
    ]

    # Analytics answers for detected signals
    analytics_answers = []
    answer_map = {
        "reach": _d(
            L,
            "Охват без DM/лида — vanity. Метрика: profile→DM. Режьте широкий контент, усильте 1 CTA.",
            "Reach without DM/lead is vanity. Metric: profile→DM. Cut broad content; one CTA.",
        ),
        "engagement": _d(
            L,
            "ER важен только если ведёт к диалогу. Считайте replies + DM, не лайки.",
            "ER matters only if it leads to dialogue. Count replies + DMs, not likes.",
        ),
        "conversion": _d(
            L,
            "Конверсия touch→paid: цель ≥1 unit / 21d. Фиксируйте stop/go на календаре.",
            "Touch→paid conversion: target ≥1 unit / 21d. Lock stop/go on calendar.",
        ),
        "cac": _d(
            L,
            "Пока unit не продаётся из тёплого — платный CAC рано. Сначала 14 касаний organic.",
            "Until unit sells from warm path — paid CAC is early. First 14 organic touches.",
        ),
        "retention": _d(
            L,
            "Retention аудитории = повтор proof + client pack, не daily posts.",
            "Audience retention = repeat proof + client pack, not daily posts.",
        ),
        "positioning": _d(
            L,
            "Угол = unit + anti-scope + 1 proof. Не «мы лучшие», а «вот геометрия решения».",
            "Angle = unit + anti-scope + 1 proof. Not “we’re best” — decision geometry.",
        ),
    }
    for h in analytics["detected"]:
        analytics_answers.append({"signal": h, "answer": answer_map.get(h, "")})

    general_tips = [
        _d(L, "Один оффер · один ICP · один канал 14 дней", "One offer · one ICP · one channel for 14 days"),
        _d(L, "Proof раньше масштаба: 1 artifact > 10 «стратегий»", "Proof before scale: 1 artifact > 10 “strategies”"),
        _d(L, "DM = продажа; пост = trust. Не путать", "DM = sell; post = trust. Don’t mix"),
        _d(L, "Kill date на каждый эксперимент продвижения", "Kill date on every promo experiment"),
    ]

    return {
        "module": "PromotionPack",
        "version": "1.0",
        "tariff": "marketing",
        "price_anchor_usd": 690,
        "project": name,
        "industry_hint": industry_id,
        "analytics": analytics,
        "analytics_answers": analytics_answers,
        "general_tips": general_tips,
        "roads": roads,
        "dm_scripts": dm_scripts,
        "sales_ideas": sales_ideas,
        "summary": _d(
            L,
            f"Продвижение «{name}»: 3 дороги (платформы · нетворкинг · соцсети) + скрипты DM. "
            f"Аналитика: {', '.join(analytics['detected']) or 'общий режим'}.",
            f"Promotion for «{name}»: 3 roads (platforms · networking · social) + DM scripts. "
            f"Analytics: {', '.join(analytics['detected']) or 'general mode'}.",
        ),
        "lang": L,
    }
