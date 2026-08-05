"""
Core deliverable builder — human-first report for the $790 Core tariff.

Market Units battle-ready pack (2026-08-05):
1. Signer numbers → answers (constraint_cash, days window)
2. Live 7-day channel log (10–15 touches + 1 artifact)
3. Calendar kill dates on T1–T3
4. Deep niche architecture cards (not library meta-templates)
5. PDF/print HTML + cards CSV as file deliverables
6. Implementation assistant path after approval
7. Full EN/RU markdown parity
"""

from __future__ import annotations

import csv
import io
import re
from datetime import date, timedelta
from typing import Any

CORE_PRICE_USD = 790


def _clip(text: str, n: int = 180) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


# ── Profile ──────────────────────────────────────────────────────────────────


def _detect_profile(business_text: str) -> dict[str, Any]:
    t = (business_text or "").lower()
    is_library = any(
        w in t
        for w in (
            "библиотек",
            "library",
            "карточ",
            "архитект",
            "architecture",
            "design pack",
            "билдер",
            "builder",
            "концепт",
            "ниш",
            "marketplace",
            "маркетплейс",
        )
    )
    is_online = any(
        w in t for w in ("онлайн", "online", "saas", "web", "digital", "сайт", "app")
    )
    is_agency = any(
        w in t for w in ("агентств", "agency", "студи", "studio", "rework", "handoff")
    )
    if is_library:
        profile = "knowledge_library"
        payer = "B2B builders / IT product studios (cycle 1); optional platform sub later"
        unit = "Architecture card pack (niche pack) or paid design-review order"
        unit_id = "unit_pack"
        direction = "product_pack"
        channel = "Warm builder DM list + 1 public proof artifact (7-day log)"
        channel_id = "ch_network"
        metric = "≥1 paid unit in 21 days + unit margin ≥ 55% after time COGS"
        metric_id = "m_paid_units"
    elif is_agency:
        profile = "agency_ops"
        payer = "Agency B2B client (retainer / pilot)"
        unit = "Paid project / pilot sprint"
        unit_id = "unit_order"
        direction = "ops_fix"
        channel = "Referrals + 1 outbound sequence (7-day log)"
        channel_id = "ch_network"
        metric = "Delivery margin + rework % drop in 21 days"
        metric_id = "m_margin"
    else:
        profile = "generic_ops"
        payer = "First-cycle payer — confirm B2B / B2C / platform"
        unit = "Paid order / pack"
        unit_id = "unit_order"
        direction = "ops_fix"
        channel = "One realistic channel (7-day touch log)"
        channel_id = "ch_network"
        metric = "One pilot metric (margin / paid units / cycle time)"
        metric_id = "m_margin"

    return {
        "profile": profile,
        "is_library": is_library,
        "is_online": is_online or is_library,
        "payer": payer,
        "unit": unit,
        "unit_id": unit_id,
        "direction": direction,
        "channel": channel,
        "channel_id": channel_id,
        "metric": metric,
        "metric_id": metric_id,
        "title_hint": _clip(business_text, 100) or "Growth / Yield core",
    }


# ── Signer numbers → answers ──────────────────────────────────────────────────


def merge_signer_numbers(
    answers: dict[str, str] | None,
    numbers: dict[str, float] | None,
    *,
    profile: dict[str, Any] | None = None,
    lang: str = "ru",
) -> tuple[dict[str, str], dict[str, float]]:
    """
    Map cash_ceiling + days into answers/numbers so open Q for
    constraint_cash / constraint_time close without extra human slots.
    """
    ans = dict(answers or {})
    nums = dict(numbers or {})
    prof = profile or {}
    default_cash = 1500.0 if prof.get("is_library") else 5000.0
    default_days = 21.0
    nums.setdefault("cash_ceiling", default_cash)
    nums.setdefault("days", default_days)
    cash = int(float(nums["cash_ceiling"]))
    days = int(float(nums["days"]))
    if not ans.get("constraint_cash"):
        ans["constraint_cash"] = _d(
            lang,
            f"${cash} потолок cash на пилот (signer)",
            f"${cash} pilot cash ceiling (signer)",
        )
    if not ans.get("constraint_time"):
        ans["constraint_time"] = _d(
            lang,
            f"{days} дней до first paid / kill review",
            f"{days} days to first paid / kill review",
        )
    if prof.get("payer") and not ans.get("who_pays"):
        ans["who_pays"] = prof["payer"]
    if prof.get("unit") and not ans.get("unit_of_value"):
        ans["unit_of_value"] = prof["unit"]
    if prof.get("channel") and not ans.get("first_channel"):
        ans["first_channel"] = prof["channel"]
    if prof.get("metric") and not ans.get("success_metric"):
        ans["success_metric"] = prof["metric"]
    if not ans.get("geography"):
        ans["geography"] = "online-first" if prof.get("is_online") else "tbd"
    if not ans.get("non_goals"):
        ans["non_goals"] = _d(
            lang,
            "Не auto-yield; не open retainer; не full custom product build в пилоте",
            "No auto-yield; no open retainer; no full custom product build in pilot",
        )
    return ans, nums


def filter_open_questions(
    open_questions: list[str],
    answers: dict[str, str],
    lang: str = "ru",
    *,
    profile: dict[str, Any] | None = None,
) -> list[str]:
    """Drop money-path Q already closed by signer answers/numbers."""
    closed_keys = {k for k, v in answers.items() if v}
    patterns = {
        "constraint_cash": ("бюджет", "cash", "потолок", "ceiling", "budget"),
        "constraint_time": ("окно", "дней", "days", "window", "срок", "time"),
        "who_pays": ("кто платит", "who pays", "платель"),
        "unit_of_value": ("единиц", "unit of value", "unit of"),
        "first_channel": ("канал", "channel", "касани"),
        "success_metric": ("метрик", "metric", "kpi"),
        "geography": ("географи", "geography", "город"),
        "non_goals": ("не дела", "non-goal", "out of scope"),
    }
    # Soft noise for knowledge library / pure online: assume no license wall / no critical logistics partner
    soft_skip = ()
    if (profile or {}).get("is_library") or (profile or {}).get("is_online"):
        soft_skip = (
            "лиценз",
            "эко-огранич",
            "regulatory",
            "партнёр",
            "partner",
            "цепочка падает",
        )
    out: list[str] = []
    for q in open_questions or []:
        ql = q.lower()
        skip = False
        for key, toks in patterns.items():
            if key in closed_keys and any(t in ql for t in toks):
                skip = True
                break
        if not skip and soft_skip and any(t in ql for t in soft_skip):
            skip = True
        if not skip:
            out.append(q)
    return out


# ── Deep niche architecture cards ────────────────────────────────────────────


