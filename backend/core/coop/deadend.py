"""DeadendRouter — change mode, shorten output, ask one next question. No same-prompt retry."""

from __future__ import annotations

from typing import Any

from backend.core.coop.brief_normalizer import classify_order, normalize_brief
from backend.core.coop.consult_patterns.flags import detect_flags, has_flag


class DeadendRouter:
    """Programmatic unblocks for consult/coop deadlocks."""

    name = "DeadendRouter"

    def route(
        self,
        brief: str,
        *,
        flags: list[dict[str, Any]] | None = None,
        prior_style: dict[str, str] | None = None,
        silent: bool = False,
    ) -> dict[str, Any]:
        flags = flags if flags is not None else detect_flags(brief)
        norm = normalize_brief(brief, prior_style=prior_style)
        order = norm["order_type"]
        codes: list[str] = []
        next_q = ""
        mode = "PASS"
        page = ""
        assumed = dict(norm.get("assumed") or {})

        if has_flag(flags, "P6"):
            codes.append("MISSING_METRIC")
            next_q = "Сколько заявок в неделю и кто обязан взять за N минут?"
            assumed.setdefault("leads_week", "ASSUMED: поток уже есть, цифра неизвестна")
            mode = "UNBLOCK"
            page = (
                "Нет числа. Один вопрос или ASSUMED. Полный пакет не собираем. "
                "KPI — видимость потерь и время реакции, не рост выручки."
            )
        if has_flag(flags, "P1"):
            codes.append("MULTI_LOCO")
            next_q = next_q or "Какой один поток берём сейчас — заявки/касса или серия?"
            if silent:
                assumed["chosen_stream"] = "ASSUMED: поток с деньгами ближе (заявки/касса); остальное в backlog"
            mode = "UNBLOCK"
            page = (
                "Больше двух локомотивов. Выбрать один TYPE_A-контур или одну TYPE_B-серию. "
                "Молчит — берём заявки/кассу, остальное backlog."
            )
        if has_flag(flags, "P2") or has_flag(flags, "P5") or has_flag(flags, "P8"):
            codes.append("MAGIC_SALES")
            next_q = next_q or "Какой KPI реакции/статуса вместо «+продажи»?"
            mode = "UNBLOCK"
            page = (
                "KPI «+продажи» с контура отказываем. Замена: время реакции, доля без хозяина, "
                "сгоревшие за неделю. Трафик не растим."
            )
        if has_flag(flags, "P7"):
            codes.append("SCOPE_EXPLOSION")
            next_q = next_q or "Что входит в пакет часов, что сверх — отдельной оценкой?"
            mode = "UNBLOCK"
            page = "Лишняя ветка не в том же чеке. Пакет часов + оценка сверх."
        if order == "TYPE_B" and prior_style and not any(norm["style_lock"].values()):
            codes.append("STYLE_COLLAPSE")
            next_q = next_q or "Повторяем в прошлом замке или это новый бриф?"
            mode = "UNBLOCK"
            page = "Вернули style_lock прошлого заказа. Смена жанра = новый бриф, не тот же ретейнер."

        deadlock = bool(codes)
        return {
            "module": self.name,
            "mode": mode,
            "deadlock": deadlock,
            "codes": codes,
            "next_question": next_q,
            "short_page": page[:600],
            "assumed": assumed,
            "order_type": order,
            "flags": [f.get("id") for f in flags],
            "allow_codegen": not (
                has_flag(flags, "P6") or has_flag(flags, "P1") or "MAGIC_SALES" in codes
            ),
        }


def is_deadlock(brief: str, flags: list[dict[str, Any]] | None = None) -> bool:
    flags = flags if flags is not None else detect_flags(brief)
    return has_flag(flags, "P6") or has_flag(flags, "P1") or has_flag(flags, "P2")
