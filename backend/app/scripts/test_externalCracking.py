from datetime import date
from app.calculations.externalCracking_calc import ExternalCrackingInputs, compute_df_external_cracking

# def test_calculation_engine():
#     print("\n=== INICIANDO TEST DE AGRIETAMIENTO EXTERNO (API 581) ===\n")

#     # CASO 1: Atmosférico - 150°F, Moderate -> Medium [cite: 105]
#     case_1 = ExternalCrackingInputs(
#         mechanism="581-Austenitic Component Atmospheric Cracking",
#         susceptibility_type="Calculated",
#         temp_op=150, 
#         driver="Moderate",
#         calculation_date=date(2024, 1, 1),
#         last_insp_date=date(2019, 1, 1), 
#         coating_install_date=date(2019, 1, 1),
#         anticipated_coating_life=0,
#         coating_present=False,
#         highest_effectiveness="E",
#         number_of_inspections=0
#     )
    
#     # CASO 2: CUI - 150°F, Moderate -> High [cite: 246] -> Adj: Medium
#     case_2 = ExternalCrackingInputs(
#         mechanism="581-Austenitic Component Cracking Under Insulation",
#         susceptibility_type="Calculated",
#         temp_op=250,
#         driver="Moderate",
#         complexity="Average", 
#         insulation="Average",
#         chloride_free=False,
#         calculation_date=date(2024, 1, 1),
#         last_insp_date=date(2023, 1, 1),
#         coating_install_date=date(2023, 1, 1),
#         anticipated_coating_life=0,
#         coating_present=True,
#         highest_effectiveness="B",
#         number_of_inspections=1
#     )

#     # CASO 3: Fuera de rango - 20°F -> None [cite: 105]
#     case_3 = ExternalCrackingInputs(
#         mechanism="581-Austenitic Component Atmospheric Cracking", 
#         susceptibility_type="Calculated",
#         temp_op=20, 
#         driver="Severe",
#         calculation_date=date(2024, 1, 1),
#         last_insp_date=date(2010, 1, 1),
#         coating_install_date=date(2010, 1, 1),
#         anticipated_coating_life=0,
#         coating_present=True,
#         highest_effectiveness="E",
#         number_of_inspections=0
#     )

#     for i, case in enumerate([case_1, case_2, case_3], 1):
#         try:
#             res = compute_df_external_cracking(case)
#             print(f"TEST {i} ({case.mechanism}):")
#             print(f"  - Tipo Susceptibilidad: {res['trace']['step_1']['susceptibility']}")
#             print(f"  - Susceptibilidad: {res['trace']['step_1']['susceptibility']}")
#             print(f"  - SVI: {res['trace']['step_2']['SVI']}")
#             print(f"  - Edad efectiva (age): {res['trace']['steps_3_7']['eff_age']}")
#             print(f"  - DF Base: {res['dfb_cracking']}")
#             print(f"  - DF Final: {res['df_cracking']}\n")
#         except Exception as e:
#             print(f"TEST {i} FALLÓ: {e}")

# if __name__ == "__main__":
#     test_calculation_engine()

def test_calculation_engine():
    print("\n=== INICIANDO TEST DE AGRIETAMIENTO EXTERNO (FIXED ARGS) ===\n")

    # CASO 1: Atmosférico
    case_1 = ExternalCrackingInputs(
        mechanism="581-Austenitic Component Atmospheric Cracking",
        susceptibility_type="Calculated", # Tipo calculado
        susceptibility=None,           # Valor por defecto inicial
        coating_quality="Medium",        # Nuevo campo obligatorio
        temp_op=150, 
        driver="Moderate",
        calculation_date=date(2024, 1, 1),
        last_insp_date=date(2019, 1, 1), 
        coating_install_date=date(2019, 1, 1),
        anticipated_coating_life=0
    )
    
    # CASO 2: CUI
    case_2 = ExternalCrackingInputs(
        mechanism="581-Austenitic Component Cracking Under Insulation",
        susceptibility_type="Calculated",
        susceptibility=None,          # Agregado
        coating_quality="High",          # Agregado
        temp_op=250,
        driver="Moderate",
        calculation_date=date(2024, 1, 1),
        last_insp_date=date(2023, 1, 1),
        coating_install_date=date(2023, 1, 1),
        anticipated_coating_life=0
    )

    # CASO 3: Fuera de rango
    case_3 = ExternalCrackingInputs(
        mechanism="581-Austenitic Component Atmospheric Cracking", 
        susceptibility_type="Calculated",
        susceptibility=None,          # Agregado
        coating_quality="No coating or primer only", # Agregado
        temp_op=20, 
        driver="Severe",
        calculation_date=date(2024, 1, 1),
        last_insp_date=date(2010, 1, 1),
        coating_install_date=date(2010, 1, 1),
        anticipated_coating_life=0
    )

    # CASO 3: Fuera de rango
    case_4 = ExternalCrackingInputs(
        mechanism="581-Austenitic Component Atmospheric Cracking", 
        susceptibility_type="Estimated",          
        susceptibility="High",          
        coating_quality="No coating or primer only", # Agregado
        temp_op=20, 
        driver="Severe",
        calculation_date=date(2024, 1, 1),
        last_insp_date=date(2010, 1, 1),
        coating_install_date=date(2010, 1, 1),
        anticipated_coating_life=0
    )

    # Ejecución de los tests...
    for i, case in enumerate([case_1, case_2, case_3, case_4], 1):
        try:
            res = compute_df_external_cracking(case)
            print(f"TEST {i} ({case.mechanism}): Susceptibilidad: {res['trace']['step_1']['susceptibility']} | DF: {res['df_cracking']}")
        except Exception as e:
            print(f"TEST {i} FALLÓ: {e}")

if __name__ == "__main__":
    test_calculation_engine()