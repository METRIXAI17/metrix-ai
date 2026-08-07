# Appsmith + alternatives — короткая регистрация и финальная настройка

Цель: после деплоя Metrix API осталось **только технически донастроить** рабочую ops-панель (live log · GenCore · clients).  
Встроенный founder pad уже есть: `/app/ops-panel.html`.

---

## A. Appsmith (рекомендуется)

### 1. Регистрация

1. Откройте [https://www.appsmith.com](https://www.appsmith.com) → **Start for free**.
2. Sign up (Google / email / GitHub).
3. Создайте **Workspace** → **New application** → имя: `Metrix Ops`.

### 2. Datasource (Railway API)

1. **Datasources** → **+ New** → **Authenticated API** (или REST API).
2. URL: `https://metrix-ai-production.up.railway.app`  
   (или ваш Railway domain).
3. Headers (optional):
   - `Content-Type: application/json`
4. **Save** → **Test** на `GET /api/v1/health` → ожидайте `{"ok": true}`.

### 3. Queries (минимум)

| Name | Method | Path | Body |
|------|--------|------|------|
| `health` | GET | `/api/v1/health` | — |
| `liveLogGet` | GET | `/api/v1/analytics/live-log/{{logId.text}}` | — |
| `liveLogList` | GET | `/api/v1/analytics/live-log?limit=20` | — |
| `liveLogTick` | POST | `/api/v1/analytics/live-log/tick` | `{"session_id":"{{logId.text}}","day_offset":{{day.value}},"note":"{{note.text}}","who":"ops"}` |
| `gencore` | POST | `/api/v1/analytics/gencore` | `{"business":"{{brief.text}}","project_name":"{{proj.text}}","generation":"v5","lang":"ru"}` |
| `wayd` | POST | `/api/v1/analytics/wayd/terminal` | `{"business":"{{brief.text}}","lang":"ru"}` |
| `roboticsPlan` | POST | `/api/v1/analytics/robotics/plan` | `{"business":"{{brief.text}}","lang":"ru"}` |
| `roboticsStart` | POST | `/api/v1/analytics/robotics/start` | `{"plan":{{roboticsPlan.data}},"lang":"ru"}` |
| `roboticsAdvance` | POST | `/api/v1/analytics/robotics/advance` | `{"session_id":"{{robId.text}}","note":"ops"}` |
| `segment` | POST | `/api/v1/analytics/segment` | `{"business":"{{brief.text}}","lang":"ru"}` |
| `implementModel` | POST | `/api/v1/analytics/implement-model` | `{"business":"{{brief.text}}","expose_price":false}` |

### 4. UI pages

1. **Page: Live Log** — Table from `liveLogList` → on row click fill `logId` → run `liveLogGet` → List of days with Tick buttons → `liveLogTick`.
2. **Page: wayD Terminal** — Text widgets bound to `wayd.data.terminal.density|signal|acceptance_p|mesh_score` + chips from `labels.ids`.
3. **Page: GenCore** — JSONViewer on `gencore.data.output.slots`.
4. **Page: Robotics** — plan → start → advance queue R0–R6.

### 5. Supabase (опционально, persist)

1. [supabase.com](https://supabase.com) → New project.
2. SQL Editor → выполнить `docs/SUPABASE_LIVE_LOG.md`.
3. Railway variables:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
4. Redeploy API → `live_log.backend = supabase`.

---

## B. Alternatives (коротко)

### Retool

1. [retool.com](https://retool.com) → Sign up → Create app.
2. Resource → REST API → base URL Railway.
3. Same queries as Appsmith table above.
4. Лучше для admin/client desks (CRM-light).

### NocoDB

1. [nocodb.com](https://www.nocodb.com) или self-host.
2. Connect Postgres (Supabase connection string).
3. Таблицы `live_log_sessions` / `live_log_days` / clients — spreadsheet UI.
4. Не заменяет GenCore UI — только таблицы.

### Founder pad already in repo

`https://<your-api>/app/ops-panel.html`  
или Vercel: `https://<vercel>/ops-panel.html`

Этого достаточно, пока Appsmith/Retool не собраны.

---

## C. Что скрыто (намеренно)

- **Единственная платная услуга** = внедрение трёх направлений (`product_pack` · `unit_pack` · `ch_network`).
- Цена **не** отдаётся в public `business-generate` / homepage.
- Ops: `POST /implement-model` с `expose_price: true` только для founder (не встраивать в public Appsmith page).

---

## D. Smoke checklist

1. `GET /health` → ok  
2. Generate → «Шаги A01–A12», не «наполнение»  
3. Resume + техконтекст (без download-отчёта)  
4. Stop-rule один раз  
5. Ops panel ↗️ live log ticks  
6. GenCore → slots ready  
7. wayD terminal → ship_gate + unique_functions  
8. Robotics plan → start → advance  

---

## E. Brief для фриланса / repad

Копировать: `docs/REQUEST_REPAD_OPS_PANEL.md`
