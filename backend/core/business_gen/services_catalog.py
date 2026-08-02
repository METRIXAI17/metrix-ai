"""
Business Tasks — 10 service types for Global Ru Workers.

Pricing language: affordable / fair / non-hype (no inflated info-marketer prices).
AI-agent class work referenced as ~$1k band in strategy docs — UI says qualitative only.
Strings are pure per language (no RU/EN mix in one pack).
"""

from __future__ import annotations

from typing import Any

# Business Tasks — distribution-facing catalog
# (non-distributive: worker_lane, resource_loop — removed from public surface)
BUSINESS_SERVICES: list[dict[str, Any]] = [
    {
        "id": "ops_reframe",
        "name_ru": "Операционный контур",
        "name_en": "Ops Contour",
        "tagline_ru": "Одна метрика, утечки, табло",
        "tagline_en": "One metric, leaks, scoreboard",
        "benefit_ru": "Меньше переделок · ясный weekly gate · маржа из тех же часов",
        "benefit_en": "Less rework · clear weekly gate · more margin from same hours",
        "price_note_ru": "Адекватная цена · без раздутых обещаний",
        "price_note_en": "Fair price · no hype promises",
        "demo_hook_ru": "За 2 минуты: карта утечек на вашем процессе",
        "demo_hook_en": "In 2 min: leak map on your process",
        "wow_ru": "До/после часов переделок на одной карточке",
        "wow_en": "Before/after rework hours on one card",
        "examples": [
            {"niche": "ai-agencies", "ru": "AI-студия: −15% rework через scoreboard handoff", "en": "AI studio: −15% rework via handoff scoreboard"},
            {"niche": "automation-builders", "ru": "No-code: одна метрика доставки, не 12 KPI", "en": "No-code: one delivery metric, not 12 KPIs"},
        ],
    },
    {
        "id": "offer_pack",
        "name_ru": "Упаковка предложения",
        "name_en": "Offer Packaging",
        "tagline_ru": "Обещание · границы · пакет",
        "tagline_en": "Promise · boundaries · pack",
        "benefit_ru": "Клиент сразу видит «за что платит» · проще закрыть сделку",
        "benefit_en": "Client sees what they pay for · easier close",
        "price_note_ru": "Недорого относительно результата",
        "price_note_en": "Affordable relative to outcome",
        "demo_hook_ru": "Черновик предложения из 5 предложений брифа",
        "demo_hook_en": "Offer draft from a 5-sentence brief",
        "wow_ru": "Клиент видит «за что платят» без воды",
        "wow_en": "Client sees what they pay for — no fluff",
        "examples": [
            {"niche": "expert-services", "ru": "Эксперт: пакет 90 дней вместо «почасовки»", "en": "Expert: 90-day pack instead of hourly"},
            {"niche": "content-monetize", "ru": "Автор: один платный шаг без инфоцыганства", "en": "Creator: one paid step, no hype"},
        ],
    },
    {
        "id": "tech_tz",
        "name_ru": "Тех-ТЗ под внедрение",
        "name_en": "Implementation Spec",
        "tagline_ru": "Объём · приёмка · вне рамок",
        "tagline_en": "Scope · acceptance · out of scope",
        "benefit_ru": "Документ, который можно отдать исполнителю сегодня",
        "benefit_en": "A document you can hand to an executor today",
        "price_note_ru": "Короткий фиксированный объём",
        "price_note_en": "Lean fixed scope",
        "demo_hook_ru": "1-страничное ТЗ с критериями приёмки",
        "demo_hook_en": "1-page spec with acceptance criteria",
        "wow_ru": "Можно отдать исполнителю сегодня",
        "wow_en": "Ready to hand to an executor today",
        "examples": [
            {"niche": "api-for-devs", "ru": "Интеграции: scope + non-goals + приёмка 3 сценария", "en": "Integrations: scope + non-goals + 3 accept scenarios"},
            {"niche": "device-assembly", "ru": "Устройства: чеклист сборки и критерии «готово»", "en": "Devices: assembly checklist + done criteria"},
        ],
    },
    {
        "id": "ai_agent_desk",
        "name_ru": "ИИ-агент под задачу",
        "name_en": "Task AI Agent",
        "tagline_ru": "Документ → агент по принятому объёму",
        "tagline_en": "Doc → agent on accepted scope",
        "benefit_ru": "Не чат ради чата — исполнимый контур с стоп-правилами",
        "benefit_en": "Not chat for chat’s sake — executable loop with stops",
        "price_note_ru": "Уровень агентской работы · по рынку",
        "price_note_en": "Agent-class work · market-fair",
        "demo_hook_ru": "Пробный прогон: агент идёт по чеклисту на демо-данных",
        "demo_hook_en": "Dry-run: agent walks checklist on demo data",
        "wow_ru": "Не чат — исполнимый контур",
        "wow_en": "Not chat — an executable loop",
        "examples": [
            {"niche": "freelace-d2c", "ru": "Фриланс: агент по match + delivery checklist", "en": "Freelance: agent for match + delivery checklist"},
            {"niche": "ai-agencies", "ru": "Студия: dry-run handoff без выдуманной certainty", "en": "Studio: dry-run handoff without fake certainty"},
        ],
    },
    {
        "id": "distribution_engine",
        "name_ru": "Дистрибуция 3D",
        "name_en": "3D Distribution",
        "tagline_ru": "Бренд · площадки · связи",
        "tagline_en": "Brand · platforms · networking",
        "benefit_ru": "7 дней: 1 ход в каждом канале · без раздутых подписок",
        "benefit_en": "7 days: 1 move per channel · no bloated retainers",
        "price_note_ru": "Без раздутых маркетинговых подписок",
        "price_note_en": "No bloated marketing retainers",
        "demo_hook_ru": "План на 7 дней: 1 ход в каждом канале",
        "demo_hook_en": "7-day plan: 1 move per channel",
        "wow_ru": "Рекомендации под нишу, не шаблонный SMM",
        "wow_en": "Niche recommendations, not generic SMM",
        "examples": [
            {"niche": "education", "ru": "Обучение: бренд + площадка + 3 тёплых intro", "en": "Education: brand + platform + 3 warm intros"},
            {"niche": "content-monetize", "ru": "Контент: proof-пост + lookalike касания", "en": "Content: proof post + lookalike touches"},
        ],
    },
    {
        "id": "expert_base_gen",
        "name_ru": "Экспертная база проекта",
        "name_en": "Project Expert Base",
        "tagline_ru": "Уникальные слои знаний под ТЗ",
        "tagline_en": "Unique knowledge layers per brief",
        "benefit_ru": "База под ваш контур, не «википедия ради объёма»",
        "benefit_en": "A base for your loop — not a wiki for bulk",
        "price_note_ru": "Разово или с обновлениями · без ловушки-абонемента",
        "price_note_en": "One-shot or with updates · no trap subscription",
        "demo_hook_ru": "Срез: онтология + плейбуки + стоп-правила",
        "demo_hook_en": "Slice: ontology + playbooks + kill-switches",
        "wow_ru": "Не энциклопедия — база под ваш контур",
        "wow_en": "Not an encyclopedia — a base for your loop",
        "examples": [
            {"niche": "cost-ops", "ru": "Unit-экон.: ontology утечек + kill-switches", "en": "Unit-econ: leak ontology + kill-switches"},
            {"niche": "asset-decisions", "ru": "Активы: критерии риска без обещаний доходности", "en": "Assets: risk criteria, no yield promises"},
        ],
    },
    {
        "id": "control_panel",
        "name_ru": "Панель управления",
        "name_en": "Control Panel",
        "tagline_ru": "Метрики · задачи · риски",
        "tagline_en": "Metrics · tasks · risks",
        "benefit_ru": "Sense · Decide · Act — без UI-шума",
        "benefit_en": "Sense · Decide · Act — no UI noise",
        "price_note_ru": "Входит в сборку · без лишнего интерфейса",
        "price_note_en": "Part of assembly · no UI clutter",
        "demo_hook_ru": "3 виджета: неопределённость / риск / план",
        "demo_hook_en": "3 widgets: uncertainty / risk / plan",
        "wow_ru": "Как кабинет пилота, не «дашборд ради дашборда»",
        "wow_en": "Pilot cockpit — not a dashboard for its own sake",
        "examples": [
            {"niche": "automation-builders", "ru": "Авто: 3 виджета на пилот, не 40 метрик", "en": "Auto: 3 pilot widgets, not 40 metrics"},
            {"niche": "ai-agencies", "ru": "Студия: risk band + next step на одном экране", "en": "Studio: risk band + next step on one screen"},
        ],
    },
    {
        "id": "full_business_gen",
        "name_ru": "Сгенерировать бизнес 🔥",
        "name_en": "Generate Business 🔥",
        "tagline_ru": "Оркестрация 10 ниш → система + база + панель",
        "tagline_en": "Orchestrate 10 niches → system + base + panel",
        "benefit_ru": "Мозг планирования: ранжирует ниши, стек услуг, расчёты",
        "benefit_en": "Planning brain: ranks niches, service stack, compute",
        "price_note_ru": "Пилот-сборка · цена по сложности",
        "price_note_en": "Pilot assembly · fair for complexity",
        "demo_hook_ru": "Полный прогон на живой нише",
        "demo_hook_en": "Full run on a live niche",
        "wow_ru": "Автономный контур, но с согласованиями как по ТЗ",
        "wow_en": "Autonomous loop, with TZ-style approvals",
        "examples": [
            {"niche": "all", "ru": "Вход: суть · Выход: план + база + панель по 10 нишам", "en": "In: essence · Out: plan + base + panel across 10 niches"},
        ],
        "cta_mode": "generate",
    },
]


