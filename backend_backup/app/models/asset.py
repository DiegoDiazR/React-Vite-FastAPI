# models/rbi_581.py
from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# =========================================================
# ASSETS
# =========================================================
class Asset(Base):
    __tablename__ = "assets"

    asset_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Business identifiers (lo que el usuario sí conoce)
    asset_id: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_id_cmms_sys: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    asset_id_equip_tech_num: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("asset_id", name="uq_assets_asset_id"),
        # Si tu "único real" es (cmms_sys, equip_tech_num), cambia a:
        # UniqueConstraint("asset_id_cmms_sys", "asset_id_equip_tech_num", name="uq_assets_cmms_technum"),
    )

    components: Mapped[List["RBIComponent"]] = relationship(
        "RBIComponent",
        back_populates="asset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# =========================================================
# COMPONENTS
# =========================================================
class RBIComponent(Base):
    __tablename__ = "rbi_components"

    component_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    asset_pk: Mapped[int] = mapped_column(
        ForeignKey("assets.asset_pk", ondelete="CASCADE"),
        nullable=False,
    )

    # Business keys del componente
    rbi_comp_comp: Mapped[str] = mapped_column(String(255), nullable=False)          # Component
    rbi_comp_comp_type: Mapped[str] = mapped_column(String(255), nullable=False)     # Component Type

    # Datos (según tu sheet)
    rbi_comp_comp_fam: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_comp_desc: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_comp_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    rbi_comp_circuit_from: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    rbi_comp_circuit_to: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    rbi_comp_comp_comm: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    rbi_comp_oper_press: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_oper_temp: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    # NUEVO: Presión atmosférica
    rbi_comp_atm_press: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_found_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_init_flu_phase: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    rbi_comp_process_flu: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rbi_comp_toxic_mixture: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    rbi_comp_toxic_fluid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_percent_toxic: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_inven: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_inven_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rbi_comp_design_press: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_design_temp: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_diam: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_length: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_fill_height: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_nom_thk: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    
    rbi_comp_smys: Mapped[Optional[str]] = mapped_column(Numeric, nullable=True)
    rbi_comp_uts: Mapped[Optional[str]] = mapped_column(Numeric, nullable=True)

    rbi_comp_stress_table: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_bm_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    rbi_comp_bm_year: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_bm_spec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_bm_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rbi_comp_weldj_eff: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_insul: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    rbi_comp_insul_type: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    rbi_comp_injec_point: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_pipe_circ_length: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_pwht: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    rbi_comp_inter_corr_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_predic_int_corr_loc: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    rbi_comp_est_int_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_est_ext_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_measu_ext_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_source_cal_corr_rate: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rbi_comp_perc_liquid_vol: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_detect_sys: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    rbi_comp_isolate_sys: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_mitigat_sys: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    rbi_comp_fluid_velocity: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_ph_water: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_geom_type: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    rbi_comp_gff_comp_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rbi_comp_cladding: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_furn_cladd_thk: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_min_struct_thk: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_liner: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_liner_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rbi_comp_release_prev_barrier: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    rbi_comp_cm_corrosion_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_comp_corrosion_allow: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_intrusive: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_min_thk: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_comp_base_mat: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_cladding_mat: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_comp_total_acid_num: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # ---> NUEVOS CAMPOS A AGREGAR AQUÍ <---
    # Fecha de instalación y condición del revestimiento (Liner)
    rbi_comp_install_liner_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    __table_args__ = (
        UniqueConstraint(
            "asset_pk",
            "rbi_comp_comp",
            "rbi_comp_comp_type",
            name="uq_rbi_components_asset_comp_comptype",
        ),
    )

    asset: Mapped["Asset"] = relationship("Asset", back_populates="components")

    analyses: Mapped[List["RBI581Analysis"]] = relationship(
        "RBI581Analysis",
        back_populates="component",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# =========================================================
# RBI 581 ANALYSIS (muchos por componente)
# =========================================================
class RBI581Analysis(Base):
    __tablename__ = "rbi_581_analysis"

    analysis_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    component_pk: Mapped[int] = mapped_column(
        ForeignKey("rbi_components.component_pk", ondelete="CASCADE"),
        nullable=False,
    )

    # Identificadores de análisis (no dependen del usuario en PK)
    # Puedes mantener unique_id si quieres (generado por backend), pero NO es PK.
    rbi_581_analysis_unique_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    rbi_581_scenario_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # para permitir múltiples corridas del mismo scenario
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    analysis_rev: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Campos del sheet
    rbi_581_coeff_y_mat: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rbi_581_stress_override: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_581_allowable_stress: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_581_flow_stress: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_581_ove_min_req_thk: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_581_course_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # rbi_581_analysis_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "component_pk",
            "rbi_581_scenario_id",
            "analysis_date",
            "analysis_rev",
            name="uq_rbi581_analysis_component_scenario_date_rev",
        ),
        # Si decides usar unique_id sí o sí:
        # UniqueConstraint("rbi_581_analysis_unique_id", name="uq_rbi581_analysis_unique_id"),
    )

    component: Mapped["RBIComponent"] = relationship("RBIComponent", back_populates="analyses")

    consequences: Mapped[List["RBI581Consequence"]] = relationship(
        "RBI581Consequence",
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    dm_thinning_rows: Mapped[List["DMThinning"]] = relationship(
        "DMThinning",
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    dm_external_rows: Mapped[list["DMExternalDamage"]] = relationship(
        "DMExternalDamage", 
        back_populates="analysis", 
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    dm_externalcracking_rows: Mapped[list["DMExternalCrackingDamage"]] = relationship(
        "DMExternalCrackingDamage", back_populates="analysis", cascade="all, delete-orphan"
    )


# =========================================================
# CONSEQUENCE (muchos por análisis)
# =========================================================
class RBI581Consequence(Base):
    __tablename__ = "rbi_581_consequence"

    consequence_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    analysis_pk: Mapped[int] = mapped_column(
        ForeignKey("rbi_581_analysis.analysis_pk", ondelete="CASCADE"),
        nullable=False,
    )

    # Para múltiples consecuencias por análisis
    conseq_type: Mapped[str] = mapped_column(String(50), nullable=False)   # ej: "financial", "env", "area", etc.
    conseq_rev: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Campos del sheet
    rbi_conseq_use_calc_invent: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    rbi_conseq_invent_group_mass: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_inc_personal_injury: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    rbi_conseq_injury_cost: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_equip_cost: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_production_cost: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_env_clean_up_cost: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_conseq_total_financial: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    rbi_conseq_user_total_financial: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_conseq_mfh_ast: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_fluid_perc_leav_dike: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_fluid_perc_onsite: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_fluid_perc_offsite: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    rbi_conseq_env_sensitivity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rbi_conseq_tank_course_height: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_dist_bottom_gwater: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_soil_type_under_tank: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    rbi_conseq_detection_rating: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_conseq_isolation_rating: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rbi_conseq_mitigation_system_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rbi_conseq_unit_area_ft2: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_personnel_count: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    rbi_conseq_personnel_presence_pct: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "analysis_pk",
            "conseq_type",
            "conseq_rev",
            name="uq_rbi581_consequence_analysis_type_rev",
        ),
    )

    analysis: Mapped["RBI581Analysis"] = relationship("RBI581Analysis", back_populates="consequences")


# =========================================================
# DM THINNING (muchos por análisis)
# =========================================================
class DMThinning(Base):
    __tablename__ = "dm_thinning"

    dm_thinning_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    analysis_pk: Mapped[int] = mapped_column(
        ForeignKey("rbi_581_analysis.analysis_pk", ondelete="CASCADE"),
        nullable=False,
    )

    # Identificador del registro dentro del análisis
    dm_thinning_dm: Mapped[str] = mapped_column(String(255), nullable=False)  # Damage Mechanism (business)
    dm_thinning_thinning_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Si un mismo DM se repite por ubicación/circuito/zona, usa esto:
    location_key: Mapped[str] = mapped_column(String(100), nullable=False, default="GLOBAL")

    # Campos del sheet (principales + los que pasaste)
    dm_thinning_gov_thin_dm: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_last_know_insp_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dm_thinning_last_know_thk: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # dm_thinning_base_mat_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    # dm_thinning_long_term_avg_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    # dm_thinning_short_term_avg_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    # dm_thinning_cladd_mat_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # TASAS DE CORROSIÓN - MATERIAL BASE
    dm_thinning_base_mat_estimated_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_base_mat_measured_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_base_mat_short_term_avg_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_base_mat_long_term_avg_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # TASAS DE CORROSIÓN - CLADDING
    dm_thinning_cladding_estimated_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_cladding_measured_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_cladding_short_term_avg_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_cladding_long_term_avg_corr_rate: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_number_a_level_insp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_thinning_number_b_level_insp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_thinning_number_c_level_insp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_thinning_number_d_level_insp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    dm_thinning_highest_effect_insp_level: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_num_highest_effect_insp_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    dm_thinning_injection_point_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_injection_point_inspect: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_deadleg_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_deadleg_inspect: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_welded_const_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_api653_mtto_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    dm_thinning_foundation_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_sett_adjus_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_sett_adjus_inspect: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_online_moni_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_key_process_variable: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    dm_thinning_electrical_resist_probes: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_corrosion_coupons: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    dm_thinning_cl_concentration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_air_oxidant_present: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_soil_resistivity: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_h2s_content: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_hydrocarbon_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_sulphur_concent: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_cooling_sys_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_water_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_water_treatm_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_recirc_sys_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_calcium_hardness: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_total_dissolved_solids: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_mo_alkalinity: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_oxygen_process_stream: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_acid_concentration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_soil_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_cathodic_protect_effect: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_coating: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_coating_age: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_max_coating_temp_rating_exc: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_coating_mtto_rare_none: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_coating_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    dm_thinning_amine_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_heat_stable_amine_salts: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_acid_gas_loading: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_amine_concentration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_hf_concentration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_h2s_partial_pressure: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_nh4hs_concentration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # ---> NUEVOS CAMPOS A AGREGAR AQUÍ <---
    
    # Confianza Bayesiana de Inspección
    dm_thinning_confidence: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Factores de revestimiento y suelo
    dm_thinning_online_moni_linning_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_resistivity_consider_base: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_coating_sup_age: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Sour Water y Cloruros 
    # (Nota: En Pydantic los pusiste como float, pero lógicamente son Booleanos)
    dm_thinning_water_present: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_cl_present: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Variables de Corrosión por CO2
    dm_thinning_present_hydrocarbon: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_thinning_water_content_pct: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_water_weight_pct: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_co2_concentration: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_ph_condition: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_thinning_mix_density: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_dynamic_viscocity: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_rugosidad_interna: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_glycol_pct: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_thinning_inhibitor_efficiency: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    dm_thinning_liner_condition:Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "analysis_pk",
            "dm_thinning_dm",
            "dm_thinning_thinning_type",
            "location_key",
            name="uq_dm_thinning_analysis_dm_type_loc",
        ),
    )

    analysis: Mapped["RBI581Analysis"] = relationship("RBI581Analysis", back_populates="dm_thinning_rows")


