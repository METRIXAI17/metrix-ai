"""Line 1 — first A2A: steer the query, then screen inefficiencies.

Tab 5 of the public surface (Promo) is the screener door.
A2A here is agent-to-agent: one agent reads the request, another marks leaks.
"""

from __future__ import annotations

from typing import Any

from backend.core.complexity_boundary import lattice
from backend.core.resonance import new_id, remember
from backend.core.voice import DISCLAIMER, clip, first_sentence


LEAKS = (
    ("essay", ("платформ", "orchestrator", "middleware", "святой грааль"), "эссе вместо объекта"),
    ("price_fantasy", ("$10,000", "$50,000", "миллионн"), "цифра без unit и без пилота"),
    ("repeat_diagram", ("физический уровень", "чип а", "чип б"), "повтор той же схемы"),
    ("no_kill", ("гарантир", "революц", "всегда"), "нет kill-условия"),
    ("passport", ("анкет", "оставьте контакт", "квалификац"), "вход просит паспорт дважды"),
    ("no_object", ("стратегия", "видение", "экосистем"), "нет вещи, которую можно взять"),
)


def screen(brief: str) -> dict[str, Any]:
    t = (brief or "").lower()
    hits = []
    for lid, keys, name in LEAKS:
        if any(k in t for k in keys):
            hits.append({"id": lid, "name": name})
    if len((brief or "").split()) > 180:
        hits.append({"id": "long", "name": "слишком длинный вход — свернуть в таблицу"})
    if not hits:
        hits.append({"id": "open", "name": "явной дыры нет — ищи границу сложности"})
    return {"leaks": hits, "count": len(hits)}


def steer(brief: str) -> dict[str, Any]:
    text = (brief or "").strip() or "запрос без тела"
    sit = first_sentence(text, "запрос")
    lat = lattice(text)
    scr = screen(text)
    leak0 = (scr["leaks"][0] or {}).get("name")
    art = {
        "id": new_id(),
        "kind": "line.a2a",
        "lane": "a2a",
        "line": 1,
        "title": "Наводка A2A",
        "break": f"Запрос «{clip(sit, 72)}» ещё не наведён. Скринер видит: {leak0}.",
        "move": lat.get("title") or "Свернуть в таблицу осей. Убрать эссе.",
        "steps": [
            f"Скринер: {leak0}.",
            f"Решётка: {lat.get('depth')} осей, {lat.get('remaining')} комбинаций.",
            f"Граница: {(lat.get('boundary') or {}).get('poke')}",
            "A2A: агент-навигатор держит запрос, агент-скринер режет дыру.",
            "Выход — таблица, не манифест продукта.",
        ],
        "artifact_week": "Один наведённый запрос + список дыр. Без нового названия платформы.",
        "anti": ["Не писать архитектуру на 3 уровня.", "Не назначать цену, пока нет unit."],
        "disclaimer": DISCLAIMER,
        "table": lat.get("table"),
        "screener": scr,
        "lattice": lat,
        "wow": lat.get("wow"),
        "meta": {"tab": 5, "engine": "metrix_ai", "a2a": True},
    }
    remember(art)
    return art
