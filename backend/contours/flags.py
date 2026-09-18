"""Feature flags. C4/C5 never take down C1–C3."""

from __future__ import annotations

import os


def _on(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip() in {"1", "true", "TRUE", "yes", "on"}


def compute_broker_enabled() -> bool:
    return _on("ENABLE_COMPUTE_BROKER")


def cold_chain_enabled() -> bool:
    return _on("ENABLE_COLD_CHAIN")


def llm_assist_enabled() -> bool:
    return _on("ENABLE_LLM_ASSIST")


def snapshot() -> dict[str, bool]:
    return {
        "ENABLE_COMPUTE_BROKER": compute_broker_enabled(),
        "ENABLE_COLD_CHAIN": cold_chain_enabled(),
        "ENABLE_LLM_ASSIST": llm_assist_enabled(),
    }
