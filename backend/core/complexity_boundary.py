"""Lattice Recursion — olympiad combinatorics, not more prose.

Karim's poke: add one constraint that kills most remaining combinations.
First object is a TABLE. Think-more adds one row, not an essay.

Complexity Boundary Metric (CBM):
  depth        — independent constraints already stacked
  remaining    — combinations that still survive
  leak         — named inefficiency
  boundary     — cheapest next poke that would change the verdict
  originality  — how far from a named-product template
"""

from __future__ import annotations

import re
from typing import Any

from backend.core.voice import clip, first_sentence

AXES: list[dict[str, str]] = [
    {"id": "self_dev", "ru": "саморазвитие", "en": "self-development", "poke": "что именно растёт, если сделка не случилась"},
    {"id": "stance", "ru": "личное отношение к проблеме", "en": "personal stance", "poke": "чья это боль — твоя или рынка"},
    {"id": "ttd", "ru": "время до первой сделки", "en": "time to first deal", "poke": "какой срок убивает идею"},
    {"id": "rear", "ru": "тыл / расслабление", "en": "rear rest", "poke": "что можно выключить, чтобы не сгореть"},
    {"id": "ops", "ru": "операционка", "en": "ops", "poke": "какой шаг повторяется руками больше двух раз"},
    {"id": "cash", "ru": "деньги на жизнь/бизнес", "en": "cash", "poke": "какая сумма закрывает месяц без героизма"},
    {"id": "funding", "ru": "финансирование", "en": "funding", "poke": "капитал за структуру или за слайд"},
    {"id": "fragment", "ru": "кризис фрагментации", "en": "fragmentation", "poke": "какие два потока не видят друг друга"},
    {"id": "chip", "ru": "данные с чипов", "en": "chip data", "poke": "какой физический сигнал сейчас слепой"},
    {"id": "intent", "ru": "назначение чипа", "en": "chip intent", "poke": "какая задача критична, какая фон"},
    {"id": "function", "ru": "функциональная роль", "en": "function role", "poke": "кто сердце, кто глаза, кто запасной"},
    {"id": "firmware", "ru": "метрическая прошивка", "en": "metric firmware", "poke": "какой proof-of-task можно зашить в 1 include"},
    {"id": "distro", "ru": "дистрибуция", "en": "distribution", "poke": "где уже стоят люди, не где «надо охватить»"},
    {"id": "quality", "ru": "качество объекта", "en": "object quality", "poke": "что можно взять руками сегодня"},
    {"id": "friend", "ru": "дружба как вход", "en": "friendship door", "poke": "где система просит паспорт дважды"},
]

_KW: dict[str, tuple[str, ...]] = {
    "self_dev": ("саморазвит", "рост", "учеба", "итмо", "курс"),
    "stance": ("отношен", "проблем", "боль", "stance"),
    "ttd": ("первой сделк", "время до", "mvp", "мвп", "первая продаж"),
    "rear": ("тыл", "расслаб", "выгоран", "сон"),
    "ops": ("операцион", "рутин", "процесс", "повтор"),
    "cash": ("хватает ли денег", "касса", "жизнь", "месяц"),
    "funding": ("финанс", "капитал", "грант", "инвест"),
    "fragment": ("фрагмент", "зоопарк", "разные протокол", "не видят"),
    "chip": ("чип", "fpga", "rtl", "risc", "телеметр", "плис"),
    "intent": ("назначен", "intent", "приоритет", "критическ"),
    "function": ("функциональн", "роль", "сердце", "глаза", "hot swap"),
    "firmware": ("прошивк", "firmware", "sdk", "include"),
    "distro": ("дистриб", "push", "native", "телеграм", "охват"),
    "quality": ("качеств", "надёжн", "rails", "рельс"),
    "friend": ("дружб", "друг", "вход без", "паспорт"),
}


def _present(text: str) -> list[str]:
    t = (text or "").lower()
    hits = []
    for ax in AXES:
        keys = _KW.get(ax["id"]) or ()
        if any(k in t for k in keys):
            hits.append(ax["id"])
    return hits


def _missing(present: list[str]) -> list[dict[str, str]]:
    have = set(present)
    return [ax for ax in AXES if ax["id"] not in have]


