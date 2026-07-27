# Deploy Metrix AI (public site + optional API)

**What goes public:** static frontend (`index.html`, `css/`, `js/`) + optional open backend.  
**What stays private:** `pilot_private/` (already in `.gitignore`).

---

## 1. Public frontend (Vercel — easiest)

### Option A — Vercel dashboard (no Git)

1. Sign up at [vercel.com](https://vercel.com/signup).  
2. **Add New Project** → **Upload** the folder:

   ```
   Desktop/metrix-ai
   ```

   Or upload only:

   - `index.html`
   - `css/`
   - `js/`
   - `vercel.json`
   - `robots.txt` (optional)
   - `client-package-latest.html` (optional sample)

3. Framework preset: **Other**.  
4. Deploy. You get a URL like `https://metrix-ai-xxxx.vercel.app`.

### Option B — GitHub + Vercel (recommended)

1. Create a **public** GitHub repo (do **not** commit `pilot_private/`, `backend/workspace/`, `.env`).  
2. Push project root (`.gitignore` already excludes secrets and pilot).  
3. Vercel → **Import** the repo → Deploy.

### After deploy

- Open the site → **Free consult** form works for localStorage save.  
- Live analysis needs the API (next section).  

Set API URL for production in `js/data.js`:

```js
api: {
  baseUrl: "https://YOUR-API-HOST",  // e.g. Railway/Fly/VPS
  processPath: "/api/v1/process",
  enabled: true,
},
```

Redeploy frontend after changing `baseUrl`.

---

## 2. Public API (backend) — international

Run the open FastAPI backend (not `pilot_private`):

```powershell
cd Desktop/metrix-ai
pip install -r requirements.txt
python -m backend.main
# http://127.0.0.1:8787
```

### Hosting options

| Host | Good for | Notes |
|------|----------|--------|
| **Railway / Render / Fly.io** | International | Docker or `uvicorn backend.main:app` |
| **Hetzner / DigitalOcean VPS** | Full control | nginx + TLS + systemd |
| **Timeweb / Selectel** | RF clients | Same stack; pair with YooKassa later |

### Minimal Dockerfile (optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY index.html css js ./
ENV METRIX_HOST=0.0.0.0 METRIX_PORT=8787
CMD ["python", "-m", "backend.main"]
```

Expose port `8787`. Set CORS in `backend/config.py` / env to include your Vercel origin.

---

## 3. Pilot private (not on public GitHub)

```powershell
cd Desktop/metrix-ai
python -m pilot_private.main
# http://127.0.0.1:8790/client
# http://127.0.0.1:8790/executor
```

Deploy only to a **private** VPS or private repo. Do not publish payment keys.

---

## 4. Checklist before go-live

- [ ] `js/data.js` → `api.baseUrl` points to production API (or `enabled: false` for form-only)  
- [ ] Vercel domain + custom domain DNS  
- [ ] HTTPS everywhere  
- [ ] CORS allows the frontend origin  
- [ ] No `pilot_private/` in the public repo  
- [ ] Privacy / оферта page if you take RF personal data  
- [ ] Stripe (intl) and/or YooKassa (RF) only on private pilot host  

---

## 5. What users see after this frontend update

| Element | Behavior |
|---------|----------|
| Hero | Free consult CTA |
| Flagships | 6 cards, simple names, detail on click |
| Method | 3 steps: consult → direction → ship |
| Pricing | Free → pilot $490–790 → main $2490 |
| Form | No “POST /api/v1/process” help text |

---

## 6. Quick local preview

```powershell
cd Desktop/metrix-ai
# static
Start-Process index.html
# or API + site
python -m backend.main
# open http://127.0.0.1:8787/app/
```
