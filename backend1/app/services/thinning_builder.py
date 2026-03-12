from __future__ import annotations

from datetime import date
from typing import Any, Optional

from app.calculations.thinning0_corr_annex2B import CorrosionRouter, CorrosionCalcInput
from app.calculations.thinning_calc_df  import (
    ThinningInputs,
    ThinningInspectionEffectiveness,
    ThinningFactors,
)

# IMPORTANTE: Asegúrate de que estas funciones existan en tu archivo thinning_presets.py
from app.calculations.thinning_presets import (
    build_thinning_probabilities,
    get_liner_expected_life, 
    get_online_monitoring_factor,
)

# Instanciamos el router
corrosion_router = CorrosionRouter()


def _as_date(x: Any) -> Optional[date]:
    if x is None or x == "":
        return None
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x))

def _as_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    if x is None or x == "":
        return default
    return float(x)

def _as_int(x: Any, default: int = 0) -> int:
    if x is None or x == "":
        return default
    return int(float(x))

def _as_str(x: Any, default: str = "") -> str:
    """Convierte a string de forma segura y limpia espacios."""
    if x is None or x == "":
        return default
    return str(x).strip()


def build_thinning_inputs_from_rows(
    *,
    comp: dict,
    analysis: dict,
    dm: dict,
    corr_calc: dict
) -> ThinningInputs:
    
    # --- 1. Extraer Mecanismos y Selección ---
    dm_thinning = _as_str(dm.get("dm_thinning_dm", ""))
    gov_thinning_mech = _as_str(dm.get("dm_thinning_gov_thin_dm", ""))
    sel_type_cr_bm = _as_str(dm.get("dm_thinning_select_type_corrosion_rate", "Estimated Rate"))
    sel_type_cr_cm = _as_str(dm.get("dm_thinning_select_type_corrosion_rate_cladding", "Estimated Rate"))
    thinning_type = _as_str(dm.get("dm_thinning_thinning_type", "General"))

    confidence_level = _as_str(dm.get("dm_thinning_confidence", "Medium"))

    # --- 2. Fechas ---
    install_date = _as_date(comp.get("rbi_comp_comp_start_date"))
    inspection_date = _as_date(analysis.get("analysis_date"))
    last_thickness_date = _as_date(dm.get("dm_thinning_last_know_insp_date"))

    if install_date is None or inspection_date is None:
        raise ValueError("Faltan fechas: rbi_comp_comp_start_date y/o analysis_date")
    
    cladding_present = bool(comp.get("rbi_comp_cladding", False))
    liner_present = bool(comp.get("rbi_comp_liner", False))

    # --- 3. Espesores ---
    t = _as_float(comp.get("rbi_comp_nom_thk"))
    if t is None or t <= 0:
        raise ValueError("Falta rbi_comp_nom_thk (t) o es <= 0")

    t_rdi = _as_float(dm.get("dm_thinning_last_know_thk"), default=t)
    if t_rdi is None or t_rdi <= 0:
        raise ValueError("t_rdi inválido")

    tc = _as_float(comp.get("rbi_comp_min_struct_thk"), default=0.0) or 0.0
    if tc < 0:
        raise ValueError("tc (minimum structural thickness) no puede ser negativo")
        
    tcm = _as_float(comp.get("rbi_comp_furn_cladd_thk"), default=0.0) or 0.0
    if tcm < 0:
        raise ValueError("tcm (cladding thickness) no puede ser negativo")

    tmin = _as_float(analysis.get("rbi_581_ove_min_req_thk"))
    if tmin is None:
        tmin = _as_float(comp.get("rbi_comp_min_thk"))
    if tmin is None or tmin <= 0:
        raise ValueError("Falta tmin (>0)")

    # --- 4. Variables de Liner (CORREGIDO) ---  
    # 1. Inicializamos valores por defecto por si NO hay liner
    RL_exp_liner = 0.0
    F_LC = 1.0
    F_liner_OM = 1.0
    liner_type = ""
    install_liner_date = None

    # 2. Evaluamos solo si hay liner
    if liner_present:
        liner_type = _as_str(comp.get("rbi_comp_liner_type", ""))

        # VALIDACIÓN CORREGIDA: Verifica si la cadena está vacía
        if not liner_type:
            raise ValueError("Debe indicar el tipo de liner (liner_type) si el equipo tiene revestimiento.")

        install_liner_date = _as_date(comp.get("rbi_comp_install_liner_date")) # O la columna real del liner

        online_monitoring_lined_flag = bool(dm.get("dm_thinning_online_moni_linning_flag", False))
        condition = _as_str(dm.get("dm_thinning_liner_condition", "Average")).capitalize()

        RL_exp_liner = get_liner_expected_life(liner_type=liner_type, conservative=True)
        
        if condition == "Poor":
            F_LC = 10.0
        elif condition == "Average":
            F_LC = 2.0
        elif condition == "Good":
            F_LC = 1.0
        else:
            raise ValueError(f"Indicar condición de liner válida (Average - Poor - Good). Se recibió: '{condition}'")
        
        if online_monitoring_lined_flag:
            F_liner_OM = 0.1
        else:
            F_liner_OM = 1.0
        
    # --- 5. Diccionario de Proceso para Anexo 2B ---
    process = { 
        "temp": _as_float(comp.get("rbi_comp_oper_temp")),
        "velocity": _as_float(comp.get("rbi_comp_fluid_velocity")),
        "ph": _as_float(comp.get("rbi_comp_ph_water")),
        "oxi": bool(corr_calc.get("dm_thinning_air_oxidant_present", False)),
        "cl_wppm": _as_float(corr_calc.get("dm_thinning_cl_concentration")),

        # --- Variables Específicas por Mecanismo ---
    
        # Ácidos (Sulfúrico, HF)
        "sulfuric_conc":  _as_float(corr_calc.get("dm_thinning_cl_concentration")),
        "hf_conc":  _as_float(corr_calc.get("dm_thinning_hf_concentration")),
    
        # Acid / Alkaline Sour Water
        "water_present": bool(corr_calc.get("dm_thinning_water_present", False)),
        "chlorides_present": bool(corr_calc.get("dm_thinning_cl_present", False)),
        "oxygen_ppb": _as_float(corr_calc.get("dm_thinning_oxygen_process_stream")),
        "nh4hs_pct": _as_float(corr_calc.get("dm_thinning_nh4hs_concentration")),
        "ph2s_psia": _as_float(corr_calc.get("dm_thinning_h2s_partial_pressure")),
    
        # HTS / Nafténico / H2S
        "h2s_mole_pct": _as_float(corr_calc.get("dm_thinning_h2s_content")),
        "hydrocarbon_type": _as_str(corr_calc.get("dm_thinning_hydrocarbon_type")),
        "sulfur": _as_float(corr_calc.get("dm_thinning_sulphur_concent")),
        "tan": _as_float(comp.get("rbi_comp_total_acid_num")),
    
        # Aminas
        "amine_type": _as_str(corr_calc.get("dm_thinning_amine_type")),
        "amine_conc": _as_float(corr_calc.get("dm_thinning_amine_concentration")),
        "acid_gas_loading": _as_float(corr_calc.get("dm_thinning_acid_gas_loading")),
        "hsas_pct": _as_float(corr_calc.get("dm_thinning_heat_stable_amine_salts")),
    
        # Cooling Water
        "is_recirculation": bool(corr_calc.get("dm_thinning_cooling_sys_type", False)),
        "is_treated": bool(corr_calc.get("dm_thinning_water_type", False)),
        "is_seawater": bool(corr_calc.get("dm_thinning_water_treatm_type", False)),
        "cw_system_type": _as_str(corr_calc.get("dm_thinning_recirc_sys_type")),
        "tds": _as_float(corr_calc.get("dm_thinning_total_dissolved_solids")),
        "ca_hardness": _as_float(corr_calc.get("dm_thinning_calcium_hardness")),
        "mo_alkalinity": _as_float(corr_calc.get("dm_thinning_mo_alkalinity")),
    
        # Soil Side (Suelo)
        "tipo_suelo": _as_str(corr_calc.get("dm_thinning_soil_type")),
        "condicion_cp": _as_str(corr_calc.get("dm_thinning_cathodic_protect_effect")),
        "resistividad_ohm_cm": _as_str(corr_calc.get("dm_thinning_soil_resistivity")),
        "resistividad_ya_considerada_en_base": bool(corr_calc.get("dm_thinning_resistivity_consider_base", False)),
        "tiene_revestimiento": bool(corr_calc.get("dm_thinning_coating", False)),
        "tipo_revestimiento": _as_str(corr_calc.get("dm_thinning_coating_type")),
        "edad_mayor_20": bool(corr_calc.get("dm_thinning_coating_sup_age", False)),
        "temp_excedida": bool(corr_calc.get("dm_thinning_max_coating_temp_rating_exc", False)),
        "mantenimiento_raro": bool(corr_calc.get("dm_thinning_coating_mtto_rare_none", False)),
    
        # CO2 Corrosion
        "diameter_in": _as_float(comp.get("rbi_comp_diam")),
        "P_psia": _as_float(comp.get("rbi_comp_oper_press")),
        "liquid_hcs_present": bool(corr_calc.get("dm_thinning_present_hydrocarbon", False)),
        "water_content_pct": _as_float(corr_calc.get("dm_thinning_water_content_pct")),
        "water_weight_pct": _as_float(corr_calc.get("dm_thinning_water_weight_pct")),
        "co2_mole_pct": _as_float(corr_calc.get("dm_thinning_co2_concentration")),
        "pH_condition": _as_str(corr_calc.get("dm_thinning_ph_condition")),
        "rho_m": _as_float(corr_calc.get("dm_thinning_mix_density")),
        "mu_m_cp": _as_float(corr_calc.get("dm_thinning_dynamic_viscocity")),
        "e_m": _as_float(corr_calc.get("dm_thinning_rugosidad_interna"), default = 0.000045), 
        "glycol_pct": _as_float(corr_calc.get("dm_thinning_glycol_pct")),
        "inhibitor_efficiency": _as_float(corr_calc.get("dm_thinning_inhibitor_efficiency")),

    }

    # --- 6. Tasas de Corrosión (INTEGRACIÓN ANEXO 2B RECUPERADA) ---
    
    Cr_bm = 0.0
    
    # RESOLVEMOS Cr_bm:
    if sel_type_cr_bm == "Estimated Rate":
        Cr_bm = _as_float(dm.get("dm_thinning_base_mat_estimated_corr_rate"), 0.0)
    elif sel_type_cr_bm == "Measured Corrosion Rate":
        Cr_bm = _as_float(dm.get("dm_thinning_base_mat_measured_corr_rate"), 0.0)
    elif sel_type_cr_bm == "Short Term Avg":
        Cr_bm = _as_float(dm.get("dm_thinning_base_mat_short_term_avg_corr_rate"), 0.0)
    elif sel_type_cr_bm == "Long Term Avg":
        Cr_bm = _as_float(dm.get("dm_thinning_base_mat_long_term_avg_corr_rate"), 0.0)
    elif sel_type_cr_bm == "Calculated Rate":
        mat_bm = _as_str(comp.get("rbi_comp_base_mat"))
        if not mat_bm:
            raise ValueError("rbi_comp_base_mat es obligatorio si selecciona 'Calculated Rate'.")
        calc_input_bm = CorrosionCalcInput(mechanism=dm_thinning, material=mat_bm, **process)
        res_bm = corrosion_router.calculate_rates(calc_input_bm)
        Cr_bm = res_bm["corrosion_rate_in_yr"]

    Cr_cm = 0.0
    
    # RESOLVEMOS Cr_cm (Solo si hay cladding):
    if cladding_present:
        if sel_type_cr_cm == "Estimated Rate":
            Cr_cm = _as_float(dm.get("dm_thinning_cladding_estimated_corr_rate"), 0.0)
        elif sel_type_cr_cm == "Measured Corrosion Rate":
            Cr_cm = _as_float(dm.get("dm_thinning_cladding_measured_corr_rate"), 0.0)
        elif sel_type_cr_cm == "Short Term Avg":
            Cr_cm = _as_float(dm.get("dm_thinning_cladding_short_term_avg_corr_rate"), 0.0)
        elif sel_type_cr_cm == "Long Term Avg":
            Cr_cm = _as_float(dm.get("dm_thinning_cladding_long_term_avg_corr_rate"), 0.0)
        elif sel_type_cr_cm == "Calculated Rate":
            mat_cm = _as_str(comp.get("rbi_comp_cladding_mat"))
            if not mat_cm:
                raise ValueError("rbi_comp_cladding_mat es obligatorio si selecciona 'Calculated Rate'.")
            calc_input_cm = CorrosionCalcInput(mechanism=dm_thinning, material=mat_cm, **process)
            res_cm = corrosion_router.calculate_rates(calc_input_cm)
            Cr_cm = res_cm["corrosion_rate_in_yr"]

    if Cr_bm < 0 or Cr_cm < 0:
        raise ValueError("Las tasas de corrosión Cr_bm y Cr_cm no pueden ser negativas.")

   
    # Si eligieron Calculated Rate para Material Base, calculamos:
    if sel_type_cr_bm == "Calculated Rate":
        mat_bm = _as_str(comp.get("rbi_comp_material"))
        calc_input_bm = CorrosionCalcInput(mechanism=dm_thinning, 
                                           material=mat_bm, 
                                           **process)
        res_bm = corrosion_router.calculate_rates(calc_input_bm)
        Cr_bm = res_bm["corrosion_rate_in_yr"] # Sobrescribe la tasa

    # Si eligieron Calculated Rate para Cladding, calculamos:
    if cladding_present and sel_type_cr_cm == "Calculated Rate":
        mat_cm = _as_str(comp.get("rbi_comp_cladding_material"))
        calc_input_cm = CorrosionCalcInput(mechanism=dm_thinning, 
                                           material=mat_cm, 
                                           **process)
        res_cm = corrosion_router.calculate_rates(calc_input_cm)
        Cr_cm = res_cm["corrosion_rate_in_yr"] # Sobrescribe la tasa

    if Cr_bm < 0 or Cr_cm < 0:
        raise ValueError("Cr_bm / Cr_cm no pueden ser negativas")

    # --- 7. Esfuerzos / Resistencia ---
    YS = _as_float(comp.get("rbi_comp_smys"))
    TS = _as_float(comp.get("rbi_comp_uts"))
    S = _as_float(analysis.get("rbi_581_allowable_stress"))
    E = _as_float(comp.get("rbi_comp_weldj_eff"), default=1.0) or 1.0

    if not all([YS, TS, S]) or any(v <= 0 for v in [YS, TS, S]):
        raise ValueError("YS, TS y rbi_581_allowable_stress deben ser > 0")

    # --- 8. Inspecciones y Factores ---
    insp = ThinningInspectionEffectiveness(
        N_A=_as_int(dm.get("dm_thinning_number_a_level_insp"), 0),
        N_B=_as_int(dm.get("dm_thinning_number_b_level_insp"), 0),
        N_C=_as_int(dm.get("dm_thinning_number_c_level_insp"), 0),
        N_D=_as_int(dm.get("dm_thinning_number_d_level_insp"), 0),
    )

    # Banderas (Booleanos)
    online = bool(dm.get("dm_thinning_online_moni_flag") or False)
    inj = bool(dm.get("dm_thinning_injection_point_flag") or False)
    dl = bool(dm.get("dm_thinning_deadleg_flag") or False)

    # Banderas de métodos individuales
    key_process = bool(dm.get("dm_thinning_key_process_variable") or False)
    electrical_resist = bool(dm.get("dm_thinning_electrical_resist_probes") or False)
    corrosion_coupons = bool(dm.get("dm_thinning_corrosion_coupons") or False)

    # --- Cálculo de F_OM (Factor de Monitoreo General) ---
    F_OM = 1.0  # Valor por defecto si no hay monitoreo
    
    if online:
        methods_list = []
        if key_process: methods_list.append("Key Process Variable")
        if electrical_resist: methods_list.append("Electrical Resistance Probes")
        if corrosion_coupons: methods_list.append("Corrosion Coupons")
            
        # VALIDACIÓN QUE FALTABA
        if not methods_list:
            raise ValueError("Si dm_thinning_online_moni_flag es True, debe seleccionar al menos un método.")
            
        F_OM = get_online_monitoring_factor(
            mechanism=dm_thinning, 
            methods=methods_list
        )
    
    F_IP = 1.2 if inj else 1.0
    F_DL = 1.3 if dl else 1.0

    factors = ThinningFactors(F_OM=F_OM, F_IP=F_IP, F_DL=F_DL)
    probs = build_thinning_probabilities(confidence=confidence_level)

    # --- 9. Retorno del Objeto Final ---
    return ThinningInputs(
        dm_thinning=dm_thinning,
        governing_thinning_mechanism=gov_thinning_mech,
        select_type_corrosion_rate=sel_type_cr_bm,
        select_type_corrosion_rate_cladding=sel_type_cr_cm,
        ext_thinning_type=thinning_type,
        
        install_date=install_date,
        inspection_date=inspection_date,
        last_thickness_date=last_thickness_date,
        
        cladding_present=cladding_present,
        liner_present=liner_present,
        
        t=float(t),
        t_rdi=float(t_rdi),
        tc=float(tc),
        tmin=float(tmin),
        tcm=float(tcm),
        
        # Variables de liner inyectadas aquí
        liner_type=liner_type,
        install_liner_date=install_liner_date,
        RL_exp_liner=float(RL_exp_liner),
        F_LC=float(F_LC),
        F_liner_OM=float(F_liner_OM),
        
        Cr_bm=float(Cr_bm),
        Cr_cm=float(Cr_cm),
        
        YS=float(YS),
        TS=float(TS),
        S=float(S),
        E=float(E),
        
        insp=insp,
        probs=probs,
        factors=factors,
    )