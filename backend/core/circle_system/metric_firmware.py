"""
Metric firmware — recognizes and auto-composes new metrics; feeds Support System.
"""

from __future__ import annotations

from typing import Any

from backend.paid.types import clamp01


BASE_METRICS = (
    {"id": "VVI", "name": "Vulnerability Void Index", "family": "core"},
    {"id": "ER", "name": "Efficiency of Error", "family": "core"},
    {"id": "RRC", "name": "Reverse Refragmentation Coefficient", "family": "core"},
    {"id": "ASM", "name": "Assembly Score", "family": "circle"},
    {"id": "CNS", "name": "Consistency Score", "family": "circle"},
    {"id": "CYS", "name": "Certain-Yes Ratio", "family": "circle"},
    {"id": "PAP", "name": "Pilot Accuracy Predicted", "family": "pilot"},
    {"id": "RCM", "name": "Resource Compatibility", "family": "resources"},
)


class MetricFirmware:
    """Discover, compose, and stream metrics to support."""

    name = "Metric Firmware"

    def run(
        self,
        *,
        assembly: dict[str, Any] | None = None,
        layers_result: dict[str, Any] | None = None,
        certainty_result: dict[str, Any] | None = None,
        pilot_pred: dict[str, Any] | None = None,
        resource_match: dict[str, Any] | None = None,
        core_metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        assembly = assembly or {}
        layers_result = layers_result or {}
        certainty_result = certainty_result or {}
        pilot_pred = pilot_pred or {}
        resource_match = resource_match or {}
        core = core_metrics or {}

        counts = certainty_result.get("counts") or {}
        n = max(1, sum(int(counts.get(k, 0)) for k in ("certain_yes", "certain_no", "uncertain")))
        cys = int(counts.get("certain_yes") or 0) / n

        values = {
            "VVI": float(core.get("vvi") or (1 - float(assembly.get("assembly_score") or 0.4))),
            "ER": float(core.get("er") or 0.55),
            "RRC": float(core.get("rrc") or 0.5),
            "ASM": float(assembly.get("assembly_score") or 0.4),
            "CNS": float(layers_result.get("consistency_score") or 0.5),
            "CYS": cys,
            "PAP": float(pilot_pred.get("predicted_end") or pilot_pred.get("y0") or 0.5),
            "RCM": float(resource_match.get("compatibility_score") or 0.4),
        }

        # Auto-compose new metrics from base
        composed_new = [
            {
                "id": "CIR",
                "name": "Circle Integrity",
                "formula": "0.4*ASM + 0.35*CNS + 0.25*CYS",
                "value": round(
                    clamp01(0.4 * values["ASM"] + 0.35 * values["CNS"] + 0.25 * values["CYS"]), 4
                ),
            },
            {
                "id": "PIR",
                "name": "Pilot Integrity Ratio",
                "formula": "0.5*PAP + 0.3*ASM + 0.2*RCM",
                "value": round(
                    clamp01(0.5 * values["PAP"] + 0.3 * values["ASM"] + 0.2 * values["RCM"]), 4
                ),
            },
            {
                "id": "SFI",
                "name": "Support Failure Index",
                "formula": "0.5*(1-CIR) + 0.3*VVI + 0.2*(1-ER)",
                "value": None,  # filled below
            },
        ]
        cir = composed_new[0]["value"]
        composed_new[2]["value"] = round(
            clamp01(0.5 * (1 - cir) + 0.3 * values["VVI"] + 0.2 * (1 - values["ER"])), 4
        )

        # Anomaly detection thresholds
        anomalies = []
        if values["ASM"] < 0.35:
            anomalies.append({"metric": "ASM", "level": "warn", "msg": "Assembly below pilot gate"})
        if values["CNS"] < 0.5:
            anomalies.append({"metric": "CNS", "level": "warn", "msg": "Layer consistency weak"})
        if composed_new[2]["value"] >= 0.55:
            anomalies.append({"metric": "SFI", "level": "critical", "msg": "Support failure risk high"})
        if values["PAP"] < 0.55:
            anomalies.append({"metric": "PAP", "level": "warn", "msg": "Pilot accuracy forecast low"})

        support_payload = {
            "source": "metric_firmware",
            "values": {**values, **{m["id"]: m["value"] for m in composed_new}},
            "anomalies": anomalies,
            "tick": "runtime",
        }

        return {
            "module": self.name,
            "base_metrics": list(BASE_METRICS),
            "values": {k: round(v, 4) for k, v in values.items()},
            "auto_composed": composed_new,
            "anomalies": anomalies,
            "support_feed": support_payload,
            "rule": "Firmware recognizes base metrics, composes new ones, streams anomalies to Support.",
        }
