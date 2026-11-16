"""OPS-7 from store_catalog + LINE_SPINE. FREE-12 closed. Science base above them."""

from __future__ import annotations

from typing import Any

from backend.core.pure_vehicle.store import read_json, write_json
from backend.core.seven_lines import LINE_SPINE
from backend.core.store_catalog import CATEGORIES

# Lines 4 and 5 have no dedicated engine. Line 2 is linked, not invented.
_ENGINE = {
    1: "backend.core.a2a_screener.steer",
    2: "backend.core.circle_system.deep_tech_pipeline.run_deep_tech_pipeline",
    3: "backend.core.craftshift_x.run",
    6: "backend.core.craftshift_x.run",
    7: "backend.core.terminal_ai.place",
}
_STUB = {4, 5}

FREE12: tuple[str, ...] = (
    "kill_branch",
    "plant_cash",
    "isolate_freelance",
    "library_card",
    "owner_monday",
    "cut_support",
    "one_robot_paper",
    "individualize",
    "green",
    "contribute",
    "direct_next",
    "recurse_spec",
)

FREE12_LINE: dict[str, str] = {
    "kill_branch": "Срезать мёртвую ветку. Новых комнат на ней нет.",
    "plant_cash": "Посадить на актив, который уже платит. Нет актива — отказ.",
    "isolate_freelance": "Пакет isolated. Дверь, Access и Allo не открывает.",
    "library_card": "Публичное чтение шаблона. Subject-hash. Без имени и телефона.",
    "owner_monday": "Хозяин слота и цифра понедельника. Не новый продукт.",
    "cut_support": "Срезать поддержку до минимума контура.",
    "one_robot_paper": "Бумажный прогон: py -3 -m robots scan all. Живого ордера нет.",
    "individualize": "Тот же шаблон в слот клиента. Короче. Не новый SKU.",
    "green": "Срезать мёртвые ветки и клише. Короче входа. Не ESG.",
    "contribute": "Шаблон в базу. Subject-hash. Коммерция без письма запрещена.",
    "direct_next": "Один следующий ход уже открытого контура. Не директолог.",
    "recurse_spec": "Плотнее спека без новой линейки. Закрыто на Allo $50.",
}

RECURSE_OPEN_SKUS = frozenset({"sku_490", "sku_1000", "sku_10000", "custom_spec_pilot"})

KILL = {
    "kill_branch": "Ветка закрыта. Дальше по ней комнат нет.",
    "plant_cash": "14 дней без движения денег — посадку вынуть.",
    "isolate_freelance": "Оплата пакета не открывает дверь.",
    "library_card": "Релицензирование запрещено. Запись остаётся персональной.",
    "owner_monday": "Нет имени хозяина или цифры понедельника — слот не ведут.",
    "cut_support": "Канал поддержки закрыт до минимума контура.",
    "one_robot_paper": "Режим не paper — прогон не запускать.",
    "individualize": "Пустой слот тикера или хозяина — экземпляр не писать.",
    "green": "Выход не короче входа — запись не принимать.",
    "contribute": "Имя, телефон или чужая лицензия — отказ.",
    "direct_next": "Без directing_fee выбор не записан.",
    "recurse_spec": "На Allo $50 файл рекурсии закрыт.",
}

