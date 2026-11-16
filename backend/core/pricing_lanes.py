"""Public SKUs for four rooms. Hits view + Web3 Store requests are free.

Base subscription is allo_month at 50 USD. Upper rooms stay for recursion and specs.
"""

from __future__ import annotations

import os
import re
from typing import Any

from backend.config import HUMAN_CONTACT_URL, TRIBUTE_ACCESS_URL, TRIBUTE_CUSTOM_URL

# Exact Tribute amounts. Never a threshold (50 must not become sku_100).
SKU_BY_USD = {
    50: "allo_month",
    100: "sku_100",
    490: "sku_490",
    1000: "sku_1000",
    2490: "full_package",
    10000: "sku_10000",
}

_EXPLICIT_IDS = (
    "sku_10000",
    "sku_1000",
    "sku_490",
    "sku_100",
    "custom_spec_pilot",
    "cross_assist",
    "full_package",
    "directing_fee",
    "game_pack",
    "allo_month",
    "access_year",
    "access_month",
)

SKUS: dict[str, dict[str, Any]] = {
    "free_life": {
        "id": "free_life",
        "usd": 0,
        "rub": 0,
        "tier": "free",
        "file": False,
        "automated": False,
        "requests": None,
        "name_ru": "Для жизни · бесплатный слой",
        "name_en": "For life · free layer",
        "gets_ru": (
            "Суть одной фразой. Решение одной фразой. "
            "5–20 простых вопросов. Eval. Тикер. Цепочка в файл."
        ),
        "gets_en": "Problem one phrase, solution one phrase, 5–20 questions, eval, ticker, chain file.",
    },
    "allo_month": {
        "id": "allo_month",
        "usd": 50,
        "rub": 0,
        "tier": "allo",
        "file": False,
        "recurse_spec": False,
        "automated": True,
        "requests": 40,
        "tokens": 40,
        "days": 31,
        "name_ru": "$50 · Allo",
        "name_en": "$50 · Allo",
        "gets_ru": "Дверь, чтение семи операций, грант запросов на месяц. Не directing, не файл рекурсии, не Main $2490.",
        "gets_en": "Door, reading of seven operations, monthly request grant. Not directing, not the recursion file, not Main $2490.",
        "env": "TRIBUTE_ALLO_URL",
    },
    "directing_fee": {
        "id": "directing_fee",
        "usd": None,
        "one_time": True,
        "tier": "directing",
        "file": False,
        "automated": False,
        "name_ru": "Directing · отдельно",
        "name_en": "Directing · separate",
        "gets_ru": "Один ход уже открытого контура. Не директолог и не рекламный кабинет.",
        "gets_en": "One stir of an already-open contour. Not a directologist and not an ad cabinet.",
        "env": "TRIBUTE_DIRECTING_URL",
    },
    "game_pack": {
        "id": "game_pack",
        "usd": 50,
        "tier": "isolated",
        "isolated": True,
        "file": False,
        "recurse_spec": False,
        "paper": True,
        "name_ru": "Игровой пакет · изолирован",
        "name_en": "Game pack · isolated",
        "gets_ru": "Paper / static. Не Allo. Не recurse_spec. Оффера, внедрения и коммерческого результата нет.",
        "gets_en": "Paper / static. Not Allo. Not recurse_spec. No offer help, no implementation, no commercial result.",
        "env": "TRIBUTE_GAME_URL",
    },
    "sku_100": {
        "id": "sku_100",
        "usd": 100,
        "rub": 9900,
        "tier": "micro",
        "file": False,
        "automated": True,
        "requests": 120,
        "days": 31,
        "name_ru": "$100 · кастом спека",
        "name_en": "$100 · custom spec",
        "custom_spec": True,
        "gets_ru": "Кастом спека: суть, решение, несколько вариантов. Каждый вариант — мелкая задача. Без кодовой рекурсии.",
        "gets_en": "Custom spec: essence, solution, several variants. Each variant is a small task. No code recursion.",
        "env": "TRIBUTE_SKU_100_URL",
    },
    "sku_490": {
        "id": "sku_490",
        "usd": 490,
        "rub": 45900,
        "tier": "assist",
        "file": True,
        "automated": True,
        "requests": 40,
        "days": 31,
        "name_ru": "$490 · рекурсия",
        "name_en": "$490 · recursion",
        "gets_ru": "Рекурсивная методика на том же слоте: bound, kill, library, monday. Файл и кодовая надстройка.",
        "gets_en": "Recursive methodology on the same slot: bound, kill, library, monday. File and code overlay.",
        "env": "TRIBUTE_SKU_490_URL",
    },
    "sku_1000": {
        "id": "sku_1000",
        "usd": 1000,
        "rub": 99000,
        "tier": "standard",
        "file": True,
        "automated": True,
        "requests": 80,
        "days": 90,
        "name_ru": "$1000 · стандарт",
        "name_en": "$1000 · standard",
        "gets_ru": "Разработка стандарта: рекурсивная методика + спеки + кодовая надстройка. Файл.",
        "gets_en": "Standard: recursive methodology + specs + code overlay. File.",
        "env": "TRIBUTE_SKU_1000_URL",
    },
    "sku_10000": {
        "id": "sku_10000",
        "usd": 10000,
        "rub": 990000,
        "tier": "contour",
        "file": True,
        "automated": False,
        "requests": 200,
        "days": 180,
        "name_ru": "$10 000 · автономный контур",
        "name_en": "$10 000 · autonomous contour",
        "gets_ru": "Дизайн автономного контура в ваш проект. Плотнее спеки, тот же контур. Файл.",
        "gets_en": "Autonomous contour designed into your project. Denser specs, same contour. File.",
        "env": "TRIBUTE_SKU_10000_URL",
    },
}

