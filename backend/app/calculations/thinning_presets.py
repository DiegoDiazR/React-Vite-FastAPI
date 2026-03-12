from typing import Tuple, Optional

from .thinning_calc_df import ThinningPriorsAndConditionals
from .thinning_prob_tables import (PRIOR_PROBABILITIES, 
                                   CONDITIONAL_PROBABILITIES, 
                                   LINING_CONDITION_MULTIPLIERS, 
                                   LINER_EXPECTED_LIFE_RANGES, 
                                   ONLINE_MONITORING_FACTORS)


def build_thinning_probabilities(confidence: str,
) -> ThinningPriorsAndConditionals:
    """
    Construye automáticamente las probabilidades API 581
    según Tablas 4.5 y 4.6
    """

    if confidence not in PRIOR_PROBABILITIES:
        raise ValueError("confidence must be: low | medium | high")

    pri = PRIOR_PROBABILITIES[confidence]

    def cp(level: str, state: int) -> float:
        return CONDITIONAL_PROBABILITIES[level][f"C0p{state}"]

    return ThinningPriorsAndConditionals(
        Prp1=pri["Prp1"],
        Prp2=pri["Prp2"],
        Prp3=pri["Prp3"],

        C0p1A=cp("A", 1), C0p1B=cp("B", 1), C0p1C=cp("C", 1), C0p1D=cp("D", 1),
        C0p2A=cp("A", 2), C0p2B=cp("B", 2), C0p2C=cp("C", 2), C0p2D=cp("D", 2),
        C0p3A=cp("A", 3), C0p3B=cp("B", 3), C0p3C=cp("C", 3), C0p3D=cp("D", 3)
    )

def get_lining_condition_factor(condition: str) -> float:
    """
    Obtiene el factor de ajuste por condición del liner (F_LC) según la Tabla 4.8.
    """
    valid_conditions = list(LINING_CONDITION_MULTIPLIERS.keys())
    if condition not in valid_conditions:
        raise ValueError(f"Condición de liner '{condition}' no es válida. Opciones: {valid_conditions}")
    
    return float(LINING_CONDITION_MULTIPLIERS[condition])


def get_liner_expected_life(liner_type: str, conservative: bool = True) -> float:
    """
    Obtiene la vida esperada del liner (RL_exp_liner) según la Tabla 4.7.
    
    Args:
        liner_type (str): El tipo de revestimiento interno.
        conservative (bool): Si es True, retorna el límite inferior del rango de vida útil. 
                             Si es False, retorna el promedio del rango.
    """
    valid_liners = list(LINER_EXPECTED_LIFE_RANGES.keys())
    if liner_type not in valid_liners:
        raise ValueError(f"Tipo de liner '{liner_type}' no es válido. Opciones: {valid_liners}")
    
    age_range = LINER_EXPECTED_LIFE_RANGES[liner_type]
    
    # Enfoque conservador: usar el mínimo del rango de vida útil esperada
    if conservative:
        return float(age_range[0])
    
    # Enfoque neutral: usar el promedio del rango
    return float(sum(age_range) / 2.0)


def get_online_monitoring_factor(mechanism: str, methods: list[str]) -> float:
    """
    Obtiene el factor de monitoreo en línea (F_OM) según la Tabla 4.9.
    Evalúa múltiples métodos y retorna el mayor (no son aditivos).
    
    Args:
        mechanism (str): El mecanismo de adelgazamiento.
        methods (list[str]): Lista de métodos de monitoreo usados en el equipo.
    """
    # 1. Fallback si el mecanismo no está en el diccionario
    if mechanism not in ONLINE_MONITORING_FACTORS:
        mechanism = "581-Thinning Damage"
        
    mechanism_data = ONLINE_MONITORING_FACTORS[mechanism]
    
    # 2. Si no mandaron métodos o la lista está vacía, el factor es 1.0 (sin crédito)
    if not methods:
        return 1.0
        
    max_factor = 1.0
    
    # 3. Iteramos por todos los métodos que ingresó el usuario
    for method in methods:
        # Limpiamos el texto por seguridad
        method_clean = method.strip()
        
        if method_clean not in mechanism_data:
            continue # Si el método no es válido (ej. viene vacío), lo ignoramos
            
        current_factor = float(mechanism_data[method_clean])
        
        # 4. Regla especial: "20 if in conjunction with probes"
        if method_clean == "Key Process Variable" and current_factor == 10.0:
            special_cases = [
                "581-Hydrochloric Acid Corrosion", 
                "581-Sulfuric Acid Corrosion"
            ]
            
            # Revisa automáticamente si "Electrical Resistance Probes" también está en la lista de métodos
            has_probes = any("Electrical Resistance Probes" in m for m in methods)
            
            if mechanism in special_cases and has_probes:
                current_factor = 20.0
                
        # 5. Guardamos solo el factor más alto (como exige la API 581)
        if current_factor > max_factor:
            max_factor = current_factor
            
    return max_factor

