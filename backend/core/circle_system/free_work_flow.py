"""
Free work flow after consultation — start button path.

Client: start free work → system self-clarifies → quality niche answer
→ day phases + quizzes → tech write spine.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR
from backend.core.circle_system.deep_tech_pipeline import DeepTechMetrixPipeline
from backend.core.circle_system.niche_answer_base import NicheAnswerBase
from backend.core.circle_system.linguistic_warmth import LinguisticWarmthEngine


_STORE = DATA_DIR / "free_work"
_STORE.mkdir(parents=True, exist_ok=True)


class FreeWorkFlow:
    name = "Free Work Flow"

    def __init__(self) -> None:
        self.niche = NicheAnswerBase()
        self.deep = DeepTechMetrixPipeline()
        self.warmth = LinguisticWarmthEngine()

    def start(
        self,
        *,
        business: str,
        industry_id: str,
        track: str = "all",
        name: str = "",
        contact: str = "",
        lang: str = "ru",
        natural_direction: str | None = None,
        numbers: dict[str, Any] | None = None,
        request_id: str | None = None,
        include_founders_lane: bool = False,  # reserved; not exposed to clients yet
        resources: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        _ = include_founders_lane  # deferred product decision
        work_id = str(uuid.uuid4())
        numbers = dict(numbers or {})

        # Deep tech pass (self-orientation)
        circle = self.deep.run(
            business,
            industry_id=industry_id,
            lang=lang,
            product_name="Metrix Free Work",
            client_label=name or "client",
            core_metrics=None,
            resources=resources,
        )
        direction = natural_direction or (
            (circle.get("layers") or {}).get("confirmed_layers") or ["ops"]
        )
        # prefer category-like: use super program primary slot affinity
        dir_guess = track if track in ("ops", "product", "promotion") else None
        if not dir_guess:
            # from certain params
            slots = {p.get("slot") for p in (circle.get("certainty") or {}).get("parameters") or []}
            if "pilot_scope" in slots or "offer" in slots:
                dir_guess = "product"
            elif "metric" in slots:
                dir_guess = "ops"
            else:
                dir_guess = "ops"

        niche_ans = self.niche.resolve(
            industry_id,
            track=dir_guess if track == "all" else track,
            natural_direction=dir_guess,
            lang=lang,
            business=business,
            numbers=numbers,
        )

        # Merge circle uncertainties into extra clarifications
        extra_q = list(niche_ans.get("clarification_questions") or [])
        for item in (circle.get("super_speed") or {}).get("items") or []:
            for q in (item.get("questions") or [])[:2]:
                extra_q.append(
                    {
                        "id": q.get("qid"),
                        "field": item.get("slot"),
                        "kind": q.get("kind"),
                        "question": q.get("text"),
                        "param_id": item.get("param_id"),
                        "from": "super_speed",
                    }
                )
        # de-dupe by id
        seen = set()
        clar_q = []
        for q in extra_q:
            qid = q.get("id") or q.get("field")
            if qid in seen:
                continue
            seen.add(qid)
            clar_q.append(q)
            if len(clar_q) >= 8:
                break

        asm = float((circle.get("assembly") or {}).get("assembly_score") or 0.4)
        warmth = self.warmth.score(
            assembly_score=asm,
            certain_yes_ratio=float((circle.get("certainty") or {}).get("counts", {}).get("certain_yes", 0))
            / max(1, sum((circle.get("certainty") or {}).get("counts", {}).values()) or 1),
            lang=lang,
        )
        rendered = self.warmth.render_answer(
            status="certain_yes" if niche_ans.get("quality_gate") else "uncertain",
            body_fact=niche_ans.get("answer") or "",
            next_action=(
                "Нажмите «уточнить» по открытым полям или продолжайте чеклист free work."
                if lang.startswith("ru")
                else "Clarify open fields or continue free-work checklist."
            ),
            warmth=warmth,
            lang=lang,
        )

        phases = self.niche.free_work_phases(lang)
        tech_specs = (circle.get("terminal_specs") or {}).get("terminal_functions") or []
        tech_md = "\n\n".join(
            f"### {t.get('title')}\n{t.get('markdown', '')}" for t in tech_specs[:4]
        )

        state = {
            "work_id": work_id,
            "request_id": request_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "industry_id": industry_id,
            "track": track,
            "direction": niche_ans.get("direction"),
            "name": name,
            "contact": contact,
            "lang": lang,
            "business": business,
            "numbers": numbers,
            "phase_index": 0,
            "answers": {},
            "status": "started",
        }
        self._save(work_id, state)

        ru = lang.startswith("ru")
        return {
            "ok": True,
            "module": self.name,
            "work_id": work_id,
            "cta": {
                "label_ru": "Начать работу бесплатно",
                "label_en": "Start free work",
                "label": "Начать работу бесплатно" if ru else "Start free work",
                "active": True,
            },
            "quality_answer": {
                **niche_ans,
                "rendered": rendered,
                "warmth": warmth,
            },
            "self_clarifications": clar_q,
            "needs_clarify_before_best": bool(clar_q) and not niche_ans.get("quality_gate"),
            "phases": phases,
            "current_phase": phases[0] if phases else None,
            "free_work_checklist": niche_ans.get("free_work_checklist"),
            "success_metric": niche_ans.get("success_metric"),
            "out_of_scope_default": niche_ans.get("out_of_scope_default"),
            "tech_write_preview": tech_md[:4000],
            "circle_summary": {
                "assembly_score": (circle.get("assembly") or {}).get("assembly_score"),
                "chain_id": circle.get("chain_id"),
                "consistency": (circle.get("layers") or {}).get("consistency_score"),
                "counts": (circle.get("certainty") or {}).get("counts"),
                "primary_super_program": ((circle.get("super_program") or {}).get("primary") or {}).get(
                    "excel_name"
                ),
                "autopilot_ready": (circle.get("layers") or {}).get("autopilot_ready"),
            },
            "product_surfaces": (circle.get("product_surfaces") or {}).get("tech_write"),
            "next_ui": {
                "show_phases": True,
                "show_clarify_form": True,
                "show_founders_lane": False,
                "primary_button": "submit_clarifications",
            },
        }

    def submit_clarifications(
        self,
        work_id: str,
        answers: dict[str, Any],
        *,
        lang: str | None = None,
    ) -> dict[str, Any]:
        state = self._load(work_id)
        if not state:
            return {"ok": False, "error": "work_id not found"}
        lang = lang or state.get("lang") or "ru"
        merged_nums = {**(state.get("numbers") or {}), **(answers or {})}
        # also store under answers
        state["answers"] = {**(state.get("answers") or {}), **(answers or {})}
        state["numbers"] = merged_nums
        state["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Re-resolve quality with filled numbers
        niche_ans = self.niche.resolve(
            state["industry_id"],
            track=state.get("track"),
            natural_direction=state.get("direction"),
            lang=lang,
            business=state.get("business") or "",
            numbers=merged_nums,
        )

        # Re-run assembly with test answers if CY/CN provided
        circle = self.deep.run(
            state.get("business") or "",
            industry_id=state["industry_id"],
            lang=lang,
            test_answers=state["answers"],
            client_label=state.get("name") or "client",
        )

        state["phase_index"] = min(
            int(state.get("phase_index") or 0) + (1 if niche_ans.get("quality_gate") else 0),
            2,
        )
        state["status"] = "clarified" if niche_ans.get("quality_gate") else "needs_more"
        self._save(work_id, state)

        phases = self.niche.free_work_phases(lang)
        idx = int(state["phase_index"])
        warmth = (circle.get("warmth") or {})
        rendered = self.warmth.render_answer(
            status="certain_yes" if niche_ans.get("quality_gate") else "uncertain",
            body_fact=niche_ans.get("answer") or "",
            next_action=(
                "Переходите к tech write / чеклисту фазы."
                if lang.startswith("ru")
                else "Continue to tech write / phase checklist."
            ),
            warmth=warmth if warmth.get("band") else self.warmth.score(
                assembly_score=float((circle.get("assembly") or {}).get("assembly_score") or 0.5),
                certain_yes_ratio=0.5,
                lang=lang,
            ),
            lang=lang,
        )

        return {
            "ok": True,
            "work_id": work_id,
            "status": state["status"],
            "quality_answer": {**niche_ans, "rendered": rendered},
            "open_clarifications": niche_ans.get("clarification_questions") or [],
            "phases": phases,
            "current_phase": phases[idx] if idx < len(phases) else phases[-1],
            "phase_index": idx,
            "assembly_score": (circle.get("assembly") or {}).get("assembly_score"),
            "tech_write_preview": "\n\n".join(
                f"### {t.get('title')}\n{t.get('markdown', '')}"
                for t in ((circle.get("terminal_specs") or {}).get("terminal_functions") or [])[:4]
            )[:4000],
            "message_ru": "Ответ обновлён по уточнениям. Можно продолжать free work.",
            "message_en": "Answer updated from clarifications. Continue free work.",
        }

    def advance_phase(self, work_id: str) -> dict[str, Any]:
        state = self._load(work_id)
        if not state:
            return {"ok": False, "error": "work_id not found"}
        phases = self.niche.free_work_phases(state.get("lang") or "ru")
        idx = min(int(state.get("phase_index") or 0) + 1, len(phases) - 1)
        state["phase_index"] = idx
        state["status"] = "phase_" + phases[idx]["id"]
        self._save(work_id, state)
        return {
            "ok": True,
            "work_id": work_id,
            "phase_index": idx,
            "current_phase": phases[idx],
            "phases": phases,
            "done_free_path": idx >= len(phases) - 1,
            "next_after_free": {
                "ru": "Опционально: paid pilot (ops/product/promo). Main — только после success.",
                "en": "Optional: paid pilot (ops/product/promo). Main only after success.",
            },
        }

    def get(self, work_id: str) -> dict[str, Any]:
        state = self._load(work_id)
        if not state:
            return {"ok": False, "error": "work_id not found"}
        return {"ok": True, "state": {k: v for k, v in state.items() if k != "business" or True}}

    def _save(self, work_id: str, state: dict[str, Any]) -> None:
        path = _STORE / f"{work_id}.json"
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self, work_id: str) -> dict[str, Any] | None:
        path = _STORE / f"{work_id}.json"
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
