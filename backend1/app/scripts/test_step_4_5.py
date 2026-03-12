import pprint
from app.calculations.cof_4_5_release_type import compute_cof_4_5_release_types

def test_paso_4_5_logic():
    print("="*80)
    print("PRUEBA PASO 4.5: CLASIFICACIÓN DE TIPO DE LIBERACIÓN (CONT vs INST)")
    print("="*80)

    # 1. Datos de entrada (Simulados del PIPE-8 con tus resultados previos)
    dn_dict = {"small": 0.25, "medium": 1.0, "large": 4.0, "rupture": 8.0}
    
    wn_dict = {
        "small": 0.2375,   # lb/s
        "medium": 3.8007, 
        "large": 60.8117,  # > 55.6 -> Debería ser INSTANTANEOUS
        "rupture": 243.2470 # > 55.6 -> Debería ser INSTANTANEOUS
    }

    # Supongamos un inventario masivo (ej: 50,000 lb) para ver el efecto de la tasa
    mass_avail_dict = {
        "small": 31.52,
        "medium": 31.52,
        "large": 31.52,
        "rupture": 31.52
    }

    # 2. Ejecución
    resultados = compute_cof_4_5_release_types(
        dn_by_hole=dn_dict,
        wn_by_hole_lbm_s=wn_dict,
        mass_avail_by_hole_lbm=mass_avail_dict
    )

    # 3. Reporte
    print(f"\n{'HUECO':<10} | {'Wn (lb/s)':<10} | {'M_3min (lb)':<12} | {'TIPO':<15}")
    print("-" * 60)

    for hole, res in resultados.items():
        print(f"{hole.upper():<10} | {res.wn_lbm_s:<10.2f} | {res.mass_3min_lbm:<12.2f} | {res.release_type.value.upper():<15}")

    print("\n" + "="*80)
    print("VERIFICACIÓN: Large y Rupture deben ser INSTANTANEOUS por superar 55.6 lb/s.")
    print("="*80)

if __name__ == "__main__":
    test_paso_4_5_logic()