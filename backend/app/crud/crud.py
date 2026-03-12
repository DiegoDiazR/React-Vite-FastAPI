from __future__ import annotations
import json
from typing import Any, Optional, Sequence
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.asset import (
    Asset,
    RBIComponent,
    RBI581Analysis,
    RBI581Consequence,
    DMThinning,
    DMExternalDamage,
    DMExternalCrackingDamage,
)

from app.schemas.schema import (
    AssetCreate,
    RBIComponentCreate,
    RBI581AnalysisCreate,
    RBI581ConsequenceCreate,
    DMThinningCreate,
    DMExternalDamageCreate,
    RBI581IntakeCreate,
    DMExternalCrackingDamageCreate,
)

from app.models.rbi581_thinning_result import RBI581ThinningResult

# =========================================================
# Helpers
# =========================================================
def _set_attrs(obj, data: dict, *, exclude: set[str] | None = None) -> None:
    """Set attributes on SQLAlchemy model from dict, ignoring keys not present."""
    exclude = exclude or set()
    for k, v in data.items():
        if k in exclude:
            continue
        if hasattr(obj, k):
            setattr(obj, k, v)


# =========================================================
# ASSET
# =========================================================
def get_asset_by_asset_id(db: Session, asset_id: str) -> Optional[Asset]:
    stmt = select(Asset).where(Asset.asset_id == asset_id)
    return db.execute(stmt).scalar_one_or_none()


def upsert_asset(db: Session, payload: AssetCreate) -> Asset:
    asset = get_asset_by_asset_id(db, payload.asset_id)

    if asset is None:
        asset = Asset(**payload.model_dump())
        db.add(asset)
        db.flush()  # asigna asset_pk
        return asset

    # update (solo lo que venga)
    _set_attrs(asset, payload.model_dump(exclude_unset=True))
    db.flush()
    return asset


