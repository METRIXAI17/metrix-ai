"""
Conceptual Trajectory — visible path of paid-core reasoning.

Marks every major process step so outputs stay non-template and auditable:
  raw input → hypotheses → compute/energy → calm/map → deliverable
  …then OPEN handoff to Conceptual Engine (supply-chain vision).

Reader stage 5 and Hypothesis Library consume this trajectory for learning.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import ConceptualStep, ConceptualTrajectory, clamp01, safe_float


class TrajectoryBuilder:
    """Build and refine the conceptual trajectory for one paid run."""

    name = "Conceptual Trajectory"

    def build(
        self,
        *,
        root_task: str,
        flow_trace: list[dict[str, Any]] | None = None,
        package: dict[str, Any] | None = None,
        mega_map: dict[str, Any] | None = None,
        hyp_lib: dict[str, Any] | None = None,
        reader: dict[str, Any] | None = None,
        founder_error: dict[str, Any] | None = None,
        residual_uncertainty: float | None = None,
    ) -> dict[str, Any]:
        flow_trace = flow_trace or []
        package = package or {}
        mega_map = mega_map or {}
        hyp_lib = hyp_lib or {}
        reader = reader or {}
        founder_error = founder_error or {}

        traj = ConceptualTrajectory(
            root_task=root_task,
            final_status=str(package.get("status") or "in_progress"),
            residual_uncertainty=0.35,
            next_open_engine="ConceptualEngine.supply_chain_vision",
        )

        # Macro conceptual marks (not all 16 micro-steps — keep elegant)
        macro: list[tuple[str, str, list[int]]] = [
            ("raw_input", "Raw intake & frame", [1, 2]),
            ("design_hardware", "Design library + Virtual Chips", [3, 4]),
            ("hypotheses", "Hypothesis modules & probe", [5, 6]),
            ("compute_energy", "Function plane + energy disentangle", [7, 8]),
            ("form_map", "Calm-point → Mega Map", [9, 10]),
            ("verify", "Metrics + critical honesty", [11, 12, 14]),
            ("learn_narrate", "Reader 5-stage + Hypothesis Library", [13, 15]),
            ("deliverable", "Paid package showcase", [16]),
        ]

        by_step = {int(t.get("step", 0)): t for t in flow_trace if t.get("step")}
        prev_delta = 0.0
        for i, (stage, name, step_ids) in enumerate(macro, start=1):
            payloads = [by_step[s] for s in step_ids if s in by_step]
            status = "ok" if payloads else "skip"
            if stage == "deliverable" and founder_error.get("suspected"):
                status = "ok"  # still produced, honesty layer flagged
            inp = ", ".join(
                str(p.get("name") or f"step {p.get('step')}") for p in payloads[:3]
            ) or name
            # Prefer payload summaries when present
            outs: list[str] = []
            for p in payloads:
                pl = p.get("payload") or {}
                if pl.get("summary"):
                    outs.append(str(pl["summary"])[:120])
                elif p.get("notes"):
                    outs.append(str(p["notes"])[:80])
            out_s = "; ".join(outs) if outs else f"{name} complete"
            # Coordinate uncertainty from mega map for form_map stage
            delta = prev_delta
            if stage == "form_map":
                comp = mega_map.get("comparison") or {}
                delta = safe_float(comp.get("mean_uncertainty"), 0.35)
            elif stage == "hypotheses":
                delta = 0.2 + 0.1 * len(hyp_lib.get("picked") or [])
            elif stage == "deliverable":
                delta = 1.0 - safe_float(package.get("paid_score"), 0.5)
            prev_delta = delta

            learning = ""
            if stage == "learn_narrate":
                learning = str(
                    (hyp_lib.get("deep_previous_step") or {}).get("finding")
                    or (reader.get("plain_summary") or "")[:160]
                )
            open_pt = ""
            if stage == "deliverable":
                open_pt = (
                    "OPEN: next conceptual mark → Conceptual Engine "
                    "(outgoing supply-chain vision + narrowing models)."
                )

            traj.append(
                ConceptualStep(
                    index=i,
                    name=name,
                    stage=stage,
                    status=status,
                    input_summary=inp[:200],
                    output_summary=out_s[:240],
                    coords_delta=float(delta),
                    learning_note=learning[:200],
                    open_point=open_pt,
                )
            )

        # Residual uncertainty: map + founder + readiness
        map_u = safe_float(
            (mega_map.get("comparison") or {}).get("mean_uncertainty"), 0.35
        )
        fe_c = safe_float(founder_error.get("confidence"), 0.0) if founder_error.get(
            "suspected"
        ) else 0.0
        ready = safe_float(package.get("paid_readiness") or package.get("paid_score"), 0.5)
        residual = clamp01(
            0.45 * map_u
            + 0.25 * fe_c
            + 0.30 * (1.0 - ready)
        )
        if residual_uncertainty is not None:
            residual = clamp01(residual_uncertainty)
        traj.residual_uncertainty = residual
        traj.final_status = str(package.get("status") or traj.final_status)

        d = traj.to_dict()
        d["module"] = self.name
        d["macro_count"] = len(macro)
        d["feeds"] = {
            "reader_stage_5": True,
            "hypothesis_library": True,
            "conceptual_engine_open": True,
        }
        d["summary"] = (
            f"Trajectory: {d['path_summary']} | residual_u={residual:.2f} | "
            f"next={traj.next_open_engine}"
        )
        return d
