"""Seven Metrix lines. One brief, seven objects.

1 A2A steer + tab-5 screener
2 Deep tech (RTL / chips)
3 Brand assets
4 Libraries
5 Sales rails
6 Quality / metrics / ready projects
7 Terminal AI — placements in financial flows
"""

from __future__ import annotations

from typing import Any

from backend.core.a2a_screener import steer as run_l1
from backend.core.ai_mgmt import pack as run_ai_mgmt
from backend.core.complexity_boundary import lattice
from backend.core.craftshift_x import run as run_craftshift
from backend.core.engine_run import industry_for, run_engine
from backend.core.store_catalog import CATEGORIES, category_by_id
from backend.core.terminal_ai import place as run_l7
from backend.core.resonance import new_id, remember
from backend.core.voice import clip, first_sentence

LINE_SPINE = {
    1: "Линия 1 A2A: наведи запрос и вырежи неэффективности скринером. Выход — таблица дыр, не название платформы.",
    2: "Линия 2 Deep Tech: RTL/FPGA, слепой сигнал чипа, тег назначения, метрическая прошивка как include.",
    3: "Линия 3 Бренд: объект, который можно поставить в X. Голос, кадр, дружба как вход.",
    4: "Линия 4 Библиотеки: пак, который открывается без нового брифа. Карточка, не чат.",
    5: "Линия 5 Рельсы продаж: кто платит, какой unit, какой kill. Типизация одной продажи.",
    6: "Линия 6 Качество: усилить понятие, поставить метрику, назвать готовый проект. CraftShift и Store уже есть.",
    7: "Линия 7 Терминальный ИИ: посади агента в его денежный поток. Стул, молчание, kill. Не чат и не бизнес для чужих клиентов.",
}


def _engine(brief: str, industry: str) -> dict[str, Any]:
    pack = run_engine(brief, industry=industry, lang="ru")
    return {
        "ok": bool(pack.get("ok")),
        "request_id": pack.get("request_id") or "",
        "idea_title": pack.get("idea_title") or "",
        "idea_blurb": clip(str(pack.get("idea_blurb") or ""), 220),
        "next_steps": list(pack.get("next_steps") or [])[:4],
        "metrics": pack.get("metrics") or {},
    }


def run_line(n: int, brief: str, *, with_engine: bool = True) -> dict[str, Any]:
    cat = category_by_id(str(n)) or {}
    text = (brief or "").strip()
    if n == 1:
        art = run_l1(text)
    elif n == 7:
        art = run_l7(text)
        mgmt = run_ai_mgmt(text)
        art["ai_mgmt"] = {
            "title": mgmt.get("title"),
            "artefacts": mgmt.get("artefacts"),
            "prompt": mgmt.get("prompt"),
        }
    elif n == 3:
        art = run_craftshift(text)
        art["kind"] = "line.brand"
        art["line"] = 3
        art["lane"] = "brand"
        art["title"] = "Бренд-актив"
    elif n == 6:
        art = run_craftshift(text)
        art["kind"] = "line.quality"
        art["line"] = 6
        art["lane"] = "quality"
        art["title"] = "Качество · готовый проект"
        art["ready"] = ["CraftShift", "Metrix Store", "Door", "Lattice Recursion"]
    else:
        sit = first_sentence(text, cat.get("title") or "линия")
        art = {
            "id": new_id(),
            "kind": f"line.{cat.get('id') or n}",
            "lane": cat.get("id") or str(n),
            "line": n,
            "title": cat.get("title") or f"Линия {n}",
            "break": f"«{clip(sit, 80)}» не собрана в unit «{cat.get('unit')}».",
            "move": cat.get("one"),
            "steps": [
                cat.get("one"),
                f"Unit: {cat.get('unit')}.",
                "Сначала таблица осей, потом имя.",
                "Kill — если за 14 дней объект не взяли.",
            ],
            "wow": cat.get("one"),
        }
        if n == 2:
            art["steps"] = [
                "Физический сигнал, который сейчас слепой.",
                "RTL/агент только на этот сигнал.",
                "Назначение чипа — тег, не слайд.",
                "Прошивка как include, не как проект на год.",
            ]
        if n == 4:
            art["steps"] = [
                "Пак открывается без нового брифа.",
                "Карточка: вход, правило, kill.",
                "Повтор = библиотека. Разово = героизм.",
            ]
        if n == 5:
            art["steps"] = [
                "Кто платит — роль, не «рынок».",
                "Unit явен.",
                "Рельс: бриф → объект → kill.",
                "Тип продажи один на контур.",
            ]
    art["category"] = cat
    art["lattice"] = lattice(text)
    if not art.get("id"):
        art["id"] = new_id()
    remember(art)
    if with_engine and len(text) >= 16:
        ind = {
            1: "ai-agencies",
            2: "device-assembly",
            3: "asset-decisions",
            4: "ai-agencies",
            5: "saas-founders",
            6: "expert-services",
            7: "expert-services",
        }.get(n) or industry_for(text)
        # infa-sol may not exist — fall back
        spine = LINE_SPINE.get(n) or ""
        engine_brief = f"{spine}\n{text}"
        try:
            art["engine"] = _engine(engine_brief, ind)
        except Exception as exc:  # noqa: BLE001
            art["engine"] = _engine(engine_brief, "expert-services")
            art["engine"]["fallback"] = str(exc)[:120]
    return art


def run_all(brief: str, *, with_engine: bool = True) -> dict[str, Any]:
    lines = [run_line(c["n"], brief, with_engine=with_engine) for c in CATEGORIES]
    return {
        "ok": True,
        "brief": clip(brief, 400),
        "lattice": lattice(brief),
        "lines": lines,
        "craftshift": run_craftshift(brief),
        "ai_mgmt": run_ai_mgmt(brief),
    }
