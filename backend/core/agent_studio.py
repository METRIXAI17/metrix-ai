"""Metrix as an AI-agent builder for four live B2B surfaces.

Not a chatbot factory. An agent here carries a financial model:
what counts as money, when to stay quiet, which artifact a human receives.
"""

from __future__ import annotations

import re
from typing import Any

from backend.core.resonance import new_id
from backend.core.voice import DISCLAIMER, clip


NICHES: dict[str, dict[str, Any]] = {
    "saas": {
        "id": "saas",
        "title": "B2B SaaS и IT",
        "size": "50–500 человек",
        "industry": "saas-founders",
        "accent": "#a5b4fc",
        "pain": (
            "Решения живут в Slack. Фича «вроде нужна», пилот «вроде идёт», "
            "экономики у решения нет — только статус в Jira."
        ),
        "agent_job": "Агент решения: сырой запрос → unit-экономика фичи + условие остановки + артефакт раскатки.",
        "why_builder": (
            "Metrix сажает в агента уникальную финмодель продуктовой линии, "
            "а не общего копайлота, который пишет тикеты. "
            "Команда 50–500 уже купила чаты. Ей не хватает модели, кто платит за фичу."
        ),
    },
    "agency": {
        "id": "agency",
        "title": "Digital и performance",
        "size": "агентства",
        "industry": "ai-agencies",
        "accent": "#5eead4",
        "pain": (
            "Каждый клиент — новый кастом. Маржа сгорает на онбординге. "
            "Метод агентства живёт в головах, не в модели."
        ),
        "agent_job": "Агент входа: бриф клиента → геометрия оффера → пакет на 14 дней с цифрой маржи.",
        "why_builder": (
            "Билдер упаковывает нестандартный метод агентства в повторяемого агента. "
            "Не ещё один GPT для копирайта — а посадка вашей экономики в каждый новый аккаунт."
        ),
    },
    "edu": {
        "id": "edu",
        "title": "Школы и образовательные проекты",
        "size": "онлайн-школы, когорты",
        "industry": "education",
        "accent": "#fda4af",
        "pain": (
            "Контент путают с деньгами. Воронка течёт. "
            "Нет единицы прогресса, которая оплачивается."
        ),
        "agent_job": "Агент когорты: урок/трафик → следующий платный шаг + экономика потока.",
        "why_builder": (
            "Чат «спроси про урок» не спасает школу. "
            "Metrix собирает агента с моделью LTV внимания: какой кусок программы продаёт, какой только греет эго."
        ),
    },
    "ecom": {
        "id": "ecom",
        "title": "E-com с высоким чеком",
        "size": "B2B и B2C",
        "industry": "ecommerce",
        "accent": "#fbbf24",
        "pain": (
            "Дорогой клик. Высокий чек должен оплатить отношение, а не ещё одну ставку. "
            "Скрипты менеджеров не являются финмоделью заказа."
        ),
        "agent_job": "Агент заказа: покупка → цикл капитала (дожим, возврат, повтор) с раздельными правилами B2B/B2C.",
        "why_builder": (
            "Общий чат на сайте не знает, что средний чек высокий — и ведёт себя как для футболок. "
            "Билдер собирает модель конкретного заказа: маржа, касса, повтор, не «upsell-скрипт»."
        ),
    },
}


def list_niches() -> list[dict[str, Any]]:
    out = []
    for k in ("saas", "agency", "edu", "ecom"):
        n = NICHES[k]
        out.append(
            {
                "id": n["id"],
                "title": n["title"],
                "size": n["size"],
                "accent": n["accent"],
                "pain": n["pain"],
                "agent_job": n["agent_job"],
            }
        )
    return out


