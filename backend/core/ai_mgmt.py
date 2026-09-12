"""Derivative prompt: managing work with AI + value artefacts.

Store category 7 (placements) ships these as objects, not advice.
"""

from __future__ import annotations

from typing import Any

from backend.core.resonance import new_id, remember
from backend.core.voice import DISCLAIMER, clip, first_sentence

PROMPT = """# AI Work Management — derivative of Metrix AI

You are not a chat. You are a seat on a cash path.

INTAKE (table, not essay)
- What breaks money this week
- Who pays
- What object the human keeps
- Kill: when you go silent

LATTICE
Add one constraint at a time (Karim poke). Each poke must kill combinations.
Never rename the product to sound smarter.

A2A
Navigator reads the request. Screener marks leaks (essay, price fantasy, no kill, passport twice).
Terminal places an agent only after a seat exists.

OUTPUT — four artefacts, always:
1. Work Charter — one page: job, unit, silence, kill
2. Kill Card — the fact that ends the run
3. Placement Seat — where in the money flow the agent sits
4. Proof Packet — the object the human can show without you

TONE
Short. Concrete. No guru. No yield promise.
Friendship door: do not ask for a passport twice.

If the human says «не нравится» — do not repeat the last architecture. Add one constraint.
"""

ARTEFACTS = (
    {
        "id": "work_charter",
        "title": "Work Charter",
        "one": "Работа, unit, молчание, kill — одна страница.",
    },
    {
        "id": "kill_card",
        "title": "Kill Card",
        "one": "Факт, который заканчивает прогон. Без факта прогон бесконечен.",
    },
    {
        "id": "placement_seat",
        "title": "Placement Seat",
        "one": "Стул агента в чужом денежном потоке.",
    },
    {
        "id": "proof_packet",
        "title": "Proof Packet",
        "one": "Объект, который человек показывает без тебя.",
    },
)


def pack(brief: str) -> dict[str, Any]:
    text = (brief or "").strip() or "нужен контур работы с ИИ, не чат"
    sit = first_sentence(text, "работа с ИИ")
    items = []
    for a in ARTEFACTS:
        items.append(
            {
                **a,
                "applied": clip(f"{a['title']}: {sit}", 160),
            }
        )
    art = {
        "id": new_id(),
        "kind": "line.ai_mgmt",
        "lane": "placements",
        "line": 7,
        "title": "Менеджмент работы с ИИ",
        "one_liner": "Четыре артефакта ценности. Промпт — производная Metrix AI.",
        "break": f"«{clip(sit, 80)}» ещё управляется чатом, не посадкой.",
        "move": "Чартер → kill → стул в потоке → proof. ИИ без стула — собеседник.",
        "prompt": PROMPT,
        "artefacts": items,
        "steps": [a["one"] for a in ARTEFACTS],
        "artifact_week": "Собрать 4 артефакта на один живой поток.",
        "anti": ["Не писать «framework сотрудничества».", "Не добавлять пятый артефакт без kill."],
        "disclaimer": DISCLAIMER,
        "wow": "ИИ без стула в деньгах — это хобби.",
        "meta": {"engine": "metrix_ai", "derivative": "ai_mgmt", "store_category": 7},
    }
    remember(art)
    return art
