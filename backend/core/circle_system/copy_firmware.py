"""Copy firmware: linguistic_warmth + answer shift + reduce-to-request.

Warmth never changes CY/CN/U. Three voices: B2C, A2A, tech_write.
"""

from __future__ import annotations

from typing import Any

from backend.core.circle_system.linguistic_warmth import LinguisticWarmthEngine
from backend.core.text_usability import polish_document
from backend.paid.types import clamp01

FORBIDDEN = (
    "гарантируем результат",
    "гарантия дохода",
    "guaranteed return",
    "we guarantee results",
    "без риска",
    "risk-free",
    "21-principle dump",
    "210 edges",
    "void_membrane на главной",
    "OAE ricochet",
    "вы обязательно заработаете",
    "natal",
    "гороскоп цены",
    "pilot всегда успешен",
    "main без пилота",
)

CANONICAL = (
    "who the work is for",
    "which void we close",
    "which gate must pass",
    "the price of this step",
    "what is not included",
    "consult → direction → ship",
    "main only after pilot",
    "assembly is not warmth",
    "code of an agreed model",
    "human-authorized owner stays",
)

JARGON_PUBLIC = {
    "ru": {
        "OAE": "операционный разбор",
        "ricochet": "обратная пересборка",
        "void_membrane": "слот риска / дыры",
        "VVI": "дыры в спеке",
        "assembly": "сходимость условий",
        "RRC": "насколько можно разобрать и собрать лучше",
        "IROI": "информационная отдача",
        "chain": "последовательность сборки",
        "CY/CN/U": "точно да / точно нет / не собрано",
        "constructor form": "каркас пустого слота",
        "pragma split": "точка ветвления",
    },
    "en": {
        "OAE": "operational analysis",
        "ricochet": "reverse rebuild",
        "void_membrane": "risk / gap slot",
        "VVI": "spec gaps",
        "assembly": "fit of conditions",
        "RRC": "how well it can be taken apart and rebuilt",
        "IROI": "informational return",
        "chain": "assembly sequence",
        "CY/CN/U": "certain yes / certain no / unbound",
        "constructor form": "empty-slot frame",
        "pragma split": "branch point",
    },
}


class CopyFirmware:
    name = "Copy Firmware"
    voices = ("b2c", "a2a", "tech_write")

    def __init__(self) -> None:
        self.warmth = LinguisticWarmthEngine()

    def publicize(self, text: str, lang: str = "en") -> str:
        out = text or ""
        table = JARGON_PUBLIC["ru"] if lang.startswith("ru") else JARGON_PUBLIC["en"]
        for src, dst in table.items():
            out = out.replace(src, dst)
        return out

    def strip_forbidden(self, text: str) -> str:
        low = (text or "").lower()
        out = text or ""
        for phrase in FORBIDDEN:
            if phrase.lower() in low:
                out = out.replace(phrase, "")
                out = out.replace(phrase.capitalize(), "")
        return " ".join(out.split())

    def offer_block(
        self,
        *,
        who: str,
        void: str,
        gate: str,
        price: str,
        not_included: str,
        voice: str = "b2c",
        lang: str = "en",
    ) -> dict[str, Any]:
        ru = lang.startswith("ru")
        if voice == "a2a":
            body = (
                f"Owner слота: {who}. Передаваемый артефакт закрывает {void}. "
                f"Gate: {gate}. Цена координации: {price}. Не входит: {not_included}."
                if ru
                else f"Slot owner: {who}. Handoff artefact closes {void}. "
                f"Gate: {gate}. Coordination price: {price}. Not included: {not_included}."
            )
        elif voice == "tech_write":
            body = (
                f"SPEC who={who}; void={void}; gate={gate}; price={price}; exclude={not_included}."
            )
        else:
            body = (
                f"Для кого: {who}. Какую дыру закрываем: {void}. "
                f"Какой gate: {gate}. Цена шага: {price}. Не входит: {not_included}."
                if ru
                else f"For: {who}. Void we close: {void}. "
                f"Gate: {gate}. Price of this step: {price}. Not included: {not_included}."
            )
        body = self.strip_forbidden(self.publicize(body, lang=lang) if voice != "tech_write" else body)
        return {
            "voice": voice,
            "who": who,
            "void": void,
            "gate": gate,
            "price": price,
            "not_included": not_included,
            "text": body,
            "certainty_untouched": True,
        }

    def render(
        self,
        *,
        status: str,
        body_fact: str,
        next_action: str,
        assembly_score: float,
        voice: str = "b2c",
        lang: str = "en",
        certain_yes_ratio: float = 0.4,
    ) -> dict[str, Any]:
        warmth = self.warmth.score(
            assembly_score=assembly_score,
            certain_yes_ratio=certain_yes_ratio,
            lang=lang,
        )
        fact = body_fact if voice == "tech_write" else self.publicize(body_fact, lang=lang)
        fact = self.strip_forbidden(fact)
        ans = self.warmth.render_answer(
            status=status,
            body_fact=fact,
            next_action=next_action,
            warmth=warmth,
            lang=lang,
        )
        ans["voice"] = voice
        ans["status"] = status  # identical to input — warmth is presentation
        ans["certainty_untouched"] = True
        return {"warmth": warmth, "answer": ans}

    def shift_copy(
        self,
        *,
        answer_shift: dict[str, Any],
        voice: str,
        lang: str,
        reduced: str,
    ) -> dict[str, Any]:
        """Apply OAE answer_shift as copy, never as a certainty rewrite."""
        mag = float((answer_shift or {}).get("magnitude") or 0)
        text = self.strip_forbidden(reduced)
        if voice != "tech_write":
            text = self.publicize(text, lang=lang)
        if mag < 0.25:
            text = text
        cleaned, report = polish_document({"copy": text})
        return {
            "text": cleaned.get("copy") or text,
            "magnitude": mag,
            "voice": voice,
            "usability": report if isinstance(report, dict) else {},
            "certainty_untouched": True,
        }

    def freeze_corpus(self) -> dict[str, Any]:
        return {
            "forbidden": list(FORBIDDEN),
            "canonical": list(CANONICAL),
            "voices": list(self.voices),
            "jargon_public": JARGON_PUBLIC,
            "rule": "warmth ≠ CY/CN/U; geometry of the project does not leak onto the landing",
        }


def polish_niche_pack(pack: dict[str, Any], lang: str = "ru") -> dict[str, Any]:
    """Run copy firmware + text usability on a niche answer pack."""
    fw = CopyFirmware()
    out = dict(pack)
    for key in ("answer", "answer_en", "hook", "tasty_proof"):
        if out.get(key):
            raw = str(out[key])
            out[key] = fw.strip_forbidden(fw.publicize(raw, lang=lang) if key != "answer_en" else fw.publicize(raw, lang="en"))
    dirs = dict(out.get("directions") or {})
    cleaned = {}
    for d, body in dirs.items():
        row = dict(body)
        for k in ("answer", "answer_en", "title"):
            if row.get(k):
                row[k] = fw.strip_forbidden(str(row[k]))
        cleaned[d] = row
    if cleaned:
        out["directions"] = cleaned
    return out
