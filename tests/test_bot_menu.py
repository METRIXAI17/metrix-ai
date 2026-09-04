from telegram_app.menu import menu_action


def test_reply_keyboard_labels():
    assert menu_action("Идеи для жизни") == "life"
    assert menu_action("Торговые боты") == "bots"
    assert menu_action("Конфиги для ремесла") == "craft"
    assert menu_action("Таргет ИИ-агентов") == "target"
    assert menu_action("Каталог магазина") == "shop"


def test_legacy_labels_fold_into_five():
    assert menu_action("In-Out Chain") == "life"
    assert menu_action("Лендинг") == "life"
    assert menu_action("Демо") == "life"
    assert menu_action("Движок") == "craft"
    assert menu_action("Стратегии") == "bots"
    assert menu_action("Агенты") == "target"
    assert menu_action("Посты") == "shop"
    assert menu_action("Мейкинг") == "shop"
    assert menu_action("AI Teammates") == "craft"
    assert menu_action("Artefacts") == "shop"


def test_commands_and_bot_suffix():
    assert menu_action("/life") == "life"
    assert menu_action("/chain") == "life"
    assert menu_action("/landing") == "life"
    assert menu_action("/engine@karimmetrixbot") == "craft"
    assert menu_action("/making") == "shop"
    assert menu_action("/bots") == "bots"
    assert menu_action("/strategies@karimmetrixbot") == "bots"
    assert menu_action("/agents") == "target"
    assert menu_action("/start") == "start"


def test_not_a_menu():
    assert menu_action("SaaS 80 человек без экономики") is None
    assert menu_action("") is None