def _architecture_cards(profile: dict[str, Any], lang: str) -> list[dict[str, str]]:
    """
    12 unique deep designs for concrete niches (not library meta-templates).
    Each card is a sellable architecture slice a builder can apply.
    """
    L = _lang(lang)
    if profile["is_library"]:
        # Deep niche designs — concrete verticals, not library meta-templates
        deep = [
            {
                "id": "A01",
                "niche": "SaaS billing",
                "title_ru": "SaaS Billing Spine",
                "title_en": "SaaS Billing Spine",
                "context_ru": "Usage+seat hybrid, dunning, kill free-tier без «вечного free».",
                "context_en": "Usage+seat hybrid, dunning, kill free-tier without eternal free.",
                "blocks_ru": "Meter → Price table → Invoice → Dunning → Churn signal → Kill free",
                "blocks_en": "Meter → Price table → Invoice → Dunning → Churn signal → Kill free",
                "boundary_ru": "Не payment gateway build; не multi-currency v0.",
                "boundary_en": "No payment-gateway build; no multi-currency in v0.",
                "failure_ru": "Free forever + no dunning → revenue illusion.",
                "failure_en": "Free forever + no dunning → revenue illusion.",
                "proof_ru": "1 price table + 1 dunning path + free-tier kill rule",
                "proof_en": "1 price table + 1 dunning path + free-tier kill rule",
            },
            {
                "id": "A02",
                "niche": "Agent ops",
                "title_ru": "Agent Ops Control Lattice",
                "title_en": "Agent Ops Control Lattice",
                "context_ru": "Multi-agent delivery: handoff, rework timer, quality floor.",
                "context_en": "Multi-agent delivery: handoff, rework timer, quality floor.",
                "blocks_ru": "Task → Owner → Handoff SLA → Quality gate → Rework timer → Esc",
                "blocks_en": "Task → Owner → Handoff SLA → Quality gate → Rework timer → Esc",
                "boundary_ru": "Не «ещё один agent chat»; только ops lattice.",
                "boundary_en": "Not another agent chat — ops lattice only.",
                "failure_ru": "Handoff без SLA → rework >30%.",
                "failure_en": "Handoff without SLA → rework >30%.",
                "proof_ru": "Rework % logged weekly + 1 kill on missed SLA",
                "proof_en": "Rework % logged weekly + 1 kill on missed SLA",
            },
            {
                "id": "A03",
                "niche": "API cost / Expert path",
                "title_ru": "API Cost · Expert Path Map",
                "title_en": "API Cost · Expert Path Map",
                "context_ru": "Горячий path жрёт tokens; нужен cheaper Expert floor.",
                "context_en": "Hot path burns tokens; need cheaper Expert quality floor.",
                "blocks_ru": "Call map → Cost/1k → Quality floor → Expert route → Cache → Kill",
                "blocks_en": "Call map → Cost/1k → Quality floor → Expert route → Cache → Kill",
                "boundary_ru": "Не rewrite всего inference stack в пилоте.",
                "boundary_en": "No full inference-stack rewrite in pilot.",
                "failure_ru": "Cost cut без quality floor → silent degradation.",
                "failure_en": "Cost cut without quality floor → silent degradation.",
                "proof_ru": "−20% token $ / path OR equal quality at lower tier",
                "proof_en": "−20% token $ / path OR equal quality at lower tier",
            },
            {
                "id": "A04",
                "niche": "Marketplace match",
                "title_ru": "Marketplace Match Geometry",
                "title_en": "Marketplace Match Geometry",
                "context_ru": "Supply cards · demand ICP · match rules · trust · settlement.",
                "context_en": "Supply cards · demand ICP · match rules · trust · settlement.",
                "blocks_ru": "Supply quality → Demand ICP → Match → Trust signal → Cash path",
                "blocks_en": "Supply quality → Demand ICP → Match → Trust signal → Cash path",
                "boundary_ru": "Trust+settlement раньше «фич маркетплейса».",
                "boundary_en": "Trust+settlement before marketplace feature bloat.",
                "failure_ru": "Match без settlement = мёртвый inventory.",
                "failure_en": "Match without settlement = dead inventory.",
                "proof_ru": "1 cash path from match → paid",
                "proof_en": "1 cash path from match → paid",
            },
            {
                "id": "A05",
                "niche": "Decision forks",
                "title_ru": "Decision Fork Engine",
                "title_en": "Decision Fork Engine",
                "context_ru": "Билдер выбирает ветку, не читает эссе. Max 3 options.",
                "context_en": "Builder picks a branch, not an essay. Max 3 options.",
                "blocks_ru": "Fork · Criteria · Kill switch · Next step · Owner",
                "blocks_en": "Fork · Criteria · Kill switch · Next step · Owner",
                "boundary_ru": "Макс. 3 option cards на шаг.",
                "boundary_en": "Max 3 option cards per step.",
                "failure_ru": "Много вариантов без kill → paralysis.",
                "failure_en": "Many options without kill → paralysis.",
                "proof_ru": "S1–S4 closed with explicit commit",
                "proof_en": "S1–S4 closed with explicit commit",
            },
            {
                "id": "A06",
                "niche": "Concept testing",
                "title_ru": "Concept Test · Calendar Kill",
                "title_en": "Concept Test · Calendar Kill",
                "context_ru": "Каждый оффер: hypothesis + metric + dates + stop/go.",
                "context_en": "Every offer: hypothesis + metric + dates + stop/go.",
                "blocks_ru": "Hypothesis · Metric · Start/Kill dates · Sample · Stop/Go",
                "blocks_en": "Hypothesis · Metric · Start/Kill dates · Sample · Stop/Go",
                "boundary_ru": "Нет даты kill = нет теста.",
                "boundary_en": "No kill date = no test.",
                "failure_ru": "«Запустим и посмотрим» без calendar.",
                "failure_en": "“Ship and see” without a calendar.",
                "proof_ru": "T1–T3 on calendar with ISO dates",
                "proof_en": "T1–T3 on calendar with ISO dates",
            },
            {
                "id": "A07",
                "niche": "Editorial production",
                "title_ru": "Editorial Desk · Ship Gate",
                "title_en": "Editorial Desk · Ship Gate",
                "context_ru": "WIP=3, assignment card, kill-the-topic, ship weekly.",
                "context_en": "WIP=3, assignment card, kill-the-topic, ship weekly.",
                "blocks_ru": "Backlog · Assignment · Deadline · Kill topic · Ship",
                "blocks_en": "Backlog · Assignment · Deadline · Kill topic · Ship",
                "boundary_ru": "WIP limit 3 active cards.",
                "boundary_en": "WIP limit 3 active cards.",
                "failure_ru": "Бесконечные драфты без ship.",
                "failure_en": "Endless drafts without ship.",
                "proof_ru": "≥3 shipped cards / week after setup",
                "proof_en": "≥3 shipped cards / week after setup",
            },
            {
                "id": "A08",
                "niche": "Unit economics",
                "title_ru": "Knowledge Pack Unit Economics",
                "title_en": "Knowledge Pack Unit Economics",
                "context_ru": "Price pack, hours COGS, target margin, break-even units.",
                "context_en": "Price pack, hours COGS, target margin, break-even units.",
                "blocks_ru": "Price · Hours · COGS · Margin · Break-even / 21d",
                "blocks_en": "Price · Hours · COGS · Margin · Break-even / 21d",
                "boundary_ru": "Без «гарантированной доходности».",
                "boundary_en": "No guaranteed yield claims.",
                "failure_ru": "Нет COGS → нет маржи.",
                "failure_en": "No COGS → no margin.",
                "proof_ru": "Break-even ≤ 3 units / 21d",
                "proof_en": "Break-even ≤ 3 units / 21d",
            },
            {
                "id": "A09",
                "niche": "Trust & settlement",
                "title_ru": "Trust · Settlement Path",
                "title_en": "Trust · Settlement Path",
                "context_ru": "Оплата и accept note раньше «социальной фичи».",
                "context_en": "Payment and accept note before social features.",
                "blocks_ru": "Offer → Accept criteria → Invoice → Pay → Ledger → Review",
                "blocks_en": "Offer → Accept criteria → Invoice → Pay → Ledger → Review",
                "boundary_ru": "Manual invoice OK in pilot.",
                "boundary_en": "Manual invoice OK in pilot.",
                "failure_ru": "Trust signals без cash path.",
                "failure_en": "Trust signals without cash path.",
                "proof_ru": "1 paid settlement recorded",
                "proof_en": "1 paid settlement recorded",
            },
            {
                "id": "A10",
                "niche": "Client pack coop",
                "title_ru": "Client Pack · Coop Handoff",
                "title_en": "Client Pack · Coop Handoff",
                "context_ru": "Похожие запросы → один pack, shared scoreboard, handoff matrix.",
                "context_en": "Similar requests → one pack, shared scoreboard, handoff matrix.",
                "blocks_ru": "Similarity → Pack slot → Handoff · Scoreboard · Capacity",
                "blocks_en": "Similarity → Pack slot → Handoff · Scoreboard · Capacity",
                "boundary_ru": "Не 8 custom TZ на каждый retainer.",
                "boundary_en": "Not 8 custom TZs per retainer.",
                "failure_ru": "Copy-paste delivery без pack geometry.",
                "failure_en": "Copy-paste delivery without pack geometry.",
                "proof_ru": "≥2 similar clients on one pack schema",
                "proof_en": "≥2 similar clients on one pack schema",
            },
            {
                "id": "A11",
                "niche": "Implementation assist",
                "title_ru": "Implementation Assistant Contour",
                "title_en": "Implementation Assistant Contour",
                "context_ru": "После approval: assistant + tester-strategist, не «только CTA».",
                "context_en": "After approval: assistant + tester-strategist — not CTA-only.",
                "blocks_ru": "Approve → Scope lock → Assist steps → Test gates → Tune → Close",
                "blocks_en": "Approve → Scope lock → Assist steps → Test gates → Tune → Close",
                "boundary_ru": "Оплата внедрения только после утверждения.",
                "boundary_en": "Implementation pay only after approval.",
                "failure_ru": "CTA без next path → drop after GO.",
                "failure_en": "CTA without next path → drop after GO.",
                "proof_ru": "Assist path with 5 executable steps + owner",
                "proof_en": "Assist path with 5 executable steps + owner",
            },
            {
                "id": "A12",
                "niche": "Distribution 7d",
                "title_ru": "Distribution · 7-Day Live Log",
                "title_en": "Distribution · 7-Day Live Log",
                "context_ru": "Не слово «network» — 10–15 касаний + 1 artifact на календаре.",
                "context_en": "Not the word “network” — 10–15 touches + 1 artifact on calendar.",
                "blocks_ru": "Day plan · Touch list · Artifact · DM path · Ledger",
                "blocks_en": "Day plan · Touch list · Artifact · DM path · Ledger",
                "boundary_ru": "1 channel only; no fixed marketing hire.",
                "boundary_en": "1 channel only; no fixed marketing hire.",
                "failure_ru": "5 каналов = 0 сигналов.",
                "failure_en": "5 channels = 0 signals.",
                "proof_ru": "7-day log executed with ≥10 touches + 1 artifact",
                "proof_en": "7-day log executed with ≥10 touches + 1 artifact",
            },
        ]
        cards = []
        for c in deep:
            cards.append(
                {
                    "id": c["id"],
                    "niche": c["niche"],
                    "title": c[f"title_{L}"],
                    "context": c[f"context_{L}"],
                    "blocks": c[f"blocks_{L}"],
                    "boundary": c[f"boundary_{L}"],
                    "failure": c[f"failure_{L}"],
                    "proof": c[f"proof_{L}"],
                }
            )
        return cards

    # Generic / agency: operational architecture set (still concrete, not empty templates)
    generic = [
        ("A01", "Intake", "Lead → qualify → commit", "Qualify gate"),
        ("A02", "Core process", "Work → gate → deliver", "Done criteria"),
        ("A03", "Quality gate", "Criteria → accept / rework", "Rework % weekly"),
        ("A04", "Offer spine", "ICP → unit → price → anti-scope", "1 price + anti-scope"),
        ("A05", "Cash loop", "Invoice → pay → ledger", "1 paid settlement"),
        ("A06", "Metric board", "One KPI · owner · weekly", "KPI owner named"),
        ("A07", "Leak map", "Where margin dies", "Top 3 leaks"),
        ("A08", "Capacity", "Who · WIP limit", "WIP ≤ 3"),
        ("A09", "Channel log", "7d touches + artifact", "≥10 touches logged"),
        ("A10", "Risk lattice", "Kill switches · hedges", "1 kill date on calendar"),
        ("A11", "Connect / DIY", "Wire vs manual", "Table with owner"),
        ("A12", "Pilot close", "Stop / Go / Rework", "Signer decision"),
    ]
    cards = []
    for cid, title, blocks, proof in generic:
        cards.append(
            {
                "id": cid,
                "niche": profile["profile"],
                "title": title,
                "context": _d(
                    lang,
                    "Операционный контур бизнеса из брифа.",
                    "Operational contour from the brief.",
                ),
                "blocks": blocks,
                "boundary": _d(lang, "Пилот 14–21 день, одна метрика.", "Pilot 14–21 days, one metric."),
                "failure": _d(lang, "Расширение scope mid-flight.", "Scope creep mid-flight."),
                "proof": proof,
            }
        )
    return cards


