"""
Expert platform knowledge libraries for Life-App niche.

physics + informatics + math + linguistic models + classification/generalization
+ applied articles + navigation = libraries for applied questions
+ concepts + breakthrough solutions + complex interconnected architecture
= expert platform
"""

from __future__ import annotations

from typing import Any


LIBRARIES: dict[str, dict[str, Any]] = {
    "physics": {
        "title": "Physics primitives",
        "entries": [
            {"id": "ph_conservation", "concept": "Conservation / balance of flows", "apply": "ops energy, cost flows"},
            {"id": "ph_entropy", "concept": "Entropy / void pressure", "apply": "VVI voids in specs"},
            {"id": "ph_resonance", "concept": "Resonance / fit peaks", "apply": "symmetry bridge client↔offer"},
        ],
    },
    "informatics": {
        "title": "Informatics primitives",
        "entries": [
            {"id": "inf_state", "concept": "State machines", "apply": "pilot phases, ticket lifecycle"},
            {"id": "inf_contracts", "concept": "Interface contracts", "apply": "integration library"},
            {"id": "inf_observability", "concept": "Logs/metrics/traces", "apply": "metric firmware → support"},
        ],
    },
    "mathematics": {
        "title": "Mathematics primitives",
        "entries": [
            {"id": "ma_logistic", "concept": "Logistic growth", "apply": "pilot accuracy predictor"},
            {"id": "ma_compose", "concept": "Metric composition", "apply": "ASM/CNS/CIR formulas"},
            {"id": "ma_threshold", "concept": "Threshold gates", "apply": "certain_yes/no, pilot gate"},
        ],
    },
    "linguistics": {
        "title": "Linguistic models",
        "entries": [
            {"id": "lg_certainty", "concept": "Certainty markers", "apply": "read lexicon CY/CN/U"},
            {"id": "lg_warmth", "concept": "Warmth bands", "apply": "answer rendering only"},
            {"id": "lg_test_shells", "concept": "Quiz shells", "apply": "super-speed assistant"},
        ],
    },
    "classification": {
        "title": "Classification & generalization",
        "entries": [
            {"id": "cl_layers", "concept": "Need layers ring", "apply": "circle-system"},
            {"id": "cl_resources", "concept": "Resource taxonomy", "apply": "resource match"},
            {"id": "cl_industries", "concept": "Industry packs", "apply": "ai-agencies, cloud, cost-eng…"},
        ],
    },
    "applied": {
        "title": "Applied articles / patterns",
        "entries": [
            {"id": "ap_free_tz", "concept": "Free tech write funnel", "apply": "consult → TZ → pilot"},
            {"id": "ap_complex_deals", "concept": "Stimulation in complex deals", "apply": "orchestration stimuli"},
            {"id": "ap_white_label", "concept": "Offline arch prompts", "apply": "no external LLM branch"},
        ],
    },
    "navigation": {
        "title": "Navigation",
        "entries": [
            {"id": "nv_ref3", "concept": "ref_3: 1 2 3 4", "apply": "param + certainty chain"},
            {"id": "nv_ref4", "concept": "ref_4: 5 6 7", "apply": "super-speed + super-program + metrics"},
            {"id": "nv_excel", "concept": "4 Бизнеса.xlsx map", "apply": "Deep Tech + Branding&VA"},
        ],
    },
    "concepts_breakthroughs": {
        "title": "Concepts & breakthrough solutions",
        "entries": [
            {"id": "cb_circle", "concept": "Circle-system autopilot", "apply": "layers as needs"},
            {"id": "cb_assembly_not_heat", "concept": "Assembly ≠ heat", "apply": "truth vs tone split"},
            {"id": "cb_metric_firmware", "concept": "Self-collecting metrics", "apply": "support feed"},
            {"id": "cb_super_program", "concept": "Six Deep Tech components", "apply": "Excel SYNTHESIS…LEDGER"},
        ],
    },
}


class ExpertKnowledgePlatform:
    """Browse/search knowledge libraries for life-app expert answers."""

    name = "Expert Knowledge Platform (Life App)"

    def catalog(self) -> dict[str, Any]:
        return {
            "module": self.name,
            "niche": "life_app",
            "equation": (
                "physics+informatics+math+linguistics+classification+applied+navigation"
                " → libraries; +concepts+breakthroughs+interconnected_architecture → expert platform"
            ),
            "libraries": {
                k: {"title": v["title"], "count": len(v["entries"])} for k, v in LIBRARIES.items()
            },
            "total_entries": sum(len(v["entries"]) for v in LIBRARIES.values()),
        }

    def search(self, query: str, limit: int = 8) -> dict[str, Any]:
        q = (query or "").lower()
        hits = []
        for lib_id, lib in LIBRARIES.items():
            for e in lib["entries"]:
                blob = f"{e['id']} {e['concept']} {e['apply']} {lib['title']}".lower()
                score = sum(1 for w in q.split() if w and w in blob)
                if score or not q:
                    hits.append(
                        {
                            "library": lib_id,
                            "score": score if q else 1,
                            **e,
                        }
                    )
        hits.sort(key=lambda x: x["score"], reverse=True)
        return {
            "module": self.name,
            "query": query,
            "hits": hits[:limit],
            "catalog": self.catalog(),
        }

    def expert_answer_scaffold(self, query: str) -> dict[str, Any]:
        found = self.search(query, limit=5)
        return {
            "question": query,
            "knowledge_hits": found["hits"],
            "architecture_note": "Interconnected: certainty → assembly → super program → layers → ops → support",
            "next": "Run deep_tech_pipeline for full consult/tech_write/pilot package",
        }


