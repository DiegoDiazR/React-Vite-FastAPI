# app/schemas/rbi_581.py
from __future__ import annotations

from datetime import date, datetime

from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# =========================================================
# Base config (para responder desde SQLAlchemy ORM)
# =========================================================
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# ASSET
# =========================================================
class AssetBase(BaseModel):
    asset_id: str = Field(..., max_length=255)
    asset_id_cmms_sys: Optional[str] = Field(default=None, max_length=255)
    asset_id_equip_tech_num: Optional[str] = Field(default=None, max_length=255)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_id_cmms_sys: Optional[str] = Field(default=None, max_length=255)
    asset_id_equip_tech_num: Optional[str] = Field(default=None, max_length=255)


class AssetOut(ORMBase, AssetBase):
    asset_pk: int


# =========================================================
# RBI COMPONENT
# =========================================================
class RBIComponentBase(BaseModel):
    # business keys
    rbi_comp_comp: str = Field(..., max_length=255)
    rbi_comp_comp_type: str = Field(..., max_length=255)

    # data
    rbi_comp_comp_fam: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_comp_desc: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_comp_start_date: Optional[date] = None
    rbi_comp_circuit_from: Optional[str] = Field(default=None, max_length=250)
    rbi_comp_circuit_to: Optional[str] = Field(default=None, max_length=250)
    rbi_comp_comp_comm: Optional[str] = None  # Text

    rbi_comp_oper_press: Optional[float] = None
    rbi_comp_oper_temp: Optional[float] = None
    rbi_comp_atm_press: Optional[float] = None  # <--- NUEVO

    rbi_comp_found_type: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_init_flu_phase: Optional[str] = Field(default=None, max_length=20)
    rbi_comp_process_flu: Optional[str] = Field(default=None, max_length=50)

    rbi_comp_toxic_mixture: Optional[bool] = None
    rbi_comp_toxic_fluid: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_percent_toxic: Optional[float] = None

    rbi_comp_inven: Optional[float] = None
    rbi_comp_inven_group: Optional[str] = Field(default=None, max_length=50)

    rbi_comp_design_press: Optional[float] = None
    rbi_comp_design_temp: Optional[float] = None

    rbi_comp_diam: Optional[float] = None
    rbi_comp_length: Optional[float] = None
    rbi_comp_fill_height: Optional[float] = None
    rbi_comp_nom_thk: Optional[float] = None
    
    rbi_comp_smys: Optional[float] = None
    rbi_comp_uts: Optional[float] = None
    
    rbi_comp_stress_table: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_bm_code: Optional[str] = Field(default=None, max_length=30)
    rbi_comp_bm_year: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_bm_spec: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_bm_grade: Optional[str] = Field(default=None, max_length=50)

    rbi_comp_weldj_eff: Optional[float] = None

    rbi_comp_insul: Optional[bool] = None
    rbi_comp_insul_type: Optional[str] = Field(default=None, max_length=200)

    rbi_comp_injec_point: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_pipe_circ_length: Optional[float] = None

    rbi_comp_pwht: Optional[bool] = None

    rbi_comp_inter_corr_type: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_predic_int_corr_loc: Optional[bool] = None

    rbi_comp_est_int_corr_rate: Optional[float] = None
    rbi_comp_est_ext_corr_rate: Optional[float] = None
    rbi_comp_measu_ext_corr_rate: Optional[float] = None
    rbi_comp_source_cal_corr_rate: Optional[str] = Field(default=None, max_length=50)

    rbi_comp_perc_liquid_vol: Optional[float] = None

    rbi_comp_detect_sys: Optional[str] = Field(default=None, max_length=4)
    rbi_comp_isolate_sys: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_mitigat_sys: Optional[str] = Field(default=None, max_length=60)

    rbi_comp_fluid_velocity: Optional[float] = None
    rbi_comp_ph_water: Optional[float] = None

    rbi_comp_geom_type: Optional[str] = Field(default=None, max_length=60)
    rbi_comp_gff_comp_type: Optional[str] = Field(default=None, max_length=50)

    rbi_comp_cladding: Optional[bool] = None
    rbi_comp_furn_cladd_thk: Optional[float] = None
    rbi_comp_min_struct_thk: Optional[float] = None

    rbi_comp_liner: Optional[bool] = None
    rbi_comp_liner_type: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_install_liner_date: Optional[date] = None # <---- Nuevo

    rbi_comp_release_prev_barrier: Optional[bool] = None

    rbi_comp_cm_corrosion_rate: Optional[float] = None
    rbi_comp_corrosion_allow: Optional[float] = None

    rbi_comp_intrusive: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_min_thk: Optional[float] = None

    rbi_comp_base_mat: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_cladding_mat: Optional[str] = Field(default=None, max_length=50)
    rbi_comp_total_acid_num: Optional[float] = None


