from __future__ import annotations
import json
from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.rbi581_external_cracking_result import RBI581ExternalCrackingResult

def upsert_external_cracking_result(
    db: Session,
    *,
    asset_pk: int,
    component_pk: int,
    analysis_pk: int,
    dm_externalcracking_pk: int,
    df_externalcracking: float,
    trace: dict[str, Any],
) -> RBI581ExternalCrackingResult:
    """
    Crea o actualiza el resultado de agrietamiento basándose en el análisis y el ID del mecanismo.
    """
    status = trace.get("status", "ok")
    message = trace.get("message")
    
    # Buscar si ya existe para este análisis y este registro de daño específico
    stmt = (
        select(RBI581ExternalCrackingResult)
        .where(RBI581ExternalCrackingResult.analysis_pk == analysis_pk)
        .where(RBI581ExternalCrackingResult.dm_externalcracking_pk == dm_externalcracking_pk)
    )
    obj = db.execute(stmt).scalar_one_or_none()

    payload = json.dumps(trace, ensure_ascii=False)

    if obj is None:
        obj = RBI581ExternalCrackingResult(
            asset_pk=asset_pk,
            component_pk=component_pk,
            analysis_pk=analysis_pk,
            dm_externalcracking_pk=dm_externalcracking_pk,
            df_externalcracking=float(df_externalcracking),
            status=str(status),
            message=str(message) if message else None,
            computed_at=datetime.utcnow(),
            trace_json=payload,
        )
        db.add(obj)
    else:
        obj.df_externalcracking = float(df_externalcracking)
        obj.status = str(status)
        obj.message = str(message) if message else None
        obj.computed_at = datetime.utcnow()
        obj.trace_json = payload

    db.flush() # Importante para obtener el PK antes del commit final
    return obj

def get_external_cracking_result(
    db: Session,
    analysis_pk: int,
    dm_externalcracking_pk: int,
) -> Optional[RBI581ExternalCrackingResult]:
    stmt = (
        select(RBI581ExternalCrackingResult)
        .where(RBI581ExternalCrackingResult.analysis_pk == analysis_pk)
        .where(RBI581ExternalCrackingResult.dm_externalcracking_pk == dm_externalcracking_pk)
    )
    return db.execute(stmt).scalar_one_or_none()