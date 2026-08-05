# GenCore · план генеративного движка (2-й флагман)

**Дата:** 2026-08-05  
**Флагман 1 (сейчас):** Consultation Core — карточки · отчёт · PDF · plan/TZ · expert base  
**Флагман 2 (GenCore):** генеративный контур, который **учится на успешных прогонах** и выдаёт новые артефакты (identity, promo, code, voice) без «чата ради чата».

---

## 1. Зачем

Посты @karimmetrix + фактические прогоны skill_memory показывают паттерн:

- brief → product_pack / unit_pack / ch_network / m_paid_units  
- A01–A06 deep niches (SaaS billing, agent ops, …)  
- near_core band, confidence ~0.94  
- conceptual + executive algorithms уже дистиллятся  

**GenCore** делает это **системой**: каждый GO-прогон → skill → следующий generate богаче; post-pay identity → gen_v2+ слоты.

---

## 2. Влияние реальных прогонов (обязательный input)

Источники: `backend/data/skill_memory/sk_*`, library runs Architecture Design Library.

| Наблюдение из прогонов | Влияние на GenCore |
|------------------------|-------------------|
| Повтор library → domain `knowledge_library`, unit_pack | **Domain priors** в router: library always product_pack first |
| Warrants S1–S4 стабильны | **Template spine** S* не регенерировать с нуля — mutate |
| A01–A06 design claims повторяются | **Card genome**: mix niche cards by score, not full rewrite |
| Executive pilot_21d + assist_steps identical shape | **Executive compiler**: one schema, fill dates/names |
| confidence 0.94, band near_core | **Ship gate** for skill persist: conf≥0.55 or near_core |
| conceptual anti_patterns fixed | **Hard rails** in GenCore (no auto-yield, no 5 channels) |
| Identity Q now unique per hash | **Question genome** separate from ops Q |

**Оценка влияния:** текущие прогоны **подтверждают** GenCore как compiler+memory, не LLM-свалку. План не ломается — усиливается (skill_memory + identity gen slots уже в коде).

---

## 3. Архитектура GenCore

```
Brief
  → SmartRouter (domain/surface/depth/products/skills)
  → SpineCompiler (S1–S4 + cards genome + channel log)
  → SkillMemory.load (top-K conceptual+executive)
  → Compose (consult pack + live log session)
  → [pay wall]
  → IdentityEngine (unique Q + delight forecast)
  → answers
  → GenSlots v2–v5 (uniqueness card, voice, proof post, result-pack)
  → SkillMemory.distill (if GO)
```

### Модули

| Module | Role |
|--------|------|
| SpineCompiler | core_deliverable + dates |
| SkillMemory | conceptual + executive algorithms |
| IdentityEngine | post-pay uniqueness + Q genome |
| LiveLog | 7-day executable log (→ Supabase) |
| AssistAgent | deploy queue |
| PromotionPack | 3 roads + DM |
| GenSlotRunner | **new** — gen_v2+ from answers |

---

## 4. Roadmap

### Phase A — now (shipped / this release)
- [x] skill distill on success  
- [x] live log session + tick API  
- [x] unique identity questions + delight forecast  
- [x] open gen slots listed post-pay  
- [ ] Supabase adapter (doc ready)

### Phase B — GenCore v0.1
- GenSlotRunner: uniqueness 1-pager from identity answers  
- Re-generate button with `answers` + `generation: v2`  
- Skill load affects card ranking (not only storage)

### Phase C — GenCore v0.2
- Voice pack (golden examples from answers)  
- Proof post draft (X-style, Metrix principles)  
- Client result-pack HTML template  

### Phase D — GenCore v1
- Optional LLM only inside GenSlotRunner (not consult spine)  
- Supabase skills table + live log  
- Private room handoff  

---

## 5. Принципы (голос Metrix)

1. Orient → pick → ship  
2. Same product · different analytics · different money  
3. Ops ≠ promo  
4. Failed hypothesis = cheap cycle  
5. Not another chat — **live pack**  
6. Author must **like** the uniqueness forecast (delight_score)

---

## 6. Метрики успеха GenCore

| Metric | Target |
|--------|--------|
| % runs that distill a skill | ≥ 60% |
| Post-pay identity answer rate | ≥ 40% of paid |
| gen_v2 request after answers | ≥ 25% |
| Delight score mean | ≥ 0.7 |
| Live log ≥3 ticks / session | ≥ 30% |

---

## 7. Что не трогать

- Consultation spine (карточки, PDF, TZ plan, expert base) — флагман 1  
- Pay-after-approve messaging  
- Hard rails: no auto-yield  

---

## 8. Связь с кодом

| Path | Status |
|------|--------|
| `skill_memory.py` | live |
| `identity_engine.py` | live |
| `live_log.py` | live (file; Supabase planned) |
| `smart_router.py` | live |
| GenSlotRunner | **planned Phase B** |