def _offer_cards(profile: dict[str, Any], lang: str) -> list[dict[str, str]]:
    L = _lang(lang)
    if profile["is_library"]:
        return [
            {
                "id": "O1",
                "name": "Niche Architecture Pack",
                "who_pays": _d(L, "Билдер / lead product / small studio", "Builder / product lead / small studio"),
                "unit": _d(
                    L,
                    "1 niche pack (12 deep cards + 1 concept test)",
                    "1 niche pack (12 deep cards + 1 concept test)",
                ),
                "price_anchor": "$190–390 (entry) · Core track $790 when full panel+plan",
                "anti_scope": _d(
                    L,
                    "Не custom dev; не agency retainer; не auto-yield",
                    "No custom dev; no agency retainer; no auto-yield",
                ),
                "why_now": _d(
                    L,
                    "Билдерам нужна геометрия решений, не мотивационный шум",
                    "Builders need decision geometry, not motivational noise",
                ),
            },
            {
                "id": "O2",
                "name": "Design Review Order",
                "who_pays": _d(L, "Команда с уже выбранной нишей", "Team with niche already chosen"),
                "unit": _d(
                    L,
                    "1 оплаченный review-заказ (TZ + kill criteria)",
                    "1 paid review order (TZ + kill criteria)",
                ),
                "price_anchor": "$290–490",
                "anti_scope": _d(
                    L,
                    "Не weekly coaching без артефакта",
                    "No weekly coaching without an artifact",
                ),
                "why_now": _d(
                    L,
                    "Быстрый unit cash path до подписки",
                    "Fast unit cash path before any subscription",
                ),
            },
            {
                "id": "O3",
                "name": "Core Growth/Yield setup",
                "who_pays": _d(
                    L,
                    "Основатель, которому нужна панель + план 21d",
                    "Founder who needs panel + 21d plan",
                ),
                "unit": "Identity + deep cards + connect/DIY + pilot metric + assist path",
                "price_anchor": f"${CORE_PRICE_USD} one-time pilot track",
                "anti_scope": _d(
                    L,
                    "Оплата внедрения — только после утверждения",
                    "Implementation pay — only after approval",
                ),
                "why_now": _d(
                    L,
                    "Закрывает разрыв explore-JSON → рабочее ядро",
                    "Closes explore-JSON → working core gap",
                ),
            },
        ]
    return [
        {
            "id": "O1",
            "name": "Paid Pilot 14–21d",
            "who_pays": profile["payer"],
            "unit": profile["unit"],
            "price_anchor": f"Core ${CORE_PRICE_USD}",
            "anti_scope": "No open-ended scope",
            "why_now": "One metric, one channel, calendar kill",
        }
    ]


def _niche_cards(profile: dict[str, Any], orch: dict[str, Any], lang: str) -> list[dict[str, str]]:
    ranking = (orch or {}).get("niche_ranking") or []
    top = ranking[:3] if ranking else [
        {"id": "automation-builders", "label": "Builders / automation", "score": 0.7},
        {"id": "expert-services", "label": "Expert / knowledge packs", "score": 0.55},
        {"id": "content-monetize", "label": "Content / knowledge", "score": 0.5},
    ]
    out = []
    for i, r in enumerate(top, 1):
        label = r.get("label") or r.get("id")
        out.append(
            {
                "id": f"N{i}",
                "niche": str(label),
                "score": f"{int(float(r.get('score') or 0) * 100)}%",
                "pain": _d(
                    lang,
                    "Нет готовой deep-архитектуры → reinvent / GPT-шум"
                    if profile["is_library"]
                    else "Операционный friction в delivery / unit",
                    "No ready deep architecture → reinvent / GPT noise"
                    if profile["is_library"]
                    else "Ops friction in delivery / unit",
                ),
                "icp": _d(
                    lang,
                    "Indie / studio builders IT-продуктов"
                    if profile["is_library"]
                    else "Владелец / ops lead",
                    "Indie / studio IT product builders"
                    if profile["is_library"]
                    else "Owner / ops lead",
                ),
                "touch_7d": profile["channel"],
                "first_test": profile["metric"],
            }
        )
    return out


def _decision_cards(profile: dict[str, Any], plan: dict[str, Any], lang: str) -> list[dict[str, str]]:
    steps = (plan or {}).get("steps") or []
    defaults = {
        "S1_direction": profile["direction"],
        "S2_unit": profile["unit_id"],
        "S3_channel": profile["channel_id"],
        "S4_metric": profile["metric_id"],
    }
    labels = {
        "S1_direction": (_d(lang, "Направление", "Direction"), profile["direction"]),
        "S2_unit": (_d(lang, "Единица ценности", "Unit of value"), profile["unit"]),
        "S3_channel": (_d(lang, "Первый канал", "First channel"), profile["channel"]),
        "S4_metric": (_d(lang, "Метрика пилота", "Pilot metric"), profile["metric"]),
    }
    cards = []
    for sid, (title, resolved) in labels.items():
        step = next((s for s in steps if s.get("id") == sid), {})
        chosen = step.get("default_option") or defaults.get(sid, "—")
        cards.append(
            {
                "id": sid,
                "title": title,
                "chosen": str(chosen),
                "resolved_as": resolved,
                "kill": "",  # global stop-rule once in analytical resume — not per decision
                "next": _d(
                    lang,
                    "Зафиксировать выбор и не расширять scope",
                    "Lock the choice and do not expand scope",
                ),
            }
        )
    return cards


# ── Calendar kill tests ───────────────────────────────────────────────────────


