"""
Karim Metrix bot — conversation first, Mini App second.

Env: TELEGRAM_BOT_TOKEN, TELEGRAM_WEBAPP_URL, METRIX_PUBLIC_URL
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from backend.core.x_posts import list_posts
from backend.core.voice import IDLE_HINT
from telegram_app import sessions
from telegram_app import texts
from telegram_app.menu import menu_action

HERE = Path(__file__).resolve().parent
AVATAR = HERE / "avatar.jpg"
MARK = ROOT / "public" / "tg" / "assets" / "mark.jpg"


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
    raw = (
        os.getenv("TELEGRAM_WEBAPP_URL", "").strip()
        or (os.getenv("METRIX_PUBLIC_URL", "").rstrip("/") + "/tg/")
        or "https://metrix-ai-production.up.railway.app/tg/"
    )
    if not raw.endswith("/"):
        raw += "/"
    return raw


def main_keyboard() -> dict:
    return {
        "keyboard": [
            [{"text": texts.MENU_DEMO}, {"text": texts.MENU_STRAT}],
            [{"text": texts.MENU_AGENTS}, {"text": texts.MENU_POSTS}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def webapp_row(webapp: str) -> list[dict]:
    return [{"text": "Открыть билдер", "web_app": {"url": webapp}}]


def nav_inline(webapp: str, *, extra: list | None = None) -> dict:
    """Primary nav — inline callbacks. Reply keyboard is a fallback; Telegram often hides it."""
    rows = [
        [
            {"text": "Демо", "callback_data": "m:demo"},
            {"text": "Стратегии", "callback_data": "m:strat"},
        ],
        [
            {"text": "Агенты", "callback_data": "m:agents"},
            {"text": "Посты", "callback_data": "m:posts"},
        ],
        webapp_row(webapp),
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
            ]
        ]
    }


def strategies_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Target Place · золото", "callback_data": "st:target_place"}],
            [{"text": "Demand · крипта", "callback_data": "st:demand"}],
            [{"text": "Ampli · Америка", "callback_data": "st:ampli"}],
        ]
    }


def niches_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "SaaS / IT 50–500", "callback_data": "ag:saas"}],
            [{"text": "Агентства digital / performance", "callback_data": "ag:agency"}],
            [{"text": "Школы и обучение", "callback_data": "ag:edu"}],
            [{"text": "E-com с высоким чеком", "callback_data": "ag:ecom"}],
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

    def send_start(self, chat_id: int, webapp: str) -> None:
        photo = AVATAR if AVATAR.exists() else MARK
        kb = start_inline(webapp)
        if photo.exists():
            with photo.open("rb") as f:
                r = self.client.post(
                    f"{self.base}/sendPhoto",
                    data={
                        "chat_id": str(chat_id),
                        "caption": texts.START,
                        "parse_mode": "HTML",
                    },
                    files={"photo": ("mark.jpg", f, "image/jpeg")},
                )
            try:
                data = r.json()
            except Exception:
                data = {"ok": False}
            if data.get("ok"):
                self.send(
                    chat_id,
                    IDLE_HINT,
                    markup=main_keyboard(),
                    html=False,
                )
                self.send(
                    chat_id,
                    "Демо · Стратегии · Агенты — кнопки под этим сообщением.",
                    markup=kb,
                    html=False,
                )
                return
        self.send(chat_id, texts.START, markup=main_keyboard())
        self.send(
            chat_id,
            "Демо · Стратегии · Агенты — кнопки под этим сообщением.",
            markup=kb,
            html=False,
        )


def bootstrap(api: BotAPI, webapp: str) -> None:
    api.call(
        "setChatMenuButton",
        menu_button={"type": "web_app", "text": "Билдер", "web_app": {"url": webapp}},
    )
    api.call(
        "setMyCommands",
        commands=[
            {"command": "start", "description": "Кто я и как это работает"},
            {"command": "demo", "description": "Собрать демо-артефакт"},
            {"command": "strategies", "description": "Три стратегии"},
            {"command": "agents", "description": "Собрать агента"},
            {"command": "posts", "description": "Черновики для X"},
        ],
    )
    api.call("setMyDescription", description=texts.DESC)
    api.call("setMyShortDescription", short_description=texts.SHORT)
    api.call("setMyName", name=texts.NAME)


def _send_artifact(api: BotAPI, chat_id: int, art: dict) -> None:
    sessions.set_mode(chat_id, "await_feedback", last_artifact_id=art.get("id"))
    api.send(chat_id, format_telegram(art), markup=resonance_kb(art["id"]))


def _run_demo(api: BotAPI, chat_id: int, brief: str, **kw) -> None:
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
    lines = ["<b>Три модели. Не сигналы.</b>\n"]
    for s in list_strategies():
        lines.append(
            f"<b>{_esc(s['name'])}</b> · {_esc(s['market'])}\n"
            f"{_esc(s['one_liner'])}\n"
            f"<i>{_esc(s['for_whom'])}</i>\n"
        )
    extra = strategies_kb()["inline_keyboard"]
    api.send(chat_id, "\n".join(lines), markup=nav_inline(webapp, extra=extra))


def show_agents(api: BotAPI, chat_id: int, webapp: str) -> None:
    lines = ["<b>Билдер агентов.</b> Агент держит финмодель, не болтает.\n"]
    for n in list_niches():
        lines.append(f"<b>{_esc(n['title'])}</b>\n{_esc(n['pain'])}\n")
    extra = niches_kb()["inline_keyboard"]
    api.send(chat_id, "\n".join(lines), markup=nav_inline(webapp, extra=extra))


def show_posts(api: BotAPI, chat_id: int, webapp: str) -> None:
    extra = posts_kb()["inline_keyboard"]
    api.send(chat_id, texts.POSTS_INTRO, markup=nav_inline(webapp, extra=extra))


def show_demo_prompt(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_demo")
    api.send(chat_id, texts.ASK_DEMO, markup=nav_inline(webapp), html=False)


def dispatch_menu(api: BotAPI, chat_id: int, action: str, webapp: str) -> None:
    if action == "start":
        sessions.set_mode(chat_id, "idle")
        api.send_start(chat_id, webapp)
        return
    if action == "help":
        api.send(chat_id, texts.HELP, markup=nav_inline(webapp), html=False)
        return
    if action == "demo":
        show_demo_prompt(api, chat_id, webapp)
        return
    if action == "strategies":
        show_strategies(api, chat_id, webapp)
        return
    if action == "agents":
        show_agents(api, chat_id, webapp)
        return
    if action == "posts":
        show_posts(api, chat_id, webapp)
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
            "demo": "demo",
            "strat": "strategies",
            "strategies": "strategies",
            "agents": "agents",
            "posts": "posts",
        }.get(data.split(":", 1)[1])
        if action:
            dispatch_menu(api, chat_id, action, webapp)
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
    if data.startswith("st:"):
        sid = data.split(":", 1)[1]
        sessions.set_mode(chat_id, "idle", strategy=sid)
        _run_demo(api, chat_id, f"стратегия {sid}", hint="strategy", strategy=sid)
        return
    if data.startswith("ag:"):
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

    if mode in ("await_demo", "await_agent_brief"):
        kw = {}
        if mode == "await_agent_brief":
            kw = {"hint": "agent", "niche": st.get("niche")}
        _run_demo(api, chat_id, raw, **kw)
        return

    if _looks_bored(raw):
        api.send(chat_id, texts.BORED)
        sessions.set_mode(chat_id, "await_demo")
        return
    if _looks_freelance(raw):
        api.send(chat_id, texts.FREELANCE)
        sessions.set_mode(chat_id, "await_demo")
        return

    # Idle free text → demo highway. That's the product.
    if len(raw) >= 8:
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
                            api.send(cid, "Кнопка не прошла. Нажмите ещё раз — Демо, Стратегии или Агенты.", html=False)
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
