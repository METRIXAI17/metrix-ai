"""
Task Reader — multi-variant, unbiased reading of a brief.

Karim Metrix (2026-08-11 / 2026-08-18):
  request reader + original decision core;
  Vibrant Capabi: every brief → open-ended generative territory;
  quality-first metric engine (not query-driven).

Never collapses to one reading. Always returns several end-states
plus a disagreement index. Bias is audited, not hidden.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.core.task_reader.linguistic_spaces import unfold_linguistic_spaces


BIAS_CHECKS = (
    "recency",          # last sentence does not overwrite the whole
    "authority",        # self-claim of expertise is not evidence
    "confirmation",     # first parse is not privileged
    "gap_filling",      # missing slots stay missing, not invented
    "formal_lock",      # do not require a formal logic chain
    "sku_first",        # do not jump to a product to sell
    "single_reading",   # forbid unique-answer collapse
)


def detect_lang(text: str) -> str:
    cyr = len(re.findall(r"[а-яёА-ЯЁ]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]", text or ""))
    if cyr >= lat:
        return "ru"
    return "en"


@dataclass
class EndState:
    id: str
    label: str
    reading: str
    deliverable: str
    confidence: float
    evidence: list[str]
    residual_unknowns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VariantReading:
    reader_id: str
    thesis: str
    end_states: list[EndState]
    bias_flags: list[str]
    evidence_score: float
    novelty_score: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reader_id": self.reader_id,
            "thesis": self.thesis,
            "end_states": [e.to_dict() for e in self.end_states],
            "bias_flags": self.bias_flags,
            "evidence_score": self.evidence_score,
            "novelty_score": self.novelty_score,
            "notes": self.notes,
        }


@dataclass
class TaskRead:
    query: str
    lang: str
    variants: list[VariantReading]
    selected_end_states: list[EndState]
    disagreement: float
    bias_audit: dict[str, Any]
    linguistic: dict[str, Any]
    objective_stance: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "Metrix Task Reader",
            "query": self.query[:2000],
            "lang": self.lang,
            "variants": [v.to_dict() for v in self.variants],
            "selected_end_states": [e.to_dict() for e in self.selected_end_states],
            "disagreement": self.disagreement,
            "bias_audit": self.bias_audit,
            "linguistic": self.linguistic,
            "objective_stance": self.objective_stance,
            "summary": self.summary,
        }


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zA-Zа-яёА-ЯЁ0-9]{3,}", (text or "").lower())}


def _has(text: str, *pats: str) -> bool:
    t = text.lower()
    return any(re.search(p, t, re.I) for p in pats)


class _Base:
    id = "base"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        raise NotImplementedError


class LiteralReader(_Base):
    id = "literal"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        act = ling.get("speech_act") or "open_brief"
        e1 = EndState(
            "literal_as_asked",
            "Как написано",
            "Считать задание тем, что сказано на поверхности, без достройки мотива.",
            "Поверхностный артефакт 1:1 к формулировке",
            0.72,
            ["surface_structure"],
            ["unstated_constraints"],
        )
        e2 = EndState(
            "literal_incomplete",
            "Как написано, но дыряво",
            "Поверхность валидна, но слоты пусты — нельзя исполнять как полное ТЗ.",
            "Список пустых слотов + уточнения",
            0.64,
            list((ling.get("concealment") or {}).get("flags") or ["length"]),
            ["felicity"],
        )
        return VariantReading(
            self.id,
            f"Literal illocution={act}. Do not upgrade it to a strategy.",
            [e1, e2],
            bias_flags=["gap_filling"] if e2.confidence > e1.confidence else [],
            evidence_score=0.8,
            novelty_score=0.15,
            notes=["Conservative pole. Exists so generative pole cannot capture the file."],
        )


class OperationalReader(_Base):
    id = "operational"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        trade = _has(text, r"трейд", r"trad", r"pnl", r"ордер")
        promo = _has(text, r"промо", r"ролик", r"карточки описан", r"промпт")
        mock = _has(text, r"макет", r"двойник", r"подоби", r"mockup", r"аватар")
        if trade:
            deliver = "Solution logger + путь к ордерам"
        elif promo:
            deliver = "Promo-lite pack (карточки / ролики / промпты)"
        elif mock:
            deliver = "Цифровой макет индивидуала"
        else:
            deliver = "Consult pack + tech-TZ (работа по запросу)"
        e1 = EndState(
            "ops_deliverable",
            "Операционный выход",
            "Задание = произвести конкретный артефакт, который можно купить или исполнить.",
            deliver,
            0.7,
            ["deliverable_guess"],
            ["acceptance_criteria"],
        )
        e2 = EndState(
            "ops_path",
            "Путь, не файл",
            "Задание = выстроить цепочку решений к ликвидности, не один документ.",
            "Терминал ожидающих ордеров / mining",
            0.55,
            ["liquidity_language"] if _has(text, r"ликвид", r"ордер", r"заказ") else ["inferred"],
            ["counterparty"],
        )
        return VariantReading(
            self.id,
            "What ships. Not what the sentence means.",
            [e1, e2],
            bias_flags=["sku_first"],
            evidence_score=0.62,
            novelty_score=0.35,
            notes=["SKU-first bias is flagged: operational reading is a candidate, not a verdict."],
        )


class GenerativeReader(_Base):
    """Vibrant Capabi: brief → open-ended generative territory."""

    id = "generative"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        unnamed = list(ling.get("unnamed_phenomena") or [])
        e1 = EndState(
            "gen_territory",
            "Открытая генеративная территория",
            "Бриф — вход в пространство вариантов, не запрос с одним правильным ответом.",
            "Набор ветвей (product / ling / money) без раннего collapse",
            0.68,
            unnamed or ["open_brief"],
            ["which_branch_to_fund"],
        )
        e2 = EndState(
            "gen_quality_first",
            "Quality-first, не query-driven",
            "Не отвечать на вопрос. Поднять значения метрик качества, пока территория не стабилизируется.",
            "Metric engine pass (VVI/ER/RRC + disagreement)",
            0.66,
            ["flagship_metric_engine"],
            ["stopping_rule"],
        )
        e3 = EndState(
            "gen_r_and_d",
            "R&D углы",
            "Границы решения ещё не посчитаны — сначала модель границ, потом деплой решений.",
            "Boundary model + unlocked R&D angles",
            0.5,
            ["karimmetrix_18aug"],
            ["hard_frameworks"],
        )
        return VariantReading(
            self.id,
            "Vibrant Capabi: translate every brief into generative territory.",
            [e1, e2, e3],
            bias_flags=[],
            evidence_score=0.48,
            novelty_score=0.82,
            notes=["This reader is allowed to over-generate; assembler will not delete it."],
        )


class AdversarialReader(_Base):
    """Unbiased / contra. Assumes the brief may hide or self-deceive."""

    id = "adversarial"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        conc = ling.get("concealment") or {}
        possible = bool(conc.get("possible_deliberate"))
        e1 = EndState(
            "adv_omission",
            "Умолчание как сигнал",
            "То, чего нет в тексте (агент, цифра, ограничение), и есть настоящее задание.",
            "Карта умолчаний + вопросы без подсказки «правильного» ответа",
            0.6 if possible else 0.42,
            list(conc.get("flags") or ["none"]),
            ["intent_of_omission"],
        )
        e2 = EndState(
            "adv_self_serve",
            "Бриф продаёт себе удобную историю",
            "Формулировка защищает статус автора. Нужен разбор без согласия с самооценкой.",
            "Contra-brief: что будет истиной, если самоописание ложно",
            0.5,
            ["authority_claims"] if _has(text, r"эксперт", r"уже умею", r"i already") else ["default"],
            ["independent_evidence"],
        )
        e3 = EndState(
            "adv_none",
            "Умолчаний нет",
            "Текст достаточно прямой. Не выдумывать заговор.",
            "Идти literal+ops",
            0.45 if not possible else 0.2,
            ["low_concealment"] if not possible else ["overfit_risk"],
            [],
        )
        return VariantReading(
            self.id,
            "Objectivity = keep the contra-reading alive even when it loses.",
            [e1, e2, e3],
            bias_flags=["confirmation"] if possible else ["gap_filling"],
            evidence_score=0.55 if possible else 0.4,
            novelty_score=0.7,
            notes=["Adversarial is not cynicism. It is a reserved slot for the reading that hurts."],
        )


class LinguisticReader(_Base):
    id = "linguistic"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        unnamed = list(ling.get("unnamed_phenomena") or ["none"])
        e1 = EndState(
            "ling_unfold",
            "Развёртка пространств",
            "Задание = провести бриф через несколько теорий и назвать новые свойства.",
            "Linguistic report + unnamed phenomena",
            0.67,
            unnamed,
            ["which_theory_is_load-bearing"],
        )
        e2 = EndState(
            "ling_hidden",
            "Скрытое явление",
            "Анализ должен обозначить то, что, возможно, утаено специально.",
            "Concealment dossier (не обвинение — гипотеза)",
            float((ling.get("concealment") or {}).get("score") or 0.3) + 0.2,
            list((ling.get("concealment") or {}).get("flags") or []),
            ["deliberate_vs_inarticulate"],
        )
        return VariantReading(
            self.id,
            ling.get("deep_structure") or "unfold spaces",
            [e1, e2],
            bias_flags=[],
            evidence_score=0.58,
            novelty_score=0.75,
            notes=["Linguistic side stays unnamed in product copy; it still runs."],
        )


class MetricReader(_Base):
    """Pure metric engine — quality-first, not query-driven."""

    id = "metric"

    def read(self, text: str, lang: str, ling: dict[str, Any]) -> VariantReading:
        n = len(_tokens(text))
        density = min(1.0, n / 80.0)
        e1 = EndState(
            "metric_push",
            "Движок метрик",
            "Не отвечать на запрос. Поднять значения (ясность, RRC, health) выше текущего.",
            "Metric delta pack + stopping rule",
            0.6 + 0.1 * (1 - density),
            ["quality_first"],
            ["target_values"],
        )
        e2 = EndState(
            "metric_gate",
            "Гейт качества",
            "Пока disagreement высокий — не отдавать один ответ клиенту.",
            "Hold + parallel variants",
            0.58,
            ["multi_variant_policy"],
            [],
        )
        return VariantReading(
            self.id,
            "Flagship: metric engine that pushes values higher. Not query-driven.",
            [e1, e2],
            bias_flags=["formal_lock"],
            evidence_score=0.5,
            novelty_score=0.6,
        )


READERS: list[_Base] = [
    LiteralReader(),
    OperationalReader(),
    GenerativeReader(),
    AdversarialReader(),
    LinguisticReader(),
    MetricReader(),
]


def _bias_audit(text: str, variants: list[VariantReading]) -> dict[str, Any]:
    flags = []
    for v in variants:
        flags.extend(v.bias_flags)
    # structural audits
    first_thesis = variants[0].thesis if variants else ""
    same = sum(1 for v in variants if v.thesis == first_thesis)
    collapse = same == len(variants)
    checks = {c: "pass" for c in BIAS_CHECKS}
    if collapse:
        checks["single_reading"] = "fail"
        checks["confirmation"] = "fail"
    if "sku_first" in flags:
        checks["sku_first"] = "watch"
    if "gap_filling" in flags:
        checks["gap_filling"] = "watch"
    if _has(text, r"эксперт", r"гуру", r"лучший"):
        checks["authority"] = "watch"
    sentences = re.split(r"[.!?]\s+", text.strip())
    if len(sentences) >= 2 and _has(sentences[-1], r"главное", r"на самом деле", r"actually"):
        checks["recency"] = "watch"
    checks["formal_lock"] = "pass"
    return {
        "checks": checks,
        "stance": "Keep all end-states. Rank, do not delete. Unknowns stay unknown.",
        "failed": [k for k, v in checks.items() if v == "fail"],
        "watch": [k for k, v in checks.items() if v == "watch"],
    }


def _disagreement(variants: list[VariantReading]) -> float:
    labels = []
    for v in variants:
        for e in v.end_states:
            labels.append(e.id.split("_")[0])
    if not labels:
        return 0.0
    from collections import Counter

    c = Counter(labels)
    top = c.most_common(1)[0][1]
    return round(1.0 - top / max(1, len(labels)), 4)


def _select_end_states(variants: list[VariantReading], k: int = 4) -> list[EndState]:
    pool: list[EndState] = []
    for v in variants:
        pool.extend(v.end_states)
    pool.sort(key=lambda e: e.confidence, reverse=True)
    seen = set()
    out: list[EndState] = []
    for e in pool:
        if e.id in seen:
            continue
        seen.add(e.id)
        out.append(e)
        if len(out) >= k:
            break
    # guarantee generative + adversarial presence if they exist
    must = {"gen_territory", "adv_omission"}
    have = {e.id for e in out}
    for v in variants:
        for e in v.end_states:
            if e.id in must and e.id not in have:
                out.append(e)
                have.add(e.id)
    return out[:6]


class TaskReader:
    name = "Metrix Task Reader"

    def read(self, query: str, lang: str | None = None) -> TaskRead:
        text = (query or "").strip()
        lang = lang or detect_lang(text)
        ling_rep = unfold_linguistic_spaces(text, lang=lang)
        ling = ling_rep.to_dict()
        variants = [r.read(text, lang, ling) for r in READERS]
        audit = _bias_audit(text, variants)
        dis = _disagreement(variants)
        selected = _select_end_states(variants)
        stance = (
            "Objective: several live end-states, explicit unknowns, "
            "no privileged first parse, concealment treated as data."
        )
        summary = (
            f"{self.name}: variants={len(variants)}, "
            f"end_states={len(selected)}, disagreement={dis:.2f}, "
            f"concealment={(ling.get('concealment') or {}).get('score', 0):.2f}, "
            f"bias_watch={audit['watch']}"
        )
        return TaskRead(
            query=text,
            lang=lang,
            variants=variants,
            selected_end_states=selected,
            disagreement=dis,
            bias_audit=audit,
            linguistic=ling,
            objective_stance=stance,
            summary=summary,
        )


def read_task(query: str, lang: str | None = None) -> dict[str, Any]:
    return TaskReader().read(query, lang=lang).to_dict()
