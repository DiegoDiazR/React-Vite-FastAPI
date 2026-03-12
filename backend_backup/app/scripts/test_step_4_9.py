import pprint
# from app.calculations.cof_4_9_toxic_consequence import (
#     compute_toxic_for_hole, ToxicInputs, ReleaseType
# )

from app.calculations.cof_4_9_toxic_consequence import compute_step_4_9_total, ReleaseType

def print_toxic_audit_report(result: dict):
    print("\n" + "="*115)
    print(f"REPORTE DE AUDITORÍA TÓXICA: {result['chemical'].upper()}")
    print("="*115)

    if not result['applies']:
        print(f"ESTADO: NO APLICA")
        print(f"RAZÓN:  {result.get('message', 'N/A')}")
        print("="*115)
        return

    # Encabezado ajustado para incluir las constantes
    header = f"{'TAMAÑO':<8} | {'TIPO':<13} | {'RATE TOX':<10} | {'MASS TOX':<10} | {'DUR(m)':<6} | {'CONSTANTES (Interp.)':<30} | {'ÁREA (ft²)':<12}"
    print(header)
    print("-" * 115)

    # Iteramos sobre los resultados individuales
    per_hole = result.get('per_hole', {})
    order = ['small', 'medium', 'large', 'rupture']
    
    for size in order:
        if size in per_hole:
            r = per_hole[size]
            dur_min = r.ld_tox_s / 60.0
            
            # Formatear las constantes para que se vean bien (c,d o e,f)
            const_str = ""
            if "c" in r.used_constants:
                const_str = f"c={r.used_constants['c']:.3f}, d={r.used_constants['d']:.3f}"
            elif "e" in r.used_constants:
                # e suele ser grande, usamos formato .1f o .0f
                const_str = f"e={r.used_constants['e']:.1f}, f={r.used_constants['f']:.3f}"
            else:
                const_str = str(r.used_constants)

            print(f"{size.upper():<8} | {r.release_type.value:<13} | {r.rate_tox_lbm_s:<10.4f} | {r.mass_tox_lbm:<10.2f} | {dur_min:<6.1f} | {const_str:<30} | {r.CA_tox_inj:<12.2f}")

    print("-" * 115)
    print(f"ÁREA TÓXICA FINAL PONDERADA (CA_tox): {result['CA_tox_inj_final']:.2f} ft²")
    print("="*115)


def run_test_suite():
    # ---------------------------------------------------------
    # 1. DATOS SIMULADOS (Lo que entregaría el Paso 4.7)
    # ---------------------------------------------------------
    # Estos valores deben coincidir con tu Excel para validar.
    # Ejemplo: Tubería 8" (PIPE-8)
    holes_data = {
        "small": {
            "Wn_lbm_s": 0.23, 
            "mass_n_lbm": 12.81, 
            "release_type": ReleaseType.CONTINUOUS
        },
        "medium": {
            "Wn_lbm_s": 3.79, 
            "mass_n_lbm": 31.5, 
            "release_type": ReleaseType.CONTINUOUS
        },
        "large": {
            "Wn_lbm_s": 60.71, 
            "mass_n_lbm": 31.5, 
            "release_type": ReleaseType.INSTANTANEOUS
        },
        "rupture": {
            "Wn_lbm_s": 242.86, 
            "mass_n_lbm": 31.5, 
            "release_type": ReleaseType.INSTANTANEOUS
        }
    }

    # Frecuencias de falla (Generic Failure Frequencies)
    gff = {"small": 8e-6, "medium": 2e-5, "large": 2e-6, "rupture": 6e-7}
    
    # Tiempo máximo de aislamiento (minutos)
    ld_max = 60.0

    # ---------------------------------------------------------
    # 2. CASO A: H2S (Debe calcular)
    # ---------------------------------------------------------
    # Supongamos una mezcla con 5% de H2S (fracción masa = 0.05)
    res_h2s = compute_step_4_9_total(
        chemical="HF",
        mfrac_tox=0.05, 
        holes_data=holes_data,
        gff_by_hole=gff,
        ldmax_n_min=ld_max
    )
    print_toxic_audit_report(res_h2s)

    # ---------------------------------------------------------
    # 3. CASO B: AMONÍACO (Debe calcular con otra fórmula)
    # ---------------------------------------------------------
    # Supongamos Amoníaco puro (fracción = 1.0)
    res_nh3 = compute_step_4_9_total(
        chemical="H2S",
        mfrac_tox=1.0, 
        holes_data=holes_data,
        gff_by_hole=gff,
        ldmax_n_min=ld_max
    )
    print_toxic_audit_report(res_nh3)

    # ---------------------------------------------------------
    # 4. CASO C: AGUA / PROPANO (No debe aplicar)
    # ---------------------------------------------------------
    res_water = compute_step_4_9_total(
        chemical="Water",
        mfrac_tox=0.0, 
        holes_data=holes_data,
        gff_by_hole=gff,
        ldmax_n_min=ld_max
    )
    print_toxic_audit_report(res_water)

if __name__ == "__main__":
    run_test_suite()