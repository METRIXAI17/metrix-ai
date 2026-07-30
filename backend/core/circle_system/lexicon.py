"""
Lexicons for Circle-System read-in and answer-out.

READ lexemes are used to classify client text (certainty, need, resource).
WRITE lexemes are used when the program emits test-questions and answers.
Warmth is linguistic only — assembly of parameters is a separate path.
"""

from __future__ import annotations

from typing import Any


# ── Read: certainty / polarity markers ─────────────────────────────────────

CERTAIN_YES_RU = (
    "точно да", "однозначно", "гарантированно", "подтверждено", "уже есть",
    "внедрено", "работает", "доказано", "обязательно", "да,", "yes",
    "definitely", "confirmed", "already live", "must", "we have",
)
CERTAIN_NO_RU = (
    "точно нет", "невозможно", "запрещено", "отсутствует", "нет,",
    "не делаем", "нельзя", "never", "impossible", "blocked", "we don't",
    "not available", "out of scope", "отказ",
)
UNCERTAIN_RU = (
    "не знаю", "возможно", "примерно", "кажется", "надо подумать",
    "зависит", "пока не ясно", "tbd", "maybe", "roughly", "unclear",
    "not sure", "depends", "примерно", "около", "или", "?",
)

# ── Read: need / layer markers (architectural layers as needs) ─────────────

LAYER_NEED_MARKERS: dict[str, tuple[str, ...]] = {
    "identity": ("бренд", "имя", "позиционирование", "brand", "naming", "ва", "va", "virtual asset"),
    "orientation": ("ориент", "ниша", "рынок", "сегмент", "industry", "market", "who is client"),
    "resources": ("ресурс", "бюджет", "команда", "стек", "ledger", "бюджет", "staff", "stack"),
    "operations": ("процесс", "ops", "операц", "workflow", "sla", "support", "support"),
    "product": ("продукт", "фича", "mvp", "spec", "тз", "tech write", "тех райт"),
    "pilot": ("пилот", "pilot", "mvp запуск", "пробный", "14 дн", "30 дн"),
    "metrics": ("метрик", "kpi", "vvi", "er", "rrc", "roi", "измер"),
    "integration": ("интеграц", "api", "webhook", "crm", "ledger", "collab"),
    "orchestration": ("оркестр", "автопилот", "dynamic", "настрой", "конфиг"),
    "expertise": ("эксперт", "консалт", "life app", "deep tech", "архитектур"),
}

# ── Read: business resource types ──────────────────────────────────────────

RESOURCE_MARKERS: dict[str, tuple[str, ...]] = {
    "compute": ("gpu", "cpu", "cloud", "vps", "token", "api cost", "compute"),
    "data": ("датасет", "crm", "ledger", "лог", "история", "база", "data"),
    "human": ("команда", "va", "бренд", "менеджер", "аналитик", "writer", "branding"),
    "capital": ("бюджет", "инвест", "runway", "cash", "оплата", "funding"),
    "channel": ("x.com", "upwork", "telegram", "сайт", "канал", "лид", "ads"),
    "ip": ("патент", "спека", "тз", "модель", "проприетар", "know-how"),
}

# ── Write: test-question shells (assembly, not heat) ───────────────────────

TEST_QUESTION_SHELLS_RU = {
    "binary": "Тест [{slot}]: выберите один вариант — ТОЧНО ДА / ТОЧНО НЕТ / НЕ ОПРЕДЕЛЕНО.",
    "scale": "Тест [{slot}]: оцените по шкале 0–4 (0=нет, 2=частично, 4=полностью).",
    "choice": "Тест [{slot}]: выберите один из вариантов: {options}.",
    "numeric": "Тест [{slot}]: укажите число (единица: {unit}). Если неизвестно — «не знаю».",
    "assembly": "Сборка [{slot}]: какие 2–3 условия должны сойтись, чтобы параметр стал ТОЧНО ДА?",
}

TEST_QUESTION_SHELLS_EN = {
    "binary": "Test [{slot}]: pick one — CERTAIN YES / CERTAIN NO / UNDEFINED.",
    "scale": "Test [{slot}]: rate 0–4 (0=none, 2=partial, 4=full).",
    "choice": "Test [{slot}]: pick one of: {options}.",
    "numeric": "Test [{slot}]: give a number (unit: {unit}). If unknown — say 'unknown'.",
    "assembly": "Assembly [{slot}]: which 2–3 conditions must hold for this to become CERTAIN YES?",
}

# ── Write: answer warmth bands (linguistic only) ───────────────────────────

