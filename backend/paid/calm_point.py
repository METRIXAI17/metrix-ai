"""
Calm-Point Image Generator — core component 5 of the Paid Product.

Generates images and conceptual forms born from a “calm point” using methods
inspired by modern physics. Starts from a low-entropy / low-noise state and
produces visual-conceptual images that later serve as assembly points.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any

from backend.paid.types import CalmPointImage, clamp01, safe_float

# Archetypes nucleated from calm points
_ARCHETYPES = (
    "radial_equilibrium",
    "phase_boundary",
    "standing_wave_lattice",
    "gradient_well",
    "interference_quiet",
    "topology_fold",
)

_PALETTES = {
    "ai-agencies": ["#5eead4", "#134e4a", "#99f6e4", "#0f172a"],
    "cloud-economy": ["#7dd3fc", "#0c4a6e", "#e0f2fe", "#0f172a"],
    "cost-engineering": ["#fbbf24", "#78350f", "#fef3c7", "#0f172a"],
    "chipmaking": ["#c4b5fd", "#4c1d95", "#ede9fe", "#0f172a"],
    "telecom": ["#86efac", "#14532d", "#dcfce7", "#0f172a"],
    "device-assembly": ["#fda4af", "#881337", "#ffe4e6", "#0f172a"],
}


def _hash_vec(seed: str, n: int = 8) -> list[float]:
    out: list[float] = []
    block = seed.encode("utf-8")
    for i in range(n):
        h = hashlib.sha256(block + bytes([i])).digest()
        # Map first 4 bytes to [0,1)
        val = int.from_bytes(h[:4], "big") / 0xFFFFFFFF
        out.append(val)
    return out


def _entropy_from_params(params: dict[str, float], energy: dict[str, Any] | None) -> float:
    """Low entropy when clarity high and entanglement/noise low."""
    clarity = safe_float(params.get("clarity", params.get("value_density")), 0.5)
    complexity = safe_float(params.get("complexity"), 0.45)
    ent = safe_float(params.get("entanglement"), 0.4)
    if energy:
        ent = 0.5 * ent + 0.5 * safe_float(energy.get("total_entanglement"), ent)
    risk = safe_float(params.get("risk"), 0.35)
    # Shannon-ish proxy on a 4-bin mix
    parts = [
        max(1e-6, clarity),
        max(1e-6, 1 - complexity),
        max(1e-6, 1 - ent),
        max(1e-6, 1 - risk),
    ]
    s = sum(parts)
    probs = [p / s for p in parts]
    h = -sum(p * math.log(p + 1e-12) for p in probs) / math.log(4)
    return clamp01(h)


class CalmPointImageGenerator:
    """
    Physics-inspired conceptual image generator.

    Does not call external image APIs by default — produces a deterministic
    visual_spec (assembly blueprint) that frontends / generative block 19
    can render. Optional hook leaves room for real raster generation later.
    """

    name = "Calm-Point Image Generator"

    def generate(
        self,
        *,
        industry_id: str,
        request_id: str = "",
        idea_title: str = "",
        params: dict[str, float] | None = None,
        energy: dict[str, Any] | None = None,
        embedding: dict[str, Any] | None = None,
        reverse_influence: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        params = {k: safe_float(v) for k, v in (params or {}).items()}
        energy = energy or {}
        embedding = embedding or {}
        reverse_influence = reverse_influence or {}

        # Calm point: drive entropy/noise down via calm_seed influence
        base_entropy = _entropy_from_params(params, energy)
        calm_boost = abs(safe_float(reverse_influence.get("entropy"), 0.0))
        seed_coh = safe_float(params.get("seed_coherence"), 0.65)
        entropy = clamp01(base_entropy * (1.0 - 0.35 * seed_coh) - calm_boost)
        noise = clamp01(
            0.55 * entropy
            + 0.25 * safe_float(params.get("entanglement"), 0.4)
            + 0.2 * safe_float(energy.get("total_entanglement"), 0.3)
            - safe_float(params.get("noise_floor"), 0.0)
        )

        seed_key = f"{industry_id}:{request_id}:{idea_title}:{entropy:.3f}"
        seed_vector = _hash_vec(seed_key, 8)
        # Blend with OAE embedding dims if present
        emb_vals = embedding.get("values") or embedding.get("vector") or []
        if isinstance(emb_vals, dict):
            emb_vals = list(emb_vals.values())
        if emb_vals:
            for i, v in enumerate(emb_vals[:8]):
                seed_vector[i] = clamp01(0.55 * seed_vector[i] + 0.45 * safe_float(v))

        arch_idx = int(seed_vector[0] * len(_ARCHETYPES)) % len(_ARCHETYPES)
        archetype = _ARCHETYPES[arch_idx]
        palette = list(_PALETTES.get(industry_id, _PALETTES["ai-agencies"]))

        # Physics method labels (conceptual, transparent)
        if entropy < 0.25:
            method = "ground_state_nucleation"
        elif noise < 0.35:
            method = "adiabatic_cooling_to_form"
        elif safe_float(energy.get("total_entanglement"), 0.5) > 0.5:
            method = "decoherence_then_rephase"
        else:
            method = "standing_wave_interference_minimum"

        # Radial / lattice geometry from seed
        cx, cy = seed_vector[1], seed_vector[2]
        radius = 0.15 + 0.35 * (1.0 - entropy)
        harmonics = 2 + int(seed_vector[3] * 5)
        nodes = 4 + int(seed_vector[4] * 8)

        title_bit = (idea_title or "Metrix form")[:48]
        image = CalmPointImage(
            id=f"cpi_{hashlib.sha256(seed_key.encode()).hexdigest()[:12]}",
            title=f"Calm Point · {title_bit}",
            entropy=entropy,
            noise=noise,
            seed_vector=seed_vector,
            form_archetype=archetype,
            visual_spec={
                "kind": "conceptual_svg_blueprint",
                "width": 1024,
                "height": 1024,
                "background": palette[-1],
                "palette": palette,
                "center": {"x": round(cx, 4), "y": round(cy, 4)},
                "radius": round(radius, 4),
                "harmonics": harmonics,
                "lattice_nodes": nodes,
                "stroke_weight": round(1.0 + 2.0 * (1.0 - noise), 3),
                "glow": round(0.2 + 0.6 * (1.0 - entropy), 3),
                "layers": [
                    {"name": "calm_core", "opacity": round(1.0 - noise, 3)},
                    {"name": "phase_rings", "count": harmonics},
                    {"name": "assembly_anchors", "count": min(8, nodes)},
                    {
                        "name": "zone_tint",
                        "zones": ["orientation", "product_sol", "market_units"],
                    },
                ],
                "render_hint": (
                    "Start from quiet center; grow rings only where noise < threshold; "
                    "use anchors as later Mega Map assembly points."
                ),
            },
            assembly_role="primary_assembly_point",
            physics_method=method,
            notes=(
                "Low-entropy seed for conceptual form; serves as assembly point "
                "for hypotheses and mega-map root alignment."
            ),
        )

        # Secondary forms (assembly field) when calm enough
        field: list[dict[str, Any]] = [image.to_dict()]
        if entropy < 0.45:
            for k in range(2):
                sv = _hash_vec(f"{seed_key}:sat{k}", 8)
                a2 = _ARCHETYPES[int(sv[0] * len(_ARCHETYPES)) % len(_ARCHETYPES)]
                field.append(
                    CalmPointImage(
                        id=f"{image.id}_s{k}",
                        title=f"Satellite form {k + 1} · {a2}",
                        entropy=clamp01(entropy + 0.08 * (k + 1)),
                        noise=clamp01(noise + 0.05 * (k + 1)),
                        seed_vector=sv,
                        form_archetype=a2,
                        visual_spec={
                            "kind": "satellite_anchor",
                            "parent": image.id,
                            "offset": {
                                "x": round(sv[1] - 0.5, 4),
                                "y": round(sv[2] - 0.5, 4),
                            },
                            "palette": palette,
                        },
                        assembly_role="secondary_assembly_point",
                        physics_method=method,
                        notes="Satellite calm form for multi-hypothesis assembly.",
                    ).to_dict()
                )

        return {
            "module": self.name,
            "primary": image.to_dict(),
            "field": field,
            "field_size": len(field),
            "entropy": round(entropy, 4),
            "noise": round(noise, 4),
            "physics_method": method,
            "assembly_points": [
                {"id": f["id"], "role": f["assembly_role"], "archetype": f["form_archetype"]}
                for f in field
            ],
            "renderable": True,
            "external_raster": False,
            "summary": (
                f"Calm point entropy={entropy:.2f}, noise={noise:.2f}, "
                f"archetype={archetype}, method={method}, field={len(field)}."
            ),
        }
