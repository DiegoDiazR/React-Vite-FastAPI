from __future__ import annotations
from datetime import date
from typing import Any, Optional

from app.calculations.externalDamage_calc_df import (
    CUIInputs,
    CUIInspectionEffectiveness
)
from app.calculations.externalDamage_presets import (
    get_cui_base_rate,
    build_cui_adjustment_factors,
    build_cui_probabilities
)

# --- Helpers (Reutilizados de thinning_builder) ---
def _as_date(x: Any) -> Optional[date]:
    if x is None or x == "": return None
    if isinstance(x, date): return x
    return date.fromisoformat(str(x))

def _as_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    if x is None or x == "": return default
    return float(x)

def _as_int(x: Any, default: int = 0) -> int:
    if x is None or x == "": return default
    return int(float(x))

def build_external_inputs_from_rows(
    *,
    comp: dict,
    analysis: dict,
    dm: dict
) -> CUIInputs:
    """
    Transforma diccionarios de base de datos en el objeto CUIInputs para el cálculo.
    """
    # 1. Identificación del Mecanismo y Modo
    dm_ext_dm = dm.get("dm_ext_dm")
    select_ext_corrosion = dm.get("dm_ext_select_ext_cr", "Calculated")
    
    # 2. Fechas Críticas
    install_date = _as_date(comp.get("rbi_comp_comp_start_date"))
    calculation_date = _as_date(analysis.get("analysis_date"))
    coating_install_date = _as_date(dm.get("dm_ext_coating_install_date")) or install_date
    last_thickness_date = _as_date(dm.get("dm_ext_last_know_insp_date"))

    if not all([install_date, calculation_date]):
        raise ValueError("Faltan fechas críticas: start_date o analysis_date")

    # 3. Datos Mecánicos y Espesores
    t = _as_float(comp.get("rbi_comp_nom_thk"), 0.0)
    tmin = _as_float(analysis.get("rbi_581_ove_min_req_thk"))
    tc = _as_float(analysis.get("rbi_581_ove_min_req_thk"), 0.0)
    
    # Espesor medido (t_rde)
    t_rde_measured = _as_float(dm.get("dm_ext_last_know_thk"))

    # 4. Propiedades del Material
    ys = _as_float(comp.get("rbi_comp_smys"), 0.0)
    ts = _as_float(comp.get("rbi_comp_uts"), 0.0)
    s = _as_float(analysis.get("rbi_581_allowable_stress"), 0.0)
    e = _as_float(comp.get("rbi_comp_weldj_eff"), 1.0)

    # 5. Tasa Base (Cálculo automático de presets)
    temp_op = _as_float(comp.get("rbi_comp_oper_temp"), 0.0) # Ajustar según tu columna
    driver = dm.get("dm_ext_atmosperic_condition", "Moderate")
    crb = get_cui_base_rate(temp_op, driver)

    # 6. Factores de Ajuste (Preset)
    factors = build_cui_adjustment_factors(
        dm_ext_dm=dm_ext_dm,
        insulation_type=comp.get("rbi_comp_insul_type", "Unknown/unspecified"),
        complexity=dm.get("dm_ext_piping_complex", "Average"),
        insulation_condition=dm.get("dm_ext_insulation_condition", "Average"),
        pooling_design=bool(dm.get("dm_ext_cr_adj_design")),
        soil_water_interface=bool(dm.get("dm_ext_sa_interface"))
    )

    # 7. Inspecciones y Probabilidades
    insp = CUIInspectionEffectiveness(
        N_A=_as_int(dm.get("dm_ext_number_a_level_insp")),
        N_B=_as_int(dm.get("dm_ext_number_b_level_insp")),
        N_C=_as_int(dm.get("dm_ext_number_c_level_insp")),
        N_D=_as_int(dm.get("dm_ext_number_d_level_insp"))
    )
    
    probs = build_cui_probabilities(confidence=dm.get("dm_ext_confidence", "medium"))

    # 8. Construcción Final
    return CUIInputs(
        dm_ext_dm=dm_ext_dm,
        select_ext_corrosion=select_ext_corrosion,
        ext_thinning_type=dm.get("dm_ext_thinning_type", "General"),
        ext_coating_quality=dm.get("dm_ext_coating_quality", "Medium"),
        install_date=install_date,
        calculation_date=calculation_date,
        coating_install_date=coating_install_date,
        last_thickness_date=last_thickness_date,
        base_mat_measured_rate=_as_float(dm.get("dm_ext_base_mat_measured_rate"), 0.0),
        t=t,
        t_rde_measured=t_rde_measured,
        tmin=tmin,
        tc=tc,
        CrB=crb,
        C_age=_as_float(dm.get("dm_ext_anticipated_coating_life"), 0.0),
        coating_failed_at_insp=bool(dm.get("dm_ext_coating_failed_at_insp")),
        YS=ys, TS=ts, S=s, E=e,
        insp=insp,
        probs=probs,
        factors=factors
    )