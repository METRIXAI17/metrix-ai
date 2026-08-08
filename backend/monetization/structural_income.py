"""
Structural auto-income — pillar 1 of Metrix Funding.

Not «passive yield on assets». This configures OUTPUT of the system
and wires instant revenue levers that fire when a client or partner
touches an already-running surface.

«Auto» = structure produces repeatable cash mechanics after setup,
not magic ROI promises.
"""

from __future__ import annotations

from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


INSTANT_LEVERS = [
    {
        "id": "orient_run",
        "sku": "orient_run",
        "price_usd": 290,
        "surface": "paid orientation / free-work advance",
        "trigger": "brief >=20 chars -> instant diagnosis pack",
    },
    {
        "id": "consult_tech",
        "sku": "consult_tech_tz",
        "price_usd": 0,
        "surface": "public Consult + Tech-TZ",
        "trigger": "niche + business -> free work -> pilot gate",
    },
    {
        "id": "promo_pack",
        "sku": "marketing",
        "price_usd": 690,
        "surface": "promotion-pack mode",
        "trigger": "offer + numbers -> 3 roads + DM scripts",
    },
    {
        "id": "pilot_14",
        "sku": "pilot_14",
        "price_usd": 1490,
        "surface": "paid pilot 14-30d",
        "trigger": "hypothesis locked + numbers filled",
    },
    {
        "id": "full_package",
        "sku": "full_package",
        "price_usd": 2490,
        "surface": "Product · Models · Promo stack",
        "trigger": "after one successful pilot or pack tour",
    },
]