# Two-line specs. 2026 senior IC → principal, USD. One consequence each.
SCIENCE: list[dict[str, Any]] = [
    {
        "id": "chief_contour_architect",
        "role": "Chief Contour Architect",
        "line": "Держит целостность IN/OUT/REALIZE по комнатам. Не добавляет восьмую операцию.",
        "band_usd": "180–240k",
        "consequence": "recurse_spec",
    },
    {
        "id": "recursion_spec_lead",
        "role": "Senior Recursion Spec Lead",
        "line": "Плотнит спеки, не увеличивая число продуктов. Файл только на верхних комнатах.",
        "band_usd": "160–210k",
        "consequence": "recurse_spec",
    },
    {
        "id": "paper_robot_operator",
        "role": "Paper Robot Operator",
        "line": "Гоняет robots scan all в paper. Живых ордеров из ядра нет.",
        "band_usd": "90–140k",
        "consequence": "one_robot_paper",
    },
    {
        "id": "greening_editor",
        "role": "Greening Editor",
        "line": "Коротит шаблон: мёртвые ветки и клише снимает. Не ESG.",
        "band_usd": "110–160k",
        "consequence": "green",
    },
    {
        "id": "freelance_curator",
        "role": "Isolated Freelance Pack Curator",
        "line": "Держит изолированные пакеты. Дверь и Allo не выдаёт.",
        "band_usd": "100–150k",
        "consequence": "isolate_freelance",
    },
    {
        "id": "science_steward",
        "role": "Scientific Base Steward",
        "line": "Публичный слой. Только subject-hash. LICENSE не переписывает.",
        "band_usd": "130–180k",
        "consequence": "contribute",
    },
    {
        "id": "library_keeper",
        "role": "Library Card Keeper",
        "line": "Публичное чтение карточки. Имени и телефона в записи нет.",
        "band_usd": "95–140k",
        "consequence": "library_card",
    },
    {
        "id": "cash_landing_analyst",
        "role": "Cash Landing Analyst",
        "line": "Сажает линию 7 на актив, который уже платит. Нет актива — отказ.",
        "band_usd": "150–200k",
        "consequence": "plant_cash",
    },
    {
        "id": "kill_editor",
        "role": "Kill-Condition Editor",
        "line": "Пишет OUT, который закрывает ветку. Новую линейку не открывает.",
        "band_usd": "120–170k",
        "consequence": "kill_branch",
    },
    {
        "id": "monday_owner",
        "role": "Monday Owner",
        "line": "Слот хозяина и цифра понедельника. Process OS, не второй продукт.",
        "band_usd": "140–190k",
        "consequence": "owner_monday",
    },
    {
        "id": "support_cutter",
        "role": "Support Cutter",
        "line": "Снимает канал поддержки до уже заданного минимума контура.",
        "band_usd": "105–155k",
        "consequence": "cut_support",
    },
    {
        "id": "slot_individualizer",
        "role": "Slot Individualizer",
        "line": "Сажает шаблон в тикер и хозяина. Экземпляр короче исходника.",
        "band_usd": "115–165k",
        "consequence": "individualize",
    },
    {
        "id": "directing_fixer",
        "role": "Directing Fixer",
        "line": "После directing_fee фиксирует один ход и один kill. Не рекламный кабинет.",
        "band_usd": "145–195k",
        "consequence": "direct_next",
    },
    {
        "id": "instrument_lead",
        "role": "Instrumentation Systems Lead",
        "line": "Научный прибор как один контур. Восьмую операцию не заводит.",
        "band_usd": "155–210k",
        "consequence": "direct_next",
    },
    {
        "id": "game_systems",
        "role": "Game Systems Designer",
        "line": "Бумажный круг игры. От двери $50 отделён. Результат не обещает.",
        "band_usd": "130–180k",
        "consequence": "isolate_freelance",
    },
    {
        "id": "ops_research_seat",
        "role": "Operations Research Seat",
        "line": "Один kill и одна цифра понедельника. Не каталог идей.",
        "band_usd": "150–205k",
        "consequence": "kill_branch",
    },
]


def ops() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cat in CATEGORIES:
        n = int(cat["n"])
        stub = n in _STUB
        rows.append(
            {
                "n": n,
                "id": cat["id"],
                "title": cat["title"],
                "title_en": cat["title_en"],
                "spine": LINE_SPINE.get(n) or "",
                "engine": None if stub else _ENGINE.get(n),
                "stub": stub,
                "landed": not stub,
                "sell_as_ready": not stub,
            }
        )
    if len(rows) != 7:
        raise RuntimeError("OPS-7 must stay seven")
    return rows


OPS = ops()


def ops_by_n(n: int) -> dict[str, Any]:
    for row in OPS:
        if row["n"] == int(n):
            return dict(row)
    raise KeyError(n)


def ensure_stores() -> None:
    current = read_json("ops7.json", {})
    if current.get("version") != "2.1.0" or len(current.get("ops") or []) != 7:
        write_json("ops7.json", {"version": "2.1.0", "codename": "PURE VEHICLE", "ops": OPS})
    free = read_json("free12.json", {})
    if free.get("ids") != list(FREE12):
        write_json(
            "free12.json",
            {
                "version": "2.1.0",
                "ids": list(FREE12),
                "lines": FREE12_LINE,
                "recurse_open_skus": sorted(RECURSE_OPEN_SKUS),
            },
        )
    science = read_json("science.json", {})
    if science.get("version") != "2.1.0" or len(science.get("entries") or []) != len(SCIENCE):
        write_json(
            "science.json",
            {
                "version": "2.1.0",
                "codename": "PURE VEHICLE",
                "layer": "scientific_base",
                "eighth_product": False,
                "entries": SCIENCE,
            },
        )


def science_base() -> dict[str, Any]:
    ensure_stores()
    return read_json("science.json", {"entries": SCIENCE, "version": "2.1.0"})


def recurse_status(sku: str) -> dict[str, Any]:
    if sku in RECURSE_OPEN_SKUS:
        return {"id": "recurse_spec", "open": True, "sku": sku}
    return {
        "id": "recurse_spec",
        "open": False,
        "sku": sku,
        "why": (
            "recurse_spec закрыт на этом слоте. "
            "Открыт только на sku_490, sku_1000, sku_10000, custom_spec_pilot. "
            "Allo $50 файл рекурсии не открывает."
        ),
    }


def open_consequences(sku: str) -> list[str]:
    if sku in RECURSE_OPEN_SKUS:
        return list(FREE12)
    return [cid for cid in FREE12 if cid != "recurse_spec"]
