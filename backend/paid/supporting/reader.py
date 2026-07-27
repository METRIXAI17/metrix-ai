"""
Reader — 5-Stage Learning Interpreter (critical supporting module).

Does NOT read from a ready-made database.
Builds a 5-stage model on the fly to realize meaning by learning it:

  1. Perception / Raw Data Intake
  2. Notation & Naming (structure + boundaries)
  3. Objectification → Virtual Asset (weight, price_signal, owner, branding)
  4. Interpretation & Connection (context, energy flows, zones, prior patterns)
  5. Application + Learning Loop (trajectory + feed Hypothesis Library)

Native flow: Phenomenon → Notation → Object → Virtual Asset (with branding).
Compatible with Virtual Chips and Blue Ocean Synthesis Core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.paid.types import (
    NotationUnit,
    PhenomenonUnit,
    VirtualAsset,
    clamp01,
    safe_float,
)


def _level(x: float, low: str, mid: str, high: str) -> str:
    if x < 0.34:
        return low
    if x < 0.67:
        return mid
    return high


def _sid(prefix: str, text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}_{h}"


class Reader:
    """
    5-stage on-the-fly learning interpreter.

    `explain()` remains the public entry (orchestrator compatibility).
    Internally runs the full 5-stage model, then produces narrative sections.
    """

    name = "Reader (5-Stage Learning Interpreter)"

    STAGES = (
        "1_perception",
        "2_notation",
        "3_objectification",
        "4_interpretation",
        "5_application_learning",
    )

    def explain(self, paid_bundle: dict[str, Any]) -> dict[str, Any]:
        """Public API: run 5-stage model + human narrative."""
        stages = self.run_five_stages(paid_bundle)
        narrative = self._narrative_from_stages(stages, paid_bundle)
        return {
            **narrative,
            "module": self.name,
            "stages": stages,
            "stage_names": list(self.STAGES),
            "virtual_assets": stages.get("3_objectification", {}).get("virtual_assets")
            or [],
            "phenomenon_chain": {
                "phenomena": stages.get("1_perception", {}).get("phenomena") or [],
                "notations": stages.get("2_notation", {}).get("notations") or [],
                "objects": stages.get("3_objectification", {}).get("objects") or [],
                "virtual_assets": stages.get("3_objectification", {}).get(
                    "virtual_assets"
                )
                or [],
            },
            "learning_feedback": stages.get("5_application_learning", {}).get(
                "learning_feedback"
            )
            or {},
            "summary": (
                f"Reader 5-stage: phenomena="
                f"{len(stages.get('1_perception', {}).get('phenomena') or [])}, "
                f"assets="
                f"{len(stages.get('3_objectification', {}).get('virtual_assets') or [])}, "
                f"sections={len(narrative.get('sections') or [])}."
            ),
        }

    def run_five_stages(self, paid_bundle: dict[str, Any]) -> dict[str, Any]:
        """Build meaning on the fly — no static DB lookup."""
        s1 = self._stage1_perception(paid_bundle)
        s2 = self._stage2_notation(s1, paid_bundle)
        s3 = self._stage3_objectify(s2, paid_bundle)
        s4 = self._stage4_interpret(s3, paid_bundle)
        s5 = self._stage5_apply_learn(s4, paid_bundle)
        return {
            "1_perception": s1,
            "2_notation": s2,
            "3_objectification": s3,
            "4_interpretation": s4,
            "5_application_learning": s5,
        }

    # ── Stage 1 ──────────────────────────────────────────────────────────────

    def _stage1_perception(self, b: dict[str, Any]) -> dict[str, Any]:
        """Raw data intake — phenomena as sensed, not yet named hard."""
        phenomena: list[PhenomenonUnit] = []
        root = str(b.get("root_task") or (b.get("package") or {}).get("title") or "task")
        phenomena.append(
            PhenomenonUnit(
                id=_sid("ph", root),
                raw=root[:160],
                source="business",
                amplitude=0.65,
                zone="orientation",
            )
        )

        scores = {}
        # scores may live under system_design merged params or explicit
        sdl = b.get("system_design_library") or {}
        for k, v in (sdl.get("merged_params") or {}).items():
            if k in ("clarity", "impact", "readiness", "risk", "product_fit", "model_fit", "promo_fit"):
                scores[k] = safe_float(v)

        plane = (b.get("function_engine") or {}).get("output_plane") or {}
        if plane:
            phenomena.append(
                PhenomenonUnit(
                    id=_sid("ph", "plane"),
                    raw=(
                        f"paid_readiness={safe_float(plane.get('paid_readiness')):.2f},"
                        f"abstract_value={safe_float(plane.get('abstract_value')):.2f}"
                    ),
                    source="function_engine",
                    amplitude=clamp01(safe_float(plane.get("paid_readiness"), 0.5)),
                    zone="structure_fi",
                )
            )

        energy = b.get("energy_flow") or {}
        if energy:
            te = safe_float(energy.get("total_entanglement"), 0.4)
            phenomena.append(
                PhenomenonUnit(
                    id=_sid("ph", f"energy{te}"),
                    raw=f"entanglement={te:.2f}, pairs={energy.get('pair_count', 0)}",
                    source="energy",
                    amplitude=te,
                    zone="market_units",
                )
            )

        chips = b.get("virtual_chips") or {}
        for c in (chips.get("chips") or [])[:6]:
            phenomena.append(
                PhenomenonUnit(
                    id=_sid("ph", str(c.get("id"))),
                    raw=f"chip:{c.get('purpose') or c.get('id')}",
                    source="chip",
                    amplitude=safe_float(c.get("amplitude"), 0.5),
                    zone=str(c.get("zone") or "unknown"),
                )
            )

        mega = b.get("mega_map") or {}
        comp = mega.get("comparison") or {}
        if comp:
            phenomena.append(
                PhenomenonUnit(
                    id=_sid("ph", "mega"),
                    raw=(
                        f"best={comp.get('best_hypothesis_id')}, "
                        f"align={comp.get('root_alignment_score')}, "
                        f"u={comp.get('mean_uncertainty')}"
                    ),
                    source="mega_map",
                    amplitude=clamp01(
                        1.0 - safe_float(comp.get("mean_uncertainty"), 0.35)
                    ),
                    zone="mega_map",
                )
            )

        critical = b.get("critical_thinking") or {}
        fe = critical.get("founder_error") or {}
        if fe.get("suspected"):
            phenomena.append(
                PhenomenonUnit(
                    id=_sid("ph", "founder"),
                    raw=f"founder_frame_risk:{fe.get('error_class')}",
                    source="parallel",
                    amplitude=safe_float(fe.get("confidence"), 0.5),
                    zone="orientation",
                )
            )

        metrics = b.get("business_metrics") or b.get("situation_metrics") or {}
        if metrics.get("top_leak"):
            leak = metrics["top_leak"]
            lid = leak.get("id") if isinstance(leak, dict) else str(leak)
            phenomena.append(
                PhenomenonUnit(
                    id=_sid("ph", f"leak{lid}"),
                    raw=f"leak:{lid}",
                    source="situation_metrics",
                    amplitude=safe_float(
                        leak.get("severity") if isinstance(leak, dict) else 0.55, 0.55
                    ),
                    zone="market_units",
                )
            )

        return {
            "stage": 1,
            "name": "Perception / Raw Data Intake",
            "phenomena": [p.to_dict() for p in phenomena],
            "count": len(phenomena),
            "note": "No database read — phenomena assembled from live paid bundle.",
        }

    # ── Stage 2 ──────────────────────────────────────────────────────────────

    def _stage2_notation(
        self, s1: dict[str, Any], b: dict[str, Any]
    ) -> dict[str, Any]:
        """Give structure and boundaries — modeling language aware."""
        notations: list[NotationUnit] = []
        category_map = {
            "business": "job",
            "function_engine": "metric",
            "energy": "flow",
            "chip": "entity",
            "mega_map": "metric",
            "parallel": "lever",
            "situation_metrics": "lever",
        }
        for p in s1.get("phenomena") or []:
            src = str(p.get("source") or "unknown")
            cat = category_map.get(src, "entity")
            raw = str(p.get("raw") or "")
            name = raw.split(":")[0][:48] if ":" in raw else raw[:48]
            if src == "chip":
                name = raw.replace("chip:", "")[:48]
                cat = "entity"
            elif src == "situation_metrics":
                cat = "lever"
            boundary = f"zone={p.get('zone')}; amp≤{safe_float(p.get('amplitude')):.2f}"
            notations.append(
                NotationUnit(
                    id=_sid("nt", str(p.get("id"))),
                    name=name or "unnamed",
                    boundary=boundary,
                    phenomenon_id=str(p.get("id")),
                    category=cat,
                )
            )

        # Explicit modeling-language skeleton for Must-Ask / commercial
        modeling_skeleton = {
            "entities": [n.name for n in notations if n.category == "entity"][:6],
            "flows": [n.name for n in notations if n.category == "flow"][:4],
            "levers": [n.name for n in notations if n.category == "lever"][:4],
            "jobs": [n.name for n in notations if n.category == "job"][:3],
            "metrics": [n.name for n in notations if n.category == "metric"][:4],
        }

        return {
            "stage": 2,
            "name": "Notation & Naming",
            "notations": [n.to_dict() for n in notations],
            "count": len(notations),
            "modeling_skeleton": modeling_skeleton,
            "note": "Boundaries fixed before objectification (prevents overclaim).",
        }

    # ── Stage 3 ──────────────────────────────────────────────────────────────

    def _stage3_objectify(
        self, s2: dict[str, Any], b: dict[str, Any]
    ) -> dict[str, Any]:
        """Turn into tangible Virtual Assets with weight, price, owner, branding."""
        chips_by_zone: dict[str, list[dict[str, Any]]] = {}
        for c in (b.get("virtual_chips") or {}).get("chips") or []:
            z = str(c.get("zone") or "unknown")
            chips_by_zone.setdefault(z, []).append(c)

        plane = (b.get("function_engine") or {}).get("output_plane") or {}
        readiness = safe_float(plane.get("paid_readiness"), 0.5)
        objects: list[dict[str, Any]] = []
        assets: list[VirtualAsset] = []

        for n in s2.get("notations") or []:
            amp = 0.5
            # recover amplitude from boundary string if present
            if "amp≤" in str(n.get("boundary") or ""):
                try:
                    amp = float(str(n["boundary"]).split("amp≤")[1].split(";")[0])
                except (IndexError, ValueError):
                    amp = 0.5
            weight = clamp01(0.4 * amp + 0.35 * readiness + 0.25 * 0.5)
            price = clamp01(weight * (0.7 + 0.3 * readiness)) * 1.2
            zone = "orientation"
            if "zone=" in str(n.get("boundary") or ""):
                zone = str(n["boundary"]).split("zone=")[1].split(";")[0]
            owner = "founder"
            if n.get("category") == "flow":
                owner = "market"
            elif n.get("category") == "entity":
                owner = "platform"
            elif n.get("category") == "job":
                owner = "client"
            brand = self._brand(str(n.get("name") or "Asset"), zone)
            chip_id = None
            if chips_by_zone.get(zone):
                chip_id = chips_by_zone[zone][0].get("id")

            obj = {
                "id": _sid("obj", str(n.get("id"))),
                "notation_id": n.get("id"),
                "name": n.get("name"),
                "tangible": True,
                "zone": zone,
            }
            objects.append(obj)
            assets.append(
                VirtualAsset(
                    id=_sid("va", str(n.get("id"))),
                    name=str(n.get("name") or "Asset"),
                    weight=weight,
                    price_signal=price,
                    owner=owner,
                    branding=brand,
                    zone=zone,
                    notation_id=str(n.get("id")),
                    chip_id=str(chip_id) if chip_id else None,
                    tags=[str(n.get("category") or "asset"), zone],
                    open_point=""
                    if weight >= 0.35
                    else "OPEN: low-weight asset — needs founder validation.",
                )
            )

        # Always surface a package-level branded asset
        pkg = b.get("package") or {}
        if pkg:
            assets.append(
                VirtualAsset(
                    id=_sid("va", "package"),
                    name=str(pkg.get("title") or "Paid package")[:60],
                    weight=safe_float(pkg.get("paid_score"), readiness),
                    price_signal=safe_float(pkg.get("paid_score"), readiness) * 1.1,
                    owner="founder",
                    branding=self._brand("Metrix Paid Spine", "product_sol"),
                    zone="product_sol",
                    notation_id="package_root",
                    chip_id=None,
                    tags=["package", "deliverable"],
                )
            )

        return {
            "stage": 3,
            "name": "Objectification → Virtual Asset",
            "objects": objects,
            "virtual_assets": [a.to_dict() for a in assets],
            "asset_count": len(assets),
            "total_weight": round(sum(a.weight for a in assets), 4),
            "note": "Assets are value-density signals, not invoices.",
        }

    def _brand(self, name: str, zone: str) -> str:
        zone_tag = {
            "product_sol": "Sol",
            "cloud_sol": "Cloud",
            "infa_sol": "Infa",
            "structure_fi": "Fi",
            "market_units": "MU",
            "mega_map": "Map",
            "calm_point": "Calm",
            "orientation": "Orient",
        }.get(zone, "MX")
        short = "".join(w[:1].upper() for w in name.replace(":", " ").split()[:3])
        return f"MX-{zone_tag}-{short or 'A'}"

    # ── Stage 4 ──────────────────────────────────────────────────────────────

    def _stage4_interpret(
        self, s3: dict[str, Any], b: dict[str, Any]
    ) -> dict[str, Any]:
        """Link assets to context, energy, zones, previous patterns."""
        energy = b.get("energy_flow") or {}
        hyp_lib = b.get("hypothesis_library") or {}
        critical = b.get("critical_thinking") or {}
        plane = (b.get("function_engine") or {}).get("output_plane") or {}
        mega = (b.get("mega_map") or {}).get("comparison") or {}

        zone_links: dict[str, list[str]] = {}
        for a in s3.get("virtual_assets") or []:
            z = str(a.get("zone") or "unknown")
            zone_links.setdefault(z, []).append(str(a.get("branding") or a.get("id")))

        gp_raw = hyp_lib.get("group_patterns")
        if isinstance(gp_raw, list):
            patterns = gp_raw[:5]
        elif isinstance(gp_raw, dict):
            patterns = list(gp_raw.values())[:5]
        else:
            patterns = []
        disc_raw = critical.get("discrepancies") or []
        if not isinstance(disc_raw, list):
            disc_raw = []

        connections = {
            "energy_direction": energy.get("zone_balance_after")
            or energy.get("resolution_steps"),
            "top_lever": (b.get("function_engine") or {}).get("top_lever"),
            "root_alignment": mega.get("root_alignment_score"),
            "patterns": patterns,
            "discrepancy_types": [
                d.get("reason")
                for d in disc_raw[:6]
                if isinstance(d, dict)
            ],
            "zone_to_assets": zone_links,
            "paid_readiness": plane.get("paid_readiness"),
        }

        interpretation = (
            f"Assets sit across {len(zone_links)} zones. "
            f"Energy entanglement={safe_float(energy.get('total_entanglement')):.0%}; "
            f"top lever «{connections['top_lever'] or 'n/a'}»; "
            f"root alignment={connections['root_alignment']}. "
            f"Honesty layer flags {len(critical.get('discrepancies') or [])} discrepancies."
        )

        return {
            "stage": 4,
            "name": "Interpretation & Connection",
            "connections": connections,
            "interpretation": interpretation,
            "note": "Between-concepts links — not template copy.",
        }

    # ── Stage 5 ──────────────────────────────────────────────────────────────

    def _stage5_apply_learn(
        self, s4: dict[str, Any], b: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply property, generate trajectory feedback, feed Hypothesis Library."""
        traj = b.get("conceptual_trajectory") or {}
        hyp_lib = b.get("hypothesis_library") or {}
        package = b.get("package") or {}
        plane = (b.get("function_engine") or {}).get("output_plane") or {}

        application = {
            "recommended_path": list(package.get("recommended_actions") or [])[:5],
            "best_hypothesis": package.get("best_hypothesis")
            or (hyp_lib.get("picked") or [{}])[0].get("claim"),
            "paid_status": package.get("status") or b.get("status"),
            "trajectory_path": traj.get("path_summary")
            or "raw → hyp → map → deliverable",
        }

        # Learning feedback for Hypothesis Library (EMA-friendly)
        top_lever = str((b.get("function_engine") or {}).get("top_lever") or "clarity")
        outcome = clamp01(
            0.5 * safe_float(package.get("paid_score"), 0.5)
            + 0.5 * safe_float(plane.get("paid_readiness"), 0.5)
        )
        learning_feedback = {
            "lever_hint": top_lever,
            "outcome_score": round(outcome, 4),
            "pattern_sources": [
                (h.get("source") if isinstance(h, dict) else None)
                for h in (hyp_lib.get("picked") or [])[:4]
            ],
            "coords_uncertainty": traj.get("residual_uncertainty"),
            "interpretation_digest": (s4.get("interpretation") or "")[:200],
            "feeds_hypothesis_library": True,
            "next_open": traj.get("next_open_engine")
            or "ConceptualEngine.supply_chain_vision",
        }

        return {
            "stage": 5,
            "name": "Application + Learning Loop",
            "application": application,
            "learning_feedback": learning_feedback,
            "note": (
                "Feedback is soft learning signal for next iteration — "
                "not a claim of online training completeness."
            ),
        }

    # ── Narrative surface (human-facing) ─────────────────────────────────────

    def _narrative_from_stages(
        self, stages: dict[str, Any], paid_bundle: dict[str, Any]
    ) -> dict[str, Any]:
        sdl = paid_bundle.get("system_design_library") or {}
        chips = paid_bundle.get("virtual_chips") or {}
        fn = paid_bundle.get("function_engine") or {}
        energy = paid_bundle.get("energy_flow") or {}
        calm = paid_bundle.get("calm_point") or {}
        mega = paid_bundle.get("mega_map") or {}
        hyps = paid_bundle.get("hypotheses") or {}
        critical = paid_bundle.get("critical_thinking") or {}
        metric_tests = paid_bundle.get("metric_tests") or {}
        hyp_lib = paid_bundle.get("hypothesis_library") or {}
        package = paid_bundle.get("package") or {}
        traj = paid_bundle.get("conceptual_trajectory") or {}

        plane = fn.get("output_plane") or {}
        comparison = mega.get("comparison") or {}
        sections: list[dict[str, str]] = []

        s1 = stages.get("1_perception") or {}
        s2 = stages.get("2_notation") or {}
        s3 = stages.get("3_objectification") or {}
        s4 = stages.get("4_interpretation") or {}
        s5 = stages.get("5_application_learning") or {}

        sections.append(
            {
                "topic": "Reader Stage 1 — Perception",
                "text": (
                    f"Intake of {s1.get('count', 0)} live phenomena "
                    f"(no static DB). Root and energy/chip/map signals held as raw amplitude."
                ),
            }
        )
        sections.append(
            {
                "topic": "Reader Stage 2 — Notation",
                "text": (
                    f"Named {s2.get('count', 0)} units with boundaries. "
                    f"Modeling skeleton: entities={len((s2.get('modeling_skeleton') or {}).get('entities') or [])}, "
                    f"levers={len((s2.get('modeling_skeleton') or {}).get('levers') or [])}."
                ),
            }
        )
        sections.append(
            {
                "topic": "Reader Stage 3 — Virtual Assets",
                "text": (
                    f"Objectified {s3.get('asset_count', 0)} Virtual Assets "
                    f"(total weight={s3.get('total_weight', 0)}). "
                    f"Each carries weight · price_signal · owner · branding."
                ),
            }
        )
        sections.append(
            {
                "topic": "Reader Stage 4 — Interpretation",
                "text": str(s4.get("interpretation") or "n/a"),
            }
        )
        sections.append(
            {
                "topic": "Reader Stage 5 — Application & Learning",
                "text": (
                    f"Path «{(s5.get('application') or {}).get('trajectory_path', 'n/a')}». "
                    f"Learning feeds Hypothesis Library on lever "
                    f"«{(s5.get('learning_feedback') or {}).get('lever_hint')}» "
                    f"(outcome={(s5.get('learning_feedback') or {}).get('outcome_score')}). "
                    f"Next OPEN: {(s5.get('learning_feedback') or {}).get('next_open')}."
                ),
            }
        )

        # Core component narrations (honest commercial surface)
        sections.append(
            {
                "topic": "System Design Library",
                "text": (
                    f"For {sdl.get('industry_id', 'this direction')} / "
                    f"{sdl.get('category', 'full package')}, pattern «{sdl.get('pattern', 'n/a')}». "
                    f"Architecture layers: {len(sdl.get('base_architecture') or [])}; "
                    f"chip refs: {len(sdl.get('chip_refs') or [])}."
                ),
            }
        )
        sections.append(
            {
                "topic": "Virtual Chips",
                "text": (
                    f"Instantiated {chips.get('chip_count', 0)} chips + "
                    f"{chips.get('variant_count', 0)} variants. "
                    f"Terminal Agency={bool(chips.get('terminal_agency_ready'))}; "
                    f"multi-agent={bool(chips.get('multi_agent_scalable'))}. "
                    f"Virtual assets bridged: {len(chips.get('virtual_assets') or [])}."
                ),
            }
        )

        av = safe_float(plane.get("abstract_value"))
        pr = safe_float(plane.get("paid_readiness"))
        top = fn.get("top_lever") or "n/a"
        sections.append(
            {
                "topic": "Function Calculation Engine",
                "text": (
                    f"Abstract value {av:.2f} ({_level(clamp01(av / 2.5), 'weak', 'moderate', 'strong')}). "
                    f"Paid readiness {pr:.0%} — "
                    f"{_level(pr, 'early for close', 'borderline for pilot', 'ready for paid path')}. "
                    f"Strongest lever: «{top}»."
                ),
            }
        )
        te = safe_float(energy.get("total_entanglement"))
        sections.append(
            {
                "topic": "Energy Flow (Market Units)",
                "text": (
                    f"{energy.get('pair_count', 0)} entangled pairs; "
                    f"entanglement {te:.0%} ({_level(te, 'clean', 'some tangle', 'heavy tangle')}). "
                    f"Redistribution prepared for gradual resolution."
                ),
            }
        )
        sections.append(
            {
                "topic": "Calm-Point & Mega Map",
                "text": (
                    f"Calm form «{(calm.get('primary') or {}).get('form_archetype', 'n/a')}» "
                    f"(entropy={safe_float(calm.get('entropy')):.2f}). "
                    f"Best hypothesis «{comparison.get('best_label') or comparison.get('best_hypothesis_id') or 'n/a'}» "
                    f"dist={comparison.get('best_distance_to_root', 'n/a')}, "
                    f"uncertainty={comparison.get('mean_uncertainty', 'n/a')}."
                ),
            }
        )
        if critical:
            fe = critical.get("founder_error") or {}
            sections.append(
                {
                    "topic": "Critical Thinking (honesty)",
                    "text": (
                        f"Groups={critical.get('group_count', 0)}; "
                        f"discrepancies={len(critical.get('discrepancies') or [])}; "
                        f"founder_frame_error suspected={fe.get('suspected', False)} "
                        f"({fe.get('error_class', 'none')}). "
                        f"{fe.get('rationale') or critical.get('summary') or ''}"
                    ),
                }
            )
        if traj:
            sections.append(
                {
                    "topic": "Conceptual Trajectory",
                    "text": (
                        f"{traj.get('path_summary') or 'n/a'} | "
                        f"residual_uncertainty={traj.get('residual_uncertainty')}. "
                        f"Open final step: {traj.get('next_open_engine')}."
                    ),
                }
            )
        if package:
            sections.append(
                {
                    "topic": "Paid Showcase",
                    "text": (
                        f"status={package.get('status')}, score={package.get('paid_score')}, "
                        f"best={package.get('best_hypothesis')}."
                    ),
                }
            )

        narrative = " ".join(s["text"] for s in sections)
        bullets = self._action_bullets(plane, energy, comparison, chips, critical, s5)

        return {
            "sections": sections,
            "narrative": narrative,
            "action_bullets": bullets,
            "plain_summary": (
                f"Reader5: readiness={pr:.0%}, entanglement={te:.0%}, "
                f"assets={s3.get('asset_count', 0)}, "
                f"best={comparison.get('best_hypothesis_id')}, "
                f"chips={chips.get('chip_count', 0)}."
            ),
            "hypotheses_count": hyps.get("count"),
            "metric_tests_passed": (
                f"{metric_tests.get('passed_count')}/{metric_tests.get('total')}"
                if metric_tests
                else None
            ),
            "hypothesis_library_iteration": hyp_lib.get("iteration"),
        }

    def _action_bullets(
        self,
        plane: dict[str, float],
        energy: dict[str, Any],
        comparison: dict[str, Any],
        chips: dict[str, Any],
        critical: dict[str, Any] | None = None,
        s5: dict[str, Any] | None = None,
    ) -> list[str]:
        bullets: list[str] = []
        critical = critical or {}
        s5 = s5 or {}
        pr = safe_float(plane.get("paid_readiness"))
        fe = critical.get("founder_error") or {}
        if fe.get("suspected"):
            bullets.append(
                f"Founder-frame review: {fe.get('recommended_correction') or 're-frame package'}"
            )
        if pr >= 0.6 and not fe.get("suspected"):
            bullets.append("Proceed to pilot TZ / paid implement outline.")
        else:
            bullets.append("Raise paid readiness via top function lever before full close.")
        if safe_float(energy.get("total_entanglement")) >= 0.45:
            bullets.append("Another Market Units pass after specs closure.")
        if comparison.get("competing_pairs", 0):
            bullets.append("Resolve competing Mega Map hypotheses before quoting.")
        if chips.get("terminal_agency_ready"):
            bullets.append("Compose Terminal Agency overlay from Virtual Chips.")
        trust = (critical.get("resolved_variant") or {}).get("trust")
        if trust == "parallel":
            bullets.append("Prefer parallel orientation details over paid plane claims.")
        next_open = (s5.get("learning_feedback") or {}).get("next_open")
        if next_open:
            bullets.append(
                f"Reserve last planning step for {next_open} (supply-chain vision)."
            )
        if not bullets:
            bullets.append("Re-orient with more client detail and re-run paid core.")
        return bullets
