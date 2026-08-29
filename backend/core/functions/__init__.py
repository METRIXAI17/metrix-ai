from backend.core.functions.creative_assistant import run_creative_assistant
from backend.core.functions.digital_mockup import run_digital_mockup
from backend.core.functions.making_chamber import run_making_function
from backend.core.functions.solution_logger import run_solution_logger

FUNCTIONS = (
    {
        "id": "creative_assistant",
        "title_ru": "Идеи, когда залипаешь",
        "title_en": "Ideas when idle",
        "hit": True,
        "blurb_ru": "Угол и правило для поста или ролика. Не «ещё один чат».",
    },
    {
        "id": "solution_logger",
        "title_ru": "Разбор своих сделок",
        "title_en": "Own-trade review",
        "hit": True,
        "blurb_ru": "Тезис, семья ошибок, что повторять нельзя. Не сигналы.",
    },
    {
        "id": "digital_mockup",
        "title_ru": "Макет вашей работы",
        "title_en": "Work mockup",
        "hit": True,
        "blurb_ru": "Темп, оффер, слоты — чтобы соло-работа вставала без театра.",
    },
    {
        "id": "making_chamber",
        "title_ru": "Камера сборки",
        "title_en": "Making chamber",
        "hit": True,
        "section": "making",
        "blurb_ru": "Неделя, которую можно прожить: событие, прогрев, страх, share, сателлит. Не план.",
    },
)

__all__ = [
    "FUNCTIONS",
    "run_creative_assistant",
    "run_solution_logger",
    "run_digital_mockup",
    "run_making_function",
]
