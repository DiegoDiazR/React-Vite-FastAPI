# app/calculations/externalCracking_presets.py

from .externalCracking_tables import SUSCEPTIBILITY_DATA, SCC_DF_TABLE, SEVERITY_INDEX_TABLE

def get_external_cracking_susceptibility(mech, temp, driver, complexity="Average", insulation="Average", chloride_free=False):
    """Calcula la susceptibilidad con los ajustes de la norma [cite: 172-180]"""
    # 1. Rango de temperatura
    if temp < 120: range_key = "Below 120F"
    elif 120 <= temp <= 200: range_key = "120 to 200F"
    elif 200 < temp <= 300: range_key = "200 to 300F"
    else: range_key = "Above 300F"
    
    # Obtener susceptibilidad base de las tablas
    base_sus = SUSCEPTIBILITY_DATA.get(mech, {}).get(range_key, {}).get(driver, "None")
    
    # Si el mecanismo es atmosférico o no hay daño, retornamos ya [cite: 39]
    if mech == "581-Austenitic Component Atmospheric Cracking" or base_sus == "None":
        return base_sus

    # 2. Ajustes exclusivos para CUI-CISCC [cite: 172]
    levels = ["None", "Low", "Medium", "High"]
    idx = levels.index(base_sus)
    
    # Complejidad: Above Average aumenta, Below Average disminuye [cite: 173-174]
    if complexity == "Above Average": 
        idx = min(idx + 1, 3)
    elif complexity == "Below Average": 
        idx = max(idx - 1, 1) if idx > 0 else 0
    
    # Condición Aislamiento: Below Average aumenta, Above Average disminuye [cite: 176-177]
    if insulation == "Below Average": 
        idx = min(idx + 1, 3)
    elif insulation == "Above Average": 
        idx = max(idx - 1, 1) if idx > 0 else 0
    
    # Libre de Cloruros: Disminuye un nivel [cite: 180]
    if chloride_free: 
        idx = max(idx - 1, 1) if idx > 0 else 0
    
    return levels[idx]

def get_scc_base_df(svi, eff, num):
    """Busca el DF Base en la tabla 2.C.1.3"""
    if svi == 0: return 0.0
    if num == 0 or eff == "None":
        return float(SCC_DF_TABLE.get(svi, {}).get(("E", 0), svi))
    
    # Cap a 3 inspecciones para este ejemplo de tabla
    safe_num = min(num, 3)
    return float(SCC_DF_TABLE.get(svi, {}).get((eff, safe_num), svi))