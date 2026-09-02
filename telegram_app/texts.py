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
    "Соберу карту модели. Два прогона бесплатно, дальше Access."
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
    "Бесплатные прогоны кончились.\n\n"
    "Metrix Access — 1 490 ₽ / месяц. Одна подписка на все три вкладки, "
    "четыре модели, риск-движок, обновления кода как есть.\n"
    "Tribute принимает оплату. Мы не храним имя, телефон и telegram_id — только HMAC доступа."
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
