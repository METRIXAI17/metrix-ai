"""
Answer base per industry × direction (ops / product / promotion).

Used to self-clarify and emit high-quality free-work / consult answers.

Note: founders dual lane (Deep Tech × Branding&VA) is stored but not exposed
in client free-work until partners explicitly enable it.
"""

from __future__ import annotations

from typing import Any


# Directions aligned with market units / category router
DIRECTIONS = ("ops", "product", "promotion")

# ── Per-niche answer packs ───────────────────────────────────────────────────

NICHE_BASE: dict[str, dict[str, Any]] = {
    "ai-agencies": {
        "name": "AI Agencies",
        "hook": "Ops efficiency without agent chaos — Teammate over token swarm.",
        "must_clarify": [
            "weekly_delivery_count",
            "margin_per_engagement",
            "rework_percent",
            "who_owns_client_success",
        ],
        "tasty_proof": "Same agents, cleaner scoreboard → margin up without new headcount.",
        "directions": {
            "ops": {
                "title": "Ops map → Teammate attach",
                "answer": (
                    "Сводим delivery к 3 рычагам: intake, rework, handoff. "
                    "Пустоты в спеках агентов → VVI down. Пилот: 14 дней scoreboard + 1 Teammate lane."
                ),
                "answer_en": (
                    "Collapse delivery to 3 levers: intake, rework, handoff. "
                    "Agent-spec voids → lower VVI. Pilot: 14-day scoreboard + one Teammate lane."
                ),
                "free_work": [
                    "List every recurring client job this week",
                    "Mark which jobs rework >20%",
                    "Name one owner for client success",
                ],
                "success_metric": "Rework hours / delivery hours ↓ 15% in pilot window",
                "out_of_scope_default": ["full multi-agent rewrite", "new model training"],
            },
            "product": {
                "title": "Terminal Teammate pre-dev",
                "answer": (
                    "Продукт = доступ к base layer, не «ещё чатбот». "
                    "Free tech write: scope Teammate steps 1–5, acceptance, DoD. "
                    "Пилот: один niche library + procurement self-gen slice."
                ),
                "answer_en": (
                    "Product = base-layer access, not another chatbot. "
                    "Free tech write: Teammate steps 1–5, acceptance, DoD. "
                    "Pilot: one niche library + procurement self-gen slice."
                ),
                "free_work": [
                    "Pick one niche library to open first",
                    "Write 5 jobs Teammate must not invent",
                    "Define pass/fail for pre-dev day",
                ],
                "success_metric": "Teammate pre-dev kit accepted by signer in ≤10 days",
                "out_of_scope_default": ["full corporate network", "hardware R&D"],
            },
            "promotion": {
                "title": "Buyer fin-model pack",
                "answer": (
                    "Промо = угол продажи Teammate покупающему бизнесу: fin model «почему окупается». "
                    "Не контент ради контента. Free: 1 proof post outline + ROI sketch."
                ),
                "answer_en": (
                    "Promo = sales angle for Teammate buyers: fin model why it pays. "
                    "Not content for content. Free: one proof post outline + ROI sketch."
                ),
                "free_work": [
                    "Name the buyer persona who signs budget",
                    "One number that makes them care (margin/hours)",
                    "One proof artifact you already have",
                ],
                "success_metric": "1 buyer conversation booked from fin-model pack",
                "out_of_scope_default": ["full ads funnel", "agency rebrand"],
            },
        },
    },
    "api-for-devs": {
        "name": "API для разработчиков",
        "hook": "Интеграции и клиентские API: карта вызовов, cost, quality floor.",
        "must_clarify": [
            "monthly_api_usd",
            "top_3_vendors",
            "quality_floor",
            "which_calls_are_hot_path",
        ],
        "tasty_proof": "Один hot path дешевле при том же quality floor — на бумаге, потом пилот.",
        "directions": {
            "ops": {
                "title": "Карта API-вызовов",
                "answer": (
                    "Список интеграций: hot path vs batch. Что режем, что кэшируем, какой пол качества. "
                    "Пилот: один клиентский путь."
                ),
                "answer_en": (
                    "Integration map: hot path vs batch. What to cut, cache, quality floor. "
                    "Pilot: one client path."
                ),
                "free_work": [
                    "Список API за 30 дней по вендорам",
                    "Что клиент замечает как «качество»",
                    "Один hot path в первую очередь",
                ],
                "success_metric": "Hot-path $ / request ↓ при quality ≥ floor",
                "out_of_scope_default": ["полная миграция multi-cloud"],
            },
            "product": {
                "title": "Пакет интеграций под клиента",
                "answer": (
                    "Документ: unit cost, quality band, fallback. Free tech write — "
                    "то, что разработчик отдаёт клиенту как ТЗ."
                ),
                "answer_en": (
                    "Pack: unit cost, quality band, fallback. Free tech write — "
                    "what the dev hands the client as TZ."
                ),
                "free_work": [
                    "Quality band словами клиента",
                    "Fallback когда API отвалился",
                    "Приёмка cost+quality",
                ],
                "success_metric": "Подписанное ТЗ + cost baseline",
                "out_of_scope_default": ["обучение своей модели с нуля"],
            },
            "promotion": {
                "title": "Event / review container",
                "answer": (
                    "Промо через review контейнер: показать чужой burn → Expert path. "
                    "Free: 1 event/thread outline + before/after table."
                ),
                "answer_en": (
                    "Promo via review container: show burn → Expert path. "
                    "Free: one event/thread outline + before/after table."
                ),
                "free_work": [
                    "One anonymized spend horror story",
                    "Before/after table skeleton",
                    "Channel: X vs event vs community",
                ],
                "success_metric": "1 qualified lead from cost-story asset",
                "out_of_scope_default": ["paid ads scale"],
            },
        },
    },
    "cost-engineering": {
        "name": "Cost Engineering",
        "hook": "Simple waste map + Parameter Void Scanner clients can resell.",
        "must_clarify": [
            "waste_categories",
            "client_type",
            "resell_or_internal",
            "current_void_tooling",
        ],
        "tasty_proof": "One void scanner offer that cost-eng shops resell without rebuilding Metrix.",
        "directions": {
            "ops": {
                "title": "Waste map for cost-eng ops",
                "answer": (
                    "Один simple offer: карта пустот параметров. Пилот: 1 клиентский процесс, "
                    "void list + owner + $ impact."
                ),
                "answer_en": (
                    "One simple offer: parameter void map. Pilot: one client process, "
                    "void list + owner + $ impact."
                ),
                "free_work": [
                    "Pick one client process with known waste",
                    "List 5 parameters often missing",
                    "Estimate $ of one void class",
                ],
                "success_metric": "Void list with $ tags accepted by client",
                "out_of_scope_default": ["ERP rewrite"],
            },
            "product": {
                "title": "Parameter Void Scanner product",
                "answer": (
                    "Broad product offer: Void Scanner pack. Free tech write: inputs, "
                    "outputs, resale packaging, acceptance."
                ),
                "answer_en": (
                    "Broad product: Void Scanner pack. Free tech write: inputs, "
                    "outputs, resale packaging, acceptance."
                ),
                "free_work": [
                    "Who resells: you or your client?",
                    "What is the Scanner deliverable file?",
                    "Price band for resale",
                ],
                "success_metric": "Resale-ready Scanner TZ signed",
                "out_of_scope_default": ["hardware sensors"],
            },
            "promotion": {
                "title": "Cost-eng proof angle",
                "answer": (
                    "Промо: один кейс «пустота → $». Free: one-pager + X thread skeleton."
                ),
                "answer_en": (
                    "Promo: one case void → $. Free: one-pager + X thread skeleton."
                ),
                "free_work": [
                    "Pick publishable (or anonymized) case",
                    "One number only on the hero line",
                    "CTA: free void scan / consult",
                ],
                "success_metric": "1 inbound from proof asset",
                "out_of_scope_default": ["conference sponsorship"],
            },
        },
    },
    "chipmaking": {
        "name": "Chipmaking",
        "hook": "Design-loop clarity — three simple offers ops / product / promo.",
        "must_clarify": [
            "design_loop_stage",
            "yield_or_latency_pain",
            "team_size",
            "tool_chain",
        ],
        "tasty_proof": "One loop stage clarified → fewer silent handoff voids.",
        "directions": {
            "ops": {
                "title": "Design-loop ops offer",
                "answer": (
                    "Ops offer: карта handoff между stage. Free: void list + owners. "
                    "Пилот: один stage boundary."
                ),
                "answer_en": (
                    "Ops offer: handoff map across stages. Free: void list + owners. "
                    "Pilot: one stage boundary."
                ),
                "free_work": [
                    "Name stages in your design loop",
                    "Where specs go silent",
                    "Who owns each boundary",
                ],
                "success_metric": "Handoff voids cut on one boundary",
                "out_of_scope_default": ["fab process change"],
            },
            "product": {
                "title": "Chip loop product pack",
                "answer": (
                    "Product: parameter management + virtual chip templates. "
                    "Free tech write: chip config language + acceptance."
                ),
                "answer_en": (
                    "Product: parameter management + virtual chip templates. "
                    "Free tech write: chip config language + acceptance."
                ),
                "free_work": [
                    "List config dimensions you sell/use",
                    "What must never be free-form",
                    "Acceptance for a config pack",
                ],
                "success_metric": "Config pack TZ accepted",
                "out_of_scope_default": ["physical mask set"],
            },
            "promotion": {
                "title": "Chip clarity promo",
                "answer": (
                    "Промо: «clarity of loop» как offer. Free: 1 diagram + caption for X/LinkedIn."
                ),
                "answer_en": (
                    "Promo: loop clarity as offer. Free: one diagram + caption for X/LinkedIn."
                ),
                "free_work": [
                    "One diagram of the loop (even rough)",
                    "One pain sentence buyers nod to",
                    "CTA to free consult",
                ],
                "success_metric": "1 design-lead conversation",
                "out_of_scope_default": ["trade show booth"],
            },
        },
    },
    "telecom": {
        "name": "Telecom",
        "hook": "ARPU, churn, SLA SKUs — linguistic ops + signal cooperation.",
        "must_clarify": [
            "arpu_or_churn_focus",
            "sla_skus",
            "care_vs_core_split",
            "support_script_pain",
        ],
        "tasty_proof": "One intent → one QoS class → one owner — care and core stop fighting.",
        "directions": {
            "ops": {
                "title": "Care × core ops",
                "answer": (
                    "Ops: linguistic intent ↔ network class. Free: intent table + owner map. "
                    "Пилот: 1 intent class."
                ),
                "answer_en": (
                    "Ops: linguistic intent ↔ network class. Free: intent table + owner map. "
                    "Pilot: one intent class."
                ),
                "free_work": [
                    "Top 5 support intents",
                    "Which hit network vs pure care",
                    "Owner per intent",
                ],
                "success_metric": "1 intent class with SLA + owner",
                "out_of_scope_default": ["RAN redesign"],
            },
            "product": {
                "title": "SLA SKU product",
                "answer": (
                    "Product: SKU вокруг SLA/intent. Free tech write: SKU sheet + acceptance."
                ),
                "answer_en": (
                    "Product: SKU around SLA/intent. Free tech write: SKU sheet + acceptance."
                ),
                "free_work": [
                    "Current SKUs that confuse care",
                    "One SKU to clarify first",
                    "Pass/fail for SKU sheet",
                ],
                "success_metric": "SKU sheet signed for one offer",
                "out_of_scope_default": ["billing system rewrite"],
            },
            "promotion": {
                "title": "Zone offer promo",
                "answer": (
                    "Промо: network zone offers. Free: 1 zone story + retention angle."
                ),
                "answer_en": (
                    "Promo: network zone offers. Free: one zone story + retention angle."
                ),
                "free_work": [
                    "Zone or segment to feature",
                    "Churn reason in one line",
                    "Offer that answers that reason",
                ],
                "success_metric": "1 retention/offer test live",
                "out_of_scope_default": ["national brand campaign"],
            },
        },
    },
    "device-assembly": {
        "name": "Device assembly",
        "hook": "Stations & configs that scale — less tribal knowledge on the line.",
        "must_clarify": [
            "stations_count",
            "config_variants",
            "rework_rate",
            "doc_vs_tribal",
        ],
        "tasty_proof": "One station config pack that a new hire can follow on day 1.",
        "directions": {
            "ops": {
                "title": "Station ops clarity",
                "answer": (
                    "Ops: station voids + rework. Free: station map + missing params. "
                    "Пилот: 1 station."
                ),
                "answer_en": (
                    "Ops: station voids + rework. Free: station map + missing params. "
                    "Pilot: one station."
                ),
                "free_work": [
                    "List stations in line order",
                    "Where rework spikes",
                    "What is only in someone's head",
                ],
                "success_metric": "Station pack used once without tribal help",
                "out_of_scope_default": ["new line hardware"],
            },
            "product": {
                "title": "Config pack product",
                "answer": (
                    "Product: config packs per device family. Free tech write: "
                    "variants, tolerances, acceptance."
                ),
                "answer_en": (
                    "Product: config packs per device family. Free tech write: "
                    "variants, tolerances, acceptance."
                ),
                "free_work": [
                    "Device families you assemble",
                    "Config dimensions",
                    "Acceptance test today",
                ],
                "success_metric": "One family config TZ accepted",
                "out_of_scope_default": ["ERP/MES full replace"],
            },
            "promotion": {
                "title": "Line proof promo",
                "answer": (
                    "Промо: before/after station clarity. Free: 1 photo/story + metric."
                ),
                "answer_en": (
                    "Promo: before/after station clarity. Free: one photo/story + metric."
                ),
                "free_work": [
                    "One safe-to-share station story",
                    "Rework number if known",
                    "CTA to free station map",
                ],
                "success_metric": "1 ops-lead conversation",
                "out_of_scope_default": ["trade magazine buy"],
            },
        },
    },
    "asset-decisions": {
        "name": "Asset decisions",
        "hook": "AI for asset management decisions — cognition · monitoring · strategies. Autoliquidity.",
        "badge": "Автоликвидность",
        "must_clarify": [
            "capital_band",
            "horizon",
            "key_metric_today",
            "what_you_refuse_to_do",
        ],
        "tasty_proof": "One situation pack: market model + risk language + do-not-do list — deals still yours.",
        "directions": {
            "ops": {
                "title": "Key metric + risk map",
                "answer": (
                    "Автоликвидность: определяем ключевую метрику, модель её изменения, риск-рамку. "
                    "Не «бот торгует», а поддержка решений. Free: metric card + what-not-to-do."
                ),
                "answer_en": (
                    "Autoliquidity: key metric, change model, risk frame. "
                    "Decision support — not unmanaged auto-trading. Free: metric card + do-not-do list."
                ),
                "free_work": [
                    "Name capital band and horizon",
                    "What metric would prove the model works",
                    "Three actions you refuse forever",
                ],
                "success_metric": "Signed key metric + risk rules for pilot window",
                "out_of_scope_default": ["custody of funds", "guaranteed yield", "unattended live trading"],
            },
            "product": {
                "title": "Situation strategy pack",
                "answer": (
                    "Продукт: готовые модели рынка под ситуацию + логический/риск разбор. "
                    "Подписка или разовая программа. Менеджмент сделок — у клиента. Work by TZ."
                ),
                "answer_en": (
                    "Product: situation market models + logical/risk analysis. "
                    "One-shot or subscription. Client keeps deal management. Work by TZ."
                ),
                "free_work": [
                    "One market situation you face now",
                    "Data sources you trust",
                    "Pass/fail for a strategy draft",
                ],
                "success_metric": "One strategy pack accepted without auto-execution clause",
                "out_of_scope_default": ["broker integration with write access", "profit SLA"],
            },
            "promotion": {
                "title": "Private-room narrative",
                "answer": (
                    "Промо аккуратно: base mechanisms (когнитивка, мониторинг, генерация стратегий). "
                    "Приватка после теста. Без гарантий. Free: 1 post outline + disclaimers."
                ),
                "answer_en": (
                    "Promo carefully: base mechanisms (cognition, monitoring, strategy gen). "
                    "Private room after test. No guarantees. Free: one post outline + disclaimers."
                ),
                "free_work": [
                    "Audience who already has capital or seeks private room",
                    "One honest non-guarantee line",
                    "CTA to free metric card",
                ],
                "success_metric": "1 private-room conversation booked",
                "out_of_scope_default": ["public yield promises", "signal-channel hype"],
            },
        },
    },
    "d2c-offramp": {
        "name": "D2C · freelace offramp",
        "hook": "Idea → freelace-ready document → market → optional terminal agent. Autoliquidity.",
        "badge": "Автоликвидность",
        "must_clarify": [
            "idea_one_liner",
            "skills_you_sell",
            "exchange_or_channel",
            "agent_allowed_yes_no",
        ],
        "tasty_proof": "Document that matches a live freelace problem and can be handed to a terminal agent.",
        "directions": {
            "ops": {
                "title": "Idea → brief → match",
                "answer": (
                    "Ops: структурируем сырую идею в brief. Базовый поиск заказов можно автоматизировать. "
                    "Free: 1 document pack under a real exchange problem shape."
                ),
                "answer_en": (
                    "Ops: structure raw idea into a brief. Basic order search can be automated. "
                    "Free: one document pack shaped like a live exchange problem."
                ),
                "free_work": [
                    "Write the incomplete idea in 5 sentences",
                    "Name exchange or channel",
                    "What you will not automate",
                ],
                "success_metric": "1 document matches a live gig shape",
                "out_of_scope_default": ["full account takeover on freelace platforms"],
            },
            "product": {
                "title": "Workspace + agent handoff",
                "answer": (
                    "Продукт: workspace D2C. Клиент платит за творческое многовариативное решение; "
                    "терминальный агент исполняет принятый документ. Free tech write: scope + DoD + handoff."
                ),
                "answer_en": (
                    "Product: D2C workspace. Client pays for creative multi-variant work; "
                    "terminal agent executes the accepted document. Free tech write: scope + DoD + handoff."
                ),
                "free_work": [
                    "Creative layer only you can do",
                    "What the agent must not invent",
                    "Acceptance checklist for the doc",
                ],
                "success_metric": "Handoff kit accepted; agent dry-run once",
                "out_of_scope_default": ["unsupervised client messaging", "payment fraud paths"],
            },
            "promotion": {
                "title": "Document not vinaigrette",
                "answer": (
                    "Промо против YouTube-винегрета: ценность = документ, изменение = цифровой продукт + агент. "
                    "Free: 1 proof post — before (idea) / after (sold or accepted doc)."
                ),
                "answer_en": (
                    "Promo vs YouTube vinaigrette: value = document, change = digital product + agent. "
                    "Free: one proof post — before (idea) / after (sold or accepted doc)."
                ),
                "free_work": [
                    "One anonymized before/after",
                    "One sentence of clear value",
                    "CTA to free workspace brief",
                ],
                "success_metric": "1 outreach reply or freelace shortlist",
                "out_of_scope_default": ["30-min empty hype videos as the product"],
            },
        },
    },
    "freelace-d2c": {
        "name": "Фриланс и D2C-офферы",
        "hook": "Идея → документ под заказ → передача исполнителю или агенту.",
        "badge": "Автоликвидность",
        "must_clarify": ["idea_one_liner", "skills_you_sell", "channel", "agent_yes_no"],
        "tasty_proof": "Документ, совпадающий с формой живого заказа.",
        "directions": {
            "ops": {
                "title": "Идея → brief",
                "answer": "Сырую идею собираем в 1-страничный brief и оффер. Можно выложить или отдать исполнителю.",
                "answer_en": "Raw idea → one-page brief and offer. Publish or hand to executor.",
                "free_work": ["5 предложений об идее", "Канал продаж", "Что не автоматизируем"],
                "success_metric": "1 документ совпал с формой заказа",
                "out_of_scope_default": ["захват аккаунтов на биржах"],
            },
            "product": {
                "title": "Пакет handoff",
                "answer": "Документ + DoD + что агент не выдумывает. Free tech write: scope и приёмка.",
                "answer_en": "Document + DoD + agent must-not invent. Free tech write: scope and acceptance.",
                "free_work": ["Творческий слой только ваш", "Что агент не трогает", "Чеклист приёмки"],
                "success_metric": "Handoff-пакет принят",
                "out_of_scope_default": ["авто-сообщения клиенту без вас"],
            },
            "promotion": {
                "title": "Документ, не винегрет",
                "answer": "Ценность = оформленное решение. Free: before/after — идея vs принятый пакет.",
                "answer_en": "Value = packaged decision. Free: before/after — idea vs accepted pack.",
                "free_work": ["Один before/after", "Одно предложение ценности", "CTA на brief"],
                "success_metric": "1 ответ на outreach или shortlist",
                "out_of_scope_default": ["пустой хайп как продукт"],
            },
        },
    },
    "expert-services": {
        "name": "Экспертные услуги",
        "hook": "Упаковка оффера: обещание, пакет, цена, возражения.",
        "must_clarify": ["who_buys", "result_promise", "price_band", "delivery_hours"],
        "tasty_proof": "Один продаваемый пакет вместо «созвонимся».",
        "directions": {
            "ops": {
                "title": "Карта услуги",
                "answer": "Кто платит, какой результат, сколько часов. Free: 1-страничный оффер.",
                "answer_en": "Who pays, what result, how many hours. Free: one-page offer.",
                "free_work": ["Кто подписывает", "Результат за 30 дней", "Часы на доставку"],
                "success_metric": "Оффер отправлен 3 людям",
                "out_of_scope_default": ["личный бренд с нуля за неделю"],
            },
            "product": {
                "title": "Пакет услуги",
                "answer": "3 модуля, цена, что не входит. Free tech write: ТЗ на доставку.",
                "answer_en": "3 modules, price, out of scope. Free tech write: delivery TZ.",
                "free_work": ["3 модуля", "Цена", "Out of scope"],
                "success_metric": "Пакет принят 1 клиентом или prepay",
                "out_of_scope_default": ["полная воронка ads"],
            },
            "promotion": {
                "title": "Угол продажи",
                "answer": "Один proof + CTA на пакет. Не контент ради контента.",
                "answer_en": "One proof + CTA to the pack. Not content for content.",
                "free_work": ["1 proof", "1 CTA", "Канал"],
                "success_metric": "1 созвон с пакетом на столе",
                "out_of_scope_default": ["daily posting machine"],
            },
        },
    },
    "ecommerce": {
        "name": "Онлайн-магазины",
        "hook": "Оффер, unit-экон., где теряется маржа.",
        "must_clarify": ["aov", "margin", "traffic_source", "top_sku"],
        "tasty_proof": "Один SKU с ясной маржой и оффером.",
        "directions": {
            "ops": {
                "title": "Unit-экон. карта",
                "answer": "AOV, маржа, возвраты, реклама. Free: leak-map на 1 странице.",
                "answer_en": "AOV, margin, returns, ads. Free: one-page leak map.",
                "free_work": ["AOV", "Маржа top SKU", "CAC если есть"],
                "success_metric": "1 leak закрыт на бумаге",
                "out_of_scope_default": ["полный редизайн магазина"],
            },
            "product": {
                "title": "Оффер SKU",
                "answer": "Упаковка top SKU: обещание, бандл, цена. Free: оффер-лист.",
                "answer_en": "Top SKU pack: promise, bundle, price. Free: offer sheet.",
                "free_work": ["Top SKU", "Обещание", "Цена/бандл"],
                "success_metric": "Оффер выложен или протестирован",
                "out_of_scope_default": ["новый бренд с нуля"],
            },
            "promotion": {
                "title": "Угол трафика",
                "answer": "Один канал + proof. Free: 1 креатив-рамка под оффер.",
                "answer_en": "One channel + proof. Free: one creative frame for the offer.",
                "free_work": ["Канал", "Proof", "CTA"],
                "success_metric": "1 тест канала",
                "out_of_scope_default": ["масштаб ads без unit-экон."],
            },
        },
    },
    "content-monetize": {
        "name": "Контент и аудитория",
        "hook": "Монетизация без размытия: один оффер к аудитории.",
        "must_clarify": ["audience_size", "platform", "offer_today", "ticket"],
        "tasty_proof": "Один платный шаг (гайд, созвон, продукт) с ясной ценой.",
        "directions": {
            "ops": {
                "title": "Карта монетизации",
                "answer": "Аудитория → касание → оффер. Free: 1 путь к оплате.",
                "answer_en": "Audience → touch → offer. Free: one path to payment.",
                "free_work": ["Размер аудитории", "Платформа", "Текущий оффер"],
                "success_metric": "1 оплата по новому пути",
                "out_of_scope_default": ["рост подписчиков как единственная цель"],
            },
            "product": {
                "title": "Цифровой продукт",
                "answer": "Гайд/пакет/созвон: scope и цена. Free tech write: структура продукта.",
                "answer_en": "Guide/pack/call: scope and price. Free tech write: product structure.",
                "free_work": ["Формат", "Цена", "Результат для покупателя"],
                "success_metric": "Продукт выложен",
                "out_of_scope_default": ["ежедневный контент-завод"],
            },
            "promotion": {
                "title": "Анонс",
                "answer": "1 пост/сторис с оффером. Free: текст анонса.",
                "answer_en": "One post/story with offer. Free: announcement copy.",
                "free_work": ["Канал", "Дата", "CTA"],
                "success_metric": "1 анонс + 1 ответ",
                "out_of_scope_default": ["агентство SMM"],
            },
        },
    },
    "education": {
        "name": "Курсы и обучение",
        "hook": "Программа → продаваемый пакет с приёмкой.",
        "must_clarify": ["audience", "outcome", "modules", "price"],
        "tasty_proof": "3 модуля + цена + для кого — один пакет.",
        "directions": {
            "ops": {
                "title": "Карта курса",
                "answer": "Для кого, какой исход, сколько модулей. Free: программа на 1 странице.",
                "answer_en": "Who, outcome, modules. Free: one-page program.",
                "free_work": ["Аудитория", "Исход", "Число модулей"],
                "success_metric": "Программа утверждена",
                "out_of_scope_default": ["LMS с нуля"],
            },
            "product": {
                "title": "Пакет курса",
                "answer": "Оффер + модули + приёмка. Free tech write: структура.",
                "answer_en": "Offer + modules + acceptance. Free tech write: structure.",
                "free_work": ["3 модуля", "Цена", "Что не входит"],
                "success_metric": "Страница продаж или пресейл",
                "out_of_scope_default": ["запись 40 часов видео"],
            },
            "promotion": {
                "title": "Пресейл",
                "answer": "1 анонс + waitlist. Free: текст пресейла.",
                "answer_en": "One announcement + waitlist. Free: presale copy.",
                "free_work": ["Канал", "Дата старта", "CTA"],
                "success_metric": "N заявок в waitlist",
                "out_of_scope_default": ["вебинарная машина"],
            },
        },
    },
    "saas-founders": {
        "name": "SaaS и цифровые продукты",
        "hook": "Один пилот, одна метрика, один оффер.",
        "must_clarify": ["icp", "activation", "price", "blocker"],
        "tasty_proof": "Pilot slice с success metric, не «весь продукт».",
        "directions": {
            "ops": {
                "title": "Activation map",
                "answer": "Где пользователь застревает. Free: 5 шагов onboarding.",
                "answer_en": "Where users stick. Free: 5 onboarding steps.",
                "free_work": ["ICP", "Activation event", "Текущий blocker"],
                "success_metric": "Activation ↑ на пилоте",
                "out_of_scope_default": ["rewrite всего продукта"],
            },
            "product": {
                "title": "Pilot vertical",
                "answer": "Узкий slice + DoD. Free tech write: scope пилота.",
                "answer_en": "Narrow slice + DoD. Free tech write: pilot scope.",
                "free_work": ["Slice", "DoD", "Цена пилота"],
                "success_metric": "1 пилот-клиент",
                "out_of_scope_default": ["enterprise SSO сразу"],
            },
            "promotion": {
                "title": "Оффер пилота",
                "answer": "1 страница: кому, зачем, цена. Free: текст оффера.",
                "answer_en": "One page: who, why, price. Free: offer copy.",
                "free_work": ["ICP", "Proof", "CTA"],
                "success_metric": "3 разговора с ICP",
                "out_of_scope_default": ["Product Hunt ради хайпа"],
            },
        },
    },
    "automation-builders": {
        "name": "Автоматизация и no-code",
        "hook": "Сценарии, которые ведут к доходу, не к «красивым схемам».",
        "must_clarify": ["process", "hours_saved", "revenue_link", "tools"],
        "tasty_proof": "Один сценарий: вход → шаг → оплачиваемый результат.",
        "directions": {
            "ops": {
                "title": "Карта процесса",
                "answer": "Где часы и деньги. Free: 1 сценарий as-is / to-be.",
                "answer_en": "Where hours and money. Free: one as-is / to-be scenario.",
                "free_work": ["Процесс", "Часы в неделю", "Связь с деньгами"],
                "success_metric": "1 сценарий запущен",
                "out_of_scope_default": ["автоматизация всего бизнеса"],
            },
            "product": {
                "title": "Сценарий-продукт",
                "answer": "Пакет: входные данные, шаги, выход. Free tech write: ТЗ сценария.",
                "answer_en": "Pack: inputs, steps, output. Free tech write: scenario TZ.",
                "free_work": ["Инструменты", "Выход", "Приёмка"],
                "success_metric": "ТЗ принято",
                "out_of_scope_default": ["кастомный SaaS"],
            },
            "promotion": {
                "title": "Кейс",
                "answer": "Before/after часов. Free: 1 кейс-карточка.",
                "answer_en": "Before/after hours. Free: one case card.",
                "free_work": ["До", "После", "CTA"],
                "success_metric": "1 лид с кейса",
                "out_of_scope_default": ["YouTube-серия без оффера"],
            },
        },
    },
    "cost-ops": {
        "name": "Себестоимость и unit-economics",
        "hook": "Где утекают деньги — карта без обрезания способности.",
        "must_clarify": ["revenue", "cogs", "fixed", "biggest_leak"],
        "tasty_proof": "1-page leak map + что не режем.",
        "directions": {
            "ops": {
                "title": "Leak map",
                "answer": "Доходы, COGS, фикс, топ-утечка. Free: 1 страница.",
                "answer_en": "Revenue, COGS, fixed, top leak. Free: one page.",
                "free_work": ["Выручка", "COGS", "Главная утечка"],
                "success_metric": "1 утечка закрыта планом",
                "out_of_scope_default": ["полный audit 5 лет"],
            },
            "product": {
                "title": "Пакет unit-экон.",
                "answer": "Шаблон метрик + правила. Free tech write: scoreboard.",
                "answer_en": "Metric template + rules. Free tech write: scoreboard.",
                "free_work": ["3 метрики", "Частота", "Owner"],
                "success_metric": "Scoreboard живёт 14 дней",
                "out_of_scope_default": ["ERP внедрение"],
            },
            "promotion": {
                "title": "Waste-killer card",
                "answer": "1 кейс «было/стало». Free: карточка.",
                "answer_en": "One before/after card. Free: case card.",
                "free_work": ["Цифра", "Действие", "CTA"],
                "success_metric": "1 разговор с buyer",
                "out_of_scope_default": ["рекламный бюджет"],
            },
        },
    },
}

