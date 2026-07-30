"""
Integration library — technical adapters + human-authorized entries.
"""

from __future__ import annotations

from typing import Any


TECH_INTEGRATIONS = (
    {
        "id": "int_http_webhook",
        "kind": "technical",
        "name": "HTTP Webhook ingress",
        "auth": "hmac_or_bearer",
        "use": "metric_firmware + support events",
    },
    {
        "id": "int_rest_api",
        "kind": "technical",
        "name": "Metrix REST process API",
        "auth": "api_key",
        "use": "consult / tech_write / pilot triggers",
    },
    {
        "id": "int_ledger_csv",
        "kind": "technical",
        "name": "Ledger CSV/JSON sink",
        "auth": "file_or_s3",
        "use": "resource + collab project merge",
    },
    {
        "id": "int_x_channel",
        "kind": "technical",
        "name": "X/Twitter public surface",
        "auth": "public",
        "use": "branding signals @karimmetrix",
    },
    {
        "id": "int_pilot_portals",
        "kind": "technical",
        "name": "Pilot client/executor portals",
        "auth": "session",
        "use": "tech write delivery + pilot board",
    },
)

HUMAN_AUTHORIZED = (
    {
        "id": "hum_branding_va",
        "kind": "human_authorized",
        "role": "Branding & Virtual Assets",
        "handle": "@andrewsmm1",
        "authority": "naming, VA objects, phenomenon→notation→object chain",
        "excel_row": "Branding&Virtual Assets",
    },
    {
        "id": "hum_deep_tech_owner",
        "kind": "human_authorized",
        "role": "Deep Tech / Metrix architecture",
        "handle": "@karimmetrix",
        "authority": "circle-system, tech write, pilot gate, main package",
        "excel_row": "Deep Tech",
    },
    {
        "id": "hum_client_signer",
        "kind": "human_authorized",
        "role": "Client acceptance signer",
        "handle": "client_designee",
        "authority": "accept pilot criteria, certain_yes/no on tests",
        "excel_row": None,
    },
)


class IntegrationLibrary:
    name = "Integration Library (tech + human-authorized)"

    def catalog(self) -> dict[str, Any]:
        return {
            "module": self.name,
            "technical": list(TECH_INTEGRATIONS),
            "human_authorized": list(HUMAN_AUTHORIZED),
            "count": len(TECH_INTEGRATIONS) + len(HUMAN_AUTHORIZED),
        }

    def match_for_plan(self, orchestration: dict[str, Any] | None = None) -> dict[str, Any]:
        cat = self.catalog()
        needed = [
            "int_rest_api",
            "int_pilot_portals",
            "int_http_webhook",
            "hum_deep_tech_owner",
            "hum_client_signer",
        ]
        # branding always if identity layer may appear
        needed.append("hum_branding_va")
        selected = []
        for item in cat["technical"] + cat["human_authorized"]:
            if item["id"] in needed:
                selected.append(item)
        return {
            **cat,
            "selected_for_run": selected,
            "orchestration_days": (orchestration or {}).get("total_calendar_days_estimate"),
        }