class StructuralIncomeEngine:
    """Configure output + instant revenue levers for a business brief."""

    name = "Structural Auto-Income"
    pillar = 1
    status = "live"

    def build(
        self,
        business_text: str,
        *,
        project_name: str = "",
        capital_hint_usd: float | None = None,
        lang: str = "ru",
    ) -> dict[str, Any]:
        L = _lang(lang)
        t = (business_text or "").lower()
        name = project_name or (business_text or "")[:60] or "Project"

        ranked = self._rank_levers(t)
        output_map = self._output_map(L, name, ranked)
        setup = self._setup_steps(L, ranked)
        weekly = self._weekly_cadence(L)
        band = self._income_band(capital_hint_usd, ranked)

        return {
            "module": self.name,
            "pillar": self.pillar,
            "status": self.status,
            "project": name,
            "thesis": _d(
                L,
                "Структурный авто-доход = настроенный OUTPUT + мгновенные рычаги. "
                "Деньги появляются, когда касаются уже работающей поверхности — "
                "не «активы сами капают».",
                "Structural auto-income = configured OUTPUT + instant levers. "
                "Cash appears when someone touches a live surface — "
                "not «assets drip by themselves».",
            ),
            "output_map": output_map,
            "instant_levers": ranked,
            "setup_steps": setup,
            "weekly_cadence": weekly,
            "income_band": band,
            "anti_promises": [
                _d(
                    L,
                    "Не обещаем пассивный yield по активам без внедрения.",
                    "No passive asset yield promises without implementation.",
                ),
                _d(
                    L,
                    "Авто = повторяемая механика после настройки, не «кнопка бабло».",
                    "Auto = repeatable mechanics after setup, not a cash button.",
                ),
            ],
            "summary": _d(
                L,
                f"Pillar 1 · {name}: {len(ranked)} рычага · top={ranked[0]['id'] if ranked else '—'} · "
                f"setup {len(setup)} шагов.",
                f"Pillar 1 · {name}: {len(ranked)} levers · top={ranked[0]['id'] if ranked else '—'} · "
                f"{len(setup)} setup steps.",
            ),
        }

    def _rank_levers(self, text: str) -> list[dict[str, Any]]:
        scores: list[tuple[float, dict[str, Any]]] = []
        for lev in INSTANT_LEVERS:
            s = 0.45
            lid = lev["id"]
            if lid == "orient_run":
                s += 0.25
            if lid == "consult_tech":
                s += 0.2
            if lid == "promo_pack" and any(
                w in text
                for w in ("промо", "promo", "продаж", "dm", "лид", "lead", "маркетинг")
            ):
                s += 0.3
            if lid == "pilot_14" and any(
                w in text for w in ("пилот", "pilot", "внедр", "implement", "14", "30")
            ):
                s += 0.35
            if lid == "full_package" and any(
                w in text for w in ("агентств", "agency", "full", "stack", "пакет")
            ):
                s += 0.2
            if any(w in text for w in ("saas", "api", "cloud", "облак", "finops")):
                if lid in ("orient_run", "pilot_14"):
                    s += 0.1
            scores.append((min(1.0, s), dict(lev)))
        scores.sort(key=lambda x: x[0], reverse=True)
        out = []
        for sc, lev in scores:
            lev = dict(lev)
            lev["fit"] = round(sc, 2)
            lev["role"] = "primary" if sc >= 0.7 else "secondary" if sc >= 0.5 else "later"
            out.append(lev)
        return out

    def _output_map(
        self, L: str, name: str, levers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        primary = [x for x in levers if x.get("role") == "primary"][:2]
        return {
            "title": _d(L, "Карта OUTPUT", "OUTPUT map"),
            "what_ships": [
                _d(
                    L,
                    f"Публичная поверхность: Generate / Consult / Promo / Funding для «{name}»",
                    f"Public surface: Generate / Consult / Promo / Funding for «{name}»",
                ),
                _d(
                    L,
                    "Ops-контур: free-work → tech write → pilot gate (цена в ops)",
                    "Ops contour: free-work → tech write → pilot gate (price in ops)",
                ),
                _d(
                    L,
                    "Артефакты: identity pack · asset map · commercial offer card",
                    "Artifacts: identity pack · asset map · commercial offer card",
                ),
            ],
            "primary_levers": [x["id"] for x in primary] or ["orient_run"],
            "close_path": _d(
                L,
                "Бриф → мгновенный pack → DM/оплата orientation → pilot при numbers",
                "Brief → instant pack → DM/pay orientation → pilot when numbers ready",
            ),
        }

    def _setup_steps(self, L: str, levers: list[dict[str, Any]]) -> list[str]:
        top = levers[0]["id"] if levers else "orient_run"
        return [
            _d(
                L,
                "1. Зафиксировать 1 оффер в 1 строке + 1 proof (кейс / metric / card).",
                "1. Lock 1 offer in 1 line + 1 proof (case / metric / card).",
            ),
            _d(
                L,
                f"2. Включить primary lever «{top}» как default CTA на сайте и в DM.",
                f"2. Wire primary lever «{top}» as default CTA on site and in DM.",
            ),
            _d(
                L,
                "3. Настроить OUTPUT: free consult → free-work phases → paid gate.",
                "3. Configure OUTPUT: free consult → free-work phases → paid gate.",
            ),
            _d(
                L,
                "4. Ledger касаний: кто / дата / артефакт / next lever.",
                "4. Touch ledger: who / date / artifact / next lever.",
            ),
            _d(
                L,
                "5. Kill-rule 14 дней: 0 qualified DM → сменить angle.",
                "5. 14-day kill: 0 qualified DM → change angle.",
            ),
        ]

    def _weekly_cadence(self, L: str) -> list[dict[str, str]]:
        return [
            {
                "day": "Mon",
                "act": _d(L, "1 proof-пост + 5 тёплых DM", "1 proof post + 5 warm DMs"),
            },
            {
                "day": "Wed",
                "act": _d(
                    L,
                    "1 free consult / generate run → case snippet",
                    "1 free consult / generate run → case snippet",
                ),
            },
            {
                "day": "Fri",
                "act": _d(
                    L,
                    "Review ledger: lever → $ · 1 CTA fix",
                    "Ledger review: lever → $ · 1 CTA fix",
                ),
            },
        ]

    def _income_band(
        self, capital_hint: float | None, levers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        top_prices = [x["price_usd"] for x in levers[:3] if x.get("price_usd")]
        avg = sum(top_prices) / max(1, len(top_prices)) if top_prices else 290
        low = round(avg * 2)
        mid = round(avg * 4)
        high = round(avg * 8)
        if capital_hint and capital_hint > 0:
            boost = min(1.5, 1.0 + capital_hint / 50_000)
            low = round(low * boost)
            mid = round(mid * boost)
            high = round(high * boost)
        return {
            "currency": "USD",
            "monthly_structural_low": low,
            "monthly_structural_mid": mid,
            "monthly_structural_high": high,
            "basis": "2-8 mid-lever closes / mo · not a yield promise",
            "requires": "live surface + weekly cadence + kill rules",
        }