_DEMOS: dict[str, dict[str, dict[str, Any]]] = {
    "ops_reframe": {
        "ru": {
            "title": "Демо: карта утечек",
            "lines": [
                "Вход: 40 ч/нед на сдачу",
                "Утечка: 12 ч переделок без табло",
                "Ход: 1 метрика + недельный контроль → цель −15% переделок",
            ],
            "cta": "Поставить себе табло",
        },
        "en": {
            "title": "Leak-map demo",
            "lines": [
                "In: 40 h/wk delivery",
                "Leak: 12 h rework without a scoreboard",
                "Move: 1 metric + weekly gate → aim −15% rework",
            ],
            "cta": "Set your scoreboard",
        },
    },
    "offer_pack": {
        "ru": {
            "title": "Эскиз предложения",
            "lines": [
                "Для: владельцев процессов в нише",
                "Обещание: ясный следующий оплачиваемый шаг",
                "Граница: без гарантии прибыли; работа по ТЗ",
            ],
            "cta": "Собрать полный пакет",
        },
        "en": {
            "title": "Offer sketch",
            "lines": [
                "For: process owners in the niche",
                "Promise: a clear next paid step",
                "Bound: no profit guarantee; work to a brief",
            ],
            "cta": "Build the full pack",
        },
    },
    "tech_tz": {
        "ru": {
            "title": "Срез ТЗ",
            "lines": [
                "В объёме: форма входа + карточка метрики",
                "Вне: биллинг-интеграции v1",
                "Приёмка: клиент подтверждает 3 сценария",
            ],
            "cta": "Дописать ТЗ",
        },
        "en": {
            "title": "Spec slice",
            "lines": [
                "In scope: intake form + metric card",
                "Out: billing integrations v1",
                "Accept: client confirms 3 scenarios",
            ],
            "cta": "Finish the spec",
        },
    },
    "ai_agent_desk": {
        "ru": {
            "title": "Пробный прогон агента",
            "lines": [
                "Вход: принятый документ",
                "Шаги: проверить → сделать → отчитаться",
                "Стоп: нет одобрения человека на денежный ход",
            ],
            "cta": "Подключить агента",
        },
        "en": {
            "title": "Agent dry-run",
            "lines": [
                "In: accepted document",
                "Steps: validate → act → report",
                "Stop: no human approve on money move",
            ],
            "cta": "Connect the agent",
        },
    },
    "distribution_engine": {
        "ru": {
            "title": "Дистрибуция на 7 дней",
            "lines": [
                "Бренд: 1 пост-доказательство",
                "Площадка: 5 касаний похожей аудитории",
                "Связи: 3 тёплых представления",
            ],
            "cta": "Запустить неделю",
        },
        "en": {
            "title": "7-day distribution",
            "lines": [
                "Brand: 1 proof post",
                "Platform: 5 lookalike touches",
                "Network: 3 warm intros",
            ],
            "cta": "Run the week",
        },
    },
    "expert_base_gen": {
        "ru": {
            "title": "Срез базы",
            "lines": [
                "Онтология: 10 сущностей",
                "Плейбуки: приём / сборка / пилот",
                "Стоп-правила: решётка рисков",
            ],
            "cta": "Сгенерировать базу",
        },
        "en": {
            "title": "Base slice",
            "lines": [
                "Ontology: 10 entities",
                "Playbooks: intake / assemble / pilot",
                "Kill-switches: risk lattice",
            ],
            "cta": "Generate the base",
        },
    },
    "control_panel": {
        "ru": {
            "title": "Превью панели",
            "lines": [
                "Неопределённость: 3 известных / 4 неизвестных",
                "Риск: жёлтый",
                "План: шаги 1–4 ждут выбора",
            ],
            "cta": "Открыть панель",
        },
        "en": {
            "title": "Panel preview",
            "lines": [
                "Uncertainty: 3 known / 4 unknown",
                "Risk: amber",
                "Plan: steps 1–4 await choice",
            ],
            "cta": "Open the panel",
        },
    },
    "full_business_gen": {
        "ru": {
            "title": "Искра бизнеса 🔥",
            "lines": [
                "Вход: суть бизнеса",
                "Процесс: синтез + согласования",
                "Выход: код-пакет · экспертная база · панель",
            ],
            "cta": "Сгенерировать бизнес",
        },
        "en": {
            "title": "Business spark 🔥",
            "lines": [
                "In: business essence",
                "Process: synthesis + approvals",
                "Out: code pack · expert base · panel",
            ],
            "cta": "Generate business",
        },
    },
}