class RBIComponentCreate(RBIComponentBase):
    pass


class RBIComponentOut(ORMBase, RBIComponentBase):
    component_pk: int
    asset_pk: int


# =========================================================
# RBI 581 ANALYSIS
# =========================================================
class RBI581AnalysisBase(BaseModel):
    rbi_581_analysis_unique_id: Optional[str] = Field(default=None, max_length=255)

    rbi_581_scenario_id: str = Field(..., max_length=255)
    analysis_date: date
    analysis_rev: int = 0

    rbi_581_coeff_y_mat: Optional[str] = Field(default=None, max_length=255)
    rbi_581_stress_override: Optional[float] = None
    rbi_581_allowable_stress: Optional[float] = None
    rbi_581_flow_stress: Optional[float] = None
    rbi_581_ove_min_req_thk: Optional[float] = None
    rbi_581_course_num: Optional[int] = None


class RBI581AnalysisCreate(RBI581AnalysisBase):
    pass


class RBI581AnalysisOut(ORMBase, RBI581AnalysisBase):
    analysis_pk: int
    component_pk: int


# =========================================================
# CONSEQUENCE
# =========================================================
class RBI581ConsequenceBase(BaseModel):
    conseq_type: str = Field(..., max_length=50)
    conseq_rev: int = 0

    rbi_conseq_use_calc_invent: Optional[bool] = None
    rbi_conseq_invent_group_mass: Optional[float] = None
    rbi_conseq_inc_personal_injury: Optional[bool] = None

    rbi_conseq_injury_cost: Optional[float] = None
    rbi_conseq_equip_cost: Optional[float] = None
    rbi_conseq_production_cost: Optional[float] = None
    rbi_conseq_env_clean_up_cost: Optional[float] = None

    rbi_conseq_total_financial: Optional[bool] = None
    rbi_conseq_user_total_financial: Optional[float] = None

    rbi_conseq_mfh_ast: Optional[float] = None
    rbi_conseq_fluid_perc_leav_dike: Optional[float] = None
    rbi_conseq_fluid_perc_onsite: Optional[float] = None
    rbi_conseq_fluid_perc_offsite: Optional[float] = None

    rbi_conseq_env_sensitivity: Optional[str] = Field(default=None, max_length=100)
    rbi_conseq_tank_course_height: Optional[float] = None
    rbi_conseq_dist_bottom_gwater: Optional[float] = None
    rbi_conseq_soil_type_under_tank: Optional[str] = Field(default=None, max_length=100)

    # <--- NUEVOS --->
    rbi_conseq_detection_rating: Optional[str] = Field(default=None, max_length=10)
    rbi_conseq_isolation_rating: Optional[str] = Field(default=None, max_length=10)
    rbi_conseq_mitigation_system_key: Optional[str] = Field(default=None, max_length=50)
    
    rbi_conseq_unit_area_ft2: Optional[float] = None
    rbi_conseq_personnel_count: Optional[float] = None
    rbi_conseq_personnel_presence_pct: Optional[float] = None


class RBI581ConsequenceCreate(RBI581ConsequenceBase):
    pass


class RBI581ConsequenceOut(ORMBase, RBI581ConsequenceBase):
    consequence_pk: int
    analysis_pk: int


