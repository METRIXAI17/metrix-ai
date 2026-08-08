"""
Assets 1:1 — pillar 2 of Metrix Funding.

Attach real assets to already-configured sales (upsells on closed or
in-flight deals). Two commercial modes:

  A) Short-term rental of assets
  B) Percentage of outcome on attached work

Never: «asset automatically yields». Always: 1:1 link to a sale or pilot.
"""

from __future__ import annotations

from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


ASSET_TYPES = [
    {
        "id": "compute_slot",
        "label_ru": "Слот compute / runtime",
        "label_en": "Compute / runtime slot",
        "rental_usd_week": 120,
        "pct_share": 8,
        "risk": "usage spikes · idle waste",
    },
    {
        "id": "va_pack",
        "label_ru": "Virtual asset pack (бренд / UI)",
        "label_en": "Virtual asset pack (brand / UI)",
        "rental_usd_week": 90,
        "pct_share": 10,
        "risk": "scope creep · taste loops",
    },
    {
        "id": "channel_seat",
        "label_ru": "Место в канале / дистрибуции",
        "label_en": "Channel / distribution seat",
        "rental_usd_week": 150,
        "pct_share": 12,
        "risk": "platform bans · cold lists",
    },
    {
        "id": "ops_board",
        "label_ru": "Ops board / scoreboard seat",
        "label_en": "Ops board / scoreboard seat",
        "rental_usd_week": 80,
        "pct_share": 7,
        "risk": "no owner · stale metrics",
    },
    {
        "id": "pilot_capacity",
        "label_ru": "Ёмкость пилота (14–30d)",
        "label_en": "Pilot capacity (14–30d)",
        "rental_usd_week": 280,
        "pct_share": 15,
        "risk": "client delay · unpaid change requests",
    },
]


