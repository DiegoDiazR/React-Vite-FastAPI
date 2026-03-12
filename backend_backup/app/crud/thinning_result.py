from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.rbi581_thinning_result import RBI581ThinningResult


def upsert_thinning_result(
    db: Session,
    *,
    asset_pk: int,
    component_pk: int,
    analysis_pk: int,
    dm_thinning_pk: int,
    df_thin: float,
    dfb_thin: Optional[float],
    trace: dict[str, Any],
) -> RBI581ThinningResult:
    """
    Crea o actualiza (analysis_pk, dm_thinning_pk) guardando trace completo.
    """
    status = trace.get("status", "ok")
    message = trace.get("message")

    obj = (
        db.query(RBI581ThinningResult)
        .filter(
            RBI581ThinningResult.analysis_pk == analysis_pk,
            RBI581ThinningResult.dm_thinning_pk == dm_thinning_pk,
        )
        .one_or_none()
    )

    payload = json.dumps(trace, ensure_ascii=False)

    if obj is None:
        obj = RBI581ThinningResult(
            asset_pk=asset_pk,
            component_pk=component_pk,
            analysis_pk=analysis_pk,
            dm_thinning_pk=dm_thinning_pk,
            df_thin=float(df_thin),
            dfb_thin=None if dfb_thin is None else float(dfb_thin),
            status=str(status),
            message=None if message is None else str(message),
            computed_at=datetime.utcnow(),
            trace_json=payload,
        )
        db.add(obj)
    else:
        obj.asset_pk = asset_pk
        obj.component_pk = component_pk
        obj.df_thin = float(df_thin)
        obj.dfb_thin = None if dfb_thin is None else float(dfb_thin)
        obj.status = str(status)
        obj.message = None if message is None else str(message)
        obj.computed_at = datetime.utcnow()
        obj.trace_json = payload

    db.commit()
    db.refresh(obj)
    return obj


def get_thinning_result(
    db: Session,
    *,
    analysis_pk: int,
    dm_thinning_pk: int,
) -> Optional[RBI581ThinningResult]:
    return (
        db.query(RBI581ThinningResult)
        .filter(
            RBI581ThinningResult.analysis_pk == analysis_pk,
            RBI581ThinningResult.dm_thinning_pk == dm_thinning_pk,
        )
        .one_or_none()
    )


def list_thinning_results_by_analysis(
    db: Session,
    *,
    analysis_pk: int,
) -> list[RBI581ThinningResult]:
    return (
        db.query(RBI581ThinningResult)
        .filter(RBI581ThinningResult.analysis_pk == analysis_pk)
        .order_by(RBI581ThinningResult.computed_at.desc())
        .all()
    )
