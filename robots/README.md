# Торговые роботы

Четыре модели. Это код согласованной модели, не Telegram-карточки и не сигналы.
Риск-движок отдельно: размер от стоп-триггера, R не является входом в size(), плечо не путается с мультипликатором.

| Робот | Рынок | Стратегия | Живое подключение |
|---|---|---|---|
| **Target Place** | золото | точки входа/выхода = места (PDH/PDL, сессия, круглая). Между местами не торгует. | MetaTrader 5 |
| **Demand** | крипта | сначала окно спроса (объём), потом имя из вотчлиста | Binance API |
| **Ampli** | Америка | сжатие opening range → сбор расширения. Сторону не угадывает. | Alpaca |
| **Two-Leg Tape** | Tape Land | внимание обгоняет цену × деньги подтверждают. Без плеча. | scan-only (Binance public) |

По умолчанию **paper**: котировки живые, ордера фейковые. Живой рынок включается отдельно, ключами.

Никакой доходности робот не обещает. Стоп на день: `ROBOT_MAX_DAILY_LOSS_PCT`.

## Запуск с бумаги (сразу)

Из папки `metrix-ai`:

```bat
py -3 -m robots scan all
py -3 -m robots paper target_place
py -3 -m robots paper demand
py -3 -m robots paper ampli
```

Или двойной клик:

- `robots\scan_all.bat` — один снимок сигналов
- `robots\run_target_place.bat`
- `robots\run_demand.bat`
- `robots\run_ampli.bat`

Журнал сделок: `robots\data\<имя>.jsonl`

## Как подключить живой рынок

Скопируйте `robots\.env.example` → `robots\.env`.

### 1. Target Place → MT5 (золото)

1. Установите и залогиньтесь в **MetaTrader 5**. Терминал должен быть запущен.
2. `pip install MetaTrader5`
3. В `.env`:

```
ROBOT_MODE=live
GOLD_BROKER=mt5
GOLD_SYMBOL=XAUUSD
MT5_LOGIN=номер_счёта
MT5_PASSWORD=пароль
MT5_SERVER=имя_сервера_как_в_MT5
```

4. `py -3 -m robots live target_place`

Котировки для логики сейчас берутся с Yahoo (`GC=F`). Ордера уходят в MT5 на `GOLD_SYMBOL`. Символ в Market Watch должен быть виден (XAUUSD / GOLD — как у брокера).

### 2. Demand → Binance (крипта)

1. Binance → API Management → создать ключ. **Только спот. Без вывода средств.**
2. В `.env`:

```
ROBOT_MODE=live
BINANCE_KEY=...
BINANCE_SECRET=...
CRYPTO_WATCH=SOLUSDT,ВАШИ_МЕСТНЫЕ_ТИКЕРЫ
CRYPTO_QUOTE_USDT=50
```

3. `py -3 -m robots live demand`

На каждый сигнал покупает на `CRYPTO_QUOTE_USDT` USDT. Окно закрылось или стоп/тейк — продаёт.

Местные «стреляющие» имена пишите в `CRYPTO_WATCH` сами. Робот не ищет монеты за вас, он торгует окно спроса на вашем списке.

### 3. Ampli → Alpaca (US)

1. Регистрация [alpaca.markets](https://alpaca.markets) → Paper Keys.
2. В `.env`:

```
ROBOT_MODE=live
US_BROKER=alpaca
US_SYMBOL=SPY
ALPACA_KEY=...
ALPACA_SECRET=...
ALPACA_PAPER=1
```

3. `py -3 -m robots live ampli`

Пока `ALPACA_PAPER=1` — бумажный счёт Alpaca, не кэш. Живые акции: `ALPACA_PAPER=0` и funded live account.

Робот торгует только US cash. Ночью будет писать «вне US cash».

## Что робот имеет право делать

- Одна позиция на символ
- Размер от `ROBOT_RISK_PCT` (для золота/US). Крипта — фикс в USDT
- Стоп и тейк из модели
- Выход по стопу, тейку, концу окна (Demand), смерти амплитуды (Ampli)
- Убийство на день, если минус больше `ROBOT_MAX_DAILY_LOSS_PCT`

Не имеет права: усредняться, торговать между местами (золото), угадывать сторону сжатия (Америка), держать крипту после окна.

## Порядок, который не пропускайте

1. `scan` — видите ли логику на живых барах
2. `paper` — сутки, смотрите `robots\data\*.jsonl`
3. Только потом `live` на минимальном размере