# =========================================================
# DM THINNING
# =========================================================
class DMThinningBase(BaseModel):
    dm_thinning_dm: str = Field(..., max_length=255)
    dm_thinning_thinning_type: Optional[str] = Field(default=None, max_length=255)
    location_key: str = Field(default="GLOBAL", max_length=100)

    dm_thinning_gov_thin_dm: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_last_know_insp_date: Optional[date] = None
    dm_thinning_last_know_thk: Optional[float] = None

    # dm_thinning_base_mat_corr_rate: Optional[float] = None
    # dm_thinning_long_term_avg_corr_rate: Optional[float] = None
    # dm_thinning_short_term_avg_corr_rate: Optional[float] = None
    # dm_thinning_cladd_mat_corr_rate: Optional[float] = None

    # TASAS DE CORROSIÓN - MATERIAL BASE
    dm_thinning_base_mat_estimated_corr_rate: Optional[float] = None
    dm_thinning_base_mat_measured_corr_rate: Optional[float] = None
    dm_thinning_base_mat_short_term_avg_corr_rate: Optional[float] = None
    dm_thinning_base_mat_long_term_avg_corr_rate: Optional[float] = None

    # TASAS DE CORROSIÓN - CLADDING
    dm_thinning_cladding_estimated_corr_rate: Optional[float] = None
    dm_thinning_cladding_measured_corr_rate: Optional[float] = None
    dm_thinning_cladding_short_term_avg_corr_rate: Optional[float] = None
    dm_thinning_cladding_long_term_avg_corr_rate: Optional[float] = None

    dm_thinning_number_a_level_insp: Optional[int] = None
    dm_thinning_number_b_level_insp: Optional[int] = None
    dm_thinning_number_c_level_insp: Optional[int] = None
    dm_thinning_number_d_level_insp: Optional[int] = None

    dm_thinning_highest_effect_insp_level: Optional[str] = Field(default=None, max_length=255)
    dm_thinning_num_highest_effect_insp_level: Optional[int] = None

    dm_thinning_injection_point_flag: Optional[bool] = None
    dm_thinning_injection_point_inspect: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_deadleg_flag: Optional[bool] = None
    dm_thinning_deadleg_inspect: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_welded_const_flag: Optional[bool] = None
    dm_thinning_api653_mtto_flag: Optional[bool] = None

    dm_thinning_foundation_type: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_sett_adjus_flag: Optional[bool] = None
    dm_thinning_sett_adjus_inspect: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_online_moni_flag: Optional[bool] = None
    dm_thinning_key_process_variable: Optional[bool] = None

    dm_thinning_electrical_resist_probes: Optional[bool] = None
    dm_thinning_corrosion_coupons: Optional[bool] = None
    
    dm_thinning_online_moni_linning_flag: Optional[bool] = None # < ------- Nuevo

    dm_thinning_cl_concentration: Optional[float] = None
    dm_thinning_air_oxidant_present: Optional[bool] = None
    dm_thinning_soil_resistivity: Optional[float] = None

    dm_thinning_h2s_content: Optional[float] = None
    dm_thinning_hydrocarbon_type: Optional[str] = Field(default=None, max_length=255)
    dm_thinning_sulphur_concent: Optional[float] = None

    dm_thinning_cooling_sys_type: Optional[bool] = None
    dm_thinning_water_type: Optional[bool] = None
    dm_thinning_water_treatm_type: Optional[bool] = None
    dm_thinning_recirc_sys_type: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_calcium_hardness: Optional[float] = None
    dm_thinning_total_dissolved_solids: Optional[float] = None
    dm_thinning_mo_alkalinity: Optional[float] = None

    dm_thinning_oxygen_process_stream: Optional[float] = None
    dm_thinning_acid_concentration: Optional[float] = None

    dm_thinning_soil_type: Optional[str] = Field(default=None, max_length=255)

    dm_thinning_cathodic_protect_effect: Optional[str] = Field(default=None, max_length=255)
    
    dm_thinning_resistivity_consider_base: Optional[bool] = None # < ------- Nuevo

    dm_thinning_coating: Optional[bool] = None
    dm_thinning_coating_age: Optional[float] = None
    dm_thinning_max_coating_temp_rating_exc: Optional[bool] = None
    dm_thinning_coating_mtto_rare_none: Optional[str] = Field(default=None, max_length=255)
    dm_thinning_coating_type: Optional[str] = Field(default=None, max_length=255)
    dm_thinning_coating_sup_age: Optional[bool] = None # < ------- Nuevo

    dm_thinning_amine_type: Optional[str] = Field(default=None, max_length=255)
    dm_thinning_heat_stable_amine_salts: Optional[float] = None
    dm_thinning_acid_gas_loading: Optional[float] = None
    dm_thinning_amine_concentration: Optional[float] = None

    dm_thinning_hf_concentration: Optional[float] = None
    dm_thinning_h2s_partial_pressure: Optional[float] = None
    dm_thinning_nh4hs_concentration: Optional[float] = None

    dm_thinning_water_present: Optional[float] = None # < ------- Nuevo
    dm_thinning_cl_present: Optional[float] = None    # < ------- Nuevo

    # para co2
    dm_thinning_present_hydrocarbon: Optional[bool] = None       # < ------- Nuevo
    dm_thinning_water_content_pct: Optional[float] = None        # < ------- Nuevo
    dm_thinning_water_weight_pct: Optional[float] = None         # < ------- Nuevo
    dm_thinning_co2_concentration: Optional[float] = None        # < ------- Nuevo
    dm_thinning_ph_condition: Optional[str] = Field(default=None, max_length=255)  # < ------- Nuevo
    dm_thinning_mix_density: Optional[float] = None              # < ------- Nuevo
    dm_thinning_dynamic_viscocity: Optional[float] = None        # < ------- Nuevo
    dm_thinning_rugosidad_interna: Optional[float] = None        # < ------- Nuevo
    dm_thinning_glycol_pct: Optional[float] = None               # < ------- Nuevo
    dm_thinning_inhibitor_efficiency: Optional[float] = None     # < ------- Nuevo
    
    dm_thinning_liner_condition: Optional[str] = Field(default=None, max_length=255)

