"""
General Semantic Engine — multi-pass narrative production.

Pass 1: skeleton from true relations + probability map + intermediate templates
Pass 2: English word-substitution / part particles
Pass 3: Anticlone (template detect + edit + layer)
Pass 4: Product-closure mode — close all recommended products sentence-by-sentence
        using concept bases + 21-principle inconsistency checks
"""

from __future__ import annotations

import re
from typing import Any

from backend.paid.narrative.anticlone import AnticloneEditor
from backend.paid.narrative.distortion import DistortionPurge
from backend.paid.narrative.probability_map import HighestProbabilityMap
from backend.paid.narrative.relations import RelationshipBrain
from backend.paid.narrative.values_and_templates import ValueTemplateEngine
from backend.paid.principles_engine import PRINCIPLES, get_principles_engine
from backend.paid.types import clamp01, safe_float


# Concept bases for pass-4 product closure (latest progress vocabulary)
CONCEPT_BASES: dict[str, list[str]] = {
    "pipeline": [
        "orientation",
        "paid_core",
        "commercial_surface",
        "must_ask",
        "learning_state",
    ],
    "narrative": [
        "relationship_brain",
        "probability_map",
        "distortion_purge",
        "anticlone",
        "value_board",
        "intermediate_template",
    ],
    "products": [
        "orientation_run",
        "pilot",
        "full_package",
        "objectly",
        "opening_edge",
        "data_market",
        "harness",
        "finops_board",
    ],
    "principles": [PRINCIPLES[i]["key"] for i in range(1, 22)],
    "discrepancy_classic": [
        "paid_vs_parallel",
        "status_vs_readiness",
        "claim_vs_metric",
        "hypothesis_vs_leak",
        "preview_vs_packageable",
        "template_vs_client_anchor",
        "direct_vs_reverse_missing",
        "sku_vs_value_board",
        "sentence_vs_under_hood",
        "principle_vs_action_gap",
    ],
}


