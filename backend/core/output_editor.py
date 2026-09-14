"""Editor of Metrix client-facing text. Same genre, cleaner. RU."""

from __future__ import annotations

import re

_BANNED = (
    r"локомотив",
    r"вселенн",
    r"трансформац",
    r"\bVVI\b",
    r"\bRRC\b",
    r"(?<![A-Za-z])ER(?![A-Za-z])",
    r"прод\s*[×xх]\s*3",
    r"7 направлен",
)

_REPL = {
    "локомотив": "поток",
    "вселенная": "контур",
    "вселенн": "контур",
    "трансформация": "сборка",
    "VVI": "видимость",
    "RRC": "сборка",
}


def edit_client_text(text: str, *, order_type: str = "TYPE_A") -> str:
    t = (text or "").strip()
    for a, b in _REPL.items():
        t = re.sub(a, b, t, flags=re.I)
    t = re.sub(r"!{2,}", ".", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    lines = [ln.rstrip() for ln in t.splitlines()]
    t = "\n".join(lines).strip()
    low = t.lower()
    if order_type == "TYPE_A" and "ретейн" not in low and "понедельник" in low:
        t += "\nРетейнер отчёта — на сдаче."
    if order_type == "TYPE_B" and "замк" in low and "следующ" not in low:
        t += "\nСледующий в этом же замке — тема X или Y?"
    return t


def banned_hits(text: str) -> list[str]:
    t = text or ""
    return [p for p in _BANNED if re.search(p, t, re.I)]
