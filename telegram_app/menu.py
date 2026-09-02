"""Menu routing for reply keyboard, commands, and inline callbacks."""

from __future__ import annotations

ALIASES = {
    "start": "start",
    "app": "start",
    "help": "help",
    "access": "access",
    "подписка": "access",
    "chain": "chain",
    "in-out chain": "chain",
    "in-out": "chain",
    "inout": "chain",
    "landing": "chain",
    "лендинг": "chain",
    "комната": "chain",
    "demo": "chain",
    "демо": "chain",
    "teammates": "teammates",
    "teammate": "teammates",
    "ai teammates": "teammates",
    "engine": "teammates",
    "движок": "teammates",
    "strategies": "chain",
    "strategy": "chain",
    "стратегии": "chain",
    "agents": "teammates",
    "agent": "teammates",
    "агенты": "teammates",
    "artefacts": "artefacts",
    "artifacts": "artefacts",
    "making": "artefacts",
    "мейкинг": "artefacts",
    "сборка": "artefacts",
    "posts": "artefacts",
    "post": "artefacts",
    "посты": "artefacts",
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
