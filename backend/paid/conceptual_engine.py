"""
Conceptual Engine — OPEN final planning step (deliberately incomplete).

Purpose (when activated after paid deliverable):
  Forecast a *vision* of further stages in the client's **outgoing supply chain**
  using:
    · statistics / situation metrics from prior paid pass
    · derivative sensitivity levers
    · a **narrowing model** (progressive constraint of possibility space)

This module is intentionally a precise scaffold — not a fake complete oracle.
It reduces uncertainty everywhere *except* the creative last-mile vision pass,
which must remain open for founder + next iteration completion.

Narrowing model (documented for implementers):

  S₀ = potential phenomenon space volume (from Blue Ocean Synthesis Core)
  For stage k = 1..K:
      L_k   = top levers at stage k (from Function Engine / Situation Metrics)
      C_k   = constraints (capacity, SLA, margin floor, delivery friction)
      N_k   = S_{k-1} · ∏_i (1 − α·clamp(|∂F/∂x_i|)) · (1 − β·friction_k)
      Vision_k = argmax expected value under N_k subject to honesty caps

  Amplitude tracking replaces heavy cycles: only stages whose amplitude
  exceeds threshold enter the chain (algorithmic transitions).

OPEN completion points are explicit in every return payload.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01, safe_float


# Default outgoing supply-chain stage template (business-facing, not logistics-only)
DEFAULT_OUTGOING_STAGES = (
    "signal_capture",       # demand / job signal
    "offer_formation",      # value prop packaging
    "delivery_execution",   # product/service fulfillment
    "feedback_billing",     # payment + learning
    "expansion_edge",       # next market edge / bifurcation
)


class ConceptualEngine:
    """
    Scaffold for supply-chain vision forecasting.

    `preview()` — safe partial projection from available statistics (demoable).
    `plan()`    — full vision; currently returns structured OPEN handoff
                  so the system stays honest about completion state.
    """

    name = "Conceptual Engine (Supply-Chain Vision)"
    status = "open_scaffold"  # not fully closed on purpose

    def __init__(
        self,
        stages: tuple[str, ...] = DEFAULT_OUTGOING_STAGES,
        alpha: float = 0.22,
        beta: float = 0.28,
        amplitude_threshold: float = 0.28,
    ) -> None:
        self.stages = stages
        self.alpha = alpha
        self.beta = beta
        self.amplitude_threshold = amplitude_threshold

    def preview(
        self,
        *,
        paid: dict[str, Any] | None = None,
        situation_metrics: dict[str, Any] | None = None,
        blue_ocean: dict[str, Any] | None = None,
        trajectory: dict[str, Any] | None = None,
        statistics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Partial narrowing preview — deterministic, no fake certainty.

        Uses residual uncertainty from trajectory + situation leaks +
        blue-ocean open volume to sketch stage amplitudes.
        """
        paid = paid or {}
        sm = situation_metrics or paid.get("situation_metrics") or paid.get(
            "business_metrics"
        ) or {}
        bo = blue_ocean or paid.get("blue_ocean") or {}
        traj = trajectory or paid.get("conceptual_trajectory") or {}
        stats = dict(statistics or {})

        plane = (paid.get("function_engine") or {}).get("output_plane") or {}
        sens = list((paid.get("function_engine") or {}).get("sensitivities") or [])
        top_lever = (paid.get("function_engine") or {}).get("top_lever") or "clarity"

        s0 = safe_float(
            ((bo.get("architecture") or {}).get("synthesis_core") or {})
            .get("potential_phenomenon_space", {})
            .get("open_volume"),
            0.45,
        )
        residual_u = safe_float(traj.get("residual_uncertainty"), 0.35)
        friction = safe_float(sm.get("delivery_friction"), 0.4)
        margin_p = safe_float(sm.get("margin_pressure"), 0.4)
        situation = safe_float(sm.get("situation_score"), 0.5)
        readiness = safe_float(
            plane.get("paid_readiness") or (paid.get("package") or {}).get("paid_score"),
            0.5,
        )

        # Lever magnitudes for narrowing product
        lever_mags: list[float] = []
        for s in sens[:6]:
            lever_mags.append(abs(safe_float(s.get("derivative"), 0.1)))
        if not lever_mags:
            lever_mags = [0.35]

        chain: list[dict[str, Any]] = []
        volume = clamp01(s0)
        for i, stage_name in enumerate(self.stages):
            # Stage-specific pressure (algorithmic transition, not a for-cycle search)
            stage_friction = clamp01(
                friction * (0.85 + 0.08 * i) + 0.1 * margin_p * (i / max(1, len(self.stages) - 1))
            )
            narrow_factor = 1.0
            for mag in lever_mags:
                narrow_factor *= 1.0 - self.alpha * clamp01(mag)
            narrow_factor *= 1.0 - self.beta * stage_friction
            narrow_factor = max(0.15, min(1.0, narrow_factor))
            volume = clamp01(volume * narrow_factor)

            amplitude = clamp01(
                0.35 * readiness
                + 0.25 * situation
                + 0.20 * (1.0 - residual_u)
                + 0.20 * (1.0 - stage_friction)
            )
            # Soft stage bias
            if stage_name == "delivery_execution":
                amplitude = clamp01(amplitude * (1.0 - 0.25 * friction))
            elif stage_name == "expansion_edge":
                amplitude = clamp01(
                    amplitude
                    * (
                        0.7
                        + 0.3
                        * safe_float(
                            (bo.get("aggregate_readiness")), readiness
                        )
                    )
                )

            active = amplitude >= self.amplitude_threshold
            chain.append(
                {
                    "index": i + 1,
                    "stage": stage_name,
                    "amplitude": round(amplitude, 4),
                    "volume_after_narrowing": round(volume, 4),
                    "friction": round(stage_friction, 4),
                    "active": active,
                    "primary_lever_hint": top_lever,
                    "vision_seed": _vision_seed(stage_name, top_lever, sm),
                    "status": "preview_active" if active else "preview_dim",
                }
            )

        return {
            "module": self.name,
            "mode": "preview",
            "status": self.status,
            "s0_open_volume": round(s0, 4),
            "residual_uncertainty": round(residual_u, 4),
            "narrowing": {
                "alpha": self.alpha,
                "beta": self.beta,
                "amplitude_threshold": self.amplitude_threshold,
                "formula": (
                    "N_k = S_{k-1} · ∏(1−α·|∂F/∂x|) · (1−β·friction_k); "
                    "activate if amplitude ≥ threshold"
                ),
            },
            "outgoing_chain": chain,
            "active_stages": [c["stage"] for c in chain if c["active"]],
            "statistics_used": {
                "situation_score": situation,
                "delivery_friction": friction,
                "margin_pressure": margin_p,
                "top_lever": top_lever,
                "extra": {k: stats[k] for k in list(stats)[:8]},
            },
            "honesty": (
                "Preview only — not a locked forecast. "
                "Full vision requires plan() completion with founder context."
            ),
            "open_points": [
                "OPEN: full ConceptualEngine.plan() vision narrative",
                "OPEN: industry-specific outgoing stage libraries",
                "OPEN: live statistics feed into narrowing coefficients",
                "OPEN: multi-horizon bifurcation at expansion_edge",
            ],
            "summary": (
                f"ConceptualEngine preview: {sum(1 for c in chain if c['active'])}/"
                f"{len(chain)} stages active; residual_u={residual_u:.2f}; "
                f"volume_end={volume:.2f}."
            ),
        }

    def plan(self, **kwargs: Any) -> dict[str, Any]:
        """
        Full vision planner — deliberately returns OPEN handoff.

        Call after paid package is packageable and Must-Ask is satisfied.
        Future iteration fills creative vision body; structure is fixed now.
        """
        preview = self.preview(**kwargs)
        return {
            **preview,
            "mode": "plan",
            "status": "awaiting_final_creative_pass",
            "vision": {
                "state": "OPEN",
                "title": "Outgoing supply-chain vision (unfilled)",
                "body": None,
                "requires": [
                    "paid package status packageable|ready",
                    "must_ask answered for entities·flows·levers·jobs·metrics",
                    "founder confirmation of residual uncertainty band",
                    "optional live statistics override",
                ],
            },
            "handoff": {
                "from": "PaidProductCore.step16",
                "to": "ConceptualEngine.plan",
                "message": (
                    "Structure and narrowing math are ready. "
                    "Final vision narrative is the intentional last open step."
                ),
            },
            "summary": (
                "ConceptualEngine.plan: structure ready, vision body OPEN "
                "for last creative / founder completion pass."
            ),
        }


def _vision_seed(stage: str, lever: str, sm: dict[str, Any]) -> str:
    leak = sm.get("top_leak") or {}
    leak_id = leak.get("id") if isinstance(leak, dict) else (str(leak) if leak else "leak")
    seeds = {
        "signal_capture": f"Capture demand jobs; watch lever «{lever}» on intake quality.",
        "offer_formation": f"Package offer around «{lever}»; compress claim surface (honesty).",
        "delivery_execution": f"Cut delivery friction; address leak «{leak_id}» first.",
        "feedback_billing": "Close billing loop; accrete data-value into ledger hooks.",
        "expansion_edge": f"Only expand where bifurcation score holds; lever «{lever}».",
    }
    return seeds.get(stage, f"Stage {stage} guided by {lever}")
