# app/calculations/cof_orchestrator.py
"""
API 581 COF Level 1
COF Orchestrator (4.2 → 4.13)

Este módulo coordina el cálculo completo de COF:
- 4.2 Release hole size + GFFs
- 4.3 Theoretical release rate W_n (por hueco)
- 4.4 Fluid inventory available for release (mass_avail,n)
- 4.5 Release type (continuous vs instantaneous)
- 4.6 Detection & isolation impact (fact_di y ld_max,n)
- 4.7 Adjusted release rate + release mass for COF (rate_n, mass_n, ld_n)
- 4.8 Flammable/explosive consequence (CA_flame, cmd & inj)
- 4.9 Toxic consequence (CA_tox, inj)
- 4.10 Nonflammable/nontoxic consequence (CA_nfnt, inj)
- 4.11 Final consequence areas (CA_f,cmd ; CA_f,inj ; CA_f)
- 4.12 Financial consequence (C_f^fin)
- 4.13 Safety consequence (C_f^inj)

Salida:
- Resultado final agregado
- Opcional: todos los intermedios (para trazabilidad)

Nota: Este orquestador asume que ya existen los módulos 4.x en app/calculations/
y que exponen funciones compute_* coherentes.
"""



from dataclasses import dataclass, field
import math
from typing import Dict, Any, Optional

# --- IMPORTACIONES DE MÓDULOS ---
from app.calculations.cof_4_1_representative_fluid import (
    step_4_1_determine_representative_fluid, 
    Step41Result
)
from app.calculations.cof_4_2_release_hole_size import (
    compute_cof_4_2_release_hole_size,
    ReleaseHoleSizeResult
)
from app.calculations.cof_4_3_release_rate import (
    compute_release_rates_for_holes,
    ReleaseRateResult,
    GasInputs,
    LiquidInputs,
    Phase
)

from app.calculations.cof_4_4_fluid_inventory import (
    compute_cof_4_4_fluid_inventory,
    InventoryInputs
)

from app.calculations.cof_4_5_release_type import (
    compute_cof_4_5_release_types,
    ReleaseTypePerHole
)

from app.calculations.cof_4_6_detec_isola_impact import (
    compute_cof_4_6_detection_isolation_impact,
    Rating,
    DetIsoImpactResult
)

from app.calculations.cof_4_7_release_rate_mass import (
    compute_cof_4_7_for_holes,
    ReleaseRateMassInputs,
    ReleaseRateMassResult,
    Step47Result, 
    Step47HoleResult  # <-- Ahora sí existe en el archivo y funcionará
    
)

# from app.calculations.cof_4_8_flammable_explosive import (
#     compute_cof_4_8_flammable_explosive,
#     HoleInput,
#     AITInputs,
#     ReleaseType as FlamReleaseType,
#     Phase as FlamPhase,
#     FlammableFinalResult
# )

from app.calculations.cof_4_8_flammable_explosive import (
    compute_cof_4_8_flammable_explosive,
    is_fluid_flammable,
    HoleInput,
    AITInputs,
    ReleaseType as FlamReleaseType,
    Phase as FlamPhase,
    FlammableFinalResult
)

from app.calculations.cof_4_9_toxic_consequence import (
    compute_step_4_9_total,
    ReleaseType as ToxReleaseType
)

from app.calculations.cof_4_10_nonflammable_nontoxic import (
        compute_nonflammable_nontoxic_for_hole,
        probability_weighted_nonflammable_area,
        NonFlamCategory,
        NonFlamHoleInputs,
        ReleaseType as NFNTReleaseType, # Alias para evitar conflicto
        TABLE_4_9_ACID_CAUSTIC
    )


from app.calculations.cof_4_11_damage_injury_areas import (
    compute_cof_4_11_damage_injury_areas,
    ConsequenceAreasByMechanism,
    FinalConsequenceAreas
)

from app.calculations.cof_4_12_financial_consequence import (
    compute_cof_4_12_financial_consequence,
    FinancialInputs,
    FinancialResult,
    HoleSize as FinHoleSize, # Alias para no confundir con ReleaseHoleSize
    TABLE_4_18_FLUID_PROPS
)


from app.calculations.cof_4_13_safety_consequence import (
    compute_cof_4_13_safety_consequence,
    SafetyConsequenceInputs,
    SafetyConsequenceResult,
    StaffingCase
)


# -------------------------------------------------------------------------
# 1. INPUTS GLOBALES (Ajustado para Presión Manométrica)
# -------------------------------------------------------------------------
@dataclass
class COFScenarioInputs:
    """
    Contenedor maestro de datos de entrada.
    """
    # --- Datos 4.1 (Fluido) ---
    fluid_name: str
    stored_phase: str
    temperature_k: float     # Temp operativa (K)
    
    # --- Datos 4.2 (Componente) ---
    component_type: str
    component_family: str    # "Piping" o "Vessel" / "Other"
    diameter_in: float       # Diámetro (interno para piping, cuerpo para vessels)
    length_ft: float         # Longitud del componente individual
    length_circuit_ft: float # Longitud total del circuito (Solo para Piping)
    
    # --- Datos 4.3 (Proceso) ---
    # CAMBIO: Inputs explícitos según tu requerimiento
    pressure_gauge_psi: float  # Presión Manométrica (leída en el instrumento)
    patm_psi: float = 14.7     # Presión Atmosférica (local)

    # --- Datos 4.6 (Sistemas de Mitigación) ---
    detection_rating: Rating = Rating.C  # Valor por defecto conservador
    isolation_rating: Rating = Rating.B

    # --- Datos 4.8 (Consecuencia Inflamable) ---
    mitigation_system_key: str = "none" # Basado en Tabla 4.10

    # --- Datos 4.9 (Consecuencia Tóxica) ---
    toxic_mfrac: float = 0.0  # Fracción de masa tóxica (0.0 a 1.0)

    # --- DATOS FINANCIEROS (NUEVO PARA 4.12) ---
    # Valores por defecto para evitar romper tests anteriores, 
    # pero en producción deberían venir del usuario.
    material_cost_factor: float = 1.0  # costfactor
    material: str = "CARBON STEEL"     # Para Table 4.16
    equipment_cost_ft2: float = 0.0    # equipcost ($/ft2)
    production_cost_day: float = 0.0   # prodcost ($/day)
    injury_cost_person: float = 0.0    # injcost ($/person)
    environmental_cost_bbl: float = 0.0 # envcost ($/bbl)
    outage_multiplier: float = 1.0     # outage_mult
    
    # --- DATOS POBLACIONALES / SEGURIDAD (4.12 y 4.13) ---
    # population_density: Usado directamente en 4.12 si se tiene el dato fijo.
    # Si se va a calcular en 4.13, este valor debería ser consistente con (personal/area).
    # population_density: float = 0.0 
    
    # Nuevos para 4.13:
    unit_area_ft2: float = 10000.0   # Área de la unidad para calcular densidad
    personnel_count: float = 0.0     # Número de personas promedio
    personnel_presence_pct: float = 100.0 # Porcentaje de tiempo presentes

    @property
    def effective_population_density(self) -> float:
        """
        Calcula la densidad de población automáticamente basada en:
        (Personal * %Presencia) / Área de la Unidad.
        """
        if self.unit_area_ft2 <= 0:
            return 0.0
            
        # Eq 3.93: Promedio de personal = Count * (Pct / 100)
        pers_avg = self.personnel_count * (self.personnel_presence_pct / 100.0)
        
        # Eq 3.94: Densidad = Pers_avg / Area
        return pers_avg / self.unit_area_ft2


