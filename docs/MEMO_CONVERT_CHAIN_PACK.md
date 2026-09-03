# Memo Convert v2 — Chain Pack

Memo Convert is not an idea-DB. It relays what is already assembled.

Input: `chain_id` or raw system text.  
Output (same 1–4 as v1) plus:

```
chain_pack {
  b2c_path?, a2a_path?,
  bound_resources, artefacts[],
  naming sigils,
  gates snapshot (VVI/ER/RRC/assembly/consistency),
  copy_blocks on 3 voices,
  miniapp_case_stub
}
```

Holes → U + `unbound_critical`. Convert does not invent slots.

Two call sites, one engine: `POST /api/v1/analytics/memo-convert` and the Telegram `/pack` surface. Feature flag `convert_v2` in `meta.version` (≥ Market Units 1.3.0). Unbound critical slots feed OAE missing params and keep Main gated.
