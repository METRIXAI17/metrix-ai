"""
Multi-layer Knowledge Synthesis — Metrix AI expert platform.

Layers:
  L0 Lexicon / domain frames
  L1 Analogy bridge
  L2 Matrix simplification (compress → check → expand)
  L3 Side computation engines (numeric / graph / risk)
  L4 Human-light planner (recognize · branch · commit)
  L5 Synthesis methods beyond analogy (constraint, contrast, morph, narrative, counterfactual)
  L6 Uncertainty + self-test + human-reaction forecast
"""

from backend.core.knowledge_synthesis.synthesis_core import (
    KnowledgeSynthesisEngine,
    run_knowledge_synthesis,
)
from backend.core.knowledge_synthesis.planner import HumanLightPlanner
from backend.core.knowledge_synthesis.expert_base import ExpertBaseBuilder

__all__ = [
    "KnowledgeSynthesisEngine",
    "run_knowledge_synthesis",
    "HumanLightPlanner",
    "ExpertBaseBuilder",
]
