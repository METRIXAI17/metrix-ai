"""
Standard integration specifications for paid TZ.

Pre-recorded rules applied when clarifying answers / industry imply integrations.
OPEN: client-specific OpenAPI still filled at implement stage.
"""

from __future__ import annotations

from typing import Any


# Catalog of standard specs (MTMF-friendly)
STANDARD_SPECS: dict[str, dict[str, Any]] = {
    "billing_api": {
        "id": "std_billing_api",
        "title": "Billing & usage metering API",
        "category": "integration",
        "requirements": [
            "Usage events: resource_id, unit, quantity, ts, tenant_id",
            "Idempotent invoice lines",
            "Webhook: invoice.paid | invoice.failed",
            "Timezone UTC; money in minor units",
        ],
        "acceptance": [
            "Double-submit of same event does not double-charge",
            "Usage visible on FinOps board within 15 min",
        ],
        "security": ["API key or mTLS", "tenant isolation"],
    },
    "auth_sso": {
        "id": "std_auth_sso",
        "title": "Auth / SSO baseline",
        "category": "integration",
        "requirements": [
            "OIDC or API tokens with scoped roles",
            "Roles: owner, operator, developer, billing_viewer",
            "Session TTL + refresh policy",
        ],
        "acceptance": ["Role cannot read other tenant usage"],
        "security": ["JWT aud/iss validated", "no shared admin passwords"],
    },
    "gpu_orchestrator": {
        "id": "std_gpu_orch",
        "title": "GPU / workload orchestrator hooks",
        "category": "integration",
        "requirements": [
            "Queue job → allocate → meter → release",
            "Reserved vs on-demand pools mapped to margin bands",
            "Preemption policy documented",
        ],
        "acceptance": [
            "Utilization metric matches billing units",
            "Failed jobs do not bill full reserved window without policy",
        ],
        "security": ["namespace isolation", "secret injection not in logs"],
    },
    "crm_webhook": {
        "id": "std_crm_webhook",
        "title": "CRM / Telegram / outbound webhooks",
        "category": "integration",
        "requirements": [
            "Events: lead.created, pilot.started, invoice.paid",
            "Retry with exponential backoff",
            "Signed payload (HMAC)",
        ],
        "acceptance": ["Promo sequence can start from pilot.started"],
        "security": ["HMAC secret rotation"],
    },
    "finops_board": {
        "id": "std_finops_board",
        "title": "FinOps signal board (decision owners)",
        "category": "product_standard",
        "requirements": [
            "Signals: utilization, margin band, churn risk, rework rate",
            "Each signal has owner role + threshold + action",
            "Daily snapshot + weekly review hook",
        ],
        "acceptance": [
            "Top leak from situation analysis has a named owner",
            "Lever change logs who/when/why",
        ],
        "security": ["PII minimized on board"],
    },
    "margin_bands": {
        "id": "std_margin_bands",
        "title": "Workload margin bands (reserved / on-demand / edge)",
        "category": "product_standard",
        "requirements": [
            "Three price/cost bands minimum",
            "Auto-suggest band from utilization forecast",
            "Client-visible vs internal margin (two layers)",
        ],
        "acceptance": ["Band switch updates quote within one billing cycle"],
        "security": ["Internal margin not exposed to client portal by default"],
    },
    "pilot_14d": {
        "id": "std_pilot_14d",
        "title": "14–30 day paid pilot scaffold",
        "category": "delivery_standard",
        "requirements": [
            "Scope one-pager: outcome, metric, price, out-of-scope",
            "Kickoff checklist + mid-pilot checkpoint",
            "Exit: convert / extend / stop with reason codes",
        ],
        "acceptance": ["Success metric defined before day 1"],
        "security": ["Data retention after stop agreed"],
    },
    "orientation_paid_unit": {
        "id": "std_orientation_unit",
        "title": "Orientation as billable unit",
        "category": "commercial_standard",
        "requirements": [
            "Deliverables: axes map, demo idea, paid package preview, questions",
            "SLA: async report within agreed hours",
        ],
        "acceptance": ["Client can answer must_ask from report alone"],
        "security": ["Client data not used for other tenants"],
    },
}


INDUSTRY_DEFAULT_SPECS: dict[str, list[str]] = {
    "cloud-economy": [
        "billing_api",
        "gpu_orchestrator",
        "finops_board",
        "margin_bands",
        "pilot_14d",
        "orientation_paid_unit",
    ],
    "ai-agencies": [
        "auth_sso",
        "crm_webhook",
        "finops_board",
        "pilot_14d",
        "orientation_paid_unit",
    ],
    "chipmaking": [
        "gpu_orchestrator",
        "finops_board",
        "pilot_14d",
        "orientation_paid_unit",
    ],
    "telecom": [
        "billing_api",
        "crm_webhook",
        "finops_board",
        "pilot_14d",
    ],
    "cost-engineering": [
        "finops_board",
        "margin_bands",
        "pilot_14d",
        "orientation_paid_unit",
    ],
    "device-assembly": [
        "finops_board",
        "pilot_14d",
        "crm_webhook",
    ],
}


class IntegrationSpecLibrary:
    """Select standard specs for TZ from industry + idea + answers."""

    name = "Integration Spec Library"

    def select(
        self,
        *,
        industry_id: str,
        idea_title: str = "",
        modeling_answers: dict[str, Any] | None = None,
        paid: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        modeling_answers = modeling_answers or {}
        paid = paid or {}
        keys = list(INDUSTRY_DEFAULT_SPECS.get(industry_id, ["pilot_14d", "orientation_paid_unit"]))

        text = f"{idea_title} {modeling_answers.get('integration_targets', '')}".lower()
        if any(w in text for w in ("billing", "invoice", "оплат", "meter")):
            keys.append("billing_api")
        if any(w in text for w in ("sso", "auth", "oidc", "login")):
            keys.append("auth_sso")
        if any(w in text for w in ("gpu", "k8s", "orchestr", "slurm", "workload")):
            keys.append("gpu_orchestrator")
        if any(w in text for w in ("telegram", "crm", "webhook", "promo")):
            keys.append("crm_webhook")
        if "margin" in text or "band" in (idea_title or "").lower():
            keys.append("margin_bands")
        if "finops" in text or "signal" in (idea_title or "").lower():
            keys.append("finops_board")

        # Always attach finops if paid top hyp mentions it
        best = str((paid.get("package") or {}).get("best_hypothesis") or "").lower()
        if "finops" in best:
            keys.append("finops_board")

        # unique preserve order
        seen: set[str] = set()
        ordered: list[str] = []
        for k in keys:
            if k not in seen and k in STANDARD_SPECS:
                seen.add(k)
                ordered.append(k)

        specs = [STANDARD_SPECS[k] for k in ordered]
        tz_block = {
            "title": "Integration & product standards (auto-selected)",
            "specs": [
                {
                    "id": s["id"],
                    "title": s["title"],
                    "requirements": s["requirements"],
                    "acceptance": s["acceptance"],
                }
                for s in specs
            ],
            "note": (
                "Эти стандарты включаются в ТЗ пилота; детальный OpenAPI клиента — "
                "на stage custom paid."
            ),
        }
        return {
            "module": self.name,
            "selected_ids": ordered,
            "specs": specs,
            "tz_block": tz_block,
            "summary": f"Selected {len(ordered)} standard specs for {industry_id}.",
        }
