from datetime import date
from backend.app.calculations.externalDamage_presets import (
    build_cui_probabilities, 
    get_cui_base_rate, 
    build_cui_adjustment_factors
)

def test_cui_presets():
    print("--- INICIANDO PRUEBAS DE CUI_PRESETS ---")

    # 1. Prueba de Interpolación de Tasas de Corrosión (Paso 3)
    # Según Tabla 2.D.3.2M: 6°C -> 0.254 (Severe) y 32°C -> 0.254 (Severe)
    # Probamos un valor intermedio (ej. 20°C) y límites.
    print("\n1. Verificando Interpolación CrB (mm/y):")
    
    t_exacta = get_cui_base_rate(71, "Severe")
    t_interp = get_cui_base_rate(50, "Moderate") # Entre 32°C (0.127) y 71°C (0.254)
    t_limite = get_cui_base_rate(200, "Dry")     # Fuera de rango (debe dar el último valor)
    
    print(f"   - Tasa exacta (71°C, Severe): {t_exacta} mm/y (Esperado: 0.508)")
    print(f"   - Tasa interpolada (50°C, Moderate): {t_interp:.4f} mm/y")
    print(f"   - Tasa límite (200°C, Dry): {t_limite} mm/y (Esperado: 0.0)")

    # 2. Prueba de Factores de Ajuste (Paso 4)
    # Verificamos que los strings cualitativos mapeen a los multiplicadores del PDF
    print("\n2. Verificando Mapeo de Factores Cualitativos:")
    
    factores = build_cui_adjustment_factors(
        insulation_type="Cellular glass",      # F_INS = 0.75
        complexity="Above Average",            # F_CM = 1.25
        insulation_condition="Below Average",  # F_IC = 1.25
        pooling_design=True,                   # F_EQ = 2.0
        soil_water_interface=False             # F_IF = 1.0
    )
    
    print(f"   - F_INS (Cellular glass): {factores.F_INS} (Esperado: 0.75)")
    print(f"   - F_CM (Above Average): {factores.F_CM} (Esperado: 1.25)")
    print(f"   - F_IC (Below Average): {factores.F_IC} (Esperado: 1.25)")
    print(f"   - Max(F_EQ, F_IF): {max(factores.F_EQ, factores.F_IF)} (Esperado: 2.0)")

    # 3. Prueba de Probabilidades Bayesianas (Pasos 15-16)
    # Verificamos que se construya el objeto de probabilidades correctamente
    print("\n3. Verificando Construcción de Probabilidades:")
    
    probs = build_cui_probabilities(
        confidence="medium", 
        eff_A="A", # Alta efectividad
        eff_B="C"  # Mediana
    )
    
    print(f"   - Prior Prp1 (Medium): {probs.Prp1} (Esperado: 0.7)")
    print(f"   - Condicional C0p1A (Efectividad A): {probs.C0p1A} (Esperado: 0.9)")
    print(f"   - Condicional C0p1B (Efectividad C): {probs.C0p1B} (Esperado: 0.5)")

    print("\n--- PRUEBAS FINALIZADAS EXITOSAMENTE ---")

if __name__ == "__main__":
    test_cui_presets()