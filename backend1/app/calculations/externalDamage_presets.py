from typing import Optional, Literal
from .externalDamage_calc_df import CUIPriorsAndConditionals, CUIAdjustmentFactors
from .externalDamage_prob_tables import (
    PRIOR_PROBABILITIES_CUI,
    CONDITIONAL_PROBABILITIES_CUI,
    CUI_CORROSION_RATES,
    INSULATION_TYPE_FACTORS,
    COMPLEXITY_FACTORS,
    INSULATION_CONDITION_FACTORS,
    EQUIPMENT_DESIGN_FACTORS,
    INTERFACE_FACTORS
)

# Valores fijos para Tipo de Aislamiento (Tabla 2.D.3.3) 
INSULATION_TYPES = Literal[
    "Unknown/unspecified", "Asbestos", "Cellular glass", "Expanded perlite",
    "Fiberglass", "Type E fiberglass", "Mineral wool", "Mineral wool (water resistant)",
    "Calcium silicate", "Flexible aerogel", "Microporous blanket", 
    "Intumescent coating", "Cementitious coating"
]

# Valores fijos para Complejidad y Condición [cite: 127]
COMPLEXITY_OPTIONS = Literal["Below Average", "Average", "Above Average"]
CONDITION_OPTIONS = Literal["Below Average", "Average", "Above Average"]


# def build_cui_probabilities(
#     confidence: str,          # "low" | "medium" | "high"
#     eff_A: str = "E",         # A/B/C/D/E (E es "Ninguna")
#     eff_B: str = "E",
#     eff_C: str = "E",
#     eff_D: str = "E",
# ) -> CUIPriorsAndConditionals:
#     """
#     Construye las probabilidades Bayesianas para CUI siguiendo la Tabla 4.5 y 4.6.
#     Misma estructura que build_thinning_probabilities.
#     """
#     if confidence not in PRIOR_PROBABILITIES_CUI:
#         raise ValueError("confidence debe ser: low | medium | high")

#     pri = PRIOR_PROBABILITIES_CUI[confidence]

#     def cp(level: str, state: int) -> float:
#         return CONDITIONAL_PROBABILITIES_CUI[level][f"C0p{state}"]

#     return CUIPriorsAndConditionals(
#         Prp1=pri["Prp1"], Prp2=pri["Prp2"], Prp3=pri["Prp3"],
#         C0p1A=cp(eff_A, 1), C0p1B=cp(eff_B, 1), C0p1C=cp(eff_C, 1), C0p1D=cp(eff_D, 1),
#         C0p2A=cp(eff_A, 2), C0p2B=cp(eff_B, 2), C0p2C=cp(eff_C, 2), C0p2D=cp(eff_D, 2),
#         C0p3A=cp(eff_A, 3), C0p3B=cp(eff_B, 3), C0p3C=cp(eff_C, 3), C0p3D=cp(eff_D, 3),
#     )

def build_cui_probabilities(confidence: str) -> CUIPriorsAndConditionals:
    """
    Solo construye el objeto con los valores FIJOS de las tablas 4.5 y 4.6.
    """
    if confidence not in PRIOR_PROBABILITIES_CUI:
        raise ValueError("confidence debe ser: low | medium | high")

    pri = PRIOR_PROBABILITIES_CUI[confidence]

    def cp(level: str, state: int) -> float:
        return CONDITIONAL_PROBABILITIES_CUI[level][f"C0p{state}"]

    # Aquí devolvemos los valores BASE de la tabla, sin elevarlos a ninguna potencia
    return CUIPriorsAndConditionals(
        Prp1=pri["Prp1"], Prp2=pri["Prp2"], Prp3=pri["Prp3"],

        C0p1A=cp("A", 1), C0p1B=cp("B", 1), C0p1C=cp("C", 1), C0p1D=cp("D", 1),
        C0p2A=cp("A", 2), C0p2B=cp("B", 2), C0p2C=cp("C", 2), C0p2D=cp("D", 2),
        C0p3A=cp("A", 3), C0p3B=cp("B", 3), C0p3C=cp("C", 3), C0p3D=cp("D", 3)
    )


