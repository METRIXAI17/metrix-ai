"""Menu routing for reply keyboard, commands, and inline callbacks."""

from __future__ import annotations

ALIASES = {
    "start": "start",
    "app": "start",
    "help": "help",
    "demo": "demo",
    "демо": "demo",
    "strategies": "strategies",
    "strategy": "strategies",
    "стратегии": "strategies",
    "agents": "agents",
    "agent": "agents",
    "агенты": "agents",
    "posts": "posts",
    "post": "posts",
    "посты": "posts",
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
