"""User-facing Telegram copy. Short, concrete names."""

from __future__ import annotations

from backend.core.voice import BORED_TEXT, FREELANCE_TEXT, START_TEXT
from backend.core.x_posts import HANDLE, X_URL

START = START_TEXT
BORED = BORED_TEXT
FREELANCE = FREELANCE_TEXT

ASK_LIFE = (
    "Флагман. Бесплатный слой. Две строки, не эссе.\n"
    "Выдаёт суть твоего вопроса и решение одной фразой.\n"
    "Потом несколько вопросов своими словами — сводка векторов.\n"
    "Внутри $490: комбо рекурсивных решений и терминальная посадка процесса.\n"
    "Eval — после оплаты."
)
ASK_CHAIN = ASK_LIFE
ASK_LANDING = ASK_LIFE
ASK_DEMO = ASK_LIFE
ASK_FLAGSHIP = ASK_LIFE

ASK_BOTS = (
    "Торговые боты. Четыре готовых модели. Код модели, не сигналы.\n"
    "Эксперимент: напишите правило своими словами — без кода. Потом оценка: зашло / почти / мимо.\n"
    "Контроль рисков — отдельно: R не плечо. Без стопа нет размера."
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
ASK_STORE = (
    "Web3 Store. Запросы бесплатно.\n"
    "Входящий заказ — не новая линейка. Напишите, что ломается — или нажмите комнату."
)
ASK_TARIFFS = (
    "Дверь <b>$50 Allo</b>. Directing — отдельно, один ход.\n"
    "Хиты — смотреть бесплатно. Web3 Store — запросы бесплатно.\n"
    "Верхние комнаты: $100 / $490 / $1000 / $10 000 — рекурсия и спеки.\n"
    "На $50 файла рекурсии нет. Сигналов нет."
)
ASK_FREELANCE = (
    "Фриланс · изолирован. Своя ссылка оплаты.\n"
    "Не открывает Allo $50, Access и Флагман."
)
ASK_CHECK = (
    "Сверить файл — до оплаты.\n"
    "Покажу суть, решение и векторы. Eval откроется после $490."
)
ASK_SHIFT = (
    "CraftShift. Пост для X и промпт ролика.\n"
    "Производная Metrix AI. Одна ситуация — один объект."
)
ASK_DOOR = "Код двери — 6 символов. Или напишите, что ломается: дверь выдастся сама."
ASK_ARTEFACTS = ASK_SHOP
ASK_MAKING = ASK_SHOP

ASK_CROSS = (
    "Cross. Напишите запрос своими словами.\n"
    "Ищу среди Финансов, Диптеха, Бренда и четырёх слоёв.\n"
    "Ассистент выберет. Упакую в ключи. Седьмой продукт не выдумаю."
)

ASK_ACCESS = ASK_TARIFFS

ASK_MONTH_CAP = (
    "Лимит запросов по тарифу закрыт. $100 = 120. Остальные — по слоту. Новый цикл — снова."
)

POSTS_INTRO = f"Короткие тексты для {HANDLE}.\n{X_URL}"

MENU_CONSULT = "Консультации"
MENU_PRIVATE = "Приватка"
MENU_WORK = "Боты и ядра"
MENU_PROFILE = "Профиль"
MENU_LIFE = "Консультации"
MENU_FLAGSHIP = "Консультации"
MENU_STORE = "Web3 Store"
MENU_TARIFFS = "Тарифы"
MENU_SHIFT = "CraftShift"
MENU_DOOR = "Дверь"
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
MENU_HITS = "Хиты"
MENU_CHECK = "Сверить файл"
MENU_SUB = "Обучение"

ASK_HITS = (
    "Хиты — не сигнальный ассистент.\n"
    "Мувики, которые заслужили данные. 🎞"
)

HELP = (
    "Консультации — суть, решение, варианты. Два режима: под капотом и рекурсивка.\n"
    "Приватка — два режима сразу. Подписка 990 ₽ в месяц.\n"
    "Боты и ядра — большой бот или мелкое ядро. Разраб 3490 ₽.\n"
    "Профиль — дверь, тикер, доступ."
)

DESC = "Консультации, приватка, боты и ядра, профиль."
SHORT = "Суть, решение, варианты. Рекурсивка — файлом."
NAME = "Метрикс АИ бот"
USERNAME = "karimmetrixbot"
