from telegram_app.menu import menu_action


def test_reply_keyboard_labels():
    assert menu_action("In-Out Chain") == "chain"
    assert menu_action("AI Teammates") == "teammates"
    assert menu_action("Artefacts") == "artefacts"


def test_legacy_labels_fold_into_three():
    assert menu_action("Лендинг") == "chain"
    assert menu_action("Демо") == "chain"
    assert menu_action("Движок") == "teammates"
    assert menu_action("Стратегии") == "chain"
    assert menu_action("Агенты") == "teammates"
    assert menu_action("Посты") == "artefacts"
    assert menu_action("Мейкинг") == "artefacts"


def test_commands_and_bot_suffix():
    assert menu_action("/chain") == "chain"
    assert menu_action("/landing") == "chain"
    assert menu_action("/engine@karimmetrixbot") == "teammates"
    assert menu_action("/making") == "artefacts"
    assert menu_action("/demo") == "chain"
    assert menu_action("/strategies@karimmetrixbot") == "chain"
    assert menu_action("/agents") == "teammates"
    assert menu_action("/start") == "start"


def test_not_a_menu():
    assert menu_action("SaaS 80 человек без экономики") is None
    assert menu_action("") is None
