# Production deploy — Vercel (frontend) + Railway (API)

**Architecture**

```
Browser  ──HTTPS──►  Vercel (static)     https://*.vercel.app
                        │
                        │  POST /api/v1/process  (CORS)
                        ▼
                     Railway (FastAPI)    https://*.up.railway.app
```

| Surface | Host | Repo path | Domain |
|---------|------|-----------|--------|
| Public site | **Vercel** | `index.html`, `css/`, `js/`, `vercel.json` | `*.vercel.app` |
| API | **Railway** | `backend/`, `Dockerfile`, `railway.toml` | `*.up.railway.app` |
| Private pilot | **Not public** | `pilot_private/` (gitignored) | private only |

---

## Order of operations (do not skip)

1. **Push** production configs to GitHub (`main`)
2. **Railway** API first → get public HTTPS URL
3. **Wire** frontend `apiBaseUrl` + Railway `METRIX_CORS`
4. **Vercel** frontend → get `*.vercel.app` URL
5. **Lock** CORS to exact Vercel origin(s)
6. **Smoke test** form → API → JSON

---

## Stage A — Railway (API)

### A1. Create project from GitHub

1. Open [railway.app](https://railway.app) → login (GitHub: `METRIXAI17`).
2. **New Project** → **Deploy from GitHub repo** → `METRIXAI17/metrix-ai`.
3. If asked for root directory: **repo root** (Dockerfile lives there).
4. Railway reads `railway.toml` + `Dockerfile` automatically.

### A2. Variables (Variables tab)

| Key | Value | Notes |
|-----|--------|--------|
| `METRIX_DEBUG` | `0` | Production |
| `METRIX_ENV` | `production` | Shown in `/health` |
| `METRIX_CORS` | `https://PLACEHOLDER.vercel.app` | Update after Vercel (Stage C) |
| `PORT` | *(leave unset)* | Railway injects automatically |

Temporary while frontend not live yet:

```text
METRIX_CORS=http://localhost:3000,http://127.0.0.1:5500
```

### A3. Public domain

1. Service → **Settings** → **Networking** → **Generate Domain**.
2. Copy URL, e.g. `https://metrix-ai-production-xxxx.up.railway.app`.
3. Wait until deploy is **Success** and healthcheck is green.

### A4. Smoke checks (browser or curl)

```text
GET  https://YOUR.up.railway.app/
GET  https://YOUR.up.railway.app/api/v1/health
GET  https://YOUR.up.railway.app/docs
```

Expect `{"ok": true, ...}` on health.

```bash
curl -sS https://YOUR.up.railway.app/api/v1/health
```

### A5. What “senior” settings you already have in repo

- Multi-layer health: `/health` + `/api/v1/health` + Docker `HEALTHCHECK`
- `railway.toml`: healthcheck path, restart on failure, drain on redeploy
- Non-root container user (`uid 10001`)
- `tini` as PID 1 + uvicorn `--proxy-headers` behind Railway edge
- `PORT` from platform env
- `METRIX_DEBUG=0` by default
- Ephemeral workspace dirs (no secrets in image; `.dockerignore` strips pilot/data)

---

## Stage B — Wire API URL into frontend

After you have the Railway URL, set it in **one** place:

### Option 1 (recommended) — `index.html` runtime

```html
<script>
  window.METRIX_RUNTIME = {
    apiBaseUrl: "https://YOUR-SERVICE.up.railway.app"
  };
</script>
```

### Option 2 — hardcode in `js/data.js`

```js
var METRIX_API_BASE = "https://YOUR-SERVICE.up.railway.app";
```

Commit + push so Vercel rebuilds with the URL.

---

## Stage C — Vercel (frontend, Vercel domain)

### C1. Import repo

1. Open [vercel.com](https://vercel.com) → login with **same GitHub** `METRIXAI17`.
2. **Add New…** → **Project** → import `metrix-ai`.
3. Settings:

| Field | Value |
|-------|--------|
| Framework Preset | **Other** |
| Root Directory | `.` (default) |
| Build Command | *(empty)* |
| Output Directory | *(empty / `.`)* |
| Install Command | *(empty)* |

4. **Deploy**.

### C2. Vercel URL

You get something like:

```text
https://metrix-ai.vercel.app
https://metrix-ai-xxxx.vercel.app
```

Production domain is on the project **Domains** tab.

### C3. Lock Railway CORS

Back on Railway → Variables:

```text
METRIX_CORS=https://metrix-ai.vercel.app,https://metrix-ai-xxxx.vercel.app
```

Include **every** origin you will open in the browser (production + preview if needed).  
Redeploy Railway (or wait for auto-restart after env change).

### C4. Optional — same-origin API proxy (advanced)

If you prefer the browser to call `/api/...` on the Vercel host (no cross-origin):

1. Set `apiBaseUrl` to `""` (empty string).
2. Add to `vercel.json` rewrites (replace destination):

```json
{
  "source": "/api/:path*",
  "destination": "https://YOUR-SERVICE.up.railway.app/api/:path*"
}
```

3. Redeploy Vercel. CORS on Railway can stay strict (server-to-server rewrite).

---

## Stage D — End-to-end verification

| Check | Expected |
|-------|----------|
| Open Vercel URL | Site loads, no mixed-content warnings |
| Free consult submit | 200 from API, success message with direction |
| Railway logs | Request lines, no 5xx |
| `GET /api/v1/health` | `ok: true`, `env: production` |
| CORS fail | Browser console shows blocked origin → fix `METRIX_CORS` |

Local form still works against `http://127.0.0.1:8787` when opened from localhost.

---

## Env reference

| Variable | Where | Default | Purpose |
|----------|--------|---------|---------|
| `PORT` | Railway | platform | Listen port |
| `METRIX_PORT` | local | `8787` | Listen port if `PORT` unset |
| `METRIX_HOST` | both | `0.0.0.0` | Bind address |
| `METRIX_DEBUG` | both | `0` | Debug logs / looser CORS |
| `METRIX_ENV` | both | `production` if not debug | Label in health |
| `METRIX_CORS` | Railway | localhost list | Allowed browser origins |

See `.env.example`.

---

## What never goes public

- `pilot_private/`
- `backend/workspace/`, `backend/data/requests/`
- `.env` with secrets
- Payment keys (Stripe / YooKassa) — private pilot host only

---

## Rollback

- **Vercel**: Deployments → previous → Promote to Production  
- **Railway**: Deployments → Redeploy previous successful build  

---

## Quick local production-like run

```powershell
cd $env:USERPROFILE\Desktop\metrix-ai
pip install -r requirements.txt
$env:METRIX_DEBUG="0"
$env:METRIX_CORS="http://127.0.0.1:5500"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8787 --proxy-headers
```
