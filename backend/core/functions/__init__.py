from backend.core.functions.creative_assistant import run_creative_assistant
from backend.core.functions.digital_mockup import run_digital_mockup
from backend.core.functions.solution_logger import run_solution_logger

FUNCTIONS = (
    {
        "id": "creative_assistant",
        "title_ru": "Творческий ассистент",
        "title_en": "Creative assistant",
        "hit": True,
        "blurb_ru": "Идеи, углы, промпты и правила для роликов — не «ещё один чат».",
    },
    {
        "id": "solution_logger",
        "title_ru": "Solution logger",
        "title_en": "Solution logger",
        "hit": True,
        "blurb_ru": "Полезный разбор своего трейдинга: тезис, семьи ошибок, путь к ордерам.",
    },
    {
        "id": "digital_mockup",
        "title_ru": "Цифровой макет",
        "title_en": "Digital mockup",
        "hit": True,
        "blurb_ru": "Подобие индивидуала: темп, оффер, слоты — быстрый разворот соло-работы.",
    },
)

__all__ = [
    "FUNCTIONS",
    "run_creative_assistant",
    "run_solution_logger",
    "run_digital_mockup",
]