# =========================================================
# COMPONENT
# =========================================================
def get_component_by_business_key(
    db: Session,
    asset_pk: int,
    rbi_comp_comp: str,
    rbi_comp_comp_type: str,
) -> Optional[RBIComponent]:
    stmt = (
        select(RBIComponent)
        .where(RBIComponent.asset_pk == asset_pk)
        .where(RBIComponent.rbi_comp_comp == rbi_comp_comp)
        .where(RBIComponent.rbi_comp_comp_type == rbi_comp_comp_type)
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_component(
    db: Session,
    *,
    asset_pk: int,
    payload: RBIComponentCreate,
) -> RBIComponent:
    comp = get_component_by_business_key(
        db=db,
        asset_pk=asset_pk,
        rbi_comp_comp=payload.rbi_comp_comp,
        rbi_comp_comp_type=payload.rbi_comp_comp_type,
    )

    data = payload.model_dump(exclude_unset=True)
    if comp is None:
        comp = RBIComponent(asset_pk=asset_pk, **data)
        db.add(comp)
        db.flush()  # asigna component_pk
        return comp

    _set_attrs(comp, data, exclude={"asset_id"})  # asset_id no existe en el modelo
    db.flush()
    return comp


# =========================================================
# ANALYSIS
# =========================================================
def get_analysis_by_business_key(
    db: Session,
    component_pk: int,
    scenario_id: str,
    analysis_date,
    analysis_rev: int,
) -> Optional[RBI581Analysis]:
    stmt = (
        select(RBI581Analysis)
        .where(RBI581Analysis.component_pk == component_pk)
        .where(RBI581Analysis.rbi_581_scenario_id == scenario_id)
        .where(RBI581Analysis.analysis_date == analysis_date)
        .where(RBI581Analysis.analysis_rev == analysis_rev)
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_analysis(
    db: Session,
    *,
    component_pk: int,
    payload: RBI581AnalysisCreate,
) -> RBI581Analysis:
    analysis = get_analysis_by_business_key(
        db=db,
        component_pk=component_pk,
        scenario_id=payload.rbi_581_scenario_id,
        analysis_date=payload.analysis_date,
        analysis_rev=payload.analysis_rev,
    )

    data = payload.model_dump(exclude_unset=True)
    if analysis is None:
        analysis = RBI581Analysis(component_pk=component_pk, **data)
        db.add(analysis)
        db.flush()  # asigna analysis_pk
        return analysis

    _set_attrs(analysis, data)
    db.flush()
    return analysis


# =========================================================
# CONSEQUENCE
# =========================================================
def get_consequence_by_business_key(
    db: Session,
    analysis_pk: int,
    conseq_type: str,
    conseq_rev: int,
) -> Optional[RBI581Consequence]:
    stmt = (
        select(RBI581Consequence)
        .where(RBI581Consequence.analysis_pk == analysis_pk)
        .where(RBI581Consequence.conseq_type == conseq_type)
        .where(RBI581Consequence.conseq_rev == conseq_rev)
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_consequence(
    db: Session,
    *,
    analysis_pk: int,
    payload: RBI581ConsequenceCreate,
) -> RBI581Consequence:
    row = get_consequence_by_business_key(
        db=db,
        analysis_pk=analysis_pk,
        conseq_type=payload.conseq_type,
        conseq_rev=payload.conseq_rev,
    )

    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = RBI581Consequence(analysis_pk=analysis_pk, **data)
        db.add(row)
        db.flush()
        return row

    _set_attrs(row, data)
    db.flush()
    return row


# =========================================================
# DM THINNING
# =========================================================
def get_dm_thinning_by_business_key(
    db: Session,
    analysis_pk: int,
    dm: str,
    thinning_type: Optional[str],
    location_key: str,
) -> Optional[DMThinning]:
    stmt = (
        select(DMThinning)
        .where(DMThinning.analysis_pk == analysis_pk)
        .where(DMThinning.dm_thinning_dm == dm)
        .where(DMThinning.location_key == location_key)
    )

    # thinning_type puede ser NULL, entonces lo tratamos con cuidado
    if thinning_type is None:
        stmt = stmt.where(DMThinning.dm_thinning_thinning_type.is_(None))
    else:
        stmt = stmt.where(DMThinning.dm_thinning_thinning_type == thinning_type)

    return db.execute(stmt).scalar_one_or_none()


def upsert_dm_thinning(
    db: Session,
    *,
    analysis_pk: int,
    payload: DMThinningCreate,
) -> DMThinning:
    row = get_dm_thinning_by_business_key(
        db=db,
        analysis_pk=analysis_pk,
        dm=payload.dm_thinning_dm,
        thinning_type=payload.dm_thinning_thinning_type,
        location_key=payload.location_key,
    )

    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = DMThinning(analysis_pk=analysis_pk, **data)
        db.add(row)
        db.flush()
        return row

    _set_attrs(row, data)
    db.flush()
    return row


# =========================================================
# DM EXTERNAL
# =========================================================
def get_dm_external_by_business_key(
    db: Session,
    analysis_pk: int,
    dm_ext_dm: str,
    dm_ext_thinning_type: Optional[str] = None,
) -> Optional[DMExternalDamage]:
    """Busca un registro de daño externo basado en su restricción de unicidad."""
    stmt = (
        select(DMExternalDamage)
        .where(DMExternalDamage.analysis_pk == analysis_pk)
        .where(DMExternalDamage.dm_ext_dm == dm_ext_dm)
    )
    
    if dm_ext_thinning_type is None:
        stmt = stmt.where(DMExternalDamage.dm_ext_thinning_type.is_(None))
    else:
        stmt = stmt.where(DMExternalDamage.dm_ext_thinning_type == dm_ext_thinning_type)
        
    return db.execute(stmt).scalar_one_or_none()


def upsert_dm_external(
    db: Session,
    *,
    analysis_pk: int,
    payload: DMExternalDamageCreate,
) -> DMExternalDamage:
    row = get_dm_external_by_business_key(
        db=db,
        analysis_pk=analysis_pk,
        dm_ext_dm=payload.dm_ext_dm,
        dm_ext_thinning_type=payload.dm_ext_thinning_type,
    )

    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = DMExternalDamage(analysis_pk=analysis_pk, **data)
        db.add(row)
        db.flush()
        return row

    _set_attrs(row, data)
    db.flush()
    return row

# =========================================================
# DM EXTERNAL CRACKING (Inputs)
# =========================================================
def get_dm_external_cracking_by_business_key(
    db: Session,
    analysis_pk: int,
    dm_extcracking_dm: str,
) -> Optional[DMExternalCrackingDamage]:
    """Busca un registro de agrietamiento externo basado en su restricción de unicidad."""
    stmt = (
        select(DMExternalCrackingDamage)
        .where(DMExternalCrackingDamage.analysis_pk == analysis_pk)
        .where(DMExternalCrackingDamage.dm_extcracking_dm == dm_extcracking_dm)
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_dm_external_cracking(
    db: Session,
    *,
    analysis_pk: int,
    payload: DMExternalCrackingDamageCreate,
) -> DMExternalCrackingDamage:
    row = get_dm_external_cracking_by_business_key(
        db=db,
        analysis_pk=analysis_pk,
        dm_extcracking_dm=payload.dm_extcracking_dm,
    )

    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = DMExternalCrackingDamage(analysis_pk=analysis_pk, **data)
        db.add(row)
    else:
        _set_attrs(row, data)
    
    db.flush()
    return row

# =========================================================
# INTAKE (endpoint único)
# =========================================================
def create_intake(db: Session, payload: RBI581IntakeCreate):
    """
    Orquestador:
    - upsert asset
    - upsert component
    - upsert analysis
    - upsert consequences (N)
    - upsert dm_thinning (N)

    Retorna (asset, component, analysis, consequences, dm_thinning)
    """
    # Transacción: si algo falla, rollback automático si lo manejas en el router
    asset = upsert_asset(db, payload.asset)

    component = upsert_component(
        db,
        asset_pk=asset.asset_pk,
        payload=payload.component,
    )

    analysis = upsert_analysis(
        db,
        component_pk=component.component_pk,
        payload=payload.analysis,
    )

    consequences: list[RBI581Consequence] = []
    for c in payload.consequences:
        consequences.append(upsert_consequence(db, analysis_pk=analysis.analysis_pk, payload=c))

    dm_thin_rows: list[DMThinning] = []
    for d in payload.dm_thinning:
        dm_thin_rows.append(upsert_dm_thinning(db, analysis_pk=analysis.analysis_pk, payload=d))
    
    # --- NUEVO: Procesamiento de DM External ---
    dm_ext_rows = []
    for de in payload.dm_external:
        dm_ext_rows.append(upsert_dm_external(db, analysis_pk=analysis.analysis_pk, payload=de))

    dm_ext_crack_rows = []
    for d_crack in payload.dm_external_cracking:
        dm_ext_crack_rows.append(upsert_dm_external_cracking(db, analysis_pk=analysis.analysis_pk, payload=d_crack))

    return asset, component, analysis, consequences, dm_thin_rows, dm_ext_rows, dm_ext_crack_rows
    
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

# 1. Agrega la función de búsqueda por llave de negocio
def get_dm_external_by_business_key(db: Session, analysis_pk: int, dm_ext_dm: str, thinning_type: str):
    stmt = (
        select(DMExternalDamage)
        .where(DMExternalDamage.analysis_pk == analysis_pk)
        .where(DMExternalDamage.dm_ext_dm == dm_ext_dm)
        .where(DMExternalDamage.dm_ext_thinning_type == thinning_type)
    )
    return db.execute(stmt).scalar_one_or_none()

# 2. Agrega la función de guardado
def upsert_dm_external(db: Session, analysis_pk: int, payload: DMExternalDamageCreate) -> DMExternalDamage:
    row = get_dm_external_by_business_key(
        db, analysis_pk, payload.dm_ext_dm, payload.dm_ext_thinning_type
    )
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = DMExternalDamage(analysis_pk=analysis_pk, **data)
        db.add(row)
    else:
        _set_attrs(row, data)
    db.flush()
    return row