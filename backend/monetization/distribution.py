"""
Modern distribution recommendations: brand · platforms · networking.

Used by promo layer and business generation for non-generic outreach.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DistributionPlan:
    brand: dict[str, Any]
    platforms: list[dict[str, Any]]
    networks: list[dict[str, Any]]
    week_plan: list[dict[str, str]]
    niche_hooks: list[str]
    anti_patterns: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DistributionEngine:
    name = "DistributionEngine"

    PLATFORM_BANK = {
        "x": {
            "id": "x",
            "name": "X / Twitter",
            "fit": ["thought", "dm", "builder"],
            "moves": ["proof post", "thread from pilot metric", "DM with artifact link"],
        },
        "telegram": {
            "id": "telegram",
            "name": "Telegram",
            "fit": ["workers", "warm", "ru_cis"],
            "moves": ["channel proof", "task drop for workers", "1:1 ops chat"],
        },
        "niche_board": {
            "id": "niche_board",
            "name": "Niche boards / marketplaces",
            "fit": ["demand", "local", "b2b"],
            "moves": ["listing with TZ language", "lookalike reply", "case snippet"],
        },
        "linkedin": {
            "id": "linkedin",
            "name": "LinkedIn",
            "fit": ["b2b", "agency", "enterprise"],
            "moves": ["operator post", "soft CTA to consult", "partner note"],
        },
        "site": {
            "id": "site",
            "name": "Global Ru Workers site",
            "fit": ["convert", "demo", "seo"],
            "moves": ["landing mode jump", "service demo wow", "panel screenshot"],
        },
        "partner": {
            "id": "partner",
            "name": "Partner / white-label",
            "fit": ["scale", "trust_transfer"],
            "moves": ["WL kit", "rev-share clarity", "joint case"],
        },
    }

    def build(
        self,
        *,
        industry_id: str,
        industry_name: str,
        idea_title: str,
        domain: str = "",
        promo_fit: float = 0.5,
        lang: str = "ru",
    ) -> DistributionPlan:
        brand = {
            "promise": (
                "Инженерия бизнеса: артефакт + метрика. Не кот в мешке."
                if lang == "ru"
                else "Business engineering: artifact + metric. No pig in a poke."
            ),
            "voice": "calm operator",
            "proof_assets": [
                "consultation document",
                "service demo (2 min wow)",
                "pilot metric card",
            ],
            "contrast": [
                "not info-marketer hype pricing",
                "not empty AI chat",
                "not yield guarantees",
            ],
            "name_lock": "Metrix AI · Global Ru Workers",
        }

        platforms = self._pick_platforms(industry_id, domain, promo_fit)
        networks = [
            {
                "id": "warm_intros",
                "name": "Тёплый нетворкинг" if lang == "ru" else "Warm networking",
                "priority": 1,
                "action": "3 intro/неделя с артефактом в кармане, не «привет чем занимаешься»",
            },
            {
                "id": "worker_liquidity",
                "name": "Пул воркеров",
                "priority": 2,
                "action": "Открытые escrow-задачи → execution liquidity",
            },
            {
                "id": "operator_circles",
                "name": "Круги операторов ниши",
                "priority": 3,
                "action": "1 полезный разбор чужой проблемы в неделю (give first)",
            },
        ]

        week_plan = [
            {"day": "1", "channel": "brand", "action": f"Proof-пост: {idea_title[:60]}"},
            {"day": "2", "channel": "network", "action": "2 тёплых intro + 1 partner note"},
            {"day": "3", "channel": "platform", "action": "5 lookalike касаний с демо-ссылкой"},
            {"day": "4", "channel": "workers", "action": "1 escrow-задача в ленту воркеров"},
            {"day": "5", "channel": "brand", "action": "Метрика/анти-паттерн (без хвастовства)"},
            {"day": "6", "channel": "platform", "action": "Ответы/треды в нишевых местах"},
            {"day": "7", "channel": "review", "action": "Что дало касание→разговор; убить слабый канал"},
        ]

        niche_hooks = self._hooks(industry_id, industry_name, domain, lang)
        anti = [
            "Постить «мотивацию» без артефакта",
            "Одинаковый pitch во все каналы",
            "Скрывать cut/условия от воркеров",
            "Обещать доходность",
            "Покупать охваты до product proof",
        ]

        summary = (
            f"Distribution 3D for «{idea_title[:40]}» @ {industry_name}: "
            f"{len(platforms)} platforms, {len(networks)} networks, 7-day plan."
        )
        return DistributionPlan(
            brand=brand,
            platforms=platforms,
            networks=networks,
            week_plan=week_plan,
            niche_hooks=niche_hooks,
            anti_patterns=anti,
            summary=summary,
        )

    def _pick_platforms(
        self, industry_id: str, domain: str, promo_fit: float
    ) -> list[dict[str, Any]]:
        base = ["site", "x", "telegram"]
        if industry_id in ("ai-agencies", "expert-services", "saas-founders", "api-for-devs"):
            base.append("linkedin")
        if industry_id in ("freelace-d2c", "device-assembly", "ecommerce", "content-monetize"):
            base.append("niche_board")
        if domain == "resource_logistics":
            base.extend(["niche_board", "partner"])
        if promo_fit >= 0.55:
            base.append("partner")
        # unique preserve order
        seen = set()
        out = []
        for pid in base:
            if pid in seen:
                continue
            seen.add(pid)
            p = dict(self.PLATFORM_BANK[pid])
            p["priority"] = len(out) + 1
            out.append(p)
        return out

    def _hooks(
        self, industry_id: str, industry_name: str, domain: str, lang: str
    ) -> list[str]:
        hooks = [
            f"Ниша {industry_name}: не «AI для всего», а один оплачиваемый контур",
            "Демо раньше цены — wow за 2 минуты",
            "Оплата после подтверждённой ценности (где модель позволяет)",
        ]
        if domain == "resource_logistics":
            hooks.append("Сначала bottleneck потока, потом маркетинг тонн")
        if industry_id == "content-monetize":
            hooks.append("Один платный шаг из фактов, не контент ради контента")
        if industry_id == "ai-agencies":
            hooks.append("Rework hours scoreboard — язык, который понимают студии")
        return hooks