class DMThinningCreate(DMThinningBase):
    pass


class DMThinningOut(ORMBase, DMThinningBase):
    dm_thinning_pk: int
    analysis_pk: int


# =========================================================
# DM EXTERNAL
# =========================================================

# --- Definición de Literales según API 581 ---
#
DAMAGE_MECHANISM = Literal[
    "581-Ferritic Component Atmospheric Corrosion", 
    "581-Ferritic Component Corrosion UnderInsulation"
]

EXTERNAL_THINNING_TYPES = Literal["General", "Localized", "Pitting"]

CORROSION_MODE = Literal["Estimated", "Calculated", "Measured"]
INSULATION_TYPES = Literal[
    "Unknown/unspecified", "Asbestos", "Cellular glass", "Expanded perlite",
    "Fiberglass", "Type E fiberglass", "Mineral wool", "Mineral wool (water resistant)",
    "Calcium silicate", "Flexible aerogel", "Microporous blanket", 
    "Intumescent coating", "Cementitious coating"
]
DRIVER_OPTIONS = Literal["Severe", "Moderate", "Mild", "Dry"]
QUALITATIVE_OPTIONS = Literal["Below Average", "Average", "Above Average"]
CONFIDENCE_LEVEL = Literal["low", "medium", "high"]

class DMExternalDamageBase(BaseModel):
    # Mecanismo e Identificadores
    dm_ext_dm: DAMAGE_MECHANISM = "581-Ferritic Component Atmospheric Corrosion"
    dm_ext_select_ext_cr: CORROSION_MODE = "Calculated"
    dm_ext_confidence: CONFIDENCE_LEVEL = "medium"
    
    # Datos de Corrosión y Espesores [cite: 15, 17, 43, 45, 131]
    # Nota: Aunque en DB es String, en Pydantic lo tratamos como float para el cálculo
    dm_ext_base_mat_measured_rate: Optional[float] = Field(0.0, ge=0)
    dm_ext_last_know_thk: Optional[float] = Field(None, ge=0)
    dm_ext_last_know_insp_date: Optional[date] = None
    
    # Recubrimiento (Step 6-8) [cite: 48, 52, 57]
    dm_ext_coating_quality: Optional[str] = None
    dm_ext_coating_install_date: Optional[date] = None
    dm_ext_anticipated_coating_life: float = Field(0.0, ge=0) # Cage
    dm_ext_coating_failed_at_insp: bool = False
    
    # Factores de Ajuste (Step 4) [cite: 26, 31, 38, 40, 41, 140]
    dm_ext_thinning_type: EXTERNAL_THINNING_TYPES = "General" # F_INS
    dm_ext_atmosperic_condition: DRIVER_OPTIONS = "Moderate"       # Driver
    dm_ext_piping_complex: QUALITATIVE_OPTIONS = "Average"         # F_CM
    dm_ext_insulation_condition: QUALITATIVE_OPTIONS = "Average"   # F_IC
    dm_ext_cr_adj_design: bool = False                             # F_EQ
    dm_ext_sa_interface: bool = False                              # F_IF
    
    # Conteo de Inspecciones (Step 14) [cite: 97]
    dm_ext_number_a_level_insp: int = Field(0, ge=0)
    dm_ext_number_b_level_insp: int = Field(0, ge=0)
    dm_ext_number_c_level_insp: int = Field(0, ge=0)
    dm_ext_number_d_level_insp: int = Field(0, ge=0)

    class Config:
        from_attributes = True