def resolve_niche(name: str | None, brief: str = "") -> str:
    key = (name or "").strip().lower()
    aliases = {
        "saas": "saas",
        "it": "saas",
        "b2b": "saas",
        "софт": "saas",
        "agency": "agency",
        "агентств": "agency",
        "performance": "agency",
        "маркетинг": "agency",
        "edu": "edu",
        "школ": "edu",
        "курс": "edu",
        "образова": "edu",
        "ecom": "ecom",
        "e-com": "ecom",
        "магазин": "ecom",
        "чеком": "ecom",
        "ecommerce": "ecom",
    }
    if key in NICHES:
        return key
    for a, nid in aliases.items():
        if a in key:
            return nid
    low = (brief or "").lower()
    checks = [
        (r"saas|b2b|50.?500|продуктов(ая|ой) команд|jira|фич", "saas"),
        (r"агентств|performance|media buying|ppc|трафик|аккаунт", "agency"),
        (r"школ|курс|когорт|урок|edtech|обучен", "edu"),
        (r"e-?com|магазин|средний чек|aov|sku|заказ", "ecom"),
    ]
    for pat, nid in checks:
        if re.search(pat, low):
            return nid
    return "saas"


def _install(niche_id: str) -> list[str]:
    common = [
        "День 1–2: снять, как решения живут сейчас (кто пишет, где умирает, что считается «сделано»).",
        "День 3–5: посадить финмодель в агента — единицы денег, стоп-условия, артефакт на выходе.",
        "День 6–10: прогнать 5 живых запросов, не демо. Смотреть, что срезонировало.",
        "День 11–14: оставить только то, что зашло. Остальное вырезать. Это и есть продукт.",
    ]
    extra = {
        "saas": "В SaaS агент сидит на входящих фичах/тикетах, не в HR-чате.",
        "agency": "В агентстве агент сидит на онбординге, не в генерации креатива.",
        "edu": "В школе агент сидит на переходе «урок → офер», не в FAQ.",
        "ecom": "В e-com агент сидит после оплаты, не в виджете «чем помочь».",
    }
    return [extra[niche_id]] + common


def build_agent(niche: str | None = None, brief: str = "") -> dict[str, Any]:
    nid = resolve_niche(niche, brief)
    n = NICHES[nid]
    stem = clip(brief, 120) if (brief or "").strip() else n["title"]
    title = f"Агент · {n['title']}"

    inputs = [
        "Ситуация своими словами (не бриф на 12 слайдов).",
        "Где сейчас принимают решения (Slack, созвон, таблица, «в голове»).",
        "Что считается деньгами в этом контуре — хотя бы грубо.",
    ]
    outputs = [
        "Именная финмодель: единица, стоп, кто нажимает.",
        "Спека агента: вход, молчание, артефакт человеку.",
        "План посадки на 14 дней без театра внедрения.",
    ]

    return {
        "id": new_id(),
        "kind": f"agent.{nid}",
        "lane": "agent",
        "niche_id": nid,
        "title": title,
        "one_liner": n["agent_job"],
        "break": n["pain"],
        "move": (
            f"{n['why_builder']} "
            f"На вашей задаче («{stem}») агент не болтает — он держит модель и отдаёт артефакт."
        ),
        "steps": _install(nid),
        "artifact_week": (
            "Одна страница: имя агента, что он ест на входе, какой артефакт сплёвывает, "
            "когда молчит, какая цифра значит, что он живой."
        ),
        "anti": [
            "Не делать агента, который «отвечает на всё».",
            "Не внедрять без единицы денег.",
            "Не держать функции, которые ни разу не зашли за 14 дней.",
        ],
        "meta": {
            "niche": n["title"],
            "size": n["size"],
            "accent": n["accent"],
            "inputs": inputs,
            "outputs": outputs,
            "industry": n["industry"],
            "why_builder": n["why_builder"],
        },
        "highway": {
            "free": "спека агента как демо",
            "paid": "сборка и посадка агента в ваш контур",
            "sku": "pilot_14",
        },
        "disclaimer": DISCLAIMER,
        "brief": clip(brief, 400),
    }
