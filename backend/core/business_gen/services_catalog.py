"""
Business Tasks — 10 service types for Global Ru Workers.

Pricing language: affordable / fair / non-hype (no inflated info-marketer prices).
AI-agent class work referenced as ~$1k band in strategy docs — UI says qualitative only.
"""

from __future__ import annotations

from typing import Any

# 10 services — names distinct from consumer demos; B2B/worker-facing
BUSINESS_SERVICES: list[dict[str, Any]] = [
    {
        "id": "ops_reframe",
        "name_ru": "Операционный контур",
        "name_en": "Ops Contour",
        "tagline_ru": "Одна метрика, утечки, scoreboard",
        "tagline_en": "One metric, leaks, scoreboard",
        "price_note_ru": "Адекватный прайс · не инфоцыганский",
        "price_note_en": "Fair pricing · not hype-tier",
        "demo_hook_ru": "За 2 минуты: leak-map на вашем процессе",
        "demo_hook_en": "In 2 min: leak-map on your process",
        "wow": "До/после часов rework на одной карточке",
    },
    {
        "id": "offer_pack",
        "name_ru": "Упаковка оффера",
        "name_en": "Offer Packaging",
        "tagline_ru": "Обещание · границы · пакет",
        "tagline_en": "Promise · boundaries · pack",
        "price_note_ru": "Недорого относительно результата",
        "price_note_en": "Affordable vs outcome",
        "demo_hook_ru": "Черновик оффера из 5 предложений брифа",
        "demo_hook_en": "Offer draft from a 5-sentence brief",
        "wow": "Клиент видит «за что платят» без воды",
    },
    {
        "id": "tech_tz",
        "name_ru": "Tech-ТЗ под внедрение",
        "name_en": "Implementation TZ",
        "tagline_ru": "Scope · приёмка · non-goals",
        "tagline_en": "Scope · acceptance · non-goals",
        "price_note_ru": "Лаконичный фиксированный объём",
        "price_note_en": "Lean fixed scope",
        "demo_hook_ru": "1-страничное ТЗ с критериями приёмки",
        "demo_hook_en": "1-page TZ with acceptance criteria",
        "wow": "Можно отдать исполнителю сегодня",
    },
    {
        "id": "ai_agent_desk",
        "name_ru": "AI-агент под задачу",
        "name_en": "Task AI Agent",
        "tagline_ru": "Документ → агент по принятому scope",
        "tagline_en": "Doc → agent on accepted scope",
        "price_note_ru": "Класс ~агентской работы · адекватно рынку",
        "price_note_en": "Agent-class work · market-fair",
        "demo_hook_ru": "Dry-run: агент проходит чеклист на демо-данных",
        "demo_hook_en": "Dry-run: agent walks checklist on demo data",
        "wow": "Не чат — исполнимый контур",
    },
    {
        "id": "distribution_engine",
        "name_ru": "Дистрибуция 3D",
        "name_en": "3D Distribution",
        "tagline_ru": "Бренд · площадки · нетворкинг",
        "tagline_en": "Brand · platforms · networking",
        "price_note_ru": "Без раздутых «маркетинг-подписок»",
        "price_note_en": "No bloated marketing retainers",
        "demo_hook_ru": "План на 7 дней: 1 ход в каждом канале",
        "demo_hook_en": "7-day plan: 1 move per channel",
        "wow": "Рекомендации под нишу, не generic SMM",
    },
    {
        "id": "worker_lane",
        "name_ru": "Воркер-линия",
        "name_en": "Worker Lane",
        "tagline_ru": "Задача · proof · выплата",
        "tagline_en": "Task · proof · payout",
        "price_note_ru": "Прозрачный % / фикс до старта",
        "price_note_en": "Clear cut/fix before start",
        "demo_hook_ru": "Карточка задачи с escrow-логикой",
        "demo_hook_en": "Task card with escrow logic",
        "wow": "Зайти → сделать → продать → получить",
    },
    {
        "id": "resource_loop",
        "name_ru": "Ресурс + логистика",
        "name_en": "Resource + Logistics",
        "tagline_ru": "Поток · bottleneck · cash cycle",
        "tagline_en": "Flow · bottleneck · cash cycle",
        "price_note_ru": "Пилот без капекса «на авось»",
        "price_note_en": "Pilot without hopeful capex",
        "demo_hook_ru": "Flow-balance: inflow/capacity/leak",
        "demo_hook_en": "Flow-balance: inflow/capacity/leak",
        "wow": "Видно где деньги умирают в цепи",
    },
    {
        "id": "expert_base_gen",
        "name_ru": "Экспертная база проекта",
        "name_en": "Project Expert Base",
        "tagline_ru": "Уникальные слои знаний под ТЗ",
        "tagline_en": "Unique knowledge layers per TZ",
        "price_note_ru": "Разово / с обновлениями · без абонемента-ловушки",
        "price_note_en": "One-shot / updates · no trap subscription",
        "demo_hook_ru": "Срез ontology + playbook + kill-switches",
        "demo_hook_en": "Slice: ontology + playbook + kill-switches",
        "wow": "Не википедия — база под ваш контур",
    },
    {
        "id": "control_panel",
        "name_ru": "Панель управления",
        "name_en": "Control Panel",
        "tagline_ru": "Метрики · задачи · риски",
        "tagline_en": "Metrics · tasks · risks",
        "price_note_ru": "Входит в сборку · без UI-нагромождения",
        "price_note_en": "Part of assembly · no UI clutter",
        "demo_hook_ru": "3 виджета: uncertainty / risk / plan",
        "demo_hook_en": "3 widgets: uncertainty / risk / plan",
        "wow": "Как кабинет пилота, не «дашборд ради дашборда»",
    },
    {
        "id": "full_business_gen",
        "name_ru": "Сгенерировать бизнес 🔥",
        "name_en": "Generate Business 🔥",
        "tagline_ru": "От сути → система + база + панель",
        "tagline_en": "Essence → system + base + panel",
        "price_note_ru": "Пилот-сборка · адекватно сложности",
        "price_note_en": "Pilot assembly · fair for complexity",
        "demo_hook_ru": "Полный прогон на живой нише",
        "demo_hook_en": "Full run on a live niche",
        "wow": "Автономный контур, но с согласованиями как по ТЗ",
    },
]