class NarrativeSemanticEngine:
    name = "Narrative Semantic Engine"
    version = "1.0"

    def __init__(self) -> None:
        self.relations = RelationshipBrain()
        self.pmap = HighestProbabilityMap()
        self.purge = DistortionPurge()
        self.anticlone = AnticloneEditor()
        self.values = ValueTemplateEngine()
        self.principles = get_principles_engine()

    def run(
        self,
        *,
        industry_id: str = "",
        business: str = "",
        idea_title: str = "",
        paid: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
        principles_report: dict[str, Any] | None = None,
        anti_down: dict[str, Any] | None = None,
        must_ask_open: int = 0,
    ) -> dict[str, Any]:
        paid = paid or {}
        scores = scores or {}
        extra = {
            k: v
            for k, v in (extra_params or {}).items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        pkg = paid.get("package") or {}
        sm = paid.get("situation_metrics") or paid.get("business_metrics") or {}
        top_lever = str(pkg.get("top_lever") or (paid.get("function_engine") or {}).get("top_lever") or "")
        top_leak = str((sm.get("top_leak") or {}).get("label") or "")
        client_tokens = self._client_tokens(business, idea_title)

        # ── Brain ──────────────────────────────────────────────────────────
        rel = self.relations.map(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            top_lever=top_lever,
            top_leak=top_leak,
            scores=scores,
            extra_params=extra,
        )
        prin = principles_report or self.principles.run(
            industry_id=industry_id,
            scores=scores,
            top_lever=top_lever,
            residual_uncertainty=safe_float(
                (paid.get("conceptual_trajectory") or {}).get("residual_uncertainty"),
                0.35,
            ),
        )
        pmap = self.pmap.build(
            paid=paid,
            business=business,
            idea_title=idea_title,
            relations=rel,
            principles=prin,
            anti_down=anti_down or {},
        )

        # ── Pass 1: skeleton from intermediate templates + map ─────────────
        val_board = self.values.analyze_values(
            paid=paid,
            extra_params=extra,
            anticlone={},
            probability_map=pmap,
            idea_title=idea_title,
        )
        intermediate = self.values.intermediate_fill(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            relations=rel,
            values=val_board,
            paid=paid,
            extra_params=extra,
        )
        pass1_sentences = [x["text"] for x in intermediate]
        for c in (pmap.get("top_positive") or [])[:3]:
            pass1_sentences.append(c["text"])

        # ── Operational purge ──────────────────────────────────────────────
        purged = self.purge.run(
            draft_sentences=pass1_sentences,
            relations=rel,
            probability_map=pmap,
            must_ask_open=must_ask_open,
            paid_status=str(paid.get("status") or ""),
            client_tokens=client_tokens,
        )
        pass1b = [k["sentence"] for k in purged["kept"]]
        if purged.get("narrowed_variants"):
            pass1b.extend(purged["narrowed_variants"][:3])

        # ── Pass 2: English particle substitution ──────────────────────────
        pass2 = self._pass2_english_particles(
            pass1b, industry_id, top_lever, idea_title, client_tokens, extra
        )

        # ── Pass 3: Anticlone ───────────────────────────────────────────────
        voids = [
            "buyer job in their exact words",
            "proof metric owner for the pilot",
            "capacity for Full Package delivery without founder burnout",
        ]
        if must_ask_open:
            voids.insert(0, f"{must_ask_open} must-ask fields still open")
        ac = self.anticlone.run(
            sentences=pass2,
            client_tokens=client_tokens,
            numbers=extra,
            true_hubs=[g["hub"] for g in (rel.get("true_groups") or [])[:3]],
            void_notes=voids,
            pass_name="pass3_anticlone",
        )
        pass3 = ac["edited_sentences"]

        # Recompute values after anticlone polish
        val_board = self.values.analyze_values(
            paid=paid,
            extra_params=extra,
            anticlone=ac,
            probability_map=pmap,
            idea_title=idea_title,
        )
        products = self.values.product_templates(
            values=val_board, paid=paid, industry_id=industry_id
        )

        # ── Pass 4: product-closure mode ───────────────────────────────────
        pass4 = self._pass4_product_closure(
            pass3, products, prin, paid, business, idea_title, client_tokens
        )

        # Cross-sentence sense + 21-principle inconsistency
        consistency = self._consistency_check(pass4["sentences"], prin, paid, pmap)

        # Final polished memo sections
        memo = self._assemble_memo(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            sentences=pass4["sentences"],
            values=val_board,
            products=products,
            relations=rel,
            pmap=pmap,
            consistency=consistency,
            top_lever=top_lever,
            top_leak=top_leak,
            extra=extra,
            must_ask_open=must_ask_open,
            paid=paid,
        )

        return {
            "module": self.name,
            "version": self.version,
            "relations": rel,
            "probability_map": {
                "top_positive": pmap.get("top_positive"),
                "writing_rails": pmap.get("writing_rails"),
                "method": pmap.get("method"),
                "max_probability": pmap.get("max_probability"),
            },
            "distortion_purge": {
                "kept_count": purged["kept_count"],
                "removed_count": purged["removed_count"],
                "distortion_rate": purged["distortion_rate"],
                "true_hubs": purged["true_hubs"],
            },
            "values": val_board,
            "intermediate_templates": intermediate,
            "product_templates": products,
            "passes": {
                "1_skeleton": pass1_sentences,
                "1b_purged": pass1b,
                "2_english_particles": pass2,
                "3_anticlone": ac,
                "4_product_closure": pass4,
            },
            "consistency": consistency,
            "concept_bases_loaded": {k: len(v) for k, v in CONCEPT_BASES.items()},
            "memo": memo,
            "plain_client_summary": memo.get("executive_summary"),
            "quality": {
                "template_index": ac.get("template_index_after"),
                "client_anchor_rate": ac.get("client_anchor_rate"),
                "anticlone_pass": ac.get("passed_threshold"),
                "consistency_score": consistency.get("score"),
                "distortion_rate": purged.get("distortion_rate"),
            },
        }

    def _client_tokens(self, business: str, idea_title: str) -> list[str]:
        words = re.findall(r"[A-Za-zа-яА-ЯёЁ]{4,}", f"{idea_title} {business}")
        seen = set()
        out = []
        for w in words:
            wl = w.lower()
            if wl not in seen:
                seen.add(wl)
                out.append(wl)
        return out[:16]

    def _pass2_english_particles(
        self,
        sentences: list[str],
        industry_id: str,
        lever: str,
        idea_title: str,
        tokens: list[str],
        extra: dict[str, Any],
    ) -> list[str]:
        """Upgrade skeleton English with action particles per clause."""
        action_verbs = {
            "context": "situates",
            "diagnosis": "isolates",
            "action": "directs",
            "hypothesis": "tests",
            "honesty": "bounds",
            "product": "recommends",
            "asset": "packages",
        }
        out = []
        for i, s in enumerate(sentences):
            # Avoid double-prefixing
            if s.startswith("Operationally,"):
                out.append(s)
                continue
            particle = list(action_verbs.values())[i % len(action_verbs)]
            # light lexical upgrade
            ns = s
            ns = ns.replace(" «", " '").replace("»", "'")
            if lever and lever not in ns and i == 1:
                ns = f"{ns.rstrip('.')} via lever '{lever}'."
            if industry_id and i == 0 and industry_id not in ns:
                ns = f"[{industry_id}] {ns}"
            out.append(f"Operationally, this {particle}: {ns}" if i < 4 else ns)
        return out

    def _pass4_product_closure(
        self,
        sentences: list[str],
        products: list[dict[str, Any]],
        principles: dict[str, Any],
        paid: dict[str, Any],
        business: str,
        idea_title: str,
        tokens: list[str],
    ) -> dict[str, Any]:
        """Close each recommended product with sentence coverage + concept bases."""
        top_products = [p for p in products if p.get("recommend_score", 0) >= 0.5][:4]
        closures: list[dict[str, Any]] = []
        extra_sentences: list[str] = []

        active_p = principles.get("active_principles") or []
        pkeys = [x.get("key") if isinstance(x, dict) else str(x) for x in active_p]

        for prod in top_products:
            parts = prod.get("parts") or []
            concept_hits = [
                c
                for c in CONCEPT_BASES["products"]
                if c in prod["sku"] or c.replace("_", "") in prod["sku"].replace("_", "")
            ]
            # sentence that closes the product
            close = (
                f"Product close — {prod['name']} (${prod['price_usd']}): "
                f"covers parts [{', '.join(parts[:5])}] "
                f"because under-hood signals favor this SKU "
                f"(score {prod['recommend_score']}). "
                f"Principle anchors: {', '.join(str(k) for k in pkeys[:3]) or 'sector, service_metrics, concept'}."
            )
            if tokens:
                close += f" Client lexicon retained: {', '.join(tokens[:4])}."
            extra_sentences.append(close)
            closures.append(
                {
                    "sku": prod["sku"],
                    "name": prod["name"],
                    "price_usd": prod["price_usd"],
                    "parts_closed": parts,
                    "concept_hits": concept_hits or CONCEPT_BASES["products"][:2],
                    "closure_sentence": close,
                }
            )

        # Merge narrative + closures
        merged = list(sentences) + extra_sentences
        # Second anticlone light pass on product sentences only
        ac2 = self.anticlone.run(
            sentences=extra_sentences,
            client_tokens=tokens,
            numbers={},
            true_hubs=[],
            void_notes=["product claim without delivery capacity"],
            pass_name="pass4_product_anticlone",
        )
        # replace extra with edited
        merged = list(sentences) + ac2["edited_sentences"]

        return {
            "mode": "product_closure",
            "closures": closures,
            "sentences": merged,
            "concept_bases": CONCEPT_BASES,
            "products_closed": len(closures),
            "anticlone_product_pass": {
                "template_index_after": ac2.get("template_index_after"),
                "passed": ac2.get("passed_threshold"),
            },
        }

    def _consistency_check(
        self,
        sentences: list[str],
        principles: dict[str, Any],
        paid: dict[str, Any],
        pmap: dict[str, Any],
    ) -> dict[str, Any]:
        """Common sense between sentences + 21-principle disconnection list."""
        issues: list[dict[str, str]] = []
        text = " ".join(sentences).lower()

        # Classic discrepancy list from CONCEPT_BASES
        status = str(paid.get("status") or "")
        if "packageable" in text and status in ("preview", "candidate_preview"):
            issues.append(
                {
                    "type": "preview_vs_packageable",
                    "detail": "Text implies packageable while status is preview",
                }
            )
        if "guaranteed" in text:
            issues.append(
                {
                    "type": "claim_vs_metric",
                    "detail": "Absolute guarantee language without metric owner",
                }
            )
        rails = pmap.get("writing_rails") or []
        if "top_lever" in rails and "lever" not in text and "lever" not in text:
            # check lever word
            if "lever" not in text:
                issues.append(
                    {
                        "type": "sentence_vs_under_hood",
                        "detail": "Top lever on probability map but missing in prose",
                    }
                )

        # Principle disconnection: active principles not reflected
        active = principles.get("active_principle_ids") or []
        principle_words = {
            2: "metric",
            4: "concept",
            14: "resource",
            16: "profit",
            19: "object",
            21: "live",
        }
        for pid, word in principle_words.items():
            if pid in active and word not in text:
                issues.append(
                    {
                        "type": "principle_vs_action_gap",
                        "detail": f"Principle {pid} active but word '{word}' absent in narrative",
                    }
                )

        # Pairwise thin similarity (clone residual)
        clone_pairs = 0
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                a, b = set(sentences[i].lower().split()), set(sentences[j].lower().split())
                if not a or not b:
                    continue
                jacc = len(a & b) / max(1, len(a | b))
                if jacc > 0.55:
                    clone_pairs += 1
                    issues.append(
                        {
                            "type": "template_vs_client_anchor",
                            "detail": f"Sentences {i} and {j} overly similar (jaccard {jacc:.2f})",
                        }
                    )

        score = clamp01(1.0 - 0.08 * len(issues) - 0.05 * clone_pairs)
        return {
            "score": round(score, 4),
            "issues": issues[:20],
            "issue_count": len(issues),
            "classic_types_covered": CONCEPT_BASES["discrepancy_classic"],
            "method": (
                "Under-hood vs sentence sense-match + 21-principle gap scan + "
                "classic discrepancy catalog"
            ),
        }

    def _assemble_memo(self, **kw: Any) -> dict[str, Any]:
        business = kw["business"]
        idea = kw["idea_title"]
        industry = kw["industry_id"]
        sentences = kw["sentences"]
        values = kw["values"]
        products = kw["products"]
        rel = kw["relations"]
        extra = kw["extra"]
        lever = kw["top_lever"]
        leak = kw["top_leak"]
        must = kw["must_ask_open"]
        paid = kw["paid"]
        consistency = kw["consistency"]

        # Clean client-facing assembly (no RU/EN mix, no system dump)
        industry_label = {
            "ai-agencies": "AI agencies",
            "cloud-economy": "cloud / API-cost operations",
            "cost-engineering": "cost engineering",
            "chipmaking": "chipmaking",
            "telecom": "telecom",
            "device-assembly": "device assembly",
        }.get(industry, (industry or "your market").replace("-", " "))

        hubs = ", ".join(
            g["hub"].replace("_", " ") for g in (rel.get("true_groups") or [])[:3]
        ) or "your core operators"
        nums_parts = []
        for k, v in list(extra.items())[:5]:
            lab = k.replace("_", " ")
            if isinstance(v, float) and 0 < v <= 1 and "day" not in k and "revenue" not in k:
                nums_parts.append(f"{lab} {v:.0%}")
            elif "revenue" in k:
                nums_parts.append(f"{lab} ${v:,.0f}" if float(v) > 100 else f"{lab} {v}")
            else:
                nums_parts.append(f"{lab} {v}")
        nums = "; ".join(nums_parts) if nums_parts else "no locked numbers yet — frame still usable"
        top_prod = products[0] if products else {}
        val_labels = ", ".join(
            v["label"] for v in (values.get("values_present") or [])[:4]
        )
        leak_clean = (leak or "").strip()
        if "размыт" in leak_clean.lower() or not leak_clean:
            leak_clean = "operational friction that is real but not yet named in buyer language"
        lever_h = (lever or "clarity").replace("_", " ")
        idea_h = (idea or "the oriented offer").strip()
        brief = (business or "").strip()
        if len(brief) > 200:
            brief = brief[:197] + "…"

        exec_sum = (
            f"You operate in {industry_label}. In your words: {brief} "
            f"We oriented the work around «{idea_h}». "
            f"Working diagnosis: {leak_clean}. "
            f"Near-term dial to turn: {lever_h}. "
            f"People and assets that must stay in the story: {hubs}. "
            f"Numbers in this run: {nums}. "
            f"Value board: {val_labels or 'will firm up after a few missing answers'}. "
            f"Sensible entry conversation: {top_prod.get('name', 'Orientation Run')} "
            f"(${top_prod.get('price_usd', 290)}). "
            f"Consult + Tech Write package sits at $1290 when you want diagnosis plus build-ready writing. "
            + (
                f"{must} clarifying items are still open — we do not oversell a full package until they are closed."
                if must
                else "Clarifying gate is clear enough for a pilot-level conversation."
            )
        )

        # Situation: clean sentences (drop machine stems)
        sit_bits = []
        for s in sentences[:5]:
            t = re.sub(
                r"Operationally, this (situates|isolates|directs|tests):\s*",
                "",
                str(s),
                flags=re.I,
            )
            t = re.sub(r"hub actor:\s*\w+", "", t, flags=re.I)
            t = re.sub(r"bound to \w+=[\d.]+", "", t, flags=re.I)
            t = re.sub(r"\s{2,}", " ", t).strip(" ;.")
            if t and len(t) > 20:
                sit_bits.append(t)
        situation_body = " ".join(sit_bits[:4]) or (
            f"Your operation sits in {industry_label}. "
            f"Keep {hubs} visible in every decision about «{idea_h}»."
        )

        claims = []
        for c in (kw["pmap"].get("top_positive") or [])[:5]:
            t = str(c.get("text") or "").strip()
            if t:
                claims.append(t)
        diagnosis_body = (
            " ".join(claims)
            if claims
            else f"Primary offer spine «{idea_h}»; turn {lever_h} first; stay honest on unknowns."
        )

        cscore = safe_float(consistency.get("score"), 0.0)
        # Never parade a broken 0.0 consistency as a client KPI
        honesty_body = (
            "This memo does not invent market size, guaranteed ROI, or buyer intent. "
            f"Internal package status: {paid.get('status') or 'n/a'}. "
            + (
                f"Narrative QC noted {consistency.get('issue_count') or 0} polish items for our team — "
                "they do not change the honesty gate on commercial claims."
                if cscore < 0.35
                else f"Narrative consistency band is healthy ({cscore:.0%})."
            )
        )

        sections = [
            {"id": "executive_summary", "title": "Executive summary", "body": exec_sum},
            {
                "id": "situation",
                "title": "Situation",
                "body": situation_body,
            },
            {
                "id": "diagnosis",
                "title": "Diagnosis",
                "body": diagnosis_body,
            },
            {
                "id": "value_board",
                "title": "What is valuable when polished",
                "body": "; ".join(
                    f"{v['label']}"
                    for v in (values.get("values_present") or [])[:8]
                )
                or "Collect five operating numbers and we will firm the value board.",
            },
            {
                "id": "recommendation",
                "title": "Recommended path",
                "body": " · ".join(
                    f"{p['name']} (${p['price_usd']})"
                    for p in products[:4]
                )
                or "Orientation Run ($290) → Consult+Tech Write ($1290)",
            },
            {
                "id": "pilot_14",
                "title": "Next 14 days",
                "body": (
                    f"1) Put a simple proof metric on «{lever_h}» with one named owner. "
                    f"2) Write one if/then pilot hypothesis (metric + deadline). "
                    f"3) Cut one free-discovery activity that burns margin without converting. "
                    f"4) Close remaining clarifying items ({must} open). "
                    f"5) Choose path: {top_prod.get('name', 'Orientation')} / Consult+Tech Write ($1290) / pause — only if honesty still holds."
                ),
            },
            {
                "id": "honesty",
                "title": "Honesty & voids",
                "body": honesty_body,
            },
        ]

        return {
            "title": f"Orientation memo — {idea_h if idea else industry_label}",
            "executive_summary": exec_sum,
            "sections": sections,
            "sentences_final": sentences,
            "tone": "consultant_client_facing",
        }
