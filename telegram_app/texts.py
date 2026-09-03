"""User-facing Telegram copy. Short names, human meaning."""

from __future__ import annotations

from backend.core.voice import BORED_TEXT, FREELANCE_TEXT, START_TEXT
from backend.core.x_posts import HANDLE, X_URL

START = START_TEXT
BORED = BORED_TEXT
FREELANCE = FREELANCE_TEXT

ASK_DEMO = (
    "In-Out Chain. Что сейчас стоит дорого на входе или на выходе. Можно криво.\n\n"
    "Пример: «SaaS 80 человек, фичи пилим, никто не знает, что считается победой».\n"
    "Или: «золото, вхожу когда уже ушло».\n\n"
    "Соберу карту. Два бесплатных результата, дальше Access."
)

ASK_LANDING = ASK_DEMO
ASK_CHAIN = ASK_DEMO

ASK_AGENT = "Кто вы — и что бесит. Одним сообщением. Тимейт держит финмодель, не болтает."

ASK_ENGINE = (
    "AI Teammates. Четыре живых агента и воркфлоу нового решения.\n\n"
    "Напишите, что бесит — или выберите тимейта. "
    "Кастом $500. Связь с человеком — отдельной кнопкой."
)

ASK_TEAMMATES = ASK_ENGINE

ASK_STRAT = "Фраза про стиль входа — или просто модель. Это код, не сигнал."

ASK_MAKING = (
    "Artefacts. Панель метрик и генератор предложений.\n\n"
    "Напишите контур своими словами. Tape Land лежит здесь же — папкой, не отдельным сервисом."
)

ASK_ARTEFACTS = ASK_MAKING

ASK_ACCESS = (
    "Два бесплатных результата использованы.\n\n"
    "Это бот-артефакт (ленд), не весь Metrix AI.\n"
    "Metrix Access — 3 290 ₽ / месяц: 40 результатов в боте. "
    "Chain, Teammates, Artefacts. Код модели, не сигналы.\n"
    "Не входит: Metrix AI $2490 (ops + оригинальный проект + промо), Custom $500.\n"
    "Оплата в Tribute. Имя и телефон не храним."
)

ASK_MONTH_CAP = (
    "Лимит месяца: 40 результатов по Access.\n"
    "Новый месяц — снова 40. Если нужен полный движок (ops + проект + промо) — это Metrix AI $2490."
)

POSTS_INTRO = (
    f"Прогрев для {HANDLE}. Инверсия, не воронка. Можно копировать как есть.\n"
    f"{X_URL}"
)

HELP = (
    "In-Out Chain — каталог моделей, одна подписка.\n"
    "AI Teammates — четыре агента, воркфлоу, связь с человеком.\n"
    "Artefacts — аналитическая панель и генератор предложений.\n\n"
    "Код согласованной модели, не сигналы. Риск-движок — отдельно от четырёх моделей."
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
