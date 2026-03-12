from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.core.db import get_db
from app.services.thinning_services import ThinningService
from app.crud.thinning_result import upsert_thinning_result

# IMPORTA TUS MODELOS REALES (ajusta rutas)
from app.models.asset import Asset
from app.models.asset import RBIComponent
from app.models.asset import RBI581Analysis
from app.models.asset import DMThinning

router = APIRouter(prefix="/rbi581", tags=["RBI581 - Thinning"])

def sa_to_dict(obj) -> dict:
    """Convierte un modelo SQLAlchemy a dict con SOLO columnas (no relaciones)."""
    mapper = inspect(obj).mapper
    return {col.key: getattr(obj, col.key) for col in mapper.column_attrs}


@router.post("/analysis/{analysis_pk}/dm-thinning/{dm_thinning_pk}/compute")
def compute_thinning(
    analysis_pk: int,
    dm_thinning_pk: int,
    db: Session = Depends(get_db),
):
    # 1) Traer Analysis
    analysis = (
        db.query(RBI581Analysis)
        .filter(RBI581Analysis.analysis_pk == analysis_pk)
        .one_or_none()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail=f"Analysis no existe: {analysis_pk}")

    # 2) Traer DM Thinning (validando que pertenece al analysis)
    dm = (
        db.query(DMThinning)
        .filter(
            DMThinning.dm_thinning_pk == dm_thinning_pk,
            DMThinning.analysis_pk == analysis_pk,
        )
        .one_or_none()
    )
    if dm is None:
        raise HTTPException(
            status_code=404,
            detail=f"DM thinning no existe o no pertenece al analysis: dm={dm_thinning_pk}, analysis={analysis_pk}",
        )

    # 3) Traer Component
    component = (
        db.query(RBIComponent)
        .filter(RBIComponent.component_pk == analysis.component_pk)  # FK en analysis
        .one_or_none()
    )
    if component is None:
        raise HTTPException(
            status_code=404,
            detail=f"Component no existe para component_pk={analysis.component_pk}",
        )

    # 4) Traer Asset
    asset = (
        db.query(Asset)
        .filter(Asset.asset_pk == component.asset_pk)
        .one_or_none()
    )
    if asset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Asset no existe para asset_pk={component.asset_pk}",
        )

    # 5) Calcular (convertimos modelos -> dicts)
    comp_dict = sa_to_dict(component)
    analysis_dict = sa_to_dict(analysis)
    dm_dict = sa_to_dict(dm)

    result = ThinningService.calculate_thinning_from_rows(
        comp=comp_dict,
        analysis=analysis_dict,
        dm=dm_dict,
        confidence=dm_dict.get("dm_thinning_confidence", "medium"),
    )

    df_thin = result.get("df_thin")
    dfb_thin = result.get("dfb_thin")
    trace = result.get("trace", {}) or {}

    if df_thin is None:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Cálculo incompleto (df_thin=None). Revisa trace/status",
                "status": trace.get("status"),
                "calc_message": trace.get("message"),
                "step_7": trace.get("step_7"),
            },
        )

    # 6) Guardar resultado
      
    saved = upsert_thinning_result(
        db,
        asset_pk=asset.asset_pk,
        component_pk=component.component_pk,
        analysis_pk=analysis.analysis_pk,
        dm_thinning_pk=dm.dm_thinning_pk,
        df_thin=float(df_thin),
        dfb_thin=None if dfb_thin is None else float(dfb_thin),
        trace=trace,
        )
    
    
    print("PK attrs:", [k for k in saved.__dict__.keys() if "pk" in k.lower() or k.lower() == "id"])

    return {
        "thinning_result_pk": saved.thinning_result_pk,
        "df_thin": saved.df_thin,
        "dfb_thin": saved.dfb_thin,
        "status": saved.status,
        "message": saved.message,
        }