# -------------------------------------------------------------------------
# 2. RESULTADO ESTRUCTURADO PARA PASO 4.3
# -------------------------------------------------------------------------
@dataclass
class Step43Result:
    """Contenedor de resultados del Paso 4.3 para todos los agujeros."""
    release_phase: str
    system_pressure_psia: float # Guardamos la P_abs calculada para referencia
    results_by_hole: Dict[Any, ReleaseRateResult]

# -------------------------------------------------------------------------
# 2. RESULTADO ESTRUCTURADO PARA PASO 4.5
# -------------------------------------------------------------------------
@dataclass
class Step45Result:
    """Resultado del Paso 4.5: Tipos de liberación por agujero."""
    results_by_hole: Dict[Any, ReleaseTypePerHole]

# -------------------------------------------------------------------------
# 2. RESULTADO ESTRUCTURADO PARA PASO 4.7
# -------------------------------------------------------------------------
@dataclass
class Step47Result:
    """Resultado final de flujo y masa ajustados por agujero."""
    results_by_hole: Dict[Any, ReleaseRateMassResult]

# -------------------------------------------------------------------------
# 3. CLASE ORQUESTADORA
# -------------------------------------------------------------------------
class COFCalculator:
    def __init__(self, inputs: COFScenarioInputs):
        self.inputs = inputs
        
        # Estado acumulado
        self.step_4_1_result: Optional[Step41Result] = None
        self.step_4_2_result: Optional[ReleaseHoleSizeResult] = None
        self.step_4_3_result: Optional[Step43Result] = None
        self.logs: list[str] = []
        self.step_4_5_result: Optional[Step45Result] = None
        self.step_4_6_result: Optional[DetIsoImpactResult] = None
        self.step_4_7_result: Optional[Step47Result] = None
        self.step_4_8_result: Optional[FlammableFinalResult] = None
        self.step_4_9_result: Optional[Dict] = None
        # self.step_4_10_result: Optional[FinalConsequenceAreas] = None
        self.step_4_11_result: Optional[FinalConsequenceAreas] = None
        self.step_4_12_result: Optional[FinancialResult] = None
        self.step_4_13_result: Optional[SafetyConsequenceResult] = None


    def execute_step_4_1(self):
        """Paso 4.1: Fluido y Propiedades."""
        self.logs.append(f"Iniciando Paso 4.1: {self.inputs.fluid_name}")
        try:
            res = step_4_1_determine_representative_fluid(
                representative_fluid=self.inputs.fluid_name,
                stored_phase=self.inputs.stored_phase,
                temperature_k=self.inputs.temperature_k
            )
            self.step_4_1_result = res
            return res
        except Exception as e:
            self.logs.append(f"Error 4.1: {e}")
            raise e

    def execute_step_4_2(self):
        """Paso 4.2: Agujeros y GFF."""
        self.logs.append(f"Iniciando Paso 4.2: {self.inputs.component_type}")
        try:
            res = compute_cof_4_2_release_hole_size(
                component_type=self.inputs.component_type,
                D_in=self.inputs.diameter_in
            )
            self.step_4_2_result = res
            return res
        except Exception as e:
            self.logs.append(f"Error 4.2: {e}")
            raise e

    def execute_step_4_3(self):
        """
        Paso 4.3: Cálculo de Tasas de Descarga (Wn).
        REALIZA EL CÁLCULO: P_abs = P_gauge + P_atm
        """
        self.logs.append("Iniciando Paso 4.3: Tasas de Liberación")
        
        if not self.step_4_1_result or not self.step_4_2_result:
            raise RuntimeError("Pasos 4.1 y 4.2 deben ejecutarse antes del 4.3")

        # 1. CÁLCULO DE PRESIÓN ABSOLUTA (Regla de Negocio)
        # Ps (abs) = Ps (gauge) + Patm
        p_abs_psia = self.inputs.pressure_gauge_psi + self.inputs.patm_psi
        self.logs.append(f"Presión Absoluta Calculada: {p_abs_psia:.2f} psia (Gauge={self.inputs.pressure_gauge_psi} + Atm={self.inputs.patm_psi})")

        # 2. Preparar Datos del Fluido
        res_4_1 = self.step_4_1_result
        phase_str = res_4_1.final_release_phase
        
        # Convertir Temp K -> Rankine
        temp_r = self.inputs.temperature_k * 1.8
        
        # 3. Configurar Inputs Específicos
        gas_in = None
        liq_in = None
        target_phase = Phase.GAS if phase_str == "Gas" else Phase.LIQUID

        if target_phase == Phase.GAS:
            mw = res_4_1.properties['mw']
            k = res_4_1.trace.get('gamma_calc', 1.4)
            
            gas_in = GasInputs(
                ps_psi=p_abs_psia,  # <--- Pasamos la absoluta calculada
                ts_rankine=temp_r,
                mw=float(mw),
                k=float(k),
                patm_psi=self.inputs.patm_psi
            )
        else:
            rho = res_4_1.properties['rho']
            liq_in = LiquidInputs(
                ps_psi=p_abs_psia,  # <--- Pasamos la absoluta calculada
                # ts_rankine=temp_r,
                rho_lbft3=float(rho),
                patm_psi=self.inputs.patm_psi
            )

   
        # 4. Obtener Diámetros de Agujeros
        dn_map = self.step_4_2_result.dn_in

        try:
            wn_results = compute_release_rates_for_holes(
                phase=target_phase,
                hole_diameters_in=dn_map,
                gas=gas_in,
                liquid=liq_in
            )
            
            self.step_4_3_result = Step43Result(
                release_phase=phase_str,
                system_pressure_psia=p_abs_psia,
                results_by_hole=wn_results
            )
            
            self.logs.append(f"Paso 4.3 completado. Wn calculado para {len(wn_results)} orificios.")
            return self.step_4_3_result

        except Exception as e:
            self.logs.append(f"Error 4.3: {e}")
            raise e

               

    def execute_step_4_4(self):
        """
        Paso 4.4: Estimar el Inventario de Fluido Disponible para la Liberación.
        Implementa Eqs. (3.9), (3.10) y (3.11).
        """
        self.logs.append("Iniciando Paso 4.4: Cálculo de Inventario por Familia")
        
        if not self.step_4_1_result or not self.step_4_3_result:
            raise RuntimeError("Debe ejecutar los Pasos 4.1 y 4.3 antes del 4.4")

        # 1. Recuperar densidad del fluido (lb/ft3)
        rho = float(self.step_4_1_result.properties['rho'])
        
        # 2. Calcular Área Transversal (ft2)
        # Area = (pi * (D/12)^2) / 4
        area_ft2 = (math.pi * (self.inputs.diameter_in / 12.0)**2) / 4.0
        
        # 3. Determinar Masa del Componente (mass_comp)
        mass_comp = area_ft2 * self.inputs.length_ft * rho
        
        # 4. Determinar Masa Total del Inventario (mass_inv) - Eq. (3.9)
        family = self.inputs.component_family.strip().capitalize()
        
        if family == "Piping":
            self.logs.append("Familia detectada: Piping. Usando longitud de circuito.")
            # Para Piping, el inventario disponible es el circuito completo
            mass_inv = area_ft2 * self.inputs.length_circuit_ft * rho
        else:
            self.logs.append(f"Familia detectada: {family}. Ignorando longitud de circuito.")
            # Para otras familias, el inventario inicial se limita al componente
            mass_inv = mass_comp

        self.logs.append(f"Masas: Componente={mass_comp:.2f} lb, Inventario Total={mass_inv:.2f} lb")

        # 5. Preparar Tasas para Masa Adicional - Eq. (3.10)
        wn_map = {sz: r.mdot_lbm_s for sz, r in self.step_4_3_result.results_by_hole.items()}
        # Wmax8: Tasa de liberación para un agujero de 8"
        wmax8 = max(wn_map.values()) 

        # 6. Ejecución de la lógica de inventario (Eqs 3.10 y 3.11)
        inv_inputs = InventoryInputs(
            mass_comp_lbm=mass_comp,
            other_component_masses_lbm={"Connected_Inventory": mass_inv - mass_comp}
        )

        try:
            res = compute_cof_4_4_fluid_inventory(
                inventory=inv_inputs,
                wn_by_hole_lbm_s=wn_map,
                wmax8_lbm_s=wmax8
            )
            self.step_4_4_result = res
            return res
        except Exception as e:
            self.logs.append(f"Error en inventario: {e}")
            raise e
        
    def execute_step_4_5(self):
        """
        Paso 4.5: Determinar el Tipo de Liberación (Continua vs Instantánea).
        Reglas:
        - Small (<0.25in) -> Continuous.
        - Otros: Instantánea si Masa_3min > 10,000 lb o Wn > 55.6 lb/s.
        """
        self.logs.append("Iniciando Paso 4.5: Determinación de Tipo de Liberación")
        
        # Validar que tengamos los pasos previos
        if not all([self.step_4_2_result, self.step_4_3_result, self.step_4_4_result]):
            raise RuntimeError("Debe ejecutar Pasos 4.2, 4.3 y 4.4 antes del 4.5")

        # 1. Preparar diccionarios alineados por tamaño de agujero
        # Usamos los Enums/Keys del Paso 4.2 como base
        dn_map = self.step_4_2_result.dn_in
        wn_map = {sz: r.mdot_lbm_s for sz, r in self.step_4_3_result.results_by_hole.items()}
        mass_avail_map = {sz: r.mass_avail_lbm for sz, r in self.step_4_4_result.per_hole.items()}

        try:
            # 2. Ejecutar lógica batch de 4.5
            res_map = compute_cof_4_5_release_types(
                dn_by_hole=dn_map,
                wn_by_hole_lbm_s=wn_map,
                mass_avail_by_hole_lbm=mass_avail_map
            )
            
            self.step_4_5_result = Step45Result(results_by_hole=res_map)
            self.logs.append("Paso 4.5 completado.")
            return self.step_4_5_result

        except Exception as e:
            self.logs.append(f"Error en Paso 4.5: {e}")
            raise e

    
        


    def execute_step_4_6(self):
        """
        Paso 4.6: Impacto de Sistemas de Detección y Aislamiento.
        Determina fact_di (reducción de magnitud) y ld_max (duración máxima).
        """
        self.logs.append(f"Iniciando Paso 4.6: Mitigación {self.inputs.detection_rating}/{self.inputs.isolation_rating}")
        
        try:
            # Ejecutamos la lógica de tablas 4.5, 4.6 y 4.7
            res = compute_cof_4_6_detection_isolation_impact(
                detection=self.inputs.detection_rating,
                isolation=self.inputs.isolation_rating
            )
            
            self.step_4_6_result = res
            self.logs.append(f"Paso 4.6 completado. Factor de reducción fact_di: {res.fact_di}")
            return res
            
        except Exception as e:
            self.logs.append(f"Error en Paso 4.6: {e}")
            raise e
        
    def execute_step_4_7(self):
        """
        Paso 4.7: Determinar Tasa de Liberación y Masa Finales.
        Aplica Eqs. (3.12), (3.13) y (3.14).
        """
        self.logs.append("Iniciando Paso 4.7: Cálculo de Flujo y Masa Finales")
        
        # Validar pre-requisitos
        if not all([self.step_4_3_result, self.step_4_4_result, self.step_4_6_result]):
            raise RuntimeError("Debe ejecutar Pasos 4.3, 4.4 y 4.6 antes del 4.7")

        # 1. Preparar mapa de inputs para el cálculo batch de 4.7
        inputs_by_hole = {}
        fact_di = self.step_4_6_result.fact_di
        
        for size in self.step_4_2_result.dn_in.keys():
            # Obtener Wn del Paso 4.3
            wn_lbm_s = self.step_4_3_result.results_by_hole[size].mdot_lbm_s
            
            # Obtener mass_avail del Paso 4.4
            mass_avail_lbm = self.step_4_4_result.per_hole[size].mass_avail_lbm
            
            # Obtener ld_max del Paso 4.6 (basado en el Rating y tamaño)
            # Nota: El orquestador debe mapear el enum HoleSize a los keys de ld_max
            hole_key = size.value if hasattr(size, 'value') else str(size)
            ld_max_min = self.step_4_6_result.ld_max_minutes[hole_key]

            inputs_by_hole[hole_key] = ReleaseRateMassInputs(
                Wn_lbm_s=wn_lbm_s,
                mass_avail_lbm=mass_avail_lbm,
                fact_di=fact_di,
                ldmax_min=ld_max_min
            )

        try:
            # 2. Ejecutar lógica batch
            res_map = compute_cof_4_4_for_holes_wrapper = compute_cof_4_7_for_holes(inputs_by_hole)
            
            self.step_4_7_result = Step47Result(results_by_hole=res_map)
            self.logs.append("Paso 4.7 completado exitosamente.")
            return self.step_4_7_result
            
        except Exception as e:
            self.logs.append(f"Error en Paso 4.7: {e}")
            raise e

          
    
    # def execute_step_4_8(self):
    #     """
    #     Paso 4.8: Consecuencia Inflamable.
    #     NORMALIZACIÓN QUIRÚRGICA: Extrae solo el valor del Enum (ej. 'small') 
    #     ignorando el nombre de la clase (ej. 'ReleaseHoleSize').
    #     """
    #     self.logs.append("Iniciando Paso 4.8: Áreas de Consecuencia Inflamable")
        
    #     if not all([self.step_4_7_result, self.step_4_5_result, self.step_4_2_result]):
    #         raise RuntimeError("Faltan pasos previos para ejecutar el 4.8")

    #     # --- FUNCIÓN DE NORMALIZACIÓN MEJORADA ---
    #     def get_clean_key(k):
    #         # Si es un Enum, k.value nos da 'small'
    #         # Si ya es un string como 'ReleaseHoleSize.small', tomamos lo después del punto
    #         s = k.value if hasattr(k, 'value') else str(k)
    #         return s.split('.')[-1].lower().strip()

    #     # Normalizamos todos los mapas
    #     rel_type_map = {get_clean_key(k): v for k, v in self.step_4_5_result.results_by_hole.items()}
    #     phys_map = {get_clean_key(k): v for k, v in self.step_4_7_result.results_by_hole.items()}
    #     gff_map = {get_clean_key(k): v for k, v in self.step_4_2_result.gff.items()}

    #     flam_holes = {}
    #     for s_key in ["small", "medium", "large", "rupture"]:
    #         if s_key not in phys_map:
    #             continue
            
    #         if s_key not in rel_type_map:
    #             self.logs.append(f"[ERROR] No match para '{s_key}'. Disponibles: {list(rel_type_map.keys())}")
    #             continue

    #         phys = phys_map[s_key]
    #         rel_data = rel_type_map[s_key]
            
    #         # Fase: Forzamos GAS para C3-C4 (Requerimiento API 581 para estas constantes)
    #         phase_str = self.step_4_1_result.final_release_phase.lower()
    #         flam_phase = FlamPhase.GAS if ("gas" in phase_str or "c3" in self.inputs.fluid_name.lower()) else FlamPhase.LIQUID
            
    #         # Tipo de liberación
    #         rel_type_str = rel_data.release_type.value.lower()
    #         flam_rel_type = FlamReleaseType.CONTINUOUS if "continuous" in rel_type_str else FlamReleaseType.INSTANTANEOUS

    #         flam_holes[s_key] = HoleInput(
    #             hole_key=s_key,
    #             release_type=flam_rel_type,
    #             final_phase=flam_phase,
    #             rate_lb_s=phys.rate_lbm_s,
    #             mass_lb=phys.mass_lbm
    #         )

    #     # --- EJECUCIÓN DEL CÁLCULO ---
    #     temp_r = self.inputs.temperature_k * 1.8
    #     ait_in = AITInputs(Ts_R=temp_r, representative_fluid=self.inputs.fluid_name)

    #     try:
    #         res = compute_cof_4_8_flammable_explosive(
    #             fluid=self.inputs.fluid_name,
    #             holes=flam_holes,
    #             ait=ait_in,
    #             mitigation_system_key=self.inputs.mitigation_system_key,
    #             gff_by_hole=gff_map,
    #             gff_total=self.step_4_2_result.gff_total
    #         )
    #         self.step_4_8_result = res
    #         self.logs.append("Paso 4.8 completado con éxito.")
    #         return res
    #     except Exception as e:
    #         self.logs.append(f"Error en 4.8: {e}")
    #         raise e

    def execute_step_4_8(self):
        """
        Paso 4.8: Consecuencia Inflamable.
        """
        self.logs.append("Iniciando Paso 4.8: Consecuencia Inflamable")
        if not self.step_4_7_result: raise RuntimeError("Requiere Paso 4.7")

        # 1. GUARDIA DE APLICABILIDAD
        # Usa la nueva lógica: Si es Steam -> False. Si es C3-C4 -> True.
        if not is_fluid_flammable(self.inputs.fluid_name):
            self.logs.append(f"Fluido '{self.inputs.fluid_name}' no es inflamable (o no tiene constantes). Áreas = 0.0")
            self.step_4_8_result = FlammableFinalResult(
                fluid=self.inputs.fluid_name, fluid_type=0, holes={}, CA_cmd_final=0.0, CA_inj_final=0.0
            )
            return self.step_4_8_result

        # 2. Preparación de Datos
        def get_clean_key(k):
             s = k.value if hasattr(k, 'value') else str(k)
             return s.split('.')[-1].lower().strip()

        rel_type_map = {get_clean_key(k): v for k, v in self.step_4_5_result.results_by_hole.items()}
        phys_map = {get_clean_key(k): v for k, v in self.step_4_7_result.results_by_hole.items()}
        gff_map = {get_clean_key(k): v for k, v in self.step_4_2_result.gff.items()}

        flam_holes = {}
        for s_key in ["small", "medium", "large", "rupture"]:
            if s_key not in phys_map: continue
            
            phys = phys_map[s_key]
            rel_data = rel_type_map.get(s_key)
            if not rel_data: continue

            phase_str = self.step_4_1_result.final_release_phase.lower()
            flam_phase = FlamPhase.GAS if ("gas" in phase_str or "c3" in self.inputs.fluid_name.lower()) else FlamPhase.LIQUID
            
            rel_type_str = rel_data.release_type.value.lower()
            flam_rel_type = FlamReleaseType.CONTINUOUS if "continuous" in rel_type_str else FlamReleaseType.INSTANTANEOUS

            flam_holes[s_key] = HoleInput(
                hole_key=s_key,
                release_type=flam_rel_type,
                final_phase=flam_phase,
                rate_lb_s=phys.rate_lbm_s,
                mass_lb=phys.mass_lbm
            )

        # 3. Ejecutar Cálculo
        temp_r = self.inputs.temperature_k * 1.8
        ait_in = AITInputs(Ts_R=temp_r, representative_fluid=self.inputs.fluid_name)

        try:
            res = compute_cof_4_8_flammable_explosive(
                fluid=self.inputs.fluid_name,  # <--- VERIFICAR QUE NO DIGA "Steam"
                holes=flam_holes,
                ait=ait_in,
                mitigation_system_key=self.inputs.mitigation_system_key,
                gff_by_hole=gff_map,
                gff_total=self.step_4_2_result.gff_total
            )
            self.step_4_8_result = res
            self.logs.append(f"Paso 4.8 OK. CMD={res.CA_cmd_final:.2f}, INJ={res.CA_inj_final:.2f}")
            return res
        except Exception as e:
            self.logs.append(f"Error 4.8: {e}")
            raise e
    


    # def execute_step_4_9(self):
    #     """
    #     Paso 4.9: Consecuencia Tóxica.
    #     NORMALIZACIÓN ROBUSTA: Asegura que las llaves coincidan entre pasos 4.5, 4.7 y 4.9.
    #     """
    #     self.logs.append(f"Iniciando Paso 4.9: Toxicidad para {self.inputs.fluid_name}")
        
    #     if not self.step_4_7_result:
    #         raise RuntimeError("Debe ejecutar el Paso 4.7 antes del 4.9")

    #     # --- FUNCIÓN DE LIMPIEZA DE LLAVES ---
    #     def get_clean_key(k):
    #         # Convierte 'ReleaseHoleSize.SMALL' o 'small' -> 'small'
    #         s = k.value if hasattr(k, 'value') else str(k)
    #         return s.split('.')[-1].lower().strip()

    #     # 1. Normalizar Mapas de Pasos Previos
    #     # Paso 4.7 (Datos Físicos: Wn, Mass)
    #     phys_map = {get_clean_key(k): v for k, v in self.step_4_7_result.results_by_hole.items()}
        
    #     # Paso 4.5 (Tipo de Liberación: Cont/Inst)
    #     rel_type_map = {get_clean_key(k): v for k, v in self.step_4_5_result.results_by_hole.items()}
        
    #     # Paso 4.2 (GFF)
    #     gff_map = {get_clean_key(k): v for k, v in self.step_4_2_result.gff.items()}

    #     # 2. Construir Payload para el Módulo Tóxico
    #     holes_payload = {}
    #     for size_key in ["small", "medium", "large", "rupture"]:
    #         if size_key not in phys_map:
    #             continue
            
    #         # Recuperar datos físicos
    #         res_4_7 = phys_map[size_key]
            
    #         # Recuperar tipo de liberación (con seguridad)
    #         if size_key not in rel_type_map:
    #             self.logs.append(f"[WARN] No se encontró tipo de liberación para '{size_key}' en Paso 4.9")
    #             continue
                
    #         rel_type_data = rel_type_map[size_key]
            
    #         # Mapeo de Enum (API 581 -> Tox Module)
    #         # Aseguramos que comparamos strings limpios
    #         rtype_str = rel_type_data.release_type.value.lower()
    #         tox_rel_type = ToxReleaseType.CONTINUOUS if "continuous" in rtype_str else ToxReleaseType.INSTANTANEOUS
            
    #         holes_payload[size_key] = {
    #             "Wn_lbm_s": res_4_7.rate_lbm_s,
    #             "mass_n_lbm": res_4_7.mass_lbm,
    #             "release_type": tox_rel_type
    #         }

    #     # 3. Obtener ld_max (usamos 'small' como referencia de sistema, o el que corresponda)
    #     # Nota: ld_max también viene de un diccionario, normalicémoslo por si acaso
    #     ld_max_map = {get_clean_key(k): v for k, v in self.step_4_6_result.ld_max_minutes.items()}
    #     ldmax_val = ld_max_map.get("small", 60.0) # Default conservador si falla

    #     try:
    #         # 4. Ejecutar Cálculo
    #         res = compute_step_4_9_total(
    #             chemical=self.inputs.fluid_name,
    #             mfrac_tox=self.inputs.toxic_mfrac,
    #             holes_data=holes_payload,
    #             gff_by_hole=gff_map,
    #             ldmax_n_min=ldmax_val
    #         )
            
    #         self.step_4_9_result = res
            
    #         if not res["applies"]:
    #             self.logs.append(f"Paso 4.9: {res.get('message', 'No aplica')}")
    #         else:
    #             self.logs.append(f"Paso 4.9 completado. CA_tox_inj: {res['CA_tox_inj_final']:.2f}")
            
    #         return res
            
    #     except Exception as e:
    #         self.logs.append(f"Error en Paso 4.9: {e}")
    #         raise e

    def execute_step_4_9(self):
        self.logs.append(f"Iniciando Paso 4.9: Toxicidad ({self.inputs.fluid_name})")
        if not self.step_4_7_result: raise RuntimeError("Requiere Paso 4.7")

        def get_clean_key(k):
             s = k.value if hasattr(k, 'value') else str(k)
             return s.split('.')[-1].lower().strip()

        phys_map = {get_clean_key(k): v for k, v in self.step_4_7_result.results_by_hole.items()}
        rel_type_map = {get_clean_key(k): v for k, v in self.step_4_5_result.results_by_hole.items()}
        gff_map = {get_clean_key(k): v for k, v in self.step_4_2_result.gff.items()}
        
        holes_payload = {}
        for s_key in ["small", "medium", "large", "rupture"]:
            if s_key not in phys_map: continue
            
            rel_data = rel_type_map.get(s_key)
            if not rel_data: continue
            
            rtype_str = rel_data.release_type.value.lower()
            tox_rel_type = ToxReleaseType.CONTINUOUS if "continuous" in rtype_str else ToxReleaseType.INSTANTANEOUS
            
            # --- DETERMINAR FASE (NUEVO) ---
            # Usamos lógica similar al 4.8: Si C3-C4 o fase es gas -> "gas", sino "liquid"
            phase_str_41 = self.step_4_1_result.final_release_phase.lower()
            if "gas" in phase_str_41 or "c3" in self.inputs.fluid_name.lower():
                hole_phase = "gas"
            else:
                hole_phase = "liquid"

            holes_payload[s_key] = {
                "Wn_lbm_s": phys_map[s_key].rate_lbm_s,
                "mass_n_lbm": phys_map[s_key].mass_lbm,
                "release_type": tox_rel_type,
                "phase": hole_phase # <--- AGREGADO: Enviamos la fase
            }

        ld_max_map = {get_clean_key(k): v for k, v in self.step_4_6_result.ld_max_minutes.items()}
        ldmax_val = ld_max_map.get("small", 60.0)

        try:
            res = compute_step_4_9_total(
                chemical=self.inputs.fluid_name,
                mfrac_tox=self.inputs.toxic_mfrac,
                holes_data=holes_payload,
                gff_by_hole=gff_map,
                ldmax_n_min=ldmax_val
            )
            self.step_4_9_result = res
            
            msg = f"CA_tox={res['CA_tox_inj_final']:.2f}" if res["applies"] else "No aplica"
            self.logs.append(f"Paso 4.9 Result: {msg}")
            return res
        except Exception as e:
            self.logs.append(f"Error 4.9: {e}")
            raise e

    
    
    def execute_step_4_10(self):
        """
        Paso 4.10: NFNT (Steam, Acids, Caustics).
        """
        self.logs.append("Iniciando Paso 4.10: NFNT Check")
        
        if not self.step_4_7_result:
             raise RuntimeError("Requiere Paso 4.7")
        
        # 1. Determinación de Categoría
        fluid = self.inputs.fluid_name
        category = None
        
        # Lógica de detección estricta basada en tus fluidos objetivo
        if "Steam" in fluid:
            category = NonFlamCategory.STEAM
        elif fluid in TABLE_4_9_ACID_CAUSTIC:
            category = NonFlamCategory.ACID_CAUSTIC
        
        # Si no es Steam ni Acid/Caustic válido, salimos con 0
        if not category:
            self.logs.append(f"Paso 4.10: Fluido '{fluid}' no es NFNT aplicable.")
            # Creamos un resultado dummy en 0 para que el paso final no falle
            # (Podrías crear una dataclass para el resultado del orquestador si lo deseas)
            self.step_4_10_result = type('obj', (object,), {
                'applies': False, 'CA_nfnt_inj_final': 0.0, 'CA_nfnt_cmd_final': 0.0
            })
            return self.step_4_10_result

        # 2. Preparar Inputs Normalizados
        def get_clean_key(k):
             s = k.value if hasattr(k, 'value') else str(k)
             return s.split('.')[-1].lower().strip()

        phys_map = {get_clean_key(k): v for k, v in self.step_4_7_result.results_by_hole.items()}
        rel_map = {get_clean_key(k): v for k, v in self.step_4_5_result.results_by_hole.items()}
        gff_map = {get_clean_key(k): v for k, v in self.step_4_2_result.gff.items()}
        
        ca_leak_results = {}
        
        # 3. Iterar y Calcular
        for s_key in ["small", "medium", "large", "rupture"]:
            if s_key not in phys_map: continue
            
            # Mapear Release Type al Enum local de este módulo
            # El paso 4.5 devuelve un enum propio, debemos convertirlo
            global_rel_type = rel_map[s_key].release_type.value.lower()
            nfnt_rel_type = NFNTReleaseType.CONTINUOUS if "continuous" in global_rel_type else NFNTReleaseType.INSTANTANEOUS
            
            inp = NonFlamHoleInputs(
                rate_n_lbm_s=phys_map[s_key].rate_lbm_s,
                mass_n_lbm=phys_map[s_key].mass_lbm,
                release_type=nfnt_rel_type
            )
            
            # Llamada al cálculo
            hole_res = compute_nonflammable_nontoxic_for_hole(
                category=category,
                hole=inp,
                fluid_name=fluid
            )
            
            ca_leak_results[s_key] = hole_res.CA_inj_leak

        # 4. Ponderación Final
        ca_final_inj = probability_weighted_nonflammable_area(
            ca_leak_by_hole=ca_leak_results,
            gff_by_hole=gff_map,
            gff_total=self.step_4_2_result.gff_total
        )
        
        # Guardar resultado en estructura compatible
        self.step_4_10_result = type('obj', (object,), {
            'applies': True,
            'CA_nfnt_inj_final': ca_final_inj,
            'CA_nfnt_cmd_final': 0.0 # NFNT no suele tener daño a equipos en L1
        })
        
        self.logs.append(f"Paso 4.10 OK ({category.value}). CA_nfnt_inj: {ca_final_inj:.2f} ft2")
        return self.step_4_10_result
    

    # =========================================================================
    # PASO 4.11: DETERMINAR ÁREAS FINALES DE DAÑO Y LESIÓN
    # =========================================================================
    def execute_final_consequence(self):
        self.logs.append("Iniciando Paso 4.11: Determinación Final de Áreas")
        
        # 1. Recopilar resultados previos (Manejo seguro de Nones/Ceros)
        
        # --- Inflamable (4.8) ---
        flam_cmd = 0.0
        flam_inj = 0.0
        if self.step_4_8_result:
            flam_cmd = self.step_4_8_result.CA_cmd_final
            flam_inj = self.step_4_8_result.CA_inj_final

        # --- Tóxico (4.9) ---
        # El paso 4.9 devuelve un diccionario
        tox_inj = 0.0
        # CMD por tóxicos es 0.0 en Level 1 (caf_cmd_tox)
        tox_cmd = 0.0 
        if self.step_4_9_result and self.step_4_9_result.get('applies'):
            tox_inj = self.step_4_9_result.get('CA_tox_inj_final', 0.0)

        # --- NFNT (4.10) ---
        nfnt_inj = 0.0
        nfnt_cmd = 0.0
        if hasattr(self, 'step_4_10_result') and self.step_4_10_result.applies:
            nfnt_inj = getattr(self.step_4_10_result, 'CA_nfnt_inj_final', 0.0)
            nfnt_cmd = getattr(self.step_4_10_result, 'CA_nfnt_cmd_final', 0.0)

        # 2. Construir objeto de entrada para 4.11
        inputs_11 = ConsequenceAreasByMechanism(
            # Component Damage
            caf_cmd_flam=flam_cmd,
            caf_cmd_tox=tox_cmd,
            caf_cmd_nfnt=nfnt_cmd,
            # Personnel Injury
            caf_inj_flam=flam_inj,
            caf_inj_tox=tox_inj,
            caf_inj_nfnt=nfnt_inj
        )

        # 3. Ejecutar cálculo formal (Eq 3.78 - 3.81)
        try:
            res_11 = compute_cof_4_11_damage_injury_areas(inputs_11)
            # Guardamos el resultado en el estado del orquestador (opcional, pero útil)
            self.step_4_11_result = res_11
        except Exception as e:
            self.logs.append(f"Error en Paso 4.11: {e}")
            raise e

        # 4. Determinar Escenario Dominante (Para Logs/UI)
        dominant_scenario = "Ninguno"
        final_area = res_11.caf
        
        if final_area > 0:
            if final_area == flam_cmd: dominant_scenario = "Inflamable (Daño Equipos)"
            elif final_area == flam_inj: dominant_scenario = "Inflamable (Lesión Personal)"
            elif final_area == tox_inj: dominant_scenario = "Tóxico (Lesión Personal)"
            elif final_area == nfnt_inj: dominant_scenario = "NFNT (Lesión Personal)"
            elif final_area == nfnt_cmd: dominant_scenario = "NFNT (Daño Equipos)"

        self.logs.append(f"Paso 4.11 Completado. FINAL COF: {final_area:.2f} ft2 ({dominant_scenario})")
        
        # Retornamos un diccionario compatible con lo que espera el frontend/tests actuales
        return {
            "final_cmd_area_ft2": res_11.caf_cmd,
            "final_inj_area_ft2": res_11.caf_inj,
            "final_cof_area_ft2": res_11.caf,
            "dominant_scenario": dominant_scenario,
            "trace": {
                "flam_cmd": res_11.caf_cmd_flam,
                "flam_inj": res_11.caf_inj_flam,
                "tox_inj": res_11.caf_inj_tox,
                "nfnt_inj": res_11.caf_inj_nfnt
            }
        }
    

    # =========================================================================
    # PASO 4.12: CONSECUENCIA FINANCIERA ($)
    # =========================================================================
    # def execute_step_4_12(self):
    #     self.logs.append("Iniciando Paso 4.12: Cálculo Financiero")
        
    #     # 1. Validaciones previas
    #     if not self.step_4_11_result: raise RuntimeError("Requiere Paso 4.11 (Áreas Finales)")
    #     if not self.step_4_2_result: raise RuntimeError("Requiere Paso 4.2 (GFF)")
    #     if not self.step_4_7_result: raise RuntimeError("Requiere Paso 4.7 (Masa Final)")

    #     # 2. Helper interno para mapear Enums (Orquestador -> Financiero)
    #     def map_hole_enum(k):
    #         # Convierte <ReleaseHoleSize.SMALL: 'small'> a FinHoleSize.SMALL
    #         k_str = str(k).lower().split('.')[-1] # "small", "medium", etc.
    #         if "small" in k_str: return FinHoleSize.SMALL
    #         if "medium" in k_str: return FinHoleSize.MEDIUM
    #         if "large" in k_str: return FinHoleSize.LARGE
    #         if "rupture" in k_str: return FinHoleSize.RUPTURE
    #         return None

    #     # 3. Mapear GFF (Probabilidades de Falla) del Paso 4.2
    #     gff_map_fin = {}
    #     for k, v in self.step_4_2_result.gff.items():
    #         hk = map_hole_enum(k)
    #         if hk: gff_map_fin[hk] = v

    #     # 4. Mapear Masas Liberadas del Paso 4.7
    #     mass_map_fin = {}
    #     for k, v in self.step_4_7_result.results_by_hole.items():
    #         hk = map_hole_enum(k)
    #         if hk: mass_map_fin[hk] = v.mass_lbm

    #     # 5. Validación de Fluido Ambiental
    #     fluid_lookup = self.inputs.fluid_name
    #     is_env_fluid = self._is_valid_env_fluid(fluid_lookup)
    #     if not is_env_fluid:
    #         self.logs.append(f"[INFO] Fluido '{fluid_lookup}' no requiere limpieza ambiental (o no está en Tabla 4.18).")

    #     # 6. Construir Inputs
    #     fin_inputs = FinancialInputs(
    #         component_type=self.inputs.component_type,
    #         gff_by_hole=gff_map_fin,
    #         gff_total=self.step_4_2_result.gff_total,
            
    #         # Áreas de Consecuencia (ft2)
    #         CA_f_cmd=self.step_4_11_result.caf_cmd,
    #         CA_f_inj=self.step_4_11_result.caf_inj,
            
    #         # Datos Económicos (Inputs de usuario)
    #         costfactor=self.inputs.material_cost_factor,
    #         material=self.inputs.material,
    #         equipcost=self.inputs.equipment_cost_ft2,
    #         prodcost=self.inputs.production_cost_day,
    #         popdens=self.inputs.population_density,
    #         injcost=self.inputs.injury_cost_person,
    #         envcost=self.inputs.environmental_cost_bbl,
    #         outage_mult=self.inputs.outage_multiplier,
            
    #         # Datos Ambientales
    #         fluid_key=fluid_lookup if is_env_fluid else None,
    #         mass_by_hole_lbm=mass_map_fin
    #     )

    #     try:
    #         # 7. Ejecutar Cálculo
    #         res = compute_cof_4_12_financial_consequence(fin_inputs)
    #         self.step_4_12_result = res
            
    #         self.logs.append(f"Paso 4.12 Completado. Costo Total: ${res.FC_f_total:,.2f}")
    #         return res
            
    #     except Exception as e:
    #         self.logs.append(f"Error en Paso 4.12: {e}")
    #         raise e

    # def _is_valid_env_fluid(self, fluid_name: str) -> bool:
    #     """
    #     Verifica si el nombre del fluido existe en la Tabla 4.18 (Propiedades Ambientales).
    #     Normaliza el string (mayúsculas, sin espacios extra) para comparar.
    #     """
    #     if not fluid_name:
    #         return False
        
    #     # Normalización local igual a la del módulo 4.12
    #     def norm(s): return " ".join(str(s).strip().upper().split())
        
    #     target = norm(fluid_name)
    #     # Verificamos si la llave existe en la tabla importada
    #     return target in TABLE_4_18_FLUID_PROPS

    def _is_valid_env_fluid(self, fluid_name: str) -> bool:
        """
        Helper para Paso 4.12:
        Verifica si el fluido existe en la Tabla 4.18 (Propiedades Ambientales).
        """
        if not fluid_name:
            return False
        
        # Normalización local (mismo criterio que el módulo 4.12)
        def norm(s): return " ".join(str(s).strip().upper().split())
        
        target = norm(fluid_name)
        
        # Verificamos si la llave existe en la tabla importada
        return target in TABLE_4_18_FLUID_PROPS

    def execute_step_4_12(self):
        self.logs.append("Iniciando Paso 4.12: Cálculo Financiero")
        
        if not self.step_4_11_result: raise RuntimeError("Requiere Paso 4.11")
        if not self.step_4_2_result: raise RuntimeError("Requiere Paso 4.2")
        if not self.step_4_7_result: raise RuntimeError("Requiere Paso 4.7")

        # ... (Mapeos de holes y GFF igual que antes) ...
        def map_hole_enum(k):
             # (Tu lógica de mapeo existente)
             k_str = str(k).lower().split('.')[-1]
             if "small" in k_str: return FinHoleSize.SMALL
             if "medium" in k_str: return FinHoleSize.MEDIUM
             if "large" in k_str: return FinHoleSize.LARGE
             if "rupture" in k_str: return FinHoleSize.RUPTURE
             return None

        gff_map_fin = {}
        for k, v in self.step_4_2_result.gff.items():
            hk = map_hole_enum(k)
            if hk: gff_map_fin[hk] = v

        mass_map_fin = {}
        for k, v in self.step_4_7_result.results_by_hole.items():
            hk = map_hole_enum(k)
            if hk: mass_map_fin[hk] = v.mass_lbm
        
        # 1. Obtener la Densidad Única y Verdadera
        # Calculada al vuelo desde (Personal / Area)
        pop_dens_val = self.inputs.effective_population_density
                
        # Validación de fluido
        fluid_lookup = self.inputs.fluid_name
        is_env_fluid = self._is_valid_env_fluid(fluid_lookup)

        # 2. Construir Inputs Financieros
        fin_inputs = FinancialInputs(
            component_type=self.inputs.component_type,
            gff_by_hole=gff_map_fin,
            gff_total=self.step_4_2_result.gff_total,
            
            CA_f_cmd=self.step_4_11_result.caf_cmd,
            CA_f_inj=self.step_4_11_result.caf_inj,
            
            costfactor=self.inputs.material_cost_factor,
            material=self.inputs.material,
            equipcost=self.inputs.equipment_cost_ft2,
            prodcost=self.inputs.production_cost_day,
            
            # AQUÍ: Usamos la densidad calculada. Sin overrides.
            popdens=pop_dens_val, 
            
            injcost=self.inputs.injury_cost_person,
            envcost=self.inputs.environmental_cost_bbl,
            outage_mult=self.inputs.outage_multiplier,
            
            fluid_key=fluid_lookup if is_env_fluid else None,
            mass_by_hole_lbm=mass_map_fin
        )

        try:
            res = compute_cof_4_12_financial_consequence(fin_inputs)
            self.step_4_12_result = res
            self.logs.append(f"Paso 4.12 Completado. Costo Total: ${res.FC_f_total:,.2f}")
            return res
        except Exception as e:
            self.logs.append(f"Error en Paso 4.12: {e}")
            raise e
    

    # =========================================================================
    # PASO 4.13: CONSECUENCIA DE SEGURIDAD (PERSONAS)
    # =========================================================================
    # def execute_step_4_13(self):
    #     self.logs.append("Iniciando Paso 4.13: Consecuencia de Seguridad")
        
    #     # Requiere el área final de lesión (calculada en 4.11)
    #     if not self.step_4_11_result:
    #         raise RuntimeError("Requiere Paso 4.11 (Áreas Finales de Lesión)")

    #     # 1. Preparar Escenario de Personal
    #     # El módulo 4.13 acepta una lista de casos. Aquí creamos uno simple
    #     # basado en los inputs del orquestador.
    #     staff_case = StaffingCase(
    #         pers_count=self.inputs.personnel_count,
    #         present_pct=self.inputs.personnel_presence_pct
    #     )

    #     # 2. Preparar Inputs
    #     # Nota: Usamos el área de lesión FINAL calculada en 4.11
    #     caf_inj = self.step_4_11_result.caf_inj
        
    #     safe_inputs = SafetyConsequenceInputs(
    #         ca_f_inj_area=caf_inj,
    #         area_safety=self.inputs.unit_area_ft2,
    #         staffing=[staff_case]
    #     )

    #     try:
    #         # 3. Ejecutar Cálculo
    #         res = compute_cof_4_13_safety_consequence(safe_inputs)
    #         self.step_4_13_result = res
            
    #         # Log informativo
    #         self.logs.append(f"Paso 4.13 Completado.")
    #         self.logs.append(f"  > Densidad Calc: {res.popdens:.6f} pers/ft2")
    #         self.logs.append(f"  > Consecuencia Final (Pers): {res.c_f_inj:.4f} personas afectadas")
            
    #         # VALIDACIÓN DE CONSISTENCIA (Opcional)
    #         # Advertir si la densidad usada en 4.12 difiere mucho de la calculada aquí
    #         if self.inputs.population_density > 0:
    #             diff = abs(res.popdens - self.inputs.population_density)
    #             if diff > 1e-5:
    #                 self.logs.append(f"[WARN] La densidad calculada en 4.13 ({res.popdens:.5f}) "
    #                                  f"difiere de la usada en 4.12 ({self.inputs.population_density:.5f})")

    #         return res
            
    #     except Exception as e:
    #         self.logs.append(f"Error en Paso 4.13: {e}")
    #         raise e

    def execute_step_4_13(self):
        self.logs.append("Iniciando Paso 4.13: Consecuencia de Seguridad")
        
        if not self.step_4_11_result: raise RuntimeError("Requiere Paso 4.11")

        # 1. Inputs Físicos Reales
        staff_case = StaffingCase(
            pers_count=self.inputs.personnel_count,
            present_pct=self.inputs.personnel_presence_pct
        )

        safe_inputs = SafetyConsequenceInputs(
            ca_f_inj_area=self.step_4_11_result.caf_inj,
            area_safety=self.inputs.unit_area_ft2,
            staffing=[staff_case]
        )

        try:
            res = compute_cof_4_13_safety_consequence(safe_inputs)
            self.step_4_13_result = res
            
            self.logs.append(f"Paso 4.13 Completado.")
            self.logs.append(f"  > Densidad Efectiva: {res.popdens:.6f} pers/ft2")
            self.logs.append(f"  > Personas Afectadas: {res.c_f_inj:.4f}")
            
            return res
            
        except Exception as e:
            self.logs.append(f"Error en Paso 4.13: {e}")
            raise e