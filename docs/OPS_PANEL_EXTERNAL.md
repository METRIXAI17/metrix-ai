# Внешняя ops-панель + клиентская панель · план подключения

## Цель

Отдельный сервис (не только `public/index.html`), где **вы** ведёте:
- live 7-day logs  
- GenCore слоты  
- identity answers  
- клиентские run'ы (desk)

## Рекомендуемый стек (практичный)

| Слой | Сервис | Зачем |
|------|--------|--------|
| DB + Auth + Realtime | **Supabase** | live_log + clients + RLS |
| Internal founder UI | **Appsmith** (self-host или cloud) | формы на ваш Railway API |
| Alt founder UI | **Retool** | быстрее для admin, дороже |
| Spreadsheet on Postgres | **NocoDB** on Supabase | «таблица клиентов» без кода |
| Уже в Metrix | `/app/ops-panel.html` | тонкий founder pad на API |

**Не** класть service role в Vercel/фронт.

## Порядок внедрения (1–2 дня)

### Day 0 — уже есть
- API: live-log, identity, gencore, business-generate  
- File fallback + optional Supabase REST upsert (`SUPABASE_*` env)  
- `public/ops-panel.html`

### Day 1 — Supabase
1. Project  
2. SQL из `docs/SUPABASE_LIVE_LOG.md`  
3. Tables clients (optional):

```sql
create table clients (
  id uuid primary key default gen_random_uuid(),
  name text,
  niche text,
  last_run_id text,
  log_session_id text,
  status text default 'pilot',
  notes text,
  created_at timestamptz default now()
);
```

4. Railway env: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`  
5. Redeploy Railway → generate creates log with `backend: supabase` when env set  

### Day 2 — Appsmith (панель для себя + клиентов)
1. New app «Metrix Ops»  
2. Datasource REST → `https://metrix-ai-production.up.railway.app`  
3. Pages:
   - **Founder:** GenCore form, live log table, identity Q  
   - **Clients:** list from Supabase `clients`, open run, attach `log_session_id`  
4. Bind buttons to:
   - `POST /api/v1/analytics/business-generate`  
   - `POST /api/v1/analytics/live-log/tick`  
   - `POST /api/v1/analytics/gencore`  
   - `POST /api/v1/analytics/identity/pack`  

### Optional — NocoDB
Point NocoDB at Supabase Postgres → sales ops edits clients without engineer.

## Почему не «ещё один custom React app» сразу
- Скорость: Appsmith/Retool = UI за часы  
- Metrix API уже source of truth  
- Потом можно заменить UI, не трогая GenCore  

## Контекст для «репада» (личный ops pad)
См. `docs/REQUEST_REPAD_OPS_PANEL.md`