# Aliases for legacy industry ids
NICHE_BASE["cloud-economy"] = NICHE_BASE["api-for-devs"]
NICHE_BASE["cost-engineering"] = NICHE_BASE["cost-ops"]
NICHE_BASE["d2c-offramp"] = NICHE_BASE["freelace-d2c"]


# Dual founders lane — tasty for Karim (deep tech) + Andryusha (branding/VA)
FOUNDERS_LANE: dict[str, Any] = {
    "id": "founders_dual",
    "title": "Deep Tech × Branding&VA",
    "for": ["@karimmetrix", "@andrewsmm1"],
    "hook": (
        "Один free-work поток: Karim закрывает assembly/tech write/pilot gate, "
        "Andryusha — Phenomenon→Notation→Object. Клиент видит вкус: "
        "не «ещё ИИ», а named virtual asset + working TZ."
    ),
    "hook_en": (
        "One free-work stream: Karim owns assembly/tech write/pilot gate, "
        "Andryusha owns Phenomenon→Notation→Object. Client taste: "
        "not another AI — a named virtual asset + working TZ."
    ),
    "joint_deliverables_free": [
        {
            "id": "va_name_seed",
            "owner": "@andrewsmm1",
            "title": "VA name seed (Notation)",
            "desc": "3 name candidates for the client's anomaly → boundaries doc (.va style)",
        },
        {
            "id": "tech_tz_spine",
            "owner": "@karimmetrix",
            "title": "Tech TZ spine",
            "desc": "Problem / scope / acceptance / metrics — terminal specs draft",
        },
        {
            "id": "object_lockup",
            "owner": "@andrewsmm1",
            "title": "Object lockup v0",
            "desc": "One visual token + one-liner that matches the TZ spine",
        },
        {
            "id": "pilot_charter_dual",
            "owner": "both",
            "title": "Pilot charter (dual sign)",
            "desc": "In/out scope + success metric + brand constraint (what naming must not break)",
        },
    ],
    "tasty_moments": [
        "Клиент получает **имя + объект** раньше, чем paid pilot — бренд и tech идут вместе.",
        "X-ready: 1 crystal visual (Andryusha) + 1 mechanism line (Karim) = post без LLM-шума.",
        "Excel chain live: Phenomenon (brief) → Notation (name) → Object (VA) → reverse branding check.",
        "Shared win metric: free work → signed pilot intent within 14 days.",
    ],
    "clarifications_for_pair": [
        "client_anomaly_one_sentence",
        "must_not_look_like",
        "tech_constraint_hard",
        "brand_tone_band",
    ],
}