FREE_FACTS_RU = (
    "Хиты — смотреть бесплатно.\n"
    "Web3 Store — запросы бесплатно."
)
FREE_FACTS_EN = "Hits: view free.\nWeb3 Store: requests free."

PUBLIC_TABS = [
    {
        "id": "hits",
        "title": "Хиты",
        "title_en": "Hits",
        "title_short": "Хиты",
        "free": True,
        "one_liner": "Мувики, которые заслужили данные. Не сигнальный ассистент.",
        "accent": "#5eead4",
    },
    {
        "id": "flagship",
        "title": "Флагман",
        "title_en": "Flagship",
        "title_short": "Флагман",
        "free": True,
        "one_liner": "Суть и решение. Несколько вариантов. $100 — кастом спека, $490 — рекурсия.",
        "accent": "#38bdf8",
    },
    {
        "id": "store",
        "title": "Web3 Store",
        "title_en": "Web3 Store",
        "title_short": "Store",
        "free": True,
        "one_liner": "Заказы Web3 как входящий поток. Запросы бесплатно.",
        "accent": "#c4b5fd",
    },
    {
        "id": "tariffs",
        "title": "Тарифы",
        "title_en": "Tariffs",
        "title_short": "Тарифы",
        "free": True,
        "one_liner": "База $50 Allo. Directing отдельно. Верхние комнаты — рекурсия.",
        "accent": "#fbbf24",
    },
]


def _url_for(sku: str) -> str:
    meta = SKUS.get(sku) or {}
    env_name = meta.get("env") or ""
    raw = (os.getenv(env_name, "") if env_name else "").strip().rstrip("/")
    if raw:
        return raw
    if sku in ("allo_month", "directing_fee", "game_pack"):
        base = TRIBUTE_ACCESS_URL or TRIBUTE_CUSTOM_URL or "https://t.me/tribute"
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}start={sku}"
    if sku in ("sku_490", "sku_1000") and TRIBUTE_CUSTOM_URL:
        return TRIBUTE_CUSTOM_URL
    return TRIBUTE_ACCESS_URL or TRIBUTE_CUSTOM_URL or "https://t.me/tribute"


def sku_of(sid: str) -> dict[str, Any]:
    row = dict(SKUS.get(sid) or SKUS["free_life"])
    row["pay_url"] = _url_for(sid) if sid != "free_life" else ""
    return row


