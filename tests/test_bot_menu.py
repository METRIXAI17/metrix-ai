from telegram_app.menu import menu_action


def test_reply_keyboard_labels():
    assert menu_action("Идеи для жизни") == "flagship"
    assert menu_action("Флагман") == "flagship"
    assert menu_action("Торговые боты") == "bots"
    assert menu_action("Конфиги для ремесла") == "craft"
    assert menu_action("Таргет ИИ-агентов") == "target"
    assert menu_action("Каталог магазина") == "shop"


def test_legacy_labels_fold_into_five():
    assert menu_action("In-Out Chain") == "flagship"
    assert menu_action("Лендинг") == "flagship"
    assert menu_action("Демо") == "flagship"
    assert menu_action("Движок") == "craft"
    assert menu_action("Стратегии") == "bots"
    assert menu_action("Агенты") == "target"
    assert menu_action("Посты") == "shop"
    assert menu_action("Мейкинг") == "shop"
    assert menu_action("AI Teammates") == "craft"
    assert menu_action("Artefacts") == "shop"


def test_commands_and_bot_suffix():
    assert menu_action("/life") == "flagship"
    assert menu_action("/chain") == "flagship"
    assert menu_action("/landing") == "flagship"
    assert menu_action("/engine@karimmetrixbot") == "craft"
    assert menu_action("/making") == "shop"
    assert menu_action("/bots") == "bots"
    assert menu_action("/strategies@karimmetrixbot") == "bots"
    assert menu_action("/agents") == "target"
    assert menu_action("/start") == "start"
    assert menu_action("/flagship") == "flagship"
    assert menu_action("/tariffs") == "tariffs"


def test_hits_and_private():
    assert menu_action("хит") == "hits"
    assert menu_action("конструкции") == "hits"
    assert menu_action("приватка") == "private"
    from telegram_app.bot import main_keyboard, nav_inline
    from telegram_app.hits import weekly_hit, format_hit

    kb = main_keyboard()["keyboard"]
    labels = [cell["text"] for row in kb for cell in row]
    assert labels[0] == "Хиты"
    assert "Флагман" in labels
    assert "Web3 Store" in labels
    assert "Тарифы" in labels
    nav = nav_inline("https://metrix-ai.vercel.app/tg/")
    flat = str(nav)
    assert "m:hits" in flat
    assert "#hits" in flat
    assert "m:flagship" in flat
    assert "m:tariffs" in flat
    assert "v=t4" in flat
    h = format_hit(weekly_hit(0))
    assert "Не рекомендация сделки" in h
    assert len(h) > 400


def test_cross_alias():
    assert menu_action("cross") == "cross"
    assert menu_action("/cross") == "cross"
    assert menu_action("ключи") == "cross"


def test_not_a_menu():
    assert menu_action("SaaS 80 человек без экономики") is None
    assert menu_action("") is None
