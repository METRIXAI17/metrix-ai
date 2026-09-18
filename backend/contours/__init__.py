"""Five product contours + Heavy Launch assembly.

C1 Partner automation · C2 Eval + Flight Recorder · C3 On-prem
C4 Compute broker (flag) · C5 Cold chain (flag)
"""

from __future__ import annotations

CONTOUR_MAP = {
    "C1": {
        "id": "C1",
        "name": "Partner automation",
        "sku": "process_rails",
        "modules": ["process_os", "partner_crm", "monday_report"],
        "gtm": True,
    },
    "C2": {
        "id": "C2",
        "name": "R&D / Metrix IP",
        "sku": "eval_flight_recorder",
        "modules": ["eval_protocol", "orientation", "flight_recorder"],
        "gtm": True,
    },
    "C3": {
        "id": "C3",
        "name": "Enterprise on-prem AI",
        "sku": "onprem_pipeline",
        "modules": ["airgap", "rag", "ha", "guardrails"],
        "gtm": True,
    },
    "C4": {
        "id": "C4",
        "name": "Systemic arbitrage",
        "sku": "compute_broker",
        "modules": ["spot_scanner", "chat_proxy", "spread_ledger"],
        "flag": "ENABLE_COMPUTE_BROKER",
    },
    "C5": {
        "id": "C5",
        "name": "Industrial / cold chain",
        "sku": "cold_chain",
        "modules": ["telemetry", "proof_of_condition", "device_registry"],
        "flag": "ENABLE_COLD_CHAIN",
    },
}

NAV_DEFAULT = ("C1", "C2", "C3")
