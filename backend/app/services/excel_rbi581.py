from __future__ import annotations

import io
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.schemas.schema import (
    AssetCreate,
    RBIComponentCreate,
    RBI581AnalysisCreate,
    RBI581ConsequenceCreate,
    DMThinningCreate,
    RBI581IntakeCreate,
    DMExternalDamageCreate,
    DMExternalCrackingDamageCreate
)
from app.schemas.excel_results import RowError, ExcelIntakeResult
from app.crud.crud import create_intake


# -----------------------------
# Helpers
# -----------------------------
def _clean_value(v):
    """Normalize Excel NaN -> None, strip strings."""
    if pd.isna(v):
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v != "" else None
    return v

def _row_to_dict(df: pd.DataFrame, idx: int) -> dict:
    row = df.iloc[idx].to_dict()
    return {k: _clean_value(v) for k, v in row.items()}

def _excel_row_number(df_index: int) -> int:
    # pandas idx starts at 0, Excel row is header(1) + data_row(1 + idx)
    return df_index + 2

def _key_for_analysis(asset_id: str, comp: str, comp_type: str, scenario: str, adate, arev) -> str:
    return f"{asset_id}|{comp}|{comp_type}|{scenario}|{adate}|{arev}"

def _key_for_component(asset_id: str, comp: str, comp_type: str) -> str:
    return f"{asset_id}|{comp}|{comp_type}"

def _require_fields(d: dict, fields: list[str]) -> Tuple[bool, list[str]]:
    missing = [f for f in fields if d.get(f) is None]
    return (len(missing) == 0, missing)


