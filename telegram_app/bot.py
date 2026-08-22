"""
Metrix AI Bot — Telegram Mini App + payments.

Env:
  TELEGRAM_BOT_TOKEN          from BotFather
  TELEGRAM_WEBAPP_URL         https://<host>/tg/   (HTTPS required in production)
  TELEGRAM_PROVIDER_TOKEN     YooKassa token from BotFather → Payments (RF cards)
  METRIX_PUBLIC_URL           fallback for webapp url

Run:
  py -3 -m telegram_app.bot
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


def _token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def _webapp() -> str:
    return (
        os.getenv("TELEGRAM_WEBAPP_URL", "").strip()
        or (os.getenv("METRIX_PUBLIC_URL", "").rstrip("/") + "/tg/")
        or "http://127.0.0.1:8787/tg/"
    )


class BotAPI:
    def __init__(self, token: str) -> None:
        self.base = f"https://api.telegram.org/bot{token}"
        self.client = httpx.Client(timeout=70)

    def call(self, method: str, **payload):
        r = self.client.post(f"{self.base}/{method}", json=payload)
        data = r.json()
        if not data.get("ok"):
            print("tg error", method, data)
        return data


def keyboard(webapp: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {
                    "text": "Открыть Metrix AI",
                    "web_app": {"url": webapp},
                }
            ],
            [
                {"text": "Работа по запросу", "web_app": {"url": webapp + "#request"}},
                {"text": "Карточки", "web_app": {"url": webapp + "#flagships"}},
            ],
        ]
    }


START = (
    "Metrix AI Bot\n\n"
    "Маркетплейс как CraftShift: флагманские карточки, работа по запросу, промо, терминал ордеров.\n\n"
    "Читалка задания держит несколько концов считывания и сама выбирает режим.\n"
    "Ориентация бесплатно. Оплата — карта РФ (ЮKassa) или Telegram Stars."
)


def handle_update(api: BotAPI, upd: dict, webapp: str) -> None:
    pcq = upd.get("pre_checkout_query")
    if pcq:
        api.call("answerPreCheckoutQuery", pre_checkout_query_id=pcq["id"], ok=True)
        return
    msg = upd.get("message") or upd.get("edited_message") or {}
    if msg.get("successful_payment"):
        sp = msg["successful_payment"]
        chat = msg["chat"]["id"]
        api.call(
            "sendMessage",
            chat_id=chat,
            text=f"Оплата принята · {sp.get('invoice_payload')} · {sp.get('total_amount')} {sp.get('currency')}",
        )
        return
    text = (msg.get("text") or "").strip()
    chat = (msg.get("chat") or {}).get("id")
    if not chat:
        return
    if text.startswith("/start") or text.startswith("/app"):
        api.call(
            "sendMessage",
            chat_id=chat,
            text=START,
            reply_markup=keyboard(webapp),
        )
        return
    if text.startswith("/pay"):
        api.call(
            "sendMessage",
            chat_id=chat,
            text="Оплата открывается из карточки в приложении (Карта РФ / Stars).",
            reply_markup=keyboard(webapp),
        )
        return
    api.call(
        "sendMessage",
        chat_id=chat,
        text="Откройте приложение — главная, запрос, карточки, промо, терминал.",
        reply_markup=keyboard(webapp),
    )


def main() -> int:
    token = _token()
    if not token:
        print("Set TELEGRAM_BOT_TOKEN (BotFather). Mini App still runs at /tg/ without the bot.")
        return 1
    webapp = _webapp()
    if webapp.startswith("http://") and "127.0.0.1" not in webapp:
        print("Warning: Telegram Mini Apps need HTTPS in production:", webapp)
    api = BotAPI(token)
    me = api.call("getMe")
    print("bot", (me.get("result") or {}).get("username"), "webapp", webapp)
    api.call(
        "setChatMenuButton",
        menu_button={"type": "web_app", "text": "Metrix AI", "web_app": {"url": webapp}},
    )
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
