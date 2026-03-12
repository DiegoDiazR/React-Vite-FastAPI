from app.calculations.cof_4_13_safety_consequence import (
    compute_cof_4_13_safety_consequence,
    SafetyConsequenceInputs,
    StaffingCase
)

def run_test_4_13():
    print("="*60)
    print("AUDIT: SECTION 4.13 SAFETY CONSEQUENCE")
    print("="*60)

    # ---------------------------------------------------------
    # Scenario Data
    # ---------------------------------------------------------
    # Example:
    # - 5 Operators present 100% of the time (24/7 coverage)
    # - 10 Maintenance staff present 25% of the time (day shift only)
    # - Unit Area (Area_safety): 40,000 ft^2
    # - Injury Area (CA_f_inj from 4.11): 8,000 ft^2
    
    staffing_list = [
        StaffingCase(pers_count=5.0, present_pct=100.0),
        StaffingCase(pers_count=10.0, present_pct=25.0)
    ]

    inp = SafetyConsequenceInputs(
        ca_f_inj_area=8_000.0,
        area_safety=40_000.0,
        staffing=staffing_list
    )

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------
    res = compute_cof_4_13_safety_consequence(inp)

    # ---------------------------------------------------------
    # Manual Validation
    # ---------------------------------------------------------
    # Pers_avg = (5*100 + 10*25) / 100 = (500 + 250)/100 = 7.5 people
    # Pop_dens = 7.5 / 40,000 = 0.0001875 people/ft^2
    # C_f_inj  = 8,000 * 0.0001875 = 1.5 people

    print(f"{'METRIC':<25} | {'VALUE':<15}")
    print("-" * 45)
    print(f"{'CA_f_inj (Input)':<25} | {inp.ca_f_inj_area:,.2f} ft²")
    print(f"{'Area_safety (Input)':<25} | {inp.area_safety:,.2f} ft²")
    print(f"{'Pers_avg (Calculated)':<25} | {res.pers_avg:.4f} people")
    print(f"{'Pop_dens (Calculated)':<25} | {res.popdens:.8f} people/ft²")
    print("-" * 45)
    print(f"{'FINAL C_f_inj':<25} | {res.c_f_inj:.4f} people")
    print("="*60)

if __name__ == "__main__":
    run_test_4_13()