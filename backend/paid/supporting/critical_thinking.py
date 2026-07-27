"""
Critical Thinking Layer — supporting module for the Paid Product.

Responsibilities:
  · Group all indicators by clear principles
    (zone, amplitude, derivative sensitivity, energy direction, discrepancy type)
  · When metric tests / parallel details disagree with paid-part results:
      – choose the correct variant
      – classify the reason for discrepancy
      – conclude about a possible founder error
  · Insert detailed descriptions developed during the work

Does not invent new heavy engines — uses paid + parallel surfaces already computed.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import (
    DiscrepancyRecord,
    FounderErrorConclusion,
    IndicatorGroup,
    clamp01,
    safe_float,
)


class CriticalThinkingLayer:
    """Group, compare paid vs parallel, classify, founder-error conclusion."""

    name = "Critical Thinking Layer"

    def analyze(
        self,
        *,
        function_engine: dict[str, Any] | None = None,
        energy_flow: dict[str, Any] | None = None,
        virtual_chips: dict[str, Any] | None = None,
        mega_map: dict[str, Any] | None = None,
        hypotheses: dict[str, Any] | None = None,
        calm_point: dict[str, Any] | None = None,
        metric_tests: dict[str, Any] | None = None,
        parallel: dict[str, Any] | None = None,
        package_claim: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        function_engine = function_engine or {}
        energy_flow = energy_flow or {}
        virtual_chips = virtual_chips or {}
        mega_map = mega_map or {}
        hypotheses = hypotheses or {}
        calm_point = calm_point or {}
        metric_tests = metric_tests or {}
        parallel = parallel or {}
        package_claim = package_claim or {}

        groups = self._group_indicators(
            function_engine, energy_flow, virtual_chips, mega_map
        )
        discrepancies = self._paid_vs_parallel(
            function_engine,
            energy_flow,
            mega_map,
            calm_point,
            metric_tests,
            parallel,
            package_claim,
            hypotheses,
        )
        founder = self._founder_error(discrepancies, metric_tests, parallel)

        # Choose resolved indicators after discrepancy arbitration
        resolved = self._resolve_variants(discrepancies, function_engine, parallel)

        descriptions = {
            "zone": (
                "Zones inherit Superstructure Sol/Fi topology; chip amplitude "
                "is the paid-layer load, not free-demo traffic."
            ),
            "amplitude": (
                "Amplitude is Market Unit energy intensity after Virtual Chip "
                "instantiation; redistribution softens incorrect peaks."
            ),
            "derivative_sensitivity": (
                "Derivative sensitivity is ∂F/∂x on the abstract value plane; "
                "elasticity scales leverage by parameter level."
            ),
            "energy_direction": (
                "Signed energy direction: +source (injects), −sink (absorbs). "
                "Conflicts under high joint amplitude = incorrect entanglement."
            ),
            "discrepancy_type": (
                "Discrepancies: paid result vs parallel details (orientation scores, "
                "OAE bridge, metric tests). Each has reason class + chosen variant."
            ),
            "founder_error": (
                "Founder error = possible framing / metric-blind-spot / over-generalization "
                "by the system author path when paid systematically overclaims vs parallel."
            ),
        }

        severity_max = max(
            [g.severity for g in groups]
            + [safe_float(d.severity) for d in discrepancies]
            + [0.0]
        )

        return {
            "module": self.name,
            "groups": [g.to_dict() for g in groups],
            "group_count": len(groups),
            "discrepancies": [d.to_dict() for d in discrepancies],
            "discrepancy_count": len(discrepancies),
            "resolved_variant": resolved,
            "founder_error": founder.to_dict(),
            "descriptions": descriptions,
            "field_severity": round(clamp01(severity_max), 4),
            "thinking_trace": [
                "Group indicators by zone / amplitude / sensitivity / direction",
                "Run paid-part vs parallel-detail metric comparisons",
                "Choose correct variant per discrepancy",
                "Classify reason codes",
                "Conclude possible founder error",
            ],
            "summary": (
                f"Critical Thinking: {len(groups)} groups, "
                f"{len(discrepancies)} discrepancies, "
                f"founder_suspected={founder.suspected}, "
                f"field_severity={severity_max:.2f}."
            ),
        }

    # ── grouping ─────────────────────────────────────────────────────────

    def _group_indicators(
        self,
        function_engine: dict[str, Any],
        energy_flow: dict[str, Any],
        virtual_chips: dict[str, Any],
        mega_map: dict[str, Any],
    ) -> list[IndicatorGroup]:
        groups: list[IndicatorGroup] = []

        zone_infl = virtual_chips.get("zone_influence") or {}
        if zone_infl:
            groups.append(
                IndicatorGroup(
                    group_key="zones",
                    by="zone",
                    members=[f"{z}:{v}" for z, v in zone_infl.items()],
                    description="Zone influence amplitudes from Virtual Chips.",
                    severity=clamp01(
                        max((safe_float(v) for v in zone_infl.values()), default=0) / 3.0
                    ),
                )
            )

        nodes = energy_flow.get("nodes") or []
        if nodes:
            high = [n["id"] for n in nodes if safe_float(n.get("amplitude")) >= 0.65]
            mid = [
                n["id"]
                for n in nodes
                if 0.35 <= safe_float(n.get("amplitude")) < 0.65
            ]
            low = [n["id"] for n in nodes if safe_float(n.get("amplitude")) < 0.35]
            groups.append(
                IndicatorGroup(
                    group_key="amplitude_bands",
                    by="amplitude",
                    members=[
                        f"high:{','.join(high) or '—'}",
                        f"mid:{','.join(mid) or '—'}",
                        f"low:{','.join(low) or '—'}",
                    ],
                    description="Energy amplitudes banded high/mid/low.",
                    severity=clamp01(len(high) / max(1, len(nodes))),
                )
            )
            sources = [
                n["id"]
                for n in nodes
                if safe_float(n.get("corrected_direction", n.get("direction"))) > 0.15
            ]
            sinks = [
                n["id"]
                for n in nodes
                if safe_float(n.get("corrected_direction", n.get("direction"))) < -0.15
            ]
            groups.append(
                IndicatorGroup(
                    group_key="energy_direction",
                    by="energy_direction",
                    members=[
                        f"sources:{','.join(sources[:6]) or '—'}",
                        f"sinks:{','.join(sinks[:6]) or '—'}",
                    ],
                    description="Energy direction after disentanglement.",
                    severity=clamp01(safe_float(energy_flow.get("total_entanglement"))),
                    discrepancy_type=(
                        "direction_conflict"
                        if energy_flow.get("pair_count", 0)
                        else None
                    ),
                )
            )

        sens = function_engine.get("sensitivities") or []
        if sens:
            top = sens[:5]
            groups.append(
                IndicatorGroup(
                    group_key="derivative_sensitivity",
                    by="derivative_sensitivity",
                    members=[
                        f"{s.get('parameter')}:∂={s.get('derivative')}" for s in top
                    ],
                    description="Top partial derivatives of abstract value F.",
                    severity=clamp01(
                        abs(safe_float(top[0].get("derivative"))) if top else 0.0
                    ),
                )
            )

        comparison = mega_map.get("comparison") or {}
        disc_members = []
        if int(comparison.get("competing_pairs") or 0):
            disc_members.append("hypothesis_coordinate_overlap")
        if safe_float(comparison.get("mean_uncertainty")) >= 0.55:
            disc_members.append("high_coordinate_uncertainty")
        groups.append(
            IndicatorGroup(
                group_key="discrepancy_types",
                by="discrepancy_type",
                members=disc_members or ["none_map"],
                description="Map-level discrepancy types before paid↔parallel pass.",
                severity=clamp01(0.2 * len(disc_members)),
                discrepancy_type="map_aggregate",
            )
        )
        return groups

    # ── paid vs parallel ─────────────────────────────────────────────────

    def _paid_vs_parallel(
        self,
        function_engine: dict[str, Any],
        energy_flow: dict[str, Any],
        mega_map: dict[str, Any],
        calm_point: dict[str, Any],
        metric_tests: dict[str, Any],
        parallel: dict[str, Any],
        package_claim: dict[str, Any],
        hypotheses: dict[str, Any],
    ) -> list[DiscrepancyRecord]:
        out: list[DiscrepancyRecord] = []
        plane = function_engine.get("output_plane") or {}
        scores = parallel.get("scores") or {}
        comparison = mega_map.get("comparison") or {}

        # D1 product axis vs product_fit
        if scores:
            paid_p = safe_float(plane.get("product_axis"), 0.5)
            par_p = safe_float(scores.get("product_fit"), paid_p)
            delta = abs(paid_p - par_p)
            if delta >= 0.18:
                # Prefer parallel if orientation is high-confidence readiness
                readiness = safe_float(scores.get("readiness"), 0.5)
                chosen = "parallel" if readiness >= 0.55 and par_p > paid_p else (
                    "paid" if paid_p > par_p + 0.1 else "blend"
                )
                out.append(
                    DiscrepancyRecord(
                        id="d_product_axis",
                        paid_signal=f"product_axis={paid_p:.2f}",
                        parallel_signal=f"product_fit={par_p:.2f}",
                        delta=delta,
                        reason="param_drift" if delta < 0.35 else "zone_desync",
                        chosen_variant=chosen,
                        severity=clamp01(delta),
                        detail="Paid product axis vs orientation product_fit.",
                    )
                )

            paid_m = safe_float(plane.get("model_axis"), 0.5)
            par_m = safe_float(scores.get("model_fit"), paid_m)
            delta_m = abs(paid_m - par_m)
            if delta_m >= 0.18:
                out.append(
                    DiscrepancyRecord(
                        id="d_model_axis",
                        paid_signal=f"model_axis={paid_m:.2f}",
                        parallel_signal=f"model_fit={par_m:.2f}",
                        delta=delta_m,
                        reason="param_drift",
                        chosen_variant="blend",
                        severity=clamp01(delta_m * 0.9),
                        detail="Paid model axis vs orientation model_fit.",
                    )
                )

        # D2 paid_readiness claim vs metric info compatibility
        for t in metric_tests.get("failed") or []:
            tid = str(t.get("id") or "test")
            if tid == "t_info_compatibility":
                out.append(
                    DiscrepancyRecord(
                        id="d_info_compat",
                        paid_signal=f"paid_readiness={plane.get('paid_readiness')}",
                        parallel_signal=t.get("detail") or "info_compat failed",
                        delta=1.0 - safe_float(t.get("score"), 0.0),
                        reason="metric_incompatibility",
                        chosen_variant="parallel",
                        severity=clamp01(1.0 - safe_float(t.get("score"), 0.0)),
                        detail="Informational compatibility test failed — trust parallel scores more.",
                    )
                )
            elif tid == "t_calm_substance":
                out.append(
                    DiscrepancyRecord(
                        id="d_calm_substance",
                        paid_signal=f"entropy={calm_point.get('entropy')}",
                        parallel_signal=t.get("detail") or "calm/substance fail",
                        delta=0.4,
                        reason="calm_premature",
                        chosen_variant="parallel",
                        severity=0.55,
                        detail="Calm form premature relative to paid substance.",
                    )
                )
            elif tid == "t_root_alignment":
                out.append(
                    DiscrepancyRecord(
                        id="d_root_align",
                        paid_signal=f"best={comparison.get('best_hypothesis_id')}",
                        parallel_signal=t.get("detail") or "low root alignment",
                        delta=1.0 - safe_float(t.get("score"), 0.0),
                        reason="map_root_divergence",
                        chosen_variant="hold",
                        severity=clamp01(1.0 - safe_float(t.get("score"), 0.0)),
                        detail="Best hypothesis diverges from root task on Mega Map.",
                    )
                )

        # D3 package paid_score overclaim vs entanglement
        paid_score = safe_float(package_claim.get("paid_score"), plane.get("paid_readiness"))
        ent = safe_float(energy_flow.get("total_entanglement"), 0.0)
        if paid_score >= 0.7 and ent >= 0.55:
            out.append(
                DiscrepancyRecord(
                    id="d_overclaim_energy",
                    paid_signal=f"paid_score={paid_score:.2f}",
                    parallel_signal=f"entanglement={ent:.2f}",
                    delta=paid_score - (1.0 - ent),
                    reason="paid_overclaim",
                    chosen_variant="parallel",
                    severity=clamp01(0.4 + 0.4 * ent),
                    detail="High paid score while Market Units still heavily entangled.",
                )
            )

        # D4 OAE bridge / abstract richness vs paid spine
        oae_abs = parallel.get("abstract_coordinates") or []
        hyp_n = int(hypotheses.get("count") or len(hypotheses.get("hypotheses") or []))
        if len(oae_abs) >= 3 and hyp_n <= 1:
            out.append(
                DiscrepancyRecord(
                    id="d_parallel_richer",
                    paid_signal=f"hypotheses={hyp_n}",
                    parallel_signal=f"oae_abstract={len(oae_abs)}",
                    delta=0.35,
                    reason="parallel_detail_richer",
                    chosen_variant="parallel",
                    severity=0.45,
                    detail="OAE double-bottom richer than paid hypothesis set — expand library.",
                )
            )

        # D5 energy conflict residual
        if int(energy_flow.get("pair_count") or 0) >= 3:
            out.append(
                DiscrepancyRecord(
                    id="d_energy_pairs",
                    paid_signal="energy_redistributed=true",
                    parallel_signal=f"pairs={energy_flow.get('pair_count')}",
                    delta=0.25,
                    reason="energy_conflict",
                    chosen_variant="blend",
                    severity=0.4,
                    detail="Multiple entangled pairs remain after redistribution.",
                )
            )

        return out

    def _resolve_variants(
        self,
        discrepancies: list[DiscrepancyRecord],
        function_engine: dict[str, Any],
        parallel: dict[str, Any],
    ) -> dict[str, Any]:
        """Aggregate chosen variants into a resolved stance."""
        if not discrepancies:
            return {
                "stance": "paid_consistent",
                "trust": "paid",
                "note": "No material paid↔parallel discrepancies.",
            }
        votes = {"paid": 0.0, "parallel": 0.0, "blend": 0.0, "hold": 0.0}
        for d in discrepancies:
            votes[d.chosen_variant] = votes.get(d.chosen_variant, 0.0) + d.severity
        trust = max(votes, key=votes.get)  # type: ignore[arg-type]
        plane = function_engine.get("output_plane") or {}
        scores = parallel.get("scores") or {}
        return {
            "stance": trust,
            "trust": trust,
            "votes": {k: round(v, 4) for k, v in votes.items()},
            "paid_plane_snapshot": plane,
            "parallel_scores_snapshot": scores,
            "note": f"Resolved trust={trust} from {len(discrepancies)} discrepancies.",
        }

    def _founder_error(
        self,
        discrepancies: list[DiscrepancyRecord],
        metric_tests: dict[str, Any],
        parallel: dict[str, Any],
    ) -> FounderErrorConclusion:
        """
        Founder error = systematic bias in how the paid path was framed
        relative to parallel verified details (not a client error).
        """
        if not discrepancies:
            return FounderErrorConclusion(
                suspected=False,
                confidence=0.1,
                error_class="none",
                rationale="No paid↔parallel discrepancies requiring founder review.",
                recommended_correction="Continue showcase path; monitor next iteration.",
            )

        overclaim = sum(
            1
            for d in discrepancies
            if d.reason in ("paid_overclaim", "calm_premature", "metric_incompatibility")
        )
        drift = sum(1 for d in discrepancies if d.reason in ("param_drift", "zone_desync"))
        map_div = sum(1 for d in discrepancies if d.reason == "map_root_divergence")
        sev = sum(d.severity for d in discrepancies) / max(1, len(discrepancies))
        failed_tests = len(metric_tests.get("failed") or [])

        suspected = False
        error_class = "none"
        rationale = ""
        correction = ""

        if overclaim >= 2 or (overclaim >= 1 and failed_tests >= 2 and sev >= 0.45):
            suspected = True
            error_class = "over_generalization"
            rationale = (
                "Paid path systematically overclaims relative to parallel details "
                f"and metric failures (overclaim={overclaim}, failed_tests={failed_tests}). "
                "Likely founder framing error: showcase package ahead of substance."
            )
            correction = (
                "Lower package status one tier; re-run with force=False; "
                "tighten paid_readiness gate; expand Hypothesis Library from OAE abstracts."
            )
        elif map_div and sev >= 0.4:
            suspected = True
            error_class = "frame_bias"
            rationale = (
                "Root-task frame may be wrong or too narrow — Mega Map best hypothesis "
                "diverges while other signals conflict."
            )
            correction = (
                "Re-state root task from client language; re-extract conceptual coordinates; "
                "do not package until root_alignment ≥ 0.45."
            )
        elif drift >= 2:
            suspected = True
            error_class = "metric_blind_spot"
            rationale = (
                "Repeated param/zone drift between paid plane and orientation scores "
                "suggests founder metric map misses a parallel axis."
            )
            correction = (
                "Add missing parallel axis into Function Engine plane; "
                "re-blend System Design Library params with orientation."
            )
        elif any(d.reason == "energy_conflict" for d in discrepancies) and sev >= 0.4:
            suspected = True
            error_class = "zone_blindness"
            rationale = (
                "Energy conflicts across zones persist — founder zone topology "
                "may under-specify Market Units coupling."
            )
            correction = (
                "Review Virtual Chip zone assignment; re-run Energy Flow with "
                "higher redistribution_rate; keep showcase as preview only."
            )
        else:
            rationale = (
                f"{len(discrepancies)} discrepancies at mean severity {sev:.2f} — "
                "below founder-error threshold; treat as normal arbitration."
            )
            correction = "Apply resolved variant trust; no founder correction required."

        conf = clamp01(0.35 + 0.4 * sev + 0.1 * overclaim + 0.05 * failed_tests)
        if not suspected:
            conf = min(conf, 0.35)

        return FounderErrorConclusion(
            suspected=suspected,
            confidence=conf,
            error_class=error_class,
            rationale=rationale,
            recommended_correction=correction,
        )
