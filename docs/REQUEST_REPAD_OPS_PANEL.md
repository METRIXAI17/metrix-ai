# Контекст запроса · операционная панель для основателя (Repad / personal ops pad)

Используйте этот текст как brief при заказе UI (Appsmith / Retool / freelace / себе в replit).

---

## Кто я
Основатель **Metrix AI** (@karimmetrix). Продукт: consultation core + GenCore (2-й флагман) — orientation → result pack, не «ещё один AI chat».

## Что нужно
**Личная операционная панель** (founder-only) + лёгкая **панель клиентов**, отдельно от публичного marketing site.

## Что уже есть (не строить с нуля)
- Public: https://metrix-ai.vercel.app  
- API: https://metrix-ai-production.up.railway.app  
- Endpoints:
  - `POST /api/v1/analytics/business-generate` (consult + live log + identity + gencore v1)
  - `GET/POST /api/v1/analytics/live-log/{id}` · `/live-log/tick`
  - `POST /api/v1/analytics/identity/pack` · `/identity/answers`
  - `POST /api/v1/analytics/gencore` (v2–v5 slots)
  - `POST /api/v1/analytics/promotion-pack`
- Thin panel: `/app/ops-panel.html`
- Docs: `SUPABASE_LIVE_LOG.md`, `GENCORE_ENGINE_PLAN.md`, `OPS_PANEL_EXTERNAL.md`

## Экраны (MVP)
1. **Runs** — список generate (session id, project, niche, band)  
2. **Live log** — 7 дней, ✓ tick, artifact flag (как в product)  
3. **Identity** — 5 unique Q + delight forecast; store answers  
4. **GenCore** — кнопки v2/v3/v4/v5, показать slots JSON humanized  
5. **Clients** — name, niche, last_run, log_session_id, status pilot/main  
6. **Promo** — 3 roads + DM scripts for a client  

## Принципы UI
- Спокойный dark UI (как Metrix: teal/slate)  
- Human language, no raw key dumps  
- A01–A12 = **path steps**, not content  
- One stop-rule for pilot (7–14d proof) — not repeated per card  
- Paywall logic already on public site; panel is **post-pay / internal**  

## Данные
- Prefer **Supabase** Postgres for clients + live_log persistence  
- Railway keeps service role secret  
- Vercel stays public static only  

## Definition of Done
- [ ] I can open a client, see their live log, tick a day  
- [ ] I can run GenCore v2 after identity answers  
- [ ] Client list persists across deploy  
- [ ] No service role in browser  

## Out of scope
- Full CRM, billing processor, multi-tenant auth (later)  
- Replacing public Generate UI  

## Voice / product north star
Orient → pick → ship. Same product, different analytics → different money.  
Failed hypothesis = cheap cycle. Not another chat — live result pack.
