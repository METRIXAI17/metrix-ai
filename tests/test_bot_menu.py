from telegram_app.menu import menu_action


def test_reply_keyboard_labels():
    assert menu_action("Демо") == "demo"
    assert menu_action("Стратегии") == "strategies"
    assert menu_action("Агенты") == "agents"
    assert menu_action("Посты") == "posts"


def test_commands_and_bot_suffix():
    assert menu_action("/demo") == "demo"
    assert menu_action("/strategies@karimmetrixbot") == "strategies"
    assert menu_action("/agents") == "agents"
    assert menu_action("/start") == "start"


def test_not_a_menu():
    assert menu_action("SaaS 80 человек без экономики") is None
    assert menu_action("") is None
