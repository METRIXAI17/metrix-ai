"""
Capital cooperation — pillar 3 of Metrix Funding.

Cooperation from partner interactions with *placed* capital —
not a classic raise pitch alone. Evidence first, narrative second.
"""

from __future__ import annotations

import re
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


READINESS_CHECKS = [
    ("unit_proof", "Unit economics proof", "Unit-экономика (цифры)"),
    ("pilot_evidence", "Pilot evidence", "Факты пилота"),
    ("ops_story", "Calm ops story", "Спокойная ops-история"),
    ("owner_map", "Owner map (who runs)", "Карта владельцев"),
    ("kill_rules", "Kill rules written", "Kill-rules записаны"),
    ("ledger", "Capital ledger open", "Ledger капитала открыт"),
]


class CapitalCoopEngine:
    """Partner cooperation loops around placed capital."""

    name = "Capital Cooperation"
    pillar = 3
    status = "live"

    def build(
        self,
        business_text: str,
        *,
        project_name: str = "",
        capital_usd: float | None = None,
        partner_role: str = "operator",
        lang: str = "ru",
    ) -> dict[str, Any]:
        L = _lang(lang)
        t = (business_text or "").lower()
        name = project_name or (business_text or "")[:60] or "Project"
        cap = float(capital_usd) if capital_usd and capital_usd > 0 else self._infer_cap(t)
        role = partner_role if partner_role in ("operator", "capital", "hybrid") else "hybrid"
        readiness = self._readiness(t, L)
        slots = self._placement_slots(L, cap, t)
        loops = self._coop_loops(L, role, name)
        partner_pack = self._partner_pack(L, readiness, slots)

        return {
            "module": self.name,
            "pillar": self.pillar,
            "status": self.status,
            "project": name,
            "thesis": _d(
                L,
                "Кооперация с размещённым капиталом: капитал кладётся в именованный слот, "
                "партнёры работают по общему табло (паки Metrix), outcome → narrative "
                "для следующего касания. Сначала evidence, потом story.",
                "Cooperation with placed capital: capital sits in a named slot, "
                "partners run on a shared scoreboard (Metrix packs), outcome → narrative "
                "for the next touch. Evidence first, story second.",
            ),
            "partner_role": role,
            "capital_usd": cap,
            "readiness": readiness,
            "placement_slots": slots,
            "coop_loops": loops,
            "partner_pack": partner_pack,
            "next_actions": self._next_actions(L, readiness, role),
            "summary": _d(
                L,
                f"Pillar 3 · {name}: cap≈${cap:,.0f} · role={role} · "
                f"ready={readiness['score']:.0%} · slots={len(slots)}",
                f"Pillar 3 · {name}: cap≈${cap:,.0f} · role={role} · "
                f"ready={readiness['score']:.0%} · slots={len(slots)}",
            ),
        }

    def _infer_cap(self, text: str) -> float:
        m = re.search(r"(\d[\d\s]{2,})\s*(k|к|тыс|\$|usd)?", text, re.I)
        if m:
            raw = m.group(1).replace(" ", "")
            try:
                n = float(raw)
                unit = (m.group(2) or "").lower()
                if unit in ("k", "к", "тыс"):
                    n *= 1000
                if n < 500:
                    n *= 1000
                return min(n, 5_000_000)
            except ValueError:
                pass
        return 10_000.0

    def _readiness(self, text: str, L: str) -> dict[str, Any]:
        keywords = {
            "unit_proof": ("unit", "марж", "margin", "cac", "ltv", "arpu", "экономик"),
            "pilot_evidence": ("пилот", "pilot", "case", "кейс", "результат", "proof"),
            "ops_story": ("ops", "процесс", "workflow", "контур", "playbook"),
            "owner_map": ("owner", "владел", "ответствен", "кто ведёт", "who runs"),
            "kill_rules": ("kill", "стоп", "stop-rule", "если 0"),
            "ledger": ("ledger", "учёт", "табло", "scoreboard", "budget"),
        }
        checks = []
        hit = 0
        for key, en, ru in READINESS_CHECKS:
            toks = keywords.get(key, ())
            ok = any(x in text for x in toks)
            if ok:
                hit += 1
            checks.append({"id": key, "label": en if L == "en" else ru, "ok": ok})
        score = hit / max(1, len(READINESS_CHECKS))
        gate = (
            "partner_ready"
            if score >= 0.5
            else "build_evidence"
            if score >= 0.25
            else "structure_first"
        )
        msg_ru = {
            "partner_ready": "Достаточно сигналов — можно открывать partner pack.",
            "build_evidence": "Нужны 1–2 proof (unit или pilot) до capital pitch.",
            "structure_first": "Сначала structural income + 1 closed orient — потом capital.",
        }[gate]
        msg_en = {
            "partner_ready": "Enough signals — open partner pack.",
            "build_evidence": "Need 1–2 proofs (unit or pilot) before capital pitch.",
            "structure_first": "Structural income + 1 closed orient first — then capital.",
        }[gate]
        return {
            "score": round(score, 2),
            "gate": gate,
            "checks": checks,
            "message": _d(L, msg_ru, msg_en),
        }

    def _placement_slots(
        self, L: str, cap: float, text: str
    ) -> list[dict[str, Any]]:
        a = round(cap * 0.40, 2)
        b = round(cap * 0.35, 2)
        c = round(cap * 0.25, 2)
        promo_bias = any(w in text for w in ("промо", "promo", "лид", "lead", "growth"))
        if promo_bias:
            a, b = b, a
        return [
            {
                "id": "slot_ops",
                "name": _d(L, "Ops / pilot capacity", "Ops / pilot capacity"),
                "usd": a,
                "purpose": _d(
                    L,
                    "Ёмкость пилотов и free-work → paid gate",
                    "Pilot capacity and free-work → paid gate",
                ),
                "kpi": _d(L, "≥1 pilot intent / 30d", "≥1 pilot intent / 30d"),
            },
            {
                "id": "slot_dist",
                "name": _d(L, "Distribution / promo", "Distribution / promo"),
                "usd": b,
                "purpose": _d(
                    L,
                    "Площадки, DM, channel seats (assets 1:1)",
                    "Platforms, DMs, channel seats (assets 1:1)",
                ),
                "kpi": _d(L, "≥5 qualified DM / 14d", "≥5 qualified DM / 14d"),
            },
            {
                "id": "slot_buffer",
                "name": _d(L, "Buffer / reserve", "Buffer / reserve"),
                "usd": c,
                "purpose": _d(
                    L,
                    "Резерв на idle kill и 1 attach-эксперимент",
                    "Reserve for idle kills and 1 attach experiment",
                ),
                "kpi": _d(L, "buffer ≥ 20% после 30d", "buffer ≥ 20% after 30d"),
            },
        ]

    def _coop_loops(self, L: str, role: str, name: str) -> list[dict[str, Any]]:
        run_step = (
            _d(
                L,
                "Operator: free consult + generate + promo cadence",
                "Operator: free consult + generate + promo cadence",
            )
            if role != "capital"
            else _d(
                L,
                "Capital partner: weekly review ledger + kill rights",
                "Capital partner: weekly review ledger + kill rights",
            )
        )
        return [
            {
                "id": "loop_place",
                "title": _d(L, "1. Размещение", "1. Placement"),
                "steps": [
                    _d(
                        L,
                        f"Именовать капитал для «{name}» в 3 слота",
                        f"Name capital for «{name}» into 3 slots",
                    ),
                    _d(L, "Записать owner на каждый слот", "Assign owner per slot"),
                    _d(L, "Открыть shared scoreboard (pack)", "Open shared scoreboard (pack)"),
                ],
            },
            {
                "id": "loop_run",
                "title": _d(L, "2. Прогон", "2. Run"),
                "steps": [
                    run_step,
                    _d(
                        L,
                        "Assets 1:1 только на closed/active sales",
                        "Assets 1:1 only on closed/active sales",
                    ),
                    _d(L, "Еженедельный 15-min partner sync", "Weekly 15-min partner sync"),
                ],
            },
            {
                "id": "loop_feedback",
                "title": _d(L, "3. Обратная связь → narrative", "3. Feedback → narrative"),
                "steps": [
                    _d(L, "Снять 1 proof artifact / 14d", "Ship 1 proof artifact / 14d"),
                    _d(
                        L,
                        "Обновить capital narrative (evidence first)",
                        "Update capital narrative (evidence first)",
                    ),
                    _d(
                        L,
                        "Решение: top-up / reallocate / pause (kill)",
                        "Decision: top-up / reallocate / pause (kill)",
                    ),
                ],
            },
        ]

    def _partner_pack(
        self, L: str, readiness: dict[str, Any], slots: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "title": _d(L, "Partner pack (1 page)", "Partner pack (1 page)"),
            "sections": [
                _d(L, "Problem in 3 lines", "Problem in 3 lines"),
                _d(L, "Unit / pilot proof (or plan)", "Unit / pilot proof (or plan)"),
                _d(L, "Placement slots + owners", "Placement slots + owners"),
                _d(L, "Coop cadence (weekly 15 min)", "Coop cadence (weekly 15 min)"),
                _d(L, "Kill rules + reallocation rights", "Kill rules + reallocation rights"),
            ],
            "gate": readiness.get("gate"),
            "slot_ids": [s["id"] for s in slots],
            "share_rule": _d(
                L,
                "Partner share после 1 proof cycle — не day-0 hype.",
                "Partner share after 1 proof cycle — not day-0 hype.",
            ),
        }

    def _next_actions(
        self, L: str, readiness: dict[str, Any], role: str
    ) -> list[str]:
        gate = readiness.get("gate")
        acts = []
        if gate == "structure_first":
            acts.append(
                _d(
                    L,
                    "Запустить Funding form → Pillar 1 setup (5 шагов).",
                    "Run Funding form → Pillar 1 setup (5 steps).",
                )
            )
            acts.append(
                _d(
                    L,
                    "Сделать 1 free consult + 1 generate multi-pass.",
                    "Do 1 free consult + 1 generate multi-pass.",
                )
            )
        elif gate == "build_evidence":
            acts.append(
                _d(
                    L,
                    "Закрыть 1 orientation / tech-TZ с numbers.",
                    "Close 1 orientation / tech-TZ with numbers.",
                )
            )
            acts.append(
                _d(
                    L,
                    "Собрать partner pack 1 page.",
                    "Assemble 1-page partner pack.",
                )
            )
        else:
            acts.append(
                _d(
                    L,
                    "Открыть partner pack + назначить owners слотов.",
                    "Open partner pack + assign slot owners.",
                )
            )
            acts.append(
                _d(
                    L,
                    "Первый weekly sync: ledger + 1 attach experiment.",
                    "First weekly sync: ledger + 1 attach experiment.",
                )
            )
        if role == "capital":
            acts.append(
                _d(
                    L,
                    "Capital: не операционировать — только review + kill rights.",
                    "Capital: do not operate — review + kill rights only.",
                )
            )
        return acts
