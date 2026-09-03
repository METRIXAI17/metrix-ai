# B2C chain vs A2A chain

Two topologies. Two constructors. Mixed request → Decision Core dual path: two `chain_id`, one `parent_bundle`.

```
B2C:  person → free consult / Auto-consult → direction → pilot gates → Promo/MM/Auto Orders/Full Package
      phases D0–1 / D1–4 / D3–10 tied to chain_id
      Main $2490 iff predicted_end≥0.7 and risk≠high

A2A:  agency ↔ agency via Market Units v2
      handoff matrix, sync score, deadlock, load
      artefact travels as handoff, not as a package purchase
      POST /market-units/run  chain_mode="a2a"

Outreach massmarket is A2A-only (Distribution 3D). Flag massmarket_a2a. Not a D2C offramp badge. No lead promise.
```

Agency briefs do not get the B2C stepper. Consumer briefs do not get the handoff matrix.
