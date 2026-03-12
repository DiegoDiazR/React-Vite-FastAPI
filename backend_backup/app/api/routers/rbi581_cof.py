from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.core.db import get_db
from app.services.cof_services import COFService
from app.crud.cof_result import upsert_cof_result
from app.schemas.schema import COFComputeResponse

# Importa tus modelos reales (Ajusta las rutas según tu proyecto)
from app.models.asset import Asset
from app.models.asset import RBIComponent
from app.models.asset import RBI581Analysis
from app.models.asset import RBI581Consequence

router = APIRouter(prefix="/rbi581", tags=["RBI581 - COF"])

def sa_to_dict(obj) -> dict:
    """Convierte un modelo SQLAlchemy a dict con SOLO columnas (no relaciones)."""
    mapper = inspect(obj).mapper
    return {col.key: getattr(obj, col.key) for col in mapper.column_attrs}


@router.post("/analysis/{analysis_pk}/consequence/{consequence_pk}/compute", response_model=COFComputeResponse)
def compute_cof(
    analysis_pk: int,
    consequence_pk: int,
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

    # 2) Traer Consequence (validando que pertenece al analysis)
    consequence = (
        db.query(RBI581Consequence)
        .filter(
            RBI581Consequence.consequence_pk == consequence_pk,
            RBI581Consequence.analysis_pk == analysis_pk,
        )
        .one_or_none()
    )
    if consequence is None:
        raise HTTPException(
            status_code=404,
            detail=f"Consecuencia no existe o no pertenece al analysis: conseq={consequence_pk}, analysis={analysis_pk}",
        )

    # 3) Traer Component
    component = (
        db.query(RBIComponent)
        .filter(RBIComponent.component_pk == analysis.component_pk)
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
    conseq_dict = sa_to_dict(consequence)

    try:
        # Llamada a nuestro servicio (que internamente llama al builder y al orquestador)
        result_dict = COFService.calculate_cof_from_rows(
            comp=comp_dict,
            conseq=conseq_dict,
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Faltan datos requeridos para el cálculo COF: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en motor COF: {e}")

    # 6) Guardar resultado en DB
    try:
        saved = upsert_cof_result(
            db=db,
            asset_pk=asset.asset_pk,
            component_pk=component.component_pk,
            analysis_pk=analysis.analysis_pk,
            consequence_pk=consequence.consequence_pk,
            cof_data=result_dict,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar los resultados del COF: {e}")

    # 7) Devolver la respuesta
    return COFComputeResponse(
        cof_result_pk=saved.cof_result_pk,
        final_cof_area_ft2=saved.final_cof_area_ft2,
        financial_total_cost=saved.financial_total_cost,
        safety_personnel_affected=saved.safety_personnel_affected,
        status=saved.status,
        message=saved.message,
    )