def _concept_tests(
    profile: dict[str, Any],
    lang: str,
    *,
    start: date | None = None,
    days_window: int = 21,
) -> list[dict[str, str]]:
    start = start or date.today()
    d21 = start + timedelta(days=min(days_window, 21))
    d14 = start + timedelta(days=14)
    d7 = start + timedelta(days=7)

    if profile["is_library"]:
        raw = [
            {
                "id": "T1",
                "hypothesis_ru": "Если отдать 1 niche pack (12 deep cards) тёплым билдерам, ≥1 оплатит unit за 21 день",
                "hypothesis_en": "If 1 niche pack (12 deep cards) goes to warm builders, ≥1 pays a unit in 21 days",
                "metric": "Paid units · target ≥1",
                "start_date": start.isoformat(),
                "kill_date": d21.isoformat(),
                "go_date": d21.isoformat(),
                "window_days": str(days_window),
                "sample_ru": "12–15 касаний / 5 deep reviews",
                "sample_en": "12–15 touches / 5 deep reviews",
                "stop_ru": "0 paid + drop-off >40% на карточке оффера",
                "stop_en": "0 paid + drop-off >40% on offer card",
                "go_ru": "≥1 paid → client_pack из похожих запросов",
                "go_en": "≥1 paid → client_pack from similar requests",
            },
            {
                "id": "T2",
                "hypothesis_ru": "Editorial desk (WIP=3) даёт ≥3 shipped cards / неделя",
                "hypothesis_en": "Editorial desk (WIP=3) yields ≥3 shipped cards / week",
                "metric": "Shipped cards / week",
                "start_date": start.isoformat(),
                "kill_date": d14.isoformat(),
                "go_date": d14.isoformat(),
                "window_days": "14",
                "sample_ru": "1 founder production loop",
                "sample_en": "1 founder production loop",
                "stop_ru": "<1 ship / week 2 недели подряд",
                "stop_en": "<1 ship / week for 2 weeks straight",
                "go_ru": "Стабильно ≥3 → открыть 2-ю deep-нишу",
                "go_en": "Stable ≥3 → open 2nd deep niche",
            },
            {
                "id": "T3",
                "hypothesis_ru": "Чистый отчёт + CSV/PDF deliverable снижает drop-off next step <25%",
                "hypothesis_en": "Clean report + CSV/PDF deliverable keeps next-step drop-off <25%",
                "metric": "Completion rate next step",
                "start_date": start.isoformat(),
                "kill_date": d14.isoformat(),
                "go_date": d7.isoformat(),
                "window_days": "14",
                "sample_ru": "Все generate sessions",
                "sample_en": "All generate sessions",
                "stop_ru": "Drop-off ≥40%",
                "stop_en": "Drop-off ≥40%",
                "go_ru": "UI primary = markdown Core + file exports",
                "go_en": "UI primary = markdown Core + file exports",
            },
        ]
    else:
        raw = [
            {
                "id": "T1",
                "hypothesis_ru": "Один канал + одна метрика → paid path за 21 день",
                "hypothesis_en": "One channel + one metric → paid path in 21 days",
                "metric": profile["metric"],
                "start_date": start.isoformat(),
                "kill_date": d21.isoformat(),
                "go_date": d21.isoformat(),
                "window_days": str(days_window),
                "sample_ru": "Пилот-контур",
                "sample_en": "Pilot contour",
                "stop_ru": "Нет движения метрики к day 14",
                "stop_en": "No metric movement by day 14",
                "go_ru": "Утвердить внедрение / next package",
                "go_en": "Approve implementation / next package",
            }
        ]

    L = _lang(lang)
    out = []
    for t in raw:
        out.append(
            {
                "id": t["id"],
                "hypothesis": t[f"hypothesis_{L}"],
                "metric": t["metric"],
                "start_date": t["start_date"],
                "kill_date": t["kill_date"],
                "go_date": t["go_date"],
                "window": f"{t['window_days']}d · kill {t['kill_date']}",
                "window_days": t["window_days"],
                "sample": t[f"sample_{L}"],
                "stop": t[f"stop_{L}"],
                "go": t[f"go_{L}"],
            }
        )
    return out


# ── Live 7-day channel log ────────────────────────────────────────────────────


def _channel_log_7d(profile: dict[str, Any], lang: str, *, start: date | None = None) -> dict[str, Any]:
    """Concrete 10–15 touches + 1 artifact — not the word 'network'."""
    start = start or date.today()
    L = _lang(lang)
    if profile["is_library"]:
        touches_plan = [
            (0, "DM#1–2", "2 warm builders (ex-colleagues / community)"),
            (1, "DM#3–5", "3 product leads from builder lists"),
            (2, "DM#6–8", "3 studio founders with similar stack"),
            (3, "Artifact", "Ship 1 public proof: sample A01 card + kill criterion"),
            (3, "DM#9–10", "2 follow-ups linking artifact"),
            (4, "DM#11–12", "2 deep review invites (15-min)"),
            (5, "DM#13–14", "2 offers: Niche Pack entry price"),
            (6, "DM#15", "1 close / schedule review · ledger update"),
        ]
        artifact = {
            "name": _d(L, "Proof-карточка A01 SaaS Billing Spine", "Proof card A01 SaaS Billing Spine"),
            "format": "1-page PDF/MD + screenshot",
            "ship_day": (start + timedelta(days=3)).isoformat(),
            "channel": "X / Telegram / LinkedIn (one surface only)",
        }
    else:
        touches_plan = [
            (0, "Touch#1–2", "2 warm intros"),
            (1, "Touch#3–5", "3 outbound / referrals"),
            (2, "Touch#6–8", "3 follow-ups"),
            (3, "Artifact", "Ship 1 proof artifact"),
            (4, "Touch#9–11", "3 deep conversations"),
            (5, "Touch#12–13", "2 offers"),
            (6, "Touch#14–15", "2 closes / ledger"),
        ]
        artifact = {
            "name": _d(L, "1 proof artifact (offer one-pager)", "1 proof artifact (offer one-pager)"),
            "format": "1-page MD/PDF",
            "ship_day": (start + timedelta(days=3)).isoformat(),
            "channel": "Primary channel only",
        }

    days = []
    touch_n = 0
    for offset, label, detail in touches_plan:
        d = start + timedelta(days=offset)
        # count numeric touches roughly
        if "Artifact" not in label:
            # extract range if present
            touch_n += 2 if "–" in label or "-" in label else 1
        days.append(
            {
                "day": d.isoformat(),
                "day_offset": offset,
                "label": label,
                "action": detail,
                "owner": "Founder",
                "done": False,
                "note": "",
            }
        )
    # Normalize claimed touches to 12–15 band
    touch_target = 14 if profile["is_library"] else 12
    return {
        "title": _d(L, "Живой 7-day channel log", "Live 7-day channel log"),
        "channel_name": profile["channel"],
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=6)).isoformat(),
        "touch_target": touch_target,
        "touch_planned": max(touch_n, touch_target),
        "artifact": artifact,
        "days": days,
        "ledger_fields": ["date", "who", "channel", "response", "next", "paid?"],
        "rule": _d(
            L,
            "Не писать «network» — только строки лога + 1 artifact link.",
            "Do not write “network” — only log rows + 1 artifact link.",
        ),
    }


def _unit_economics(profile: dict[str, Any], numbers: dict[str, float] | None = None) -> dict[str, Any]:
    nums = numbers or {}
    cash = float(nums.get("cash_ceiling", 1500 if profile["is_library"] else 2000))
    if profile["is_library"]:
        return {
            "unit_name": "Niche Architecture Pack / Design Review",
            "price_anchor_usd": 290,
            "core_track_usd": CORE_PRICE_USD,
            "hours_per_unit": 6,
            "internal_rate_usd": 45,
            "cogs_usd": 270,
            "target_margin_pct": 55,
            "note": (
                "At pack $290 and 6h @$45 COGS is tight — price $490+ or template leverage <3h. "
                f"Core ${CORE_PRICE_USD} = setup+panel+plan, not one card. Cash ceiling ${int(cash)}."
            ),
            "break_even_units_21d": 2,
            "cash_ceiling_pilot_usd": int(cash),
        }
    return {
        "unit_name": profile["unit"],
        "price_anchor_usd": CORE_PRICE_USD,
        "core_track_usd": CORE_PRICE_USD,
        "hours_per_unit": 12,
        "internal_rate_usd": 50,
        "cogs_usd": 600,
        "target_margin_pct": 45,
        "note": "Unit economics skeleton — lock with client numbers.",
        "break_even_units_21d": 1,
        "cash_ceiling_pilot_usd": int(cash),
    }


def _connect_diy(profile: dict[str, Any], lang: str) -> list[dict[str, str]]:
    return [
        {
            "layer": "Control panel",
            "connect": "Metrix Sense/Decide/Act + Core report",
            "diy": _d(lang, "Notion board с теми же 3 колонками", "Notion board with the same 3 columns"),
            "day": "1–2",
        },
        {
            "layer": "Card catalog",
            "connect": "expert_base + architecture cards export CSV",
            "diy": "Git/Notion DB schema A01–A12",
            "day": "2–5",
        },
        {
            "layer": "Scoreboard",
            "connect": "diy_табло / simple ledger",
            "diy": "Sheet: unit · hours · margin · kill",
            "day": "3–7",
        },
        {
            "layer": "Channel log",
            "connect": "distribution surface (1 channel)",
            "diy": _d(lang, "Warm DM list 15 + 1 proof artifact", "Warm DM list 15 + 1 proof artifact"),
            "day": "1–7",
        },
        {
            "layer": "Integrations",
            "connect": _d(lang, "Только если CRM/pay already", "Only if CRM/pay already"),
            "diy": "Manual invoice + accept note",
            "day": "7–14",
        },
    ]


