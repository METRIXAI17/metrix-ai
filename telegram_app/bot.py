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
            [{"text": texts.MENU_CHAIN}, {"text": texts.MENU_TEAMMATES}],
            [{"text": texts.MENU_ARTEFACTS}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def webapp_row(webapp: str) -> list[dict]:
    return [{"text": "In-Out Chain", "web_app": {"url": webapp}}]


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
            {"text": "In-Out Chain", "callback_data": "m:chain"},
            {"text": "AI Teammates", "callback_data": "m:teammates"},
        ],
        [
            {"text": "Artefacts", "callback_data": "m:artefacts"},
        ],
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
            ]
        ]
    }


def strategies_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Target Place · золото", "callback_data": "st:target_place"}],
            [{"text": "Demand · крипта", "callback_data": "st:demand"}],
            [{"text": "Ampli · Америка", "callback_data": "st:ampli"}],
            [{"text": "Two-Leg Tape · Tape Land", "callback_data": "st:two_leg_tape"}],
            [{"text": "Risk Engine · отдельно", "callback_data": "rk:engine"}],
        ]
    }


def niches_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Unit Desk · SaaS 50–500", "callback_data": "ag:saas"}],
            [{"text": "Onboard Geometry · агентства", "callback_data": "ag:agency"}],
            [{"text": "Cohort Step · школы", "callback_data": "ag:edu"}],
            [{"text": "Order Cycle · e-com чек", "callback_data": "ag:ecom"}],
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
                    "In-Out Chain · AI Teammates · Artefacts — кнопки под этим сообщением.",
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
        menu_button={"type": "web_app", "text": "Chain", "web_app": {"url": webapp}},
    )
    api.call(
        "setMyCommands",
        commands=[
            {"command": "start", "description": "Кто я и как это работает"},
            {"command": "chain", "description": "In-Out Chain — модели и подписка"},
            {"command": "teammates", "description": "AI Teammates — агенты и воркфлоу"},
            {"command": "artefacts", "description": "Artefacts — панель и предложения"},
            {"command": "access", "description": "Metrix Access · 3 290 ₽"},
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


def _run_demo(api: BotAPI, chat_id: int, brief: str, **kw) -> None:
    feature = "strategy" if kw.get("strategy") or kw.get("hint") == "strategy" else "teammate" if kw.get("niche") or kw.get("hint") in ("agent", "teammates") else "artefact_panel"
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


def show_chain(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_landing")
    extra = strategies_kb()["inline_keyboard"]
    api.send(chat_id, texts.ASK_CHAIN, markup=nav_inline(webapp, extra=extra), html=False)


def show_landing(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_chain(api, chat_id, webapp)


def show_teammates(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_engine")
    extra = niches_kb()["inline_keyboard"]
    api.send(chat_id, texts.ASK_TEAMMATES, markup=nav_inline(webapp, extra=extra), html=False)


def show_engine(api: BotAPI, chat_id: int, webapp: str) -> None:
    show_teammates(api, chat_id, webapp)


def show_artefacts(api: BotAPI, chat_id: int, webapp: str) -> None:
    sessions.set_mode(chat_id, "await_making")
    extra = [
        [{"text": "Аналитическая панель", "callback_data": "af:panel"}],
        [{"text": "Генератор предложений", "callback_data": "af:offer"}],
        [{"text": "Tape Land · two-leg-tape", "callback_data": "st:two_leg_tape"}],
    ]
    api.send(chat_id, texts.ASK_ARTEFACTS, markup=nav_inline(webapp, extra=extra), html=False)


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
    if action in ("chain", "landing", "demo", "strategies"):
        show_chain(api, chat_id, webapp)
        return
    if action in ("teammates", "engine", "agents"):
        show_teammates(api, chat_id, webapp)
        return
    if action in ("artefacts", "making", "posts"):
        show_artefacts(api, chat_id, webapp)
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
            "chain": "chain",
            "landing": "chain",
            "demo": "chain",
            "teammates": "teammates",
            "engine": "teammates",
            "strat": "chain",
            "strategies": "chain",
            "agents": "teammates",
            "artefacts": "artefacts",
            "making": "artefacts",
            "posts": "artefacts",
            "access": "access",
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
        if not _gate(api, chat_id, "artefact_panel" if kind == "panel" else "offer_gen", webapp):
            return
        from backend.core.artefacts import analytical_panel, offer_generator
        from backend.core.resonance import remember

        art = analytical_panel("контур из бота") if kind == "panel" else offer_generator("предложение из бота")
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
            api.send(chat_id, "Access открыт. Одна подписка на все три вкладки.", markup=nav_inline(webapp))
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

    if mode in ("await_demo", "await_landing"):
        _run_demo(api, chat_id, raw, hint="landing")
        return

    if mode == "await_engine":
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