class AssetAttachEngine:
    """Build 1:1 asset attach plans on top of configured sales."""

    name = "Assets 1:1 Attach"
    pillar = 2
    status = "live"

    def build(
        self,
        business_text: str,
        *,
        project_name: str = "",
        existing_sales: list[str] | None = None,
        preferred_mode: str = "auto",
        lang: str = "ru",
    ) -> dict[str, Any]:
        L = _lang(lang)
        t = (business_text or "").lower()
        name = project_name or (business_text or "")[:60] or "Project"
        sales = existing_sales or self._infer_sales(t)
        mode = self._resolve_mode(preferred_mode, t)
        attachments = self._pick_attachments(t, mode, L)
        playbook = self._playbook(L, sales, attachments, mode)

        return {
            "module": self.name,
            "pillar": self.pillar,
            "status": self.status,
            "project": name,
            "thesis": _d(
                L,
                "Активы 1:1 = допродажи к уже настроенным продажам. "
                "Либо краткосрочная аренда актива, либо % от результата — "
                "всегда привязка к сделке, никогда «актив сам зарабатывает».",
                "Assets 1:1 = upsells on already-configured sales. "
                "Either short-term asset rental or % of outcome — "
                "always tied to a deal, never «asset earns alone».",
            ),
            "mode": mode,
            "base_sales": sales,
            "attachments": attachments,
            "playbook": playbook,
            "rules": [
                _d(
                    L,
                    "Правило 1:1 — один attach ↔ один sale / pilot SKU.",
                    "1:1 rule — one attach ↔ one sale / pilot SKU.",
                ),
                _d(
                    L,
                    "Аренда: срок 1–4 недели, kill если idle > 40% времени.",
                    "Rental: 1–4 weeks, kill if idle > 40% of time.",
                ),
                _d(
                    L,
                    "%: потолок share 7–15%, только после signed scope.",
                    "%: share cap 7–15%, only after signed scope.",
                ),
                _d(
                    L,
                    "Нет auto-yield: актив = структура + риск-метрика.",
                    "No auto-yield: asset = structure + risk metric.",
                ),
            ],
            "summary": _d(
                L,
                f"Pillar 2 · {name}: mode={mode} · {len(attachments)} attach · base={', '.join(sales[:3])}",
                f"Pillar 2 · {name}: mode={mode} · {len(attachments)} attaches · base={', '.join(sales[:3])}",
            ),
        }

    def _infer_sales(self, text: str) -> list[str]:
        sales = ["orient_run"]
        if any(w in text for w in ("пилот", "pilot", "внедр")):
            sales.append("pilot_14")
        if any(w in text for w in ("промо", "promo", "маркетинг", "dm")):
            sales.append("marketing")
        if any(w in text for w in ("full", "пакет", "stack", "агентств")):
            sales.append("full_package")
        if any(w in text for w in ("consult", "консульт", "тех-тз", "tech")):
            sales.append("consult_tech_tz")
        seen: set[str] = set()
        out: list[str] = []
        for s in sales:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    def _resolve_mode(self, preferred: str, text: str) -> str:
        p = (preferred or "auto").lower()
        if p in ("rental", "percent"):
            return p
        if any(w in text for w in ("% ", "процент", "share", "rev-share", "revenue share")):
            return "percent"
        if any(w in text for w in ("аренд", "rent", "lease", "slot", "слот")):
            return "rental"
        return "hybrid"

    def _pick_attachments(
        self, text: str, mode: str, L: str
    ) -> list[dict[str, Any]]:
        picks: list[dict[str, Any]] = []
        for a in ASSET_TYPES:
            score = 0.4
            aid = a["id"]
            if aid == "compute_slot" and any(
                w in text for w in ("api", "cloud", "runtime", "агент", "llm", "compute")
            ):
                score += 0.35
            if aid == "va_pack" and any(
                w in text for w in ("бренд", "brand", "ui", "дизайн", "virtual", "va")
            ):
                score += 0.35
            if aid == "channel_seat" and any(
                w in text
                for w in ("канал", "channel", "дистриб", "x.com", "telegram", "лид")
            ):
                score += 0.35
            if aid == "ops_board":
                score += 0.15
            if aid == "pilot_capacity" and any(
                w in text for w in ("пилот", "pilot", "14", "30", "внедр")
            ):
                score += 0.4
            if score < 0.5:
                continue
            label = a["label_en"] if L == "en" else a["label_ru"]
            offer: dict[str, Any] = {
                "asset_id": aid,
                "label": label,
                "fit": round(min(1.0, score), 2),
                "risk": a["risk"],
                "attach_to": "pilot_14" if aid == "pilot_capacity" else "orient_run",
            }
            if mode in ("rental", "hybrid"):
                offer["rental"] = {
                    "usd_per_week": a["rental_usd_week"],
                    "min_weeks": 1,
                    "max_weeks": 4,
                    "note": _d(L, "Оплата вперёд · idle kill 40%", "Prepaid · idle kill 40%"),
                }
            if mode in ("percent", "hybrid"):
                offer["percent"] = {
                    "share_pct": a["pct_share"],
                    "of": _d(L, "валового outcome пилота / сделки", "gross pilot / deal outcome"),
                    "cap_note": _d(
                        L,
                        "Только после signed scope + numbers",
                        "Only after signed scope + numbers",
                    ),
                }
            picks.append(offer)
        picks.sort(key=lambda x: x["fit"], reverse=True)
        return picks[:4] or [
            {
                "asset_id": "ops_board",
                "label": _d(L, "Ops board seat", "Ops board seat"),
                "fit": 0.55,
                "risk": "no owner",
                "attach_to": "orient_run",
                "rental": {"usd_per_week": 80, "min_weeks": 1, "max_weeks": 4},
                "percent": {"share_pct": 7, "of": "deal outcome"},
            }
        ]

    def _playbook(
        self,
        L: str,
        sales: list[str],
        attachments: list[dict[str, Any]],
        mode: str,
    ) -> list[str]:
        base = sales[0] if sales else "orient_run"
        first = attachments[0]["asset_id"] if attachments else "ops_board"
        return [
            _d(
                L,
                f"1. Закрыть/зафиксировать base sale «{base}» (или active pilot).",
                f"1. Close/lock base sale «{base}» (or active pilot).",
            ),
            _d(
                L,
                f"2. Предложить attach «{first}» в mode={mode} — 1 абзац, 1 цена, 1 kill.",
                f"2. Offer attach «{first}» in mode={mode} — 1 para, 1 price, 1 kill.",
            ),
            _d(
                L,
                "3. В ledger: sale_id · asset_id · rental|% · start · end · owner.",
                "3. Ledger: sale_id · asset_id · rental|% · start · end · owner.",
            ),
            _d(
                L,
                "4. Через 7 дней: utilization review. Idle → cut or convert to %.",
                "4. Day 7: utilization review. Idle → cut or convert to %.",
            ),
            _d(
                L,
                "5. Не продавать 2+ attach до proof utilization первого.",
                "5. Do not sell 2+ attaches before first utilization proof.",
            ),
        ]
