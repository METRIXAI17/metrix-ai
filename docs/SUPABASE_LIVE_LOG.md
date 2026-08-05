# Supabase · живой 7-day channel log

Сейчас Metrix пишет live log в **локальные JSON** (`backend/data/live_logs/`) — работает на Railway как ephemeral.  
Чтобы лог был **живым между деплоями и устройствами** — подключаем Supabase.

## Зачем Supabase

| Нужда | Как |
|-------|-----|
| Persist log после redeploy | Postgres table |
| Multi-device (телефон + desktop) | shared session_id |
| Realtime «галочки» | Supabase Realtime |
| Auth optional | anon key + RLS by session token |

## Минимальная схема

```sql
-- sessions
create table live_log_sessions (
  id text primary key,
  project_name text,
  run_id text,
  start_date date,
  end_date date,
  touch_target int default 12,
  touches_done int default 0,
  artifact jsonb default '{}',
  artifact_shipped boolean default false,
  channel_name text,
  status text default 'live',
  lang text default 'ru',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- day rows
create table live_log_days (
  id bigserial primary key,
  session_id text references live_log_sessions(id) on delete cascade,
  day_offset int not null,
  day date,
  label text,
  action text,
  owner text default 'Founder',
  done boolean default false,
  note text default '',
  touched_at timestamptz,
  unique(session_id, day_offset)
);

-- optional ledger of DM replies
create table live_log_ledger (
  id bigserial primary key,
  session_id text references live_log_sessions(id) on delete cascade,
  ts timestamptz default now(),
  who text,
  response text,
  note text,
  day_offset int
);

-- RLS: allow access if client knows session_id (share as secret link)
alter table live_log_sessions enable row level security;
alter table live_log_days enable row level security;
alter table live_log_ledger enable row level security;

create policy "session read" on live_log_sessions for select using (true);
create policy "session insert" on live_log_sessions for insert with check (true);
create policy "session update" on live_log_sessions for update using (true);
-- tighten later with auth.uid() or signed tokens
```

## Env

```bash
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_key=...   # server only
SUPABASE_ANON_KEY=...           # if client direct (optional)
```

## Как сработаться (порядок)

1. Создать project на [supabase.com](https://supabase.com)  
2. SQL Editor → выполнить схему выше  
3. В Railway / `.env` добавить `SUPABASE_URL` + service role  
4. В коде `live_log.py` — ветка: если env set → write Supabase, else file  
5. UI уже шлёт `POST /api/v1/analytics/live-log/tick` — **менять фронт не нужно**  
6. (Опционально) Realtime: subscribe `live_log_days` filter `session_id=eq.<id>`  
7. Ссылка клиенту: `https://metrix-ai.vercel.app/?log=<session_id>` (deep-link later)

## API уже в Metrix

| Method | Path | Действие |
|--------|------|----------|
| GET | `/api/v1/analytics/live-log/{id}` | состояние |
| POST | `/api/v1/analytics/live-log/tick` | ✓ день / artifact |

## Mapping file → Supabase

| File field | Table |
|------------|--------|
| session.* | `live_log_sessions` |
| session.days[] | `live_log_days` |
| session.ledger[] | `live_log_ledger` |

## Не делать

- Не класть service role в Vercel public bundle  
- Не открывать RLS `using (true)` навсегда в prod без rate limit  
- Не дублировать log только в localStorage — теряется