# Free work day phases (client-facing)
FREE_WORK_PHASES = (
    {
        "id": "D0_1_start",
        "days": "0–1",
        "title_ru": "Старт",
        "title_en": "Start",
        "actions": [
            {"n": 1, "ru": "Заполнить brief: бизнес, ниша, цель, что уже есть", "en": "Fill brief: business, niche, goal, what you already have", "result_ru": "Текст ≥20 символов", "result_en": "Text ≥20 chars"},
            {"n": 2, "ru": "Указать industry", "en": "Set industry", "result_ru": "Корректный market unit", "result_en": "Correct market unit"},
            {"n": 3, "ru": "Приложить числа (бюджет, SLA, конверсия)", "en": "Attach numbers (budget, SLA, conversion)", "result_ru": "Меньше НЕОПРЕДЕЛЕНО", "result_en": "Fewer UNDEFINED"},
            {"n": 4, "ru": "Назначить signer (ТОЧНО ДА/НЕТ)", "en": "Name signer (CERTAIN YES/NO)", "result_ru": "Human-authorized acceptance", "result_en": "Human-authorized acceptance"},
            {"n": 5, "ru": "(Опц.) change-prep: что менять нельзя", "en": "(Opt.) change-prep: what must not change", "result_ru": "Constraint map", "result_en": "Constraint map"},
        ],
        "system": "Step A — params + indirect CY/CN/U",
    },
    {
        "id": "D1_4_tests",
        "days": "1–4",
        "title_ru": "Тесты неопределённостей (Super Speed)",
        "title_en": "Uncertainty tests (Super Speed)",
        "actions": [
            {"n": 6, "ru": "Пройти quiz по каждому UNDEFINED", "en": "Complete quiz per UNDEFINED", "result_ru": "Assembly растёт", "result_en": "Assembly rises"},
            {"n": 7, "ru": "Отвечать ТОЧНО ДА / ТОЧНО НЕТ / НЕ ЗНАЮ", "en": "Answer CERTAIN YES / NO / UNKNOWN", "result_ru": "Чистые статусы", "result_en": "Clean statuses"},
            {"n": 8, "ru": "Для metric/timeline/resource — числа или «не знаю»", "en": "For metric/timeline/resource — numbers or unknown", "result_ru": "Magnitude slots", "result_en": "Magnitude slots"},
            {"n": 9, "ru": "На «сборку» — 2–3 условия", "en": "For assembly — 2–3 conditions", "result_ru": "Assembly map", "result_en": "Assembly map"},
        ],
        "system": "Step B — tests, assembly (not heat), Super Program",
    },
    {
        "id": "D3_10_techwrite",
        "days": "3–10",
        "title_ru": "Tech write (бесплатно)",
        "title_en": "Tech write (free)",
        "actions": [
            {"n": 10, "ru": "Прочитать terminal specs (TZ, pilot charter, metrics)", "en": "Read terminal specs (TZ, pilot charter, metrics)", "result_ru": "Понимание scope", "result_en": "Scope understanding"},
            {"n": 11, "ru": "Замечания по problem / scope / acceptance", "en": "Notes on problem / scope / acceptance", "result_ru": "Rework round 1", "result_en": "Rework round 1"},
            {"n": 12, "ru": "Подтвердить out of scope (ТОЧНО НЕТ)", "en": "Confirm out of scope (CERTAIN NO)", "result_ru": "Защита пилота", "result_en": "Pilot protection"},
            {"n": 13, "ru": "Согласовать 1 success metric (подпись signer)", "en": "Agree 1 success metric (signer)", "result_ru": "Gate пилота", "result_en": "Pilot gate"},
        ],
        "system": "phased insert tech write (ops rules R4)",
    },
)


