import pprint

from app.calculations.cof_4_10_nonflammable_nontoxic import (
    compute_nonflammable_nontoxic_for_hole,
    probability_weighted_nonflammable_area,
    NonFlamCategory,
    NonFlamHoleInputs,
    ReleaseType
)

def print_nonflam_audit(title: str, results: dict, final_ca: float):
    print("\n" + "="*100)
    print(f"AUDITORÍA 4.10: {title}")
    print("="*100)
    
    header = f"{'TAMAÑO':<10} | {'RATE (lb/s)':<12} | {'MASS (lb)':<10} | {'FACT IC':<8} | {'CA CONT':<10} | {'CA INST':<10} | {'CA LEAK':<10}"
    print(header)
    print("-" * 100)

    order = ['small', 'medium', 'large', 'rupture']
    
    for size in order:
        if size in results:
            r = results[size]['result']
            inp = results[size]['input']
            
            print(f"{size.upper():<10} | {inp.rate_n_lbm_s:<12.4f} | {inp.mass_n_lbm:<10.2f} | {r.fact_ic:<8.4f} | {r.CA_inj_cont:<10.2f} | {r.CA_inj_inst:<10.2f} | {r.CA_inj_leak:<10.2f}")

    print("-" * 100)
    print(f"ÁREA FINAL PONDERADA (CA_nfnt): {final_ca:.2f} ft²")
    print("="*100)


def run_test_4_10():
    # ---------------------------------------------------------
    # 1. DATOS DE ENTRADA SIMULADOS (Del Paso 4.7)
    # ---------------------------------------------------------
    holes_data = {
        "small":   NonFlamHoleInputs(rate_n_lbm_s=0.213, mass_n_lbm=12.807, release_type=ReleaseType.CONTINUOUS),
        "medium":  NonFlamHoleInputs(rate_n_lbm_s=3.415, mass_n_lbm=31.53, release_type=ReleaseType.CONTINUOUS),
        "large":   NonFlamHoleInputs(rate_n_lbm_s=54.644, mass_n_lbm=31.53, release_type=ReleaseType.INSTANTANEOUS),   # Rate < 55.6 (Transición)
        "rupture": NonFlamHoleInputs(rate_n_lbm_s=218.577, mass_n_lbm=31.53, release_type=ReleaseType.INSTANTANEOUS)  # Rate > 55.6 (Full Inst)
    }

    gff = {"small": 8e-6, "medium": 2e-5, "large": 2e-6, "rupture": 6e-7}
    gff_tot = sum(gff.values())

    # ---------------------------------------------------------
    # ESCENARIO A: VAPOR (STEAM)
    # ---------------------------------------------------------
    # NOTA: Aunque las constantes C9 y C10 ahora están "hardcodeadas" 
    # como 0.6 y 63.32 dentro de la función matemática, 
    # el sistema aún requiere el objeto SteamConstants para validar la llamada.
    
    
    res_steam = {}
    ca_map_steam = {}

    for size, inp in holes_data.items():
        res = compute_nonflammable_nontoxic_for_hole(
            category=NonFlamCategory.STEAM,
            hole=inp
        )
        res_steam[size] = {'result': res, 'input': inp}
        ca_map_steam[size] = res.CA_inj_leak

    final_steam = probability_weighted_nonflammable_area(
        ca_leak_by_hole=ca_map_steam,
        gff_by_hole=gff,
        gff_total=gff_tot
    )
    
    print_nonflam_audit("VAPOR DE AGUA (STEAM)", res_steam, final_steam)

    # ---------------------------------------------------------
    # ESCENARIO B: ÁCIDO / CÁUSTICO
    # ---------------------------------------------------------
    # Aquí SI se usan las constantes 'a' y 'b' pasadas.
    # Usaremos a=50, b=1 para verificar fácilmente (CA = 0.2 * 50 * Rate = 10 * Rate)
    # acid_consts = AcidCausticConstants(a=50.0, b=1.0)
    
    # ---------------------------------------------------------
    # ESCENARIO B: ÁCIDO / CÁUSTICO
    # ---------------------------------------------------------
    # CORRECCIÓN: Ya no pasamos un objeto de constantes manuales.
    # Pasamos el NOMBRE DEL FLUIDO para que el sistema busque en la Tabla 4.9 interna.
    fluid_for_test = "Acid/caustic-LP" 
    
    res_acid = {}
    ca_map_acid = {}

    for size, inp in holes_data.items():
        res = compute_nonflammable_nontoxic_for_hole(
            category=NonFlamCategory.ACID_CAUSTIC,
            hole=inp,
            fluid_name=fluid_for_test # <--- CAMBIO CLAVE: Usamos el nombre para el lookup
        )
        res_acid[size] = {'result': res, 'input': inp}
        ca_map_acid[size] = res.CA_inj_leak

    final_acid = probability_weighted_nonflammable_area(
        ca_leak_by_hole=ca_map_acid,
        gff_by_hole=gff,
        gff_total=gff_tot
    )

    print_nonflam_audit(f"ÁCIDO ({fluid_for_test})", res_acid, final_acid)

if __name__ == "__main__":
    run_test_4_10()