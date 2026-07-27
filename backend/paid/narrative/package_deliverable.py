"""
Consult + Tech Write — paid client deliverable synthesizer.

This is NOT a template wrapper around Market Unit blurbs.
It synthesizes a unique consultation + technical specification from the
full analysis graph (brief · numbers · OAE · decision · situation ·
function plane · hypotheses · memo-convert · portfolio).

Folders:
  10_consult_metareality/   consultation (unique to this brief)
  11_tech_write_specsforge/ technical specification (build-ready)
  12_package_result/        combined client pack (primary open file)
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import PROJECT_ROOT, WORKSPACE_ROOT, public_api_url
from backend.core.category_router import route_categories
from backend.core.industry_sanity import load_sanity, sanity_check_mechanism
from backend.core.market_units import PACKAGE_PRICING, market_unit_for
from backend.core.text_usability import (
    client_tokens_from_brief,
    polish_document,
    underhood_coverage,
)
from backend.paid.types import clamp01, safe_float


# ── Text hygiene ───────────────────────────────────────────────────────────

_JUNK = [
    r"Job-to-be-done покупателя размыт\.?",
    r"hub actor:\s*\w+",
    r"Operationally, this (situates|isolates|directs|tests):\s*",
    r"bound to \w+=[\d.]+",
    r"paid_score=[\d.]+",
    r"Block 18\b.*",
    r"\bVVI\b|\bRRC\b|\bER\b(?=\s|=)",
    r"orientation-fir\w*",
    r"meta\.paid_product_core\S*",
    r"chip_\w+",
    r"hyp_\w+",
    r"Founder-frame review:.*",
    r"Compose Terminal Agency overlay.*",
    r"Virtual Chips\.?",
    r"Function Engine plane.*",
    r"ConceptualEngine\.\w+",
    r"Mega Map hypotheses.*",
    r"System Design Library params.*",
    r"parallel orientation details over paid plane claims\.?",
    r"supply-chain vision\.?",
]


def _e(x: Any) -> str:
    return html.escape(str(x if x is not None else ""))


def _clean(s: Any) -> str:
    t = str(s or "")
    for pat in _JUNK:
        t = re.sub(pat, "", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" ;,.")
    return t


def _sentences(text: str) -> list[str]:
    text = _clean(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 12]


def _brief_claims(business: str) -> list[str]:
    """Pull concrete claims from the client brief — basis of unique diagnosis."""
    raw = (business or "").replace("\n", " ").strip()
    if not raw:
        return []
    # Split on . ; and "then"/connectors carefully
    chunks = re.split(r"(?<=[.!?])\s+|(?<=;)\s+", raw)
    claims = []
    for c in chunks:
        c = c.strip(" -•")
        if len(c) < 18:
            continue
        # Keep operational/economic claims, drop pure greetings
        claims.append(c if c.endswith((".", "!", "?")) else c + ".")
    # Also extract "X then Y" patterns as single claims if short brief
    if len(claims) < 2 and len(raw) > 40:
        claims = [raw if raw.endswith(".") else raw + "."]
    return claims[:8]


def _fmt_money(v: float) -> str:
    if abs(v) >= 1000:
        return f"${v:,.0f}"
    return f"${v:,.2f}"


def _fmt_pct(v: float) -> str:
    if v <= 1.0:
        return f"{v * 100:.0f}%"
    return f"{v:.1f}%"


def _human_industry(industry_id: str) -> str:
    return {
        "ai-agencies": "AI agency operations",
        "cloud-economy": "cloud / third-party API cost operations",
        "cost-engineering": "cost engineering",
        "chipmaking": "chip design / fab decision loops",
        "telecom": "telecom commercial operations",
        "device-assembly": "device assembly & configuration",
    }.get(industry_id, industry_id.replace("-", " "))


def _safe(s: str) -> str:
    s = re.sub(r"[^\w.\-]+", "_", (s or "").strip())[:80]
    return s or "ws"


# ── Number economics (tangible math from client inputs) ────────────────────

def _economics(nums: dict[str, float], business: str, industry_id: str) -> dict[str, Any]:
    util = safe_float(nums.get("utilization"), 0)
    rework = safe_float(nums.get("rework"), 0)
    gm = safe_float(nums.get("gross_margin"), 0)
    rev = safe_float(nums.get("monthly_revenue"), 0)
    cycle = safe_float(nums.get("cycle_days"), 0)
    churn = safe_float(nums.get("churn"), 0)
    arpu = safe_float(nums.get("arpu"), 0)

    out: dict[str, Any] = {"known": {}, "derived": [], "pressure_lines": []}
    if util:
        out["known"]["utilization"] = util
    if rework:
        out["known"]["rework"] = rework
    if gm:
        out["known"]["gross_margin"] = gm
    if rev:
        out["known"]["monthly_revenue"] = rev
    if cycle:
        out["known"]["cycle_days"] = cycle
    if churn:
        out["known"]["churn"] = churn
    if arpu:
        out["known"]["arpu"] = arpu

    # Derived cash stories (honest order-of-magnitude, labeled as estimate)
    if rev and rework and rework <= 1:
        # Rough: rework burns a share of delivery capacity → revenue at risk band
        rework_drag = rev * rework * 0.45  # not full revenue; partial drag estimate
        out["derived"].append(
            {
                "id": "rework_drag",
                "label": "Monthly rework drag (order-of-magnitude)",
                "value": rework_drag,
                "text": (
                    f"At ~{_fmt_money(rev)}/mo revenue and {_fmt_pct(rework)} rework, "
                    f"a conservative drag band is ~{_fmt_money(rework_drag)}/mo "
                    f"(not lost revenue 1:1 — capacity recycled into redo work)."
                ),
            }
        )
        out["pressure_lines"].append(
            f"Rework at {_fmt_pct(rework)} is eating delivery capacity — "
            f"rough monthly drag ~{_fmt_money(rework_drag)}."
        )

    if rev and util and util <= 1:
        util_gap = max(0.0, 0.75 - util)  # gap to a healthy 75% band
        if util_gap > 0.02:
            upside = rev * (util_gap / max(util, 0.15)) * 0.35
            out["derived"].append(
                {
                    "id": "util_gap",
                    "label": "Utilization gap to 75% band",
                    "value": util_gap,
                    "text": (
                        f"Utilization {_fmt_pct(util)} vs a healthy ~75% band "
                        f"(gap {_fmt_pct(util_gap)}). Closing even part of that gap "
                        f"is worth roughly {_fmt_money(upside)}/mo in recovered capacity value "
                        f"(estimate, not a forecast)."
                    ),
                }
            )
            out["pressure_lines"].append(
                f"Utilization {_fmt_pct(util)} leaves a clear capacity gap before 75%."
            )

    if gm and gm <= 1 and gm < 0.4:
        out["pressure_lines"].append(
            f"Gross margin {_fmt_pct(gm)} is tight for custom delivery — "
            f"every free discovery hour hits harder than on a 50%+ shop."
        )
    if cycle and cycle > 14:
        out["pressure_lines"].append(
            f"Cycle time ~{cycle:.0f} days: long loops amplify scope creep and rework compounding."
        )
    if churn and churn <= 1 and churn >= 0.05:
        out["pressure_lines"].append(
            f"Churn {_fmt_pct(churn)} means acquisition spend is leaking out the back."
        )

    # Brief-derived qualitative economics
    b = business.lower()
    if "free discovery" in b or "free discov" in b:
        out["pressure_lines"].append(
            "Free discovery is named in the brief — unpaid scoping is a designed margin leak, not an accident."
        )
    if "scope explode" in b or "scope creep" in b or "scope explodes" in b:
        out["pressure_lines"].append(
            "Scope explosion after discovery is explicit — packaging and gates are under-specified."
        )
    if "retainer" in b and ("dilut" in b or "chaos" in b):
        out["pressure_lines"].append(
            "Retainers are diluting delivery focus — productized attach will beat more retainer hours."
        )
    if any(w in b for w in ("api", "token", "openai", "llm")) and industry_id == "cloud-economy":
        out["pressure_lines"].append(
            "Third-party API / token spend is in the brief — unit cost of intelligence is a primary lever."
        )

    if not out["pressure_lines"]:
        out["pressure_lines"].append(
            "Numbers and brief are thin on cash mechanics — consultation still maps structure; "
            "fill utilization / margin / rework / revenue to harden the money story."
        )
    return out


# ── Core synthesizer ───────────────────────────────────────────────────────

class ConsultationSynthesizer:
    """Build unique consultation + tech spec from analysis graph."""

    def synthesize(
        self,
        *,
        industry_id: str,
        business: str,
        idea_title: str,
        client_name: str,
        nums: dict[str, float],
        paid: dict[str, Any],
        memo_convert: dict[str, Any],
        market_unit: dict[str, Any],
        oae: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        demo_idea: dict[str, Any] | None = None,
        demo_ideas: list[dict[str, Any]] | None = None,
        narrative: dict[str, Any] | None = None,
        offer: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        oae = oae or {}
        decision = decision or {}
        demo_idea = demo_idea or {}
        demo_ideas = demo_ideas or []
        narrative = narrative or {}
        offer = offer or {}
        pkg = paid.get("package") or {}
        sm = paid.get("situation_metrics") or paid.get("business_metrics") or {}
        fn = paid.get("function_engine") or {}
        hyp = paid.get("hypotheses") or {}
        must = paid.get("must_ask") or paid.get("clarifying_questions") or {}

        name = (client_name or "").strip() or "there"
        claims = _brief_claims(business)
        econ = _economics(nums, business, industry_id)
        product, product_line = self._pick_product(
            market_unit=market_unit,
            industry_id=industry_id,
            business=business,
            demo_ideas=demo_ideas,
            demo_idea=demo_idea or {},
        )

        # Primary oriented spine from demo / OAE — humanized
        spine = _clean(
            demo_idea.get("title")
            or idea_title
            or (oae.get("reduced_to_request") or {}).get("primary_idea")
            or product
        )
        if any(
            x in spine.lower()
            for x in (
                "verdictlattice",
                "pragma",
                "zoneweave",
                "opticprism",
                "solution bridge",
            )
        ):
            spine = product
        # Strip internal scaffold prefixes from spine shown to clients
        spine = re.sub(
            r"^(Solution Bridge:\s*convert orientation into 1–3 pickable SKUs for\s*)",
            "",
            spine,
            flags=re.I,
        ).strip() or product

        # Secondary surfaces (portfolio) — unique options, not a SKU dump
        surfaces = self._surfaces(demo_idea, demo_ideas, oae, product)

        # Mechanism of change — what actually has to change in THEIR shop
        mechanism = self._mechanism(
            industry_id=industry_id,
            business=business,
            claims=claims,
            econ=econ,
            spine=spine,
            product=product,
            product_line=product_line,
            top_lever=str(pkg.get("top_lever") or fn.get("top_lever") or ""),
            surfaces=surfaces,
        )

        # Diagnosis (once) — never reused as "situation" dump
        diagnosis = self._diagnosis(
            name=name,
            industry_id=industry_id,
            claims=claims,
            econ=econ,
            mechanism=mechanism,
        )

        # Situation (different angle) — how the system behaves now
        situation = self._situation(
            claims=claims,
            econ=econ,
            sm=sm,
            decision=decision,
            business=business,
        )

        # What we recommend (why THIS, not a catalog)
        recommendation = self._recommendation(
            product=product,
            product_line=product_line,
            spine=spine,
            surfaces=surfaces,
            mechanism=mechanism,
            econ=econ,
            industry_id=industry_id,
            offer=offer,
            pkg=pkg,
        )

        # 14-day plan unique to numbers + claims
        action_notes = self._action_notes(
            econ=econ,
            mechanism=mechanism,
            product=product,
            claims=claims,
            must=must,
            industry_id=industry_id,
        )

        # Constraints / engagement frame
        constraints = self._constraints(
            industry_id=industry_id,
            product=product,
            econ=econ,
            must=must,
            pkg=pkg,
            founder_error=bool(pkg.get("founder_error_suspected")),
        )

        # Technical specification (tangible)
        tech = self._tech_spec(
            industry_id=industry_id,
            business=business,
            name=name,
            spine=spine,
            product=product,
            product_line=product_line,
            mechanism=mechanism,
            econ=econ,
            claims=claims,
            surfaces=surfaces,
            memo_convert=memo_convert,
            fn=fn,
            demo_idea=demo_idea,
            must=must,
        )

        # Opening letter
        opening = self._opening(name, industry_id, claims, econ, mechanism)

        bundle = PACKAGE_PRICING["consult_techwrite_bundle"]
        consult_p = PACKAGE_PRICING["metareality_consult"]
        tech_p = PACKAGE_PRICING["specsforge_tech_write"]

        # What they got — short evidence list (no 14-day program line)
        got = [
            f"Diagnosis from your brief"
            + (f" ({len(claims)} claims)" if claims else ""),
            (
                "Cash/capacity reading: " + econ["pressure_lines"][0]
                if econ.get("pressure_lines")
                else "Structure map ready when you add numbers"
            ),
            f"Change mechanism: {mechanism['title']}",
            f"Product choice: {product}",
            "Short notes for next steps + recommended pilot",
        ]

        # Category router + industry sanity (judgment check)
        sanity = sanity_check_mechanism(industry_id, mechanism["title"], business)
        cat = route_categories(
            business=business,
            industry_id=industry_id,
            nums=nums,
            sanity_hints=sanity,
            lang="en",
        )
        # How module map helps THIS product (owner change-readiness)
        module_help = self._module_map_help(
            product=product,
            mechanism=mechanism,
            module_map=list(sanity.get("module_map") or []),
            track=(cat.get("primary") or "ops"),
            industry_id=industry_id,
            variant=sanity.get("variant"),
        )

        # Pilot price by track (public funnel)
        pilot_by_track = {"ops": 690, "product": 790, "promotion": 490}
        pilot_usd = pilot_by_track.get(cat.get("primary") or "ops", 690)
        pilot_offer = {
            "track": cat.get("primary") or "ops",
            "price_usd": pilot_usd,
            "product": product,
            "title": f"Recommended pilot · {product}",
            "description_path": "10_consult_metareality/CONSULTATION.html",
            # Absolute URL filled in PackageDeliverableWriter.write once request_id is known
            "description_url_hint": "",
        }

        # Usability polish — no duplicate water, simpler clauses, dry math limit
        tokens = client_tokens_from_brief(business)
        polished, usability = polish_document(
            {
                "opening": opening,
                "diagnosis": diagnosis,
                "situation": situation,
            },
            client_tokens=tokens,
            max_money_per_section=1,
        )
        opening = polished.get("opening") or opening
        diagnosis = polished.get("diagnosis") or diagnosis
        situation = polished.get("situation") or situation

        underhood = underhood_coverage(
            {
                "business": business,
                "nums": nums,
                "demo_idea": demo_idea,
                "demo_ideas": demo_ideas,
                "oae": oae,
                "decision": decision,
                "paid": paid,
                "memo_convert": memo_convert,
                "market_unit": market_unit,
                "narrative": narrative,
            }
        )

        doc = {
            "client_name": name,
            "industry_id": industry_id,
            "industry_label": _human_industry(industry_id),
            "opening": opening,
            "diagnosis": diagnosis,
            "situation": situation,
            "mechanism": mechanism,
            "recommendation": recommendation,
            "action_notes": action_notes,
            "plan_14": action_notes,  # alias for older callers/tests
            "constraints": constraints,
            "tech": tech,
            "got_today": got,
            "module_help": module_help,
            "pilot_offer": pilot_offer,
            "econ": econ,
            "claims": claims,
            "spine": spine,
            "product": product,
            "product_line": product_line,
            "surfaces": surfaces,
            "bundle": bundle,
            "consult_p": consult_p,
            "tech_p": tech_p,
            "brief_clip": (business or "").strip()[:500],
            "paid_score": safe_float(paid.get("paid_score") or pkg.get("paid_score")),
            "package_status": pkg.get("status") or paid.get("status") or "",
            "category_router": cat,
            "sanity": sanity,
            "usability": usability,
            "underhood_coverage": underhood,
            "lang": "en",
        }
        doc["tangibility"] = self.score_tangibility(doc, business=business, nums=nums)
        doc["ru"] = self._ru_pack(doc)
        return doc

    # ── Section builders ─────────────────────────────────────────────────

    def _surfaces(
        self,
        demo_idea: dict[str, Any],
        demo_ideas: list[dict[str, Any]],
        oae: dict[str, Any],
        product: str,
    ) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        seen: set[str] = set()
        fly = (oae.get("reduced_to_request") or {}).get("double_bottom_flyouts") or []
        for title in fly:
            t = _clean(title)
            if not t or t.lower() in seen:
                continue
            seen.add(t.lower())
            out.append({"title": t, "role": "adjacent option from analysis"})
        for idea in demo_ideas[:6]:
            t = _clean(idea.get("title") or "")
            if not t or t.lower() in seen:
                continue
            if any(
                x in t.lower()
                for x in ("verdictlattice", "pragma", "zoneweave", "opticprism")
            ):
                continue
            seen.add(t.lower())
            role = str(idea.get("role") or idea.get("label") or "portfolio")
            out.append({"title": t, "role": role.replace("_", " ")})
        if product and product.lower() not in seen:
            out.insert(0, {"title": product, "role": "primary product attach"})
        # Prefer diversity: different roles first
        ranked: list[dict[str, str]] = []
        roles_used: set[str] = set()
        for item in out:
            role = (item.get("role") or "")[:24]
            if role in roles_used and len(ranked) >= 2:
                continue
            roles_used.add(role)
            ranked.append(item)
        for item in out:
            if item not in ranked:
                ranked.append(item)
        return ranked[:5]

    def _mechanism(
        self,
        *,
        industry_id: str,
        business: str,
        claims: list[str],
        econ: dict[str, Any],
        spine: str,
        product: str,
        product_line: str,
        top_lever: str,
        surfaces: list[dict[str, str]],
    ) -> dict[str, Any]:
        b = business.lower()
        lever = (top_lever or "clarity").replace("_", " ")

        # Industry + brief specific mechanism titles
        if industry_id == "ai-agencies":
            if "free discovery" in b or "scope" in b:
                title = "Kill unpaid discovery → sell a paid orientation SKU → attach Teammate"
                steps = [
                    "Stop free discovery as the default door. Replace with a paid orientation / map session that produces a pickable SKU list.",
                    f"Use the oriented spine «{spine}» as the session output — not a free proposal marathon.",
                    f"Attach **{product}** only after the buyer sees a one-page payback sketch (buyer fin model), not after more demos.",
                    "Gate retainers: every retainer hour maps to a closed acceptance item or it does not start.",
                ]
                proof = [
                    "Free discovery hours / week → target near zero on new logos",
                    "Rework % on projects that passed paid orientation vs those that did not",
                    "Utilization and gross margin after 2–3 closed cycles",
                ]
            else:
                title = f"Ops geometry first, then {product} attach"
                steps = [
                    f"Map delivery geometry before building more agents: {spine}.",
                    f"Pick one attach surface for {product} ({product_line}).",
                    f"Turn lever «{lever}» with one metric owner — not three parallel initiatives.",
                    "Close one pilot with written acceptance before expanding scope.",
                ]
                proof = ["Utilization", "Rework %", "Gross margin", "Cycle days"]
        elif industry_id == "cloud-economy":
            title = "Collapse third-party API unit cost without killing quality"
            steps = [
                "Inventory every third-party API / token path that touches a billable unit of work.",
                "Route high-volume repetitive work to an Expert / local path; keep paid APIs for high-judgment steps only.",
                f"Productize the result as **{product}**: {product_line}.",
                "Publish a before/after unit-cost table the founder can defend to a co-founder.",
            ]
            proof = ["API $ per unit of work", "Quality band (pass rate)", "Latency under SLA"]
        elif industry_id == "cost-engineering":
            title = "Cut waste parameters; keep capability; resell the map"
            steps = [
                "Run a one-page parameter waste map on the live system (not a generic checklist).",
                "Mark parameters that spend money without protecting a capability metric.",
                f"Package the method as **{product}** for the broad audience that hires cost engineers.",
                "Prove $ saved per cut parameter with one before/after snapshot.",
            ]
            proof = ["Parameter waste $", "Capability metric unchanged", "Rework cost"]
        elif industry_id == "chipmaking":
            title = "Make design-loop voids and yield risk explicit before tapeout money"
            steps = [
                f"Lock a void index on the current loop: «{spine}».",
                f"Run **{product}** as a decision twin before the next expensive gate.",
                "Separate NRE spend decisions from iteration hope — written gate criteria.",
            ]
            proof = ["Void index", "NRE vs iteration spend", "Gate pass/fail criteria"]
        elif industry_id == "telecom":
            title = "Translate ARPU/churn/SLA into SKUs operators can sell"
            steps = [
                f"Write SLA-native SKU language for «{spine}» in buyer words (not a spreadsheet dump).",
                f"Ship {product} as the commercial surface on one plan family first.",
                "Tie one promo motion to a single retention or ARPU lever with an owner.",
            ]
            proof = ["ARPU", "Churn", "SLA breach rate", "SKU attach rate"]
        else:
            title = f"Orient → pick → attach {product}"
            steps = [
                f"Orient the operation around «{spine}».",
                f"Attach **{product}** with written acceptance.",
                f"Instrument lever «{lever}» with one owner.",
            ]
            proof = list((econ.get("known") or {}).keys()) or ["cycle time", "margin"]

        # Inject money lines into steps when available
        if econ.get("derived"):
            steps.append(
                "Use the cash/capacity reading in this pack as the pilot scoreboard — not vanity dashboards."
            )

        return {
            "title": title,
            "steps": steps,
            "proof_metrics": proof,
            "lever": lever,
            # Client-facing contrast only (no *markdown*, no SKU-catalog lecture)
            "why_this_case": (
                f"Why this, for your case: the oriented model and the pressure lines "
                f"point to «{title}» — not to a full catalog tour."
            ),
        }

    def _diagnosis(
        self,
        *,
        name: str,
        industry_id: str,
        claims: list[str],
        econ: dict[str, Any],
        mechanism: dict[str, Any],
    ) -> str:
        who = name if name != "there" else "You"
        lines = [
            f"{who} — diagnosis for this brief only.",
            "",
            f"**Domain:** {_human_industry(industry_id)}.",
            "",
            "**From your words:**",
        ]
        if claims:
            for c in claims:
                lines.append(f"- {c}")
        else:
            lines.append("- (Brief was short — diagnosis is provisional until you add operating detail.)")

        lines += ["", "**What the numbers say:**"]
        if econ.get("derived"):
            for d in econ["derived"]:
                lines.append(f"- {d['text']}")
        # Qualitative pressure only (skip lines already covered by derived cash math)
        for p in econ.get("pressure_lines") or []:
            pl = p.lower()
            if econ.get("derived") and any(
                k in pl for k in ("rework at", "utilization ", "drag ~", "capacity gap")
            ):
                continue
            lines.append(f"- {p}")

        lines += [
            "",
            f"**Therefore the change mechanism is:** {mechanism['title']}.",
        ]
        return "\n".join(lines)

    def _situation(
        self,
        *,
        claims: list[str],
        econ: dict[str, Any],
        sm: dict[str, Any],
        decision: dict[str, Any],
        business: str,
    ) -> str:
        """Different from diagnosis: how work moves today, who holds the bottleneck."""
        parts: list[str] = []
        parts.append("How work moves today (from your brief and metrics):")

        # Reconstruct flow from claims
        flow_bits = []
        for c in claims:
            cl = c.lower()
            if any(w in cl for w in ("discovery", "scope", "retainer", "deliver", "client", "rework", "api", "token", "yield", "churn", "sla", "station")):
                flow_bits.append(c.rstrip("."))
        if flow_bits:
            parts.append("**Observed loop:** " + " → ".join(flow_bits[:4]) + ".")
        else:
            parts.append(
                f"**Observed loop:** {(_clean(business)[:220] + '…') if len(business) > 220 else _clean(business)}"
            )

        # Bottleneck from economics
        if econ.get("known", {}).get("rework", 0) >= 0.15:
            parts.append(
                f"**Bottleneck candidate:** rework at {_fmt_pct(econ['known']['rework'])} — "
                "work re-enters the same stations instead of exiting clean."
            )
        elif econ.get("known", {}).get("utilization", 0) and econ["known"]["utilization"] < 0.6:
            parts.append(
                f"**Bottleneck candidate:** under-loaded utilization "
                f"({_fmt_pct(econ['known']['utilization'])}) while margin stays tight — "
                "sales or packaging, not pure labor shortage."
            )
        elif econ.get("known", {}).get("churn", 0) >= 0.05:
            parts.append(
                f"**Bottleneck candidate:** churn {_fmt_pct(econ['known']['churn'])} — "
                "retention is cheaper than another acquisition wave if the product SKU is clearer."
            )
        else:
            cov = sm.get("numbers_coverage")
            if cov is not None:
                parts.append(
                    f"**Metric coverage on this run:** {safe_float(cov):.0%} of expected operating numbers present."
                )

        # Decision mode — only if it helps the client
        mode = decision.get("active_mode")
        if mode and mode != "scoring":
            parts.append(
                f"**Processing note:** the system routed this case into «{mode.replace('_', ' ')}» mode — "
                "more generative refinement than pure scoring — treat recommendations as directional until you lock one pilot metric."
            )

        return "\n\n".join(parts)

    def _recommendation(
        self,
        *,
        product: str,
        product_line: str,
        spine: str,
        surfaces: list[dict[str, str]],
        mechanism: dict[str, Any],
        econ: dict[str, Any],
        industry_id: str,
        offer: dict[str, Any],
        pkg: dict[str, Any],
    ) -> dict[str, Any]:
        # Section 4: product only — case "why" lives once in section 3
        why = [
            f"Primary product: {product} — {product_line}.",
        ]
        # Ranked alternatives with case rationale
        alts = []
        for s in surfaces:
            if s["title"].lower() == product.lower():
                continue
            alts.append(
                {
                    "title": s["title"],
                    "when": (
                        f"Use if the primary attach stalls — role in portfolio: {s['role']}. "
                        f"Still subordinate to mechanism «{mechanism['title']}»."
                    ),
                }
            )
        # Money frame for buyer (if agency)
        buyer_proof = None
        if industry_id == "ai-agencies" and econ.get("derived"):
            buyer_proof = (
                "Before you sell Terminal Teammate outward, draw the buyer's payback on one page: "
                "their rework/utilization/margin → hours saved → price of attach. "
                "That fin model is the promotion for ops-efficiency buyers."
            )
        elif industry_id == "cloud-economy":
            buyer_proof = (
                "Promotion is an event that reviews what already ships, then points to Expert — "
                "not a generic FinOps webinar."
            )

        return {
            "why": why,
            "alternatives": alts[:3],
            "buyer_proof": buyer_proof,
            "mechanism_title": mechanism["title"],
            "status_note": (
                f"Analysis package status: {pkg.get('status') or 'n/a'}; "
                f"readiness {safe_float(pkg.get('paid_readiness')):.0%}."
                if pkg
                else ""
            ),
        }

    def _action_notes(
        self,
        *,
        econ: dict[str, Any],
        mechanism: dict[str, Any],
        product: str,
        claims: list[str],
        must: dict[str, Any],
        industry_id: str,
    ) -> list[str]:
        """Short next-step notes (not a full 14-day program dump)."""
        proof = mechanism.get("proof_metrics") or ["pilot metric"]
        p0 = proof[0] if proof else "pilot metric"
        step1 = (
            mechanism["steps"][0]
            if mechanism.get("steps")
            else f"Start the first move on «{mechanism.get('title')}»."
        )
        notes = [
            f"Confirm the diagnosis in one short paragraph with your team.",
            f"Put a simple weekly check on: {', '.join(proof[:3])}.",
            f"First move: {step1}",
            f"Attach {product} on one live lane only — not a company-wide rollout.",
            f"Keep one before/after note on {p0}; then decide pilot go / no-go.",
        ]
        return notes

    def _constraints(
        self,
        *,
        industry_id: str,
        product: str,
        econ: dict[str, Any],
        must: dict[str, Any],
        pkg: dict[str, Any],
        founder_error: bool,
    ) -> list[str]:
        cs = [
            f"This consultation is scoped to {_human_industry(industry_id)} and the mechanism named above — not unlimited strategy.",
            f"Primary product attach under discussion: {product}.",
            "No guaranteed revenue, market size, or ROI. Estimates from your numbers are labeled as order-of-magnitude.",
            "Tech specification becomes binding only after you accept the consultation frame (this document).",
            "Human locks final price and legal SoW.",
        ]
        if econ.get("known"):
            ks = ", ".join(f"{k}={_fmt_pct(v) if v <= 1 and 'revenue' not in k and 'day' not in k else ( _fmt_money(v) if 'revenue' in k else v)}" for k, v in list(econ['known'].items())[:5])
            cs.append(f"Numbers used in this pack: {ks}. Wrong inputs → wrong cash story; correct them and re-run.")
        must_n = int(must.get("must_count") or 0)
        if must_n:
            cs.append(f"{must_n} must-ask items remain open — do not treat Full Package as closed.")
        if founder_error:
            cs.append(
                "Founder-frame check: at least one analysis path flagged a possible framing error — "
                "re-read the mechanism with a skeptical co-founder before spending implement budget."
            )
        return cs

    def _tech_spec(
        self,
        *,
        industry_id: str,
        business: str,
        name: str,
        spine: str,
        product: str,
        product_line: str,
        mechanism: dict[str, Any],
        econ: dict[str, Any],
        claims: list[str],
        surfaces: list[dict[str, str]],
        memo_convert: dict[str, Any],
        fn: dict[str, Any],
        demo_idea: dict[str, Any],
        must: dict[str, Any],
    ) -> dict[str, Any]:
        """Build-ready technical document — unique to this case."""
        fn_title = _clean(
            ((memo_convert.get("analog_engine") or {}).get("function_meta") or {}).get(
                "title"
            )
            or fn.get("top_lever")
            or mechanism["title"]
        )
        out_key = (
            (memo_convert.get("analog_engine") or {}).get("function_meta") or {}
        ).get("out") or "shippable_attach"

        # Work packages from mechanism steps
        wps = []
        for i, step in enumerate(mechanism.get("steps") or [], 1):
            wps.append(
                {
                    "id": f"WP{i}",
                    "title": f"Work package {i}",
                    "description": step,
                    "owner": "Client ops lead" if i <= 2 else f"{product} implementer",
                    "output": (
                        mechanism["proof_metrics"][min(i - 1, len(mechanism["proof_metrics"]) - 1)]
                        if mechanism.get("proof_metrics")
                        else "Written artifact"
                    ),
                }
            )

        # Interfaces / inputs-outputs
        interfaces = [
            {
                "from": "Client brief + numbers",
                "to": "Consultation frame (this package)",
                "contract": "Claims listed; numbers versioned; acceptance of diagnosis",
            },
            {
                "from": "Consultation frame",
                "to": "Technical specification (this section)",
                "contract": "Mechanism locked; WPs ordered; proof metrics named",
            },
            {
                "from": "Technical specification",
                "to": f"{product} implement / pre-dev",
                "contract": "DoD checklist green; no open must-ask that blocks scope",
            },
        ]

        # Acceptance — case specific
        acceptance = [
            f"Diagnosis paragraph accepted by {name if name != 'there' else 'client owner'} without unresolved contradictions to the brief.",
            f"Mechanism «{mechanism['title']}» is the only active change program for the next 14 days (no parallel pet projects).",
            f"Scoreboard live for: {', '.join(mechanism.get('proof_metrics') or ['pilot metric'])}.",
            f"One live-lane attach plan for **{product}** exists in writing (who, which client/path, by when).",
        ]
        if econ.get("derived"):
            acceptance.append(
                f"Cash/capacity reading reviewed: {econ['derived'][0]['label']} — accepted or replaced with client’s own calc."
            )
        if claims:
            acceptance.append(
                f"At least {min(3, len(claims))} brief claims explicitly addressed in the implement plan (not ignored)."
            )

        # Definition of done
        dod = [
            "Consultation MD/HTML signed off (email OK).",
            "This tech spec filed in workspace `11_tech_write_specsforge` without open blockers.",
            f"WP1 and WP2 complete with artifacts linked.",
            f"Pilot metric baseline recorded for {mechanism.get('proof_metrics', ['n/a'])[0]}.",
            "Go / no-go on expand to pilot written in one sentence.",
        ]

        # Non-goals
        non_goals = [
            "Full company reorg",
            "Guaranteed revenue uplift",
            "Building every portfolio idea in parallel",
            "Replacing legal SoW / tax / employment advice",
        ]
        if industry_id == "ai-agencies":
            non_goals.append("Training a new foundation model or multi-agent swarm as the first move")
        if industry_id == "cloud-economy":
            non_goals.append("Migrating all workloads off cloud in one step")

        # Data dictionary from known numbers
        data_dict = []
        for k, v in (econ.get("known") or {}).items():
            data_dict.append(
                {
                    "field": k,
                    "value": v,
                    "use": "Pilot scoreboard input" if k in str(mechanism.get("proof_metrics")).lower() or True else "Context",
                }
            )

        # Deliverables from demo idea seeds if present
        seeds = list(demo_idea.get("deliverables_seed") or [])
        deliverables = seeds or [
            "Consultation frame",
            "Technical specification",
            "Pilot scoreboard",
            f"{product} attach plan",
        ]

        return {
            "title": f"Technical specification — {product} / {mechanism['title']}",
            # Keep objective short and human — no internal function codes for client
            "objective": (
                f"Implement the accepted mechanism «{mechanism['title']}» "
                f"with primary product {product} ({product_line})."
            ),
            "scope_in": [
                mechanism["title"],
                f"Product attach: {product}",
                "Pilot scoreboard",
                "Written acceptance and DoD",
            ],
            "scope_out": non_goals,
            "work_packages": wps,
            "interfaces": interfaces,
            "acceptance": acceptance,
            "definition_of_done": dod,
            "deliverables": deliverables,
            "data_dictionary": data_dict,
            "risks": self._tech_risks(industry_id, econ, must),
            "open_questions": self._open_questions(must, claims),
        }

    def _tech_risks(
        self, industry_id: str, econ: dict[str, Any], must: dict[str, Any]
    ) -> list[str]:
        risks = [
            "Wrong number inputs invalidate cash readings — re-run after correction.",
            "Running multiple mechanisms at once will destroy the 14-day proof.",
        ]
        if econ.get("known", {}).get("rework", 0) >= 0.2:
            risks.append(
                "High rework means implement capacity is fake until a gate kills redo loops."
            )
        if int(must.get("must_count") or 0) > 0:
            risks.append("Open must-ask items can silently change scope mid-pilot.")
        if industry_id == "ai-agencies":
            risks.append(
                "Sales may keep promising free discovery while ops tries to kill it — leadership must align."
            )
        return risks

    def _open_questions(self, must: dict[str, Any], claims: list[str]) -> list[str]:
        qs = []
        for q in (must.get("questions") or must.get("must") or [])[:5]:
            if isinstance(q, dict):
                qs.append(_clean(q.get("text") or q.get("question") or q.get("prompt") or ""))
            else:
                qs.append(_clean(q))
        qs = [q for q in qs if q and len(q) > 10]
        if not qs:
            qs = [
                "Who owns the pilot metric week-to-week?",
                "Which single live lane gets the product attach first?",
                "What will you stop doing (explicitly) during the 14 days?",
            ]
        return qs[:6]

    def _opening(
        self,
        name: str,
        industry_id: str,
        claims: list[str],
        econ: dict[str, Any],
        mechanism: dict[str, Any],
    ) -> str:
        greet = f"{name}," if name != "there" else "Hello,"
        claim_n = len(claims)
        money = econ["derived"][0]["text"] if econ.get("derived") else econ["pressure_lines"][0]
        return (
            f"{greet}\n\n"
            f"Free orientation for {_human_industry(industry_id)}, "
            f"built from your brief"
            f"{f' ({claim_n} claims)' if claim_n else ''} "
            f"and your numbers.\n\n"
            f"Headline: {mechanism['title']}.\n\n"
            f"Cash reading: {money}\n\n"
            f"Below: diagnosis, how work moves today, the change mechanism, "
            f"the product choice, short notes for next steps, and a recommended pilot."
        )

    def _pick_product(
        self,
        *,
        market_unit: dict[str, Any],
        industry_id: str,
        business: str,
        demo_ideas: list[dict[str, Any]],
        demo_idea: dict[str, Any],
    ) -> tuple[str, str]:
        """
        Choose a concrete product for this brief (diversity + accuracy).
        Prefer Market Unit primary, then portfolio titles that match brief tokens.
        """
        base = (market_unit.get("product") or {}).get("name") or "Primary product"
        line = _clean((market_unit.get("product") or {}).get("one_liner") or base)
        text = (business or "").lower()
        # Industry-specific overrides from brief signals
        overrides = {
            "ai-agencies": [
                (("free discovery", "rework", "retainer"), "Terminal Teammate",
                 "Ops console that raises delivery efficiency without agent chaos"),
                (("content", "token", "creative"), "Expert",
                 "Cut API/token burn while keeping creative quality"),
            ],
            "cloud-economy": [
                (("api", "token", "openai", "anthropic"), "Expert",
                 "Cut third-party API spend while holding quality"),
                (("finops", "aws", "gpu", "egress"), "CloudForge Precision Optimizer",
                 "Spend and placement under product context"),
            ],
            "telecom": [
                (("arpu", "churn", "sla", "mvno"), "SLA-native SKU Builder",
                 "SKUs that speak carrier SLA and QoS"),
                (("care", "support", "intent"), "Linguistic Signal Weaver",
                 "Intent signal weave for care and tariffs"),
            ],
            "chipmaking": [
                (("yield", "tapeout", "nre"), "Yield Geometry Twin",
                 "Conceptual twin before tapeout decisions"),
            ],
            "cost-engineering": [
                (("parameter", "waste", "tolerance"), "Parameter Void Scanner",
                 "Cut waste parameters without cutting capability"),
            ],
            "device-assembly": [
                (("station", "rework", "config"), "Config product workflow",
                 "Assembly → setup → guided config as a product"),
            ],
        }
        for keys, name, one in overrides.get(industry_id, []):
            if any(k in text for k in keys):
                return name, one
        # Portfolio pick: first non-jargon idea with brief token hit
        for idea in demo_ideas[:6]:
            title = _clean(idea.get("title") or "")
            if not title or any(
                x in title.lower()
                for x in ("verdictlattice", "pragma", "zoneweave", "solution bridge")
            ):
                continue
            toks = set(re.findall(r"[a-z]{4,}", title.lower()))
            brief_toks = set(re.findall(r"[a-z]{4,}", text))
            if len(toks & brief_toks) >= 2:
                return title[:80], line
        return base, line

    def _module_map_help(
        self,
        *,
        product: str,
        mechanism: dict[str, Any],
        module_map: list[str],
        track: str,
        industry_id: str,
        variant: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Explain how change-owner modules (M1…Mn) support the proposed product.
        Improves accuracy: modules are product-path steps, not a generic checklist.
        """
        if not module_map:
            module_map = [
                "M1 Brief lock",
                "M2 Metric scoreboard",
                f"M3 First move on «{mechanism.get('title') or product}»",
                f"M4 Attach {product} on one lane",
                "M5 Pilot go / no-go",
            ]
        # Tie each module to the product path in plain language
        tied = []
        for i, m in enumerate(module_map[:6]):
            if i == 0:
                why = f"keeps the brief that justifies {product} stable"
            elif i == 1:
                why = f"proves whether {product} moved the right number"
            elif i == len(module_map[:6]) - 1:
                why = f"decides if {product} expands after the pilot"
            else:
                why = f"prepares the business so {product} can attach without chaos"
            tied.append({"module": m, "helps_product": why})

        variant_name = (variant or {}).get("name") or ""
        return {
            "title": f"How the change map supports {product}",
            "intro": (
                f"These modules prepare the business for change so {product} is not "
                f"dropped into a broken loop. Order follows track «{track}»"
                + (f" and variant «{variant_name}»" if variant_name else "")
                + f" under mechanism «{mechanism.get('title') or product}»."
            ),
            "modules": tied,
            "product": product,
            "track": track,
        }

    def _ru_pack(self, doc: dict[str, Any]) -> dict[str, str]:
        """Russian mirror of key client sections (structured, not machine-mix)."""
        name = doc.get("client_name") or "коллега"
        mech = doc.get("mechanism") or {}
        product = doc.get("product") or "продукт"
        claims = doc.get("claims") or []
        claim_lines = "\n".join(f"- {c}" for c in claims[:6]) or "- (краткий бриф)"
        pressure = ""
        if (doc.get("econ") or {}).get("derived"):
            pressure = (doc["econ"]["derived"][0].get("text") or "")
        elif (doc.get("econ") or {}).get("pressure_lines"):
            pressure = doc["econ"]["pressure_lines"][0]
        steps = "\n".join(
            f"{i}. {s}" for i, s in enumerate(mech.get("steps") or [], 1)
        )
        notes = "\n".join(
            f"- {n}" for n in (doc.get("action_notes") or doc.get("plan_14") or [])
        )
        tracks = doc.get("category_router") or {}
        primary = (tracks.get("primary") or "ops")
        primary_ru = {
            "ops": "операционный успех",
            "product": "продукт",
            "promotion": "продвижение",
        }.get(primary, primary)
        pilot = doc.get("pilot_offer") or {}
        why = (mech.get("why_this_case") or "").replace("*", "")
        return {
            "opening": (
                f"{name},\n\n"
                f"Бесплатная ориентация Metrix AI ({doc.get('industry_label')}). "
                f"Собрана из вашего брифа и цифр.\n\n"
                f"Главный вывод: {mech.get('title')}.\n\n"
                f"Деньги/мощность: {pressure or 'добавьте цифры — усилится денежная линия.'}\n\n"
                f"Рекомендуемый трек: {primary_ru}. "
                f"Ниже — диагноз, ситуация, механизм, продукт, краткие заметки и пилот."
            ),
            "diagnosis": (
                f"{name} — диагноз по этому брифу.\n\n"
                f"Что вы сообщили:\n{claim_lines}\n\n"
                f"Вывод: механизм «{mech.get('title')}», продукт {product}."
            ),
            "situation": (
                "Как работа идёт сейчас — из брифа и метрик.\n\n"
                + (doc.get("situation") or "")[:900]
            ),
            "mechanism_title": mech.get("title") or "",
            "mechanism_steps": steps,
            "why_this_case": why,
            "action_notes": notes,
            "plan_14": notes,
            "product": product,
            "track_primary_ru": primary_ru,
            "pilot_usd": pilot.get("price_usd") or 690,
            "pilot_title": pilot.get("title") or f"Пилот · {product}",
            "module_help": (doc.get("module_help") or {}).get("intro") or "",
            "note": (
                "RU — зеркало структуры. Полная техспека в TECH_SPEC (EN); "
                "перевод после принятия пилота по запросу."
            ),
        }

    # ── Tangibility score ────────────────────────────────────────────────

    def score_tangibility(self, doc: dict[str, Any], *, business: str, nums: dict[str, float]) -> dict[str, Any]:
        """Hard quality gate for 'feels like a paid product'."""
        checks: list[dict[str, Any]] = []
        diag = doc.get("diagnosis") or ""
        sit = doc.get("situation") or ""
        tech = doc.get("tech") or {}
        opening = doc.get("opening") or ""
        full = "\n".join([diag, sit, opening, json.dumps(tech, ensure_ascii=False)])

        def add(cid: str, ok: bool, detail: str) -> None:
            checks.append({"id": cid, "pass": ok, "detail": detail})

        # 1. No duplicate diagnosis dump inside situation
        diag_core = re.sub(r"\s+", " ", diag)[:180]
        add(
            "no_duplicate_diagnosis",
            diag_core[:80] not in sit if len(diag_core) > 40 else True,
            "Situation must not paste diagnosis",
        )

        # 2. Client brief tokens present
        tokens = [
            t.lower()
            for t in re.findall(r"[A-Za-zА-Яа-я]{4,}", business or "")
            if t.lower()
            not in {
                "with",
                "that",
                "this",
                "from",
                "have",
                "need",
                "want",
                "they",
                "them",
                "your",
                "their",
                "about",
                "into",
                "then",
                "than",
            }
        ]
        hits = sum(1 for t in tokens[:20] if t in full.lower())
        add(
            "brief_token_grounding",
            hits >= min(4, max(2, len(tokens[:20]) // 4)),
            f"brief token hits={hits}",
        )

        # 3. Numbers appear if provided
        if nums:
            num_hit = False
            for k, v in nums.items():
                if isinstance(v, float) and v <= 1:
                    if f"{v*100:.0f}%" in full or f"{v:.0%}" in full or str(int(v * 100)) in full:
                        num_hit = True
                if "revenue" in k and (str(int(v)) in full or f"{v:,.0f}" in full):
                    num_hit = True
                if str(v) in full:
                    num_hit = True
            add("numbers_in_prose", num_hit, "client numbers reflected in prose")
        else:
            add("numbers_in_prose", True, "no numbers supplied — skip")

        # 4. Tech has real WPs and acceptance
        wps = tech.get("work_packages") or []
        acc = tech.get("acceptance") or []
        add("tech_work_packages", len(wps) >= 3, f"WPs={len(wps)}")
        add("tech_acceptance", len(acc) >= 4, f"acceptance={len(acc)}")
        add(
            "tech_has_dod",
            len(tech.get("definition_of_done") or []) >= 3,
            "DoD present",
        )

        # 5. No internal jargon leaks
        bad = ["hub actor", "размыт", "chip_", "Virtual Chips", "Function Engine plane", "paid_score="]
        leak = [b for b in bad if b.lower() in full.lower()]
        add("no_jargon_leak", len(leak) == 0, f"leaks={leak}")

        # 6. Mechanism is specific (not empty / not just product name)
        mech = (doc.get("mechanism") or {}).get("title") or ""
        add(
            "mechanism_specific",
            len(mech) > 20 and "catalog" not in mech.lower(),
            mech[:80],
        )

        # 7. Recommendation explains why (not only offer table)
        rec = doc.get("recommendation") or {}
        why = " ".join(rec.get("why") or [])
        add("recommendation_has_why", len(why) > 80 and "why" in why.lower() or "because" in why.lower() or "point" in why.lower() or "mechanism" in why.lower(), "why length")

        # 8. Claims extracted when brief long enough
        if len(business or "") > 80:
            add(
                "claims_from_brief",
                len(doc.get("claims") or []) >= 2,
                f"claims={len(doc.get('claims') or [])}",
            )
        else:
            add("claims_from_brief", True, "short brief")

        # 9. Got-today is evidence not pure marketing
        got = " ".join(doc.get("got_today") or [])
        add(
            "got_is_evidence",
            ("diagnosis" in got.lower() or "диагноз" in got.lower())
            and (
                "mechanism" in got.lower()
                or "product" in got.lower()
                or "пилот" in got.lower()
                or "pilot" in got.lower()
            ),
            "got_today lists real artifacts",
        )

        # 10. Opening is grounded (brief/numbers), not a catalog pitch
        add(
            "opening_anti_template",
            "your brief" in opening.lower()
            or "headline" in opening.lower()
            or "free orientation" in opening.lower(),
            "opening sets uniqueness contract",
        )

        passed = sum(1 for c in checks if c["pass"])
        total = len(checks)
        score = passed / total if total else 0.0
        return {
            "score": round(score, 4),
            "passed": passed,
            "total": total,
            "ready_for_paid_send": score >= 0.8 and all(
                c["pass"]
                for c in checks
                if c["id"]
                in {
                    "no_duplicate_diagnosis",
                    "no_jargon_leak",
                    "tech_work_packages",
                    "tech_acceptance",
                    "mechanism_specific",
                }
            ),
            "checks": checks,
        }


# ── Writer ─────────────────────────────────────────────────────────────────

class PackageDeliverableWriter:
    name = "Package Deliverable Writer"
    version = "2.0-tangible"

    FOLDERS = (
        "01_orientation",
        "02_specs",
        "03_product_ideas",
        "04_fin_models",
        "05_promotion",
        "06_cloud_plans",
        "07_monetization",
        "08_deliverables",
        "09_paid_portal",
        "10_consult_metareality",
        "11_tech_write_specsforge",
        "12_package_result",
        "10_client_pack",
    )

    def __init__(self) -> None:
        self.synth = ConsultationSynthesizer()

    def write(
        self,
        *,
        request_id: str,
        industry_id: str,
        business: str,
        idea_title: str,
        narrative: dict[str, Any] | None = None,
        commercial: dict[str, Any] | None = None,
        paid: dict[str, Any] | None = None,
        memo_convert: dict[str, Any] | None = None,
        market_unit: dict[str, Any] | None = None,
        success: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
        client_name: str = "",
        oae: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        demo_idea: dict[str, Any] | None = None,
        demo_ideas: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        narrative = narrative or {}
        commercial = commercial or {}
        paid = paid or {}
        memo_convert = memo_convert or {}
        market_unit = market_unit or market_unit_for(industry_id)
        success = success or {}
        extra = dict(extra_params or {})
        for k, v in (success.get("business_numbers") or {}).items():
            if k not in extra and isinstance(v, (int, float)):
                extra[k] = float(v)
        nums = {
            k: float(v)
            for k, v in extra.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        }

        offer = dict(commercial.get("commercial_offer") or {})
        if not offer and isinstance(commercial.get("tangible"), dict):
            offer = dict((commercial["tangible"] or {}).get("commercial_offer") or {})

        # Pull demo / oae / decision from paid if not passed
        if not demo_idea and isinstance(paid.get("product"), dict):
            demo_idea = (paid.get("product") or {}).get("demo_idea")
        # commercial paid_for_final may not include product — OK

        doc = self.synth.synthesize(
            industry_id=industry_id,
            business=business,
            idea_title=idea_title,
            client_name=client_name,
            nums=nums,
            paid=paid,
            memo_convert=memo_convert,
            market_unit=market_unit,
            oae=oae or paid.get("oae") or {},
            decision=decision or paid.get("decision") or {},
            demo_idea=demo_idea or {},
            demo_ideas=demo_ideas or [],
            narrative=narrative,
            offer=offer,
        )
        doc["request_id"] = request_id
        pack_url = public_api_url(f"/api/v1/packages/{request_id}/result")
        consult_url = public_api_url(f"/api/v1/packages/{request_id}/consult")
        if isinstance(doc.get("pilot_offer"), dict):
            doc["pilot_offer"] = {
                **doc["pilot_offer"],
                "description_url_hint": pack_url,
                "consult_url": consult_url,
            }

        ws = WORKSPACE_ROOT / _safe(request_id)
        ws.mkdir(parents=True, exist_ok=True)
        for folder in self.FOLDERS:
            (ws / folder).mkdir(parents=True, exist_ok=True)

        consult_paths = self._write_consult(ws / "10_consult_metareality", doc)
        tech_paths = self._write_tech(ws / "11_tech_write_specsforge", doc)
        result_paths = self._write_result(ws / "12_package_result", doc)

        (ws / "README_CLIENT.md").write_text(self._readme(doc), encoding="utf-8")
        # QA + underhood + usability + RU mirror
        (ws / "12_package_result" / "TANGIBILITY_QA.json").write_text(
            json.dumps(
                {
                    "tangibility": doc["tangibility"],
                    "usability": doc.get("usability"),
                    "underhood_coverage": doc.get("underhood_coverage"),
                    "category_router": doc.get("category_router"),
                    "sanity": {
                        "ok": (doc.get("sanity") or {}).get("ok"),
                        "variant": (doc.get("sanity") or {}).get("variant"),
                        "flags": (doc.get("sanity") or {}).get("flags"),
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        ru = doc.get("ru") or {}
        ru_md = (
            f"# Ваш результат — бесплатная консультация\n\n"
            f"Для: {doc['client_name']} · Отрасль: {doc['industry_label']}\n"
            f"Трек: {ru.get('track_primary_ru')} · Продукт: {ru.get('product')}\n\n"
            f"## Обращение\n\n{ru.get('opening')}\n\n"
            f"## 1. Диагноз\n\n{ru.get('diagnosis')}\n\n"
            f"## 2. Ситуация\n\n{ru.get('situation')}\n\n"
            f"## 3. Механизм: {ru.get('mechanism_title')}\n\n"
            f"{ru.get('why_this_case')}\n\n{ru.get('mechanism_steps')}\n\n"
            f"## 4. Продукт\n\n{ru.get('product')}\n\n"
            f"## 5. Рекомендуемый пилот\n\n"
            f"**{ru.get('pilot_title')}** — ${ru.get('pilot_usd')}\n\n"
            f"[Открыть описание]({(doc.get('pilot_offer') or {}).get('description_url_hint') or '#'})\n\n"
            f"## 6. Краткие заметки для дальнейших шагов\n\n{ru.get('action_notes')}\n\n"
            f"---\n\n{ru.get('note')}\n"
        )
        (ws / "12_package_result" / "YOUR_RESULT_ru.md").write_text(ru_md, encoding="utf-8")

        manifest_path = ws / "manifest.json"
        manifest: dict[str, Any] = {}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                manifest = {}
        manifest.update(
            {
                "workspace_id": request_id,
                "industry_id": industry_id,
                "package": "consult_techwrite_bundle",
                "package_price_usd": doc["bundle"]["price_usd"],
                "deliverable_version": self.version,
                "tangibility_score": doc["tangibility"]["score"],
                "ready_for_paid_send": doc["tangibility"]["ready_for_paid_send"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "client_folders": {
                    "consult": "10_consult_metareality",
                    "tech_write": "11_tech_write_specsforge",
                    "package_result": "12_package_result",
                },
                "primary_client_file": "12_package_result/YOUR_RESULT.html",
            }
        )
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        latest = PROJECT_ROOT / "client-package-latest.html"
        latest.write_text(
            Path(result_paths["html"]).read_text(encoding="utf-8"), encoding="utf-8"
        )

        return {
            "module": self.name,
            "version": self.version,
            "workspace": str(ws),
            "consult": consult_paths,
            "tech_write": tech_paths,
            "package_result": result_paths,
            "readme": str(ws / "README_CLIENT.md"),
            "latest_html": str(latest),
            "url": pack_url,
            "consult_url": consult_url,
            "tech_url": public_api_url(f"/api/v1/packages/{request_id}/tech"),
            "primary": result_paths.get("html"),
            "tangibility": doc["tangibility"],
            "summary": (
                f"Tangible pack v{self.version}: tangibility="
                f"{doc['tangibility']['score']:.0%}, "
                f"ready={doc['tangibility']['ready_for_paid_send']}, "
                f"mechanism={doc['mechanism']['title'][:60]}"
            ),
        }

    # ── File writers ─────────────────────────────────────────────────────

    def _write_consult(self, folder: Path, doc: dict[str, Any]) -> dict[str, str]:
        md = f"""# MetaReality Consultation

**Client:** {doc['client_name']}  
**Domain:** {doc['industry_label']}  
**Request:** `{doc['request_id']}`  
**Package:** Consult + Tech Write · ${doc['bundle']['price_usd']}  
**Tangibility:** {doc['tangibility']['score']:.0%} · ready_for_paid_send={doc['tangibility']['ready_for_paid_send']}

---

## Opening

{doc['opening']}

---

## 1. Diagnosis

{doc['diagnosis']}

---

## 2. Situation — how work moves today

{doc['situation']}

---

## 3. Change mechanism

### {doc['mechanism']['title']}

{doc['mechanism'].get('why_this_case') or ''}

Steps:

{chr(10).join(f'{i}. {s}' for i, s in enumerate(doc['mechanism']['steps'], 1))}

Proof metrics: {', '.join(doc['mechanism']['proof_metrics'])}

---

## 4. Recommendation

{chr(10).join(doc['recommendation']['why'])}

{f"Buyer-facing proof: {doc['recommendation']['buyer_proof']}" if doc['recommendation'].get('buyer_proof') else ''}

---

## 5. Short notes for next steps

{chr(10).join(f'- {n}' for n in (doc.get('action_notes') or doc.get('plan_14') or []))}

---

## 6. Recommended pilot

**{(doc.get('pilot_offer') or {}).get('title') or doc['product']}** — ${(doc.get('pilot_offer') or {}).get('price_usd') or 690}

Open description: `{(doc.get('pilot_offer') or {}).get('description_path') or '10_consult_metareality/CONSULTATION.html'}`

---
"""
        html_doc = self._html_shell(
            title=f"Consultation — {doc['mechanism']['title'][:60]}",
            badge="METAREALITY · CONSULTATION",
            subtitle=f"{doc['client_name']} · {doc['industry_label']}",
            body_html=self._md_to_html(md),
            doc=doc,
        )
        paths = self._dump(folder, "CONSULTATION", md, html_doc, {
            "mechanism": doc["mechanism"],
            "diagnosis": doc["diagnosis"],
            "pilot_offer": doc.get("pilot_offer"),
            "tangibility": doc["tangibility"],
        })
        return paths

    def _write_tech(self, folder: Path, doc: dict[str, Any]) -> dict[str, str]:
        t = doc["tech"]
        wps = "\n".join(
            f"### {wp['id']} — {wp['title']}\n"
            f"- **Description:** {wp['description']}\n"
            f"- **Owner:** {wp['owner']}\n"
            f"- **Output / metric:** {wp['output']}\n"
            for wp in t["work_packages"]
        )
        interfaces = "\n".join(
            f"| {i['from']} | {i['to']} | {i['contract']} |"
            for i in t["interfaces"]
        )
        data_rows = "\n".join(
            f"| `{d['field']}` | {d['value']} | {d['use']} |"
            for d in t.get("data_dictionary") or []
        ) or "| — | — | no numeric inputs |"

        md = f"""# {t['title']}

**Client:** {doc['client_name']}  
**Request:** `{doc['request_id']}`  
**Depends on:** accepted MetaReality consultation  
**List price (tech write component):** ${doc['tech_p']['price_usd']}

---

## 1. Objective

{t['objective']}

## 2. Scope

### In scope
{chr(10).join(f'- {x}' for x in t['scope_in'])}

### Out of scope (non-goals)
{chr(10).join(f'- {x}' for x in t['scope_out'])}

## 3. Work packages

{wps}

## 4. Interfaces

| From | To | Contract |
|------|-----|----------|
{interfaces}

## 5. Data dictionary (this run)

| Field | Value | Use |
|-------|------:|-----|
{data_rows}

## 6. Acceptance criteria

{chr(10).join(f'- [ ] {a}' for a in t['acceptance'])}

## 7. Definition of done

{chr(10).join(f'- [ ] {d}' for d in t['definition_of_done'])}

## 8. Deliverables

{chr(10).join(f'- {d}' for d in t['deliverables'])}

## 9. Risks

{chr(10).join(f'- {r}' for r in t['risks'])}

## 10. Open questions

{chr(10).join(f'- {q}' for q in t['open_questions'])}

---

## Handoff

1. Client accepts consultation + this spec.  
2. Implement / {doc['product']} pre-dev starts on WP1.  
3. Optional expand: Paid Pilot $1490 or Full Orientation $2490 — only after DoD.
"""
        html_doc = self._html_shell(
            title=t["title"][:70],
            badge="SPECSFORGE · TECHNICAL SPECIFICATION",
            subtitle=f"{doc['client_name']} · build-ready · ${doc['tech_p']['price_usd']}",
            body_html=self._md_to_html(md),
            doc=doc,
        )
        return self._dump(folder, "TECH_SPEC", md, html_doc, t)

    def _write_result(self, folder: Path, doc: dict[str, Any]) -> dict[str, str]:
        t = doc["tech"]
        tang = doc["tangibility"]
        ready_badge = "READY TO SEND" if tang["ready_for_paid_send"] else "QA FLAGS — REVIEW"

        pilot = doc.get("pilot_offer") or {}
        notes = doc.get("action_notes") or doc.get("plan_14") or []
        why3 = (doc["mechanism"].get("why_this_case") or "").replace("*", "")
        md = f"""# Your result — free orientation

Prepared for {doc['client_name']}  
Domain · {doc['industry_label']}

---

## Opening

{doc['opening']}

---

## What you received

{chr(10).join(f'- {g}' for g in doc['got_today'])}

---

## 1. Diagnosis

{doc['diagnosis']}

---

## 2. Situation (how work moves today)

{doc['situation']}

---

## 3. Change mechanism — {doc['mechanism']['title']}

{why3}

{chr(10).join(f'{i}. {s}' for i, s in enumerate(doc['mechanism']['steps'], 1))}

Proof metrics: {', '.join(doc['mechanism']['proof_metrics'])}

---

## 4. Recommendation

{chr(10).join(doc['recommendation']['why'])}

{f"Buyer-facing proof: {doc['recommendation']['buyer_proof']}" if doc['recommendation'].get('buyer_proof') else ''}

---

## 5. Recommended pilot

**{pilot.get('title') or doc['product']}** — ${pilot.get('price_usd') or 690}

Track: {pilot.get('track') or 'ops'}

[Open description]({pilot.get('description_url_hint') or '/app/client-package-latest.html'})

Full consult write-up: `{pilot.get('description_path') or '10_consult_metareality/CONSULTATION.html'}`

---

## 6. Short notes for next steps

{chr(10).join(f'- {n}' for n in notes)}

---

Metrix AI · free orientation · v{PackageDeliverableWriter.version}
"""
        # HTML body — structured, not raw dump
        body = f"""
        <section class="card lead">
          <div class="ready {'ok' if tang['ready_for_paid_send'] else 'warn'}">{_e(ready_badge)}</div>
          <h2>Opening</h2>
          <div class="prose">{self._paras(doc['opening'])}</div>
        </section>

        <section class="card highlight">
          <h2>What you received</h2>
          <ul class="check">{''.join(f'<li>{self._inline(_e(g))}</li>' for g in doc['got_today'])}</ul>
        </section>

        <section class="card">
          <h2>1. Diagnosis</h2>
          <div class="prose">{self._paras(doc['diagnosis'])}</div>
        </section>

        <section class="card">
          <h2>2. Situation — how work moves today</h2>
          <div class="prose">{self._paras(doc['situation'])}</div>
        </section>

        <section class="card">
          <h2>3. Change mechanism</h2>
          <div class="product-name">{_e(doc['mechanism']['title'])}</div>
          <p>{_e(why3)}</p>
          <ol class="days">{''.join(f'<li>{_e(s)}</li>' for s in doc['mechanism']['steps'])}</ol>
          <p class="muted">Proof metrics: {_e(', '.join(doc['mechanism']['proof_metrics']))}</p>
        </section>

        <section class="card">
          <h2>4. Recommendation</h2>
          <div class="prose">{''.join(f'<p>{self._inline(_e(w))}</p>' for w in doc['recommendation']['why'])}</div>
          {f"<p>Buyer-facing proof: {_e(doc['recommendation']['buyer_proof'])}</p>" if doc['recommendation'].get('buyer_proof') else ''}
        </section>

        <section class="card highlight">
          <h2>5. Recommended pilot</h2>
          <div class="product-name">{_e(pilot.get('title') or doc['product'])}</div>
          <div class="price">${_e(pilot.get('price_usd') or 690)}</div>
          <p class="muted">Track: {_e(pilot.get('track') or 'ops')}</p>
          <p><a class="btn-pilot" href="{_e(pilot.get('description_url_hint') or '/app/client-package-latest.html')}">Open description</a></p>
        </section>

        <section class="card">
          <h2>6. Short notes for next steps</h2>
          <ul>{''.join(f'<li>{self._inline(_e(n))}</li>' for n in notes)}</ul>
        </section>
        """
        html_doc = self._html_shell(
            title=f"Your result — {doc['mechanism']['title'][:50]}",
            badge="YOUR RESULT · FREE ORIENTATION",
            subtitle=f"{doc['client_name']} · {doc['industry_label']}",
            body_html=body,
            doc=doc,
            hero_extra=f"<p class='tagline'>{_e(doc['mechanism']['title'])}</p>",
        )
        return self._dump(
            folder,
            "YOUR_RESULT",
            md,
            html_doc,
            {
                "mechanism": doc["mechanism"],
                "tangibility": tang,
                "product": doc["product"],
            },
        )

    def _dump(
        self, folder: Path, stem: str, md: str, html_doc: str, meta: dict[str, Any]
    ) -> dict[str, str]:
        md_path = folder / f"{stem}.md"
        html_path = folder / f"{stem}.html"
        json_path = folder / f"{stem.lower()}.json"
        md_path.write_text(md, encoding="utf-8")
        html_path.write_text(html_doc, encoding="utf-8")
        json_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        return {"markdown": str(md_path), "html": str(html_path), "json": str(json_path)}

    def _readme(self, doc: dict[str, Any]) -> str:
        return f"""# Client workspace — {doc['client_name']}

**Open first:** `12_package_result/YOUR_RESULT.html`

**Mechanism:** {doc['mechanism']['title']}  
**Tangibility:** {doc['tangibility']['score']:.0%} · ready={doc['tangibility']['ready_for_paid_send']}  
**Package:** ${doc['bundle']['price_usd']}

| Folder | Content |
|--------|---------|
| 12_package_result | Combined result |
| 10_consult_metareality | Full consultation |
| 11_tech_write_specsforge | Full technical specification |
"""

    def _inline(self, s: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def _paras(self, text: str) -> str:
        chunks = re.split(r"\n\s*\n", text or "")
        out = []
        for ch in chunks:
            ch = ch.strip()
            if not ch:
                continue
            if ch.startswith("- "):
                items = "".join(
                    f"<li>{self._inline(_e(line[2:]))}</li>"
                    for line in ch.splitlines()
                    if line.startswith("- ")
                )
                out.append(f"<ul>{items}</ul>")
            elif ch.startswith("**") and ch.endswith("**") and "\n" not in ch:
                out.append(f"<p><strong>{_e(ch.strip('*'))}</strong></p>")
            else:
                # preserve single newlines as <br> sparingly
                lines = ch.split("\n")
                if all(l.startswith("- ") or l.startswith("**") for l in lines if l.strip()):
                    buf = []
                    for l in lines:
                        if l.startswith("- "):
                            buf.append(f"<li>{self._inline(_e(l[2:]))}</li>")
                        elif l.strip():
                            buf.append(f"<p>{self._inline(_e(l))}</p>")
                    if any("<li>" in b for b in buf):
                        out.append("<ul>" + "".join(b for b in buf if b.startswith("<li>")) + "</ul>")
                        out.extend(b for b in buf if not b.startswith("<li>"))
                    else:
                        out.extend(buf)
                else:
                    out.append(f"<p>{self._inline(_e(ch))}</p>")
        return "".join(out)

    def _md_to_html(self, md: str) -> str:
        lines = md.splitlines()
        out: list[str] = []
        in_ul = False
        in_ol = False
        for line in lines:
            if line.startswith("# "):
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
                continue
            if line.startswith("## "):
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
                out.append(f"<h2>{_e(line[3:])}</h2>")
            elif line.startswith("### "):
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
                out.append(f"<h3>{_e(line[4:])}</h3>")
            elif re.match(r"^\d+\.\s", line):
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                if not in_ol:
                    out.append("<ol>")
                    in_ol = True
                out.append(f"<li>{self._inline(_e(re.sub(r'^\\d+\\.\\s', '', line)))}</li>")
            elif line.startswith("- "):
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
                if not in_ul:
                    out.append("<ul>")
                    in_ul = True
                out.append(f"<li>{self._inline(_e(line[2:]))}</li>")
            elif line.strip() in ("", "---"):
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
            else:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
                out.append(f"<p>{self._inline(_e(line))}</p>")
        if in_ul:
            out.append("</ul>")
        if in_ol:
            out.append("</ol>")
        return "\n".join(out)

    def _html_shell(
        self,
        *,
        title: str,
        badge: str,
        subtitle: str,
        body_html: str,
        doc: dict[str, Any],
        hero_extra: str = "",
    ) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(title)}</title>
  <style>
    :root {{
      --bg: #060d14; --card: #0c1522; --line: #1a2a3a;
      --accent: #5eead4; --accent2: #38bdf8; --gold: #fbbf24;
      --text: #e8eef6; --muted: #8ba0b5; --ok: #34d399; --warn: #f59e0b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "Segoe UI", system-ui, sans-serif; color: var(--text); line-height: 1.7;
      background: radial-gradient(1000px 520px at 0% -10%, #0f766e33, transparent),
                  radial-gradient(800px 480px at 100% 0%, #1e3a5f40, var(--bg));
    }}
    .wrap {{ max-width: 840px; margin: 0 auto; padding: 2rem 1.15rem 4rem; }}
    .hero {{
      border: 1px solid var(--line); border-radius: 22px; padding: 1.6rem 1.7rem;
      background: linear-gradient(155deg, #0f1c2bee, #042f2eaa); margin-bottom: 1.1rem;
      box-shadow: 0 20px 50px #0006;
    }}
    .badge {{
      display: inline-block; font-size: .7rem; font-weight: 800; letter-spacing: .06em;
      padding: .28rem .7rem; border-radius: 999px; background: #134e4a; color: var(--accent);
    }}
    h1 {{ font-size: 1.45rem; margin: .55rem 0 .35rem; letter-spacing: -0.025em; line-height: 1.25; }}
    h2 {{ font-size: 1.02rem; color: var(--accent); margin: 0 0 .65rem; }}
    h3 {{ font-size: .95rem; color: var(--accent2); }}
    .muted {{ color: var(--muted); font-size: .92rem; }}
    .tagline {{ color: var(--gold); font-weight: 600; margin: .45rem 0 0; }}
    .card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 16px;
      padding: 1.15rem 1.3rem; margin-bottom: .85rem;
    }}
    .card.lead {{ border-color: #134e4a; }}
    .card.highlight {{ background: linear-gradient(160deg, #0c1522, #0a2e2a88); border-color: #0f766e66; }}
    .card.honesty {{ border-color: #422006; background: #1c1408; }}
    .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }}
    @media (max-width: 700px) {{ .grid2 {{ grid-template-columns: 1fr; }} }}
    ul.check {{ list-style: none; padding: 0; margin: 0; }}
    ul.check li {{ padding: .35rem 0 .35rem 1.5rem; position: relative; }}
    ul.check li::before {{ content: "✓"; position: absolute; left: 0; color: var(--ok); font-weight: 800; }}
    ol.days {{ padding-left: 1.15rem; margin: 0; }}
    ol.days li {{ margin-bottom: .5rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .88rem; margin-top: .5rem; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: .45rem .3rem; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: .75rem; text-transform: uppercase; letter-spacing: .04em; }}
    .product-name {{ font-size: 1.2rem; font-weight: 800; color: var(--accent); margin-bottom: .4rem; }}
    .price {{ font-size: 2rem; font-weight: 800; color: var(--accent2); }}
    .ready {{ display: inline-block; font-size: .75rem; font-weight: 800; padding: .25rem .6rem; border-radius: 8px; margin-bottom: .7rem; }}
    .ready.ok {{ background: #064e3b; color: var(--ok); }}
    .ready.warn {{ background: #78350f; color: var(--warn); }}
    .prose p {{ margin: 0 0 .65rem; }}
    .prose ul {{ margin: .3rem 0 .7rem; padding-left: 1.2rem; }}
    code {{ color: var(--accent2); font-size: .85em; }}
    a.btn-pilot {{
      display: inline-block; margin-top: .5rem; padding: .55rem 1rem;
      background: var(--accent); color: #042f2e; font-weight: 800;
      border-radius: 10px; text-decoration: none;
    }}
    footer {{ margin-top: 1.4rem; color: var(--muted); font-size: .8rem; text-align: center; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <span class="badge">{_e(badge)}</span>
      <h1>{_e(title)}</h1>
      <p class="muted">{_e(subtitle)} · {_e(doc.get('request_id',''))}</p>
      {hero_extra}
    </header>
    {body_html}
    <footer>Metrix AI · Consult + Tech Write · v{PackageDeliverableWriter.version} · Not financial advice</footer>
  </div>
</body>
</html>"""