# ── Traditional artefacts (safety / QoL). Pattern → slot, not how-to. ───────

def _ta(
    id: str,
    short_name: str,
    domain: str,
    claim: str,
    evidence_grade: str,
    affects: list[str],
    contra: list[str],
    hint: str,
    risk_delta: float,
    qol_delta: float,
    hooks: list[str],
    source_span: str,
) -> dict[str, Any]:
    from backend.core.naming_canon import artefact_sigil

    return {
        "id": id,
        "short_name": short_name,
        "domain": domain,  # safety | qol | hybrid
        "claim": claim,
        "evidence_grade": evidence_grade,  # lived | codified | contested
        "affects": list(affects),
        "contra_indications": list(contra),
        "cy_cn_u_hint": hint,
        "risk_delta": risk_delta,
        "qol_delta": qol_delta,
        "chain_hooks": list(hooks),
        "source_span": source_span,
        "sigil": artefact_sigil(id, domain),
        "kind": "traditional_artefact",
        "medical_legal_howto": False,
    }


TRADITIONAL_ARTEFACTS: list[dict[str, Any]] = [
    # water / food / sleep-rhythm
    _ta("ta_water_window_s", "Water window", "safety", "Predictable water windows cut void_membrane on load days.", "lived", ["void_membrane"], ["healthcare", "medical", "pharma"], "U", -0.03, 0.04, ["pragma_void_pressure"], "Regular water windows stabilize attention load."),
    _ta("ta_meal_anchor_q", "Meal anchor", "qol", "Shared meal clock reduces open_manifold in household ops.", "lived", ["open_manifold", "value_pipeline"], ["healthcare", "dietetics"], "U", 0.0, 0.05, ["pragma_rhythm"], "A repeating meal clock is a household metronome."),
    _ta("ta_sleep_gate_s", "Sleep gate", "safety", "Fixed sleep gate lowers risk on next-day delivery slots.", "codified", ["void_membrane", "bound_shell"], ["healthcare", "medical"], "U", -0.04, 0.03, ["pragma_load"], "Protect the sleep gate before adding night work."),
    _ta("ta_caffeine_late_c", "Late stimulant", "safety", "Late stimulants are contested as a load hack; keep U.", "contested", ["void_membrane"], ["healthcare"], "U", 0.0, 0.0, ["pragma_contested"], "Late stimulant as productivity is contested."),
    # dwelling / heat
    _ta("ta_heat_buffer_s", "Heat buffer", "safety", "A heat/cold buffer on dwelling cuts infra_sol void.", "lived", ["infra_sol", "void_membrane"], ["construction_unlicensed"], "U", -0.03, 0.04, ["pragma_infra"], "Buffer the dwelling climate before scaling night shifts."),
    _ta("ta_light_q", "Daylight slot", "qol", "Daylight in the work slot lowers digital-noise void.", "lived", ["signal_port", "open_manifold"], [], "CY", -0.01, 0.04, ["pragma_attention"], "Daylight in the work slot is a cheap QoL bind."),
    _ta("ta_exit_path_s", "Clear exit path", "safety", "A clear physical exit path binds infra_sol safety slot.", "codified", ["infra_sol", "bound_shell"], ["fire_code_authority"], "CY", -0.05, 0.02, ["pragma_safety_path"], "Keep one unblocked exit path in the workspace."),
    _ta("ta_mold_contested_c", "Air-cure myth", "safety", "Folk air-cures for damp are contested; do not raise assembly.", "contested", ["infra_sol"], ["healthcare", "housing_law"], "U", 0.02, 0.0, ["pragma_contested"], "Folk damp cures stay U until a building check."),
    # money / debt / contract
    _ta("ta_written_terms_s", "Written terms", "safety", "Written terms bind revenue_hinge and cut contract void.", "codified", ["revenue_hinge", "bound_shell"], ["legal_advice"], "CY", -0.05, 0.02, ["pragma_contract"], "Write the terms before the work starts."),
    _ta("ta_debt_cap_q", "Debt cap", "qol", "A named debt cap lowers money void without a legal how-to.", "lived", ["revenue_hinge", "void_membrane"], ["legal_advice", "finance_advice"], "U", -0.03, 0.04, ["pragma_money"], "Name a debt cap as a slot, not as a product."),
    _ta("ta_handoff_receipt_s", "Handoff receipt", "safety", "A receipt on handoff binds structure_fi owner slot.", "codified", ["structure_fi", "role_lattice"], ["legal_advice"], "CY", -0.04, 0.02, ["pragma_handoff"], "Every handoff gets a receipt and an owner."),
    _ta("ta_handshake_only_c", "Handshake-only", "safety", "Handshake-only deals are contested as sufficient bind.", "contested", ["revenue_hinge"], ["legal_advice"], "U", 0.03, 0.0, ["pragma_contested"], "Handshake-only is not a closed revenue_hinge."),
    # attention / digital noise
    _ta("ta_notice_batch_q", "Notice batch", "qol", "Batching notices lowers signal_port noise.", "lived", ["signal_port", "open_manifold"], [], "CY", -0.02, 0.05, ["pragma_attention"], "Batch notices; do not live inside the inbox."),
    _ta("ta_night_mute_s", "Night mute", "safety", "Night mute on channels protects sleep-gate and load.", "lived", ["void_membrane", "signal_port"], [], "CY", -0.03, 0.04, ["pragma_load"], "Mute channels in the sleep gate."),
    _ta("ta_dual_device_q", "Work device split", "qol", "A work/life device split cuts digital-noise void.", "lived", ["signal_port", "bound_shell"], [], "U", -0.01, 0.04, ["pragma_attention"], "Split work device from rest device when you can."),
    _ta("ta_always_on_c", "Always-on myth", "qol", "Always-on availability as quality is contested.", "contested", ["signal_port"], [], "U", 0.02, -0.02, ["pragma_contested"], "Always-on is not a QoL bind."),
    # body / load
    _ta("ta_load_cap_s", "Load cap", "safety", "A named daily load cap binds bound_shell.", "lived", ["bound_shell", "void_membrane"], ["healthcare", "medical", "sports_medicine"], "U", -0.04, 0.03, ["pragma_load"], "Cap the day's load before adding a lane."),
    _ta("ta_walk_slot_q", "Walk slot", "qol", "A walk slot between sessions lowers open_manifold.", "lived", ["open_manifold", "value_pipeline"], ["healthcare"], "U", 0.0, 0.04, ["pragma_rhythm"], "A walk slot is a QoL metronome, not therapy."),
    _ta("ta_rest_day_s", "Rest day", "safety", "A rest day in the week binds void_membrane on people-ops.", "lived", ["void_membrane", "role_lattice"], ["healthcare"], "U", -0.03, 0.04, ["pragma_load"], "Keep one rest day in the week of delivery."),
    _ta("ta_pain_push_c", "Push-through", "safety", "Pushing through pain as discipline is contested.", "contested", ["void_membrane"], ["healthcare", "medical"], "U", 0.05, -0.04, ["pragma_contested"], "Pain-as-signal is medical; this artefact stays U."),
    # community / handoff
    _ta("ta_named_owner_s", "Named owner", "safety", "A named owner on the weak link binds role_lattice.", "codified", ["role_lattice", "structure_fi"], [], "CY", -0.04, 0.02, ["pragma_handoff"], "Name the owner of the weak link."),
    _ta("ta_backup_human_q", "Backup human", "qol", "A backup human on handoff lowers community void.", "lived", ["role_lattice", "open_manifold"], [], "CY", -0.02, 0.05, ["pragma_handoff"], "Every critical handoff has a backup human."),
    _ta("ta_circle_check_s", "Circle check", "safety", "A short circle-check before go-live binds product_sol.", "lived", ["product_sol", "success_gauge"], [], "CY", -0.03, 0.03, ["pragma_gate"], "Circle-check the gate before Main."),
    _ta("ta_crowd_wisdom_c", "Crowd as spec", "hybrid", "Crowd-as-spec is contested; does not raise assembly.", "contested", ["success_gauge"], [], "U", 0.01, 0.0, ["pragma_contested"], "A crowd is not a closed success_gauge."),
]


def list_traditional_artefacts(domain: str | None = None) -> list[dict[str, Any]]:
    items = list(TRADITIONAL_ARTEFACTS)
    if domain in ("safety", "qol", "hybrid"):
        items = [a for a in items if a["domain"] == domain]
    return items


def get_traditional_artefact(artefact_id: str) -> dict[str, Any] | None:
    for a in TRADITIONAL_ARTEFACTS:
        if a["id"] == artefact_id or a.get("sigil") == artefact_id:
            return dict(a)
    return None


def search_traditional_artefacts(query: str, *, domain: str | None = None, limit: int = 12) -> list[dict[str, Any]]:
    q = (query or "").lower()
    hits = []
    for a in list_traditional_artefacts(domain):
        blob = " ".join(
            str(a.get(k) or "")
            for k in ("id", "short_name", "claim", "source_span", "domain")
        ).lower()
        score = sum(1 for w in q.split() if w and w in blob) if q else 1
        if score:
            hits.append({**a, "score": score})
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:limit]

