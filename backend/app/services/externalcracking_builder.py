from __future__ import annotations
from datetime import date
from typing import Any, Optional
from app.calculations.externalCracking_calc import ExternalCrackingInputs

# --- Helpers ---
def _as_date(x: Any) -> Optional[date]:
    if x is None or x == "": return None
    if isinstance(x, date): return x
    return date.fromisoformat(str(x))

def _as_float(x: Any, default: float = 0.0) -> float:
    if x is None or x == "": return default
    return float(x)

def _as_int(x: Any, default: int = 0) -> int:
    if x is None or x == "": return default
    return int(float(x))

def build_cracking_inputs_from_rows(
    *,
    comp: dict,
    analysis: dict,
    dm: dict
) -> ExternalCrackingInputs:
    """
    Transforma diccionarios de DB en el objeto ExternalCrackingInputs.
    """
    # 1. Fechas Críticas
    # Si no hay fecha de instalación de recubrimiento, usamos la fecha de inicio del componente
    install_date = _as_date(comp.get("rbi_comp_comp_start_date"))
    calculation_date = _as_date(analysis.get("analysis_date"))
    coating_install_date = _as_date(dm.get("dm_extcrack_coating_install_date")) or install_date
    
    if not all([install_date, calculation_date]):
        raise ValueError("Faltan fechas críticas: rbi_comp_comp_start_date o analysis_date")

    # 2. Construcción del objeto de entrada para el motor
    return ExternalCrackingInputs(
        # Identificación
        mechanism=dm.get("dm_extcracking_dm"),
        susceptibility_type=dm.get("dm_extcrack_susceptibility_type", "Calculated"),
        susceptibility=dm.get("dm_extcrack_susceptibility", None),
        
        # Condiciones de Proceso
        temp_op=_as_float(comp.get("rbi_comp_oper_temp")),
        driver=dm.get("dm_extcrack_atm_condition", "Moderate"),
        
        # Fechas
        calculation_date=calculation_date,
        last_insp_date=_as_date(dm.get("dm_extcrack_last_know_insp_date")) or install_date,
        coating_install_date=coating_install_date,
        
        # Recubrimiento y Ajustes CUI
        anticipated_coating_life=_as_float(dm.get("dm_extcrack_anticipated_coating_life")),
        coating_quality=dm.get("dm_extcrack_coating_quality", "Medium"),
        coating_present=bool(dm.get("dm_extcrack_coating_present")),
        coating_failed_at_insp=bool(dm.get("dm_extcrack_coating_failed_at_insp")),
        
        # Factores Cualitativos (API 581 Step 1.1 - 1.3)
        complexity=dm.get("dm_extcrack_piping_complex", "Average"),
        insulation=dm.get("dm_extcrack_insulation_condition", "Average"),
        chloride_free=bool(dm.get("dm_extcrack_cl_free")),
        
        # Inspección (Step 9)
        highest_effectiveness=dm.get("dm_extcrack_high_effec_insp", "E"),
        number_of_inspections=_as_int(dm.get("dm_extcrack_num_high_effec_insp"))
    )