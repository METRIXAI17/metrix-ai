/**
 * Metrix AI — public surface
 * RU default · EN/RU · earning contour for AI freelancer + client
 * Flow: inbox → status → escalate → Monday report → repeat
 * Engine internals stay off this surface.
 */
window.METRIX_DATA = {
  brand: {
    name: "Metrix AI",
    x: "https://x.com/karimmetrix",
    mark: "assets/metrix-brand-m.jpg",
  },

  /** UI chrome strings — one language pack at a time, no mixed mode */
  ui: {
    en: {
      nav_products: "Products",
      nav_consult: "Consult + TZ",
      nav_tasks: "Slots",
      nav_generate: "Assemble order",
      nav_promo: "Sale talk",
      nav_funding: "Funding",
      nav_product: "Product",
      nav_niches: "Flow layers",
      nav_flagships: "What you get",
      nav_path: "Path",
      nav_pricing: "Pricing",
      nav_system: "Flow",
      hero_badge: "Metrix · door into the stream",
      hero_h1a: "Name the hole.",
      hero_h1b: "Assemble the object.",
      hero_sub:
        "Two demos free. If the object landed — Access holds the contour: inbox, owner, Monday. If not — we do not sell another chat.",
      cta_earn: "Open Access",
      cta_consult: "Consult + TZ",
      cta_chain: "Start the contour",
      chain_step_1: "Inbox",
      chain_step_2: "Status",
      chain_step_3: "Escalate",
      chain_step_4: "Report",
      chain_step_5: "Repeat",
      chain_stepper_lead: "Layers of one stream. Not a list of directions.",
      flow_1: "Inbox",
      flow_1s: "All leads in one list",
      flow_2: "Status",
      flow_2s: "Named owner · N minutes",
      flow_3: "Escalate",
      flow_3s: "If nobody took it",
      flow_4: "Report",
      flow_4s: "Monday: in / on time / burned",
      flow_5: "Repeat",
      flow_5s: "Retainer on the report",
      flow_lead: "Each layer is a spill of the same flow — not idea #5.",
      cta_niches: "Flow layers",
      cta_tasks: "Business tasks",
      cta_generate: "Build a demo",
      cta_card_consult: "Help with earning →",
      cta_pricing: "View tariffs",
      eyebrow_product: "Product",
      offer_title: "What hits the till. What Monday shows.",
      in_label: "Input",
      in_text: "A fuzzy brief: «make a bot», «so leads don't vanish»",
      out_label: "Output",
      out_text: "One contour TZ + Monday report + retainer offer",
      not_pig: "Hole and report before the pipe",
      not_pig_p:
        "Cheap bot = chat. Paid contour = owner + deadline + escalate + weekly leak number. We do not grow traffic. A cheap bot outside looks the same — if you only need chat, do not hire us.",
      eyebrow_system: "One stream",
      system_title: "Flow layers",
      system_lead:
        "Inbox → status → escalate → report → repeat. Hover a ring. Architecture stays inside.",
      layer_hover_hint: "Hover a layer",
      eyebrow_flagships: "What you get",
      flagships_title: "Value, not a catalog of ideas",
      flagships_lead: "Cash, Monday number, hours not burned. Store, CraftShift and the bot stay as rooms of the same door.",
      eyebrow_niches: "Same flow, different spill",
      niches_title: "Where the contour sits",
      niches_lead: "Not ten ideas. Ten places the same leak lives.",
      eyebrow_cards: "Start",
      cards_title: "Assemble the order",
      cards_lead: "One contour or one series. Click a card. No seven-direction list.",
      eyebrow_path: "Path",
      how_title: "How it works",
      how_lead:
        "For the AI freelancer and their client. Assemble the order. Don't lose leads. Don't burn hours on extra branches.",
      worker_eyebrow: "After handoff",
      worker_title: "Stabilise the direction",
      worker_copy:
        "Monday report + 4–8 hours of fixes a month + one channel. Content = their numbers, not an AI blog. Empty numbers → «contour is not run». Not invented success.",
      form_title: "Help with earning",
      form_lead:
        "Describe the hole in your words. We cut TYPE_A contour from TYPE_B series. No number → qualification questions, not a full pack.",
      label_niche: "Where the leak sits",
      label_track: "Track",
      label_x: "X nickname",
      label_telegram: "Telegram",
      label_business: "The brief",
      business_ph: "What arrives, where it lives, who takes it, what burns if nobody takes it.",
      tech_tz: "TZ",
      result_label: "Consult result",
      cta_free_work: "Assemble the contour",
      cta_new: "New brief",
      fw_eyebrow: "Assembly",
      fw_title_default: "Next steps",
      fw_clarify: "Clarifications",
      fw_clarify_hint: "At most three questions. Then assumed, marked ASSUMED.",
      fw_send: "Send",
      fw_checklist: "Acceptance",
      fw_tech: "TZ",
      fw_next: "Next phase →",
      pricing_title: "Pricing",
      pricing_why: "",
      pricing_lead: "",
      pricing_note: "",
      pricing_discount: "Access 3 290 ₽ · пилот 45 000 ₽ · Cross 80 000 ₽",
      tariff_cta: "Help with earning",
      tariff_cta_generate: "Assemble order",
      tariff_cta_consult: "Help with earning",
      tariff_cta_promo: "Sale talk",
      tariff_cta_funding: "Open Funding",
      tariff_cta_later: "After one step",
      funding_title: "Funding · 3 pillars",
      funding_lead:
        "Structural income · assets 1:1 on configured sales · placed-capital coop. Map first. No auto-yield promises.",
      funding_eyebrow: "Funding · partner contour",
      funding_headline: "Project / offer *",
      funding_headline_ph: "E.g. lead inbox contour · capital for a 14-day pilot",
      funding_body: "Business + capital context *",
      funding_body_ph:
        "What you sell, existing sales/pilots, capital size if any, partners, unit numbers…",
      funding_capital: "Capital to place (USD, optional)",
      funding_role: "Your role",
      funding_role_hybrid: "Hybrid",
      funding_role_operator: "Operator",
      funding_role_capital: "Capital partner",
      funding_asset_mode: "Asset attach mode",
      funding_mode_auto: "Auto",
      funding_mode_rental: "Rental",
      funding_mode_percent: "Percent",
      funding_run: "Build funding plan",
      funding_result: "Funding plan",
      funding_launch: "Launch path",
      funding_paid: "Paid quickstart",
      funding_slots: "Capital slots",
      funding_attach: "1:1 attaches",
      funding_levers: "Instant levers",
      after_one_step: "After one step",
      tariff_popular: "Start here",
      footer_tag: " · door · hole and report before the pipe",
      top: "Top",
      close: "Close",
      select: "Select…",
      all_tracks: "All three",
      details: "Details →",
      for_whom: "For whom",
      workers_title: "AI freelancer",
      workers_text:
        "Assemble the order. Don't burn hours on extra branches. Retainer is the Monday report, not a new idea list.",
      clients_title: "Their client",
      clients_text:
        "Leads already exist and die without a name. We do not grow traffic. You see the weekly leak and reaction time.",
      audience_title: "Two sides of one contour",
      audience_lead:
        "Assembler: TZ without extra branches. Client: leads with a name. Same stream.",
      tasks_eyebrow: "Third mode",
      tasks_title: "A slot in the stream",
      tasks_lead:
        "Not a to-do list. One named object: the hole, the artefact, the next paid step.",
      tasks_example_label: "From live briefs",
      try_demo: "View demo",
      demo: "Demo",
      continue: "Continue to consult",
      fair_price: "Price of the hole vs price of the contour",
      generate_title: "Assemble the order",
      generate_lead:
        "One contour TYPE_A or one series TYPE_B. Mixed brief is split. Not seven directions.",
      gen_headline_label: "Order in a few words *",
      gen_headline_ph: "E.g. leads from Telegram vanish · weekly leak number",
      gen_business_label: "What is breaking *",
      gen_business_ph: "Where leads live, who takes them, what happens if nobody takes them…",
      gen_channel_label: "Channel",
      gen_channel_auto: "Auto",
      gen_channel_online: "Online",
      gen_channel_offline: "Offline",
      gen_channel_hybrid: "Hybrid",
      gen_run: "Assemble",
      gen_loading: "Assembling the contour…",
      gen_result: "Result",
      gen_plan: "Plan (as TZ)",
      gen_open_q: "Questions / approvals",
      gen_panel: "What Monday shows",
      gen_quality: "Acceptance",
      gen_expert: "Assumptions (marked)",
      gen_code: "Files of the contour",
      gen_orch: "Where the leak sits",
      gen_stack: "Pipe (last)",
      gen_forecast: "Handoff forecast",
      gen_forecast_lead: "What the runs imply if you approve the contour — not a revenue promise",
      gen_min_chars: "At least 20 characters",
      gen_error: "Error",
      success_go: "Contour can be handed over",
      success_cond: "Need a number or one stream — then assemble",
      form_err: "Where the leak sits + brief (≥20 characters)",
      form_ok: "OK",
      assets_note: "We do not grow traffic. We do not promise revenue. Assets: structure and risk only.",
      auto_note: "You confirm before any paid implementation. Extra branch = hours pack, not the same check.",
      door_eyebrow: "Door",
      door_title: "One code. Store. CraftShift. Bot.",
      door_lead:
        "Same door. Rooms are spills of one stream, not a second product.",
      store_eyebrow: "Metrix Store",
      store_title: "Rooms of one stream",
      store_lead:
        "First result is a table. Think-more adds one constraint — not another essay. Not an idea store.",
      ai_eyebrow: "SKU after a pilot",
      ai_title: "Physical-goods cash cycle",
      ai_lead:
        "One overlay of the same contour for a physical SKU. Not a second brain. Not Access. Not a course.",
      theses_eyebrow: "Process claims",
      theses_title: "Theses on order",
      theses_lead: "One killable process claim. Not a list of directions.",
    },
    ru: {
      nav_products: "Продукты",
      nav_consult: "Консультация + ТЗ",
      nav_tasks: "Слоты",
      nav_generate: "Сборка заказа",
      nav_promo: "Разговор продажи",
      nav_funding: "Фандинг",
      nav_product: "Продукт",
      nav_niches: "Слои потока",
      nav_flagships: "Что получите",
      nav_path: "Путь",
      nav_pricing: "Цены",
      nav_system: "Поток",
      hero_badge: "Metrix · дверь в поток",
      hero_h1a: "Назовите дыру.",
      hero_h1b: "Соберите объект.",
      hero_sub:
        "Два демо бесплатно. Если объект зашёл — Access держит контур: вход, хозяин, понедельник. Если нет — не продаём чат.",
      cta_earn: "Открыть Access",
      cta_consult: "Консультация + ТЗ",
      cta_chain: "Собрать контур",
      chain_step_1: "Вход",
      chain_step_2: "Статус",
      chain_step_3: "Эскалация",
      chain_step_4: "Отчёт",
      chain_step_5: "Повтор",
      chain_stepper_lead: "Слои одного потока. Не список направлений.",
      flow_1: "Вход",
      flow_1s: "Все заявки в один список",
      flow_2: "Статус",
      flow_2s: "Хозяин · N минут",
      flow_3: "Эскалация",
      flow_3s: "Если не взяли",
      flow_4: "Отчёт",
      flow_4s: "Понедельник: пришло / вовремя / сгорело",
      flow_5: "Повтор",
      flow_5s: "Ретейнер на отчёте",
      flow_lead: "Каждый слой — перелив того же потока, не идея №5.",
      cta_niches: "Слои потока",
      cta_tasks: "Бизнес-таски",
      cta_generate: "Собрать демо"
      cta_card_consult: "Помощь в заработке →",
      cta_pricing: "Смотреть тарифы",
      eyebrow_product: "Продукт",
      offer_title: "Что попадёт в кассу. Что видно в понедельник.",
      in_label: "На входе",
      in_text: "Размытый бриф: «сделай бота», «чтобы заявки не терялись»",
      out_label: "На выходе",
      out_text: "Одно ТЗ на контур + отчёт понедельника + оффер ретейнера",
      not_pig: "Дыра и отчёт раньше трубы",
      not_pig_p:
        "Дешёвый бот = чат. Дорогой контур = хозяин + срок + эскалация + недельная цифра потерь. Трафик не растим. Снаружи похоже на бота за 30к — если нужен только чат, нас не берите.",
      eyebrow_system: "Один поток",
      system_title: "Слои потока",
      system_lead:
        "Вход → статус → эскалация → отчёт → повтор. Наведите на кольцо. Архитектура остаётся внутри.",
      layer_hover_hint: "Наведите на слой",
      eyebrow_flagships: "Что получите",
      flagships_title: "Ценность, не каталог идей",
      flagships_lead: "Касса, цифра понедельника, часы не слиты. Стор, CraftShift и бот — комнаты той же двери.",
      eyebrow_niches: "Тот же поток, другой перелив",
      niches_title: "Где сидит контур",
      niches_lead: "Не десять идей. Десять мест, где живёт та же дыра.",
      eyebrow_cards: "Старт",
      cards_title: "Собрать заказ",
      cards_lead: "Один контур или одна серия. Нажмите карточку. Без списка из семи направлений.",
      eyebrow_path: "Путь",
      how_title: "Как это работает",
      how_lead:
        "Для ИИ-фрилансера и его заказчика. Собрать заказ. Не терять заявки. Не слить часы на лишнюю ветку.",
      worker_eyebrow: "После сдачи",
      worker_title: "Стабилизация направления",
      worker_copy:
        "Отчёт понедельника + 4–8 часов правок в месяц + один канал. Контент = их цифры, не блог про ИИ. Пустые цифры → «контур не ведут». Успех не придумываем.",
      form_title: "Помощь в заработке",
      form_lead:
        "Опишите дыру своими словами. Режем TYPE_A-контур и TYPE_B-серию отдельно. Нет числа — вопросы квалификации, не полный пакет.",
      label_niche: "Где сидит дыра",
      label_track: "Трек",
      label_x: "Ник в X",
      label_telegram: "Telegram",
      label_business: "Бриф",
      business_ph: "Что приходит, где живёт, кто берёт, что сгорает если не взяли.",
      tech_tz: "ТЗ",
      result_label: "Результат консультации",
      cta_free_work: "Собрать контур",
      cta_new: "Новый бриф",
      fw_eyebrow: "Сборка",
      fw_title_default: "Следующие шаги",
      fw_clarify: "Уточнения",
      fw_clarify_hint: "Максимум три вопроса. Дальше допущения с пометкой ASSUMED.",
      fw_send: "Отправить",
      fw_checklist: "Приёмка",
      fw_tech: "ТЗ",
      fw_next: "Следующая фаза →",
      pricing_title: "Цены",
      pricing_why: "",
      pricing_lead: "",
      pricing_note: "",
      pricing_discount: "Access 3 290 ₽ · пилот 45 000 ₽ · Cross 80 000 ₽",
      tariff_cta: "Помощь в заработке",
      tariff_cta_generate: "Сборка заказа",
      tariff_cta_consult: "Помощь в заработке",
      tariff_cta_promo: "Разговор продажи",
      tariff_cta_funding: "Открыть фандинг",
      tariff_cta_later: "После одного шага",
      funding_title: "Фандинг · 3 столпа",
      funding_lead:
        "Структурный доход · активы 1:1 к настроенным продажам · кооп размещённого капитала. Сначала карта. Без авто-обещаний доходности.",
      funding_eyebrow: "Фандинг · партнёрский контур",
      funding_headline: "Проект / оффер *",
      funding_headline_ph: "Напр.: контур входящих · капитал под пилот 14 дней",
      funding_body: "Бизнес + контекст капитала *",
      funding_body_ph:
        "Что продаёте, какие продажи/пилоты уже есть, размер капитала, партнёры, unit-цифры…",
      funding_capital: "Капитал к размещению (USD, опционально)",
      funding_role: "Ваша роль",
      funding_role_hybrid: "Гибрид",
      funding_role_operator: "Оператор",
      funding_role_capital: "Капитал-партнёр",
      funding_asset_mode: "Режим attach активов",
      funding_mode_auto: "Авто",
      funding_mode_rental: "Аренда",
      funding_mode_percent: "Процент",
      funding_run: "Собрать план фандинга",
      funding_result: "План фандинга",
      funding_launch: "Путь запуска",
      funding_paid: "Платная часть · quickstart",
      funding_slots: "Слоты капитала",
      funding_attach: "Attach 1:1",
      funding_levers: "Мгновенные рычаги",
      after_one_step: "После одного шага",
      tariff_popular: "Начать отсюда",
      footer_tag: " · дверь · дыра и отчёт раньше трубы",
      top: "Наверх",
      close: "Закрыть",
      select: "Выберите…",
      all_tracks: "Все три",
      details: "Подробнее →",
      for_whom: "Для кого",
      workers_title: "ИИ-фрилансер",
      workers_text:
        "Собрать заказ. Не слить часы на лишнюю ветку. Ретейнер — отчёт понедельника, не список новых идей.",
      clients_title: "Его заказчик",
      clients_text:
        "Заявки уже есть и сгорают без имени. Трафик не растим. Видно недельную потерю и время реакции.",
      audience_title: "Две стороны одного контура",
      audience_lead:
        "Сборщик: ТЗ без лишней ветки. Заказчик: заявки с именем. Тот же поток.",
      tasks_eyebrow: "Третий режим",
      tasks_title: "Слот в потоке",
      tasks_lead:
        "Не список дел. Один именованный объект: дыра, артефакт, следующий платный шаг.",
      tasks_example_label: "Из живых брифов",
      try_demo: "Смотреть демо",
      demo: "Демо",
      continue: "К консультации",
      fair_price: "Цена дыры vs цена контура",
      generate_title: "Сборка заказа",
      generate_lead:
        "Один контур TYPE_A или одна серия TYPE_B. Смешанный бриф режем. Не семь направлений.",
      gen_headline_label: "Заказ в нескольких словах *",
      gen_headline_ph: "Напр.: заявки из Telegram теряются · цифра потерь за неделю",
      gen_business_label: "Что ломается *",
      gen_business_ph: "Где живут заявки, кто берёт, что если не взяли…",
      gen_channel_label: "Канал",
      gen_channel_auto: "Авто",
      gen_channel_online: "Онлайн",
      gen_channel_offline: "Офлайн",
      gen_channel_hybrid: "Гибрид",
      gen_run: "Собрать",
      gen_loading: "Собираем контур…",
      gen_result: "Результат",
      gen_plan: "План (как по ТЗ)",
      gen_open_q: "Вопросы / согласования",
      gen_panel: "Что видно в понедельник",
      gen_quality: "Приёмка",
      gen_expert: "Допущения (помечены)",
      gen_code: "Файлы контура",
      gen_orch: "Где сидит дыра",
      gen_stack: "Труба (последней)",
      gen_forecast: "Прогноз сдачи",
      gen_forecast_lead: "Что означают прогоны, если утвердите контур — не обещание выручки",
      gen_min_chars: "Не меньше 20 символов",
      gen_error: "Ошибка",
      success_go: "Контур можно сдавать",
      success_cond: "Нужно число или один поток — потом сборка",
      form_err: "Где сидит дыра + бриф (≥20 символов)",
      form_ok: "Готово",
      assets_note: "Трафик не растим. Выручку не обещаем. Активы: структура и риск.",
      auto_note: "До платной реализации подтверждаете вы. Лишняя ветка = пакет часов, не тот же чек.",
      door_eyebrow: "Дверь",
      door_title: "Один код. Стор. CraftShift. Бот.",
      door_lead:
        "Та же дверь. Комнаты — переливы одного потока, не второй продукт.",
      store_eyebrow: "Metrix Store",
      store_title: "Комнаты одного потока",
      store_lead:
        "Первый выход — таблица. Think-more добавляет одно ограничение, не ещё одно эссе. Не стор идей.",
      ai_eyebrow: "SKU после пилота",
      ai_title: "Кассовый цикл физического товара",
      ai_lead:
        "Один перелив того же контура под физический SKU. Не второй мозг. Не Access. Не курс.",
      theses_eyebrow: "Тезисы процесса",
      theses_title: "Тезисы на заказ",
      theses_lead: "Одно убиваемое утверждение про процесс. Не список направлений.",
    },
  },

  industries: {
    en: [
      { id: "ai-agencies", name: "AI agencies & studios", short: "Studios", blurb: "Handover a contour, not a platform", icon: "◇", accent: "#5eead4" },
      { id: "api-for-devs", name: "Integrations & features", short: "Pipe", blurb: "Statuses without empty handoff", icon: "⚡", accent: "#7dd3fc" },
      { id: "freelace-d2c", name: "Freelance", short: "Freelance", blurb: "Assemble the order · don't burn hours", icon: "↗", accent: "#67e8f9" },
      { id: "expert-services", name: "Expert services", short: "Consult", blurb: "Hole in the brief, one TZ", icon: "✦", accent: "#c4b5fd" },
      { id: "content-monetize", name: "Content & audience", short: "Series", blurb: "Same style lock, next piece", icon: "◈", accent: "#86efac" },
      { id: "education", name: "Education", short: "Playbook", blurb: "One-page status rules", icon: "◫", accent: "#fda4af" },
      { id: "automation-builders", name: "Automation & no-code", short: "Inbox", blurb: "Hole and report first · bot last", icon: "◎", accent: "#f9a8d4" },
      { id: "cost-ops", name: "Unit economics", short: "Leak", blurb: "Weekly number that burned", icon: "▤", accent: "#fcd34d" },
      { id: "device-assembly", name: "Device assembly", short: "Owner", blurb: "Named owner and a deadline", icon: "⬢", accent: "#fb7185" },
      { id: "asset-decisions", name: "Asset decisions", short: "Risk", blurb: "Structure & risk · no yield promise", icon: "◎", accent: "#e9d5ff" },
    ],
    ru: [
      { id: "ai-agencies", name: "AI-агентства и студии", short: "Студии", blurb: "Сдать контур, не платформу", icon: "◇", accent: "#5eead4" },
      { id: "api-for-devs", name: "Интеграции и фичи", short: "Труба", blurb: "Статусы без пустого перевода", icon: "⚡", accent: "#7dd3fc" },
      { id: "freelace-d2c", name: "Фриланс", short: "Фриланс", blurb: "Собрать заказ · не слить часы", icon: "↗", accent: "#67e8f9" },
      { id: "expert-services", name: "Экспертные услуги", short: "Консалт", blurb: "Дыра в заявке, одно ТЗ", icon: "✦", accent: "#c4b5fd" },
      { id: "content-monetize", name: "Контент и аудитория", short: "Серия", blurb: "Тот же замок стиля, следующий кусок", icon: "◈", accent: "#86efac" },
      { id: "education", name: "Обучение", short: "Регламент", blurb: "Правила статусов на одну страницу", icon: "◫", accent: "#fda4af" },
      { id: "automation-builders", name: "Автоматизация и no-code", short: "Вход", blurb: "Дыра и отчёт раньше бота", icon: "◎", accent: "#f9a8d4" },
      { id: "cost-ops", name: "Себестоимость и unit-economics", short: "Потери", blurb: "Недельная цифра, что сгорело", icon: "▤", accent: "#fcd34d" },
      { id: "device-assembly", name: "Сборка и конфиг устройств", short: "Хозяин", blurb: "Имя хозяина и срок", icon: "⬢", accent: "#fb7185" },
      { id: "asset-decisions", name: "Решения по активам", short: "Риск", blurb: "Структура и риск · без обещания доходности", icon: "◎", accent: "#e9d5ff" },
    ],
  },

  tracks: {
    en: [
      { id: "product", name: "Product", label: "Core / Product", color: "#5eead4" },
      { id: "models", name: "Teammate", label: "Yield / Teammate", color: "#fbbf24" },
      { id: "promotion", name: "Promotion", label: "Promotion", color: "#c4b5fd" },
    ],
    ru: [
      { id: "product", name: "Product", label: "Ядро / Продукт", color: "#5eead4" },
      { id: "models", name: "Teammate", label: "Yield / Напарник", color: "#fbbf24" },
      { id: "promotion", name: "Promotion", label: "Продвижение", color: "#c4b5fd" },
    ],
  },

  whyUsSlides: {
    en: [
      { key: "core", title: "Inbox", text: "All leads in one list. Named owner. N minutes. What burns if nobody takes it." },
      { key: "coop", title: "Contour", text: "One TYPE_A contour or one TYPE_B series. Mixed brief is split. Extra branch = hours pack." },
      { key: "promo", title: "Sale talk", text: "Chat for 30k vs a named leak. We do not grow traffic. Retainer sold at handoff." },
      { key: "yield", title: "Monday", text: "In / taken on time / burned / on whom. Empty numbers → contour is not run." },
    ],
    ru: [
      { key: "core", title: "Вход", text: "Все заявки в один список. Хозяин. N минут. Что сгорает, если не взяли." },
      { key: "coop", title: "Контур", text: "Один TYPE_A-контур или одна TYPE_B-серия. Смешанный бриф режем. Лишняя ветка = пакет часов." },
      { key: "promo", title: "Разговор продажи", text: "Чат за 30к vs потеря с именем. Трафик не растим. Ретейнер продаётся на сдаче." },
      { key: "yield", title: "Понедельник", text: "Пришло / взяли вовремя / сгорело / на ком. Пустые цифры → контур не ведут." },
    ],
  },

  howSteps: {
    en: [
      { n: "01", title: "Brief", text: "Fuzzy text is enough. We pull goal / inbox / artefact / deadline / done-when." },
      { n: "02", title: "One contour", text: "TYPE_A: owner, statuses, escalate, Monday number. TYPE_B: style lock and the first piece." },
      { n: "03", title: "Handover", text: "Files + one-page playbook. Retainer offer at handoff, not after you disappear." },
      { n: "04", title: "Repeat", text: "A: subscription on their weekly numbers. B: next piece in the same lock. Not a new genre." },
    ],
    ru: [
      { n: "01", title: "Бриф", text: "Размытый текст достаточен. Достаём цель / вход / артефакт / срок / как поймём что готово." },
      { n: "02", title: "Один контур", text: "TYPE_A: хозяин, статусы, эскалация, цифра понедельника. TYPE_B: замок стиля и первый кусок." },
      { n: "03", title: "Сдача", text: "Файлы + регламент на страницу. Оффер ретейнера на сдаче, не после исчезновения." },
      { n: "04", title: "Повтор", text: "A: подписка на их цифры недели. B: следующий кусок в том же замке. Не смена жанра." },
    ],
  },

  /** Nested matryoshka layers — outer → center */
  systemLayers: {
    en: [
      {
        id: "capital",
        label: "Repeat · retainer",
        short: "Repeat",
        text: "A: Monday report subscription + 4–8 hours of fixes. B: next piece in the same style lock. Sold at handoff. Not a new direction.",
      },
      {
        id: "marketing",
        label: "Monday report",
        short: "Report",
        text: "In / taken on time / burned / on whom. Empty numbers → contour is not run. We do not become the ads person.",
      },
      {
        id: "coop",
        label: "Escalate",
        short: "Escalate",
        text: "If nobody took it in N minutes — named next owner. Extra branch for «our manager» = hours pack, not the same check.",
      },
      {
        id: "assist",
        label: "Status · owner",
        short: "Status",
        text: "Stages without empty handoff. Named owner. N minutes. Pipe (Telegram / sheet / CRM) comes last.",
      },
      {
        id: "core",
        label: "Inbox",
        short: "Inbox",
        text: "All inboxes → one list. Qualification: leads/week, where they live, who takes them, what burns. No number → questions, not a full TZ.",
      },
    ],
    ru: [
      {
        id: "capital",
        label: "Повтор · ретейнер",
        short: "Повтор",
        text: "A: подписка на отчёт понедельника + 4–8 часов правок. B: следующий кусок в том же замке стиля. Продаётся на сдаче. Не новое направление.",
      },
      {
        id: "marketing",
        label: "Отчёт понедельника",
        short: "Отчёт",
        text: "Пришло / взяли вовремя / сгорело / на ком. Пустые цифры → контур не ведут. Директологом не становимся.",
      },
      {
        id: "coop",
        label: "Эскалация",
        short: "Эскалация",
        text: "Не взяли за N минут — следующий хозяин по имени. Ветка «под нашего менеджера» = пакет часов, не тот же чек.",
      },
      {
        id: "assist",
        label: "Статус · хозяин",
        short: "Статус",
        text: "Стадии без пустого перевода. Хозяин по имени. N минут. Труба (Telegram / таблица / CRM) — последней.",
      },
      {
        id: "core",
        label: "Вход заявок",
        short: "Вход",
        text: "Все входы → один список. Квалификация: заявки/нед, где живут, кто берёт, что сгорает. Нет числа — вопросы, не полное ТЗ.",
      },
    ],
  },

  /** Public surface: no implement prices — commercial hidden (ops-only) */
  pricingTiers: {
    en: [
      {
        id: "access",
        name: "Metrix Access",
        price: "3 290 ₽",
        priceStyle: "soft",
        period: "month · 40 results · eval on each",
        popular: true,
        tagline: "Door · rooms · conversation",
        cta: "access",
        includes: [
          "Eval on every Access run — four axes, not a score theatre",
          "Door: Store, CraftShift, bot, site — one code",
          "Two free objects, then this wall",
          "Not included: signals, Main without a pilot, custom spec",
        ],
      },
      {
        id: "pilot",
        name: "Custom spec pilot",
        price: "45 000 ₽",
        priceStyle: "soft",
        period: "named void · recursive conclusions",
        popular: false,
        tagline: "Under the hood: recursive spec, not a new chat",
        cta: "pilot",
        includes: [
          "Named void, gate, acceptance test",
          "OutcomeContract before Stage 1",
          "Recursive conclusions stay inside — you get the object",
          "Not included: signals, yield, Main without this pilot",
        ],
      },
      {
        id: "cross",
        name: "Cross assist",
        price: "80 000 ₽",
        priceStyle: "soft",
        period: "query → options → keys",
        popular: false,
        tagline: "Search proposed options. Pack into keys.",
        cta: "cross",
        includes: [
          "Query among Finance / Deeptech / Brand + four layers",
          "Assistant picks. Does not invent a seventh product",
          "Packed keys you can hand to a contour",
          "Not included: traffic promise, AI-powered unlock copy",
        ],
      },
    ],
    ru: [
      {
        id: "access",
        name: "Metrix Access",
        price: "3 290 ₽",
        priceStyle: "soft",
        period: "месяц · 40 результатов · eval на каждом",
        popular: true,
        tagline: "Дверь · комнаты · разговор",
        cta: "access",
        includes: [
          "Eval на каждом прогоне Access — четыре оси, не театр баллов",
          "Дверь: Стор, CraftShift, бот, сайт — один код",
          "Два бесплатных объекта, потом эта стена",
          "Не входит: сигналы, Main без пилота, custom spec",
        ],
      },
      {
        id: "pilot",
        name: "Custom spec pilot",
        price: "45 000 ₽",
        priceStyle: "soft",
        period: "именованная дыра · рекурсивные выводы",
        popular: false,
        tagline: "Под капотом: рекурсивная спека, не новый чат",
        cta: "pilot",
        includes: [
          "Именованная дыра, gate, тест приёмки",
          "OutcomeContract до Stage 1",
          "Рекурсивные выводы остаются внутри — вам объект",
          "Не входит: сигналы, доходность, Main без этого пилота",
        ],
      },
      {
        id: "cross",
        name: "Cross assist",
        price: "80 000 ₽",
        priceStyle: "soft",
        period: "запрос → варианты → ключи",
        popular: false,
        tagline: "Ищем среди предложенных. Пакуем в ключи.",
        cta: "cross",
        includes: [
          "Запрос по Финансам / Диптеху / Бренду + четыре слоя",
          "Ассистент выбирает. Седьмой продукт не выдумывает",
          "Ключи, которые можно отдать контуру",
          "Не входит: обещание трафика, AI-powered unlock",
        ],
      },
    ],
  },

  flagshipDetails: {
    en: [
      { id: "core", title: "Assemble the order", text: "Fuzzy brief → one TYPE_A contour or one TYPE_B series. Pipe last. Opens assembly." },
      { id: "coop", title: "Contour + Monday", text: "Owner, statuses, escalate, weekly leak number. Retainer sold at handoff. Opens consult." },
      { id: "promo", title: "Sale talk", text: "Plus and minus named. Chat vs named leak. No traffic promise. Same Promo mode in the header." },
      { id: "assist", title: "Handover kit", text: "Accesses + one-page playbook + retainer offer. After the contour is assembled — not a new idea list." },
      { id: "tune", title: "Hours pack", text: "«One more branch for our manager» is not the same check. Extra = hours pack." },
      { id: "assets", title: "Risk, not yield", text: "Structure and risk only. No automatic yield. We do not grow traffic." },
    ],
    ru: [
      { id: "core", title: "Сборка заказа", text: "Размытый бриф → один TYPE_A-контур или одна TYPE_B-серия. Труба последней. Ведёт в сборку." },
      { id: "coop", title: "Контур + понедельник", text: "Хозяин, статусы, эскалация, недельная цифра потерь. Ретейнер на сдаче. Ведёт в консультацию." },
      { id: "promo", title: "Разговор продажи", text: "Плюс и минус названы. Чат vs потеря с именем. Без обещания трафика. Тот же режим Promo в шапке." },
      { id: "assist", title: "Пакет сдачи", text: "Доступы + регламент на страницу + оффер ретейнера. После сборки контура — не список идей." },
      { id: "tune", title: "Пакет часов", text: "«Ещё ветка под нашего менеджера» — не тот же чек. Сверх пакета = оценка часов." },
      { id: "assets", title: "Риск, не доходность", text: "Только структура и риск. Без авто-доходности. Трафик не растим." },
    ],
  },

  flagships: {
    en: [
      { id: "consult", title: "Consult: hole → TZ", essence: "Named leak + one missing number. Gate: a hole you can name. Price: consult. Not included: traffic growth, Main $2490.", detail: "Diagnose → one contour → Monday report → retainer.", track: "product", accent: "#5eead4", sticker: "Consult", cta: "request" },
      { id: "direction", title: "One stream", essence: "TYPE_A contour or TYPE_B series — pick one. Gate: one stream named. Price: consult. Not included: seven directions.", detail: "Layers of one flow, not a catalog dump.", track: "product", accent: "#67e8f9", sticker: "Stream", cta: "request" },
      { id: "pilot", title: "14-day pilot", essence: "One channel. Signed scope. Gate: a number exists, risk ≠ high. Price: $490–790. Not included: Main.", detail: "Pilot only after the contour is assembled.", track: "models", accent: "#fbbf24", sticker: "Pilot", cta: "later" },
      { id: "main", title: "Physical SKU after pilot", essence: "Same contour on a physical cash cycle. Gate: predicted end ≥ 0.7 and risk ≠ high. Price: $2490. Not included: skip the pilot, courses.", detail: "Ops + catalog project + promo for physical SKUs. One overlay, not a second brain.", track: "product", accent: "#fb7185", sticker: "SKU", cta: "later" },
      { id: "prompts", title: "Playbook + report templates", essence: "One-page status rules and Monday template you run yourself. Gate: TZ ready. Price: inside Main. Not included: a hosted model call.", detail: "Templates, not a lecture.", track: "ops", accent: "#86efac", sticker: "Playbook", cta: "generate" },
      { id: "auto", title: "Qualification answers", essence: "Yes / no / not assembled — in plain language. Gate: sequence started. Price: consult. Not included: pretending an empty slot is advice.", detail: "No number → we stop the full pack.", track: "ops", accent: "#38bdf8", sticker: "Qualify", cta: "request" },
    ],
    ru: [
      { id: "consult", title: "Консультация: дыра → ТЗ", essence: "Названная потеря + одно недостающее число. Gate: дыру можно назвать. Цена: консультация. Не входит: рост трафика, Main $2490.", detail: "Диагноз → один контур → отчёт понедельника → ретейнер.", track: "product", accent: "#5eead4", sticker: "Контур", cta: "request" },
      { id: "direction", title: "Один поток", essence: "TYPE_A-контур или TYPE_B-серия — выбрать одно. Gate: поток назван. Цена: консультация. Не входит: семь направлений.", detail: "Слои одного потока, не свалка каталога.", track: "product", accent: "#67e8f9", sticker: "Поток", cta: "request" },
      { id: "pilot", title: "Пилот 14 дней", essence: "Один канал. Подписанный скоуп. Gate: число есть, risk ≠ high. Цена: $490–790. Не входит: Main.", detail: "Пилот только после сборки контура.", track: "models", accent: "#fbbf24", sticker: "Пилот", cta: "later" },
      { id: "main", title: "Физический SKU после пилота", essence: "Тот же контур на кассовом цикле товара. Gate: predicted end ≥ 0.7 и risk ≠ high. Цена: $2490. Не входит: пропуск пилота, курсы.", detail: "Процессы + проект каталога + промо физических SKU. Один перелив, не второй мозг.", track: "product", accent: "#fb7185", sticker: "SKU", cta: "later" },
      { id: "prompts", title: "Регламент + шаблоны отчёта", essence: "Правила статусов на страницу и шаблон понедельника, запускаете сами. Gate: ТЗ готово. Цена: внутри Main. Не входит: вызов чужой модели.", detail: "Шаблоны, не лекция.", track: "ops", accent: "#86efac", sticker: "Регламент", cta: "generate" },
      { id: "auto", title: "Ответы квалификации", essence: "Да / нет / не собрано — человеческим языком. Gate: последовательность начата. Цена: консультация. Не входит: притворяться, что пустой слот — совет.", detail: "Нет числа — полный пакет не собираем.", track: "ops", accent: "#38bdf8", sticker: "Квалификация", cta: "request" },
    ],
  },

  api: {
    baseUrl: (function resolveApiBase() {
      if (typeof window !== "undefined" && window.METRIX_RUNTIME && window.METRIX_RUNTIME.apiBaseUrl != null) {
        return String(window.METRIX_RUNTIME.apiBaseUrl).replace(/\/$/, "");
      }
      var host = typeof location !== "undefined" ? location.hostname : "";
      if (host === "localhost" || host === "127.0.0.1") {
        return "http://127.0.0.1:8787";
      }
      return "https://metrix-ai-production.up.railway.app";
    })(),
    processPath: "/api/v1/process",
    freeWorkStartPath: "/api/v1/analytics/free-work/start",
    chainB2cStartPath: "/api/v1/analytics/chain/b2c/start",
    freeWorkClarifyPath: "/api/v1/analytics/free-work/clarify",
    freeWorkAdvancePath: "/api/v1/analytics/free-work/advance",
    businessGeneratePath: "/api/v1/analytics/business-generate",
    businessServicesPath: "/api/v1/analytics/business-services",
    fundingPackPath: "/api/v1/analytics/funding-pack",
    promotionPackPath: "/api/v1/analytics/promotion-pack",
    enabled: true,
  },
};

