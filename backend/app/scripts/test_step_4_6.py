import pprint
from app.calculations.cof_4_6_detec_isola_impact import (
    compute_cof_4_6_detection_isolation_impact, 
    Rating
)

def test_paso_4_6_impacto():
    print("="*80)
    print("PRUEBA PASO 4.6: IMPACTO DE DETECCIÓN Y AISLAMIENTO")
    print("="*80)

    # Caso 1: Planta Automatizada (A-A)
    print("\n[ESCENARIO 1: TOTALMENTE AUTOMATIZADO (A-A)]")
    res_aa = compute_cof_4_6_detection_isolation_impact(
        detection=Rating.A, 
        isolation=Rating.A
    )
    print(f"   Factor de Reducción (fact_di): {res_aa.fact_di}")
    print(f"   Tiempos Máximos (min):")
    pprint.pprint(res_aa.ld_max_minutes)

    # Caso 2: Operación Manual (C-C)
    print("\n[ESCENARIO 2: OPERACIÓN MANUAL / VISUAL (C-C)]")
    res_cc = compute_cof_4_6_detection_isolation_impact(
        detection=Rating.C, 
        isolation=Rating.C
    )
    print(f"   Factor de Reducción (fact_di): {res_cc.fact_di}")
    print(f"   Tiempos Máximos (min):")
    pprint.pprint(res_cc.ld_max_minutes)

    # Verificación de lógica conservadora
    print("\n[ESCENARIO 3: DETECCIÓN C / AISLAMIENTO A (No en Tabla 4.6)]")
    res_ca = compute_cof_4_6_detection_isolation_impact(
        detection=Rating.C, 
        isolation=Rating.A
    )
    print(f"   Factor fact_di esperado (0.00): {res_ca.fact_di}")

    # Verificación de lógica conservadora
    print("\n[ESCENARIO 4: DETECCIÓN C / AISLAMIENTO B (No en Tabla 4.6)]")
    res_cb = compute_cof_4_6_detection_isolation_impact(
        detection=Rating.C, 
        isolation=Rating.B
    )

    print(f"   Factor de Reducción (fact_di): {res_cb.fact_di}")
    print(f"   Tiempos Máximos (min):")
    pprint.pprint(res_cb.ld_max_minutes)

if __name__ == "__main__":
    test_paso_4_6_impacto()