def _num(amount: Any) -> float | None:
    if amount is None or amount == "":
        return None
    if isinstance(amount, bool):
        return None
    if isinstance(amount, (int, float)):
        return float(amount)
    raw = str(amount).lower().replace(" ", "").replace(",", "").replace("$", "").replace("₽", "")
    raw = raw.replace("usd", "").replace("rub", "").replace("руб", "")
    match = re.search(r"\d+(?:\.\d+)?", raw)
    if not match:
        return None
    return float(match.group(0))


def _rub(amount: Any, name: str, currency: str) -> bool:
    cur = (currency or "").strip().lower()
    if cur in {"rub", "rur", "₽"}:
        return True
    blob = f"{amount} {name}".lower()
    return "₽" in str(amount) or "руб" in blob


def map_tribute_amount(amount: Any, name: str = "", currency: str = "") -> str:
    """Exact Tribute map. 50 USD is allo_month. 1000 must not eat 10000. No n >= 50 threshold."""
    text = str(name or "").lower()
    compact = re.sub(r"[\s,]", "", text)
    for sid in _EXPLICIT_IDS:
        if sid in text:
            return sid
    if any(k in text for k in ("game pack", "game_pack", "создание игры", "игровой пакет")):
        return "game_pack"
    if "directing_fee" in text or "directing fee" in text:
        return "directing_fee"
    if re.search(r"\ballo\b", text):
        return "allo_month"
    n = _num(amount)
    rub = _rub(amount, name, currency)
    if n == 3290:
        return "access_month"
    if rub and n == 45000:
        return "custom_spec_pilot"
    if rub and n == 80000:
        return "cross_assist"
    if n is not None and not rub:
        exact = SKU_BY_USD.get(int(n)) if float(n).is_integer() else None
        if exact:
            return exact
    if re.search(r"(?<!\d)10000(?!\d)", compact) or "10k" in text:
        return "sku_10000"
    if re.search(r"(?<!\d)1000(?!\d)", compact):
        return "sku_1000"
    if re.search(r"(?<!\d)490(?!\d)", compact):
        return "sku_490"
    if re.search(r"(?<!\d)100(?!\d)", compact) or re.search(r"(?<!\d)120(?!\d)", compact):
        return "sku_100"
    if not rub and re.search(r"(?<!\d)50(?!\d)", compact):
        return "allo_month"
    if "access" in text or "3290" in compact:
        return "access_month"
    return "unknown"


def tariff_board(lang: str = "ru") -> dict[str, Any]:
    ru = (lang or "ru").startswith("ru")
    paid = [sku_of(s) for s in ("sku_100", "sku_490", "sku_1000", "sku_10000")]
    free = sku_of("free_life")
    return {
        "tabs": PUBLIC_TABS,
        "free_facts": FREE_FACTS_RU if ru else FREE_FACTS_EN,
        "free_life": free,
        "base": sku_of("allo_month"),
        "directing": sku_of("directing_fee"),
        "isolated": [sku_of("game_pack")],
        "paid": paid,
        "human": HUMAN_CONTACT_URL or "https://x.com/karimmetrix",
        "flagship": {
            "usd": 490,
            "role_ru": (
                "База — Allo $50: дверь, чтение семи операций, грант запросов. "
                "Directing отдельно. Хиты и Store бесплатно. "
                "Верхние комнаты $100 / $490 / $1000 / $10 000 — рекурсия и спеки."
            ),
            "role_en": (
                "Base is Allo $50: door, seven operations, request grant. "
                "Directing is separate. Hits and Store are free. "
                "Upper rooms $100 / $490 / $1000 / $10000 stay for recursion and specs."
            ),
        },
        "note": (
            "Одна цена двери: $50 Allo. Directing — отдельно. "
            "После оплаты файл — на верхних комнатах, кроме $100. На $50 файла рекурсии нет."
            if ru
            else "One door price: $50 Allo. Directing is separate. Recursion file is an upper room, not $50."
        ),
    }
