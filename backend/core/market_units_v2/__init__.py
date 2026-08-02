"""
Market Units v2 — operational coordination core.

Layers (recursive reinforcement of the OAS kernel):
  1. SystemReader        — intake + semantic graph of client state
  2. ProblemRecognition  — ranked problem lattice with failure modes
  3. MetricComposer      — VVI/ER/RRC + business levers → product quality index
  4. CoordinationLayer   — multi-node coordination scores & handoff matrix
  5. OntologyEngine      — ontological combinations → task algorithms
  6. TeammateNetwork     — terminal teammate mesh (roles, links, load)
  7. MarketUnitsEngine   — full orchestrator + recursive core boost forecast

If something goes wrong: degrade gracefully to static unit catalog,
never block the main request pipeline.
"""

from __future__ import annotations

from .engine import MarketUnitsEngine, run_market_units_v2

__all__ = [
    "MarketUnitsEngine",
    "run_market_units_v2",
]
