# Basic cybersecurity · Metrix AI

## What is installed

| Control | Implementation |
|---------|----------------|
| Rate limit | 120 req / 60s per IP on `/api/*` (`METRIX_RATE_LIMIT`, `METRIX_RATE_WINDOW_SEC`) |
| Body size | Max 512KB (`METRIX_MAX_BODY_BYTES`) |
| Security headers | nosniff, DENY frames, CSP light, Referrer-Policy, Permissions-Policy |
| Ops key | `METRIX_OPS_KEY` + header `X-Metrix-Ops-Key` for robotics start / price expose |
| Input sanitize | Control-char strip + length cap on free-text |
| Path safety | Request id validation (existing) |
| Secrets out of store | Supabase sync redacts price + secret keys |
| Service role | Never in frontend; server-only env |

## Railway env

```bash
METRIX_DEBUG=0
METRIX_ENV=production
METRIX_CORS=https://your.vercel.app
METRIX_PUBLIC_URL=https://metrix-ai-production.up.railway.app
METRIX_OPS_KEY=<long random>
METRIX_RATE_LIMIT=120
METRIX_RATE_WINDOW_SEC=60
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<server only>
```

## Not yet (later)

- WAF / Cloudflare
- JWT auth for client rooms
- Audit log of ops key use
- Honeypot fields
- Full CSP without unsafe-inline (after bundling static JS)

## Incident basics

1. Rotate `METRIX_OPS_KEY` and Supabase service role if leaked  
2. Tighten CORS to exact origins  
3. Disable open RLS policies (schema defaults to service-role only)  