window.METRIX_DATA.getLang = function () {
  try {
    var L = localStorage.getItem("metrix_lang");
    if (L === "en" || L === "ru") return L;
    return "ru";
  } catch (e) {
    return "ru";
  }
};

window.METRIX_DATA.setLang = function (lang) {
  if (lang !== "en" && lang !== "ru") lang = "en";
  try {
    localStorage.setItem("metrix_lang", lang);
  } catch (e) {}
  try {
    document.documentElement.lang = lang;
  } catch (e2) {}
  try {
    document.dispatchEvent(new CustomEvent("metrix:lang", { detail: { lang: lang } }));
  } catch (e3) {}
  return lang;
};

window.METRIX_DATA.t = function (key) {
  var lang = window.METRIX_DATA.getLang();
  var pack = window.METRIX_DATA.ui[lang] || window.METRIX_DATA.ui.en;
  return pack[key] != null ? pack[key] : (window.METRIX_DATA.ui.en[key] || key);
};

window.METRIX_DATA.getIndustries = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.industries[lang] || window.METRIX_DATA.industries.en).slice();
};

window.METRIX_DATA.getTracks = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.tracks[lang] || window.METRIX_DATA.tracks.en).slice();
};

window.METRIX_DATA.getFlagships = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.flagships[lang] || window.METRIX_DATA.flagships.en).slice();
};

window.METRIX_DATA.getFlagshipDetails = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.flagshipDetails[lang] || window.METRIX_DATA.flagshipDetails.en).slice();
};

window.METRIX_DATA.getWhyUs = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.whyUsSlides[lang] || window.METRIX_DATA.whyUsSlides.en).slice();
};

window.METRIX_DATA.getHowSteps = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.howSteps[lang] || window.METRIX_DATA.howSteps.en).slice();
};

window.METRIX_DATA.getSystemLayers = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.systemLayers[lang] || window.METRIX_DATA.systemLayers.en).slice();
};

window.METRIX_DATA.getPricingTiers = function () {
  var lang = window.METRIX_DATA.getLang();
  return (window.METRIX_DATA.pricingTiers[lang] || window.METRIX_DATA.pricingTiers.en).slice();
};
