"""
Linguistic Signal Weaver (Telecom)

Полное раскрытие «Linguistic Coop» (линг) → модуль лингвистической кооперации,
обработки сигналов, понимания протоколов и языковых моделей, полезных в telecom.

Не просто «чат»: сигнал + язык + протокол как единая ткань.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.core.metrics import CoreMetrics, compute_core_metrics


# Упрощённая карта telecom-сигналов / протокольных семейств
PROTOCOL_FAMILY = {
    "sip": ["sip", "invite", "bye", "register", "voip"],
    "diameter": ["diameter", "gx", "gy", "rx", "pcrf"],
    "gtp": ["gtp", "s11", "s5", "pgw", "sgw"],
    "http2_sbi": ["http2", "sbi", "nrf", "amf", "smf", "udm", "5gc"],
    "ss7_map": ["ss7", "map", "sccp", "isup"],
    "rtp_media": ["rtp", "rtcp", "codec", "jitter", "mos"],
    "qos_policy": ["qos", "sla", "dscp", "priority", "latency", "packet loss"],
    "linguistic_ops": ["intent", "dialog", "nlu", "ivr", "agent", "language", "линг"],
}


@dataclass
class SignalChannel:
    name: str
    family: str
    strength: float
    noise: float
    cooperative: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LinguisticWeaveResult:
    industry_focus: str
    channels: list[dict[str, Any]]
    dominant_family: str
    cooperation_score: float
    protocol_map: dict[str, list[str]]
    optimized_phrases: list[str]
    recommendations: list[str]
    metrics: CoreMetrics
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "Linguistic Signal Weaver (Telecom)",
            "industry_focus": self.industry_focus,
            "channels": self.channels,
            "dominant_family": self.dominant_family,
            "cooperation_score": self.cooperation_score,
            "protocol_map": self.protocol_map,
            "optimized_phrases": self.optimized_phrases,
            "recommendations": self.recommendations,
            "metrics": self.metrics.to_dict(),
            "summary": self.summary,
        }


class LinguisticSignalWeaver:
    name = "Linguistic Signal Weaver (Telecom)"

    def weave(
        self,
        text: str,
        industry_id: str = "telecom",
        target_outcome: str = "clarity_and_qos",
    ) -> LinguisticWeaveResult:
        text_l = (text or "").lower()
        channels: list[SignalChannel] = []
        protocol_map: dict[str, list[str]] = {}

        for family, keys in PROTOCOL_FAMILY.items():
            hits = [k for k in keys if k in text_l]
            if not hits and industry_id != "telecom" and family not in (
                "linguistic_ops",
                "qos_policy",
            ):
                continue
            strength = min(1.0, 0.15 + len(hits) * 0.22)
            if industry_id == "telecom":
                strength = min(1.0, strength + 0.12)
            noise = max(0.05, 0.45 - len(hits) * 0.08)
            # cooperation: linguistic + protocol together
            cooperative = family in ("linguistic_ops", "qos_policy") or len(hits) >= 2
            channels.append(
                SignalChannel(
                    name=f"ch_{family}",
                    family=family,
                    strength=round(strength, 4),
                    noise=round(noise, 4),
                    cooperative=cooperative,
                    notes=[f"hits={hits}"] if hits else ["inferred baseline"],
                )
            )
            if hits:
                protocol_map[family] = hits

        if not channels:
            channels.append(
                SignalChannel(
                    name="ch_linguistic_ops",
                    family="linguistic_ops",
                    strength=0.4,
                    noise=0.3,
                    cooperative=True,
                    notes=["fallback linguistic channel"],
                )
            )

        channels.sort(key=lambda c: c.strength - c.noise, reverse=True)
        dominant = channels[0].family
        coop = sum(c.strength for c in channels if c.cooperative) / max(
            1, len([c for c in channels if c.cooperative])
        )
        coop = min(1.0, coop + 0.1 * len(protocol_map))

        phrases = self._optimize_phrases(text, dominant, target_outcome, industry_id)
        recs = self._recommendations(channels, dominant, industry_id, coop)

        # voids = noisy weak channels
        weak = [c for c in channels if c.noise > 0.3 and c.strength < 0.4]
        metrics = compute_core_metrics(
            known_params=len(protocol_map) + 2,
            required_params=max(6, len(PROTOCOL_FAMILY) // 2),
            ambiguity_score=min(1.0, sum(c.noise for c in channels) / max(1, len(channels))),
            conflict_score=0.1 if len(protocol_map) > 4 else 0.05,
            missing_critical=len(weak),
            detected_errors=len(weak) + 1,
            actionable_errors=len(weak),
            improvement_delta=coop * 0.5,
            fragments=len(channels),
            successful_reassemblies=sum(1 for c in channels if c.cooperative),
            structure_entropy=0.5,
            reverse_links=sum(1 for c in channels if c.cooperative),
            forward_links=max(1, len(channels)),
            notes=["linguistic-signal weave metrics"],
        )

        summary = (
            f"{self.name}: dominant={dominant}, cooperation={coop:.2f}, "
            f"channels={len(channels)}, phrases={len(phrases)}, "
            f"health={metrics.health_score:.2f}."
        )

        return LinguisticWeaveResult(
            industry_focus=industry_id,
            channels=[c.to_dict() for c in channels],
            dominant_family=dominant,
            cooperation_score=round(coop, 4),
            protocol_map=protocol_map,
            optimized_phrases=phrases,
            recommendations=recs,
            metrics=metrics,
            summary=summary,
        )

    def _optimize_phrases(
        self,
        text: str,
        dominant: str,
        outcome: str,
        industry_id: str,
    ) -> list[str]:
        # extract noun-ish tokens for personalization
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]{4,}", text.lower())
        top = list(dict.fromkeys(words))[:6]
        topic = ", ".join(top[:3]) if top else industry_id

        base = [
            f"Orient protocol narrative around {dominant} for: {topic}.",
            f"Reduce linguistic noise: one intent → one QoS class → one owner.",
            f"Target outcome «{outcome}»: map customer language to signal metrics.",
        ]
        if industry_id == "telecom":
            base.append(
                "Carrier language: speak SLA, ARPU, churn — not generic AI hype."
            )
            base.append(
                "Weave IVR/NLU intents with core/RAN events for closed-loop care."
            )
        if dominant in ("rtp_media", "qos_policy"):
            base.append("Lead with MOS/latency proof before product feature lists.")
        if dominant == "http2_sbi":
            base.append("5GC SBI story: NRF discovery → service graph → product SKU.")
        return base

    def _recommendations(
        self,
        channels: list[SignalChannel],
        dominant: str,
        industry_id: str,
        coop: float,
    ) -> list[str]:
        recs = [
            f"Make {dominant} the spine of the telecom offer copy.",
            "Pair every linguistic intent with a measurable signal KPI.",
        ]
        noisy = [c.family for c in channels if c.noise > 0.35]
        if noisy:
            recs.append(f"Denoise families: {', '.join(noisy[:3])} — define glossaries.")
        if coop < 0.55:
            recs.append("Raise cooperation: joint runbooks for NLU ops + network ops.")
        if industry_id != "telecom":
            recs.append(
                "Non-telecom request: reuse Linguistic Signal Weaver as metaphor "
                "for protocol-grade client communication."
            )
        recs.append("Export optimized phrases into Promo Automation messages.")
        return recs
