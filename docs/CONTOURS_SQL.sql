-- Optional Timescale/Postgres schema for contour engines.
-- Production Railway stays JSON-file-backed. Applied by docker-compose init.

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS eval_datasets (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  name TEXT,
  version TEXT,
  notes TEXT,
  created TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS eval_cases (
  id TEXT PRIMARY KEY,
  dataset_id TEXT REFERENCES eval_datasets(id),
  input_json JSONB NOT NULL,
  gold_json JSONB NOT NULL,
  tags TEXT[]
);

CREATE TABLE IF NOT EXISTS eval_runs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  dataset_id TEXT,
  engine_version TEXT,
  param_snapshot JSONB,
  axes JSONB NOT NULL,
  created TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS eval_run_results (
  id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES eval_runs(id),
  results JSONB
);

CREATE TABLE IF NOT EXISTS flight_logs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  agent_id TEXT,
  trace_id TEXT,
  step_type TEXT,
  prompt_tokens INT,
  completion_tokens INT,
  latency_ms DOUBLE PRECISION,
  cost_usd DOUBLE PRECISION,
  payload_json JSONB,
  ts TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  source TEXT,
  text TEXT,
  owner TEXT,
  stage TEXT,
  sla_minutes INT,
  project_id TEXT,
  discrepancy JSONB,
  created TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS outcome_contracts (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  named_observable TEXT,
  baseline TEXT,
  target TEXT,
  measurement TEXT,
  exclusions TEXT,
  acceptance_test TEXT
);

CREATE TABLE IF NOT EXISTS spread_ledger (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  node_id TEXT,
  client_rate DOUBLE PRECISION,
  spot_cost DOUBLE PRECISION,
  delta DOUBLE PRECISION,
  timestamp TIMESTAMPTZ DEFAULT now()
);

-- Hypertable needs PK to include timestamp. Skip auto-convert; JSON store is production.
-- SELECT create_hypertable('spread_ledger', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  firmware_version TEXT,
  last_seen TIMESTAMPTZ,
  generation TEXT
);

CREATE TABLE IF NOT EXISTS telemetry (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  device_id TEXT,
  temperature DOUBLE PRECISION,
  shock DOUBLE PRECISION,
  battery DOUBLE PRECISION,
  ts TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS partners (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  name TEXT,
  type TEXT,
  contact TEXT
);

CREATE TABLE IF NOT EXISTS referrals (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  partner_id TEXT,
  project_id TEXT,
  contour TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  ts TIMESTAMPTZ DEFAULT now(),
  tenant_id TEXT NOT NULL,
  event TEXT,
  payload JSONB
);
