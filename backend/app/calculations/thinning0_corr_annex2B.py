from pydantic import BaseModel, Field
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass

# Importar tus calculadoras
from .thinning1_corr_HCL import HClCorrosionCalculator
from .thinning2_corr_HTS_NA import HTSNACorrosionMaster
from .thinning3_corr_HT_H2S_H2 import H2S_CorrosionCalculator
from .thinning4_corr_H2SO4 import SulfuricAcidCorrosionEngine
from .thinning5_corr_HF import HFCorrosionCalculator
from .thinning6_corr_AlkalineSourWater import AlkalineSourWaterCorrosion
from .thinning7_corr_Amine import AmineCorrosionCalculator
from .thinning8_corr_HT_Oxidation import CalculadoraOxidacionAltaTemp
from .thinning9_corr_Acid_Sour_Water import AcidSourWaterCorrosion
from .thinning10_corr_Cooling_Water import CoolingWaterCorrosion
from .thinning11_corr_soil_side import CalculadoraCorrosionSuelo
from .thinning12_corr_CO2 import CO2CorrosionModel 

@dataclass(frozen=True)
class CorrosionCalcInput:
    # Variables Mandatorias
    mechanism: str
    material: str
    
    # Variables Globales / Comunes
    temp: Optional[float] = None
    velocity: Optional[float] = 0.0
    ph: Optional[float] = None
    oxi: Optional[bool] = False
    cl_wppm: Optional[float] = None
    
    # --- Variables Específicas por Mecanismo ---
    
    # Ácidos (Sulfúrico, HF)
    sulfuric_conc: Optional[float] = None
    hf_conc: Optional[float] = None
    
    # Acid / Alkaline Sour Water
    water_present: Optional[bool] = True
    chlorides_present: Optional[bool] = False
    oxygen_ppb: Optional[float] = 0.0
    nh4hs_pct: Optional[float] = None
    ph2s_psia: Optional[float] = None
    
    # HTS / Nafténico / H2S
    h2s_mole_pct: Optional[float] = None
    hydrocarbon_type: Optional[str] = "Naphtha"
    sulfur: Optional[float] = None
    tan: Optional[float] = None
    
    # Aminas
    amine_type: Optional[str] = None
    amine_conc: Optional[float] = None
    acid_gas_loading: Optional[float] = None
    hsas_pct: Optional[float] = None
    
    # Cooling Water
    is_recirculation: Optional[bool] = False
    is_treated: Optional[bool] = False
    is_seawater: Optional[bool] = False
    cw_system_type: Optional[str] = "open"
    tds: Optional[float] = None
    ca_hardness: Optional[float] = None
    mo_alkalinity: Optional[float] = None
    
    # Soil Side (Suelo)
    tipo_suelo: Optional[str] = None
    condicion_cp: Optional[str] = None
    resistividad_ohm_cm: Optional[float] = None
    resistividad_ya_considerada_en_base: Optional[bool] = False
    tiene_revestimiento: Optional[bool] = False
    tipo_revestimiento: Optional[str] = None
    edad_mayor_20: Optional[bool] = False
    temp_excedida: Optional[bool] = False
    mantenimiento_raro: Optional[bool] = False
    
    # CO2 Corrosion
    diameter_in: Optional[float] = 8.0
    P_psia: Optional[float] = None
    liquid_hcs_present: Optional[bool] = False
    water_content_pct: Optional[float] = 0.0
    water_weight_pct: Optional[float] = 0.0
    co2_mole_pct: Optional[float] = 0.0
    pH_condition: Optional[str] = "condensation"
    rho_m: Optional[float] = 1000.0
    mu_m_cp: Optional[float] = 1.0
    e_m: Optional[float] = 0.000045
    glycol_pct: Optional[float] = 0.0
    inhibitor_efficiency: Optional[float] = 0.0

