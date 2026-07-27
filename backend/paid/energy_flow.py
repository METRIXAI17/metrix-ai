"""
Energy Flow Disentangler (Market Units) — core component 4 of the Paid Product.

Sees interconnections as incorrect entanglement and correctly redistributes
energy flows. Used for situation analysis and gradual resolution.

Works with: amplitude · zones · energy direction.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import EnergyNode, clamp01, safe_float


class EnergyFlowDisentangler:
    """
    Market Units layer: build energy graph from chips / zones / scores,
    detect incorrect entanglement, redistribute amplitudes and directions.
    """

    name = "Energy Flow Disentangler (Market Units)"

    def __init__(
        self,
        entanglement_threshold: float = 0.45,
        redistribution_rate: float = 0.5,
        amplitude_cap: float = 0.9,
    ) -> None:
        self.entanglement_threshold = entanglement_threshold
        self.redistribution_rate = redistribution_rate
        self.amplitude_cap = amplitude_cap

    def _nodes_from_chips(self, chips: list[dict[str, Any]]) -> list[EnergyNode]:
        nodes: list[EnergyNode] = []
        for c in chips:
            cid = str(c.get("id") or c.get("template_id") or "chip")
            nodes.append(
                EnergyNode(
                    id=cid,
                    zone=str(c.get("zone") or "unknown"),
                    amplitude=clamp01(safe_float(c.get("amplitude"), 0.5)),
                    direction=max(
                        -1.0, min(1.0, safe_float(c.get("energy_direction"), 0.0))
                    ),
                )
            )
        return nodes

    def _nodes_from_zones(
        self,
        zone_influence: dict[str, float],
        scores: dict[str, float] | None = None,
    ) -> list[EnergyNode]:
        scores = scores or {}
        nodes: list[EnergyNode] = []
        for zone, amp in zone_influence.items():
            direction = 0.0
            if zone in ("product_sol", "cloud_sol", "market_units"):
                direction = 0.3 + 0.4 * safe_float(scores.get("promo_fit"), 0.5)
            elif zone in ("infa_sol",):
                direction = -0.2
            elif zone == "orientation":
                direction = 0.1
            nodes.append(
                EnergyNode(
                    id=f"zone::{zone}",
                    zone=zone,
                    amplitude=clamp01(safe_float(amp) / max(1.0, safe_float(amp) + 0.5)),
                    direction=max(-1.0, min(1.0, direction)),
                )
            )
        return nodes

    def detect_entanglement(self, nodes: list[EnergyNode]) -> list[EnergyNode]:
        """
        Incorrect entanglement: high co-amplitude + conflicting directions
        or same-zone overcrowding.
        """
        n = len(nodes)
        for i in range(n):
            entangled: list[str] = []
            score = 0.0
            for j in range(n):
                if i == j:
                    continue
                a, b = nodes[i], nodes[j]
                # Direction conflict under high joint amplitude
                dir_conflict = abs(a.direction - b.direction)
                joint = (a.amplitude + b.amplitude) / 2.0
                same_zone = 1.0 if a.zone == b.zone else 0.0
                e = joint * (0.55 * dir_conflict + 0.35 * same_zone + 0.1)
                if e >= self.entanglement_threshold:
                    entangled.append(b.id)
                    score = max(score, e)
            nodes[i].entangled_with = entangled
            nodes[i].entanglement_score = clamp01(score)
        return nodes

    def redistribute(self, nodes: list[EnergyNode]) -> list[EnergyNode]:
        """
        Gradual resolution: pull amplitude from over-entangled sinks/sources
        toward zone-mean balance; soften conflicting directions.
        """
        if not nodes:
            return nodes

        # Zone mean amplitudes
        zone_sum: dict[str, float] = {}
        zone_cnt: dict[str, int] = {}
        for n in nodes:
            zone_sum[n.zone] = zone_sum.get(n.zone, 0.0) + n.amplitude
            zone_cnt[n.zone] = zone_cnt.get(n.zone, 0) + 1
        zone_mean = {
            z: zone_sum[z] / max(1, zone_cnt[z]) for z in zone_sum
        }

        rate = self.redistribution_rate
        for n in nodes:
            mean = zone_mean.get(n.zone, n.amplitude)
            # Move amplitude toward mean when entangled
            pull = rate * n.entanglement_score * (mean - n.amplitude)
            new_amp = clamp01(n.amplitude + pull)
            new_amp = min(self.amplitude_cap, new_amp)

            # Soften direction toward local average of non-conflicting peers
            if n.entangled_with:
                peer_dirs = [
                    p.direction
                    for p in nodes
                    if p.id in n.entangled_with
                ]
                if peer_dirs:
                    avg_peer = sum(peer_dirs) / len(peer_dirs)
                    # If conflict is large, damp direction toward 0 then slightly to peers
                    conflict = abs(n.direction - avg_peer)
                    new_dir = n.direction * (1.0 - 0.4 * rate * conflict) + 0.15 * rate * avg_peer
                    new_dir = max(-1.0, min(1.0, new_dir))
                else:
                    new_dir = n.direction
            else:
                new_dir = n.direction

            n.corrected_amplitude = round(new_amp, 4)
            n.corrected_direction = round(new_dir, 4)
        return nodes

    def analyze(
        self,
        *,
        chips: list[dict[str, Any]] | None = None,
        zone_influence: dict[str, float] | None = None,
        scores: dict[str, float] | None = None,
        axes: dict[str, float] | None = None,
        chip_params: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Full Market Units pass: graph → entanglement → redistribution."""
        chips = chips or []
        zone_influence = zone_influence or {}
        scores = {k: safe_float(v) for k, v in (scores or {}).items()}
        axes = {k: safe_float(v) for k, v in (axes or {}).items()}
        chip_params = chip_params or {}

        # Override thresholds from energy chip if present
        thr = safe_float(
            chip_params.get("entanglement_threshold"), self.entanglement_threshold
        )
        rate = safe_float(
            chip_params.get("redistribution_rate"), self.redistribution_rate
        )
        cap = safe_float(chip_params.get("amplitude_cap"), self.amplitude_cap)
        self.entanglement_threshold = thr
        self.redistribution_rate = rate
        self.amplitude_cap = cap

        nodes = self._nodes_from_chips(chips)
        if zone_influence:
            nodes.extend(self._nodes_from_zones(zone_influence, scores))

        # Synthetic market-unit node from axes (situation analysis anchor)
        if axes:
            mu_amp = clamp01(
                0.4 * axes.get("monetization_fit", 0.5)
                + 0.3 * scores.get("promo_fit", 0.5)
                + 0.3 * (1.0 - axes.get("risk", 0.3))
            )
            nodes.append(
                EnergyNode(
                    id="market_unit::situation",
                    zone="market_units",
                    amplitude=mu_amp,
                    direction=max(
                        -1.0,
                        min(
                            1.0,
                            axes.get("monetization_fit", 0.5)
                            - axes.get("risk", 0.3),
                        ),
                    ),
                )
            )

        if not nodes:
            return {
                "module": self.name,
                "nodes": [],
                "entangled_pairs": [],
                "total_entanglement": 0.0,
                "redistributed": False,
                "zone_balance_before": {},
                "zone_balance_after": {},
                "resolution_steps": [],
                "summary": "No energy nodes to disentangle.",
            }

        nodes = self.detect_entanglement(nodes)
        before_balance = self._zone_balance(nodes, corrected=False)
        nodes = self.redistribute(nodes)
        after_balance = self._zone_balance(nodes, corrected=True)

        pairs: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for n in nodes:
            for other in n.entangled_with:
                key = tuple(sorted((n.id, other)))
                if key in seen:
                    continue
                seen.add(key)
                pairs.append(
                    {
                        "a": key[0],
                        "b": key[1],
                        "score": round(n.entanglement_score, 4),
                    }
                )

        total_e = (
            sum(n.entanglement_score for n in nodes) / max(1, len(nodes))
        )
        steps = self._resolution_steps(nodes, pairs, total_e)

        return {
            "module": self.name,
            "nodes": [n.to_dict() for n in nodes],
            "entangled_pairs": pairs,
            "pair_count": len(pairs),
            "total_entanglement": round(total_e, 4),
            "redistributed": True,
            "zone_balance_before": before_balance,
            "zone_balance_after": after_balance,
            "amplitude_mean": round(
                sum(n.amplitude for n in nodes) / len(nodes), 4
            ),
            "direction_mean": round(
                sum(n.direction for n in nodes) / len(nodes), 4
            ),
            "thresholds": {
                "entanglement_threshold": thr,
                "redistribution_rate": rate,
                "amplitude_cap": cap,
            },
            "resolution_steps": steps,
            "summary": (
                f"Market Units: nodes={len(nodes)}, entangled_pairs={len(pairs)}, "
                f"entanglement={total_e:.2f}, zones={list(after_balance.keys())}."
            ),
        }

    def _zone_balance(
        self, nodes: list[EnergyNode], *, corrected: bool
    ) -> dict[str, dict[str, float]]:
        acc: dict[str, list[float]] = {}
        dir_acc: dict[str, list[float]] = {}
        for n in nodes:
            amp = (
                n.corrected_amplitude
                if corrected and n.corrected_amplitude is not None
                else n.amplitude
            )
            d = (
                n.corrected_direction
                if corrected and n.corrected_direction is not None
                else n.direction
            )
            acc.setdefault(n.zone, []).append(float(amp))
            dir_acc.setdefault(n.zone, []).append(float(d))
        out: dict[str, dict[str, float]] = {}
        for z, amps in acc.items():
            out[z] = {
                "amplitude_mean": round(sum(amps) / len(amps), 4),
                "direction_mean": round(
                    sum(dir_acc[z]) / max(1, len(dir_acc[z])), 4
                ),
                "count": len(amps),
            }
        return out

    def _resolution_steps(
        self,
        nodes: list[EnergyNode],
        pairs: list[dict[str, Any]],
        total_e: float,
    ) -> list[dict[str, str]]:
        steps = [
            {
                "step": "1",
                "action": "Map amplitudes and energy directions per node/zone",
            },
            {
                "step": "2",
                "action": (
                    f"Detect incorrect entanglement "
                    f"({len(pairs)} pairs, score={total_e:.2f})"
                ),
            },
            {
                "step": "3",
                "action": "Redistribute amplitude toward zone means under entanglement",
            },
            {
                "step": "4",
                "action": "Soften conflicting energy directions for gradual resolution",
            },
        ]
        hot = [n for n in nodes if n.entanglement_score >= self.entanglement_threshold]
        if hot:
            steps.append(
                {
                    "step": "5",
                    "action": (
                        "Focus next analysis on: "
                        + ", ".join(n.id for n in hot[:4])
                    ),
                }
            )
        return steps