class DMExternalDamageCreate(DMExternalDamageBase):
    pass

#     analysis_pk: int

#     @field_validator("dm_ext_base_mat_measured_rate")
#     @classmethod
#     def validate_measured_rate(cls, v: float, info: Any):
#         """Valida que si la tasa es manual, el valor sea mayor a 0."""
#         #
#         if info.data.get("dm_ext_select_ext_cr") in ("Measured", "Estimated") and v <= 0:
#             raise ValueError(
#                 f"Debe proporcionar una tasa mayor a 0 para el modo '{info.data.get('dm_ext_select_ext_cr')}'"
#             )
#         return v

class DMExternalDamageUpdate(DMExternalDamageBase):
    pass

class DMExternalDamageOut(ORMBase, DMExternalDamageBase):
    dm_extdamage_pk: int  # Corregido para coincidir con el modelo
    analysis_pk: int      #



# =========================================================
# DM EXTERNAL CRACKING (Austeníticos)
# =========================================================

# --- Definición de Literales según API 581 ---
CRACKING_MECHANISM = Literal[
    "581-Austenitic Component Atmospheric Cracking", 
    "581-Austenitic Component Cracking Under Insulation"
]

SUSCEPTIBILITY_MODE = Literal["Estimated", "Calculated", "Measured"]

SUSCEPTIBILITY_LEVELS = Literal["None_", "Low", "Medium", "High"]

COATING_QUALITY_CRACK = Literal["No coating or primer only", "Medium", "High"]

DRIVER_CRACKING = Literal["Severe", "Moderate", "Mild", "Dry"]

QUALITATIVE_CRACKING = Literal["Below Average", "Average", "Above Average"]

