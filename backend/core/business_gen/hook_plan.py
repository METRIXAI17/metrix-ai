"""
Hook plan — short, catchy custom plan that makes the buyer want Core.

Not a second full report: a 6–8 line purchase-oriented surface
shown above the long Core markdown.
"""

from __future__ import annotations

from typing import Any

CORE_PRICE_USD = 790


def build_hook_plan(
    *,
    project_name: str,
    profile: dict[str, Any],
    value: dict[str, Any],
    counts: dict[str, Any],
    signer_numbers: dict[str, Any],
    channel_log: dict[str, Any] | None = None,
    concept_tests: list[dict[str, str]] | None = None,
    assist: dict[str, Any] | None = None,
    open_questions: list[str] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """Return a compact conversion surface + one-screen markdown."""
    is_en = (lang or "").lower().startswith("en")
    title = project_name or profile.get("title_hint") or "Your Core"
    mid = value.get("realized_mid_usd", 0)
    gap = value.get("gap_usd", CORE_PRICE_USD)
    band = value.get("band", "orientation_plus")
    cash = int(float((signer_numbers or {}).get("cash_ceiling") or 1500))
    days = int(float((signer_numbers or {}).get("days") or 21))
    cards_n = int((counts or {}).get("total_cards") or 0)
    touches = int((counts or {}).get("channel_touches") or 0)
    kill = ""
    if concept_tests:
        t1 = concept_tests[0]
        kill = f"{t1.get('id', 'T1')} kill {t1.get('kill_date', '')}"
    art = ((channel_log or {}).get("artifact") or {}).get("name") or "1 proof artifact"
    # Count only money-path open questions (cash/time/who/unit) — not regulatory noise
    money_toks = (
        "бюджет",
        "cash",
        "потол",
        "ceiling",
        "budget",
        "окно",
        "дней",
        "days",
        "кто платит",
        "who pays",
        "единиц",
        "unit of",
        "метрик",
        "metric",
    )
    oq = sum(
        1
        for q in (open_questions or [])
        if any(t in (q or "").lower() for t in money_toks)
    )

    if is_en:
        headline = f"{title} — your Core in one screen"
        pitch = (
            f"Not a dump of advice: **{cards_n} decision cards**, a **{touches}-touch / 7-day log**, "
            f"and **calendar kills** so you know when to stop."
        )
        lines = [
            f"### Your custom plan (buy-ready)",
            f"**{headline}**",
            "",
            f"1. **Who pays:** {profile.get('payer', '—')}",
            f"2. **Unit you sell:** {profile.get('unit', '—')}",
            f"3. **Cash ceiling / window:** ${cash} · {days} days (signer numbers locked)",
            f"4. **7-day proof:** {touches} touches + artifact «{art}»",
            f"5. **Kill on calendar:** {kill or 'T1 dated'}",
            f"6. **After you approve:** implementation assistant path opens "
            f"({(assist or {}).get('summary', '5 assist steps')})",
            "",
            f"**Value now ~${mid}** of Core **${CORE_PRICE_USD}** · gap **${gap}** · band `{band}`",
            f"Open money questions left: **{oq}** (cash/days already filled from signer).",
            "",
            f"> Approve Core (${CORE_PRICE_USD}) → file exports (CSV/MD/PDF) + assist path. "
            f"Pay only after you say go.",
        ]
        bullets = [
            f"{cards_n} deep cards (SaaS billing · agent ops · API cost…)",
            f"{touches}-touch live channel log + 1 artifact",
            f"Calendar kill {kill or 'T1–T3'}",
            f"Cash ${cash} / {days}d locked in answers",
            "Implementation assistant after approval (not CTA-only)",
            "Download CSV + print HTML→PDF",
        ]
        cta = f"Approve Core · ${CORE_PRICE_USD}"
        sub_cta = "Download pack · then open assist path"
    else:
        headline = f"{title} — ваше Ядро на одном экране"
        pitch = (
            f"Не свалка советов: **{cards_n} карточек решений**, **{touches} касаний / 7 дней**, "
            f"и **kill на календаре** — чтобы знать, когда остановиться."
        )
        lines = [
            f"### Ваш кастомный план (чтобы захотеть купить)",
            f"**{headline}**",
            "",
            f"1. **Кто платит:** {profile.get('payer', '—')}",
            f"2. **Unit продажи:** {profile.get('unit', '—')}",
            f"3. **Cash / окно:** ${cash} · {days} дней (числа signer зафиксированы)",
            f"4. **Proof за 7 дней:** {touches} касаний + artifact «{art}»",
            f"5. **Kill на календаре:** {kill or 'T1 с датой'}",
            f"6. **После approval:** открывается implementation assistant "
            f"({(assist or {}).get('summary', '5 шагов assist')})",
            "",
            f"**Ценность сейчас ~${mid}** из Core **${CORE_PRICE_USD}** · gap **${gap}** · band `{band}`",
            f"Открытых money-вопросов: **{oq}** (cash/days уже из signer).",
            "",
            f"> Утвердить Ядро (${CORE_PRICE_USD}) → файлы (CSV/MD/PDF) + assist path. "
            f"Оплата только после вашего GO.",
        ]
        bullets = [
            f"{cards_n} deep-карточек (SaaS billing · agent ops · API cost…)",
            f"Живой log: {touches} касаний + 1 artifact",
            f"Calendar kill {kill or 'T1–T3'}",
            f"Cash ${cash} / {days}д в answers",
            "Implementation assistant после approval (не только CTA)",
            "Скачать CSV + print HTML→PDF",
        ]
        cta = f"Утвердить Ядро · ${CORE_PRICE_USD}"
        sub_cta = "Скачать pack · затем assist path"

    markdown = "\n".join(lines)
    return {
        "module": "HookPlan",
        "version": "1.0",
        "headline": headline,
        "pitch": pitch,
        "bullets": bullets,
        "markdown": markdown,
        "cta": cta,
        "sub_cta": sub_cta,
        "price_usd": CORE_PRICE_USD,
        "value_mid_usd": mid,
        "gap_usd": gap,
        "band": band,
        "open_questions_left": oq,
        "why_buy_now": bullets[:4],
        "lang": "en" if is_en else "ru",
    }