def _pilot_plan_21d(profile: dict[str, Any], lang: str, *, start: date | None = None) -> list[dict[str, str]]:
    start = start or date.today()

    def band(a: int, b: int) -> str:
        return f"{(start + timedelta(days=a)).isoformat()} → {(start + timedelta(days=b)).isoformat()}"

    return [
        {
            "days": "0–2",
            "dates": band(0, 2),
            "focus": _d(lang, "Identity + schema + commit S1–S4", "Identity + schema + commit S1–S4"),
            "owner": "Founder",
            "exit": _d(lang, "Схема + 4 решения записаны", "Schema + 4 decisions locked"),
        },
        {
            "days": "3–7",
            "dates": band(3, 7),
            "focus": _d(
                lang,
                "12 deep arch cards + 3 offers + 1 niche pack + channel log start",
                "12 deep arch cards + 3 offers + 1 niche pack + channel log start",
            ),
            "owner": "Founder / editor",
            "exit": "Pack v0 shippable",
        },
        {
            "days": "7–10",
            "dates": band(7, 10),
            "focus": _d(
                lang,
                "7-day channel log: 12–15 touches + 1 artifact",
                "7-day channel log: 12–15 touches + 1 artifact",
            ),
            "owner": "Founder",
            "exit": _d(lang, "≥3 deep conversations", "≥3 deep conversations"),
        },
        {
            "days": "11–18",
            "dates": band(11, 18),
            "focus": _d(lang, "Concept test T1: paid unit path", "Concept test T1: paid unit path"),
            "owner": "Founder",
            "exit": _d(lang, "Paid или kill reason", "Paid or kill reason"),
        },
        {
            "days": "19–21",
            "dates": band(19, 21),
            "focus": _d(
                lang,
                f"Stop/Go: Core ${CORE_PRICE_USD} implementation approval or rework",
                f"Stop/Go: Core ${CORE_PRICE_USD} implementation approval or rework",
            ),
            "owner": "Signer",
            "exit": _d(lang, "Решение + notes → assist path", "Decision + notes → assist path"),
        },
    ]


# ── Implementation assistant path (after approval) ────────────────────────────


def _implementation_assistant_path(
    profile: dict[str, Any],
    lang: str,
    *,
    start: date | None = None,
) -> dict[str, Any]:
    start = start or date.today()
    L = _lang(lang)
    steps = [
        {
            "id": "IA1",
            "day": (start + timedelta(days=0)).isoformat(),
            "title_ru": "Scope lock после approval",
            "title_en": "Scope lock after approval",
            "action_ru": "Зафиксировать S1–S4, cash ceiling, anti-scope; подписать accept note.",
            "action_en": "Lock S1–S4, cash ceiling, anti-scope; sign accept note.",
            "owner": "Signer + Metrix assist",
            "exit_ru": "Scope PDF/MD accepted",
            "exit_en": "Scope PDF/MD accepted",
        },
        {
            "id": "IA2",
            "day": (start + timedelta(days=1)).isoformat(),
            "title_ru": "Assist: desk + schema",
            "title_en": "Assist: desk + schema",
            "action_ru": "Поднятие editorial desk WIP=3 и schema A01–A12 в Notion/Git.",
            "action_en": "Stand up editorial desk WIP=3 and A01–A12 schema in Notion/Git.",
            "owner": "Implementation assistant",
            "exit_ru": "Board live + first 3 cards assigned",
            "exit_en": "Board live + first 3 cards assigned",
        },
        {
            "id": "IA3",
            "day": (start + timedelta(days=3)).isoformat(),
            "title_ru": "Tester-strategist: T1 gate",
            "title_en": "Tester-strategist: T1 gate",
            "action_ru": "Прогон hypothesis T1, проверка calendar kill, sample touches.",
            "action_en": "Run T1 hypothesis, verify calendar kill, sample touches.",
            "owner": "Tester-strategist",
            "exit_ru": "T1 status green/amber/red",
            "exit_en": "T1 status green/amber/red",
        },
        {
            "id": "IA4",
            "day": (start + timedelta(days=7)).isoformat(),
            "title_ru": "Channel log mid-check",
            "title_en": "Channel log mid-check",
            "action_ru": "Аудит 7-day log: ≥10 касаний + artifact shipped?",
            "action_en": "Audit 7-day log: ≥10 touches + artifact shipped?",
            "owner": "Implementation assistant",
            "exit_ru": "Log complete or kill channel",
            "exit_en": "Log complete or kill channel",
        },
        {
            "id": "IA5",
            "day": (start + timedelta(days=14)).isoformat(),
            "title_ru": "Final client tune",
            "title_en": "Final client tune",
            "action_ru": "Под клиента: pack pricing, niche #2 decision, stop/go Core close.",
            "action_en": "Per client: pack pricing, niche #2 decision, stop/go Core close.",
            "owner": "Signer + assist",
            "exit_ru": "Tune notes + next package or hold",
            "exit_en": "Tune notes + next package or hold",
        },
    ]
    path = []
    for s in steps:
        path.append(
            {
                "id": s["id"],
                "day": s["day"],
                "title": s[f"title_{L}"],
                "action": s[f"action_{L}"],
                "owner": s["owner"],
                "exit": s[f"exit_{L}"],
            }
        )
    return {
        "trigger": "implementation_approval",
        "pay_model": "optional_on_implementation_approval",
        "status": "ready_after_approve",
        "summary": _d(
            L,
            "После GO: 5 шагов assistant + tester-strategist (не CTA-only).",
            "After GO: 5 assistant + tester-strategist steps (not CTA-only).",
        ),
        "steps": path,
        "cta_after": _d(
            L,
            f"Утвердить внедрение Ядра (${CORE_PRICE_USD}) → открыть assist path",
            f"Approve Core implementation (${CORE_PRICE_USD}) → open assist path",
        ),
    }


def _value_assessment(
    profile: dict[str, Any],
    quality: dict[str, Any],
    cards_count: int,
    closed_money_path: bool,
    *,
    has_channel_log: bool = False,
    has_calendar: bool = False,
    has_exports: bool = False,
    has_assist: bool = False,
    lang: str = "ru",
) -> dict[str, Any]:
    conf = float((quality or {}).get("confidence") or 0.33)
    anti = float((quality or {}).get("anti_template_score") or 0.6)
    commit = bool((quality or {}).get("commit_ready"))
    base = 240
    base += min(200, cards_count * 8)
    base += int(anti * 80)
    base += int(conf * 140)
    if closed_money_path:
        base += 70
    if commit:
        base += 50
    if profile["is_library"]:
        base += 30
    if has_channel_log:
        base += 40
    if has_calendar:
        base += 30
    if has_exports:
        base += 25
    if has_assist:
        base += 35
    auto_cap = int(CORE_PRICE_USD * 0.88)
    realized = int(max(200, min(auto_cap, base)))
    gap = max(0, CORE_PRICE_USD - realized)
    gap_pct = round(gap / CORE_PRICE_USD * 100)
    if realized >= int(CORE_PRICE_USD * 0.72):
        band = "near_core"
        verdict = _d(
            lang,
            "Сильный productized Core-draft. До полных $790: живой channel log execution + approval внедрения",
            "Strong productized Core-draft. To full $790: live channel log execution + implementation approval",
        )
    elif realized >= int(CORE_PRICE_USD * 0.5):
        band = "orientation_plus"
        verdict = _d(
            lang,
            "Orientation + deep cards; до $790 не хватает money-path proof",
            "Orientation + deep cards; money-path proof still missing for $790",
        )
    else:
        band = "explore_draft"
        verdict = _d(
            lang,
            "Explore-черновик; как товар $790 ещё рано",
            "Explore draft; too early as a $790 product",
        )
    return {
        "tariff": _d(lang, "Core / Ядро", "Core"),
        "tariff_price_usd": CORE_PRICE_USD,
        "realized_value_usd_low": max(180, realized - 70),
        "realized_value_usd_high": min(CORE_PRICE_USD - 40, realized + 50),
        "realized_mid_usd": realized,
        "gap_usd": gap,
        "gap_pct": gap_pct,
        "band": band,
        "verdict": verdict,
        "what_closes_gap": [
            _d(lang, "Подтвердить who_pays + budget ceiling числами (answers)", "Confirm who_pays + budget ceiling as numbers (answers)"),
            _d(lang, "1 реальный 7-day channel log (не «network» словом)", "1 real 7-day channel log (not the word “network”)"),
            _d(lang, "≥1 concept test с kill на календаре", "≥1 concept test with kill on calendar"),
            _d(lang, "Утвердить внедрение → implementation assistant path", "Approve implementation → implementation assistant path"),
        ],
        "honesty_note": _d(
            lang,
            "Оценка — deliverable artifact, не гарантия revenue. Auto-pack capped below $790 until human proof.",
            "Valuation is a deliverable artifact, not a revenue guarantee. Auto-pack capped below $790 until human proof.",
        ),
    }


