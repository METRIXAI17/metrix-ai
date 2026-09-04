"""Five engine modes → sellable artefacts. Concrete, short, no private voice."""

from __future__ import annotations

from typing import Any

from backend.core.engine_run import config_from_engine, run_engine
from backend.core.resonance import new_id, remember
from backend.core.sales_modes import section_by_id
from backend.core.voice import DISCLAIMER, clip, first_sentence


def _base(sec: dict[str, Any], brief: str, kind: str) -> dict[str, Any]:
    return {
        "id": new_id(),
        "kind": kind,
        "lane": sec["id"],
        "mode": sec["mode"],
        "title": sec["title"],
        "one_liner": sec["one_liner"],
        "disclaimer": DISCLAIMER,
        "brief": clip(brief, 400),
        "highway": {"free": "этот результат", "paid": "Access", "sku": "access_month"},
    }


def run_life(brief: str) -> dict[str, Any]:
    sec = section_by_id("life") or {}
    text = (brief or "").strip() or "день тяжёлый, не знаю с чего начать"
    pack = run_engine(text, industry=sec.get("industry") or "expert-services", lang="ru")
    sit = first_sentence(text, "день")
    ideas = []
    if pack.get("idea_title"):
        ideas.append(pack["idea_title"])
    for s in pack.get("next_steps") or []:
        ideas.append(str(s))
    if not ideas:
        ideas = [
            "Один конкретный шаг на сегодня, не план на месяц.",
            "Что убрать из дня, чтобы стало легче — не что добавить.",
            "Где деньги или сон ломаются первым — туда одна правка.",
        ]
    art = _base(sec, text, "mode.life")
    art.update(
        {
            "title": "Идеи для жизни",
            "break": f"Сейчас: «{clip(sit, 90)}». Нет одного шага — день размазан.",
            "move": "Чат даёт короткие улучшения. Не терапия, не курс.",
            "steps": [clip(x, 180) for x in ideas[:5]],
            "artifact_week": "3 идеи на неделю. Одна обязательная на сегодня.",
            "anti": ["Не превращать в дневник.", "Не обещать здоровье или доход."],
            "meta": {"engine": "metrix_ai", "engine_ok": bool(pack.get("ok")), "request_id": pack.get("request_id") or ""},
        }
    )
    remember(art)
    return art


def run_craft(brief: str) -> dict[str, Any]:
    sec = section_by_id("craft") or {}
    text = (brief or "").strip() or "ремесло на заказ, сроки плывут"
    pack = run_engine(text, industry=sec.get("industry") or "expert-services", lang="ru")
    cfg = config_from_engine(pack, niche="agency")
    art = _base(sec, text, "mode.craft")
    slots = cfg.get("slots") or {}
    steps = cfg.get("steps") or [
        "Имя изделия.",
        "Материал и себестоимость.",
        "Срок сдачи.",
        "Когда молчать клиенту.",
        "Цена и kill, если заказ не оплачен.",
    ]
    art.update(
        {
            "title": "Конфиг для ремесла",
            "break": "Без конфига каждый заказ — геройство. Маржа сгорает на уточнениях.",
            "move": cfg.get("blurb") or "Файл заказа: изделие, материал, срок, цена, молчание.",
            "steps": [str(s) for s in steps][:6],
            "artifact_week": "Один конфиг на живой заказ. Повтор — тот же файл, другие цифры.",
            "anti": ["Не писать брендбук.", "Не делать чат вместо конфига."],
            "meta": {
                "engine": "metrix_ai",
                "engine_ok": bool(cfg.get("ok")),
                "config": cfg,
                "slots": slots,
                "request_id": cfg.get("request_id") or pack.get("request_id") or "",
            },
        }
    )
    remember(art)
    return art


