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
        "id": "disagreement",
        "role": "Несогласие",
        "line": "Несогласие, которое назвали шумом, было началом собственной меры. Его можно сказать вслух без драки.",
        "consequence": "kill_branch",
    },
    {
        "id": "denial",
        "role": "Отрицание",
        "line": "Чужое «нет» не отменяет сделанную работу. Оно показывает, кто не стал слушать.",
        "consequence": "recurse_spec",
    },
    {
        "id": "unheard",
        "role": "Неуслышание",
        "line": "Неуслышание — не приговор. Это повод собрать стол, где фраза доходит до другого человека.",
        "consequence": "library_card",
    },
    {
        "id": "generation",
        "role": "Поколение",
        "line": "Держать объём, пока вокруг торгуют вниманием. Это не лозунг и не поза.",
        "consequence": "owner_monday",
    },
    {
        "id": "concept_ground",
        "role": "Концепт",
        "line": "Концепт не украшает решение. Он даёт место, на котором решение можно построить.",
        "consequence": "direct_next",
    },
    {
        "id": "together",
        "role": "Идея и инженерия",
        "line": "Идея без инженерии остаётся настроением. Инженерия без идеи остаётся станком. Они работают в одном месте.",
        "consequence": "individualize",
    },
    {
        "id": "real_data",
        "role": "Ценные данные",
        "line": "Ценное можно показать другому человеку без тумана: имя вещи и число, которое существует.",
        "consequence": "contribute",
    },
    {
        "id": "till",
        "role": "Касса человека",
        "line": "Таблица: что пришло, что должно, что можно заплатить. Это не обещание дохода.",
        "consequence": "plant_cash",
    },
    {
        "id": "bridge",
        "role": "Легальный мост",
        "line": "Кто отдал, кто принял, какая цифра. Если это нельзя показать другу — это не мост.",
        "consequence": "cut_support",
    },
    {
        "id": "volume",
        "role": "Объёмная закупка",
        "line": "Цель — объём, который можно купить и принять. Не витрина личности.",
        "consequence": "one_robot_paper",
    },
    {
        "id": "contract",
        "role": "Полузакрытый контракт",
        "line": "Двое названы, объём назван. Без сцены и без лекции.",
        "consequence": "isolate_freelance",
    },
    {
        "id": "archive",
        "role": "Прошлая схема",
        "line": "Дверь, консультация и пилот остаются в архиве. Публичный ход с 2.9 другой.",
        "consequence": "green",
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
    if science.get("version") != "2.9.1" or len(science.get("entries") or []) != len(SCIENCE):
        write_json(
            "science.json",
            {
                "version": "2.9.1",
                "codename": "VISION",
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
