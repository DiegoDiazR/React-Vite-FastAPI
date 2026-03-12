from __future__ import annotations

from typing import Any, Dict

from app.calculations.thinning_calc_df import compute_df_thinning
# from app.services.thinning_builder import build_thinning_inputs_from_rows
from app.services.thinning_builder import build_thinning_inputs_from_rows


def _sa_to_dict(obj: Any) -> Dict[str, Any]:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class ThinningService:
    @staticmethod
    def calculate_thinning_from_rows(
        *,
        comp: dict,
        analysis: dict,
        dm: dict,
        confidence: str = "medium",
    ) -> Dict[str, Any]:
        inputs = build_thinning_inputs_from_rows(
            comp=comp,
            analysis=analysis,
            dm=dm,
            confidence=confidence,
        )

        trace = compute_df_thinning(inputs)

        return {
            "df_thin": trace.get("step_13", {}).get("DF_thin"),
            "dfb_thin": trace.get("step_12", {}).get("DFb_thin"),
            "trace": trace,
        }

    @staticmethod
    def calculate_thinning_from_models(
        *,
        comp_obj: Any,
        analysis_obj: Any,
        dm_obj: Any,
        confidence: str = "medium",
    ) -> Dict[str, Any]:
        """
        Recibe objetos SQLAlchemy, los convierte a dict, y reutiliza calculate_thinning_from_rows.
        """
        return ThinningService.calculate_thinning_from_rows(
            comp=_sa_to_dict(comp_obj),
            analysis=_sa_to_dict(analysis_obj),
            dm=_sa_to_dict(dm_obj),
            confidence=confidence,
        )
