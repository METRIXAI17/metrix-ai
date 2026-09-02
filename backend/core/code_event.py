"""Data model for agreed-model code. Not a trading signal.

ModelState → CodeEvent → close_trigger / stop_trigger.
Live updates are the current version of the model, as-is.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

MODEL_VERSION = "1.8.0"


@dataclass
class Trigger:
    kind: str  # price | time | window | amplitude_death | invalidation | two_leg_break
    rule: str
    price: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.rule, "price": self.price}


@dataclass
class ModelState:
    model_id: str
    version: str = MODEL_VERSION
    params: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"model_id": self.model_id, "version": self.version, "params": self.params}


@dataclass
class CodeEvent:
    """Event emitted by an agreed model. Public copy must not call this a signal."""

    model_id: str
    model_version: str
    symbol: str
    side: str  # buy | sell | flat
    reason: str
    entry: float
    stop: Trigger
    close: Trigger
    as_of_ms: int = 0
    tag: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "code_event",
            "legal": "код согласованной модели, не сигнал",
            "model_id": self.model_id,
            "model_version": self.model_version,
            "symbol": self.symbol,
            "side": self.side,
            "reason": self.reason,
            "entry": self.entry,
            "stop_trigger": self.stop.as_dict(),
            "close_trigger": self.close.as_dict(),
            "as_of_ms": self.as_of_ms,
            "tag": self.tag,
            "meta": self.meta,
        }


def from_robot_signal(sig: Any, *, model_id: str, close: Trigger | None = None) -> CodeEvent:
    sl = float(getattr(sig, "sl", 0) or 0)
    tp = float(getattr(sig, "tp", 0) or 0)
    side = getattr(getattr(sig, "side", None), "value", None) or str(getattr(sig, "side", "flat"))
    stop = Trigger(
        kind="price",
        rule="инвалидация тезиса модели — стоп-триггер, не «откат настроения»",
        price=sl,
    )
    if close is None:
        close = Trigger(
            kind="price" if tp else "rule",
            rule="закрывающий триггер модели (место / окно / смерть амплитуды / слом ноги)",
            price=tp,
        )
    return CodeEvent(
        model_id=model_id,
        model_version=MODEL_VERSION,
        symbol=str(getattr(sig, "symbol", "")),
        side=str(side),
        reason=str(getattr(sig, "reason", "")),
        entry=float(getattr(sig, "entry", 0) or 0),
        stop=stop,
        close=close,
        tag=str(getattr(sig, "tag", "") or ""),
        meta=dict(getattr(sig, "meta", None) or {}),
    )


def public_copy(event: CodeEvent | dict[str, Any]) -> dict[str, Any]:
    d = event.as_dict() if isinstance(event, CodeEvent) else dict(event)
    d.pop("raw_signal", None)
    return d