def service_demo(service_id: str, lang: str = "ru", seed_text: str = "") -> dict[str, Any]:
    """Lightweight wow-demo payload for each service (pure lang pack)."""
    lang = "en" if lang == "en" else "ru"
    svc = next((s for s in BUSINESS_SERVICES if s["id"] == service_id), None)
    if not svc:
        return {"error": "unknown_service", "id": service_id}

    pack = _DEMOS.get(service_id, {})
    d = pack.get(lang) or pack.get("ru") or {
        "title": svc["name_ru"] if lang == "ru" else svc["name_en"],
        "lines": [svc.get("wow_ru") if lang == "ru" else svc.get("wow_en")],
        "cta": "Далее" if lang == "ru" else "Continue",
    }
    return {
        "service": {
            "id": svc["id"],
            "name": svc["name_ru"] if lang == "ru" else svc["name_en"],
            "name_ru": svc["name_ru"],
            "name_en": svc["name_en"],
            "tagline": svc["tagline_ru"] if lang == "ru" else svc["tagline_en"],
            "price_note": svc["price_note_ru"] if lang == "ru" else svc["price_note_en"],
            "price_note_ru": svc["price_note_ru"],
            "price_note_en": svc["price_note_en"],
            "demo_hook": svc["demo_hook_ru"] if lang == "ru" else svc["demo_hook_en"],
        },
        "demo": d,
        "lang": lang,
        "seed_used": bool(seed_text),
        "note": svc["demo_hook_ru"] if lang == "ru" else svc["demo_hook_en"],
    }


def list_services(lang: str = "ru") -> list[dict[str, Any]]:
    lang = "en" if lang == "en" else "ru"
    out = []
    for s in BUSINESS_SERVICES:
        examples = []
        for ex in s.get("examples") or []:
            examples.append(
                {
                    "niche": ex.get("niche"),
                    "text": ex.get("ru") if lang == "ru" else ex.get("en"),
                }
            )
        out.append(
            {
                "id": s["id"],
                "name": s["name_ru"] if lang == "ru" else s["name_en"],
                "tagline": s["tagline_ru"] if lang == "ru" else s["tagline_en"],
                "benefit": s.get("benefit_ru") if lang == "ru" else s.get("benefit_en"),
                "price_note": s["price_note_ru"] if lang == "ru" else s["price_note_en"],
                "demo_hook": s["demo_hook_ru"] if lang == "ru" else s["demo_hook_en"],
                "wow": s["wow_ru"] if lang == "ru" else s["wow_en"],
                "examples": examples,
                "cta_mode": s.get("cta_mode") or "consult",
            }
        )
    return out
