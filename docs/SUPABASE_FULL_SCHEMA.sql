-- Metrix AI · full Supabase schema
-- Run in Supabase SQL Editor (once per project)
-- Covers: live_log · metrix_runs (all responses) · skill_memory · clients

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. Live log
-- ═══════════════════════════════════════════════════════════════════════════

create table if not exists live_log_sessions (
  id text primary key,
  project_name text,
  run_id text,
  start_date date,
  end_date date,
  touch_target int default 12,
  touches_done int default 0,
  artifact jsonb default '{}'::jsonb,
  artifact_shipped boolean default false,
  channel_name text,
  status text default 'live',
  lang text default 'ru',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists live_log_days (
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

create table if not exists live_log_ledger (
  id bigserial primary key,
  session_id text references live_log_sessions(id) on delete cascade,
  ts timestamptz default now(),
  who text,
  response text,
  note text,
  day_offset int
);

create index if not exists idx_live_log_days_session on live_log_days(session_id);
create index if not exists idx_live_log_ledger_session on live_log_ledger(session_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. All Metrix AI responses (sync)
-- ═══════════════════════════════════════════════════════════════════════════

create table if not exists metrix_runs (
  id text primary key,
  endpoint text not null,
  project_name text,
  industry_id text,
  lang text default 'ru',
  segment_id text,
  path_id text,
  acceptance_p double precision,
  ship_gate text,
  summary jsonb default '{}'::jsonb,
  payload jsonb default '{}'::jsonb,
  content_hash text,
  business_excerpt text,
  created_at timestamptz default now()
);

create index if not exists idx_metrix_runs_created on metrix_runs(created_at desc);
create index if not exists idx_metrix_runs_endpoint on metrix_runs(endpoint);
create index if not exists idx_metrix_runs_segment on metrix_runs(segment_id);
create index if not exists idx_metrix_runs_path on metrix_runs(path_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Skill memory
-- ═══════════════════════════════════════════════════════════════════════════

create table if not exists skill_memory (
  id text primary key,
  name text,
  domain text,
  tags jsonb default '[]'::jsonb,
  success boolean default false,
  confidence double precision,
  band text,
  conceptual_algorithm jsonb default '{}'::jsonb,
  executive_algorithm jsonb default '{}'::jsonb,
  lang text default 'ru',
  version text default '1.0',
  payload jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_skill_memory_domain on skill_memory(domain);
create index if not exists idx_skill_memory_created on skill_memory(created_at desc);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Clients (CRM-light for Appsmith)
-- ═══════════════════════════════════════════════════════════════════════════

create table if not exists clients (
  id text primary key,
  name text,
  contact text,
  segment_id text,
  industry_id text,
  project_name text,
  last_run_id text,
  notes text,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. RLS (service role bypasses RLS; anon policies locked down)
-- ═══════════════════════════════════════════════════════════════════════════

alter table live_log_sessions enable row level security;
alter table live_log_days enable row level security;
alter table live_log_ledger enable row level security;
alter table metrix_runs enable row level security;
alter table skill_memory enable row level security;
alter table clients enable row level security;

-- Drop loose policies if re-running
do $$ begin
  -- live_log: no public open policies in prod — service role only
  -- Optional: allow select by knowing exact session id from signed link later
  null;
end $$;

-- Service role uses bypass. For anon/authenticated: deny by default (no policies = deny).
-- If you need client-facing read of own log, add a narrow policy later:
-- create policy "log read by id" on live_log_sessions for select
--   using (id = current_setting('request.headers', true)::json->>'x-log-id');

comment on table metrix_runs is 'All Metrix AI API responses synced from Railway backend';
comment on table skill_memory is 'Distilled skills from successful generate runs';
comment on table live_log_sessions is '7-day channel log sessions';