class CorrosionRouter:
    def __init__(self):
        # 2. INSTANCIAR EN MEMORIA
        self.hcl_calc = HClCorrosionCalculator() #
        self.hts_na_calc = HTSNACorrosionMaster()
        self.h2s_calc = H2S_CorrosionCalculator()
        self.h2so4_calc = SulfuricAcidCorrosionEngine() #
        self.hf_calc = HFCorrosionCalculator()
        self.alkaline_sw_calc = AlkalineSourWaterCorrosion()
        self.amine_calc = AmineCorrosionCalculator()
        self.ht_ox_calc = CalculadoraOxidacionAltaTemp()
        self.acid_sw_calc = AcidSourWaterCorrosion()
        self.cw_calc = CoolingWaterCorrosion()
        self.co2_calc = CO2CorrosionModel()

    def calculate_rates(self, inputs: CorrosionCalcInput) -> Dict[str, Any]:
        
        if not inputs.material:
            raise ValueError("Se requiere un material válido para el cálculo.")
        
        mechanism = inputs.mechanism    
        mat = inputs.material.strip()

        trace_log = {
            "mechanism_evaluated": mechanism,
            "variables_used": {}    
        }

        mpy_final = 0.0

        # ==========================================
        # 1. ÁCIDO CLORHÍDRICO (HCl)
        # ==========================================
        if mechanism == "581-Hydrochloric Acid Corrosion":
            mat_hcl = [
                    "Carbon Steel",
                    "Type 304 Series Stainless Steel", 
                    "Type 316 Series Stainless Steel",
                    "Type 321 Series Stainless Steel", 
                    "Type 347 Series Stainless Steel", 
                    "Alloy 400",
                    "Alloy C-276", 
                    "Alloy B-2", 
                    "Alloy 825", 
                    "Alloy 625"
            ]
            # Validar aplicabilidad
            if mat not in mat_hcl:
                raise ValueError(f"El material '{mat}' no es aplicable para HCl Corrosion.")
                
            trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "ph": inputs.ph,
                    "cl_wppm": inputs.cl_wppm,
                    "oxygen_present": inputs.oxi
                    }

            mpy = self.hcl_calc.calcular_tasa(material=mat, 
                                                  temp_f=inputs.temp, 
                                                  ph=inputs.ph, 
                                                  cl_wppm=inputs.cl_wppm, 
                                                  oxigeno=inputs.oxi)
            trace_log["corrosion_rate"] = mpy
            if isinstance(mpy, str): raise ValueError(f"Validación Ácido Cloridrico: '{mpy}'")
            mpy_final = float(mpy)
             
            
            # ==========================================
            # 2. ÁCIDO SULFÚRICO (H2SO4)
            # ==========================================
        elif mechanism == "581-Sulfuric Acid Corrosion":
                mat_sulfuric = [
                    "Carbon Steel",
                    "Type 304 Stainless Steel",
                    "Type 316 Stainless Steel",
                    "Alloy 20",
                    "Alloy C-276",
                    "Alloy B-2"
                ]
                if mat not in mat_sulfuric:
                    raise ValueError(f"El material '{mat}' no es aplicable para Sulfuric Acid Corrosion. Opciones: '{mat_sulfuric}'")
                
                trace_log["variables_used"] = {
                    "material": mat,
                    "sulfuric_concent": inputs.sulfuric_conc,
                    "temp_f": inputs.temp,
                    "fluid_velocity": inputs.velocity,
                    "oxidant": inputs.oxi
                }

                mpy = self.h2so4_calc.get_corrosion_rate(material=mat,
                                                         temp_f=inputs.temp,
                                                         ph=inputs.ph,
                                                         cl_wppm=inputs.cl_wppm, 
                                                         oxigeno=inputs.oxi)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Ácido Sulfúrico: '{mpy}'")
                mpy_final = float(mpy)
                
            # ==========================================
            # 3. OXIDACIÓN A ALTA TEMPERATURA
            # ==========================================
        elif mechanism == "581-High Temperature Oxidation":
                mat_ht_ox = [
                    "Carbon Steel",
                    "1 1/4Cr",
                    "2 1/4Cr",
                    "5Cr",
                    "7Cr",
                    "9Cr",
                    "12Cr",
                    "Type 304 Stainless Steel",
                    "Type 309 Stainless Steel",
                    "310 SS/HK",
                    "800 H/HP"
                ]
                if mat not in mat_ht_ox:
                    raise ValueError(f"El material '{mat}' no aplica para Oxidacion por Alta Temperatura. Opciones: '{mat_ht_ox}'")
                
                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp
                }

                mpy = self.ht_ox_calc.calcular_tasa(material=mat, temperatura_f=inputs.temp)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Oxidacion por Alta Temperatura: '{mpy}'")
                mpy_final = float(mpy)
            
            
            # ==========================================
            # 4. High Temperature H2/H2S Corrosion
            # ==========================================
        elif mechanism == "581-High Temperature H2/H2S Corrosion":
                mat_ht_hs_h2s = [
                    "Carbon Steel", 
                    "1Cr-1/5Mo", 
                    "1Cr-1/2Mo", 
                    "1 1/4Cr-1/2Mo", 
                    "2 1/4Cr-1Mo", 
                    "3Cr-1Mo",
                    "5Cr-1/2Mo",
                    "7Cr",
                    "9Cr-1Mo",
                    "12Cr",
                    "Type 304 Stainless Steel", 
                    "Type 304L Stainless Steel",
                    "Type 316 Stainless Steel", 
                    "Type 316L Stainless Steel",
                    "Type 321 Stainless Steel", 
                    "Type 347 Stainless Steel"
                ]
            
                if mat not in mat_ht_hs_h2s:
                    raise ValueError(f"El material '{mat}' no aplica para Corrosion por Alta Temperatura H2/H2S. Opciones: '{mat_ht_hs_h2s}'")
            
                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "h2s_content": inputs.h2s_mole_pct,
                    "tipo_hicrocarburo": inputs.hydrocarbon_type
                    }
            
                mpy = self.h2s_calc.get_corrosion_rate(material=mat, 
                                                   temp_f=inputs.temp, 
                                                   h2s_mole_pct=inputs.h2s_mole_pct, 
                                                   hydrocarbon_type=inputs.hydrocarbon_type)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Corrosion por Alta Temperatura H2/H2S: '{mpy}'")
                mpy_final = float(mpy)
            
            # ==========================================
            # 5. High Temperature Sulfidic and Naphthenic Acid
            # ==========================================
        
        elif mechanism == "581-High Temperature Sulfidic and Naphthenic Acid":
                mat_ht_sulfidic_naphthenic = [
                    "Carbon Steel",
                    "1Cr-1/5Mo",
                    "1Cr-1/2Mo",
                    "1 1/4Cr-1/2Mo",
                    "2 1/4Cr-1Mo",
                    "3Cr-1Mo",
                    "5Cr",
                    "7Cr",
                    "9Cr",
                    "12Cr",
                    "Austenitic SS Without Mo",
                    "316 SS with < 2.5 % Mo",
                    "316 SS with ≥ 2.5 %"
                ]
            
                if mat not in mat_ht_sulfidic_naphthenic:
                    raise ValueError(f"El material '{mat}' no aplica para Corrosion Alta Temperatura por Acido Sulfidico y Naftenico. Opciones: '{mat_ht_sulfidic_naphthenic}'")
                
                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "sulfur_content": inputs.sulfur,
                    "tan": inputs.tan,
                    "fluid_velocity": inputs.velocity
                    }
            
                mpy = self.hts_na_calc.calculate(material=mat, 
                                                 temperature=inputs.temp, 
                                                 sulfur=inputs.sulfur, 
                                                 tan=inputs.tan, 
                                                 velocity=inputs.velocity)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Corrosion Alta Temperatura por Acido Sulfidico y Naftenico: '{mpy}'")
                mpy_final = float(mpy)
            
            # ==========================================
            # 6. hydrofluoric Acid Corrosion
            # ==========================================
        
        elif mechanism == "581-Hydrofluoric Acid Corrosion":
                mat_hf_corrosion = [
                    "Carbon Steel",
                    "Alloy 400"
                ]
            
                if mat not in mat_hf_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para Corrosion por HF. Opciones: '{mat_hf_corrosion}'")
            
                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "hf_content": inputs.sulfur,
                    "fluid_velocity": inputs.velocity,
                    "oxidizers": inputs.oxi}
            
                mpy = self.hf_calc.determinar_tasa(material=mat, 
                                               temp_f=inputs.temp, 
                                               hf_conc=inputs.hf_conc, 
                                               velocidad_ft_s=inputs.velocity, 
                                               aerado=inputs.oxi)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Corrosion por HF: '{mpy}'")
                mpy_final = float(mpy)
        
            # ==========================================
            # 7. Alkaline Sour Water Corrosion
            # ==========================================

        elif mechanism == "581-Alkaline Sour Water Corrosion":
                mat_alkaline_corrosion = "Carbon Steel"

                if mat not in mat_alkaline_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para Alkaline Sour Water Corrosion. Opciones: '{mat_alkaline_corrosion}'")
                
                trace_log["variables_used"] = {
                    "material": mat,
                    "nh4hs_concentration ": inputs.nh4hs_pct,
                    "fluid_velocity": inputs.velocity,
                    "h2s_partial_pressure": inputs.ph2s_psia
                    }
                
                mpy = self.alkaline_sw_calc.calculate_corrosion_rate(nh4hs_pct=inputs.nh4hs_pct, 
                                                                     velocity=inputs.velocity, 
                                                                     ph2s=inputs.ph2s_psia)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Alkaline Sour Water Corrosion: '{mpy}'")
                mpy_final = float(mpy)
            
            # ==========================================
            # 8. Amine Corrosion
            # ==========================================

        elif mechanism == "581-Amine Corrosion":
                mat_amine_corrosion = [
                    "Carbon Steel",
                    "Stainless Steel"
                    ]
                
                if mat not in mat_amine_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para Amine Corrosion. Opciones: '{mat_amine_corrosion}'")
                
                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "amine_type": inputs.amine_type,
                    "amine_concentration": inputs.amine_conc,
                    "acid_gas_loading": inputs.acid_gas_loading,
                    "fluid_velocity": inputs.velocity,
                    "hsas_concentration": inputs.hsas_pct,
                    }
                
                mpy = self.amine_calc.calculate_rate(material=mat, 
                                                     amine=inputs.amine_type, 
                                                     conc=inputs.amine_conc, 
                                                     temp=inputs.temp, 
                                                     loading=inputs.acid_gas_loading, 
                                                     velocity=inputs.velocity, 
                                                     hsas=inputs.hsas_pct)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Alkaline Sour Water Corrosion: '{mpy}'")
                mpy_final = float(mpy)
            
            # ==========================================
            # 9. Acid Sour Water Corrosion
            # ==========================================

        elif mechanism == "581-Acid Sour Water Corrosion":
                mat_acid_sw_corrosion = [
                    "Carbon Steel",
                    "Low-alloy Steels"
                    ]
                
                if mat not in mat_acid_sw_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para Acid Sour Water Corrosion. Opciones: '{mat_acid_sw_corrosion}'")
                
                mat_review = mat in mat_acid_sw_corrosion

                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "water_presemy": inputs.water_present,
                    "ph": inputs.ph,
                    "chlorides_present": inputs.chlorides_present,
                    "oxydants_present": inputs.oxygen_ppb,
                    "fluid_velocity": inputs.velocity,
                    }
                
                mpy = self.acid_sw_calc.calculate_corrosion_rate(water_present=inputs.water_present, 
                                                                 ph=inputs.ph, 
                                                                 chlorides_present=inputs.chlorides_present, 
                                                                 is_carbon_or_low_alloy= mat_review, 
                                                                 temperature_f=inputs.temp, 
                                                                 oxygen_ppb=inputs.oxygen_ppb, 
                                                                 velocity=inputs.velocity, 
                                                                 velocity_unit='fps')
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Acid Sour Water Corrosion: '{mpy}'")
                mpy_final = float(mpy)
            
            # ==========================================
            # 10. Cooling Water Corrosion
            # ==========================================

        elif mechanism == "581-Cooling Water Corrosion":
                mat_cooling_w_corrosion = [
                    "Carbon Steel",
                    "Low-alloy Steels"
                    ]
                
                if mat not in mat_cooling_w_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para Cooling Water Corrosion. Opciones: '{mat_cooling_w_corrosion}'")
                
                mat_review = mat in mat_cooling_w_corrosion

                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "is_recirculation": inputs.is_recirculation,
                    "is_treated": inputs.is_treated,
                    "is_seawater": inputs.is_seawater,
                    "system_type": inputs.cw_system_type,
                    "fluid_velocity": inputs.velocity,
                    "tds": inputs.tds,
                    "ca_hardness": inputs.ca_hardness,
                    "mo_alkalinity": inputs.mo_alkalinity,
                    "fluid_velocity": inputs.ph,
                    "chlorides": inputs.cl_wppm
                    }
                
                mpy = self.cw_calc.evaluate_system(is_carbon_steel=mat_review, 
                                                   is_recirculation=inputs.is_recirculation, 
                                                   is_treated=inputs.is_treated, 
                                                   is_seawater=inputs.is_seawater, 
                                                   system_type=inputs.cw_system_type, 
                                                   temp_F=inputs.temp, 
                                                   velocity_fts=inputs.velocity, 
                                                   tds=inputs.tds, 
                                                   ca_hardness=inputs.ca_hardness, 
                                                   mo_alkalinity=inputs.mo_alkalinity, 
                                                   ph_a=inputs.ph, 
                                                   chlorides=inputs.cl_wppm)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Cooling Water Corrosion: '{mpy}'")
                mpy_final = float(mpy)
            
            # ==========================================
            # 11. Soil Side Corrosion
            # ==========================================

        elif mechanism == "581-Soil Side Corrosion":
                mat_soil_corrosion = "Carbon Steel"

                if mat not in mat_soil_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para Soil Side Corrosion. Opciones: '{mat_soil_corrosion}'")
                                
                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "tipo_suelon": inputs.tipo_suelo,
                    "condicion_cp": inputs.condicion_cp,
                    "resistividad_ohm_cm": inputs.resistividad_ohm_cm,
                    "resistividad_ya_considerada_en_base": inputs.resistividad_ya_considerada_en_base,
                    "tiene_revestimiento": inputs.tiene_revestimiento,
                    "tipo_revestimiento": inputs.tipo_revestimiento,
                    "edad_mayor_20": inputs.edad_mayor_20,
                    "temp_excedida": inputs.temp_excedida,
                    "mantenimiento_raro": inputs.mantenimiento_raro
                    }
                
                mpy = CalculadoraCorrosionSuelo(tipo_suelo=inputs.tipo_suelo, 
                                                temperatura_f=inputs.temp, 
                                                condicion_cp=inputs.condicion_cp, 
                                                resistividad_ohm_cm=inputs.resistividad_ohm_cm, 
                                                resistividad_ya_considerada_en_base=inputs.resistividad_ya_considerada_en_base, 
                                                tiene_revestimiento=inputs.tiene_revestimiento, 
                                                tipo_revestimiento=inputs.tipo_revestimiento, 
                                                edad_mayor_20=inputs.edad_mayor_20, 
                                                temp_excedida=inputs.temp_excedida, 
                                                mantenimiento_raro=inputs.mantenimiento_raro)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación Soil Side Corrosion: '{mpy}'")
                mpy_final = float(mpy)

            
            # ==========================================
            # 12. CO2 Corrosion
            # ==========================================

        elif mechanism == "581-CO2 Corrosion":
                mat_co2_corrosion = "Carbon Steel"

                if mat not in mat_co2_corrosion:
                    raise ValueError(f"El material '{mat}' no aplica para CO2 Corrosion. Opciones: '{mat_co2_corrosion}'")
                
                mat_review = mat in mat_co2_corrosion

                trace_log["variables_used"] = {
                    "material": mat,
                    "temp_f": inputs.temp,
                    "liquid_hcs_present": inputs.liquid_hcs_present,
                    "water_content_pct": inputs.water_content_pct,
                    'fluid_velocity': inputs.velocity,
                    "diameter_in": inputs.diameter_in,
                    "water_weight_pct": inputs.water_weight_pct,
                    "P_psia": inputs.P_psia,
                    "co2_mole_pct": inputs.co2_mole_pct,
                    "pH_condition": inputs.pH_condition,
                    "rho_m": inputs.rho_m,
                    "mu_m_cp": inputs.mu_m_cp,
                    "e_m": inputs.e_m,
                    "glycol_pct": inputs.glycol_pct,
                    "inhibitor_efficiency": inputs.inhibitor_efficiency
                    
                    }
                
                co2_params = {
                    'is_carbon_steel': mat_review,
                    'liquid_hcs_present': inputs.liquid_hcs_present,
                    'water_content_pct': inputs.water_content_pct,
                    'fluid_velocity_fps': inputs.velocity,
                    'diameter_in': inputs.diameter_in,
                    'water_weight_pct': inputs.water_weight_pct,
                    'T_F': inputs.temp,
                    'P_psia': inputs.P_psia,
                    'co2_mole_pct': inputs.co2_mole_pct,
                    'pH_condition': inputs.pH_condition,
                    'rho_m': inputs.rho_m,
                    'mu_m_cp': inputs.mu_m_cp,
                    'e_m': inputs.e_m,
                    'glycol_pct': inputs.glycol_pct,
                    'inhibitor_efficiency': inputs.inhibitor_efficiency
                }

                mpy = self.co2_calc.calculate_corrosion_rate(**co2_params)
                trace_log["corrosion_rate"] = mpy
                if isinstance(mpy, str):
                    raise ValueError(f"Validación CO2 Corrosion: '{mpy}'")
                mpy_final = float(mpy)
                
        else:
            raise ValueError(f"Mecanismo no implementado en el router: {mechanism}")
        
        return {
            "corrosion_rate_mpy": round(mpy_final, 3),
            "corrosion_rate_in_yr": round(mpy_final / 1000.0, 6),
            "trace": trace_log
        }

corrosion_router = CorrosionRouter()