# =========================================================
# DM EXTERNAL (muchos por análisis)
# =========================================================
class DMExternalDamage(Base):
    __tablename__ = "dm_ExternalDamage"

    dm_extdamage_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    analysis_pk: Mapped[int] = mapped_column(
        ForeignKey("rbi_581_analysis.analysis_pk", ondelete="CASCADE"),
        nullable=False,
    )

    # Identificador del registro dentro del análisis
    dm_ext_dm:                       Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dm_ext_select_ext_cr:            Mapped[str] = mapped_column(String(255), nullable=True)
    dm_ext_base_mat_measured_rate:   Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_ext_thinning_type:            Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_ext_coating_quality:          Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_ext_coating_install_date:     Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dm_ext_last_know_insp_date:      Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dm_ext_last_know_thk:            Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_ext_anticipated_coating_life: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_ext_coating_failed_at_insp:   Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_ext_atmosperic_condition:     Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_ext_piping_complex:           Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_ext_insulation_condition:     Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_ext_cr_adj_design:            Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_ext_sa_interface:             Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_ext_confidence:               Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dm_ext_number_a_level_insp:      Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_ext_number_b_level_insp:      Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_ext_number_c_level_insp:      Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_ext_number_d_level_insp:      Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "analysis_pk",
            "dm_ext_dm",
            "dm_ext_thinning_type",
            name="uq_dm_thinning_analysis_dm_type_loc",
        ),
    )

    analysis: Mapped["RBI581Analysis"] = relationship("RBI581Analysis", back_populates="dm_external_rows")



# =========================================================
# DM EXTERNAL CRACKING (muchos por análisis)
# =========================================================
class DMExternalCrackingDamage(Base):
    __tablename__ = "dm_ExternalCrackingDamage"

    dm_extcracking_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    analysis_pk: Mapped[int] = mapped_column(
        ForeignKey("rbi_581_analysis.analysis_pk", ondelete="CASCADE"),
        nullable=False,
    )

    # Identificador del registro dentro del análisis
    dm_extcracking_dm:                    Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dm_extcrack_num_high_effec_insp:      Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dm_extcrack_high_effec_insp:          Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_last_know_insp_date:      Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dm_extcrack_susceptibility_type:      Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_atm_condition:            Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_susceptibility:           Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_coating_present:          Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_extcrack_coating_install_date:     Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dm_extcrack_coating_quality:          Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_anticipated_coating_life: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    dm_extcrack_coating_failed_at_insp:   Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dm_extcrack_piping_complex:           Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_insulation_condition:     Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dm_extcrack_cl_free:                  Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "analysis_pk",
            "dm_extcracking_dm",
            name="uq_dm_externalcracking_analysis_dm_type_loc",
        ),
    )

    analysis: Mapped["RBI581Analysis"] = relationship("RBI581Analysis", back_populates="dm_externalcracking_rows")