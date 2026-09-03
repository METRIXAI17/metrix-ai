"""
Support System — receives metric firmware feeds, tracks failures, routes owners.

Cross-references (user: «дописать отсылку»):
  ref_3 → points 1–4 (param + certainty chain)
  ref_4 → points 5–7 (super-speed, super-program, compose metrics)
  pilot model → differential equation predetermined L
  Excel Deep Tech components + Branding&VA human-authorized row
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.lexicon import REFERENCE_MAP


class SupportSystem:
    """Failure tracking + ticket routing from metric firmware."""

    name = "Support System"

    def run(
        self,
        metric_firmware: dict[str, Any] | None = None,
        artefacts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        fw = metric_firmware or {}
        feed = fw.get("support_feed") or {}
        anomalies = list(fw.get("anomalies") or feed.get("anomalies") or [])

        tickets = []
        for i, a in enumerate(anomalies, 1):
            severity = a.get("level") or "info"
            owner = "hum_deep_tech_owner"
            if a.get("metric") in ("RCM",):
                owner = "hum_client_signer"
            if "brand" in str(a.get("msg", "")).lower():
                owner = "hum_branding_va"
            hook = None
            for art in artefacts or []:
                if art.get("chain_hooks"):
                    hook = {"artefact_id": art.get("id"), "sigil": art.get("sigil"), "hooks": art.get("chain_hooks")}
                    break
            tickets.append(
                {
                    "ticket_id": f"SUP-{i:03d}-{a.get('metric', 'GEN')}",
                    "metric": a.get("metric"),
                    "severity": severity,
                    "message": a.get("msg"),
                    "owner": owner,
                    "human_authorized_owner": True,
                    "status": "open",
                    "sla_hours": 4 if severity == "critical" else 24 if severity == "warn" else 72,
                    "refs": ["metric_firmware", "ref_4:point_7", "ops_rules.R5", "ops_rules.R7"],
                    "artefact": hook,
                }
            )

        health = "green"
        if any(t["severity"] == "critical" for t in tickets):
            health = "red"
        elif any(t["severity"] == "warn" for t in tickets):
            health = "yellow"

        return {
            "module": self.name,
            "how_it_works": {
                "ru": [
                    "1) Metric Firmware на каждом тике считает base + auto-composed метрики.",
                    "2) Аномалии (пороги ASM/CNS/SFI/PAP) попадают в support_feed.",
                    "3) Support System открывает тикеты с severity, owner, SLA.",
                    "4) Ops rule R5: metric_firmware.anomaly → open_support_ticket.",
                    "5) Human-authorized owners: deep tech, branding/VA, client signer.",
                    "6) Закрытие тикета требует либо retest assembly, либо certain_yes на связанном параметре.",
                    "7) Агрегированный health (green/yellow/red) уходит в pilot predictor residual watch.",
                ],
                "en": [
                    "1) Metric Firmware computes base + auto-composed metrics each tick.",
                    "2) Threshold breaches become support_feed anomalies.",
                    "3) Support opens tickets with severity, owner, SLA.",
                    "4) Ops rule R5 routes anomalies to tickets.",
                    "5) Human-authorized owners handle brand/tech/client acceptance.",
                    "6) Ticket close requires assembly retest or certain_yes on linked param.",
                    "7) Health color feeds pilot residual monitoring.",
                ],
            },
            "references": {
                **REFERENCE_MAP,
                "excel_deep_tech": "4 Бизнеса.xlsx · Deep Tech components",
                "excel_branding_va": "4 Бизнеса.xlsx · Branding&Virtual Assets",
                "x_profile": "@karimmetrix / KARIM METRIX (screenshot 190342)",
                "ops_rule": "R5_support_on_anomaly",
                "firmware": "circle_system.metric_firmware",
                "pilot_model": "pilot_predictor discrete logistic L=0.92",
            },
            "health": health,
            "open_tickets": tickets,
            "ticket_count": len(tickets),
            "values_snapshot": feed.get("values") or fw.get("values") or {},
        }
