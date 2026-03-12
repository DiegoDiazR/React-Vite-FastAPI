from __future__ import annotations
from typing import Any, Dict
from app.calculations.externalCracking_calc import compute_df_external_cracking
from app.services.externalcracking_builder import build_cracking_inputs_from_rows

def _sa_to_dict(obj: Any) -> Dict[str, Any]:
    """Convierte objeto SQLAlchemy a diccionario de forma segura."""
    if hasattr(obj, "__table__"):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return dict(obj)

class ExternalCrackingService:
    @staticmethod
    def calculate_cracking_from_rows(
        *,
        comp: dict,
        analysis: dict,
        dm: dict
    ) -> Dict[str, Any]:
        """
        Calcula el Factor de Daño por Agrietamiento Externo (SCC) desde diccionarios.
        """
        # 1. Construir Inputs usando el Builder
        inputs = build_cracking_inputs_from_rows(comp=comp, analysis=analysis, dm=dm)

        # 2. Ejecutar Motor de Cálculo (Paso 1 al 10 de API 581)
        result = compute_df_external_cracking(inputs)

        # 3. Estructurar Respuesta para el modelo RBI581ExternalCrackingResult
        return {
            "df_externalcracking": result.get("df_cracking", 1.0),
            "status": result.get("status", "ok"),
            "message": result.get("message"),
            "trace_json": result.get("trace") # Guardamos el rastro completo
        }

    @staticmethod
    def calculate_cracking_from_models(
        *,
        comp_obj: Any,
        analysis_obj: Any,
        dm_obj: Any
    ) -> Dict[str, Any]:
        """
        Punto de entrada cuando tienes los objetos de base de datos.
        """
        return ExternalCrackingService.calculate_cracking_from_rows(
            comp=_sa_to_dict(comp_obj),
            analysis=_sa_to_dict(analysis_obj),
            dm=_sa_to_dict(dm_obj)
        )