def _combinations(n_present: int, n_total: int = 15) -> int:
    # surviving combo count: 2^(unknown) with a floor, dampened by stacked constraints
    unknown = max(0, n_total - n_present)
    return max(1, 2 ** min(unknown, 12))


def lattice(brief: str, extra_axes: list[str] | None = None) -> dict[str, Any]:
    text = (brief or "").strip()
    present = _present(text)
    for ax in extra_axes or []:
        if ax and ax not in present:
            present.append(ax)
    miss = _missing(present)
    remaining = _combinations(len(present))
    depth = len(present)
    # originality: Karim-style stacked constraints beat named-product templates
    named = bool(re.search(r"(platform|orchestrator|middleware|saas fee)", text, re.I))
    originality = round(min(1.0, 0.18 * depth + (0.0 if named else 0.25)), 3)
    leak_ax = miss[0] if miss else AXES[4]
    leak = leak_ax["poke"]
    boundary = miss[0] if miss else None
    cbm = round(min(1.0, depth / 8.0 + (1.0 / max(remaining, 1)) * 0.4), 3)
    rows = []
    for ax in AXES:
        on = ax["id"] in present
        rows.append(
            {
                "axis": ax["id"],
                "name": ax["ru"],
                "state": "on" if on else "open",
                "poke": "" if on else ax["poke"],
            }
        )
    verdict = (
        "решётка живая — следующий укол убьёт лишнее"
        if remaining > 4
        else "комбинация сжата — можно назвать объект"
    )
    title = first_sentence(text, "контур без имени")
    named_object = clip(
        f"{'Сжатый' if remaining <= 4 else 'Открытый'} контур · {depth} осей · {remaining} комбинаций",
        96,
    )
    return {
        "ok": True,
        "method": "lattice_recursion",
        "title": named_object,
        "seed": clip(title, 120),
        "table": rows,
        "present": present,
        "depth": depth,
        "remaining": remaining,
        "leak": leak,
        "boundary": {
            "axis": (boundary or {}).get("id") if isinstance(boundary, dict) else None,
            "name": (boundary or {}).get("ru") if isinstance(boundary, dict) else None,
            "poke": (boundary or {}).get("poke") if isinstance(boundary, dict) else leak,
        },
        "cbm": cbm,
        "originality": originality,
        "verdict": verdict,
        "wow": f"Осталось {remaining} комбинаций. Один укол — «подумать ещё».",
    }


def think_more(brief: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Add one Karim-style constraint: the current boundary axis."""
    prev = state or lattice(brief)
    extra = list(prev.get("present") or _present(brief))
    b = prev.get("boundary") or {}
    axis = b.get("axis")
    if axis and axis not in extra:
        extra.append(axis)
    elif extra:
        for ax in AXES:
            if ax["id"] not in extra:
                extra.append(ax["id"])
                break
    nxt = lattice(brief, extra_axes=extra)
    nxt["think_more"] = int(prev.get("think_more") or 0) + 1
    nxt["added_axis"] = axis
    nxt["wow"] = (
        f"Укол #{nxt['think_more']}: {b.get('poke') or 'ещё одна ось'}. "
        f"Комбинаций {prev.get('remaining')} → {nxt['remaining']}."
    )
    return nxt


def attach_boundary(out: dict[str, Any], brief: str) -> dict[str, Any]:
    lat = lattice(brief)
    meta = dict(out.get("meta") or {})
    meta["complexity_boundary"] = lat
    out["meta"] = meta
    out["complexity_boundary"] = lat
    return out


def table_telegram(lat: dict[str, Any]) -> str:
    lines = [
        f"<b>{lat.get('title') or 'Решётка'}</b>",
        lat.get("wow") or "",
        "",
        "<code>ось                  статус</code>",
    ]
    for row in (lat.get("table") or [])[:12]:
        mark = "●" if row.get("state") == "on" else "○"
        lines.append(f"{mark} {row.get('name')}")
    b = lat.get("boundary") or {}
    if b.get("poke"):
        lines.append("")
        lines.append(f"граница: {b['poke']}")
    return "\n".join(x for x in lines if x is not None)