WARMTH_BANDS: dict[str, dict[str, Any]] = {
    "cold": {
        "score_range": (0.0, 0.25),
        "tone": "formal_sparse",
        "lexemes_ru": ("факт:", "параметр:", "статус:", "значение:"),
        "lexemes_en": ("fact:", "param:", "status:", "value:"),
        "rule": "No metaphors. Short clauses. Numbers first.",
    },
    "cool": {
        "score_range": (0.25, 0.45),
        "tone": "professional",
        "lexemes_ru": ("по данным", "следует", "рекомендуется", "в рамках"),
        "lexemes_en": ("based on", "it follows", "recommended", "within"),
        "rule": "Clear structure, light connectors, no hype.",
    },
    "neutral": {
        "score_range": (0.45, 0.60),
        "tone": "balanced",
        "lexemes_ru": ("можно", "имеет смысл", "практический шаг", "согласуется"),
        "lexemes_en": ("you can", "it makes sense", "practical step", "aligns"),
        "rule": "Balanced advice + one concrete next action.",
    },
    "warm": {
        "score_range": (0.60, 0.80),
        "tone": "collaborative",
        "lexemes_ru": ("давайте", "вместе", "уже близко", "хорошая опора"),
        "lexemes_en": ("let's", "together", "almost there", "strong base"),
        "rule": "Partner voice; celebrate partial wins; still factual.",
    },
    "hot": {
        "score_range": (0.80, 1.01),
        "tone": "energetic_careful",
        "lexemes_ru": ("сильный сигнал", "можно ускорять", "готово к пилоту"),
        "lexemes_en": ("strong signal", "safe to accelerate", "pilot-ready"),
        "rule": "High energy only if assembly_score is high; never fake certainty.",
    },
}

# ── Write: status labels ───────────────────────────────────────────────────

STATUS_LABELS = {
    "certain_yes": {"ru": "ТОЧНО ДА", "en": "CERTAIN YES", "code": "CY"},
    "certain_no": {"ru": "ТОЧНО НЕТ", "en": "CERTAIN NO", "code": "CN"},
    "uncertain": {"ru": "НЕОПРЕДЕЛЕНО", "en": "UNDEFINED", "code": "U"},
}

# ── Super program parameter families (match targets) ───────────────────────

SUPER_PROGRAM_FAMILIES = (
    "synthesis_core",
    "reality_layer_interface",
    "symmetry_bridge",
    "value_proposition_engine",
    "engagement_transaction_protocol",
    "metrix_ledger_operational_core",
)

# Excel Deep Tech row references (4 Бизнеса.xlsx)
DEEP_TECH_COMPONENTS_EXCEL = (
    "SYNTHESIS CORE",
    "REALITY LAYER INTERFACE",
    "SYMMETRY BRIDGE",
    "VALUE PROPOSITION ENGINE",
    "ENGAGEMENT & TRANSACTION PROTOCOL",
    "METRIX LEDGER & OPERATIONAL CORE",
)

# Cross-refs from Market Units notes: 3→1..4, 4→5..7, models=open
REFERENCE_MAP = {
    "ref_3": {"points": [1, 2, 3, 4], "meaning": "parameter_dev + indirect_certainty chain"},
    "ref_4": {"points": [5, 6, 7], "meaning": "super_speed + super_program + metric_compose"},
    "models": "open",
    "pilot_model": "differential_equation_predetermined_indicator",
}


def detect_markers(text: str, table: dict[str, tuple[str, ...]]) -> dict[str, float]:
    """Return hit strength [0..1] per key for any marker table."""
    low = (text or "").lower()
    out: dict[str, float] = {}
    for key, words in table.items():
        hits = sum(1 for w in words if w.lower() in low)
        if hits:
            out[key] = min(1.0, hits / max(2.0, len(words) * 0.15))
    return out


def lexicon_catalog() -> dict[str, Any]:
    return {
        "module": "circle_system.lexicon",
        "read": {
            "certain_yes": list(CERTAIN_YES_RU),
            "certain_no": list(CERTAIN_NO_RU),
            "uncertain": list(UNCERTAIN_RU),
            "layers": {k: list(v) for k, v in LAYER_NEED_MARKERS.items()},
            "resources": {k: list(v) for k, v in RESOURCE_MARKERS.items()},
        },
        "write": {
            "test_shells_ru": TEST_QUESTION_SHELLS_RU,
            "test_shells_en": TEST_QUESTION_SHELLS_EN,
            "warmth_bands": WARMTH_BANDS,
            "status_labels": STATUS_LABELS,
        },
        "super_program_families": list(SUPER_PROGRAM_FAMILIES),
        "deep_tech_components_excel": list(DEEP_TECH_COMPONENTS_EXCEL),
        "reference_map": REFERENCE_MAP,
    }
