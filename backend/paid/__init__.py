"""
Block 18 — Paid Product Core (Meta-Reality Engine commercial surface)

Core 6:
  1. System Design Library
  2. Virtual Chips (parametric hardware + Virtual Assets)
  3. Function Calculation Engine
  4. Energy Flow Disentangler (Market Units)
  5. Calm-Point Image Generator
  6. Mega Map Builder

Supporting:
  Hypothesis Modules · Hypothesis Library (smart navigator)
  Reader (5-Stage Learning Interpreter)
  Critical Thinking Layer · Metric Tests · Situation Metrics
  Must-Ask Loop · Conceptual Trajectory
  Blue Ocean Identifier bridge
  Conceptual Engine (OPEN final supply-chain vision step)

Flow: 16 steps in 8 stages + conceptual trajectory + Blue Ocean blocks
     + Final layer (21 principles · assembler · anti-down · NFT · harness · capital).
"""

from backend.paid.blue_ocean import BlueOceanBridge
from backend.paid.capital_efficiency import CapitalEfficiencyEngine
from backend.paid.commercial_layer import CommercialLayer
from backend.paid.conceptual_engine import ConceptualEngine
from backend.paid.final_layer import FinalProductLayer
from backend.paid.interfaces import (
    BLUE_OCEAN_BLOCKS,
    CONCEPTUAL_TRAJECTORY_STAGES,
    PAID_FLOW_STAGES,
    PAID_FLOW_STEPS,
)
from backend.paid.meaning_vectors import MeaningVectorStore, get_standard_paid_vectors
from backend.paid.must_ask import MustAskLoop
from backend.paid.orchestrator import PaidProductCore, flow_overview, paid_ready_payload
from backend.paid.principles_engine import PrinciplesEngine, get_principles_engine
from backend.paid.situation_metrics import SituationMetricsEngine
from backend.paid.system_design_library import SystemDesignLibrary, get_system_design_library
from backend.paid.trajectory import TrajectoryBuilder
from backend.paid.virtual_chips import VirtualChipLibrary, get_virtual_chip_library

__all__ = [
    "MeaningVectorStore",
    "get_standard_paid_vectors",
    "PaidProductCore",
    "paid_ready_payload",
    "flow_overview",
    "CommercialLayer",
    "FinalProductLayer",
    "CapitalEfficiencyEngine",
    "PrinciplesEngine",
    "get_principles_engine",
    "PAID_FLOW_STAGES",
    "PAID_FLOW_STEPS",
    "CONCEPTUAL_TRAJECTORY_STAGES",
    "BLUE_OCEAN_BLOCKS",
    "SystemDesignLibrary",
    "get_system_design_library",
    "VirtualChipLibrary",
    "get_virtual_chip_library",
    "BlueOceanBridge",
    "ConceptualEngine",
    "SituationMetricsEngine",
    "MustAskLoop",
    "TrajectoryBuilder",
]
