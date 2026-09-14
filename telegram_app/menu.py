"""Menu routing for reply keyboard, commands, and inline callbacks."""

from __future__ import annotations

ALIASES = {
    "start": "start",
    "app": "start",
    "help": "help",
    "access": "access",
    "подписка": "access",
    "life": "life",
    "жизнь": "life",
    "разговор": "life",
    "идеи для жизни": "life",
    "store": "store",
    "стор": "store",
    "магазин metrix": "store",
    "metrix store": "store",
    "shift": "shift",
    "craftshift": "shift",
    "крафт": "shift",
    "door": "door",
    "дверь": "door",
    "chain": "life",
    "in-out chain": "life",
    "in-out": "life",
    "inout": "life",
    "landing": "life",
    "лендинг": "life",
    "demo": "life",
    "демо": "life",
    "bots": "bots",
    "боты": "bots",
    "торговые боты": "bots",
    "strategies": "bots",
    "strategy": "bots",
    "стратегии": "bots",
    "craft": "craft",
    "ремесло": "craft",
    "конфиги для ремесла": "craft",
    "teammates": "craft",
    "teammate": "craft",
    "ai teammates": "craft",
    "engine": "craft",
    "движок": "craft",
    "target": "target",
    "агенты": "target",
    "таргет ии-агентов": "target",
    "таргет ии агентов": "target",
    "agents": "target",
    "agent": "target",
    "shop": "shop",
    "магазин": "shop",
    "каталог магазина": "shop",
    "artefacts": "shop",
    "artifacts": "shop",
    "making": "shop",
    "мейкинг": "shop",
    "посты": "shop",
    "posts": "shop",
    "post": "shop",
    "hit": "hits",
    "hits": "hits",
    "хит": "hits",
    "хиты": "hits",
    "конструкц": "hits",
    "конструкции": "hits",
    "glossary": "hits",
    "глоссарий": "hits",
    "подписка-хит": "sub",
    "обучен": "sub",
    "приватка": "private",
    "private": "private",
}


def menu_action(text: str) -> str | None:
    """Map a user tap or command to a menu id. None = not a menu button."""
    t = (text or "").strip().lower()
    if not t:
        return None
    if t.startswith("/"):
        t = t[1:]
        t = t.split("@", 1)[0]
        t = t.split()[0] if t else t
    return ALIASES.get(t)
