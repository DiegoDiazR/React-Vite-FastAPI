import pprint
from app.calculations.cof_4_7_release_rate_mass import (
    compute_cof_4_7_for_holes, 
    ReleaseRateMassInputs
)

def test_paso_4_7_integral():
    print("="*85)
    print("PRUEBA PASO 4.7: MAGNITUD FINAL DE LA LIBERACIÓN (AJUSTADA)")
    print("="*85)

    # 1. Datos de entrada (Simulados del PIPE-8 con Rating A-A)
    # Wn obtenidos en el Paso 4.3 (lb/s)
    # Mass_avail obtenido en el Paso 4.4 (lb)
    # fact_di y ldmax obtenidos en el Paso 4.6 (Rating A-A)
    
    fact_di_cb = 0.1 # Reducción por sistema A-A
    
    inputs = {
        "small": ReleaseRateMassInputs(
            Wn_lbm_s=0.2375, mass_avail_lbm=31.52, fact_di=fact_di_cb, ldmax_min=60.0
        ),
        "medium": ReleaseRateMassInputs(
            Wn_lbm_s=3.8007, mass_avail_lbm=31.52, fact_di=fact_di_cb, ldmax_min=40.0
        ),
        "large": ReleaseRateMassInputs(
            Wn_lbm_s=60.8117, mass_avail_lbm=31.52, fact_di=fact_di_cb, ldmax_min=20.0
        ),
        "rupture": ReleaseRateMassInputs(
            Wn_lbm_s=243.2470, mass_avail_lbm=31.52, fact_di=fact_di_cb, ldmax_min=60.0
        )
    }

    # 2. Ejecución
    resultados = compute_cof_4_7_for_holes(inputs)

    # 3. Reporte
    print(f"\n{'HUECO':<10} | {'Wn_adj (lb/s)':<12} | {'ld_n (s)':<10} | {'Mass_n (lb)':<12}")
    print("-" * 65)

    for hole, res in resultados.items():
        print(f"{hole.upper():<10} | {res.rate_lbm_s:<12.4f} | {res.ld_s:<10.2f} | {res.mass_lbm:<12.4f}")

    print("\n" + "="*85)
    print("ANÁLISIS: Nota cómo Wn_adj es menor a Wn original por el crédito de seguridad.")
    print("="*85)

if __name__ == "__main__":
    test_paso_4_7_integral()