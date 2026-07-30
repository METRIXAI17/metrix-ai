"""
Terminal functions / subtopic specs — concrete tech-write units from layers + super program.
"""

from __future__ import annotations

from typing import Any


SUBTOPIC_TEMPLATES: dict[str, dict[str, Any]] = {
    "orientation_brief": {
        "layer": "orientation",
        "title": "Orientation brief",
        "sections": ("context", "segment", "constraint_map", "must_ask"),
    },
    "tech_write_core": {
        "layer": "product",
        "title": "Tech write / TZ core",
        "sections": ("problem", "scope", "interfaces", "acceptance", "metrics"),
    },
    "pilot_charter": {
        "layer": "pilot",
        "title": "Pilot charter",
        "sections": ("in_scope", "out_of_scope", "timeline", "success", "roles"),
    },
    "ops_rules_slice": {
        "layer": "operations",
        "title": "Operational rules slice",
        "sections": ("triggers", "actions", "owners", "escalation"),
    },
    "integration_contract": {
        "layer": "integration",
        "title": "Integration contract",
        "sections": ("systems", "auth", "data_map", "sla"),
    },
    "metric_firmware_spec": {
        "layer": "metrics",
        "title": "Metric firmware spec",
        "sections": ("base_metrics", "derived", "collection", "support_hooks"),
    },
    "ledger_hooks": {
        "layer": "resources",
        "title": "Ledger & resource hooks",
        "sections": ("resource_inventory", "collab_authors", "ledger_fields"),
    },
    "arch_prompt_pack": {
        "layer": "expertise",
        "title": "Architectural prompt pack (offline)",
        "sections": ("system_prompt", "module_map", "client_white_label"),
    },
}


class TerminalSpecBuilder:
    """Build terminal function specs from circle state."""

    name = "Terminal Spec Builder"

    def run(
        self,
        layers_result: dict[str, Any],
        super_program: dict[str, Any] | None = None,
        certainty_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        confirmed = set(layers_result.get("confirmed_layers") or [])
        need_levels = {L["layer"]: L["need_level"] for L in layers_result.get("layers") or []}
        primary = (super_program or {}).get("primary") or {}
        params = {p["slot"]: p for p in (certainty_result or {}).get("parameters") or []}

        specs: list[dict[str, Any]] = []
        for key, tmpl in SUBTOPIC_TEMPLATES.items():
            layer = tmpl["layer"]
            if need_levels.get(layer) in ("absent",) and layer not in confirmed:
                # still emit skeleton for product/pilot always
                if key not in ("tech_write_core", "pilot_charter"):
                    continue
            body_lines = []
            for sec in tmpl["sections"]:
                body_lines.append(f"## {sec}")
                # attach param snippets when available
                for slot, p in params.items():
                    if slot in sec or sec in ("scope", "problem", "context", "success"):
                        body_lines.append(f"- ({slot}/{p.get('status')}): {p.get('snippet','')[:160]}")
                        break
                else:
                    body_lines.append(f"- [TODO:{sec}] fill from client test answers")

            specs.append(
                {
                    "id": key,
                    "title": tmpl["title"],
                    "layer": layer,
                    "sections": list(tmpl["sections"]),
                    "status": "ready_draft" if layer in confirmed else "skeleton",
                    "markdown": "\n".join(body_lines),
                    "super_program_link": primary.get("family"),
                }
            )

        return {
            "module": self.name,
            "terminal_functions": specs,
            "count": len(specs),
            "tech_write_ids": [s["id"] for s in specs if "tech" in s["id"] or s["id"] == "pilot_charter"],
            "rule": "Each subtopic is a terminal function with explicit sections (spec-grade).",
        }
