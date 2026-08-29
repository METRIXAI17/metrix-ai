"""Menu routing for reply keyboard, commands, and inline callbacks."""

from __future__ import annotations

ALIASES = {
    "start": "start",
    "app": "start",
    "help": "help",
    "landing": "landing",
    "лендинг": "landing",
    "комната": "landing",
    "demo": "landing",
    "демо": "landing",
    "engine": "engine",
    "движок": "engine",
    "strategies": "engine",
    "strategy": "engine",
    "стратегии": "engine",
    "agents": "engine",
    "agent": "engine",
    "агенты": "engine",
    "making": "making",
    "мейкинг": "making",
    "сборка": "making",
    "posts": "making",
    "post": "making",
    "посты": "making",
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
