"""
Text Usability Suite — goals (architecture decisions):

1. NO_DUP — kill paragraph/sentence duplication (same idea twice = defect)
2. SIMPLE — prefer short clauses; flag overlong / nested sentences
3. WATER — cut empty consultant filler without case anchors
4. DRY_MATH — allow at most one money line per section; rest is conclusion
5. BILINGUAL — structure supports ru/en field pairs without mixed sentences
6. TANGIBLE — require mechanism + next action + one client token

Programs call `polish_document(sections)` before write.
Does NOT invent strategy — only cleans and scores existing prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


# Filler phrases that read as water without client anchors
_WATER = re.compile(
    r"\b("
    r"it is important to note|needless to say|in today's (?:fast[- ]paced )?world|"
    r"leverage synergies|going forward|at the end of the day|"
    r"as previously mentioned|in conclusion,? we|"
    r"данн(?:ый|ая|ое) (?:раздел|текст)|как уже было сказано|"
    r"в современном мире|важно отметить,? что"
    r")\b",
    re.I,
)

_COMPLEX_MARKERS = re.compile(
    r"\b(notwithstanding|heretofore|aforementioned|vis-à-vis|whereby|"
    r"соответственно|вышеизложенн\w+|в рамках парадигмы)\b",
    re.I,
)


@dataclass
class SectionScore:
    id: str
    sentences: int
    dups_removed: int
    water_hits: int
    avg_words: float
    long_sentences: int
    issues: list[str] = field(default_factory=list)
    score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "sentences": self.sentences,
            "dups_removed": self.dups_removed,
            "water_hits": self.water_hits,
            "avg_words": round(self.avg_words, 1),
            "long_sentences": self.long_sentences,
            "issues": self.issues,
            "score": round(self.score, 4),
        }


def split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    # Keep bullets as units
    if "\n- " in text or text.startswith("- "):
        parts = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts.append(line)
        return parts
    # Split on sentence end; do not require next capital (filler strip can leave lowercase)
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s%$.]", " ", s, flags=re.U)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def dedupe_sentences(sentences: list[str], *, jaccard: float = 0.72) -> tuple[list[str], int]:
    """Remove near-duplicate sentences (keeps first)."""
    kept: list[str] = []
    removed = 0
    norms: list[set[str]] = []
    norm_strs: list[str] = []
    for s in sentences:
        ns = _norm(s)
        toks = set(ns.split())
        if len(toks) < 3:
            kept.append(s)
            norms.append(toks)
            norm_strs.append(ns)
            continue
        dup = False
        for prev, prev_s in zip(norms, norm_strs):
            if not prev:
                continue
            inter = len(toks & prev)
            union = len(toks | prev) or 1
            if inter / union >= jaccard:
                dup = True
                break
            # one sentence contains the other (after filler strip)
            if ns and prev_s and (ns in prev_s or prev_s in ns):
                dup = True
                break
            # high token overlap on shorter sentence
            shorter, longer = (toks, prev) if len(toks) <= len(prev) else (prev, toks)
            if len(shorter) >= 3 and len(shorter & longer) / len(shorter) >= 0.85:
                dup = True
                break
            # substring containment for long repeats
            if len(toks) > 8 and toks.issubset(prev):
                dup = True
                break
        if dup:
            removed += 1
            continue
        kept.append(s)
        norms.append(toks)
        norm_strs.append(ns)
    return kept, removed


def simplify_sentence(s: str, *, max_words: int = 28) -> str:
    """Light simplify: strip complex markers, split overlong with semicolon if possible."""
    s = _COMPLEX_MARKERS.sub("", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ,;")
    words = s.split()
    if len(words) <= max_words:
        return s
    # Prefer break at ; or — or ,
    for sep in ("; ", " — ", " - ", ", and ", ", "):
        if sep in s:
            left, right = s.split(sep, 1)
            if 6 <= len(left.split()) <= max_words:
                return left.rstrip(",;") + "."
    # Hard truncate at max_words with ellipsis only if still too long
    return " ".join(words[:max_words]).rstrip(",;") + "."


def strip_water(text: str) -> tuple[str, int]:
    hits = len(_WATER.findall(text or ""))
    cleaned = _WATER.sub("", text or "")
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned, hits


def limit_money_lines(sentences: list[str], *, max_money: int = 1) -> list[str]:
    """Keep at most max_money sentences that look like pure calculation lines."""
    money_re = re.compile(r"\$[\d,]+|\d+%\s*(?:rework|utilization|margin)|drag band|order-of-magnitude", re.I)
    out: list[str] = []
    money_count = 0
    for s in sentences:
        is_money = bool(money_re.search(s)) and len(s.split()) > 12
        if is_money:
            money_count += 1
            if money_count > max_money:
                # Keep conclusion-style short form if possible
                m = re.search(r"(~?\$[\d,]+(?:/mo)?|\d+%)", s)
                if m and not any(m.group(0) in x for x in out):
                    out.append(f"Cash reading: {m.group(0)} — use as pilot scoreboard, not a promise.")
                continue
        out.append(s)
    return out


def polish_section(
    section_id: str,
    text: str,
    *,
    max_words: int = 26,
    max_money_lines: int = 1,
    client_tokens: set[str] | None = None,
) -> tuple[str, SectionScore]:
    raw = text or ""
    raw, water = strip_water(raw)
    sents = split_sentences(raw)
    sents, dups = dedupe_sentences(sents)
    sents = [simplify_sentence(s, max_words=max_words) for s in sents]
    sents = limit_money_lines(sents, max_money=max_money_lines)
    # Drop empties after simplify
    sents = [s for s in sents if s and len(s) > 3]

    words = [len(s.split()) for s in sents] or [0]
    avg = sum(words) / max(1, len(words))
    long_n = sum(1 for w in words if w > max_words + 4)
    issues: list[str] = []
    if dups:
        issues.append(f"removed_{dups}_dups")
    if water:
        issues.append(f"water_hits_{water}")
    if long_n:
        issues.append(f"long_sents_{long_n}")
    if client_tokens:
        blob = " ".join(sents).lower()
        hits = sum(1 for t in client_tokens if t in blob)
        if hits < min(2, len(client_tokens)):
            issues.append("weak_client_anchor")

    score = 1.0
    score -= 0.08 * dups
    score -= 0.05 * water
    score -= 0.04 * long_n
    if "weak_client_anchor" in issues:
        score -= 0.15
    score = clamp01(score)

    # Rebuild: bullets stay lines; prose joins with space
    if any(s.startswith(("- ", "* ", "•")) or s.startswith("**") for s in sents):
        body = "\n".join(sents)
    else:
        body = " ".join(sents)

    return body, SectionScore(
        id=section_id,
        sentences=len(sents),
        dups_removed=dups,
        water_hits=water,
        avg_words=avg,
        long_sentences=long_n,
        issues=issues,
        score=score,
    )


def polish_document(
    sections: dict[str, str],
    *,
    client_tokens: set[str] | None = None,
    max_money_per_section: int = 1,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Polish all sections; return cleaned map + usability report."""
    out: dict[str, str] = {}
    scores: list[SectionScore] = []
    for sid, text in sections.items():
        body, sc = polish_section(
            sid,
            text,
            max_money_lines=max_money_per_section if sid in ("diagnosis", "opening", "situation") else 2,
            client_tokens=client_tokens,
        )
        out[sid] = body
        scores.append(sc)

    # Cross-section duplicate: if diagnosis core appears in situation, trim situation
    if "diagnosis" in out and "situation" in out:
        d_norm = _norm(out["diagnosis"])[:120]
        if len(d_norm) > 40 and d_norm[:50] in _norm(out["situation"]):
            sit_sents, _ = dedupe_sentences(
                split_sentences(out["situation"])
                + []  # no-op
            )
            # remove sents that are too similar to diagnosis
            d_toks = set(_norm(out["diagnosis"]).split())
            kept = []
            for s in sit_sents:
                st = set(_norm(s).split())
                if not st:
                    continue
                j = len(st & d_toks) / max(1, len(st | d_toks))
                if j < 0.55:
                    kept.append(s)
            out["situation"] = " ".join(kept) if kept else out["situation"]
            scores.append(
                SectionScore(
                    id="cross_dedupe",
                    sentences=len(kept),
                    dups_removed=1,
                    water_hits=0,
                    avg_words=0,
                    long_sentences=0,
                    issues=["cross_section_dedupe"],
                    score=0.9,
                )
            )

    mean = sum(s.score for s in scores) / max(1, len(scores))
    report = {
        "module": "Text Usability Suite",
        "version": "1.0",
        "mean_score": round(mean, 4),
        "pass": mean >= 0.72,
        "sections": [s.to_dict() for s in scores],
        "goals": [
            "NO_DUP",
            "SIMPLE",
            "WATER",
            "DRY_MATH",
            "BILINGUAL_READY",
            "TANGIBLE",
        ],
    }
    return out, report


