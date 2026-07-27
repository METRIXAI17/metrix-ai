"""
Idea Portfolio Engine — multiple demo ideas for operational success.

Instead of a single seed idea, builds an adaptive set covering product /
teammate / angle gaps until operational-success coverage is exhaustive enough.

Primary idea (rank 1) remains available as `demo_idea` for backward compatibility.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any


# Operational-success stages (marketing strategy 1→6 compressed into sellable ideas)
OPS_ROLES: list[dict[str, Any]] = [
    {
        "role": "consultation",
        "stage": 1,
        "track": "product",
        "label": "MetaReality consultation",
        "template": "Free orientation consult — {hook}",
        "covers": ("product", "clarity", "ops"),
    },
    {
        "role": "solution_bridge",
        "stage": 1,
        "track": "product",
        "label": "Solution Bridge · Pick a solution",
        "template": "Clear SKUs after orientation — {hook}",
        "covers": ("product", "clarity", "ops"),
    },
    {
        "role": "specs_writing",
        "stage": 1,
        "track": "product",
        "label": "SpecsForge tech writing",
        "template": "SpecsForge pack after consult: recursive specs for {hook}",
        "covers": ("product", "specs"),
    },
    {
        "role": "predev_teammate",
        "stage": 1,
        "track": "models",
        "label": "Terminal Teammate pre-dev",
        "template": "Terminal Teammate pre-dev production for promo stage — {hook}",
        "covers": ("models", "promo", "ops"),
    },
    {
        "role": "posts_surface",
        "stage": 2,
        "track": "promotion",
        "label": "AnalogBridge posts surface",
        "template": "X AnalogBridge operator surface for posts around {hook}",
        "covers": ("promo", "surface"),
    },
    {
        "role": "replies_optimizer",
        "stage": 2,
        "track": "models",
        "label": "CloudForge replies",
        "template": "CloudForge precision optimizer for replies under {hook}",
        "covers": ("models", "surface"),
    },
    {
        "role": "marketplace_lattice",
        "stage": 3,
        "track": "product",
        "label": "PragmaVault marketplace",
        "template": "PragmaVault pattern lattice — assign ready patterns for {hook}",
        "covers": ("product", "market"),
    },
    {
        "role": "ads_weave",
        "stage": 4,
        "track": "promotion",
        "label": "Linguistic Signal ads",
        "template": "Linguistic Signal Weaver ads kit angled at {hook}",
        "covers": ("promo", "ads"),
    },
    {
        "role": "decision_harness",
        "stage": 5,
        "track": "models",
        "label": "VerdictLattice harness",
        "template": "VerdictLattice decision core — interest zone harness for {hook}",
        "covers": ("models", "harness"),
    },
    {
        "role": "insight_chat",
        "stage": 5,
        "track": "product",
        "label": "OpticPrism chatbot",
        "template": "OpticPrism insight lens chatbot for interaction on {hook}",
        "covers": ("product", "harness"),
    },
    {
        "role": "post_lead_topology",
        "stage": 6,
        "track": "promotion",
        "label": "ZoneWeave post→lead",
        "template": "ZoneWeave topology: post → lead actions for {hook}",
        "covers": ("promo", "topology"),
    },
    {
        "role": "client_geometry_deep",
        "stage": 6,
        "track": "product",
        "label": "ClientGeometry deep",
        "template": "ClientGeometry forge — deep client interaction architecture for {hook}",
        "covers": ("product", "topology"),
    },
    {
        "role": "demand_heat_overlay",
        "stage": 6,
        "track": "models",
        "label": "Superstructure heat markers",
        "template": "Superstructure overlay: demand heat markers on {hook}",
        "covers": ("models", "topology", "ops"),
    },
]

MIN_IDEAS = 3
MAX_IDEAS = 9
GAP_THRESHOLD = 0.55


@dataclass
class IdeaPortfolio:
    primary: dict[str, Any]
    ideas: list[dict[str, Any]]
    coverage: dict[str, Any]
    summary: str
    method: str = "ops_success_exhaustive_portfolio"

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "IdeaPortfolioEngine",
            "method": self.method,
            "count": len(self.ideas),
            "primary": self.primary,
            "ideas": self.ideas,
            "coverage": self.coverage,
            "summary": self.summary,
        }


class IdeaPortfolioEngine:
    """Build adaptive multi-idea set for operational success."""

    name = "IdeaPortfolioEngine"

    def __init__(self, idea_seeds: dict[str, dict[str, list[str]]] | None = None) -> None:
        # Lazy import avoid circular; seeds injected from product_sol
        self.idea_seeds = idea_seeds or {}

    def build(
        self,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
        primary_track: str = "product",
        specs_ready: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> IdeaPortfolio:
        scores = orientation.get("scores") or {}
        tracks_rec = orientation.get("tracks_recommended") or [
            "product",
            "models",
            "promotion",
        ]
        track = primary_track if primary_track in ("product", "models", "promotion") else "product"
        hook = self._hook_phrase(business_text)
        gaps = self._detect_gaps(scores, track)
        target_n = self._target_count(gaps, track, scores)

        candidates: list[dict[str, Any]] = []

        # A) Industry seed titles across all tracks (exhaustive catalog slice)
        seeds = self.idea_seeds.get(industry_id) or self.idea_seeds.get("ai-agencies") or {}
        for tr, titles in seeds.items():
            for i, title in enumerate(titles):
                candidates.append(
                    self._candidate(
                        title=title,
                        track=tr,
                        kind="industry_seed",
                        role=f"seed_{tr}_{i}",
                        stage=1 if tr == "product" else (2 if tr == "models" else 4),
                        covers=(tr, "seed"),
                        base_score=self._seed_score(tr, track, scores, i),
                        why=f"Industry seed · {tr} · fit={scores.get(tr + '_fit' if tr != 'models' else 'model_fit', 0):.2f}",
                    )
                )

        # B) Ops-success role templates (strategy 1–6)
        for role in OPS_ROLES:
            title = role["template"].format(industry=industry_id, hook=hook)
            boost = 0.12 if any(g in role["covers"] for g in gaps) else 0.0
            if role["track"] == track:
                boost += 0.08
            if role["role"] == "solution_bridge":
                boost += 0.1  # always valuable between orient and pick
            if role["role"] == "specs_writing" and specs_ready:
                boost += 0.05
            candidates.append(
                self._candidate(
                    title=title,
                    track=role["track"],
                    kind="ops_role",
                    role=role["role"],
                    stage=role["stage"],
                    covers=tuple(role["covers"]),
                    base_score=0.48 + boost + float(scores.get("overall_orientation", 0.5)) * 0.2,
                    why=f"Ops stage {role['stage']} · {role['label']}",
                    label=role["label"],
                )
            )

        # C) Orientation-driven custom spine from business tokens
        for custom in self._custom_spines(business_text, industry_id, track, scores, hook):
            candidates.append(custom)

        # Dedup by normalized title
        candidates = self._dedupe(candidates)

        # Rank and select until coverage / target_n
        candidates.sort(key=lambda c: c["score"], reverse=True)
        selected = self._select(candidates, target_n, gaps, track)

        # Enrich client-facing fields — short diagnosis, not raw dump
        biz_one = re.sub(r"\s+", " ", (business_text or "").strip())
        if len(biz_one) > 160:
            biz_one = biz_one[:157].rsplit(" ", 1)[0] + "…"
        summary_biz = (
            f"We read your situation as: {biz_one} "
            f"Next: lock one track and ship a 14-day pilot metric."
        )
        ideas: list[dict[str, Any]] = []
        for rank, c in enumerate(selected, start=1):
            ideas.append(
                {
                    "rank": rank,
                    "id": c["id"],
                    "title": c["title"],
                    "track": c["track"],
                    "industry": industry_id,
                    "kind": c["kind"],
                    "role": c["role"],
                    "ops_stage": c["stage"],
                    "score": round(c["score"], 4),
                    "covers": list(c["covers"]),
                    "label": c.get("label") or c["role"],
                    "summary": summary_biz if rank == 1 else (
                        f"Complementary idea for operational success ({c['role']}): "
                        f"{c['title'][:120]}"
                    ),
                    "why_now": c["why"],
                    "why_in_portfolio": c.get("why_selected")
                    or "Closes a gap or stage in the operational-success path",
                    "deliverables_seed": self._deliverables(c["role"], c["track"]),
                    "specs_ready": specs_ready,
                    "is_primary": rank == 1,
                }
            )

        primary = ideas[0] if ideas else self._fallback_primary(
            industry_id, track, summary_biz, scores, specs_ready
        )
        if ideas and not ideas[0].get("is_primary"):
            ideas[0]["is_primary"] = True

        # Primary keeps legacy fields used elsewhere
        primary_out = {
            **primary,
            "alternative": ideas[1]["title"] if len(ideas) > 1 else primary.get("title"),
            "portfolio_count": len(ideas),
            "portfolio_roles": [i["role"] for i in ideas],
        }

        coverage = self._coverage_report(ideas, gaps, target_n)
        summary = (
            f"Idea portfolio: {len(ideas)} ideas (target {target_n}) · "
            f"primary=«{primary_out['title'][:50]}» · "
            f"gaps={list(gaps)} · stages={sorted({i['ops_stage'] for i in ideas})}"
        )

        return IdeaPortfolio(
            primary=primary_out,
            ideas=ideas,
            coverage=coverage,
            summary=summary,
        )

    # ── internals ────────────────────────────────────────────────────────

    def _hook_phrase(self, business: str) -> str:
        """Short client-readable hook (not a raw word salad)."""
        raw = (business or "").strip()
        if not raw:
            return "your operating geometry"
        # Prefer first clause under ~72 chars
        clause = re.split(r"[.!?\n;]", raw, maxsplit=1)[0].strip()
        clause = re.sub(r"\s+", " ", clause)
        if 24 <= len(clause) <= 72:
            return clause[0].lower() + clause[1:] if clause else "your operating geometry"
        if len(clause) > 72:
            cut = clause[:72].rsplit(" ", 1)[0]
            return (cut[0].lower() + cut[1:]) if cut else "your operating geometry"
        words = re.findall(r"[A-Za-zа-яА-ЯёЁ0-9%]{4,}", raw)
        stop = {
            "with", "that", "this", "from", "have", "need", "want", "about",
            "their", "your", "для", "который", "чтобы", "person", "people",
        }
        picked = [w for w in words if w.lower() not in stop][:4]
        if not picked:
            return "your operating geometry"
        return " ".join(picked)

    def _detect_gaps(self, scores: dict[str, Any], primary: str) -> set[str]:
        gaps: set[str] = set()
        mapping = {
            "product": float(scores.get("product_fit", 0.5)),
            "models": float(scores.get("model_fit", 0.5)),
            "promo": float(scores.get("promo_fit", 0.5)),
            "clarity": float(scores.get("readiness", scores.get("overall_orientation", 0.5))),
        }
        for k, v in mapping.items():
            if v < GAP_THRESHOLD:
                gaps.add(k)
        # Always treat primary weak fit as gap
        pkey = "promo" if primary == "promotion" else ("models" if primary == "models" else "product")
        if mapping.get(pkey, 1.0) < 0.62:
            gaps.add(pkey)
        if not gaps:
            gaps.add("ops")  # still expand ops path lightly
        return gaps

    def _target_count(self, gaps: set[str], track: str, scores: dict[str, Any]) -> int:
        # Exhaustive improvement: more gaps → more ideas
        n = MIN_IDEAS + len(gaps)
        if float(scores.get("overall_orientation", 0.5)) < 0.5:
            n += 1
        if track == "all":
            n += 1
        return max(MIN_IDEAS, min(MAX_IDEAS, n))

    def _seed_score(
        self, tr: str, primary: str, scores: dict[str, Any], idx: int
    ) -> float:
        fit_key = "model_fit" if tr == "models" else ("promo_fit" if tr == "promotion" else "product_fit")
        fit = float(scores.get(fit_key, 0.5))
        bonus = 0.15 if tr == primary else 0.0
        # slight preference for first seed
        return 0.4 + fit * 0.45 + bonus - idx * 0.02

    def _candidate(
        self,
        *,
        title: str,
        track: str,
        kind: str,
        role: str,
        stage: int,
        covers: tuple[str, ...],
        base_score: float,
        why: str,
        label: str | None = None,
    ) -> dict[str, Any]:
        hid = hashlib.sha1(f"{role}:{title}".encode("utf-8")).hexdigest()[:10]
        return {
            "id": f"idea_{role}_{hid}",
            "title": title,
            "track": track,
            "kind": kind,
            "role": role,
            "stage": stage,
            "covers": covers,
            "score": max(0.05, min(0.99, base_score)),
            "why": why,
            "label": label,
        }

    def _custom_spines(
        self,
        business: str,
        industry_id: str,
        track: str,
        scores: dict[str, Any],
        hook: str,
    ) -> list[dict[str, Any]]:
        out = []
        # Parameter / margin / churn heuristics
        low = business.lower()
        if any(k in low for k in ("margin", "rework", "utilization", "марж", "загрузк")):
            out.append(
                self._candidate(
                    title=f"Margin-defense product map for {hook}",
                    track="product",
                    kind="custom_spine",
                    role="margin_defense",
                    stage=1,
                    covers=("product", "ops", "clarity"),
                    base_score=0.62 + float(scores.get("product_fit", 0.5)) * 0.2,
                    why="Business text signals margin/rework/utilization pressure",
                    label="Margin defense spine",
                )
            )
        if any(k in low for k in ("churn", "arpu", "retention", "отток")):
            out.append(
                self._candidate(
                    title=f"Retention / ARPU lever pack for {hook}",
                    track="models",
                    kind="custom_spine",
                    role="retention_arpu",
                    stage=1,
                    covers=("models", "ops"),
                    base_score=0.6 + float(scores.get("model_fit", 0.5)) * 0.2,
                    why="Business text signals churn/ARPU pressure",
                    label="Retention lever",
                )
            )
        if any(k in low for k in ("cloud", "gpu", "latency", "aws", "gcp", "cost")):
            out.append(
                self._candidate(
                    title=f"Cost-to-latency product board for {hook}",
                    track="product",
                    kind="custom_spine",
                    role="cost_latency",
                    stage=2,
                    covers=("product", "models"),
                    base_score=0.58 + float(scores.get("product_fit", 0.5)) * 0.2,
                    why="Business text signals cloud/cost/latency",
                    label="Cost-latency board",
                )
            )
        if track == "promotion" or "promo" in low or "outreach" in low:
            out.append(
                self._candidate(
                    title=f"Reverse outreach angle kit for {industry_id}: {hook}",
                    track="promotion",
                    kind="custom_spine",
                    role="reverse_outreach",
                    stage=4,
                    covers=("promo", "ads"),
                    base_score=0.57 + float(scores.get("promo_fit", 0.5)) * 0.25,
                    why="Promotion / outreach path emphasized",
                    label="Reverse outreach",
                )
            )
        return out

    def _dedupe(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        out = []
        for it in items:
            key = re.sub(r"\s+", " ", it["title"].lower())[:90]
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out

    def _select(
        self,
        ranked: list[dict[str, Any]],
        target_n: int,
        gaps: set[str],
        primary: str,
    ) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        covered: set[str] = set()
        stages: set[int] = set()
        roles: set[str] = set()
        tracks_have: set[str] = set()

        def _take(c: dict[str, Any], reason: str) -> bool:
            if c["role"] in roles or len(selected) >= MAX_IDEAS:
                return False
            new_covers = set(c["covers"]) - covered
            item = {
                **c,
                "why_selected": reason
                or f"Ranked for ops success; closes {sorted(new_covers & gaps) or list(c['covers'])[:2]}",
            }
            selected.append(item)
            covered.update(c["covers"])
            # track name also counts as cover for gap logic
            if c["track"] == "promotion":
                covered.add("promo")
            elif c["track"] == "models":
                covered.add("models")
            else:
                covered.add("product")
            stages.add(c["stage"])
            roles.add(c["role"])
            tracks_have.add(c["track"])
            return True

        # Pass 0: guarantee track diversity (product + models + promotion when useful)
        must_tracks = ["product", "models", "promotion"]
        if primary in must_tracks:
            # primary first
            must_tracks = [primary] + [t for t in must_tracks if t != primary]
        for tr in must_tracks:
            if tr in tracks_have:
                continue
            for c in ranked:
                if c["track"] == tr and _take(c, f"Track diversity · {tr}"):
                    break

        # Pass 1: greedy by score with diversity bonus until target_n
        for c in ranked:
            if len(selected) >= max(target_n, MIN_IDEAS):
                break
            if c["role"] in roles:
                continue
            diversity = 0.0
            new_covers = set(c["covers"]) - covered
            if new_covers & gaps:
                diversity += 0.15
            if c["stage"] not in stages:
                diversity += 0.08
            if c["track"] not in tracks_have:
                diversity += 0.1
            boosted = {**c, "score": min(0.99, c["score"] + diversity)}
            _take(
                boosted,
                f"Ranked for ops success; closes {sorted(new_covers & gaps) or list(c['covers'])[:2]}",
            )

        # Pass 2: force remaining gaps
        for g in sorted(gaps):
            if g in covered or len(selected) >= MAX_IDEAS:
                continue
            for c in ranked:
                if c["role"] in roles:
                    continue
                hit = g in c["covers"] or (
                    g == "promo" and c["track"] == "promotion"
                ) or (g == "models" and c["track"] == "models") or (
                    g == "product" and c["track"] == "product"
                ) or (g == "clarity" and "clarity" in c["covers"])
                if hit and _take(c, f"Forced gap fill for «{g}»"):
                    break

        # Primary track ideas win rank-1 (ops success starts with the chosen track)
        def _sort_key(x: dict[str, Any]) -> tuple:
            track_boost = 1 if x.get("track") == primary else 0
            # Solution bridge is the intentional middle step after orient
            role_boost = 1 if x.get("role") == "solution_bridge" and primary == "product" else 0
            return (track_boost, role_boost, x.get("score") or 0)

        selected.sort(key=_sort_key, reverse=True)
        return selected[: max(MIN_IDEAS, min(MAX_IDEAS, max(target_n, len(selected))))]

    def _deliverables(self, role: str, track: str) -> list[str]:
        base = {
            "consultation": ["Constraint map", "Reality checklist", "Consult memo"],
            "solution_bridge": ["Orient→SKU map", "Pick list 1–3", "Handoff card"],
            "specs_writing": ["Spec pack", "Acceptance criteria", "Recursion log"],
            "predev_teammate": ["Pre-dev kit", "Promo asset list", "Handoff to surface"],
            "posts_surface": ["Post operator flow", "Script", "Cadence rules"],
            "replies_optimizer": ["Reply policy", "Quality bands", "Spend table"],
            "marketplace_lattice": ["Pattern fit", "Lattice access", "Adaptation notes"],
            "ads_weave": ["Ad phrase kit", "Signal map", "Angle card"],
            "decision_harness": ["Decision tree", "Interest zone", "Escalation"],
            "insight_chat": ["Chat module", "Insight prompts", "Human handoff"],
            "post_lead_topology": ["Action graph", "Post→lead path", "Zone map"],
            "client_geometry_deep": ["Advantage brief", "Architecture sketch", "Sequence"],
            "demand_heat_overlay": ["Heat markers", "Indicator board", "Overlay"],
        }
        if role in base:
            return base[role]
        if track == "promotion":
            return ["Angle card", "Message kit", "Channel fit"]
        if track == "models":
            return ["Teammate attach brief", "Necessity proof", "Pilot path"]
        return ["Parameter map", "Short breakdown", "Paid implement outline"]

    def _coverage_report(
        self, ideas: list[dict[str, Any]], gaps: set[str], target_n: int
    ) -> dict[str, Any]:
        tracks = sorted({i["track"] for i in ideas})
        stages = sorted({i["ops_stage"] for i in ideas})
        roles = [i["role"] for i in ideas]
        covered: set[str] = set()
        for i in ideas:
            covered |= set(i.get("covers") or [])
            tr = i.get("track")
            if tr == "promotion":
                covered.add("promo")
            elif tr == "models":
                covered.add("models")
            elif tr == "product":
                covered.add("product")
        return {
            "target_count": target_n,
            "actual_count": len(ideas),
            "tracks_covered": tracks,
            "ops_stages_covered": stages,
            "roles": roles,
            "gaps_detected": sorted(gaps),
            "gaps_addressed": sorted(gaps & covered),
            "gaps_remaining": sorted(gaps - covered),
            "exhaustive_enough": (
                len(ideas) >= MIN_IDEAS
                and len(stages) >= 2
                and len(tracks) >= 2
                and (
                    not gaps
                    or len(gaps & covered) >= max(1, (len(gaps) + 1) // 2)
                )
            ),
        }

    def _fallback_primary(
        self,
        industry_id: str,
        track: str,
        summary: str,
        scores: dict[str, Any],
        specs_ready: bool,
    ) -> dict[str, Any]:
        return {
            "rank": 1,
            "id": "idea_fallback",
            "title": f"Orientation-first product kit for {industry_id}",
            "track": track,
            "industry": industry_id,
            "kind": "fallback",
            "role": "consultation",
            "ops_stage": 1,
            "score": 0.5,
            "covers": ["product", "ops"],
            "label": "Fallback primary",
            "summary": summary,
            "why_now": f"fit={scores.get('overall_orientation', 0.5)}",
            "why_in_portfolio": "Fallback when portfolio empty",
            "deliverables_seed": ["Parameter map", "Breakdown", "Next steps"],
            "specs_ready": specs_ready,
            "is_primary": True,
            "portfolio_count": 1,
            "portfolio_roles": ["consultation"],
        }