def _pick_direction(track: str | None, natural: str | None = None) -> str:
    t = (track or natural or "ops").lower()
    if t in ("models", "teammate"):
        return "product"
    if t in DIRECTIONS:
        return t
    if t == "all":
        return natural if natural in DIRECTIONS else "ops"
    return "ops"


class NicheAnswerBase:
    """Resolve quality answers + clarification needs per niche × direction."""

    name = "Niche Answer Base"

    def resolve(
        self,
        industry_id: str,
        *,
        track: str | None = None,
        natural_direction: str | None = None,
        lang: str = "ru",
        business: str = "",
        numbers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        niche = NICHE_BASE.get(industry_id) or NICHE_BASE["ai-agencies"]
        direction = _pick_direction(track, natural_direction)
        pack = (niche.get("directions") or {}).get(direction) or niche["directions"]["ops"]
        numbers = numbers or {}
        ru = lang.startswith("ru")

        # Self-clarify: which must_clarify still empty
        still_need = []
        for key in niche.get("must_clarify") or []:
            if numbers.get(key) in (None, "", []):
                # also soft-match in business text
                if key.replace("_", " ") not in (business or "").lower() and key not in (business or "").lower():
                    still_need.append(key)

        from backend.core.circle_system.copy_firmware import CopyFirmware

        fw = CopyFirmware()
        pack = {
            **pack,
            "answer": fw.strip_forbidden(str(pack.get("answer") or "")),
            "answer_en": fw.strip_forbidden(str(pack.get("answer_en") or pack.get("answer") or "")),
        }
        answer = pack["answer"] if ru else pack.get("answer_en") or pack["answer"]
        answer = fw.publicize(answer, lang=lang)
        free_work = list(pack.get("free_work") or [])

        # Quality boost when numbers present
        filled = [k for k in (niche.get("must_clarify") or []) if numbers.get(k) not in (None, "")]
        quality = 0.45 + 0.1 * len(filled) + (0.15 if len(still_need) <= 1 else 0)
        quality = min(0.95, quality)

        clar_questions = []
        for key in still_need[:4]:
            clar_questions.append(
                {
                    "id": f"clr_{key}",
                    "field": key,
                    "kind": "numeric_or_text",
                    "question_ru": f"Уточнение для качества ответа: укажите «{key}» (число или факт). Если нет — «не знаю».",
                    "question_en": f"Quality clarify: provide «{key}» (number or fact). If none — say unknown.",
                    "question": (
                        f"Уточнение: «{key}» (число/факт) или «не знаю»."
                        if ru
                        else f"Clarify «{key}» (number/fact) or unknown."
                    ),
                }
            )

        return {
            "module": self.name,
            "industry_id": industry_id,
            "industry_name": niche["name"],
            "direction": direction,
            "hook": niche.get("hook"),
            "tasty_proof": niche.get("tasty_proof"),
            "title": pack.get("title"),
            "answer": answer,
            "quality_score": round(quality, 3),
            "quality_gate": quality >= 0.55,
            "must_clarify_open": still_need,
            "clarification_questions": clar_questions,
            "free_work_checklist": free_work,
            "success_metric": pack.get("success_metric"),
            "out_of_scope_default": list(pack.get("out_of_scope_default") or []),
            "all_directions": {
                d: {
                    "title": (niche["directions"][d].get("title")),
                    "success_metric": niche["directions"][d].get("success_metric"),
                }
                for d in DIRECTIONS
                if d in niche["directions"]
            },
        }

    def founders_lane(self, lang: str = "ru") -> dict[str, Any]:
        f = FOUNDERS_LANE
        return {
            **f,
            "display_hook": f["hook"] if lang.startswith("ru") else f["hook_en"],
        }

    def free_work_phases(self, lang: str = "ru") -> list[dict[str, Any]]:
        ru = lang.startswith("ru")
        out = []
        for ph in FREE_WORK_PHASES:
            out.append(
                {
                    "id": ph["id"],
                    "days": ph["days"],
                    "title": ph["title_ru"] if ru else ph["title_en"],
                    "system": ph["system"],
                    "actions": [
                        {
                            "n": a["n"],
                            "action": a["ru"] if ru else a["en"],
                            "result": a["result_ru"] if ru else a["result_en"],
                        }
                        for a in ph["actions"]
                    ],
                }
            )
        return out

    def catalog(self) -> dict[str, Any]:
        return {
            "industries": list(NICHE_BASE.keys()),
            "directions": list(DIRECTIONS),
            "count_packs": sum(len(v["directions"]) for v in NICHE_BASE.values()),
        }


def get_niche_answer(
    industry_id: str,
    track: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return NicheAnswerBase().resolve(industry_id, track=track, **kwargs)