def client_tokens_from_brief(business: str, limit: int = 24) -> set[str]:
    stop = {
        "with", "that", "this", "from", "have", "need", "want", "they", "them",
        "your", "their", "about", "into", "then", "than", "and", "the", "for",
        "our", "are", "was", "were", "will", "can", "not", "but", "all",
        "это", "как", "для", "или", "при", "что", "они", "мы", "вы", "нас",
    }
    toks = re.findall(r"[A-Za-zА-Яа-я]{4,}", business or "")
    uniq = []
    seen: set[str] = set()
    for t in toks:
        tl = t.lower()
        if tl in stop or tl in seen:
            continue
        seen.add(tl)
        uniq.append(tl)
        if len(uniq) >= limit:
            break
    return set(uniq)


def underhood_coverage(payload: dict[str, Any]) -> dict[str, Any]:
    """Audit which analysis surfaces are present for deliverable synthesis."""
    keys = {
        "business": bool(payload.get("business")),
        "nums": bool(payload.get("nums")),
        "demo_idea": bool(payload.get("demo_idea")),
        "demo_ideas": bool(payload.get("demo_ideas")),
        "oae": bool(payload.get("oae")),
        "decision": bool(payload.get("decision")),
        "paid_package": bool((payload.get("paid") or {}).get("package")),
        "situation_metrics": bool(
            (payload.get("paid") or {}).get("situation_metrics")
            or (payload.get("paid") or {}).get("business_metrics")
        ),
        "function_engine": bool((payload.get("paid") or {}).get("function_engine")),
        "hypotheses": bool((payload.get("paid") or {}).get("hypotheses")),
        "must_ask": bool(
            (payload.get("paid") or {}).get("must_ask")
            or (payload.get("paid") or {}).get("clarifying_questions")
        ),
        "memo_convert": bool(payload.get("memo_convert")),
        "market_unit": bool(payload.get("market_unit")),
        "reader": bool((payload.get("paid") or {}).get("reader")),
        "mega_map": bool((payload.get("paid") or {}).get("mega_map")),
        "energy_flow": bool((payload.get("paid") or {}).get("energy_flow")),
        "critical_thinking": bool((payload.get("paid") or {}).get("critical_thinking")),
        "blue_ocean": bool((payload.get("paid") or {}).get("blue_ocean")),
        "capital_efficiency": bool((payload.get("paid") or {}).get("capital_efficiency")),
        "narrative": bool(payload.get("narrative")),
    }
    used = sum(1 for v in keys.values() if v)
    return {
        "module": "Underhood Coverage Audit",
        "fields": keys,
        "used": used,
        "total": len(keys),
        "coverage": round(used / len(keys), 4),
        "missing": [k for k, v in keys.items() if not v],
        "note": "Deliverable should read every True field; missing = synthesis gap",
    }
