from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.core.db import get_db
from app.services.externalcracking_services import ExternalCrackingService
from app.crud.externalcracking_result import upsert_external_cracking_result
from app.schemas.schema import ExternalCrackingComputeResponse

# Modelos actualizados
from app.models.asset import Asset, RBIComponent, RBI581Analysis, DMExternalCrackingDamage

router = APIRouter(prefix="/rbi581", tags=["RBI581 - External Cracking"])

def sa_to_dict(obj) -> dict:
    """Convierte un modelo SQLAlchemy a dict con SOLO columnas (no relaciones)."""
    mapper = inspect(obj).mapper
    return {col.key: getattr(obj, col.key) for col in mapper.column_attrs}

@router.post(
    "/analysis/{analysis_pk}/dm-external-cracking/{dm_extcracking_pk}/compute", 
    response_model=ExternalCrackingComputeResponse
)
def compute_external_cracking(
    analysis_pk: int,
    dm_extcracking_pk: int,
    db: Session = Depends(get_db),
):
    # 1) Traer el Análisis (Validación de existencia)
    analysis = (
        db.query(RBI581Analysis)
        .filter(RBI581Analysis.analysis_pk == analysis_pk)
        .one_or_none()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail=f"Analysis no existe: {analysis_pk}")

    # 2) Traer Datos de Entrada de Agrietamiento (Inputs)
    dm = (
        db.query(DMExternalCrackingDamage)
        .filter(
            DMExternalCrackingDamage.dm_extcracking_pk == dm_extcracking_pk,
            DMExternalCrackingDamage.analysis_pk == analysis_pk,
        )
        .one_or_none()
    )
    if dm is None:
        raise HTTPException(
            status_code=404,
            detail=f"Registro de agrietamiento no existe o no pertenece al análisis: {dm_extcracking_pk}"
        )

    # 3) Traer el Componente (Para obtener rbi_comp_oper_temp y rbi_comp_comp_start_date)
    component = (
        db.query(RBIComponent)
        .filter(RBIComponent.component_pk == analysis.component_pk)
        .one_or_none()
    )
    if component is None:
        raise HTTPException(status_code=404, detail="Component no encontrado para este análisis.")

    # 4) Traer el Asset (Para el join de resultados)
    asset = db.query(Asset).filter(Asset.asset_pk == component.asset_pk).one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset no encontrado.")

    # 5) Ejecutar Cálculo (Transformación a diccionarios y envío al Service)
    comp_dict = sa_to_dict(component)
    analysis_dict = sa_to_dict(analysis)
    dm_dict = sa_to_dict(dm)

    try:
        # El servicio utiliza el Cracking Builder para mapear los inputs de API 581
        result = ExternalCrackingService.calculate_cracking_from_rows(
            comp=comp_dict,
            analysis=analysis_dict,
            dm=dm_dict
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Error en validación de datos: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en motor de agrietamiento: {e}")

    df_crack = result.get("df_externalcracking")
    trace = result.get("trace_json", {})

    if df_crack is None:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Cálculo de agrietamiento incompleto. Revisa parámetros.",
                "status": result.get("status"),
                "calc_message": result.get("message")
            }
        )

    # 6) Persistir Resultado en rbi_581_external_cracking_results
    try:
        saved = upsert_external_cracking_result(
            db=db,
            asset_pk=asset.asset_pk,
            component_pk=component.component_pk,
            analysis_pk=analysis.analysis_pk,
            dm_externalcracking_pk=dm.dm_extcracking_pk,
            df_externalcracking=float(df_crack),
            trace=trace
        )
        db.commit() # Confirmamos la transacción
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar resultado en base de datos: {e}")

    # 7) Respuesta final al cliente
    return ExternalCrackingComputeResponse(
        externalcracking_result_pk=saved.externalcracking_result_pk,
        df_externalcracking=saved.df_externalcracking,
        status=saved.status,
        message=saved.message,
        computed_at=saved.computed_at
    )