"""
wayD — Terminal Data Metrics Model (concierge analytical spine).

Labels are first-class system edges. Unique functions emerge when modules
compose along labeled edges (direction × segment × path × metric).
"""

from backend.core.wayd.labels import Label, LabelBus, stamp_labels
from backend.core.wayd.terminal_metrics import TerminalMetrics, compute_terminal
from backend.core.wayd.edges import SystemEdge, EdgeMesh, compose_edges, unique_functions

__all__ = [
    "Label",
    "LabelBus",
    "stamp_labels",
    "TerminalMetrics",
    "compute_terminal",
    "SystemEdge",
    "EdgeMesh",
    "compose_edges",
    "unique_functions",
]
