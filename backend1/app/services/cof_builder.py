from __future__ import annotations

from typing import Any, Optional

from app.calculations.cof_4_0_orchestrator import COFScenarioInputs


def _as_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    """Convierte de forma segura a float, usando un default si es nulo o vacío."""
    if x is None or x == "":
        return default
    try:
        return float(x)
    except (ValueError, TypeError):
        return default


def _as_str(x: Any, default: str = "") -> str:
    """Convierte a string de forma segura y limpia espacios."""
    if x is None or x == "":
        return default
    return str(x).strip()


def build_cof_inputs_from_rows(
    *,
    comp: dict,
    conseq: dict,
) -> COFScenarioInputs:
    """
    Construye los inputs para el orquestador COF (API 581 Nivel 1) a partir 
    de representaciones en diccionario de la BD.
    """
    
    # ---------------------------------------------------------
    # 1. Datos Físicos y Operativos (Obligatorios para la física)
    # ---------------------------------------------------------
    fluid_name = _as_str(comp.get("rbi_comp_process_flu"), default="Water")
    stored_phase = _as_str(comp.get("rbi_comp_init_flu_phase"), default="Liquid")
    
    # Manejo de Temperatura (API 581 COF usa Kelvin como base en nuestro orquestador)
    # Asumimos que la BD guarda grados Celsius y los pasamos a Kelvin.
    # Si tu BD ya guarda Kelvin, quita el "+ 273.15".
    temp_c = _as_float(comp.get("rbi_comp_oper_temp"))
    if temp_c is None:
        raise ValueError("Falta la temperatura de operación (rbi_comp_oper_temp)")
    temperature_k = temp_c 

    pressure_gauge_psi = _as_float(comp.get("rbi_comp_oper_press"))
    if pressure_gauge_psi is None:
        raise ValueError("Falta la presión de operación (rbi_comp_oper_press)")

    # ---------------------------------------------------------
    # 2. Datos del Componente
    # ---------------------------------------------------------
    comp_type = _as_str(comp.get("rbi_comp_gff_comp_type")) or _as_str(comp.get("rbi_comp_comp_type"))
    if not comp_type:
        raise ValueError("Falta el tipo de componente para GFF (ej. PIPE-2)")

    diameter_in = _as_float(comp.get("rbi_comp_diam"))
    if diameter_in is None or diameter_in <= 0:
        raise ValueError("Falta el diámetro (rbi_comp_diam) o es <= 0")

    # Si faltan las longitudes, asumimos un default conservador, 
    # pero es mejor que estén.
    length_ft = _as_float(comp.get("rbi_comp_length"), default=100.0)
    length_circuit_ft = _as_float(comp.get("rbi_comp_pipe_circ_length"), default=100.0)

    # ---------------------------------------------------------
    # 3. Datos del Sistema y Mitigación
    # ---------------------------------------------------------
    patm_psi = _as_float(comp.get("rbi_comp_atm_press"), default=14.7)
    
    # Toxicidad
    toxic_mfrac = _as_float(comp.get("rbi_comp_percent_toxic"), default=0.0)
    
    # Sistemas (Vienen de la tabla de consecuencias en tu mapping)
    detection_rating = _as_str(conseq.get("rbi_conseq_detection_rating"), default="C")
    isolation_rating = _as_str(conseq.get("rbi_conseq_isolation_rating"), default="C")
    
    raw_mitigation = _as_str(conseq.get("rbi_conseq_mitigation_system_key"), default="none")
    mitigation_key = raw_mitigation.lower()

    # ---------------------------------------------------------
    # 4. Datos Financieros (Paso 4.12)
    # ---------------------------------------------------------
    material = _as_str(comp.get("rbi_comp_base_mat"), default="Carbon Steel")
    
    # Los costos pueden ser nulos en la BD, se manejan como $0.0
    equipment_cost_ft2 = _as_float(conseq.get("rbi_conseq_equip_cost"), default=0.0)
    production_cost_day = _as_float(conseq.get("rbi_conseq_production_cost"), default=0.0)
    injury_cost_person = _as_float(conseq.get("rbi_conseq_injury_cost"), default=0.0)
    environmental_cost_bbl = _as_float(conseq.get("rbi_conseq_env_clean_up_cost"), default=0.0)
    
    # Multiplicador de parada (Default 1.0 = normal, en tu test usaste 1.5)
    outage_multiplier = 1.0 

    # ---------------------------------------------------------
    # 5. Seguridad y Población (Paso 4.13)
    # ---------------------------------------------------------
    unit_area_ft2 = _as_float(conseq.get("rbi_conseq_unit_area_ft2"), default=10000.0)
    personnel_count = _as_float(conseq.get("rbi_conseq_personnel_count"), default=0.0)
    personnel_presence_pct = _as_float(conseq.get("rbi_conseq_personnel_presence_pct"), default=100.0)

    if unit_area_ft2 <= 0:
        raise ValueError("El área de la unidad (rbi_conseq_unit_area_ft2) debe ser > 0")

    # ---------------------------------------------------------
    # 6. Construir y Retornar
    # ---------------------------------------------------------
    return COFScenarioInputs(
        fluid_name=fluid_name,
        stored_phase=stored_phase,
        temperature_k=float(temperature_k),
        pressure_gauge_psi=float(pressure_gauge_psi),
        
        component_type=comp_type,
        component_family=_as_str(comp.get("rbi_comp_comp_fam"), default="Piping"),
        diameter_in=float(diameter_in),
        length_ft=float(length_ft),
        length_circuit_ft=float(length_circuit_ft),
        
        patm_psi=float(patm_psi),
        detection_rating=detection_rating,
        isolation_rating=isolation_rating,
        mitigation_system_key=mitigation_key,
        toxic_mfrac=float(toxic_mfrac),
        
        material_cost_factor=1.0, # Asumido 1.0 salvo que exista columna
        material=material,
        equipment_cost_ft2=float(equipment_cost_ft2),
        production_cost_day=float(production_cost_day),
        injury_cost_person=float(injury_cost_person),
        environmental_cost_bbl=float(environmental_cost_bbl),
        outage_multiplier=float(outage_multiplier),
        
        unit_area_ft2=float(unit_area_ft2),
        personnel_count=float(personnel_count),
        personnel_presence_pct=float(personnel_presence_pct)
    )