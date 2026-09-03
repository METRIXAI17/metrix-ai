"""
Main Operational Analytics Engine (OAE)
======================================

Другая логика, не «просто scoring seeds»:

1. **Constructor of a certain form**
   Неопределённые / размытые параметры не отбрасываются —
   они трактуются как *конструктор определённой формы*:
   скелет, в который можно «влить» недостающую геометрию.

2. **Dynamic embedding assembly**
   Из параметров (известных + конструкторов void) собирается
   лёгкий embedding-вектор (не нейросеть, а детерминированная
   сборка осей/маяков/success-весов) — «смысловой стержень» запроса.

3. **Deep analysis on embedding**
   Кластеры, энергии, напряжения, сопоставление с ready solutions.

4. **Reduce back to user request**
   Результат глубокого слоя сжимается обратно в язык клиента.

5. **Answer shift parameters**
   Насколько ответ должен сдвинуться от «голого seed» к запросу.

6. **Abstract coordinates (double bottom)**
   Список абстрактных координат от ready solutions, которые
   «вылетают» как второй слой (double bottom effect).

7. **Reverse void ricochet (RRC)**
   Рикошет обратной пустоты: void → reverse link → reassembly
   (reverse refragmentation phenomenon).

Интегрирует:
- Pragma Collection phenomena (splitting points)
- System log features
- Custom success metrics influence
- Decision Core mode

Hooks for:
- block 18: paid product core (meaning vectors)
- block 19: generativity concept
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from backend.core.metrics import compute_core_metrics
from backend.core.pragma_phenomena import evaluate_pragma_phenomena
from backend.zones.product_sol import IDEA_SEEDS


# ── Embedding dimension labels (stable order) ────────────────────────────────
EMBED_DIMS = (
    "value",
    "urgency",
    "complexity",
    "money",
    "risk",
    "product",
    "models",
    "promo",
    "clarity",
    "void_mass",  # constructor energy from undefined params
    "success_pull",
    "log_gravity",
)


@dataclass
class ConstructorSlot:
    """
    Конструктор определённой формы для undefined/vague параметра.

    form_type — какой «каркас» ставим вместо пустоты
    (acceptance / actor / metric / channel / constraint).
    """

    param_name: str
    form_type: str
    openness: float  # 0=almost defined, 1=fully vague
    inject_dims: dict[str, float]
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmbeddingBundle:
    """Собранный embedding + метаданные."""

    vector: list[float]
    dims: list[str]
    norm: float
    known_mass: float
    constructor_mass: float
    assembly_notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector": [round(x, 5) for x in self.vector],
            "dims": self.dims,
            "norm": round(self.norm, 5),
            "known_mass": round(self.known_mass, 4),
            "constructor_mass": round(self.constructor_mass, 4),
            "assembly_notes": self.assembly_notes,
        }


@dataclass
class AbstractCoordinate:
    """
    Абстрактная координата «второго дна» (double bottom).

    Вылетает из ready solution, когда embedding близок по
    латентной оси, даже если title seed другой.
    """

    id: str
    label: str
    source_solution: str
    track: str
    coordinate: list[float]
    flyout_strength: float
    latent_role: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RicochetEvent:
    """Один акт reverse void ricochet."""

    void_name: str
    reverse_link: str
    energy_in: float
    energy_out: float
    reassembled_fragment: str
    rrc_delta: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OAEResult:
    constructors: list[dict[str, Any]]
    embedding: dict[str, Any]
    deep_analysis: dict[str, Any]
    reduced_to_request: dict[str, Any]
    answer_shift: dict[str, Any]
    abstract_coordinates: list[dict[str, Any]]
    ricochet: dict[str, Any]
    pragma: dict[str, Any]
    demo_ideas: list[dict[str, Any]]
    processing_logic: str
    metrics_delta: dict[str, Any]
    summary: str
    # slots for future blocks
    paid_hook: dict[str, Any]
    generative_hook: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": "Main Operational Analytics Engine",
            "constructors": self.constructors,
            "embedding": self.embedding,
            "deep_analysis": self.deep_analysis,
            "reduced_to_request": self.reduced_to_request,
            "answer_shift": self.answer_shift,
            "abstract_coordinates": self.abstract_coordinates,
            "ricochet": self.ricochet,
            "pragma": self.pragma,
            "demo_ideas": self.demo_ideas,
            "processing_logic": self.processing_logic,
            "metrics_delta": self.metrics_delta,
            "summary": self.summary,
            "paid_hook": self.paid_hook,
            "generative_hook": self.generative_hook,
        }


class OperationalAnalyticsEngine:
    """Main Operational Analytics Engine."""

    name = "Main Operational Analytics Engine"

    # map vague/missing param names → constructor form
    FORM_MAP = {
        "goal": "outcome_frame",
        "actors": "role_lattice",
        "inputs": "signal_port",
        "process": "value_pipeline",
        "constraints": "bound_shell",
        "metrics": "success_gauge",
        "risks": "void_membrane",
        "monetization": "revenue_hinge",
        "default": "open_manifold",
    }

    def run(
        self,
        *,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
        idea_title: str,
        vvi: float,
        er: float,
        rrc: float,
        health: float,
        info_roi: float,
        success_card: dict[str, Any] | None = None,
        system_features: dict[str, Any] | None = None,
        decision_mode: str = "scoring",
        missing_params: list[str] | None = None,
        portfolio_ideas: list[dict[str, Any]] | None = None,
    ) -> OAEResult:
        scores = orientation.get("scores") or {}
        axes = (orientation.get("frame") or {}).get("axes") or {}
        pmap = (orientation.get("parameter_map") or {})
        params = dict(pmap.get("params") or {})
        missing = list(missing_params or pmap.get("missing") or [])
        success_card = success_card or {}
        sys_f = system_features or {}
        influence = success_card.get("influence") or {}

        # ── 1. Constructors from vague/undefined ─────────────────────────
        constructors = self._build_constructors(missing, params, vvi, axes)

        # ── 2. Assemble embedding ────────────────────────────────────────
        emb = self._assemble_embedding(
            axes, scores, params, constructors, success_card, sys_f
        )

        # ── 3. Deep analysis ─────────────────────────────────────────────
        deep = self._deep_analyze(emb, industry_id, scores, constructors)

        # ── 4. Pragma splitting ──────────────────────────────────────────
        sc_comp = float(success_card.get("weighted_composite") or 0.5)
        sc_tgt = float((success_card.get("tz") or {}).get("composite_target") or 0.62)
        pragma = evaluate_pragma_phenomena(
            vvi=vvi,
            er=er,
            rrc=rrc,
            health=health,
            readiness=float(scores.get("readiness", 0.5)),
            overall=float(scores.get("overall_orientation", 0.5)),
            info_roi=info_roi,
            success_composite=sc_comp,
            success_target=sc_tgt,
            product_fit=float(scores.get("product_fit", 0.5)),
            promo_fit=float(scores.get("promo_fit", 0.5)),
        )

        # ── 5. Abstract coordinates (double bottom) ──────────────────────
        abstract = self._abstract_coordinates(
            emb, industry_id, idea_title, deep, pragma.demo_fast_path
        )

        # ── 6. Reverse void ricochet ─────────────────────────────────────
        ricochet_gain = float(influence.get("oae_ricochet_gain") or 1.0)
        ricochet = self._reverse_void_ricochet(
            constructors, rrc, er, ricochet_gain, decision_mode
        )

        # ── 7. Answer shift ──────────────────────────────────────────────
        shift_sens = float(influence.get("oae_shift_sensitivity") or 0.8)
        answer_shift = self._answer_shift(
            emb, deep, business_text, idea_title, shift_sens, scores
        )

        # ── 8. Reduce back to request ────────────────────────────────────
        reduced = self._reduce_to_request(
            business_text, idea_title, deep, abstract, answer_shift, ricochet
        )

        # ── 9. Demo ideas (portfolio + abstract flyouts) ─────────────────
        demo_ideas = self._demo_ideas(
            industry_id,
            idea_title,
            abstract,
            pragma,
            decision_mode,
            reduced,
            portfolio_ideas=portfolio_ideas,
        )

        # ── 10. Metrics delta after OAE ──────────────────────────────────
        rrc_after = min(0.98, rrc + float(ricochet.get("total_rrc_delta") or 0))
        vvi_after = max(0.05, vvi - 0.04 * len(constructors) * 0.15)
        metrics_after = compute_core_metrics(
            known_params=max(3, len(params)),
            required_params=max(8, len(params) + len(missing)),
            ambiguity_score=vvi_after * 0.8,
            conflict_score=0.06,
            missing_critical=max(0, len(missing) // 3),
            detected_errors=max(1, len(constructors)),
            actionable_errors=max(1, len(constructors)),
            improvement_delta=min(1.0, (rrc_after - rrc) + 0.1),
            fragments=max(4, len(abstract) + 2),
            successful_reassemblies=max(1, int(ricochet.get("events_count") or 1)),
            structure_entropy=0.48,
            reverse_links=max(1, int(ricochet.get("events_count") or 1)),
            forward_links=max(2, len(EMBED_DIMS) // 2),
        )
        metrics_delta = {
            "vvi_before": round(vvi, 4),
            "vvi_after": round(vvi_after, 4),
            "rrc_before": round(rrc, 4),
            "rrc_after": round(rrc_after, 4),
            "health_after": round(metrics_after.health_score, 4),
            "core_after": metrics_after.to_dict(),
        }

        logic = self._logic_label(decision_mode, pragma, constructors)

        paid_hook = {
            "block": 18,
            "status": "implemented",
            "note": (
                "Paid Product Core: System Design Library · Virtual Chips · "
                "Function Engine · Energy Flow (Market Units) · Calm Point · Mega Map"
            ),
            "candidate": info_roi >= 1.8 and sc_comp >= 0.5,
            "inputs_for_paid": [
                "reduced_to_request",
                "embedding",
                "answer_shift",
                "success_tz",
                "abstract_coordinates",
                "demo_ideas",
            ],
            "module_path": "backend.paid.orchestrator.PaidProductCore",
        }
        generative_hook = {
            "block": 19,
            "status": "slot_ready",
            "note": "Generativity concept will expand abstract_coordinates + demo_ideas",
            "should_run": decision_mode
            in ("generative_development", "dual_ricochet")
            or pragma.demo_fast_path,
            "inputs_for_gen": ["abstract_coordinates", "embedding", "pragma.triggered"],
        }

        summary = (
            f"{self.name}: logic={logic}, constructors={len(constructors)}, "
            f"embed_norm={emb.norm:.3f}, abstract={len(abstract)}, "
            f"ricochet_events={ricochet.get('events_count', 0)}, "
            f"shift={answer_shift.get('magnitude', 0):.3f}, "
            f"demo_ideas={len(demo_ideas)}."
        )

        return OAEResult(
            constructors=[c.to_dict() for c in constructors],
            embedding=emb.to_dict(),
            deep_analysis=deep,
            reduced_to_request=reduced,
            answer_shift=answer_shift,
            abstract_coordinates=[a.to_dict() for a in abstract],
            ricochet=ricochet,
            pragma=pragma.to_dict(),
            demo_ideas=demo_ideas,
            processing_logic=logic,
            metrics_delta=metrics_delta,
            summary=summary,
            paid_hook=paid_hook,
            generative_hook=generative_hook,
        )

    # ── 1. Constructor of a certain form ─────────────────────────────────

    def _build_constructors(
        self,
        missing: list[str],
        params: dict[str, float],
        vvi: float,
        axes: dict[str, float],
    ) -> list[ConstructorSlot]:
        """
        Vague/undefined → constructor slots.

        Идея: пустота — не «ошибка удаления», а *форма*,
        в которую OAE вливает энергию осей (constructor mass).
        """
        slots: list[ConstructorSlot] = []
        # from explicit missing
        for name in missing[:10]:
            clean = name.replace("p_", "").replace("sec_", "")
            form = self.FORM_MAP.get(clean, self.FORM_MAP["default"])
            openness = min(1.0, 0.45 + vvi * 0.4)
            inject = self._form_inject(form, axes, openness)
            slots.append(
                ConstructorSlot(
                    param_name=name,
                    form_type=form,
                    openness=round(openness, 4),
                    inject_dims=inject,
                    note=f"Undefined «{name}» → constructor form «{form}»",
                )
            )
        # weak params also get soft constructors
        for k, v in params.items():
            if v < 0.28 and len(slots) < 12:
                form = self.FORM_MAP.get(k.replace("p_", ""), self.FORM_MAP["default"])
                openness = min(1.0, 0.35 + (0.28 - v))
                slots.append(
                    ConstructorSlot(
                        param_name=k,
                        form_type=form,
                        openness=round(openness, 4),
                        inject_dims=self._form_inject(form, axes, openness),
                        note=f"Vague param «{k}»={v:.2f} → soft constructor",
                    )
                )
        if not slots and vvi >= 0.35:
            # pure high void without listed missing
            slots.append(
                ConstructorSlot(
                    param_name="latent_void",
                    form_type="open_manifold",
                    openness=round(min(1.0, vvi), 4),
                    inject_dims=self._form_inject("open_manifold", axes, vvi),
                    note="High VVI without named missing — open manifold constructor",
                )
            )
        return slots

    def _form_inject(
        self, form: str, axes: dict[str, float], openness: float
    ) -> dict[str, float]:
        base = {
            "outcome_frame": {"value": 0.4, "clarity": -0.2},
            "role_lattice": {"complexity": 0.25, "value": 0.15},
            "signal_port": {"urgency": 0.2, "product": 0.15},
            "value_pipeline": {"product": 0.35, "complexity": 0.15},
            "bound_shell": {"risk": 0.3, "money": 0.1},
            "success_gauge": {"success_pull": 0.35, "clarity": 0.2},
            "void_membrane": {"void_mass": 0.45, "risk": 0.2},
            "revenue_hinge": {"money": 0.4, "promo": 0.25},
            "open_manifold": {"void_mass": 0.5, "complexity": 0.2},
        }.get(form, {"void_mass": 0.3})
        # scale by openness and lightly by axes
        out: dict[str, float] = {}
        for dim, w in base.items():
            ax_boost = 0.0
            if dim == "value":
                ax_boost = float(axes.get("value_density", 0.5)) * 0.15
            if dim == "risk":
                ax_boost = float(axes.get("risk", 0.3)) * 0.15
            out[dim] = round(w * openness + ax_boost, 4)
        return out

    # ── 2. Embedding assembly ────────────────────────────────────────────

    def _assemble_embedding(
        self,
        axes: dict[str, float],
        scores: dict[str, float],
        params: dict[str, float],
        constructors: list[ConstructorSlot],
        success_card: dict[str, Any],
        sys_f: dict[str, Any],
    ) -> EmbeddingBundle:
        """
        Динамическая сборка embedding из:
        - known axes/scores/params
        - constructor inject dims (void → form energy)
        - success metric weights
        - system log gravity
        """
        vec = {d: 0.0 for d in EMBED_DIMS}
        notes: list[str] = []

        # known geometry
        vec["value"] += float(axes.get("value_density", 0.5))
        vec["urgency"] += float(axes.get("time_pressure", 0.4))
        vec["complexity"] += float(axes.get("complexity", 0.5))
        vec["money"] += float(axes.get("monetization_fit", 0.5))
        vec["risk"] += float(axes.get("risk", 0.25))
        vec["product"] += float(scores.get("product_fit", 0.5))
        vec["models"] += float(scores.get("model_fit", 0.5))
        vec["promo"] += float(scores.get("promo_fit", 0.5))
        vec["clarity"] += float(scores.get("readiness", 0.5))
        notes.append("Injected orientation axes + track scores")

        known_mass = sum(max(0.0, v) for v in vec.values())

        # param presence boosts product/clarity slightly
        if params:
            avg_p = sum(params.values()) / max(1, len(params))
            vec["clarity"] += avg_p * 0.15
            vec["product"] += avg_p * 0.08
            notes.append(f"Parameter map mass avg={avg_p:.2f}")

        # constructors → void_mass and form inject
        constructor_mass = 0.0
        for c in constructors:
            constructor_mass += c.openness
            for dim, w in c.inject_dims.items():
                if dim in vec:
                    vec[dim] += w
                elif dim == "void_mass":
                    vec["void_mass"] += w
                else:
                    vec["void_mass"] += w * 0.5
        if constructors:
            notes.append(
                f"Assembled {len(constructors)} constructor form(s), "
                f"constructor_mass={constructor_mass:.2f}"
            )

        # success pull
        sc_vals = success_card.get("values") or {}
        wm = (success_card.get("tz") or {}).get("weight_map") or {}
        pull = 0.0
        for k, w in wm.items():
            pull += float(sc_vals.get(k, 0.5)) * float(w)
        if not wm:
            pull = float(success_card.get("weighted_composite") or 0.5)
        vec["success_pull"] += pull
        notes.append(f"Success pull={pull:.3f} from custom TZ weights")

        # log gravity
        log_g = 0.0
        if sys_f.get("mean_iroi"):
            log_g += min(0.4, float(sys_f["mean_iroi"]) / 10.0)
        if sys_f.get("paid_true_rate"):
            log_g += float(sys_f["paid_true_rate"]) * 0.25
        if sys_f.get("n_requests", 0) > 0:
            log_g += min(0.2, sys_f["n_requests"] / 100.0)
        vec["log_gravity"] += log_g
        if log_g > 0:
            notes.append(f"System log gravity={log_g:.3f}")

        # ordered vector
        ordered = [float(vec[d]) for d in EMBED_DIMS]
        # L2 normalize for comparison stability
        norm = math.sqrt(sum(x * x for x in ordered)) or 1.0
        unit = [x / norm for x in ordered]

        return EmbeddingBundle(
            vector=unit,
            dims=list(EMBED_DIMS),
            norm=norm,
            known_mass=known_mass,
            constructor_mass=constructor_mass,
            assembly_notes=notes,
        )

    # ── 3. Deep analysis ─────────────────────────────────────────────────

    def _deep_analyze(
        self,
        emb: EmbeddingBundle,
        industry_id: str,
        scores: dict[str, float],
        constructors: list[ConstructorSlot],
    ) -> dict[str, Any]:
        v = emb.vector
        # energy partitions
        surface_idx = [0, 1, 2, 3, 4]  # value..risk
        track_idx = [5, 6, 7]
        latent_idx = [8, 9, 10, 11]
        surface_e = sum(abs(v[i]) for i in surface_idx)
        track_e = sum(abs(v[i]) for i in track_idx)
        latent_e = sum(abs(v[i]) for i in latent_idx)
        # tension between product vs promo dims
        tension = abs(v[5] - v[7])
        # entropy of absolute components
        abs_v = [abs(x) + 1e-9 for x in v]
        s = sum(abs_v)
        probs = [x / s for x in abs_v]
        ent = -sum(p * math.log(p) for p in probs) / math.log(len(probs))

        top_dims = sorted(
            zip(EMBED_DIMS, v), key=lambda x: abs(x[1]), reverse=True
        )[:4]

        return {
            "surface_energy": round(surface_e, 4),
            "track_energy": round(track_e, 4),
            "latent_energy": round(latent_e, 4),
            "product_promo_tension": round(tension, 4),
            "embedding_entropy": round(ent, 4),
            "top_dimensions": [
                {"dim": d, "weight": round(w, 4)} for d, w in top_dims
            ],
            "constructor_count": len(constructors),
            "industry_id": industry_id,
            "readiness": float(scores.get("readiness", 0.5)),
            "analysis_notes": [
                "Deep layer = energy split surface/track/latent on assembled embedding",
                "High latent_energy → double-bottom / abstract coords likely",
                "High tension → Full Package tour must balance tracks",
            ],
        }

    # ── 5. Abstract coordinates / double bottom ──────────────────────────

    def _abstract_coordinates(
        self,
        emb: EmbeddingBundle,
        industry_id: str,
        primary_idea: str,
        deep: dict[str, Any],
        demo_fast: bool,
    ) -> list[AbstractCoordinate]:
        """
        Ready solutions «вылетают» как абстрактные координаты
        (double bottom) — второй слой под primary seed.
        """
        seeds = IDEA_SEEDS.get(industry_id, IDEA_SEEDS["ai-agencies"])
        out: list[AbstractCoordinate] = []
        # build pseudo-coords for each seed title
        for track, titles in seeds.items():
            for i, title in enumerate(titles):
                if title == primary_idea:
                    continue
                coord = self._title_to_coord(title, track, emb)
                # flyout = cosine-like with embedding + latent energy
                sim = _cosine(emb.vector, coord)
                latent = float(deep.get("latent_energy") or 0.3)
                strength = max(0.0, sim * 0.65 + latent * 0.25 + (0.1 if demo_fast else 0.0))
                if strength < 0.22 and not demo_fast:
                    continue
                role = {
                    "product": "surface_offer",
                    "models": "money_geometry",
                    "promotion": "attention_lattice",
                }.get(track, "latent")
                out.append(
                    AbstractCoordinate(
                        id=f"abs_{track}_{i}",
                        label=title[:80],
                        source_solution=title,
                        track=track,
                        coordinate=[round(c, 4) for c in coord],
                        flyout_strength=round(min(1.0, strength), 4),
                        latent_role=role,
                    )
                )
        out.sort(key=lambda a: a.flyout_strength, reverse=True)
        return out[:6]

    def _title_to_coord(self, title: str, track: str, emb: EmbeddingBundle) -> list[float]:
        h = hashlib.sha256(f"{track}:{title}".encode()).digest()
        base = [(h[i] / 255.0) * 0.35 for i in range(len(EMBED_DIMS))]
        # align track dims
        track_boost = {"product": 5, "models": 6, "promotion": 7}.get(track, 5)
        base[track_boost] += 0.45
        # mix a bit of request embedding so flyout is request-relative
        mixed = [0.55 * emb.vector[i] + 0.45 * base[i] for i in range(len(EMBED_DIMS))]
        n = math.sqrt(sum(x * x for x in mixed)) or 1.0
        return [x / n for x in mixed]

    # ── 6. Reverse void ricochet ─────────────────────────────────────────

    def _reverse_void_ricochet(
        self,
        constructors: list[ConstructorSlot],
        rrc: float,
        er: float,
        gain: float,
        decision_mode: str,
    ) -> dict[str, Any]:
        """
        Reverse void ricochet:
          void (constructor) → reverse link → reassembly fragment
        RRC logic: higher reverse density after ricochet.
        """
        events: list[RicochetEvent] = []
        force = decision_mode in ("dual_ricochet", "recursive_refinement")
        if not constructors and not force:
            return {
                "enabled": False,
                "events_count": 0,
                "events": [],
                "total_rrc_delta": 0.0,
                "note": "No constructors / mode does not force ricochet",
            }

        targets = constructors[:5] or [
            ConstructorSlot(
                "forced_void",
                "open_manifold",
                0.5,
                {"void_mass": 0.4},
                "forced by mode",
            )
        ]
        total_delta = 0.0
        for i, c in enumerate(targets):
            energy_in = c.openness * (0.5 + er * 0.5) * gain
            # ricochet: part of void energy becomes structure
            energy_out = energy_in * (0.45 + rrc * 0.35)
            delta = min(0.12, energy_out * 0.08)
            total_delta += delta
            reverse_link = f"rev::{c.form_type}::{c.param_name}"
            fragment = (
                f"Reassembled «{c.param_name}» via {c.form_type}: "
                f"define acceptance + owner + metric gauge"
            )
            events.append(
                RicochetEvent(
                    void_name=c.param_name,
                    reverse_link=reverse_link,
                    energy_in=round(energy_in, 4),
                    energy_out=round(energy_out, 4),
                    reassembled_fragment=fragment,
                    rrc_delta=round(delta, 4),
                )
            )
        return {
            "enabled": True,
            "events_count": len(events),
            "events": [e.to_dict() for e in events],
            "total_rrc_delta": round(total_delta, 4),
            "phenomenon": "reverse_void_ricochet",
            "note": (
                "Voids bounce through reverse links into reassemblable fragments "
                "(RRC reverse refragmentation)"
            ),
        }

    # ── 7. Answer shift ──────────────────────────────────────────────────

    def _answer_shift(
        self,
        emb: EmbeddingBundle,
        deep: dict[str, Any],
        business_text: str,
        idea_title: str,
        sensitivity: float,
        scores: dict[str, float],
    ) -> dict[str, Any]:
        """
        Параметры сдвига ответа: насколько demo idea должна
        «прилипнуть» к лексике/геометрии запроса vs остаться seed.
        """
        tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]{4,}", business_text.lower())
        uniq = list(dict.fromkeys(tokens))[:12]
        # magnitude from constructor mass + latent energy + low clarity
        clarity = emb.vector[EMBED_DIMS.index("clarity")]
        void_m = emb.vector[EMBED_DIMS.index("void_mass")]
        magnitude = _clamp01(
            sensitivity
            * (
                0.35 * emb.constructor_mass / max(1.0, emb.known_mass + emb.constructor_mass)
                + 0.30 * float(deep.get("latent_energy") or 0)
                + 0.20 * max(0.0, 0.55 - clarity)
                + 0.15 * void_m
            )
        )
        direction = {
            "toward_client_lexicon": round(magnitude * 0.6, 4),
            "toward_latent_coords": round(magnitude * float(deep.get("latent_energy") or 0.3), 4),
            "preserve_seed_spine": round(1.0 - magnitude * 0.5, 4),
        }
        return {
            "magnitude": round(magnitude, 4),
            "sensitivity": round(sensitivity, 4),
            "direction": direction,
            "anchor_tokens": uniq[:8],
            "seed_title": idea_title,
            "guidance": (
                "Shift demo wording toward client tokens while preserving seed spine"
                if magnitude >= 0.25
                else "Light shift — seed already aligned"
            ),
            "readiness": float(scores.get("readiness", 0.5)),
            "copy_firmware": {
                "rule": "answer_shift is copy, never a CY/CN/U rewrite",
                "certainty_untouched": True,
            },
        }

    # ── 8. Reduce to request ─────────────────────────────────────────────

    def _reduce_to_request(
        self,
        business_text: str,
        idea_title: str,
        deep: dict[str, Any],
        abstract: list[AbstractCoordinate],
        shift: dict[str, Any],
        ricochet: dict[str, Any],
    ) -> dict[str, Any]:
        """Сжимает deep-layer обратно в ответ, привязанный к запросу."""
        snippet = business_text.strip().replace("\n", " ")
        if len(snippet) > 220:
            snippet = snippet[:220] + "…"
        flyouts = [a.label for a in abstract[:3]]
        fragments = [
            e.get("reassembled_fragment")
            for e in (ricochet.get("events") or [])[:2]
        ]
        return {
            "request_anchor": snippet,
            "primary_idea": idea_title,
            "why_this_maps": (
                f"Embedding top dims → "
                + ", ".join(
                    f"{t['dim']}={t['weight']}"
                    for t in (deep.get("top_dimensions") or [])[:3]
                )
            ),
            "double_bottom_flyouts": flyouts,
            "ricochet_fragments": [f for f in fragments if f],
            "client_facing_bridge": (
                f"For your case («{snippet[:80]}…»), the oriented spine is «{idea_title}». "
                f"Shift={shift.get('magnitude', 0):.2f}. "
                + (
                    f"Secondary surfaces: {'; '.join(flyouts)}."
                    if flyouts
                    else "No strong double-bottom flyout."
                )
            ),
            "answer_shift_applied": shift.get("direction"),
        }

    # ── 9. Demo ideas ────────────────────────────────────────────────────

    def _demo_ideas(
        self,
        industry_id: str,
        primary: str,
        abstract: list[AbstractCoordinate],
        pragma: Any,
        decision_mode: str,
        reduced: dict[str, Any],
        portfolio_ideas: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Multi-idea list for ops success.
        Prefers Superstructure / Product Sol portfolio when provided;
        always appends abstract flyouts that don't duplicate titles.
        """
        ideas: list[dict[str, Any]] = []
        seen_titles: set[str] = set()

        def _add(item: dict[str, Any]) -> None:
            title = str(item.get("title") or "").strip()
            key = title.lower()[:90]
            if not title or key in seen_titles:
                return
            seen_titles.add(key)
            ideas.append(item)

        if portfolio_ideas:
            for p in portfolio_ideas:
                _add(
                    {
                        **p,
                        "source": p.get("source") or "Product Sol portfolio",
                        "bridge": reduced.get("client_facing_bridge")
                        if p.get("is_primary") or p.get("rank") == 1
                        else None,
                    }
                )
        else:
            _add(
                {
                    "rank": 1,
                    "title": primary,
                    "kind": "primary_seed",
                    "source": "Product Sol + orientation",
                    "bridge": reduced.get("client_facing_bridge"),
                }
            )

        # Abstract flyouts fill residual gaps (cap total ~12 for readability)
        max_total = 12
        start_rank = len(ideas) + 1
        for i, a in enumerate(abstract[:4], start=start_rank):
            if len(ideas) >= max_total:
                break
            _add(
                {
                    "rank": i,
                    "title": a.label,
                    "kind": "double_bottom_flyout",
                    "role": f"abstract_{a.latent_role or a.track}",
                    "track": getattr(a, "track", None) or "product",
                    "source": f"abstract:{a.track}",
                    "flyout_strength": a.flyout_strength,
                    "latent_role": a.latent_role,
                    "pragma": [t.phenomenon for t in pragma.triggered[:2]],
                    "why_in_portfolio": "Abstract coordinate flyout for generative depth",
                    "is_primary": False,
                }
            )

        # Keep portfolio order: do not let flyouts steal primary
        primary_keep = ideas[0] if ideas else None
        rest = ideas[1:]
        rest.sort(
            key=lambda x: (
                0 if x.get("kind") == "double_bottom_flyout" else 1,
                float(x.get("score") or 0),
            ),
            reverse=True,
        )
        ideas = ([primary_keep] if primary_keep else []) + rest
        ideas = ideas[:max_total]

        # Re-rank sequentially
        for i, idea in enumerate(ideas, start=1):
            idea["rank"] = i
            idea["is_primary"] = i == 1

        return ideas

    def _logic_label(self, mode: str, pragma: Any, constructors: list) -> str:
        if mode == "dual_ricochet" or any(
            t.phenomenon == "brittle_refragmentation" for t in pragma.triggered
        ):
            return "constructor_embed_ricochet"
        if mode == "generative_development" or pragma.demo_fast_path:
            return "constructor_embed_generative_split"
        if mode == "recursive_refinement" or constructors:
            return "constructor_embed_recursive"
        return "constructor_embed_scoring"


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return max(0.0, min(1.0, dot / (na * nb)))


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))
