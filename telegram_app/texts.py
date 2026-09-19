"""User-facing Telegram copy. Short, concrete names."""

from __future__ import annotations

from backend.core.voice import BORED_TEXT, FREELANCE_TEXT, START_TEXT
from backend.core.x_posts import HANDLE, X_URL

START = START_TEXT
BORED = BORED_TEXT
FREELANCE = FREELANCE_TEXT

ASK_LIFE = (
    "Флагман. Две строки, не эссе.\n"
    "Что ломается — одной фразой.\n"
    "Что должно сесть — второй.\n"
    "Дальше: 5–20 вопросов, eval, тикер. Файл — после оплаты (кроме $100)."
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
    "Хиты — смотреть бесплатно.\n"
    "Web3 Store — запросы бесплатно.\n\n"
    "Для жизни, бесплатно:\n"
    "· суть одной фразой\n"
    "· решение одной фразой\n"
    "· кастом после 5–20 вопросов\n"
    "· eval — насколько можем помочь\n"
    "· тикер в системе\n"
    "· цепочка в файл\n\n"
    "Потом оплата → товар в Tribute с тикером.\n"
    "Файл: рекурсивная методика + спеки + кодовая надстройка того же движка.\n\n"
    "$100 — 120 мелких задач. Без файла.\n"
    "$490 — Assist. Файл.\n"
    "$1000 — стандарт. Файл.\n"
    "$10 000 — автономный контур в ваш проект. Файл."
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

HELP = (
    "Хиты — конструкция, не сигнал. Смотреть бесплатно.\n"
    "Флагман — две строки, не эссе. Eval, тикер, потом тариф.\n"
    "Web3 Store — запросы бесплатно.\n"
    "Тарифы: $100 без файла · $490 / $1000 / $10 000 — файл."
)

MENU_LIFE = "Флагман"
MENU_FLAGSHIP = "Флагман"
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
MENU_SUB = "Обучение"
MENU_PRIVATE = "Приватка"

ASK_HITS = (
    "Хиты — короткий разбор одной финансовой конструкции. Смотреть бесплатно.\n"
    "Не тикер сделки, не сигнал. Напишите «хит», «глоссарий»."
)

DESC = HELP[:120]
SHORT = "Хиты и Store бесплатно. $100 без файла. Остальное — файл."
NAME = "Метрикс АИ бот"
USERNAME = "karimmetrixbot"
