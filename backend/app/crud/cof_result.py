from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.rbi581_cof_result import RBI581COFResult


def upsert_cof_result(
    db: Session,
    *,
    asset_pk: int,
    component_pk: int,
    analysis_pk: int,
    consequence_pk: int,
    cof_data: dict[str, Any],
) -> RBI581COFResult:
    """
    Crea o actualiza (analysis_pk, consequence_pk) guardando los resultados clave 
    en columnas y la traza completa (logs, pasos) en trace_json.
    """
    # Extraer información del diccionario retornado por COFService
    status = cof_data.get("status", "ok")
    message = cof_data.get("message")
    
    areas = cof_data.get("areas", {})
    financial = cof_data.get("financial", {})
    safety = cof_data.get("safety", {})

    # Buscar si ya existe un resultado para esta Consecuencia en este Análisis
    obj = (
        db.query(RBI581COFResult)
        .filter(
            RBI581COFResult.analysis_pk == analysis_pk,
            RBI581COFResult.consequence_pk == consequence_pk,
        )
        .one_or_none()
    )

    # Convertir todo el resultado a JSON para trazabilidad
    payload = json.dumps(cof_data, ensure_ascii=False)

    if obj is None:
        obj = RBI581COFResult(
            asset_pk=asset_pk,
            component_pk=component_pk,
            analysis_pk=analysis_pk,
            consequence_pk=consequence_pk,
            
            # --- Áreas ---
            final_cmd_area_ft2=areas.get("final_cmd_area_ft2"),
            final_inj_area_ft2=areas.get("final_inj_area_ft2"),
            final_cof_area_ft2=areas.get("final_cof_area_ft2"),
            
            # --- Financiero ---
            financial_total_cost=financial.get("total_cost"),
            financial_cmd_cost=financial.get("cmd_cost"),
            financial_inj_cost=financial.get("inj_cost"),
            financial_env_cost=financial.get("env_cost"),
            financial_prod_cost=financial.get("prod_cost"),
            
            # --- Seguridad ---
            safety_population_density=safety.get("population_density"),
            safety_personnel_affected=safety.get("personnel_affected"),
            
            status=str(status),
            message=None if message is None else str(message),
            computed_at=datetime.utcnow(),
            trace_json=payload,
        )
        db.add(obj)
    else:
        # Actualizar datos si ya existe
        obj.asset_pk = asset_pk
        obj.component_pk = component_pk
        
        obj.final_cmd_area_ft2 = areas.get("final_cmd_area_ft2")
        obj.final_inj_area_ft2 = areas.get("final_inj_area_ft2")
        obj.final_cof_area_ft2 = areas.get("final_cof_area_ft2")
        
        obj.financial_total_cost = financial.get("total_cost")
        obj.financial_cmd_cost = financial.get("cmd_cost")
        obj.financial_inj_cost = financial.get("inj_cost")
        obj.financial_env_cost = financial.get("env_cost")
        obj.financial_prod_cost = financial.get("prod_cost")
        
        obj.safety_population_density = safety.get("population_density")
        obj.safety_personnel_affected = safety.get("personnel_affected")
        
        obj.status = str(status)
        obj.message = None if message is None else str(message)
        obj.computed_at = datetime.utcnow()
        obj.trace_json = payload

    db.commit()
    db.refresh(obj)
    return obj


def get_cof_result(
    db: Session,
    *,
    analysis_pk: int,
    consequence_pk: int,
) -> Optional[RBI581COFResult]:
    """
    Recupera un resultado específico.
    """
    return (
        db.query(RBI581COFResult)
        .filter(
            RBI581COFResult.analysis_pk == analysis_pk,
            RBI581COFResult.consequence_pk == consequence_pk,
        )
        .one_or_none()
    )


def list_cof_results_by_analysis(
    db: Session,
    *,
    analysis_pk: int,
) -> list[RBI581COFResult]:
    """
    Lista todos los resultados de Consecuencia asociados a un Análisis.
    (Útil si corres múltiples escenarios de consecuencia).
    """
    return (
        db.query(RBI581COFResult)
        .filter(RBI581COFResult.analysis_pk == analysis_pk)
        .order_by(RBI581COFResult.computed_at.desc())
        .all()
    )