def _recommended_choices(profile: dict[str, Any]) -> dict[str, str]:
    return {
        "S1_direction": profile["direction"],
        "S2_unit": profile["unit_id"],
        "S3_channel": profile["channel_id"],
        "S4_metric": profile.get("metric_id") or "m_margin",
        "S5_assembly": "auto",
        "S6_verify": "selftest",
    }


def _inferred_answers(profile: dict[str, Any], answers: dict[str, str], numbers: dict[str, float], lang: str) -> dict[str, str]:
    merged = {
        "who_pays": answers.get("who_pays") or profile["payer"],
        "unit_of_value": answers.get("unit_of_value") or profile["unit"],
        "first_channel": answers.get("first_channel") or profile["channel"],
        "success_metric": answers.get("success_metric") or profile["metric"],
        "constraint_cash": answers.get("constraint_cash")
        or f"${int(numbers.get('cash_ceiling', 1500))} pilot ceiling",
        "constraint_time": answers.get("constraint_time")
        or f"{int(numbers.get('days', 21))} days",
        "geography": answers.get("geography") or ("online-first" if profile["is_online"] else "tbd"),
        "non_goals": answers.get("non_goals")
        or _d(
            lang,
            "Не auto-yield; не open retainer; не custom full product build в пилоте",
            "No auto-yield; no open retainer; no full custom product build in pilot",
        ),
    }
    return merged


# ── File exports ──────────────────────────────────────────────────────────────


def export_cards_csv(
    arch: list[dict[str, str]],
    offers: list[dict[str, str]],
    tests: list[dict[str, str]],
) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "type",
            "id",
            "niche",
            "title",
            "context",
            "blocks",
            "boundary",
            "failure",
            "proof",
            "start_date",
            "kill_date",
            "metric",
        ]
    )
    for c in arch:
        w.writerow(
            [
                "architecture",
                c.get("id"),
                c.get("niche", ""),
                c.get("title"),
                c.get("context"),
                c.get("blocks"),
                c.get("boundary"),
                c.get("failure"),
                c.get("proof"),
                "",
                "",
                "",
            ]
        )
    for o in offers:
        w.writerow(
            [
                "offer",
                o.get("id"),
                "",
                o.get("name"),
                o.get("why_now"),
                o.get("unit"),
                o.get("anti_scope"),
                "",
                o.get("price_anchor"),
                "",
                "",
                "",
            ]
        )
    for t in tests:
        w.writerow(
            [
                "concept_test",
                t.get("id"),
                "",
                t.get("hypothesis"),
                t.get("stop"),
                t.get("go"),
                "",
                "",
                t.get("sample"),
                t.get("start_date"),
                t.get("kill_date"),
                t.get("metric"),
            ]
        )
    return buf.getvalue()


