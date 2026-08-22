"""
Metrix AI Bot — Mini App launcher.

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

    def send_start(self, chat_id: int, webapp: str) -> None:
        caption = (
            "<b>Metrix AI</b>\n"
            "Одно окно для workflows и оригинальных проектов.\n\n"
            "Работа по запросу · флагманские карточки · промо · терминал.\n"
            "Читалка держит несколько считываний и сама выбирает режим.\n\n"
            "<i>Идеи сразу. Сейчас без оплаты.</i>"
        )
        photo = AVATAR if AVATAR.exists() else MARK
        kb = keyboard(webapp)
        if photo.exists():
            with photo.open("rb") as f:
                r = self.client.post(
                    f"{self.base}/sendPhoto",
                    data={
                        "chat_id": str(chat_id),
                        "caption": caption,
                        "parse_mode": "HTML",
                    },
                    files={"photo": ("mark.jpg", f, "image/jpeg")},
                )
            try:
                data = r.json()
            except Exception:
                data = {"ok": False}
            if data.get("ok"):
                self.call(
                    "sendMessage",
                    chat_id=chat_id,
                    text="Откройте приложение ↓",
                    reply_markup=kb,
                )
                return
        self.call(
            "sendMessage",
            chat_id=chat_id,
            text=caption.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""),
            reply_markup=kb,
        )


def keyboard(webapp: str) -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Открыть Metrix AI", "web_app": {"url": webapp}}],
            [
                {"text": "Работа по запросу", "web_app": {"url": webapp + "#request"}},
                {"text": "Карточки", "web_app": {"url": webapp + "#flagships"}},
            ],
        ]
    }


def bootstrap(api: BotAPI, webapp: str) -> None:
    api.call(
        "setChatMenuButton",
        menu_button={"type": "web_app", "text": "Metrix AI", "web_app": {"url": webapp}},
    )
    api.call(
        "setMyCommands",
        commands=[
            {"command": "start", "description": "Открыть Metrix AI"},
            {"command": "app", "description": "Приложение"},
        ],
    )
    api.call(
        "setMyDescription",
        description=(
            "Metrix AI — одно окно для workflows и оригинальных проектов. "
            "Работа по запросу, флагманские карточки, промо, терминал."
        ),
    )
    api.call(
        "setMyShortDescription",
        short_description="Metrix AI · запрос · карточки · промо",
    )
    api.call("setMyName", name="Metrix AI")


def handle_update(api: BotAPI, upd: dict, webapp: str) -> None:
    pcq = upd.get("pre_checkout_query")
    if pcq:
        api.call("answerPreCheckoutQuery", pre_checkout_query_id=pcq["id"], ok=True)
        return
    msg = upd.get("message") or upd.get("edited_message") or {}
    if msg.get("successful_payment"):
        sp = msg["successful_payment"]
        api.call(
            "sendMessage",
            chat_id=msg["chat"]["id"],
            text=f"Оплата принята · {sp.get('invoice_payload')}",
        )
        return
    text = (msg.get("text") or "").strip()
    chat = (msg.get("chat") or {}).get("id")
    if not chat:
        return
    if text.startswith("/start") or text.startswith("/app") or text.startswith("/pay"):
        api.send_start(chat, webapp)
        return
    api.send_start(chat, webapp)


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
                allowed_updates=["message", "pre_checkout_query"],
            )
            for upd in data.get("result") or []:
                offset = int(upd["update_id"]) + 1
                handle_update(api, upd, webapp)
        except KeyboardInterrupt:
            print("stop")
            return 0
        except Exception as exc:  # noqa: BLE001
            print("poll error", exc)
            time.sleep(2)


if __name__ == "__main__":
    raise SystemExit(main())
