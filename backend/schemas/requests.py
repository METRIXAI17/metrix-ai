"""
Схемы запросов и ответов.

Простота: клиент присылает industry + business text (+ опции).
Система возвращает ориентацию, идею, breakdown, метрики, next steps.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class TrackPreference(str, Enum):
    PRODUCT = "product"
    MODELS = "models"
    PROMOTION = "promotion"
    ALL = "all"


@dataclass
class ClientRequest:
    """Входной клиентский запрос (как форма на сайте)."""

    industry: str
    business: str
    track: str = "all"
    name: str = ""
    contact: str = ""
    program_id: str | None = None
    # UI language (en|ru). Empty → auto-detect from business text.
    lang: str = ""
    extra_params: dict[str, float] = field(default_factory=dict)
    # Custom success metrics positioning → becomes unique TZ for the query
    # Example: {"weights": {"iroi": 0.4}, "targets": {"clarity": 0.7}, "priority": ["iroi","impact"]}
    success_metrics: dict[str, Any] = field(default_factory=dict)
    enable_self_improve: bool = True
    enable_fin_models: bool = True
    enable_monetization: bool = True
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.industry or not str(self.industry).strip():
            errors.append("industry is required")
        if not self.business or len(self.business.strip()) < 20:
            errors.append("business description must be at least 20 characters")
        track = (self.track or "all").lower()
        if track not in ("product", "models", "promotion", "all", ""):
            errors.append("track must be product|models|promotion|all")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClientRequest":
        lang_raw = str(data.get("lang") or data.get("language") or "").strip().lower()
        if lang_raw not in ("en", "ru", ""):
            lang_raw = ""
        return cls(
            industry=str(data.get("industry") or data.get("industry_id") or ""),
            business=str(data.get("business") or data.get("business_text") or ""),
            track=str(data.get("track") or "all"),
            name=str(data.get("name") or ""),
            contact=str(data.get("contact") or data.get("email") or ""),
            program_id=data.get("program_id"),
            lang=lang_raw,
            extra_params=dict(data.get("extra_params") or {}),
            success_metrics=dict(data.get("success_metrics") or {}),
            enable_self_improve=bool(data.get("enable_self_improve", True)),
            enable_fin_models=bool(data.get("enable_fin_models", True)),
            enable_monetization=bool(data.get("enable_monetization", True)),
            request_id=str(data.get("request_id") or uuid4()),
        )


@dataclass
class ProcessResponse:
    """Полный ответ пайплайна — то, что видит клиент / витрина."""

    ok: bool
    request_id: str
    industry: str
    operating_mode: str
    orientation: dict[str, Any]
    demo_idea: dict[str, Any]
    breakdown: dict[str, Any]
    metrics: dict[str, Any]
    zones_touched: list[str]
    fin_models: list[dict[str, Any]]
    monetization: dict[str, Any]
    structure: dict[str, Any]
    self_improve: dict[str, Any]
    next_steps: list[str]
    decision_core: dict[str, Any] = field(default_factory=dict)
    operational_analytics: dict[str, Any] = field(default_factory=dict)
    success_metrics: dict[str, Any] = field(default_factory=dict)
    # Multi-idea portfolio for operational success (rank 1 == demo_idea)
    demo_ideas: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
