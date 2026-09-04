"""User-facing Telegram copy. Short names, human meaning."""

from __future__ import annotations

from backend.core.voice import BORED_TEXT, FREELANCE_TEXT, START_TEXT
from backend.core.x_posts import HANDLE, X_URL

START = START_TEXT
BORED = BORED_TEXT
FREELANCE = FREELANCE_TEXT

ASK_DEMO = (
    "In-Out Chain. Что стоит дорого на in или на out. Можно криво.\n\n"
    "Пример: «золото, вхожу когда уже ушло».\n"
    "Карточка «Стоп на перемене» — не сигнал: жив ли тезис стратегии, не сливать бюджет.\n\n"
    "Соберу карту. Два бесплатных результата, дальше Access."
)

ASK_LANDING = ASK_DEMO
ASK_CHAIN = ASK_DEMO

ASK_AGENT = "Кто вы — и что бесит. Одним сообщением. Тимейт держит финмодель, не болтает."

ASK_ENGINE = (
    "AI Teammates. Два живых: IT-внедрение и продакшн-агентства. "
    "На выходе конфиг, который можно отдать подрядчику. Edu и ecom — не этот контур.\n\n"
    "Напишите, что бесит — или выберите тимейта. Кастом $500 — посадка конфига."
)

ASK_TEAMMATES = ASK_ENGINE

ASK_STRAT = "Фраза про стиль входа — или просто модель. Это код, не сигнал."

ASK_MAKING = (
    "Artefacts. Продаём только тезисы.\n\n"
    "Напишите контур своими словами. На руки — короткие утверждения про процесс, "
    "каждое можно убить фактом. Не отчёт и не проект в подарок."
)

ASK_ARTEFACTS = ASK_MAKING

ASK_ACCESS = (
    "Два бесплатных результата использованы.\n\n"
    "Это бот-артефакт (ленд), не весь Metrix AI.\n"
    "Metrix Access — 3 290 ₽ / месяц: 40 карт под вашу ситуацию. "
    "Живой снимок рынка в Access не списывается — рынок может обновиться в любой момент.\n"
    "Chain, Teammates, Artefacts. Код модели, не сигналы.\n"
    "Не входит: Metrix AI $2490 как отдельный SKU (тот же движок, посадка физ. ecom), Custom $500.\n"
    "Оплата в Tribute. Имя и телефон не храним."
)

ASK_MONTH_CAP = (
    "Лимит месяца: 40 карт под вашу ситуацию.\n"
    "Живой снимок модели (кнопка «Как сейчас») не списывается — тики рынка в лимит не входят.\n"
    "Новый месяц — снова 40 карт. Движок в боте уже работает: тезисы, конфиги, in-out. $2490 — посадка того же движка в физ. ecom."
)

POSTS_INTRO = (
    f"Прогрев для {HANDLE}. Инверсия, не воронка. Можно копировать как есть.\n"
    f"{X_URL}"
)

HELP = (
    "In-Out Chain — модели и карточка «Стоп на перемене».\n"
    "AI Teammates — IT и продакшн, конфиг на заказ.\n"
    "Artefacts — тезисы на заказ. Только тезисы.\n\n"
    "Код согласованной модели, не сигналы. Движок в боте: тезисы, конфиги, in-out."
)

MENU_CHAIN = "In-Out Chain"
MENU_TEAMMATES = "AI Teammates"
MENU_ARTEFACTS = "Artefacts"
MENU_LANDING = MENU_CHAIN
MENU_ENGINE = MENU_TEAMMATES
MENU_MAKING = MENU_ARTEFACTS
MENU_DEMO = MENU_CHAIN
MENU_STRAT = MENU_CHAIN
MENU_AGENTS = MENU_TEAMMATES
MENU_POSTS = MENU_ARTEFACTS

DESC = (
    "Karim Metrix · In-Out Chain. Снимает рутину, закрывает решённое и нерешённое, "
    "режет стоимость in и out. Код модели, не сигналы."
)
SHORT = "In-Out Chain · Teammates · Artefacts. Одна подписка."
NAME = "Karim Metrix"