class DMExternalCrackingDamageBase(BaseModel):
    # Mecanismo e Identificadores
    dm_extcracking_dm: CRACKING_MECHANISM = "581-Austenitic Component Atmospheric Cracking"
    dm_extcrack_susceptibility_type: SUSCEPTIBILITY_MODE = "Calculated"
    
    # Datos de Susceptibilidad y Driver
    dm_extcrack_susceptibility: Optional[SUSCEPTIBILITY_LEVELS] = None
    dm_extcrack_atm_condition: DRIVER_CRACKING = "Moderate"
    
    # Recubrimiento (Step 6-8)
    dm_extcrack_coating_present: bool = False
    
    dm_extcrack_coating_install_date: Optional[date] = None
    dm_extcrack_coating_quality: Optional[COATING_QUALITY_CRACK] = None
    dm_extcrack_anticipated_coating_life: Optional[float] = Field(0.0, ge=0)
    dm_extcrack_coating_failed_at_insp: Optional[bool] = False
    
    # Ajustes CUI (Step 1.1-1.3)
    dm_extcrack_piping_complex: Optional[QUALITATIVE_CRACKING] = None
    dm_extcrack_insulation_condition: Optional[QUALITATIVE_CRACKING] = None
    dm_extcrack_cl_free: Optional[bool] = None
    
    # Inspecciones y Fechas
    dm_extcrack_last_know_insp_date: Optional[date] = None
    dm_extcrack_high_effec_insp: str = "E"  # Nivel A, B, C, D o E
    dm_extcrack_num_high_effec_insp: int = Field(0, ge=0)

    class Config:
        from_attributes = True
    
    @model_validator(mode="after")
    def validate_logic_by_type(self) -> "DMExternalCrackingDamageBase":
        # --- Lógica de Susceptibilidad ---
        # s_type = self.dm_extcrack_susceptibility_type
        # if s_type == "Calculated" and self.dm_extcrack_piping_complex is None:
        #     raise ValueError("Para tipo 'Calculated', la complejidad es obligatoria.")
        
        # --- Validación de Recubrimiento ---
        if self.dm_extcrack_coating_present:
            # Si hay recubrimiento, exigimos los datos mínimos para el Step 7
            if self.dm_extcrack_coating_quality is None:
                raise ValueError("Si el recubrimiento está presente, la calidad es obligatoria.")
            if self.dm_extcrack_coating_install_date is None:
                raise ValueError("Si el recubrimiento está presente, la fecha de instalación es obligatoria.")
        
        return self

class DMExternalCrackingDamageCreate(DMExternalCrackingDamageBase):
    pass


class DMExternalCrackingDamageUpdate(DMExternalCrackingDamageBase):
    pass

class DMExternalCrackingDamageOut(DMExternalCrackingDamageBase):
    dm_extcracking_pk: int  # Primary Key del modelo
    analysis_pk: int

# =========================================================
# INTAKE (para endpoint único de entrada)
# =========================================================
class RBI581IntakeCreate(BaseModel):
    asset: AssetCreate
    component: RBIComponentCreate
    analysis: RBI581AnalysisCreate

    # muchos
    consequences: List[RBI581ConsequenceCreate] = Field(default_factory=list)
    dm_thinning: List[DMThinningCreate] = Field(default_factory=list)
    dm_external: List[DMExternalDamageCreate] = Field(default_factory=list)
    dm_external_cracking: List[DMExternalCrackingDamageCreate] = Field(default_factory=list)


class RBI581IntakeOut(ORMBase):
    asset: AssetOut
    component: RBIComponentOut
    analysis: RBI581AnalysisOut
    consequences: List[RBI581ConsequenceOut]
    dm_thinning: List[DMThinningOut]
    dm_external: List[DMExternalDamageOut]
    dm_external_cracking: List[DMExternalCrackingDamageOut]

# =========================================================
# Result thinning
# =========================================================
class ThinningComputeResponse(BaseModel):
    result_pk: int
    df_thin: float
    dfb_thin: Optional[float] = None
    status: str
    message: Optional[str] = None

# =========================================================
# Result COF
# =========================================================

class COFComputeResponse(BaseModel):
    cof_result_pk: int
    final_cof_area_ft2: Optional[float]
    financial_total_cost: Optional[float]
    safety_personnel_affected: Optional[float]
    status: str
    message: Optional[str]


# =========================================================
# Result External
# =========================================================

class ExternalComputeResponse(BaseModel):
    external_result_pk: int
    df_external: float
    status: str
    message: Optional[str] = None
    computed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# =========================================================
# Result External Cracking 
# =========================================================

class ExternalCrackingComputeResponse(BaseModel):
    externalcracking_result_pk: int
    df_externalcracking: float
    status: str = "ok"
    message: Optional[str] = None
    computed_at: Optional[datetime] = None
    trace_json: Optional[dict] = None 
    model_config = ConfigDict(from_attributes=True)