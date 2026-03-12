from __future__ import annotations
from typing import Any, Dict
from app.calculations.externalDamage_calc_df import compute_df_cui
from app.services.external_builder import build_external_inputs_from_rows

def _sa_to_dict(obj: Any) -> Dict[str, Any]:
    """Convierte objeto SQLAlchemy a diccionario."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

class ExternalDamageService:
    @staticmethod
    def calculate_external_from_rows(
        *,
        comp: dict,
        analysis: dict,
        dm: dict
    ) -> Dict[str, Any]:
        """
        Calcula el Factor de Daño Externo desde diccionarios.
        """
        # 1. Construir Inputs
        inputs = build_external_inputs_from_rows(comp=comp, analysis=analysis, dm=dm)

        # 2. Ejecutar Motor de Cálculo
        trace = compute_df_cui(inputs)

        # 3. Estructurar Respuesta para el esquema Result
        # Se alinea con los nombres de columna del modelo RBI581ExternalResult
        return {
            "df_external": trace.get("step_18", {}).get("DF_CUI"),
            "status": trace.get("status", "ok"),
            "message": trace.get("message"),
            "trace": trace
        }

    @staticmethod
    def calculate_external_from_models(
        *,
        comp_obj: Any,
        analysis_obj: Any,
        dm_obj: Any
    ) -> Dict[str, Any]:
        """
        Recibe objetos SQLAlchemy y delega a la función de filas.
        """
        return ExternalDamageService.calculate_external_from_rows(
            comp=_sa_to_dict(comp_obj),
            analysis=_sa_to_dict(analysis_obj),
            dm=_sa_to_dict(dm_obj)
        )