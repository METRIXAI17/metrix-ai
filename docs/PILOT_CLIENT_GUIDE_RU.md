# Инструкция: как клиент проходит пилот Metrix (Deep Tech / Circle-System)

**Реалистичный горизонт с тестами и переделками: 21–35 календарных дней**  
(сжатый режим: 14–21 день при готовности данных и быстрых ответах на тесты)

Цены (private pilot ladder):  
- Free consult + free tech write / TZ — **$0**  
- Pilot ops / product / promo — **$690 / $790 / $490**  
- Main package — **$2490** только после успеха пилота  

---

## Что делает клиент (по шагам)

### День 0–1 · Старт

| # | Действие клиента | Результат |
|---|------------------|-----------|
| 1 | Заполнить brief: бизнес, ниша, цель, что уже есть | Текст ≥20 символов в consult / portal |
| 2 | Указать industry (`ai-agencies` / `cloud-economy` / …) | Корректный market unit |
| 3 | Приложить числа, если есть (бюджет, SLA, конверсия) | Меньше NEОПРЕДЕЛЕНО |
| 4 | Назначить **signer** (кто ставит ТОЧНО ДА/НЕТ) | Human-authorized acceptance |
| 5 | (Опц.) change-prep: что менять нельзя | Constraint map |

**Система:** Step A — параметры + косвенный CY/CN/U.

### День 1–4 · Тесты неопределённостей (Super Speed)

| # | Действие клиента | Результат |
|---|------------------|-----------|
| 6 | Пройти quiz-тесты по каждому UNDEFINED | Assembly растёт |
| 7 | Отвечать **ТОЧНО ДА / ТОЧНО НЕТ / НЕ ЗНАЮ**, не «примерно» где можно | Чистые статусы |
| 8 | Для metric/timeline/resource — дать числа или «не знаю» | Magnitude slots |
| 9 | На вопросы «сборка» — 2–3 условия, которые должны сойтись | Assembly map |

**Система:** Step B — тесты, сборка (не тепло), Super Program match.  
Ответы клиенту идут с **лингвистическим теплом**, но статус истины не подменяется.

### День 3–10 · Tech write (бесплатно / в рамках воронки)

| # | Действие клиента | Результат |
|---|------------------|-----------|
| 10 | Прочитать terminal specs (TZ, pilot charter, metrics) | Понимание scope |
| 11 | Замечания по секциям (problem / scope / acceptance) | Rework round 1 |
| 12 | Подтвердить **out of scope** (всё, что ТОЧНО НЕТ) | Защита пилота |
| 13 | Согласовать 1 success metric пилота (подпись signer) | Gate пилота |

**Система:** phased insert tech write (ops rules R4).

### День 8–28 · Пилот

| # | Действие клиента | Результат |
|---|------------------|-----------|
| 14 | Оплатить/активировать pilot track (ops/product/promo) | Старт P4 |
| 15 | Дать доступы по integration list (API/CRM/ledger — что в scope) | Resource match |
| 16 | Еженедельно 30–45 мин sync (или async в portal) | Снижение SFI |
| 17 | Смотреть support tickets (жёлтый/красный health) | Быстрые фиксы |
| 18 | Не расширять scope без retest assembly | Контроль PAP |

**Система:** metric firmware → support; pilot predictor (L=0.92).

### День 21–35 · Закрытие / main

| # | Действие клиента | Результат |
|---|------------------|-----------|
| 19 | Приёмка по success criterion | Pilot success / fail |
| 20 | Rework loop если predicted_end < 0.7 или risk=high | +3–10 дней |
| 21 | Решение по main package $2490 | Только после success |

---

## Реалистичный таймлайн

| Сценарий | Дни | Условие |
|----------|-----|---------|
| **Оптимистичный** | 14–18 | Данные готовы, ответы на тесты ≤48ч, 1 rework |
| **Базовый (рекомендуемый)** | **21–28** | 1–2 rework, частичные интеграции |
| **С переделками** | **28–35** | Много UNDEFINED, смена scope, 2+ rework |
| **Стоп / пауза** | +∞ | Нет signer, assembly < 0.45, consistency < 0.62 |

Буфер на тесты и переделки заложен **20–30%** календаря (orchestration stimulation `rework_buffer`).

---

## Чеклист готовности к пилоту

- [ ] Free consult получен  
- [ ] Tech write / TZ прочитан и прокомментирован  
- [ ] Неопределённости либо закрыты тестами, либо явно out of scope  
- [ ] Assembly score ≥ 0.45  
- [ ] Circle consistency ≥ 0.62  
- [ ] Один signed success metric  
- [ ] Owner со стороны клиента (signer)  
- [ ] Branding/VA контакты согласованы, если затрагивается identity  

---

## Что клиент *не* должен делать

1. Подменять UNDEFINED «красивым да» — support и predictor поймают contradiction.  
2. Просить main package до pilot success.  
3. Ждать «магии LLM» — runtime детерминированный; внешняя LLM не обязательна.  
4. Расширять pilot mid-flight без retest.

---

## Контакты ролей (текущий стат)

| Роль | Кто | Зачем |
|------|-----|-------|
| Deep Tech / architecture | @karimmetrix | circle-system, TZ, pilot gate |
| Branding & Virtual Assets | @andrewsmm1 | naming, VA, phenomenon→object |
| Client signer | назначает клиент | CY/CN, acceptance |
