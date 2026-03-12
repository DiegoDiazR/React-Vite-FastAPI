from __future__ import annotations
import json
from dataclasses import is_dataclass, asdict
from datetime import date, datetime
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models.rbi581_external_result import RBI581ExternalResult

def upsert_external_result(
    db: Session,
    *,
    asset_pk: int,
    component_pk: int,
    analysis_pk: int,
    dm_external_pk: int,
    df_external: float,
    trace: dict[str, Any],
) -> RBI581ExternalResult:
    """
    Crea o actualiza el resultado de daño externo (CUI/Atmosférico) 
    guardando el DF final y la traza completa de cálculo.
    """
    status = trace.get("status", "ok")
    message = trace.get("message")

    obj = (
        db.query(RBI581ExternalResult)
        .filter(
            RBI581ExternalResult.analysis_pk == analysis_pk,
            RBI581ExternalResult.dm_external_pk == dm_external_pk,
        )
        .one_or_none()
    )

    # Helper para serializar fechas
    # 1. Helper Mejorado para Serialización
    def json_serial(obj):
        """Maneja fechas, dataclasses y objetos genéricos."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if is_dataclass(obj):
            return asdict(obj) # Convierte dataclasses como CUIInspectionEffectiveness a dict
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Type {type(obj)} not serializable")

    # 2. Convertir a JSON con el helper mejorado
    try:
        payload_json = json.dumps(trace, default=json_serial, ensure_ascii=False)
    except Exception as e:
        # Log preventivo por si algo más falla
        payload_json = json.dumps({"error": "Falló serialización", "details": str(e)})

    # Convertimos el rastro a JSON usando el serializador personalizado
    payload_json = json.dumps(trace, default=json_serial, ensure_ascii=False)

    obj = (
        db.query(RBI581ExternalResult)
        .filter(
            RBI581ExternalResult.analysis_pk == analysis_pk,
            RBI581ExternalResult.dm_external_pk == dm_external_pk,
        )
        .one_or_none()
    )

    if obj is None:
        obj = RBI581ExternalResult(
            asset_pk=asset_pk,
            component_pk=component_pk,
            analysis_pk=analysis_pk,
            dm_external_pk=dm_external_pk,
            df_external=float(df_external),
            status=str(status),
            message=None if message is None else str(message),
            computed_at=datetime.utcnow(),
            trace_json=payload_json, # Ahora sí funcionará
        )
        db.add(obj)
    else:
        # Actualización de campos existentes
        obj.asset_pk = asset_pk
        obj.component_pk = component_pk
        obj.df_external = float(df_external)
        obj.status = str(status)
        obj.message = None if message is None else str(message)
        obj.computed_at = datetime.utcnow()
        obj.trace_json = payload_json

    db.commit()
    db.refresh(obj)
    return obj


def get_external_result(
    db: Session,
    *,
    analysis_pk: int,
    dm_external_pk: int,
) -> Optional[RBI581ExternalResult]:
    """Recupera un resultado específico por análisis y entrada de DM."""
    return (
        db.query(RBI581ExternalResult)
        .filter(
            RBI581ExternalResult.analysis_pk == analysis_pk,
            RBI581ExternalResult.dm_external_pk == dm_external_pk,
        )
        .one_or_none()
    )


def list_external_results_by_analysis(
    db: Session,
    *,
    analysis_pk: int,
) -> list[RBI581ExternalResult]:
    """Lista todos los factores de daño externo calculados para un análisis."""
    return (
        db.query(RBI581ExternalResult)
        .filter(RBI581ExternalResult.analysis_pk == analysis_pk)
        .order_by(RBI581ExternalResult.computed_at.desc())
        .all()
    )