# -----------------------------
# Main loader
# -----------------------------
def load_rbi581_excel(db: Session, file_bytes: bytes) -> ExcelIntakeResult:
    result = ExcelIntakeResult()

    try:
        xls = pd.ExcelFile(io.BytesIO(file_bytes))
    except Exception as e:
        result.failed = 1
        result.errors.append(RowError(sheet="FILE", row=0, message="No se pudo leer el archivo Excel", details=str(e)))
        return result

    required_sheets = ["assets", 
                       "rbi_components", 
                       "rbi_581_analysis", 
                       "rbi_581_consequence", 
                       "dm_thinning", 
                       "dm_ExternalDamage",
                       "dm_ExternalCrackingDamage"]
    for s in required_sheets:
        if s not in xls.sheet_names:
            result.failed = 1
            result.errors.append(RowError(sheet="FILE", row=0, message=f"Falta la hoja requerida: {s}"))
            return result

    # Read sheets
    assets_df = pd.read_excel(xls, "assets")
    comps_df = pd.read_excel(xls, "rbi_components")
    analysis_df = pd.read_excel(xls, "rbi_581_analysis")
    conseq_df = pd.read_excel(xls, "rbi_581_consequence")
    dm_df = pd.read_excel(xls, "dm_thinning")
    dm_ext_df = pd.read_excel(xls, "dm_ExternalDamage")
    dm_extcracking_df = pd.read_excel(xls, "dm_ExternalCrackingDamage")

    # ---- 1) Parse assets (map by asset_id)
    assets_by_id: Dict[str, AssetCreate] = {}
    for i in range(len(assets_df)):
        row = _row_to_dict(assets_df, i)
        ok, missing = _require_fields(row, ["asset_id"])
        if not ok:
            result.failed += 1
            result.errors.append(RowError(sheet="assets", row=_excel_row_number(i),
                                          key=None, message=f"Faltan campos: {missing}"))
            continue
        try:
            assets_by_id[row["asset_id"]] = AssetCreate(**row)
        except Exception as e:
            result.failed += 1
            result.errors.append(RowError(sheet="assets", row=_excel_row_number(i),
                                          key=row.get("asset_id"), message="Validación falló", details=str(e)))

    # ---- 2) Parse components (map by component key)
    comps_by_key: Dict[str, RBIComponentCreate] = {}
    for i in range(len(comps_df)):
        row = _row_to_dict(comps_df, i)
        ok, missing = _require_fields(row, ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type"])
        if not ok:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_components", row=_excel_row_number(i),
                                          key=None, message=f"Faltan campos: {missing}"))
            continue

        asset_id = row["asset_id"]
        if asset_id not in assets_by_id:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_components", row=_excel_row_number(i),
                                          key=_key_for_component(asset_id, row["rbi_comp_comp"], row["rbi_comp_comp_type"]),
                                          message=f"asset_id no existe en hoja assets: {asset_id}"))
            continue

        try:
            comp_key = _key_for_component(asset_id, row["rbi_comp_comp"], row["rbi_comp_comp_type"])
            # quitar asset_id porque el schema de componente no lo incluye (lo usamos como join)
            row_no_asset = dict(row)
            row_no_asset.pop("asset_id", None)
            comps_by_key[comp_key] = RBIComponentCreate(**row_no_asset)
        except Exception as e:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_components", row=_excel_row_number(i),
                                          key=row.get("asset_id"), message="Validación falló", details=str(e)))

    # ---- 3) Parse analysis (map by analysis key)
    analysis_by_key: Dict[str, RBI581AnalysisCreate] = {}
    analysis_to_component_key: Dict[str, str] = {}  # analysis_key -> component_key
    for i in range(len(analysis_df)):
        row = _row_to_dict(analysis_df, i)
        ok, missing = _require_fields(row, ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev"])
        if not ok:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_581_analysis", row=_excel_row_number(i),
                                          key=None, message=f"Faltan campos: {missing}"))
            continue

        comp_key = _key_for_component(row["asset_id"], row["rbi_comp_comp"], row["rbi_comp_comp_type"])
        if comp_key not in comps_by_key:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_581_analysis", row=_excel_row_number(i),
                                          key=comp_key, message="No existe el componente (revisa rbi_components)"))
            continue

        akey = _key_for_analysis(
            row["asset_id"], row["rbi_comp_comp"], row["rbi_comp_comp_type"],
            row["rbi_581_scenario_id"], row["analysis_date"], int(row["analysis_rev"])
        )

        try:
            # quitar joins
            row_no_join = dict(row)
            for k in ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type"]:
                row_no_join.pop(k, None)
            # analysis_rev puede venir como float desde excel
            if row_no_join.get("analysis_rev") is not None:
                row_no_join["analysis_rev"] = int(row_no_join["analysis_rev"])
            analysis_by_key[akey] = RBI581AnalysisCreate(**row_no_join)
            analysis_to_component_key[akey] = comp_key
        except Exception as e:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_581_analysis", row=_excel_row_number(i),
                                          key=akey, message="Validación falló", details=str(e)))

    # ---- 4) Group consequences by analysis key
    conseq_by_analysis: Dict[str, List[RBI581ConsequenceCreate]] = defaultdict(list)
    for i in range(len(conseq_df)):
        row = _row_to_dict(conseq_df, i)
        ok, missing = _require_fields(row, ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev", "conseq_type", "conseq_rev"])
        if not ok:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_581_consequence", row=_excel_row_number(i),
                                          key=None, message=f"Faltan campos: {missing}"))
            continue

        akey = _key_for_analysis(
            row["asset_id"], row["rbi_comp_comp"], row["rbi_comp_comp_type"],
            row["rbi_581_scenario_id"], row["analysis_date"], int(row["analysis_rev"])
        )

        if akey not in analysis_by_key:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_581_consequence", row=_excel_row_number(i),
                                          key=akey, message="No existe el análisis (revisa rbi_581_analysis)"))
            continue

        try:
            row_no_join = dict(row)
            for k in ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev"]:
                row_no_join.pop(k, None)
            # conseq_rev puede venir como float desde excel
            if row_no_join.get("conseq_rev") is not None:
                row_no_join["conseq_rev"] = int(row_no_join["conseq_rev"])
            conseq_by_analysis[akey].append(RBI581ConsequenceCreate(**row_no_join))
        except Exception as e:
            result.failed += 1
            result.errors.append(RowError(sheet="rbi_581_consequence", row=_excel_row_number(i),
                                          key=akey, message="Validación falló", details=str(e)))

    # ---- 5) Group dm_thinning by analysis key
    dm_by_analysis: Dict[str, List[DMThinningCreate]] = defaultdict(list)
    for i in range(len(dm_df)):
        row = _row_to_dict(dm_df, i)
        ok, missing = _require_fields(row, ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev", "dm_thinning_dm", "location_key"])
        if not ok:
            result.failed += 1
            result.errors.append(RowError(sheet="dm_thinning", row=_excel_row_number(i),
                                          key=None, message=f"Faltan campos: {missing}"))
            continue

        akey = _key_for_analysis(
            row["asset_id"], row["rbi_comp_comp"], row["rbi_comp_comp_type"],
            row["rbi_581_scenario_id"], row["analysis_date"], int(row["analysis_rev"])
        )

        if akey not in analysis_by_key:
            result.failed += 1
            result.errors.append(RowError(sheet="dm_thinning", row=_excel_row_number(i),
                                          key=akey, message="No existe el análisis (revisa rbi_581_analysis)"))
            continue

        try:
            row_no_join = dict(row)
            for k in ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev"]:
                row_no_join.pop(k, None)
            dm_by_analysis[akey].append(DMThinningCreate(**row_no_join))
        except Exception as e:
            result.failed += 1
            result.errors.append(RowError(sheet="dm_thinning", row=_excel_row_number(i),
                                          key=akey, message="Validación falló", details=str(e)))
            
    # ---- 6) Group dm_external by analysis key        
    dm_ext_by_analysis = defaultdict(list)
    for i in range(len(dm_ext_df)):
        row = _row_to_dict(dm_ext_df, i)
        akey = _key_for_analysis(row["asset_id"], row["rbi_comp_comp"], row["rbi_comp_comp_type"],
                                 row["rbi_581_scenario_id"], row["analysis_date"], int(row["analysis_rev"]))
        
        if akey in analysis_by_key:
            row_no_join = dict(row)
            for k in ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev"]:
                row_no_join.pop(k, None)
            dm_ext_by_analysis[akey].append(DMExternalDamageCreate(**row_no_join))

    # ---- 7) NUEVO: Parse dm_external_cracking (Agrietamiento Austenítico) ----
    dm_extcracking_by_analysis = defaultdict(list)
    for i in range(len(dm_extcracking_df)):
        row = _row_to_dict(dm_extcracking_df, i)
        
        # Validación de campos obligatorios para el JOIN del Excel
        ok, missing = _require_fields(row, ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev"])
        if not ok:
            result.failed += 1
            result.errors.append(RowError(sheet="dm_ExternalCrackingDamage", row=_excel_row_number(i), message=f"Faltan campos de unión: {missing}"))
            continue

        akey = _key_for_analysis(row["asset_id"], row["rbi_comp_comp"], row["rbi_comp_comp_type"],
                                 row["rbi_581_scenario_id"], row["analysis_date"], int(row["analysis_rev"]))
        
        if akey not in analysis_by_key:
            result.failed += 1
            result.errors.append(RowError(sheet="dm_ExternalCrackingDamage", row=_excel_row_number(i), key=akey, message="Análisis no encontrado"))
            continue

        try:
            row_no_join = dict(row)
            # Limpiamos las columnas que se usaron para relacionar las hojas
            for k in ["asset_id", "rbi_comp_comp", "rbi_comp_comp_type", "rbi_581_scenario_id", "analysis_date", "analysis_rev"]:
                row_no_join.pop(k, None)
            
            # Instanciamos el Schema (Pydantic validará los tipos aquí)
            dm_extcracking_by_analysis[akey].append(DMExternalCrackingDamageCreate(**row_no_join))
        except Exception as e:
            result.failed += 1
            result.errors.append(RowError(sheet="dm_ExternalCrackingDamage", row=_excel_row_number(i), key=akey, message="Validación falló", details=str(e)))

    # ---- 6) Persist: for each analysis key create intake
    for akey, analysis_obj in analysis_by_key.items():
        comp_key = analysis_to_component_key[akey]

        # Reconstruir keys
        # comp_key = asset_id|comp|type
        asset_id, comp, comp_type = comp_key.split("|", 2)

        intake = RBI581IntakeCreate(
            asset=assets_by_id[asset_id],
            component=comps_by_key[comp_key],
            analysis=analysis_obj,
            consequences=conseq_by_analysis.get(akey, []),
            dm_thinning=dm_by_analysis.get(akey, []),
            dm_external=dm_ext_by_analysis.get(akey, []),
            dm_external_cracking=dm_extcracking_by_analysis.get(akey, []),
        )

        try:
            create_intake(db, intake)
            result.inserted_or_updated += 1
        except Exception as e:
            db.rollback()
            result.failed += 1
            result.errors.append(RowError(sheet="DB", row=0, key=akey, message="Error guardando en BD", details=str(e)))
            continue

    # Commit final si todo bien
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        result.failed += 1
        result.errors.append(RowError(sheet="DB", row=0, key=None, message="Error al hacer commit", details=str(e)))

    return result

    