def get_cui_base_rate(temp_c: float, driver: str) -> float:
    """
    Obtiene la tasa de corrosión base (CrB) mediante interpolación lineal (Paso 3)[cite: 17, 137].
    Drivers: 'Severe' (0), 'Moderate' (1), 'Mild' (2), 'Dry' (3)[cite: 135].
    """
    driver_map = {"Severe": 0, "Moderate": 1, "Mild": 2, "Dry": 3}
    idx = driver_map.get(driver, 2) # Por defecto 'Mild'
    
    temps = sorted(CUI_CORROSION_RATES.keys())
    
    # Manejo de límites
    if temp_c <= temps[0]: return CUI_CORROSION_RATES[temps[0]][idx]
    if temp_c >= temps[-1]: return CUI_CORROSION_RATES[temps[-1]][idx]
    
    # Interpolación lineal 
    for i in range(len(temps) - 1):
        t1, t2 = temps[i], temps[i+1]
        if t1 <= temp_c <= t2:
            r1 = CUI_CORROSION_RATES[t1][idx]
            r2 = CUI_CORROSION_RATES[t2][idx]
            return r1 + (r2 - r1) * (temp_c - t1) / (t2 - t1)
    return 0.0

# def build_cui_adjustment_factors(
#     insulation_type: str = "Unknown/unspecified",
#     complexity: str = "Average",
#     insulation_condition: str = "Average",
#     pooling_design: bool = False,
#     soil_water_interface: bool = False
# ) -> CUIAdjustmentFactors:
#     """
#     Mapea las selecciones cualitativas a factores numéricos (Paso 4)[cite: 25, 27].
#     """
#     return CUIAdjustmentFactors(
#         F_INS=INSULATION_TYPE_FACTORS.get(insulation_type, 1.5), # [cite: 28, 140]
#         F_CM=COMPLEXITY_FACTORS.get(complexity, 1.0),            # [cite: 29]
#         F_IC=INSULATION_CONDITION_FACTORS.get(insulation_condition, 1.0), # [cite: 36]
#         F_EQ=EQUIPMENT_DESIGN_FACTORS.get("Yes" if pooling_design else "No"), # [cite: 40]
#         F_IF=INTERFACE_FACTORS.get("Yes" if soil_water_interface else "No")   # [cite: 41]
#     )

def build_cui_adjustment_factors(
    dm_ext_dm: str,
    insulation_type: INSULATION_TYPES = "Unknown/unspecified",
    complexity: COMPLEXITY_OPTIONS = "Average",
    insulation_condition: CONDITION_OPTIONS = "Average",
    pooling_design: bool = False,
    soil_water_interface: bool = False
) -> CUIAdjustmentFactors:
    """
    Mapea selecciones cualitativas fijas a factores numéricos de la norma API 581.
    """
    # 1. Factores de diseño (Fijos: 2.0 si aplica, 1.0 si no) 
    f_eq = 2.0 if pooling_design else 1.0 
    f_if = 2.0 if soil_water_interface else 1.0

    # 2. Si el mecanismo es Atmosférico, los factores de aislamiento se neutralizan a 1.0
    if dm_ext_dm == "581-Ferritic Component Atmospheric Corrosion":
        return CUIAdjustmentFactors(F_INS=1.0, F_CM=1.0, F_IC=1.0, F_EQ=f_eq, F_IF=f_if)
    
    # 3. Para CUI, asignamos los valores fijos de las tablas de la norma 
    f_ins = INSULATION_TYPE_FACTORS.get(insulation_type, 1.5) # 
    f_cm = COMPLEXITY_FACTORS.get(complexity, 1.0)           # [cite: 31, 32]
    f_ic = INSULATION_CONDITION_FACTORS.get(insulation_condition, 1.0) # [cite: 38, 39]

    return CUIAdjustmentFactors(
        F_INS=f_ins, F_CM=f_cm, F_IC=f_ic, F_EQ=f_eq, F_IF=f_if
    )
