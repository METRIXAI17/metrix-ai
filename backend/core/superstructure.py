"""
Superstructure / Product Overlay

Соединяющий интеллектуальный слой:
Infa Sol ↔ Cloud Sol ↔ Structure Fi ↔ Product Sol → единый продуктовый результат.

Позволяет «скользить» между зонами, не теряя финальный product result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.metrics import CoreMetrics, blend_metrics
from backend.zones.registry import ZoneRegistry, get_zone_registry


@dataclass
class OverlayPassage:
    """Один переход между зонами при работе над продуктом."""

    from_zone: str
    to_zone: str
    reason: str
    artifact_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_zone": self.from_zone,
            "to_zone": self.to_zone,
            "reason": self.reason,
            "artifact_keys": self.artifact_keys,
        }


@dataclass
class SuperstructureResult:
    product_title: str
    zone_outputs: dict[str, Any]
    passages: list[OverlayPassage]
    unified_metrics: CoreMetrics
    product_result: dict[str, Any]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": "Superstructure / Product Overlay",
            "product_title": self.product_title,
            "zone_outputs": self.zone_outputs,
            "passages": [p.to_dict() for p in self.passages],
            "unified_metrics": self.unified_metrics.to_dict(),
            "product_result": self.product_result,
            "summary": self.summary,
        }


class SuperstructureOverlay:
    """
    Оркестратор зон. Не дублирует логику модулей — связывает их.

    Поток (по умолчанию):
      orientation → Infa Sol → Product Sol (draft idea)
                 → Cloud Sol (optimize under product)
                 → Structure Fi (decisions + money geometry)
                 → unify product_result
    """

    name = "Superstructure / Product Overlay"

    def __init__(self, registry: ZoneRegistry | None = None) -> None:
        self.registry = registry or get_zone_registry()

    def compose(
        self,
        business_text: str,
        industry_id: str,
        orientation: dict[str, Any],
        info_roi: float = 1.0,
    ) -> SuperstructureResult:
        tracks = orientation.get("tracks_recommended") or ["product", "models", "promotion"]
        primary = tracks[0]

        passages: list[OverlayPassage] = []
        zone_outputs: dict[str, Any] = {}

        # 1) Infa Sol — foundation
        infa = self.registry.infa.run(business_text, industry_id, orientation)
        zone_outputs["infa_sol"] = infa.to_dict()
        passages.append(
            OverlayPassage(
                "orientation",
                "infa_sol",
                "Build specs twin and operator surface",
                ["specs", "meta_reality", "analog_bridge"],
            )
        )

        specs_ready = bool((infa.specs or {}).get("ready_for_build"))
        # draft title from first product seed via product zone later

        # 2) Product Sol — draft idea (need title for cloud context)
        product = self.registry.product.run(
            business_text,
            industry_id,
            orientation,
            primary_track=primary,
            specs_ready=specs_ready,
        )
        zone_outputs["product_sol"] = product.to_dict()
        product_title = product.demo_idea.get("title") or "Metrix Product Result"
        demo_ideas = list(getattr(product, "demo_ideas", None) or [])
        if not demo_ideas and product.demo_idea:
            demo_ideas = [product.demo_idea]
        portfolio = getattr(product, "portfolio", None) or {}
        passages.append(
            OverlayPassage(
                "infa_sol",
                "product_sol",
                "Materialize client geometry + multi-idea portfolio for ops success",
                ["demo_idea", "demo_ideas", "client_geometry", "portfolio"],
            )
        )

        # 3) Cloud Sol — optimize under concrete product
        cloud = self.registry.cloud.run(
            business_text, industry_id, orientation, product_title=product_title
        )
        zone_outputs["cloud_sol"] = cloud.to_dict()
        passages.append(
            OverlayPassage(
                "product_sol",
                "cloud_sol",
                "Tune compute & linguistic signal for this product",
                ["cloudforge", "linguistic", "pragma_vault"],
            )
        )

        # 4) Structure Fi — decisions & topology
        structure = self.registry.structure.run(
            industry_id, orientation, tracks, info_roi=info_roi
        )
        zone_outputs["structure_fi"] = structure.to_dict()
        passages.append(
            OverlayPassage(
                "cloud_sol",
                "structure_fi",
                "Lock decisions, optics, revenue zones",
                ["verdict_lattice", "optic_prism", "zone_weave"],
            )
        )

        # 5) Back to product overlay — unified result
        passages.append(
            OverlayPassage(
                "structure_fi",
                "superstructure",
                "Unify zones into single product result",
                ["product_result"],
            )
        )

        unified = blend_metrics(
            [infa.metrics, cloud.metrics, structure.metrics, product.metrics],
            weights=[0.30, 0.25, 0.20, 0.25],
        )

        product_result = {
            "title": product_title,
            "industry": industry_id,
            "primary_track": primary,
            "tracks_recommended": tracks,
            "demo_idea": product.demo_idea,
            "demo_ideas": demo_ideas,
            "idea_count": len(demo_ideas),
            "portfolio": portfolio if isinstance(portfolio, dict) else {},
            "specs_ready": specs_ready,
            "cloud_plan": (cloud.cloudforge or {}).get("plan"),
            "linguistic_dominant": (cloud.linguistic or {}).get("dominant_family"),
            "decision_mode": (structure.verdict_lattice or {}).get("operating_mode"),
            "health": unified.health_score,
            "vvi": unified.vvi,
            "er": unified.er,
            "rrc": unified.rrc,
            "movement_allowed": [
                "infa_sol",
                "cloud_sol",
                "structure_fi",
                "product_sol",
                "superstructure",
            ],
            "how_to_move": (
                "Любая зона доступна через overlay: передай zone_id и request_id — "
                "Superstructure сохраняет product_result и догружает артефакты зоны."
            ),
        }

        summary = (
            f"{self.name}: «{product_title[:70]}» · ideas={len(demo_ideas)} | "
            f"passages={len(passages)} | health={unified.health_score:.2f} "
            f"(VVI={unified.vvi:.2f}, ER={unified.er:.2f}, RRC={unified.rrc:.2f})."
        )

        return SuperstructureResult(
            product_title=product_title,
            zone_outputs=zone_outputs,
            passages=passages,
            unified_metrics=unified,
            product_result=product_result,
            summary=summary,
        )

    def move_to_zone(
        self,
        zone_id: str,
        composed: SuperstructureResult,
    ) -> dict[str, Any]:
        """Бесшовный доступ к артефактам зоны без потери product_result."""
        if zone_id == "superstructure":
            return {
                "zone": zone_id,
                "product_result": composed.product_result,
                "summary": composed.summary,
            }
        data = composed.zone_outputs.get(zone_id)
        if not data:
            return {"error": f"unknown or empty zone '{zone_id}'", "zone": zone_id}
        return {
            "zone": zone_id,
            "artifacts": data,
            "product_result_ref": {
                "title": composed.product_title,
                "health": composed.unified_metrics.health_score,
            },
        }
