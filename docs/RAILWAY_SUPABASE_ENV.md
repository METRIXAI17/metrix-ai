# Railway env · Supabase persist + security

## 1. SQL (один раз)

Supabase → SQL Editor → paste & run:

`docs/SUPABASE_FULL_SCHEMA.sql`

## 2. Railway Variables

| Key | Value |
|-----|--------|
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | service_role (server only) |
| `METRIX_OPS_KEY` | long random (ops header) |
| `METRIX_DEBUG` | `0` |
| `METRIX_ENV` | `production` |
| `METRIX_CORS` | exact Vercel origin(s) |
| `METRIX_PUBLIC_URL` | Railway HTTPS URL |

Redeploy after save.

## 3. Verify

```bash
curl -sS https://YOUR.up.railway.app/api/v1/health
# supabase_sync: true  when env set
```

Generate once → Supabase table `metrix_runs` should gain a row.  
Live log tick → `live_log_sessions` / `live_log_days`.  
Skill distill → `skill_memory`.

## 4. Appsmith

Import query list from `docs/appsmith/metrix_ops_datasource.json`  
Guide: `docs/APPSMITH_SETUP.md`
