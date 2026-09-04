"""User-facing Telegram copy. Short, concrete names."""

from __future__ import annotations

from backend.core.voice import BORED_TEXT, FREELANCE_TEXT, START_TEXT
from backend.core.x_posts import HANDLE, X_URL

START = START_TEXT
BORED = BORED_TEXT
FREELANCE = FREELANCE_TEXT

ASK_LIFE = (
    "Идеи для жизни. Напишите, что сейчас тяжело — сон, деньги, дом, нагрузка.\n"
    "Отвечу короткими шагами, не лекцией."
)
ASK_CHAIN = ASK_LIFE
ASK_LANDING = ASK_LIFE
ASK_DEMO = ASK_LIFE

ASK_BOTS = (
    "Торговые боты. Четыре готовых модели. Код модели, не сигналы.\n"
    "Эксперимент: напишите правило своими словами — без кода. Потом оценка: зашло / почти / мимо."
)
ASK_STRAT = ASK_BOTS

ASK_CRAFT = (
    "Конфиги для ремесла. Опишите изделие, материал, срок.\n"
    "Соберу файл заказа: что делать, когда молчать, какая цена."
)
ASK_TEAMMATES = ASK_CRAFT
ASK_ENGINE = ASK_CRAFT
ASK_AGENT = ASK_CRAFT

ASK_TARGET = (
    "Таргет ИИ-агентов. Кто платит, какой канал, какой текст, когда молчать."
)

ASK_SHOP = (
    "Каталог магазина. Товар своими словами.\n"
    "Соберу карточку: имя, описание, когда человеку это нужно."
)
ASK_ARTEFACTS = ASK_SHOP
ASK_MAKING = ASK_SHOP

ASK_ACCESS = (
    "Два бесплатных результата использованы.\n\n"
    "Metrix Access — 3 290 ₽ / месяц, 40 результатов.\n"
    "Пять разделов: жизнь, торговые боты, ремесло, агенты, магазин.\n"
    "Оплата в Tribute. Имя и телефон не храним."
)

ASK_MONTH_CAP = (
    "Лимит месяца: 40 результатов. Новый месяц — снова 40."
)

POSTS_INTRO = f"Короткие тексты для {HANDLE}.\n{X_URL}"

HELP = (
    "Идеи для жизни — короткий чат, что улучшить сегодня.\n"
    "Торговые боты — витрина и эксперимент с промптом без кода.\n"
    "Конфиги для ремесла — файл заказа.\n"
    "Таргет ИИ-агентов — роль, канал, текст.\n"
    "Каталог магазина — имя, описание, когда нужно."
)

MENU_LIFE = "Идеи для жизни"
MENU_BOTS = "Торговые боты"
MENU_CRAFT = "Конфиги для ремесла"
MENU_TARGET = "Таргет ИИ-агентов"
MENU_SHOP = "Каталог магазина"
MENU_CHAIN = MENU_LIFE
MENU_TEAMMATES = MENU_CRAFT
MENU_ARTEFACTS = MENU_SHOP
MENU_LANDING = MENU_LIFE
MENU_ENGINE = MENU_CRAFT
MENU_MAKING = MENU_SHOP
MENU_DEMO = MENU_LIFE
MENU_STRAT = MENU_BOTS
MENU_AGENTS = MENU_TARGET
MENU_POSTS = MENU_SHOP

DESC = HELP[:120]
SHORT = "Пять разделов: жизнь, боты, ремесло, агенты, магазин."
NAME = "Metrix"
