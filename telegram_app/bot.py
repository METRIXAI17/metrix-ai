"""
Karim Metrix bot — conversation first, Mini App second.

Env: TELEGRAM_BOT_TOKEN, TELEGRAM_WEBAPP_URL, METRIX_PUBLIC_URL
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import HUMAN_CONTACT_URL, TRIBUTE_ACCESS_URL, TRIBUTE_CUSTOM_URL
from backend.core.access import consume, is_entitled, redeem, subject_hash
from backend.core.agent_studio import list_niches
from backend.core.demo_highway import (
    build_demo,
    format_almost_prompt,
    format_hit,
    format_miss,
    format_telegram,
)
from backend.core.resonance import load as load_art
from backend.core.resonance import resonate
from backend.core.strategies import list_strategies
from backend.core.teammates import list_teammates, workflow_payload
from backend.core.x_posts import list_posts
from backend.core.voice import IDLE_HINT
from telegram_app import sessions
from telegram_app import texts
from telegram_app.menu import menu_action

HERE = Path(__file__).resolve().parent
AVATAR = HERE / "avatar.jpg"
MARK = ROOT / "public" / "tg" / "assets" / "mark.jpg"
PHOTO_ROOT = ROOT / "public" / "assets" / "x-posts"
SECTION_PHOTO = {
    "start": PHOTO_ROOT / "geo-start.jpg",
    "life": ROOT / "public" / "tg" / "assets" / "sec-life.jpg",
    "bots": ROOT / "public" / "tg" / "assets" / "sec-bots.jpg",
    "craft": ROOT / "public" / "tg" / "assets" / "sec-craft.jpg",
    "target": ROOT / "public" / "tg" / "assets" / "sec-target.jpg",
    "shop": ROOT / "public" / "tg" / "assets" / "sec-shop.jpg",
    "store": ROOT / "public" / "assets" / "store" / "hero.jpg",
    "shift": ROOT / "public" / "assets" / "store" / "craft.jpg",
    "door": ROOT / "public" / "assets" / "studio-square.jpg",
    "chain": ROOT / "public" / "tg" / "assets" / "sec-life.jpg",
    "teammates": ROOT / "public" / "tg" / "assets" / "sec-craft.jpg",
    "artefacts": ROOT / "public" / "tg" / "assets" / "sec-shop.jpg",
    "target_place": PHOTO_ROOT / "geo-gold.jpg",
    "demand": PHOTO_ROOT / "geo-demand.jpg",
    "ampli": PHOTO_ROOT / "geo-ampli.jpg",
    "two_leg_tape": PHOTO_ROOT / "geo-tape.jpg",
    "risk": PHOTO_ROOT / "geo-risk.jpg",
}


def _load_dotenv() -> None:
    p = ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def _token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def _webapp() -> str:
    # Mini App is static on Vercel. Don't inherit METRIX_PUBLIC_URL (Railway API) —
    # that made the Telegram button open a dead /tg/ whenever the API host was down.
    raw = os.getenv("TELEGRAM_WEBAPP_URL", "").strip() or "https://metrix-ai.vercel.app/tg/"
    if not raw.endswith("/"):
        raw += "/"
    return raw


def main_keyboard() -> dict:
    return {
        "keyboard": [
            [{"text": texts.MENU_LIFE}, {"text": texts.MENU_STORE}],
            [{"text": texts.MENU_SHIFT}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def webapp_row(webapp: str) -> list[dict]:
    url = webapp if "#" in webapp else webapp.rstrip("/") + "/#store"
    return [{"text": "Открыть стор", "web_app": {"url": url}}]


def _tribute_url() -> str:
    return TRIBUTE_ACCESS_URL or "https://t.me/tribute"


def _human_url() -> str:
    return HUMAN_CONTACT_URL or "https://x.com/karimmetrix"


def subscribe_row() -> list[dict]:
    return [{"text": "Access · 3 290 ₽", "url": _tribute_url()}]


def human_row() -> list[dict]:
    return [{"text": "Связаться с человеком", "url": _human_url()}]


def nav_inline(webapp: str, *, extra: list | None = None) -> dict:
    """Primary nav — three sections. Reply keyboard is a fallback; Telegram often hides it."""
    rows = [
        [
            {"text": "Разговор", "callback_data": "m:life"},
            {"text": "Стор", "callback_data": "m:store"},
        ],
        [
            {"text": "CraftShift", "callback_data": "m:shift"},
            {"text": "Дверь", "callback_data": "m:door"},
        ],
        [{"text": "Ещё 5 комнат", "callback_data": "m:more"}],
        webapp_row(webapp),
        subscribe_row(),
        [{"text": "X · @karimmetrix", "url": "https://x.com/karimmetrix"}],
    ]
    if extra:
        rows = extra + rows
    return {"inline_keyboard": rows}


def start_inline(webapp: str) -> dict:
    return nav_inline(webapp)


def resonance_kb(artifact_id: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "Зашло", "callback_data": f"rs:hit:{artifact_id}"},
                {"text": "Почти", "callback_data": f"rs:almost:{artifact_id}"},
                {"text": "Мимо", "callback_data": f"rs:miss:{artifact_id}"},
            ],
            [{"text": "Подумать ещё", "callback_data": f"tm:{artifact_id}"}],
        ]
    }


def strategies_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Target Place · золото", "callback_data": "st:target_place"}],
            [{"text": "Demand · крипта", "callback_data": "st:demand"}],
            [{"text": "Ampli · Америка", "callback_data": "st:ampli"}],
            [{"text": "Two-Leg Tape · Tape Land", "callback_data": "st:two_leg_tape"}],
            [{"text": "Как сейчас · живой снимок (не списывает)", "callback_data": "lv:now"}],
            [{"text": "Стоп на перемене · не сливать бюджет", "callback_data": "ss:now"}],
            [{"text": "Контроль рисков · отдельно", "callback_data": "rk:engine"}],
        ]
    }


def niches_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "IT Desk · внедрение", "callback_data": "ag:saas"}],
            [{"text": "Production Geometry · продакшн", "callback_data": "ag:agency"}],
            human_row(),
        ]
    }


def posts_kb() -> dict:
    rows = []
    for p in list_posts():
        rows.append([{"text": p["theme"], "callback_data": f"xp:{p['id']}"}])
    return {"inline_keyboard": rows}


class BotAPI:
    def __init__(self, token: str) -> None:
        self.base = f"https://api.telegram.org/bot{token}"
        self.client = httpx.Client(timeout=70)

    def call(self, method: str, **payload):
        r = self.client.post(f"{self.base}/{method}", json=payload)
        try:
            data = r.json()
        except Exception:
            data = {"ok": False, "error": r.text[:200]}
        if not data.get("ok"):
            print("tg error", method, data)
        return data

    def send(
        self,
        chat_id: int,
        text: str,
        *,
        markup: dict | None = None,
        html: bool = True,
    ) -> dict:
        payload: dict = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        if html:
            payload["parse_mode"] = "HTML"
        if markup:
            payload["reply_markup"] = markup
        data = self.call("sendMessage", **payload)
        if not data.get("ok") and html:
            payload.pop("parse_mode", None)
            data = self.call("sendMessage", **payload)
        return data

    def send_photo(
        self,
        chat_id: int,
        path: Path,
        caption: str = "",
        *,
        markup: dict | None = None,
        html: bool = True,
    ) -> dict:
        if not path or not path.exists():
            return self.send(chat_id, caption or "…", markup=markup, html=html)
        data: dict = {"chat_id": str(chat_id)}
        cap = (caption or "")[:1024]
        if cap:
            data["caption"] = cap
            if html:
                data["parse_mode"] = "HTML"
        if markup:
            data["reply_markup"] = json.dumps(markup)
        with path.open("rb") as f:
            r = self.client.post(
                f"{self.base}/sendPhoto",
                data=data,
                files={"photo": (path.name, f, "image/jpeg")},
            )
        try:
            out = r.json()
        except Exception:
            out = {"ok": False}
        if not out.get("ok") and html:
            data.pop("parse_mode", None)
            with path.open("rb") as f:
                r = self.client.post(
                    f"{self.base}/sendPhoto",
                    data=data,
                    files={"photo": (path.name, f, "image/jpeg")},
                )
            try:
                out = r.json()
            except Exception:
                out = {"ok": False}
        if not out.get("ok"):
            print("tg error sendPhoto", out)
            return self.send(chat_id, caption or "…", markup=markup, html=html)
        return out

    def send_start(self, chat_id: int, webapp: str) -> None:
        from backend.core.door import mint, public_view

        rec = mint("разговор", room="talk")
        sessions.set_mode(chat_id, "idle", door=rec["code"])
        photo = SECTION_PHOTO.get("store") or SECTION_PHOTO["start"]
        if not photo.exists():
            photo = SECTION_PHOTO["start"]
        if not photo.exists():
            photo = AVATAR if AVATAR.exists() else MARK
        kb = start_inline(webapp)
        cap = texts.START + f"\n\nДверь <code>{rec['code']}</code> — стор, CraftShift, сайт."
        sent = self.send_photo(chat_id, photo, cap)
        if sent.get("ok"):
            self.send(
                chat_id,
                IDLE_HINT,
                markup=main_keyboard(),
                html=False,
            )
            self.send(
                chat_id,
                "Один код. Стор. CraftShift. Кнопки под этим сообщением.",
                markup=kb,
                html=False,
            )
            return
        self.send(chat_id, texts.START, markup=main_keyboard())
        self.send(
            chat_id,
            "In-Out Chain · AI Teammates · Artefacts — кнопки под этим сообщением.",
            markup=kb,
            html=False,
        )


def bootstrap(api: BotAPI, webapp: str) -> None:
    api.call(
        "setChatMenuButton",
        menu_button={"type": "web_app", "text": "Стор", "web_app": {"url": webapp + "#store"}},
    )
    api.call(
        "setMyCommands",
        commands=[
            {"command": "start", "description": "Дверь"},
            {"command": "life", "description": "Разговор"},
            {"command": "store", "description": "Metrix Store"},
            {"command": "shift", "description": "CraftShift"},
            {"command": "door", "description": "Код двери"},
            {"command": "access", "description": "Access · 3 290 ₽"},
        ],
    )
    api.call("setMyDescription", description=texts.DESC)
    api.call("setMyShortDescription", short_description=texts.SHORT)
    api.call("setMyName", name=texts.NAME)


def _send_artifact(api: BotAPI, chat_id: int, art: dict) -> None:
    sessions.set_mode(
        chat_id,
        "await_feedback",
        last_artifact_id=art.get("id"),
        closer_id=art.get("closer_id"),
        last_engine_brief=art.get("engine_brief") or "",
    )
    essay = art.get("abstraction") or {}
    if essay.get("essay"):
        from backend.core.content_closer import format_abstraction_telegram

        raw = format_abstraction_telegram(essay)
        if len(raw) > 3900:
            raw = raw[:3890] + "…"
        api.send(chat_id, raw)
    api.send(chat_id, format_telegram(art), markup=resonance_kb(art["id"]))


def _gate(api: BotAPI, chat_id: int, feature: str, webapp: str) -> bool:
    sub = subject_hash(chat_id)
    gate = consume(sub, feature)
    if gate.get("allowed"):
        return True
    extra = [subscribe_row()]
    msg = texts.ASK_MONTH_CAP if gate.get("reason") == "month_cap" else texts.ASK_ACCESS
    api.send(chat_id, msg, markup=nav_inline(webapp, extra=extra), html=False)
    return False


def _run_section(api: BotAPI, chat_id: int, section: str, brief: str, **kw) -> None:
    from backend.core.mode_surfaces import run_mode

    feat = {
        "life": "life",
        "bots": "trading_prompt",
        "craft": "craft",
        "target": "target",
        "shop": "shop",
    }.get(section, "life")
    if kw.pop("watch", False):
        feat = "watch"
    if not _gate(api, chat_id, feat, _webapp()):
        return
    api.send(chat_id, "Собираю…")
    try:
        art = run_mode(section, brief, strategy=kw.get("strategy"))
    except Exception as exc:  # noqa: BLE001
        api.send(chat_id, f"Сломалось. Напишите короче.\n<code>{exc}</code>"[:400])
        return
    _send_artifact(api, chat_id, art)


def _run_demo(api: BotAPI, chat_id: int, brief: str, **kw) -> None:
    hint = (kw.get("hint") or "").lower()
    if hint in ("life", "landing", "chain"):
        _run_section(api, chat_id, "life", brief)
        return
    if hint in ("bots", "strategy") or kw.get("strategy"):
        _run_section(api, chat_id, "bots", brief, strategy=kw.get("strategy"), watch=kw.get("watch", False))
        return
    if hint in ("craft", "engine", "teammates", "agent"):
        _run_section(api, chat_id, "craft" if hint != "target" else "target", brief)
        return
    if hint == "target":
        _run_section(api, chat_id, "target", brief)
        return
    if hint in ("shop", "making", "artefacts"):
        _run_section(api, chat_id, "shop", brief)
        return
    if kw.pop("watch", False):
        feature = "watch"
    elif kw.get("strategy") or kw.get("hint") == "strategy":
        feature = "strategy"
    elif kw.get("niche") or kw.get("hint") in ("agent", "teammates"):
        feature = "teammate"
    else:
        feature = "life"
    if not _gate(api, chat_id, feature, _webapp()):
        return
    api.send(chat_id, "Собираю…")
    try:
        art = build_demo(brief, **kw)
    except ValueError as exc:
        api.send(chat_id, str(exc))
        return
    except Exception as exc:  # noqa: BLE001
        api.send(chat_id, f"Сломалось на сборке. Напишите ещё раз короче.\n<code>{exc}</code>"[:500])
        return
    _send_artifact(api, chat_id, art)


def _esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def show_strategies(api: BotAPI, chat_id: int, webapp: str) -> None:
    lines = ["<b>Четыре модели. Код, не сигналы.</b> Риск-движок — отдельно.\n"]
    for s in list_strategies():
        lines.append(
            f"<b>{_esc(s['name'])}</b> · {_esc(s['market'])}\n"
            f"{_esc(s['one_liner'])}\n"
            f"<i>{_esc(s['for_whom'])}</i>\n"
        )
    extra = strategies_kb()["inline_keyboard"]
    api.send(chat_id, "\n".join(lines), markup=nav_inline(webapp, extra=extra))


def show_agents(api: BotAPI, chat_id: int, webapp: str) -> None:
    lines = ["<b>AI Teammates.</b> Тимейт держит финмодель, не болтает.\n"]
    for n in list_teammates():
        lines.append(f"<b>{_esc(n['codename'])}</b> · {_esc(n['title'])}\n{_esc(n['user_facing'])}\n")
    wf = workflow_payload()
    lines.append("<b>Воркфлоу нового решения</b>")
    for step in wf["steps"]:
        lines.append(f"· {_esc(step['title'])}: {_esc(step['do'])}")
    extra = niches_kb()["inline_keyboard"]
    api.send(chat_id, "\n".join(lines), markup=nav_inline(webapp, extra=extra))


def show_posts(api: BotAPI, chat_id: int, webapp: str) -> None:
    extra = posts_kb()["inline_keyboard"]
    api.send(chat_id, texts.POSTS_INTRO, markup=nav_inline(webapp, extra=extra))


def show_life(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_life")
    api.send_photo(
        chat_id,
        SECTION_PHOTO["life"],
        texts.ASK_LIFE,
        markup=nav_inline(webapp),
        html=False,
    )


def show_bots(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_bots")
    extra = strategies_kb()["inline_keyboard"]
    api.send_photo(
        chat_id,
        SECTION_PHOTO["bots"],
        texts.ASK_BOTS,
        markup=nav_inline(webapp, extra=extra),
        html=False,
    )


def show_chain(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_life(api, chat_id, webapp)


def show_landing(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_chain(api, chat_id, webapp)


def show_craft(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_craft")
    api.send_photo(
        chat_id,
        SECTION_PHOTO["craft"],
        texts.ASK_CRAFT,
        markup=nav_inline(webapp),
        html=False,
    )


def show_target(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_target")
    api.send_photo(
        chat_id,
        SECTION_PHOTO["target"],
        texts.ASK_TARGET,
        markup=nav_inline(webapp),
        html=False,
    )


def show_teammates(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_craft(api, chat_id, webapp)


def show_engine(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_teammates(api, chat_id, webapp)


def show_shop(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_shop")
    api.send_photo(
        chat_id,
        SECTION_PHOTO["shop"],
        texts.ASK_SHOP,
        markup=nav_inline(webapp),
        html=False,
    )


def show_artefacts(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_shop(api, chat_id, webapp)


def show_hits(api: BotAPI, chat_id: int, webapp: str) -> None:
    from telegram_app.hits import format_hit, glossary, weekly_hit

    hit = weekly_hit(int(time.time() // 86400 // 7))
    extra = {
        "inline_keyboard": [
            [{"text": "Глоссарий", "callback_data": "ht:gloss"}],
            [{"text": "Обучение", "callback_data": "ht:sub"}],
            [{"text": "Приватка", "callback_data": "ht:priv"}],
        ]
    }
    api.send(chat_id, format_hit(hit), markup=nav_inline(webapp, extra=extra["inline_keyboard"]))


def show_sub(api: BotAPI, chat_id: int, webapp: str) -> None:
    from telegram_app.subscription import format_tier

    api.send(
        chat_id,
        format_tier("free") + "\n\n" + format_tier("paid"),
        markup=nav_inline(webapp),
    )


def show_private(api: BotAPI, chat_id: int, webapp: str) -> None:
    from telegram_app.subscription import format_tier

    api.send(chat_id, format_tier("private"), markup=nav_inline(webapp))


def _door_of(chat_id: int, brief: str = "", room: str = "talk") -> str:
    from backend.core.door import bind, mint

    st = sessions.load(chat_id)
    code = st.get("door") or ""
    if code:
        rec = bind(code, brief=brief, room=room)
        sessions.set_mode(chat_id, st.get("mode") or "idle", door=rec["code"])
        return rec["code"]
    rec = mint(brief, room=room)
    sessions.set_mode(chat_id, st.get("mode") or "idle", door=rec["code"])
    return rec["code"]


def store_kb() -> dict:
    from backend.core.store_catalog import CATEGORIES

    rows = []
    row: list[dict] = []
    for c in CATEGORIES:
        row.append({"text": f"{c['n']}. {c['title']}", "callback_data": f"stc:{c['n']}"})
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return {"inline_keyboard": rows}


def show_store(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_store", door=_door_of(chat_id, room="store"))
    extra = store_kb()["inline_keyboard"]
    photo = SECTION_PHOTO.get("store") or SECTION_PHOTO["shop"]
    api.send_photo(
        chat_id,
        photo,
        texts.ASK_STORE,
        markup=nav_inline(webapp, extra=extra),
        html=False,
    )


def show_shift(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_shift", door=_door_of(chat_id, room="craftshift"))
    photo = SECTION_PHOTO.get("shift") or SECTION_PHOTO["craft"]
    api.send_photo(
        chat_id,
        photo,
        texts.ASK_SHIFT,
        markup=nav_inline(webapp),
        html=False,
    )


def show_door(api: BotAPI, chat_id: int, webapp: str) -> None:
    code = _door_of(chat_id, room="talk")
    sessions.set_mode(chat_id, "await_door", door=code)
    api.send(
        chat_id,
        f"{texts.ASK_DOOR}\n\nВаш код: <code>{code}</code>\nСайт: https://metrix-ai.vercel.app/store/?door={code}",
        markup=nav_inline(webapp),
    )


def show_more(api: BotAPI, chat_id: int, webapp: str) -> None:
    extra = [
        [
            {"text": "Торговые боты", "callback_data": "m:bots"},
            {"text": "Ремесло", "callback_data": "m:craft"},
        ],
        [
            {"text": "Агенты", "callback_data": "m:target"},
            {"text": "Каталог товара", "callback_data": "m:shop"},
        ],
    ]
    api.send(chat_id, "Старые пять комнат — если нужны.", markup=nav_inline(webapp, extra=extra), html=False)


def show_making(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_artefacts(api, chat_id, webapp)


def show_access(api: BotAPI, chat_id: int, webapp: str) -> None:
    extra = [subscribe_row(), human_row()]
    api.send(chat_id, texts.ASK_ACCESS, markup=nav_inline(webapp, extra=extra), html=False)


def show_demo_prompt(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_chain(api, chat_id, webapp)


def dispatch_menu(api: BotAPI, chat_id: int, action: str, webapp: str) -> None:
    if action == "start":
        sessions.set_mode(chat_id, "idle")
        api.send_start(chat_id, webapp)
        return
    if action == "help":
        api.send(chat_id, texts.HELP, markup=nav_inline(webapp), html=False)
        return
    if action == "access":
        show_access(api, chat_id, webapp)
        return
    if action in ("life", "chain", "landing", "demo"):
        show_life(api, chat_id, webapp)
        return
    if action in ("bots", "strategies"):
        show_bots(api, chat_id, webapp)
        return
    if action in ("craft", "teammates", "engine"):
        show_craft(api, chat_id, webapp)
        return
    if action in ("target", "agents"):
        show_target(api, chat_id, webapp)
        return
    if action in ("shop", "artefacts", "making", "posts"):
        show_artefacts(api, chat_id, webapp)
        return
    if action == "store":
        show_store(api, chat_id, webapp)
        return
    if action == "shift":
        show_shift(api, chat_id, webapp)
        return
    if action == "door":
        show_door(api, chat_id, webapp)
        return
    if action == "more":
        show_more(api, chat_id, webapp)
        return
    if action == "hits":
        show_hits(api, chat_id, webapp)
        return
    if action == "sub":
        show_sub(api, chat_id, webapp)
        return
    if action == "private":
        show_private(api, chat_id, webapp)
        return


def handle_callback(api: BotAPI, cq: dict, webapp: str) -> None:
    cid = cq.get("id")
    data = (cq.get("data") or "").strip()
    msg = cq.get("message") or {}
    from_user = cq.get("from") or {}
    chat_id = (msg.get("chat") or {}).get("id") or from_user.get("id")
    api.call("answerCallbackQuery", callback_query_id=cid)
    if not chat_id:
        return
    if data.startswith("m:"):
        action = {
            "life": "life",
            "chain": "life",
            "landing": "life",
            "demo": "life",
            "bots": "bots",
            "teammates": "craft",
            "engine": "craft",
            "craft": "craft",
            "strat": "bots",
            "strategies": "bots",
            "target": "target",
            "agents": "target",
            "shop": "shop",
            "artefacts": "shop",
            "making": "shop",
            "posts": "shop",
            "store": "store",
            "shift": "shift",
            "door": "door",
            "more": "more",
            "access": "access",
            "hits": "hits",
            "sub": "sub",
            "private": "private",
        }.get(data.split(":", 1)[1])
        if action:
            dispatch_menu(api, chat_id, action, webapp)
        return
    if data.startswith("ht:"):
        kind = data.split(":", 1)[1]
        if kind == "gloss":
            from telegram_app.hits import glossary

            api.send(chat_id, glossary(), markup=nav_inline(webapp))
        elif kind == "sub":
            show_sub(api, chat_id, webapp)
        else:
            show_private(api, chat_id, webapp)
        return
    if data.startswith("rs:"):
        _, verdict, aid = (data.split(":", 2) + ["", ""])[:3]
        out = resonate(aid, verdict)
        art = out.get("artifact") or load_art(aid) or {}
        if verdict == "hit":
            api.send(chat_id, format_hit(art), markup=start_inline(webapp))
            sessions.set_mode(chat_id, "await_contact", last_artifact_id=aid)
        elif verdict == "almost":
            api.send(chat_id, format_almost_prompt())
            sessions.set_mode(chat_id, "await_almost", last_artifact_id=aid)
        else:
            api.send(chat_id, format_miss(), markup=main_keyboard())
            sessions.set_mode(chat_id, "idle")
        return
    if data.startswith("stc:"):
        n = data.split(":", 1)[1]
        sessions.set_mode(chat_id, "await_store", store_cat=n, door=_door_of(chat_id, room=f"store:{n}"))
        from backend.core.store_catalog import category_by_id

        cat = category_by_id(n) or {}
        api.send(chat_id, f"{cat.get('n')}. {cat.get('title')}\n{cat.get('one')}\n\n{cat.get('placeholder')}", html=False)
        return
    if data.startswith("tm:"):
        if not _gate(api, chat_id, "think_more", webapp):
            return
        from backend.core.complexity_boundary import table_telegram, think_more
        from backend.core.resonance import load as load_art2

        aid = data.split(":", 1)[1]
        prev = load_art2(aid) or {}
        brief = prev.get("brief") or sessions.load(chat_id).get("last_engine_brief") or "контур"
        nxt = think_more(brief, prev.get("lattice"))
        api.send(chat_id, table_telegram(nxt), markup=resonance_kb(aid))
        return
    if data.startswith("st:"):
        sid = data.split(":", 1)[1]
        sessions.set_mode(chat_id, "idle", strategy=sid)
        _run_demo(api, chat_id, f"стратегия {sid}", hint="strategy", strategy=sid)
        return
    if data.startswith("lv:"):
        sid = data.split(":", 1)[1]
        if sid in ("now", "live", ""):
            sid = sessions.load(chat_id).get("strategy") or "two_leg_tape"
        sessions.set_mode(chat_id, "idle", strategy=sid)
        _run_demo(
            api,
            chat_id,
            f"живой снимок модели {sid} как есть, без новой посадки",
            hint="strategy",
            strategy=sid,
            watch=True,
        )
        return
    if data.startswith("ss:"):
        from backend.core.stop_on_shift import check_stop
        from backend.core.resonance import remember

        if not _gate(api, chat_id, "stop_on_shift", webapp):
            return
        sid = data.split(":", 1)[1]
        if sid in ("now", "live", ""):
            sid = sessions.load(chat_id).get("strategy") or "target_place"
        art = check_stop(
            f"проверка противоречия модели {sid} по живому контуру",
            strategy=sid,
        )
        remember(art)
        api.send(chat_id, format_telegram(art), markup=resonance_kb(art["id"]))
        return
    if data.startswith("rk:"):
        from backend.core.risk_engine import demo_card
        from backend.core.resonance import remember

        if not _gate(api, chat_id, "risk", webapp):
            return
        art = demo_card("риск-движок из бота")
        art["id"] = art.get("id") or "risk"
        remember(art)
        api.send(chat_id, format_telegram(art), markup=resonance_kb(art["id"]))
        return
    if data.startswith("af:"):
        kind = data.split(":", 1)[1]
        if kind == "thesis":
            feat = "thesis"
        elif kind == "panel":
            feat = "artefact_panel"
        else:
            feat = "offer_gen"
        if not _gate(api, chat_id, feat, webapp):
            return
        from backend.core.artefacts import analytical_panel, offer_generator, order_theses
        from backend.core.resonance import remember

        if kind == "thesis":
            art = order_theses("контур из бота: назови отношение, которое сдвинулось")
        elif kind == "panel":
            art = analytical_panel("контур из бота")
        else:
            art = offer_generator("предложение из бота")
        remember(art)
        api.send(chat_id, format_telegram(art), markup=resonance_kb(art["id"]))
        return
    if data.startswith("ag:")
        nid = data.split(":", 1)[1]
        sessions.set_mode(chat_id, "await_agent_brief", niche=nid)
        api.send(chat_id, texts.ASK_AGENT, markup=nav_inline(webapp), html=False)
        return
    if data.startswith("xp:"):
        from backend.core.x_posts import format_post, post_by_id

        post = post_by_id(data.split(":", 1)[1])
        if post:
            api.send(chat_id, f"<b>{post['theme']}</b>\n\n{format_post(post)}")
        return


def _looks_bored(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in ("скуч", "нечего", "залип", "делать нечего", "bored"))


def _looks_freelance(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in ("фриланс", "подработа", "есть заказ", "возьмёшь"))


def handle_text(api: BotAPI, chat_id: int, text: str, webapp: str) -> None:
    raw = (text or "").strip()
    st = sessions.load(chat_id)
    mode = st.get("mode") or "idle"

    action = menu_action(raw)
    if action:
        dispatch_menu(api, chat_id, action, webapp)
        return

    if raw.lower() in ("pack", "/pack", "конверт", "convert"):
        from backend.core.memo_convert import MemoConvertEngine
        from backend.core.orientation_engine import OrientationEngine

        orient = OrientationEngine().orient(raw if len(raw) > 24 else "pack a consult sequence for an operator who needs a named gap closed in ops", "ai-agencies")
        conv = MemoConvertEngine().convert(
            business_text=raw if len(raw) > 24 else "operator consult sequence, named gap, free then pilot then main",
            industry_id="ai-agencies",
            orientation=orient.to_dict(),
        ).to_dict()
        pack = conv.get("chain_pack") or {}
        sig = (pack.get("naming_sigils") or {}).get("chain") or "—"
        task = pack.get("tech_task_0") or {}
        title = task.get("title") if isinstance(task, dict) else ""
        api.send(
            chat_id,
            f"<b>{sig}</b>\n1. Consult\n2. Direction\n3. Ship\nArtefact: sequence pack\nTech-task: {title or 'assemble bound slots'}\nCTA: free consult → pilot. Main only after gates.",
        )
        return

    if raw.startswith("mx_") or raw.lower().startswith("/access "):
        token = raw.split(maxsplit=1)[-1].strip()
        out = redeem(token, bind_subject=subject_hash(chat_id))
        if out.get("ok"):
            api.send(chat_id, "Access открыт. Одна подписка на все пять разделов.", markup=nav_inline(webapp))
        else:
            api.send(chat_id, "Токен не принят. Если только что оплатили Tribute — подождите минуту или напишите «связаться с человеком».")
        return

    if mode == "await_almost":
        prev = load_art(st.get("last_artifact_id") or "") or {}
        brief = f"{prev.get('brief') or ''}\nЧто не зашло: {raw}"
        _run_demo(
            api,
            chat_id,
            brief,
            hint=prev.get("lane") or "",
            strategy=prev.get("strategy_id"),
            niche=prev.get("niche_id"),
        )
        return

    if mode == "await_contact":
        api.send(
            chat_id,
            "Ок, записал. Когда буду на связи — продолжим пилот с того артефакта, который зашёл. "
            "Если надо быстрее — напишите «давай сейчас».",
        )
        sessions.set_mode(chat_id, "idle")
        return

    if mode in ("await_demo", "await_landing", "await_life"):
        _run_section(api, chat_id, "life", raw)
        return
    if mode == "await_bots":
        _run_section(api, chat_id, "bots", raw, strategy=st.get("strategy"))
        return
    if mode in ("await_craft", "await_engine"):
        _run_section(api, chat_id, "craft", raw)
        return
    if mode == "await_target":
        _run_section(api, chat_id, "target", raw)
        return
    if mode in ("await_shop", "await_making"):
        _run_section(api, chat_id, "shop", raw)
        return
    if mode == "await_store":
        if not _gate(api, chat_id, "store", webapp):
            return
        from backend.core.seven_lines import run_line

        n = int(st.get("store_cat") or 1)
        api.send(chat_id, "Собираю комнату…")
        art = run_line(n, raw, with_engine=False)
        art["id"] = art.get("id") or ""
        from backend.core.resonance import remember
        from backend.core.demo_highway import format_telegram

        if not art.get("id"):
            remember(art)
        _door_of(chat_id, raw, f"store:{n}")
        api.send(chat_id, format_telegram(art) if art.get("break") else (art.get("wow") or art.get("title") or "объект"), markup=resonance_kb(art.get("id") or "x"))
        return
    if mode == "await_shift":
        if not _gate(api, chat_id, "craftshift", webapp):
            return
        from backend.core.craftshift_x import run as run_cs
        from backend.core.demo_highway import format_telegram

        api.send(chat_id, "Собираю пост и кадр…")
        art = run_cs(raw)
        _door_of(chat_id, raw, "craftshift")
        post = art.get("post") or ""
        api.send(chat_id, format_telegram(art), markup=resonance_kb(art["id"]))
        if post:
            api.send(chat_id, f"<b>Пост</b>\n<pre>{_esc(post)[:3500]}</pre>")
        return
    if mode == "await_door":
        from backend.core.door import load as door_load

        rec = door_load(raw)
        if rec:
            sessions.set_mode(chat_id, "idle", door=rec["code"])
            api.send(chat_id, f"Дверь <code>{rec['code']}</code> открыта. Пишите, что ломается.")
            return
        api.send(chat_id, "Код не найден. 6 символов, или напишите ситуацию — выдадим новый.")
        return

    if mode == "await_engine_legacy":
        from backend.core.content_closer import comfort_turn

        hist = st.get("comfort_history") or []
        turn = comfort_turn(raw, history=hist, lang="ru")
        hist = (hist + [{"role": "user", "text": raw}, {"role": "assistant", "text": turn["reply"]}])[-8:]
        sessions.set_mode(chat_id, "await_engine", comfort_history=hist)
        api.send(chat_id, turn["reply"], html=False)
        if len(raw) >= 24:
            _run_demo(api, chat_id, raw, hint="engine")
        return

    if mode == "await_making":
        _run_demo(api, chat_id, raw, hint="making")
        return

    if mode in ("await_agent_brief",):
        _run_demo(api, chat_id, raw, hint="agent", niche=st.get("niche"))
        return

    if _looks_bored(raw):
        api.send(chat_id, texts.BORED)
        sessions.set_mode(chat_id, "await_demo")
        return
    if _looks_freelance(raw):
        api.send(chat_id, texts.FREELANCE)
        sessions.set_mode(chat_id, "await_demo")
        return

    from backend.core.door import load as door_load

    rec = door_load(raw)
    if rec:
        sessions.set_mode(chat_id, "idle", door=rec["code"])
        api.send(chat_id, f"Дверь <code>{rec['code']}</code>. Продолжаем с того же контура.")
        return

    # Idle free text → conversation first.
    if len(raw) >= 8:
        _door_of(chat_id, raw, "talk")
        _run_demo(api, chat_id, raw)
        return
    api.send(chat_id, IDLE_HINT, markup=main_keyboard())


def handle_update(api: BotAPI, upd: dict, webapp: str) -> None:
    pcq = upd.get("pre_checkout_query")
    if pcq:
        api.call("answerPreCheckoutQuery", pre_checkout_query_id=pcq["id"], ok=True)
        return
    cq = upd.get("callback_query")
    if cq:
        handle_callback(api, cq, webapp)
        return
    msg = upd.get("message") or upd.get("edited_message") or {}
    if msg.get("successful_payment"):
        sp = msg["successful_payment"]
        api.call(
            "sendMessage",
            chat_id=msg["chat"]["id"],
            text=f"Оплата принята. Это про внедрение, не про «ещё доступ». · {sp.get('invoice_payload')}",
        )
        return
    chat = (msg.get("chat") or {}).get("id")
    if not chat:
        return
    text = (msg.get("text") or "").strip()
    handle_text(api, chat, text, webapp)


def main() -> int:
    _load_dotenv()
    token = _token()
    if not token:
        print("Set TELEGRAM_BOT_TOKEN. Mini App still runs at /tg/.")
        return 1
    webapp = _webapp()
    api = BotAPI(token)
    me = api.call("getMe")
    print("bot", (me.get("result") or {}).get("username"), "webapp", webapp)
    if not me.get("ok"):
        return 1
    bootstrap(api, webapp)
    offset = 0
    while True:
        try:
            data = api.call(
                "getUpdates",
                offset=offset,
                timeout=50,
                allowed_updates=["message", "callback_query", "pre_checkout_query"],
            )
            for upd in data.get("result") or []:
                offset = int(upd["update_id"]) + 1
                try:
                    handle_update(api, upd, webapp)
                except Exception as exc:  # noqa: BLE001
                    print("update error", exc)
                    chat = ((upd.get("message") or upd.get("callback_query") or {}).get("message") or upd.get("message") or {}).get("chat") or {}
                    cid = chat.get("id") or ((upd.get("callback_query") or {}).get("from") or {}).get("id")
                    if cid:
                        try:
                            api.send(cid, "Кнопка не прошла. Нажмите ещё раз — In-Out Chain, AI Teammates или Artefacts.", html=False)
                        except Exception:
                            pass
        except KeyboardInterrupt:
            print("stop")
            return 0
        except Exception as exc:  # noqa: BLE001
            print("poll error", exc)
            time.sleep(2)


if __name__ == "__main__":
    raise SystemExit(main())
