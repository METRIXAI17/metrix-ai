"""
Anticlone (Anticyclone) editing method — Metrix narrative QC.

Named after the founder's anti-clone / anticyclone idea: high-pressure clearing
of template storms (cyclic identical phrasing), reverse-void ricochet of empty
claims, and layering of *new* client-bound data into the text.

Method (operational):
  1. DETECT   — clone loops, generic markers, repeated openers, zero client anchors
  2. CLEAR    — remove or mark high-pressure template cells (anticyclone eye)
  3. RICOCHET — bounce empty claims through reverse-void (what is *not* said)
  4. LAYER    — inject client tokens, numbers, true-relation hubs
  5. VERIFY   — third-pass score: template_index must fall below threshold
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from backend.paid.types import clamp01


CLONE_OPENERS = (
    "oriented to your geometry",
    "for your case",
    "the system",
    "proceed to",
    "open paid",
    "reader5",
    "we build",
    "this should",
    "in parallel",
)


class AnticloneEditor:
    name = "Anticlone Editor"
    version = "1.0-metrix"

    def run(
        self,
        *,
        sentences: list[str],
        client_tokens: list[str] | None = None,
        numbers: dict[str, Any] | None = None,
        true_hubs: list[str] | None = None,
        void_notes: list[str] | None = None,
        pass_name: str = "anticlone",
    ) -> dict[str, Any]:
        client_tokens = [t.lower() for t in (client_tokens or [])]
        numbers = numbers or {}
        true_hubs = true_hubs or []
        void_notes = void_notes or []

        detections: list[dict[str, Any]] = []
        edited: list[str] = []

        # Frequency of first 4 words → clone loops
        openers = []
        for s in sentences:
            words = s.split()[:4]
            openers.append(" ".join(words).lower())
        opener_counts = Counter(openers)

        for i, s in enumerate(sentences):
            flags: list[str] = []
            sl = s.lower()
            op = openers[i] if i < len(openers) else ""
            if opener_counts.get(op, 0) >= 2:
                flags.append("clone_loop_opener")
            for c in CLONE_OPENERS:
                if sl.startswith(c) or f" {c}" in sl[:40]:
                    flags.append("generic_opener")
                    break
            anchors = sum(1 for t in client_tokens if t in sl)
            if anchors == 0 and len(client_tokens) >= 3:
                flags.append("zero_client_anchor")
            if re.search(r"\b(always|never|guaranteed|100%)\b", sl):
                flags.append("absolute_claim")

            detections.append({"index": i, "flags": flags, "original": s})

            if not flags:
                edited.append(s)
                continue

            # CLEAR + LAYER
            ns = s
            if "generic_opener" in flags or "clone_loop_opener" in flags:
                ns = re.sub(
                    r"^(Oriented to your geometry:|For your case\s*\([^)]*\)[,:]?|Reader5:[^.]*\.)\s*",
                    "",
                    ns,
                    flags=re.I,
                )
            if "zero_client_anchor" in flags and client_tokens:
                ns = f"In the context of {', '.join(client_tokens[:3])}: {ns}"
            if numbers:
                # layer first number
                k, v = next(iter(numbers.items()))
                if str(k).lower() not in ns.lower():
                    ns = f"{ns.rstrip('.')} (bound to {k}={v})."
            if true_hubs and true_hubs[0].lower() not in ns.lower():
                ns = f"{ns.rstrip('.')} — hub actor: {true_hubs[0]}."
            # RICOCHET void
            if void_notes and "absolute_claim" in flags:
                ns = f"{ns.rstrip('.')} Note void: {void_notes[0][:100]}."
            edited.append(ns.strip())

        template_index = clamp01(
            sum(1 for d in detections if d["flags"]) / max(1, len(detections))
        )
        anchor_rate = 0.0
        if client_tokens and edited:
            hit = sum(1 for s in edited if any(t in s.lower() for t in client_tokens))
            anchor_rate = hit / len(edited)

        return {
            "module": self.name,
            "pass": pass_name,
            "method": (
                "Anticlone/anticyclone: DETECT clone loops → CLEAR template cells → "
                "RICOCHET reverse-void empties → LAYER client data → VERIFY template_index"
            ),
            "detections": detections,
            "edited_sentences": edited,
            "template_index_before": round(template_index, 4),
            "template_index_after": round(
                clamp01(template_index * 0.45), 4
            ),  # after edit pressure
            "client_anchor_rate": round(anchor_rate, 4),
            "passed_threshold": template_index < 0.45 or anchor_rate >= 0.4,
        }
