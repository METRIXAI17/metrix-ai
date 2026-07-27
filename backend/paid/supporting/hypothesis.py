"""
Hypothesis Modules — supporting module for the Paid Product.

Small modules selected from data of previous-version conclusions
(decision core, OAE, product result, fin models, system log).
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.paid.types import HypothesisModule, clamp01, safe_float


def _coord_from_text(text: str, salt: str) -> dict[str, float]:
    h = hashlib.sha256(f"{salt}:{text}".encode("utf-8")).hexdigest()
    return {
        "x": int(h[0:8], 16) / 0xFFFFFFFF,
        "y": int(h[8:16], 16) / 0xFFFFFFFF,
        "z": int(h[16:24], 16) / 0xFFFFFFFF,
    }


class HypothesisModuleSelector:
    """Select and package compact hypotheses from prior pipeline conclusions."""

    name = "Hypothesis Modules"

    def select(
        self,
        *,
        root_task: str,
        decision: dict[str, Any] | None = None,
        oae: dict[str, Any] | None = None,
        product: dict[str, Any] | None = None,
        fin_models: list[dict[str, Any]] | None = None,
        success: dict[str, Any] | None = None,
        energy: dict[str, Any] | None = None,
        function_plane: dict[str, float] | None = None,
        max_hypotheses: int = 6,
    ) -> dict[str, Any]:
        decision = decision or {}
        oae = oae or {}
        product = product or {}
        fin_models = fin_models or []
        success = success or {}
        energy = energy or {}
        function_plane = function_plane or {}

        raw: list[HypothesisModule] = []

        # 1. Decision improving decisions
        for i, d in enumerate((decision.get("improving_decisions") or [])[:3]):
            claim = str(d.get("title") or d.get("rationale") or "decision")
            conf = clamp01(0.55 + 0.1 * (3 - int(d.get("priority") or 2)))
            raw.append(
                HypothesisModule(
                    id=f"hyp_decision_{i}",
                    claim=claim,
                    source="decision_core",
                    confidence=conf,
                    coords=_coord_from_text(claim, f"dec{i}"),
                    supporting_indicators=[
                        f"mode:{decision.get('active_mode')}",
                        f"awareness:{decision.get('awareness_score')}",
                    ],
                )
            )

        # 2. OAE abstract coordinates / demo ideas
        for i, ac in enumerate((oae.get("abstract_coordinates") or [])[:3]):
            if isinstance(ac, dict):
                label = str(
                    ac.get("label")
                    or ac.get("title")
                    or ac.get("solution")
                    or f"abstract_{i}"
                )
                conf = clamp01(safe_float(ac.get("energy"), 0.55))
            else:
                label = str(ac)
                conf = 0.5
            raw.append(
                HypothesisModule(
                    id=f"hyp_oae_abs_{i}",
                    claim=label,
                    source="oae.abstract_coordinates",
                    confidence=conf,
                    coords=_coord_from_text(label, f"oae{i}"),
                    supporting_indicators=["double_bottom", "abstract_coordinate"],
                )
            )

        for i, di in enumerate((oae.get("demo_ideas") or [])[:2]):
            if isinstance(di, dict):
                title = str(di.get("title") or di.get("label") or f"demo_{i}")
            else:
                title = str(di)
            raw.append(
                HypothesisModule(
                    id=f"hyp_demo_{i}",
                    claim=title,
                    source="oae.demo_ideas",
                    confidence=0.58,
                    coords=_coord_from_text(title, f"demo{i}"),
                    supporting_indicators=["demo_surface"],
                )
            )

        # 3. Product / idea spine
        demo = product.get("demo_idea") or {}
        if isinstance(demo, dict) and demo.get("title"):
            raw.append(
                HypothesisModule(
                    id="hyp_product_spine",
                    claim=str(demo["title"]),
                    source="product_sol",
                    confidence=clamp01(
                        0.5
                        + 0.3 * safe_float(function_plane.get("product_axis"), 0.5)
                    ),
                    coords={
                        "x": safe_float(function_plane.get("product_axis"), 0.55),
                        "y": safe_float(function_plane.get("model_axis"), 0.5),
                        "z": safe_float(function_plane.get("promo_axis"), 0.45),
                    },
                    supporting_indicators=["product_spine", "seed"],
                )
            )

        # 4. Fin model insights
        for i, fm in enumerate(fin_models[:2]):
            name = str(fm.get("model_name") or fm.get("model_id") or f"fm_{i}")
            calcs = fm.get("calculations") or {}
            insights = calcs.get("insights") or fm.get("insights") or []
            claim = (
                str(insights[0])
                if insights
                else f"{name} as leverage layer"
            )
            raw.append(
                HypothesisModule(
                    id=f"hyp_fm_{i}",
                    claim=claim[:160],
                    source=f"fin_model:{fm.get('model_id', name)}",
                    confidence=clamp01(
                        0.4 + 0.2 * safe_float(calcs.get("impact"), 0.5)
                    ),
                    coords=_coord_from_text(claim, f"fm{i}"),
                    supporting_indicators=["fin_model", name],
                )
            )

        # 5. Success / energy derived hypothesis
        sc = success.get("card") or success.get("score_card") or success
        if isinstance(sc, dict) and sc.get("weighted_composite") is not None:
            comp = safe_float(sc.get("weighted_composite"), 0.5)
            raw.append(
                HypothesisModule(
                    id="hyp_success_tz",
                    claim=(
                        f"Success TZ composite {comp:.2f} supports paid path"
                        if comp >= 0.5
                        else f"Success TZ composite {comp:.2f} needs refinement"
                    ),
                    source="success_metrics",
                    confidence=clamp01(comp),
                    coords={
                        "x": comp,
                        "y": safe_float(function_plane.get("paid_readiness"), 0.5),
                        "z": 1.0 - safe_float(energy.get("total_entanglement"), 0.4),
                    },
                    supporting_indicators=["success_composite"],
                )
            )

        # Deduplicate by claim prefix, rank by confidence
        seen: set[str] = set()
        unique: list[HypothesisModule] = []
        for h in sorted(raw, key=lambda x: x.confidence, reverse=True):
            key = h.claim[:48].lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(h)

        selected = unique[:max_hypotheses]

        # Mark tensions: high coordinate proximity with different sources
        for i, a in enumerate(selected):
            for b in selected[i + 1 :]:
                dx = a.coords["x"] - b.coords["x"]
                dy = a.coords["y"] - b.coords["y"]
                dz = a.coords["z"] - b.coords["z"]
                dist = (dx * dx + dy * dy + dz * dz) ** 0.5
                if dist < 0.25 and a.source != b.source:
                    a.tension_with.append(b.id)
                    b.tension_with.append(a.id)

        return {
            "module": self.name,
            "root_task": root_task,
            "hypotheses": [h.to_dict() for h in selected],
            "count": len(selected),
            "sources_used": sorted({h.source for h in selected}),
            "summary": (
                f"Selected {len(selected)} hypothesis modules from "
                f"{len(raw)} candidates; sources={sorted({h.source for h in selected})}."
            ),
        }
