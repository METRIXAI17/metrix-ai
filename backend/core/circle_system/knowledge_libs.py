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