def export_print_html(
    *,
    title: str,
    markdown: str,
    lang: str,
) -> str:
    """Print-ready HTML (browser → Save as PDF). No external deps."""
    safe_title = (title or "Metrix Core").replace("<", "")
    # Escape minimal HTML in markdown body
    body = (
        (markdown or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    # crude markdown headings → keep as pre for fidelity
    return f"""<!DOCTYPE html>
<html lang="{_lang(lang)}">
<head>
<meta charset="utf-8"/>
<title>{safe_title} · Metrix Core</title>
<style>
  body {{ font-family: ui-sans-serif, system-ui, sans-serif; max-width: 820px; margin: 2rem auto; color: #0f172a; line-height: 1.45; }}
  h1 {{ font-size: 1.4rem; }}
  pre {{ white-space: pre-wrap; font-family: inherit; font-size: 0.92rem; }}
  .meta {{ color: #64748b; font-size: 0.85rem; margin-bottom: 1.5rem; }}
  @media print {{ body {{ margin: 0.8cm; }} }}
</style>
</head>
<body>
  <p class="meta">Metrix AI · Core deliverable · {_d(lang, "печать → PDF", "print → PDF")} · {date.today().isoformat()}</p>
  <h1>{safe_title}</h1>
  <pre>{body}</pre>
</body>
</html>
"""


# ── Markdown builders (RU + EN parity) ────────────────────────────────────────


def build_markdown(
    *,
    project_name: str,
    profile: dict[str, Any],
    identity: str,
    arch: list[dict[str, str]],
    offers: list[dict[str, str]],
    niches: list[dict[str, str]],
    decisions: list[dict[str, str]],
    tests: list[dict[str, str]],
    unit_econ: dict[str, Any],
    connect: list[dict[str, str]],
    pilot: list[dict[str, str]],
    value: dict[str, Any],
    moves: list[str],
    forecast_summary: str,
    open_questions: list[str],
    gate: dict[str, Any],
    quality: dict[str, Any],
    channel_log: dict[str, Any],
    assist: dict[str, Any],
    answers: dict[str, str],
    lang: str,
) -> str:
    L = _lang(lang)
    title = project_name or profile["title_hint"]
    lines: list[str] = []

    if L == "en":
        lines.append(f"# Core: {title}")
        lines.append("")
        lines.append("## 1. Identity")
        lines.append(identity)
        lines.append("")
        lines.append(
            f"**Profile:** {profile['profile']} · **Channel mode:** "
            f"{'online' if profile['is_online'] else 'hybrid'} · **Payer (v0):** {profile['payer']}"
        )
        lines.append("")
        lines.append("## 2. Unit of value & metric")
        lines.append(f"- **Unit:** {profile['unit']}")
        lines.append(f"- **Pilot metric:** {profile['metric']}")
        lines.append(f"- **First channel (7 days):** {profile['channel']}")
        lines.append(f"- **Cash ceiling:** {answers.get('constraint_cash', '—')}")
        lines.append(f"- **Time window:** {answers.get('constraint_time', '—')}")
        lines.append("- **Out of scope:** auto-yield, open retainer, 5 channels at once")
        lines.append("")
        lines.append("## 3. Deep architecture cards (niche designs)")
        for c in arch:
            lines.append(f"### {c['id']} · {c['title']} · _{c.get('niche', '')}_")
            lines.append(f"- Context: {c['context']}")
            lines.append(f"- Blocks: {c['blocks']}")
            lines.append(f"- Boundaries: {c['boundary']}")
            lines.append(f"- Failure: {c['failure']}")
            lines.append(f"- Proof: {c['proof']}")
            lines.append("")
        lines.append("## 4. Offers")
        for o in offers:
            lines.append(f"### {o['id']} · {o['name']}")
            lines.append(f"- Who pays: {o['who_pays']}")
            lines.append(f"- Unit: {o['unit']}")
            lines.append(f"- Price anchor: {o['price_anchor']}")
            lines.append(f"- Anti-scope: {o['anti_scope']}")
            lines.append(f"- Why now: {o['why_now']}")
            lines.append("")
        lines.append("## 5. Niches (top)")
        for n in niches:
            lines.append(
                f"- **{n['id']} {n['niche']}** ({n['score']}) — pain: {n['pain']}; "
                f"ICP: {n['icp']}; touch: {n['touch_7d']}"
            )
        lines.append("")
        lines.append("## 6. Path decisions (S1–S4)")
        for d in decisions:
            lines.append(
                f"- **{d['id']} {d['title']}** → `{d['chosen']}` · {d['resolved_as']} · kill: {d['kill']}"
            )
        lines.append("")
        lines.append("## 7. Concept tests (calendar kill)")
        for t in tests:
            lines.append(f"### {t['id']}")
            lines.append(f"- Hypothesis: {t['hypothesis']}")
            lines.append(f"- Metric: {t['metric']}")
            lines.append(
                f"- **Calendar:** start `{t.get('start_date')}` · kill `{t.get('kill_date')}` · go `{t.get('go_date')}`"
            )
            lines.append(f"- Window: {t['window']}")
            lines.append(f"- Stop: {t['stop']}")
            lines.append(f"- Go: {t['go']}")
            lines.append("")
        lines.append("## 8. Live 7-day channel log")
        lines.append(f"- **Channel:** {channel_log.get('channel_name')}")
        lines.append(
            f"- **Window:** {channel_log.get('start_date')} → {channel_log.get('end_date')} · "
            f"touches target **{channel_log.get('touch_target')}**"
        )
        art = channel_log.get("artifact") or {}
        lines.append(
            f"- **Artifact (1):** {art.get('name')} · ship `{art.get('ship_day')}` · {art.get('format')}"
        )
        lines.append(f"- Rule: {channel_log.get('rule')}")
        for day in channel_log.get("days") or []:
            lines.append(
                f"  - `{day['day']}` · {day['label']}: {day['action']} · owner {day['owner']}"
            )
        lines.append("")
        lines.append("## 9. Unit economics (skeleton)")
        lines.append(f"- Unit: {unit_econ.get('unit_name')}")
        lines.append(f"- Price anchor: ${unit_econ.get('price_anchor_usd')}")
        lines.append(f"- Core track: ${unit_econ.get('core_track_usd')}")
        lines.append(
            f"- COGS ≈ ${unit_econ.get('cogs_usd')} ({unit_econ.get('hours_per_unit')}h × "
            f"${unit_econ.get('internal_rate_usd')})"
        )
        lines.append(f"- Target margin: {unit_econ.get('target_margin_pct')}%")
        lines.append(f"- Break-even units / 21d: {unit_econ.get('break_even_units_21d')}")
        lines.append(f"- Cash ceiling: ${unit_econ.get('cash_ceiling_pilot_usd')}")
        lines.append(f"- Note: {unit_econ.get('note')}")
        lines.append("")
        lines.append("## 10. Connect vs DIY")
        for row in connect:
            lines.append(
                f"- **{row['layer']}** (d{row['day']}): connect → {row['connect']}; DIY → {row['diy']}"
            )
        lines.append("")
        lines.append("## 11. 21-day plan (dated)")
        for p in pilot:
            lines.append(
                f"- **{p['days']}** `{p.get('dates', '')}` · {p['focus']} · owner: {p['owner']} · exit: {p['exit']}"
            )
        lines.append("")
        lines.append("## 12. Implementation assistant (after approval)")
        lines.append(f"- {assist.get('summary')}")
        lines.append(f"- Pay model: `{assist.get('pay_model')}`")
        for s in assist.get("steps") or []:
            lines.append(
                f"  - **{s['id']}** `{s['day']}` · {s['title']}: {s['action']} → {s['exit']}"
            )
        lines.append(f"- CTA: {assist.get('cta_after')}")
        lines.append("")
        lines.append("## 13. Original moves")
        for m in (moves or [])[:6]:
            lines.append(f"- {m}")
        lines.append("")
        lines.append("## 14. Implementation forecast")
        lines.append(forecast_summary or "—")
        lines.append("")
        lines.append(f"## 15. Value vs Core tariff (${CORE_PRICE_USD})")
        lines.append(
            f"- Realized now: **${value['realized_value_usd_low']}–${value['realized_value_usd_high']}** "
            f"(mid ~${value['realized_mid_usd']})"
        )
        lines.append(f"- Gap to ${CORE_PRICE_USD}: **${value['gap_usd']}** (~{value['gap_pct']}%) · band `{value['band']}`")
        lines.append(f"- Verdict: {value['verdict']}")
        lines.append("- What closes the gap:")
        for w in value["what_closes_gap"]:
            lines.append(f"  - {w}")
        lines.append("")
        lines.append("## 16. Open questions / sign-offs")
        if open_questions:
            for q in open_questions:
                lines.append(f"- {q}")
        else:
            lines.append("- Critical money-path slots closed by signer numbers (confirm).")
        lines.append("")
        conf = (quality or {}).get("confidence")
        lines.append("## 17. Gate")
        lines.append(
            f"- Verdict: {gate.get('verdict', '—')} · confidence: {conf} · "
            f"commit_ready: {(quality or {}).get('commit_ready')}"
        )
        lines.append(
            f"- CTA: when band near_core / orientation_plus — **approve Core implementation (${CORE_PRICE_USD})** "
            "→ open implementation assistant path."
        )
        lines.append("")
        lines.append("---")
        lines.append(
            "Implementation payment is optional and only after approval. "
            "Structure and risk without auto-yield promises."
        )
    else:
        lines.append(f"# Ядро: {title}")
        lines.append("")
        lines.append("## 1. Идентичность")
        lines.append(identity)
        lines.append("")
        lines.append(
            f"**Профиль:** {profile['profile']} · **Канал:** "
            f"{'онлайн' if profile['is_online'] else 'гибрид'} · **Плательщик (v0):** {profile['payer']}"
        )
        lines.append("")
        lines.append("## 2. Единица ценности и метрика")
        lines.append(f"- **Unit:** {profile['unit']}")
        lines.append(f"- **Метрика пилота:** {profile['metric']}")
        lines.append(f"- **Первый канал (7 дней):** {profile['channel']}")
        lines.append(f"- **Cash ceiling:** {answers.get('constraint_cash', '—')}")
        lines.append(f"- **Окно дней:** {answers.get('constraint_time', '—')}")
        lines.append("- **Не делаем:** auto-yield, open retainer, 5 каналов сразу")
        lines.append("")
        lines.append("## 3. Архитектурные карточки (deep niche designs)")
        for c in arch:
            lines.append(f"### {c['id']} · {c['title']} · _{c.get('niche', '')}_")
            lines.append(f"- Контекст: {c['context']}")
            lines.append(f"- Блоки: {c['blocks']}")
            lines.append(f"- Границы: {c['boundary']}")
            lines.append(f"- Failure: {c['failure']}")
            lines.append(f"- Proof: {c['proof']}")
            lines.append("")
        lines.append("## 4. Офферы")
        for o in offers:
            lines.append(f"### {o['id']} · {o['name']}")
            lines.append(f"- Кто платит: {o['who_pays']}")
            lines.append(f"- Unit: {o['unit']}")
            lines.append(f"- Якорь цены: {o['price_anchor']}")
            lines.append(f"- Anti-scope: {o['anti_scope']}")
            lines.append(f"- Why now: {o['why_now']}")
            lines.append("")
        lines.append("## 5. Ниши (top)")
        for n in niches:
            lines.append(
                f"- **{n['id']} {n['niche']}** ({n['score']}) — pain: {n['pain']}; "
                f"ICP: {n['icp']}; touch: {n['touch_7d']}"
            )
        lines.append("")
        lines.append("## 6. Решения на пути (S1–S4)")
        for d in decisions:
            lines.append(
                f"- **{d['id']} {d['title']}** → `{d['chosen']}` · {d['resolved_as']} · kill: {d['kill']}"
            )
        lines.append("")
        lines.append("## 7. Тесты концептов (calendar kill)")
        for t in tests:
            lines.append(f"### {t['id']}")
            lines.append(f"- Гипотеза: {t['hypothesis']}")
            lines.append(f"- Метрика: {t['metric']}")
            lines.append(
                f"- **Календарь:** start `{t.get('start_date')}` · kill `{t.get('kill_date')}` · go `{t.get('go_date')}`"
            )
            lines.append(f"- Окно: {t['window']}")
            lines.append(f"- Stop: {t['stop']}")
            lines.append(f"- Go: {t['go']}")
            lines.append("")
        lines.append("## 8. Живой 7-day channel log")
        lines.append(f"- **Канал:** {channel_log.get('channel_name')}")
        lines.append(
            f"- **Окно:** {channel_log.get('start_date')} → {channel_log.get('end_date')} · "
            f"касаний target **{channel_log.get('touch_target')}**"
        )
        art = channel_log.get("artifact") or {}
        lines.append(
            f"- **Artifact (1):** {art.get('name')} · ship `{art.get('ship_day')}` · {art.get('format')}"
        )
        lines.append(f"- Правило: {channel_log.get('rule')}")
        for day in channel_log.get("days") or []:
            lines.append(
                f"  - `{day['day']}` · {day['label']}: {day['action']} · owner {day['owner']}"
            )
        lines.append("")
        lines.append("## 9. Unit economics (скелет)")
        lines.append(f"- Unit: {unit_econ.get('unit_name')}")
        lines.append(f"- Price anchor: ${unit_econ.get('price_anchor_usd')}")
        lines.append(f"- Core track: ${unit_econ.get('core_track_usd')}")
        lines.append(
            f"- COGS ≈ ${unit_econ.get('cogs_usd')} ({unit_econ.get('hours_per_unit')}ч × "
            f"${unit_econ.get('internal_rate_usd')})"
        )
        lines.append(f"- Target margin: {unit_econ.get('target_margin_pct')}%")
        lines.append(f"- Break-even units / 21d: {unit_econ.get('break_even_units_21d')}")
        lines.append(f"- Cash ceiling: ${unit_econ.get('cash_ceiling_pilot_usd')}")
        lines.append(f"- Note: {unit_econ.get('note')}")
        lines.append("")
        lines.append("## 10. Connect vs DIY")
        for row in connect:
            lines.append(
                f"- **{row['layer']}** (d{row['day']}): connect → {row['connect']}; DIY → {row['diy']}"
            )
        lines.append("")
        lines.append("## 11. План 21 день (с датами)")
        for p in pilot:
            lines.append(
                f"- **{p['days']}** `{p.get('dates', '')}` · {p['focus']} · owner: {p['owner']} · exit: {p['exit']}"
            )
        lines.append("")
        lines.append("## 12. Implementation assistant (после approval)")
        lines.append(f"- {assist.get('summary')}")
        lines.append(f"- Pay model: `{assist.get('pay_model')}`")
        for s in assist.get("steps") or []:
            lines.append(
                f"  - **{s['id']}** `{s['day']}` · {s['title']}: {s['action']} → {s['exit']}"
            )
        lines.append(f"- CTA: {assist.get('cta_after')}")
        lines.append("")
        lines.append("## 13. Оригинальные ходы")
        for m in (moves or [])[:6]:
            lines.append(f"- {m}")
        lines.append("")
        lines.append("## 14. Прогноз внедрения")
        lines.append(forecast_summary or "—")
        lines.append("")
        lines.append(f"## 15. Оценка ценности vs тариф Ядро (${CORE_PRICE_USD})")
        lines.append(
            f"- Реализовано сейчас: **${value['realized_value_usd_low']}–${value['realized_value_usd_high']}** "
            f"(mid ~${value['realized_mid_usd']})"
        )
        lines.append(
            f"- Gap до ${CORE_PRICE_USD}: **${value['gap_usd']}** (~{value['gap_pct']}%) · band `{value['band']}`"
        )
        lines.append(f"- Вердикт: {value['verdict']}")
        lines.append("- Что закрывает gap:")
        for w in value["what_closes_gap"]:
            lines.append(f"  - {w}")
        lines.append("")
        lines.append("## 16. Открытые вопросы / согласования")
        if open_questions:
            for q in open_questions:
                lines.append(f"- {q}")
        else:
            lines.append("- Критичные money-path слоты закрыты числами signer (подтвердите).")
        lines.append("")
        conf = (quality or {}).get("confidence")
        lines.append("## 17. Gate")
        lines.append(
            f"- Verdict: {gate.get('verdict', '—')} · confidence: {conf} · "
            f"commit_ready: {(quality or {}).get('commit_ready')}"
        )
        lines.append(
            f"- CTA: при band near_core / orientation_plus — **утвердить внедрение Ядра (${CORE_PRICE_USD})** "
            "→ открыть implementation assistant path."
        )
        lines.append("")
        lines.append("---")
        lines.append(
            "Оплата внедрения — опционально и только после утверждения. "
            "Структура и риск без обещаний auto-yield."
        )
    return "\n".join(lines)


def build_core_deliverable(
    business_text: str,
    *,
    core: dict[str, Any],
    orchestration: dict[str, Any] | None = None,
    channel: dict[str, Any] | None = None,
    forecast: dict[str, Any] | None = None,
    project_name: str = "",
    industry_id: str = "",
    lang: str = "ru",
    final_gate: dict[str, Any] | None = None,
    answers: dict[str, str] | None = None,
    numbers: dict[str, float] | None = None,
    start_date: date | None = None,
) -> dict[str, Any]:
    """Build primary human deliverable for Core tariff surface."""
    profile = _detect_profile(business_text)
    ans, nums = merge_signer_numbers(answers, numbers, profile=profile, lang=lang)
    start = start_date or date.today()
    days_window = int(float(nums.get("days", 21)))

    plan = (core or {}).get("plan") or {}
    quality = (core or {}).get("quality") or {}
    synthesis = (core or {}).get("synthesis") or {}
    moves = list(synthesis.get("original_moves") or [])

    arch = _architecture_cards(profile, lang)
    offers = _offer_cards(profile, lang)
    niches = _niche_cards(profile, orchestration or {}, lang)
    decisions = _decision_cards(profile, plan, lang)
    tests = _concept_tests(profile, lang, start=start, days_window=days_window)
    unit_econ = _unit_economics(profile, nums)
    connect = _connect_diy(profile, lang)
    pilot = _pilot_plan_21d(profile, lang, start=start)
    channel_log = _channel_log_7d(profile, lang, start=start)
    assist = _implementation_assistant_path(profile, lang, start=start)

    open_q = filter_open_questions(
        list(plan.get("open_questions") or []), ans, lang=lang, profile=profile
    )

    closed = profile["is_library"] or bool(quality.get("commit_ready")) or bool(ans.get("constraint_cash"))
    value = _value_assessment(
        profile,
        quality,
        len(arch) + len(offers) + len(tests),
        closed,
        has_channel_log=True,
        has_calendar=True,
        has_exports=True,
        has_assist=True,
        lang=lang,
    )

    ch = channel or {}
    if profile["is_library"]:
        identity = _d(
            lang,
            (
                f"Мы строим **онлайн-ядро**: библиотеку deep architectural designs и карточек решений "
                f"для билдеров IT-продуктов. Не «ещё один GPT-совет», а **геометрия**: unit, границы, "
                f"proof, kill на календаре. Канал: {ch.get('mode', 'online')}. "
                f"Уникальный угол: {_clip(business_text, 140)}."
            ),
            (
                f"We build an **online core**: a library of deep architectural designs and decision cards "
                f"for IT product builders. Not another GPT tip — **geometry**: unit, boundaries, "
                f"proof, calendar kill. Channel: {ch.get('mode', 'online')}. "
                f"Unique angle: {_clip(business_text, 140)}."
            ),
        )
    else:
        identity = _d(
            lang,
            (
                f"Growth/Yield ядро для: {_clip(business_text, 160)}. "
                f"Канал {ch.get('mode', 'auto')}. Структура активов и риск — без auto-yield."
            ),
            (
                f"Growth/Yield core for: {_clip(business_text, 160)}. "
                f"Channel {ch.get('mode', 'auto')}. Asset structure and risk — no auto-yield."
            ),
        )

    gate = final_gate or {}
    md = build_markdown(
        project_name=project_name or profile["title_hint"],
        profile=profile,
        identity=identity,
        arch=arch,
        offers=offers,
        niches=niches,
        decisions=decisions,
        tests=tests,
        unit_econ=unit_econ,
        connect=connect,
        pilot=pilot,
        value=value,
        moves=moves,
        forecast_summary=(forecast or {}).get("summary") or "",
        open_questions=open_q,
        gate=gate,
        quality=quality,
        channel_log=channel_log,
        assist=assist,
        answers=ans,
        lang=lang,
    )

    csv_blob = export_cards_csv(arch, offers, tests)
    html_blob = export_print_html(
        title=project_name or profile["title_hint"],
        markdown=md,
        lang=lang,
    )

    return {
        "title": project_name or profile["title_hint"],
        "format": "human_core_report",
        "primary": "markdown",
        "markdown": md,
        "identity": identity,
        "profile": profile,
        "recommended_choices": _recommended_choices(profile),
        "inferred_answers": _inferred_answers(profile, ans, nums, lang),
        "signer_numbers": {
            "cash_ceiling": float(nums.get("cash_ceiling", 0)),
            "days": int(float(nums.get("days", 21))),
            "team": int(float(nums.get("team", 1))) if "team" in nums else 1,
        },
        "architecture_cards": arch,
        "offer_cards": offers,
        "niche_cards": niches,
        "decision_cards": decisions,
        "concept_tests": tests,
        "channel_log_7d": channel_log,
        "implementation_assistant": assist,
        "unit_economics": unit_econ,
        "connect_vs_diy": connect,
        "pilot_21d": pilot,
        "value_vs_core": value,
        "original_moves": moves[:6],
        "open_questions": open_q,
        "exports": {
            "cards_csv": csv_blob,
            "print_html": html_blob,
            "markdown": md,
            "filenames": {
                "csv": "metrix-core-cards.csv",
                "html": "metrix-core-report.html",
                "md": "metrix-core-report.md",
            },
            "note": _d(
                lang,
                "Скачайте CSV/MD/HTML (print→PDF) — deliverable как файл, не только экран.",
                "Download CSV/MD/HTML (print→PDF) — deliverable as a file, not only on screen.",
            ),
        },
        "counts": {
            "architecture_cards": len(arch),
            "offer_cards": len(offers),
            "niche_cards": len(niches),
            "decision_cards": len(decisions),
            "concept_tests": len(tests),
            "channel_touches": channel_log.get("touch_target", 0),
            "assist_steps": len(assist.get("steps") or []),
            "total_cards": len(arch) + len(offers) + len(niches) + len(decisions) + len(tests),
        },
        "ux": {
            "show_json": False,
            "show_markdown_first": True,
            "collapse_raw": True,
            "show_exports": True,
            "show_assist_path": True,
            "cta": (
                _d(
                    lang,
                    f"Утвердить внедрение Ядра (${CORE_PRICE_USD}) → assist path",
                    f"Approve Core implementation (${CORE_PRICE_USD}) → assist path",
                )
                if value["band"] != "explore_draft"
                else _d(lang, "Закрыть gap и перегенерировать", "Close the gap and regenerate")
            ),
        },
        "industry_hint": industry_id,
        "lang": _lang(lang),
        "version": "core_deliverable_2.0_battle",
    }
