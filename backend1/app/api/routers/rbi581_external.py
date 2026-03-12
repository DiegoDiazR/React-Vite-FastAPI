from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.core.db import get_db
from app.services.external_services import ExternalDamageService
from app.crud.external_result import upsert_external_result
from app.schemas.schema import ExternalComputeResponse

# Importación de modelos (ajustados a tu estructura)
from app.models.asset import Asset, RBIComponent, RBI581Analysis, DMExternalDamage

router = APIRouter(prefix="/rbi581", tags=["RBI581 - External Damage"])

def sa_to_dict(obj) -> dict:
    """Convierte un modelo SQLAlchemy a dict con SOLO columnas (no relaciones)."""
    mapper = inspect(obj).mapper
    return {col.key: getattr(obj, col.key) for col in mapper.column_attrs}

@router.post(
    "/analysis/{analysis_pk}/dm-external/{dm_extdamage_pk}/compute", 
    response_model=ExternalComputeResponse
)
def compute_external_damage(
    analysis_pk: int,
    dm_extdamage_pk: int,
    db: Session = Depends(get_db),
):
    # 1) Traer el Análisis
    analysis = (
        db.query(RBI581Analysis)
        .filter(RBI581Analysis.analysis_pk == analysis_pk)
        .one_or_none()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail=f"Analysis no existe: {analysis_pk}")

    # 2) Traer Datos de Entrada de Daño Externo (CUI/Atmosférica)
    dm = (
        db.query(DMExternalDamage)
        .filter(
            DMExternalDamage.dm_extdamage_pk == dm_extdamage_pk,
            DMExternalDamage.analysis_pk == analysis_pk,
        )
        .one_or_none()
    )
    if dm is None:
        raise HTTPException(
            status_code=404,
            detail=f"Registro de daño externo no existe o no pertenece al análisis: {dm_extdamage_pk}"
        )

    # 3) Traer el Componente (Datos mecánicos de image_ebbd17.png)
    component = (
        db.query(RBIComponent)
        .filter(RBIComponent.component_pk == analysis.component_pk)
        .one_or_none()
    )
    if component is None:
        raise HTTPException(status_code=404, detail="Component no encontrado para este análisis.")

    # 4) Traer el Asset
    asset = db.query(Asset).filter(Asset.asset_pk == component.asset_pk).one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset no encontrado.")

    # 5) Ejecutar Cálculo (Modelos -> Diccionarios)
    comp_dict = sa_to_dict(component)
    analysis_dict = sa_to_dict(analysis)
    dm_dict = sa_to_dict(dm)

    try:
        # El servicio utiliza el Builder para mapear rbi_comp_oper_temp, etc.
        #
        result = ExternalDamageService.calculate_external_from_rows(
            comp=comp_dict,
            analysis=analysis_dict,
            dm=dm_dict
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Error en validación de datos: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en motor CUI: {e}")

    df_ext = result.get("df_external")
    trace = result.get("trace", {})

    if df_ext is None:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Cálculo incompleto. Revisa parámetros de entrada.",
                "status": trace.get("status"),
                "calc_message": trace.get("message")
            }
        )

    # 6) Persistir Resultado en rbi_581_external_results
    #
    try:
        saved = upsert_external_result(
            db=db,
            asset_pk=asset.asset_pk,
            component_pk=component.component_pk,
            analysis_pk=analysis.analysis_pk,
            dm_external_pk=dm.dm_extdamage_pk,
            df_external=float(df_ext),
            trace=trace
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar resultado: {e}")

    # 7) Respuesta final al cliente (Esquema ExternalComputeResponse)
    return ExternalComputeResponse(
        external_result_pk=saved.external_result_pk,
        df_external=saved.df_external,
        status=saved.status,
        message=saved.message
    )