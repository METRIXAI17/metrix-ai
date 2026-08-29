from telegram_app.menu import menu_action


def test_reply_keyboard_labels():
    assert menu_action("Лендинг") == "landing"
    assert menu_action("Движок") == "engine"
    assert menu_action("Мейкинг") == "making"


def test_legacy_labels_fold_into_three():
    assert menu_action("Демо") == "landing"
    assert menu_action("Стратегии") == "engine"
    assert menu_action("Агенты") == "engine"
    assert menu_action("Посты") == "making"


def test_commands_and_bot_suffix():
    assert menu_action("/landing") == "landing"
    assert menu_action("/engine@karimmetrixbot") == "engine"
    assert menu_action("/making") == "making"
    assert menu_action("/demo") == "landing"
    assert menu_action("/strategies@karimmetrixbot") == "engine"
    assert menu_action("/agents") == "engine"
    assert menu_action("/start") == "start"


def test_not_a_menu():
    assert menu_action("SaaS 80 человек без экономики") is None
    assert menu_action("") is None
