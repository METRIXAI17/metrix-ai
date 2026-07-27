"""
Mega Map Builder — core component 6 of the Paid Product.

Constructs the generated Mega Map. After running hypotheses it creates a map
with coordinate uncertainty and measures how much the coordinates differ.
This is the primary tool for comparing hypotheses against the root task.
"""

from __future__ import annotations

import math
from typing import Any

from backend.paid.types import MegaMapPoint, clamp01, safe_float


class MegaMapBuilder:
    """
    Places hypotheses in a 3D conceptual map relative to the root task,
    attaches uncertainty radii, and scores divergence from root.
    """

    name = "Mega Map Builder"

    def build(
        self,
        *,
        root_task: str,
        hypotheses: list[dict[str, Any]],
        params: dict[str, float] | None = None,
        output_plane: dict[str, float] | None = None,
        calm_point: dict[str, Any] | None = None,
        energy: dict[str, Any] | None = None,
        root_coords: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        params = {k: safe_float(v) for k, v in (params or {}).items()}
        output_plane = {k: safe_float(v) for k, v in (output_plane or {}).items()}
        calm_point = calm_point or {}
        energy = energy or {}

        # Root anchor: calm-point center or default origin of paid plane
        primary = calm_point.get("primary") or {}
        vs = primary.get("visual_spec") or {}
        center = vs.get("center") or {}
        rx = safe_float(center.get("x"), 0.5)
        ry = safe_float(center.get("y"), 0.5)
        if root_coords:
            rx = safe_float(root_coords.get("x"), rx)
            ry = safe_float(root_coords.get("y"), ry)
        rz = clamp01(
            0.5 * output_plane.get("paid_readiness", 0.5)
            + 0.5 * output_plane.get("risk_adjusted", 0.5)
        )
        root = MegaMapPoint(
            hypothesis_id="root_task",
            x=rx,
            y=ry,
            z=rz,
            uncertainty=clamp01(
                0.15
                + 0.4 * safe_float(params.get("coordinate_uncertainty"), 0.35)
                + 0.2 * safe_float(energy.get("total_entanglement"), 0.3)
            ),
            distance_to_root=0.0,
            label=(root_task or "Root task")[:80],
        )

        points: list[MegaMapPoint] = [root]
        for h in hypotheses:
            coords = h.get("coords") or {}
            conf = clamp01(safe_float(h.get("confidence"), 0.5))
            # Base coords from hypothesis; fallback to derived from claim hash-ish fields
            x = safe_float(coords.get("x"), 0.5)
            y = safe_float(coords.get("y"), 0.5)
            z = safe_float(coords.get("z"), conf)
            # Soft pull toward output plane axes
            x = clamp01(0.7 * x + 0.3 * output_plane.get("product_axis", x))
            y = clamp01(0.7 * y + 0.3 * output_plane.get("model_axis", y))
            z = clamp01(0.7 * z + 0.3 * output_plane.get("promo_axis", z))

            unc = clamp01(
                (1.0 - conf) * 0.55
                + 0.25 * safe_float(params.get("coordinate_uncertainty"), 0.35)
                + 0.2 * safe_float(params.get("discrepancy_pressure"), 0.3)
            )
            dist = math.sqrt((x - rx) ** 2 + (y - ry) ** 2 + (z - rz) ** 2)
            points.append(
                MegaMapPoint(
                    hypothesis_id=str(h.get("id") or "hyp"),
                    x=x,
                    y=y,
                    z=z,
                    uncertainty=unc,
                    distance_to_root=dist,
                    label=str(h.get("claim") or h.get("id") or "hypothesis")[:80],
                )
            )

        # Pairwise coordinate differences among hypotheses (exclude root)
        hyp_pts = [p for p in points if p.hypothesis_id != "root_task"]
        pairwise: list[dict[str, Any]] = []
        for i in range(len(hyp_pts)):
            for j in range(i + 1, len(hyp_pts)):
                a, b = hyp_pts[i], hyp_pts[j]
                d = math.sqrt(
                    (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2
                )
                overlap = max(
                    0.0,
                    (a.uncertainty + b.uncertainty) - d,
                )
                pairwise.append(
                    {
                        "a": a.hypothesis_id,
                        "b": b.hypothesis_id,
                        "coord_delta": round(d, 4),
                        "uncertainty_overlap": round(overlap, 4),
                        "competing": overlap > 0.05 and d < 0.35,
                    }
                )

        # Rank by closeness to root with uncertainty penalty
        ranked = sorted(
            hyp_pts,
            key=lambda p: p.distance_to_root + 0.5 * p.uncertainty,
        )
        best = ranked[0] if ranked else None
        mean_dist = (
            sum(p.distance_to_root for p in hyp_pts) / len(hyp_pts) if hyp_pts else 0.0
        )
        mean_unc = (
            sum(p.uncertainty for p in hyp_pts) / len(hyp_pts) if hyp_pts else 0.0
        )
        spread = 0.0
        if len(hyp_pts) >= 2:
            spread = sum(pw["coord_delta"] for pw in pairwise) / max(1, len(pairwise))

        comparison = {
            "best_hypothesis_id": best.hypothesis_id if best else None,
            "best_distance_to_root": round(best.distance_to_root, 4) if best else None,
            "best_label": best.label if best else None,
            "mean_distance_to_root": round(mean_dist, 4),
            "mean_uncertainty": round(mean_unc, 4),
            "hypothesis_spread": round(spread, 4),
            "root_alignment_score": round(
                clamp01(1.0 - mean_dist / math.sqrt(3.0)), 4
            ),
            "competing_pairs": sum(1 for pw in pairwise if pw["competing"]),
        }

        return {
            "module": self.name,
            "root": root.to_dict(),
            "points": [p.to_dict() for p in points],
            "hypothesis_count": len(hyp_pts),
            "pairwise_deltas": pairwise,
            "comparison": comparison,
            "map_bounds": {
                "x": [0.0, 1.0],
                "y": [0.0, 1.0],
                "z": [0.0, 1.0],
            },
            "summary": (
                f"Mega Map: {len(hyp_pts)} hypotheses, "
                f"best={comparison['best_hypothesis_id']}, "
                f"mean_dist={mean_dist:.3f}, spread={spread:.3f}, "
                f"alignment={comparison['root_alignment_score']:.2f}."
            ),
        }
