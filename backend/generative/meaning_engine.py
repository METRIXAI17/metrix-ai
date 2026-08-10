"""
Generative meaning engine (block 19 upgrade).

Builds dense meaning moves from brief + path + segment — not generic slogans.
Feeds originality surface and essence presentation.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def _tok(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]{4,}", (text or "").lower())


def _seed(text: str) -> int:
    return int(hashlib.sha256((text or "").encode()).hexdigest()[:10], 16)


MOVE_TEMPLATES_RU = [
    "Смысл: {core} — не как «улучшение», а как снятие friction «{friction}».",
    "Анти-смысл: мы не {anti}; мы даём {unit} с kill.",
    "Геометрия: persona×work×situation → один lever за цикл.",
    "Доказательство: 1 artifact > 10 стратегий; path={path}.",
    "Деньги: structural surface first; capital только после structure_first.",
    "Исполнение: S0–S10 видимы; approve глазами, не «магия модели».",
    "Promo вшит в situation: angle из top friction, не отдельный «маркетинг».",
    "Оригинал: hash-уникальный title + triple report shape.",
]

FRICTION_GUESS = [
    ("rework", ("rework", "передел", "handoff", "сдач")),
    ("scope", ("scope", "размаз", "всё сразу", "много")),
    ("cost", ("api", "token", "cost", "дорог")),
    ("identity", ("увлеч", "творч", "persona", "узнава")),
    ("ship", ("отгруз", "ship", "publish", "запуск")),
    ("margin", ("марж", "margin", "утеч", "leak")),
]


def expand_meanings(
    business_text: str,
    *,
    path_id: str = "",
    segment_id: str = "",
    unit: str = "unit pack",
    lang: str = "ru",
) -> dict[str, Any]:
    is_ru = not (lang or "").lower().startswith("en")
    t = (business_text or "").lower()
    toks = _tok(business_text)
    seed = _seed(business_text + path_id + segment_id)

    friction = "open"
    for fid, keys in FRICTION_GUESS:
        if any(k in t for k in keys):
            friction = fid
            break

    core = " ".join(toks[:6]) if toks else "craft shift"
    anti = "ещё один AI-чат" if is_ru else "another AI chat"

    templates = MOVE_TEMPLATES_RU if is_ru else [
        "Meaning: {core} removes friction «{friction}», not vague improvement.",
        "Anti: not {anti}; we ship {unit} with kill.",
        "Geometry: three axes → one lever per cycle.",
        "Proof: 1 artifact > 10 strategies; path={path}.",
        "Money: structural surface first; capital after structure_first.",
        "Exec: S0–S10 visible; human approve before execute.",
        "Promo woven into situation from top friction.",
        "Original: hash-unique title + triple report.",
    ]

    moves = []
    for i, tmpl in enumerate(templates):
        if (seed >> i) & 1 or i < 5:  # keep at least 5
            moves.append(
                tmpl.format(
                    core=core[:48],
                    friction=friction,
                    anti=anti,
                    unit=unit,
                    path=path_id or "library_ship",
                )
            )

    # densify with unique pairs
    pairs = []
    if "карточ" in t or "catalog" in t or "catalog" in path_id:
        pairs.append("catalog=executable offers" if not is_ru else "каталог=исполняемые офферы")
    if "увлеч" in t or "творч" in t or "hobby" in t:
        pairs.append("hobby→measured shift" if not is_ru else "увлечение→измеримый сдвиг")
    if "api" in t:
        pairs.append("API approve-and-run surface")
    pairs.append(f"segment={segment_id or '—'}")

    density = round(min(1.0, 0.35 + 0.08 * len(moves) + 0.05 * len(pairs) + min(0.2, len(set(toks)) / 80)), 3)

    essence = (
        f"«{core[:40]}» · unit={unit} · friction={friction} · "
        f"path={path_id or '—'} · anti={anti}"
    )

    return {
        "module": "MeaningEngine",
        "version": "1.0.0",
        "status": "live",
        "friction": friction,
        "core_phrase": core[:80],
        "moves": moves[:8],
        "pairs": pairs,
        "density": density,
        "essence_one_liner": essence,
        "block19": True,
        "message": (
            f"Meaning density={density} · moves={len(moves)}"
            if not is_ru
            else f"Плотность смысла={density} · moves={len(moves)}"
        ),
    }