def run_target(brief: str) -> dict[str, Any]:
    sec = section_by_id("target") or {}
    text = (brief or "").strip() or "нужно куда целить агента"
    pack = run_engine(text, industry=sec.get("industry") or "ai-agencies", lang="ru")
    art = _base(sec, text, "mode.target")
    steps = pack.get("next_steps") or [
        "Кто платит агенту — имя роли, не «все».",
        "Где они уже есть — канал.",
        "Какой текст агент имеет право сказать.",
        "Когда агент молчит.",
        "Kill: 14 дней без ответа — выключить.",
    ]
    art.update(
        {
            "title": "Таргет ИИ-агента",
            "break": "Агент без цели пишет всем. Это не таргет, это шум.",
            "move": pack.get("idea_title") or "Одна роль, один канал, один текст, одно молчание.",
            "steps": [str(s) for s in steps][:5],
            "artifact_week": "Карточка таргета: роль · канал · текст · молчание · kill.",
            "anti": ["Не целиться в «рынок целиком».", "Не путать таргет с промптом чата."],
            "meta": {"engine": "metrix_ai", "engine_ok": bool(pack.get("ok")), "request_id": pack.get("request_id") or ""},
        }
    )
    remember(art)
    return art


def run_shop(brief: str) -> dict[str, Any]:
    sec = section_by_id("shop") or {}
    text = (brief or "").strip() or "физический товар без понятного момента покупки"
    pack = run_engine(text, industry=sec.get("industry") or "ecommerce", lang="ru")
    sit = first_sentence(text, "товар")
    art = _base(sec, text, "mode.shop")
    art.update(
        {
            "title": "Карточка каталога",
            "break": f"«{clip(sit, 80)}» без момента нужды — витрина обои.",
            "move": pack.get("idea_title") or "Уникальное имя, описание, когда человеку это нужно.",
            "steps": [
                "Имя товара — одно, своё.",
                "Описание: что в руках, не «премиум качество».",
                "Когда нужно: ситуация, не сезон в рекламе.",
                "Кому не нужно — тоже написать.",
            ],
            "artifact_week": "1 карточка каталога: имя · описание · момент нужды.",
            "anti": ["Не копировать чужой каталог.", "Не обещать доход с витрины."],
            "meta": {"engine": "metrix_ai", "engine_ok": bool(pack.get("ok")), "request_id": pack.get("request_id") or ""},
            "catalog_card": {
                "name": pack.get("idea_title") or clip(sit, 48),
                "description": clip(str(pack.get("idea_blurb") or text), 220),
                "when_needed": (pack.get("next_steps") or ["когда старый предмет сломался или кончился"])[0],
            },
        }
    )
    remember(art)
    return art


def run_trading_prompt(prompt: str, strategy: str | None = None) -> dict[str, Any]:
    """No-code experiment: plain-language prompt + strategy + rating hooks."""
    from backend.core.strategies import run_strategy, resolve_strategy

    text = (prompt or "").strip() or "проверить модель как есть"
    sid = resolve_strategy(strategy, text)
    body = run_strategy(sid, text)
    body["kind"] = "mode.trading_experiment"
    body["lane"] = "bots"
    body["mode"] = "trading"
    body["prompt"] = clip(text, 800)
    meta = dict(body.get("meta") or {})
    meta["no_code"] = True
    meta["prompt"] = clip(text, 800)
    meta["engine"] = "metrix_ai"
    body["meta"] = meta
    body["anti"] = list(body.get("anti") or []) + ["Не вставлять код. Только фраза про правило."]
    remember(body)
    return body


def run_mode(section_id: str, brief: str, *, strategy: str | None = None) -> dict[str, Any]:
    sec = section_by_id(section_id)
    sid = (sec or {}).get("id") or "life"
    if sid == "bots":
        return run_trading_prompt(brief, strategy)
    if sid == "craft":
        return run_craft(brief)
    if sid == "target":
        return run_target(brief)
    if sid == "shop":
        return run_shop(brief)
    return run_life(brief)
