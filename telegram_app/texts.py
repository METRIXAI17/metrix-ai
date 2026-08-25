"""User-facing Telegram copy. Short names, human meaning."""

from __future__ import annotations

from backend.core.voice import BORED_TEXT, FREELANCE_TEXT, START_TEXT
from backend.core.x_posts import HANDLE, X_URL

START = START_TEXT
BORED = BORED_TEXT
FREELANCE = FREELANCE_TEXT

ASK_DEMO = (
    "Киньте ситуацию своими словами. Можно криво.\n\n"
    "Пример: «SaaS 80 человек, фичи пилим, никто не знает, что считается победой».\n"
    "Или: «золото, вхожу когда уже ушло».\n\n"
    "Соберу один артефакт. Не отчёт."
)

ASK_AGENT = "Кто вы — и что бесит. Одним сообщением. Соберу спеку агента, не презентацию."

ASK_STRAT = "Если хотите, добавьте одну фразу про свой стиль входа. Или просто выберите стратегию — соберу карту как есть."

POSTS_INTRO = (
    f"Черновики для {HANDLE}. Можно копировать как есть, можно править под настроение.\n"
    f"{X_URL}"
)

HELP = (
    "Демо — собираю артефакт из вашей ситуации.\n"
    "Стратегии — Target Place (золото), Demand (крипта), Ampli (Америка).\n"
    "Агенты — билдер под SaaS, агентства, школы, e-com.\n"
    "Посты — тексты для X.\n\n"
    "Любое другое сообщение тоже можно. Я не справочник."
)

MENU_DEMO = "Демо"
MENU_STRAT = "Стратегии"
MENU_AGENTS = "Агенты"
MENU_POSTS = "Посты"

DESC = (
    "Карим · Metrix. Демо финансовых моделей и AI-агентов. "
    "Если артефакт зайдёт — это вход в платную посадку. Не сигналы."
)
SHORT = "Демо моделей и агентов. Если зашло — это товар."
NAME = "Karim Metrix"