def service_demo(service_id: str, lang: str = "ru", seed_text: str = "") -> dict[str, Any]:
    """Lightweight wow-demo payload for each service (songwriter-style short demo)."""
    svc = next((s for s in BUSINESS_SERVICES if s["id"] == service_id), None)
    if not svc:
        return {"error": "unknown_service", "id": service_id}

    demos: dict[str, dict[str, Any]] = {
        "ops_reframe": {
            "title": "Leak-map demo",
            "lines": [
                "Вход: 40ч/нед delivery",
                "Утечка: 12ч rework без scoreboard",
                "Ход: 1 метрика + weekly gate → цель −15% rework",
            ],
            "cta": "Поставить себе scoreboard",
        },
        "offer_pack": {
            "title": "Offer sketch",
            "lines": [
                "Для: владельцев процессов в нише",
                "Обещание: ясный следующий оплачиваемый шаг",
                "Граница: без гарантии прибыли; работа по ТЗ",
            ],
            "cta": "Собрать полный пакет",
        },
        "tech_tz": {
            "title": "TZ slice",
            "lines": [
                "In scope: intake form + metric card",
                "Out: billing integrations v1",
                "Accept: клиент подтверждает 3 сценария",
            ],
            "cta": "Дописать ТЗ",
        },
        "ai_agent_desk": {
            "title": "Agent dry-run",
            "lines": [
                "Вход: принятый doc",
                "Шаги: validate → act → report",
                "Стоп: нет human approve на money-move",
            ],
            "cta": "Подключить агента",
        },
        "distribution_engine": {
            "title": "7-day distribution",
            "lines": [
                "Бренд: 1 proof-пост",
                "Площадка: 5 lookalike касаний",
                "Нетворк: 3 тёплых intro",
            ],
            "cta": "Запустить неделю",
        },
        "worker_lane": {
            "title": "Task → payout",
            "lines": [
                "Задача: собрать пакет документов",
                "Proof: checklist + file hash",
                "Выплата: milestone escrow release",
            ],
            "cta": "Взять задачу",
        },
        "resource_loop": {
            "title": "Flow snapshot",
            "lines": [
                "Inflow 100 · capacity 72 · leak 14%",
                "Bottleneck: capacity",
                "Не крутить маркетинг до расширения hub",
            ],
            "cta": "Полный resource loop",
        },
        "expert_base_gen": {
            "title": "Base slice",
            "lines": [
                "Ontology: 10 entities",
                "Playbooks: intake / assemble / pilot",
                "Kill-switches: risk lattice",
            ],
            "cta": "Сгенерировать базу",
        },
        "control_panel": {
            "title": "Panel preview",
            "lines": [
                "Uncertainty: 3 known / 4 unknown",
                "Risk: amber",
                "Plan: S1–S4 await choice",
            ],
            "cta": "Открыть панель",
        },
        "full_business_gen": {
            "title": "Business spark 🔥",
            "lines": [
                "Вход: суть бизнеса",
                "Процесс: синтез + согласования",
                "Выход: код-пакет · экспертная база · панель",
            ],
            "cta": "Сгенерировать бизнес",
        },
    }
    d = demos.get(service_id, {"title": svc["name_ru"], "lines": [svc["wow"]], "cta": "Далее"})
    return {
        "service": svc,
        "demo": d,
        "lang": lang,
        "seed_used": bool(seed_text),
        "note": svc["demo_hook_ru"] if lang == "ru" else svc["demo_hook_en"],
    }


def list_services(lang: str = "ru") -> list[dict[str, Any]]:
    out = []
    for s in BUSINESS_SERVICES:
        out.append(
            {
                "id": s["id"],
                "name": s["name_ru"] if lang == "ru" else s["name_en"],
                "tagline": s["tagline_ru"] if lang == "ru" else s["tagline_en"],
                "price_note": s["price_note_ru"] if lang == "ru" else s["price_note_en"],
                "demo_hook": s["demo_hook_ru"] if lang == "ru" else s["demo_hook_en"],
                "wow": s["wow"],
            }
        )
    return out
