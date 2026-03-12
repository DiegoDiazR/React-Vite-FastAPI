from app.calculations.cof_4_11_damage_injury_areas import (
    compute_cof_4_11_damage_injury_areas,
    ConsequenceAreasByMechanism
)

def run_test_4_11():
    print("="*60)
    print("TEST SECTION 4.11: FINAL CONSEQUENCE AREA")
    print("="*60)

    # Scenario 1: Dominant Toxic Injury
    # Flammable creates damage (cmd) but Toxic creates larger injury area.
    case_1 = ConsequenceAreasByMechanism(
        caf_cmd_flam=500.0,  # Flammable Damage
        caf_inj_flam=200.0,  # Flammable Injury
        caf_inj_tox=1500.0,  # Toxic Injury (Dominant)
        caf_inj_nfnt=0.0
    )
    
    res_1 = compute_cof_4_11_damage_injury_areas(case_1)
    
    print(f"CASE 1 (Toxic Dominant):")
    print(f"  Inputs: CMD_Flam={case_1.caf_cmd_flam}, INJ_Tox={case_1.caf_inj_tox}")
    print(f"  Result CA_cmd (Eq 3.79): {res_1.caf_cmd} (Expected 500.0)")
    print(f"  Result CA_inj (Eq 3.80): {res_1.caf_inj} (Expected 1500.0)")
    print(f"  Result CA_final (Eq 3.81): {res_1.caf} (Expected 1500.0)")
    print("-" * 60)

    # Scenario 2: Dominant Flammable Damage
    # Flammable Damage is massive (e.g., rupture), larger than injury.
    case_2 = ConsequenceAreasByMechanism(
        caf_cmd_flam=121.90, # Massive equipment damage
        caf_inj_flam=299.04,
        caf_inj_tox=100.0,
        caf_inj_nfnt=0.0
    )
    
    res_2 = compute_cof_4_11_damage_injury_areas(case_2)

    print(f"CASE 2 (Flammable Damage Dominant):")
    print(f"  Inputs: CMD_Flam={case_2.caf_cmd_flam}, INJ_Flam={case_2.caf_inj_flam}")
    print(f"  Result CA_cmd:   {res_2.caf_cmd} (Expected 2000.0)")
    print(f"  Result CA_inj:   {res_2.caf_inj} (Expected 800.0)")
    print(f"  Result CA_final: {res_2.caf} (Expected 2000.0)")
    print("=" * 60)

if __name__ == "__main__":
    run_test_4_11()