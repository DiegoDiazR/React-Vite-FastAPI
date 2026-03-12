import pprint
from app.calculations.cof_4_0_orchestrator import COFCalculator, COFScenarioInputs
from app.calculations.cof_4_6_detec_isola_impact import Rating

# def print_separator(step_name: str):
#     print("\n" + "="*95)
#     print(f"VERIFICACIÓN ACUMULATIVA: {step_name}")
#     print("="*95)


# def test_full_flammable_consequence():
#     print_separator("PASO 4.8: CONSECUENCIA INFLAMABLE FINAL (INTEGRADO)")
    
#     inputs = COFScenarioInputs(
#         fluid_name="C3-C4", 
#         stored_phase="Gas", # Gas
#         temperature_k=300.0,
#         component_type="PIPE-8", 
#         component_family="Piping",
#         diameter_in=8, 
#         length_ft=1, 
#         length_circuit_ft=2.625,
#         pressure_gauge_psi=180.0, 
#         patm_psi=12.5,
#         detection_rating=Rating.C, 
#         isolation_rating=Rating.B,
#         mitigation_system_key="fire_water_deluge_and_monitors",
#         toxic_mfrac=0.1
#     )
    
#     calc = COFCalculator(inputs)
    
#     # Cadena completa
#     calc.execute_step_4_1()
#     calc.execute_step_4_2()
#     calc.execute_step_4_3()
#     calc.execute_step_4_4()
#     calc.execute_step_4_5()
#     calc.execute_step_4_6()
#     calc.execute_step_4_7()
    
#     # Ahora el execute_step_4_8 no debería fallar por llaves
#     res_4_8 = calc.execute_step_4_8()
#     res_4_9 = calc.execute_step_4_9() # Tóxico
#     res_4_10 = calc.execute_step_4_10()
#     res_4_11 = calc.execute_final_consequence()
    
#     print(f"Resultado para {res_4_8.fluid}:")
#     print(f"  CA_flam_cmd_final: {res_4_8.CA_cmd_final:,.2f} ft²")
#     print(f"  CA_flam_inj_final: {res_4_8.CA_inj_final:,.2f} ft²")
#     print(f"  CA_tox_inj_final: {res_4_9['CA_tox_inj_final']:,.2f} ft²")
#     print(f"  CA_nfnt_inj_final: {res_4_10.CA_nfnt_inj_final:.2f} ft²")

       
#     print("\nLogs del Orquestador:")
#     for log in calc.logs[-3:]: # Ver últimos logs
#         print(f"  [LOG] {log}")

# if __name__ == "__main__":
#     test_full_flammable_consequence()


# def print_header(title):
#     print("\n" + "="*80)
#     print(f" {title}")
#     print("="*80)

# def run_test_case(title, inputs):
#     print_header(title)
#     calc = COFCalculator(inputs)
    
#     try:
#         # --- 1. FÍSICA DE LA FUGA (Pasos 4.1 - 4.7) ---
#         print(">>> Ejecutando Física (4.1 - 4.7)...")
#         calc.execute_step_4_1()
#         calc.execute_step_4_2()
#         calc.execute_step_4_3()
#         calc.execute_step_4_4()
#         calc.execute_step_4_5()
#         calc.execute_step_4_6()
#         calc.execute_step_4_7()
        
#         # --- 2. CONSECUENCIAS POR MECANISMO (Pasos 4.8 - 4.10) ---
#         print(">>> Ejecutando Consecuencias (4.8 - 4.10)...")
        
#         # 4.8 Inflamable
#         res_4_8 = calc.execute_step_4_8()
#         val_flam_cmd = res_4_8.CA_cmd_final
#         val_flam_inj = res_4_8.CA_inj_final
        
#         # 4.9 Tóxico
#         res_4_9 = calc.execute_step_4_9()
#         val_tox_inj = res_4_9.get('CA_tox_inj_final', 0.0)
        
#         # 4.10 NFNT
#         res_4_10 = calc.execute_step_4_10()
#         val_nfnt_inj = getattr(res_4_10, 'CA_nfnt_inj_final', 0.0)
#         val_nfnt_cmd = getattr(res_4_10, 'CA_nfnt_cmd_final', 0.0)
        
#         # --- 3. ARBITRAJE FINAL (Paso 4.11) ---
#         print(">>> Ejecutando Arbitraje Final (4.11)...")
#         final = calc.execute_final_consequence()
        
#         # --- REPORTE ---
#         print("\n" + "-"*40)
#         print(f" RESULTADOS PARA: {inputs.fluid_name}")
#         print("-"*40)
#         print(f" 1. INFLAMABLE (4.8)")
#         print(f"    - Daño Equipos:   {val_flam_cmd:10,.2f} ft²")
#         print(f"    - Lesión Pers.:   {val_flam_inj:10,.2f} ft²")
        
#         print(f" 2. TÓXICO (4.9)")
#         print(f"    - Lesión Pers.:   {val_tox_inj:10,.2f} ft²")
        
#         print(f" 3. NFNT (4.10)")
#         print(f"    - Lesión Pers.:   {val_nfnt_inj:10,.2f} ft²")
        
#         print("-" * 40)
#         print(f" ÁREA FINAL (COF):   {final['final_cof_area_ft2']:10,.2f} ft²")
#         print(f" ESCENARIO DOMINANTE: {final['dominant_scenario']}")
#         print("-" * 40)
        
#         return True

#     except Exception as e:
#         print(f"\n❌ ERROR CRÍTICO EN {inputs.fluid_name}:")
#         print(f"   {e}")
#         # Opcional: imprimir logs para depurar
#         # for log in calc.logs: print(f"   [LOG] {log}")
#         import traceback
#         traceback.print_exc()
#         return False

# def test_unified_logic():
#     print("INICIANDO BATERÍA DE PRUEBAS API 581 COF NIVEL 1")

#     # ---------------------------------------------------------
#     # CASO 1: INFLAMABLE PURO (C5 - Pentano)
#     # ---------------------------------------------------------
#     # Objetivo: Verificar que 4.8 domina y 4.9/4.10 son ignorados.
#     inp_c5 = COFScenarioInputs(
#         fluid_name="C3-C4", 
#         stored_phase="Gas", # Gas
#         temperature_k=300.0,
#         component_type="PIPE-2", 
#         component_family="Piping",
#         diameter_in=2, 
#         length_ft=2.625, 
#         length_circuit_ft=2.625,
#         pressure_gauge_psi=180.0, 
#         patm_psi=12.5,
#         detection_rating=Rating.C, 
#         isolation_rating=Rating.B,
#         mitigation_system_key="fire_water_deluge_and_monitors",
#         toxic_mfrac=0.0
#     )
#     run_test_case("CASO 1: Propano (Inflamable)", inp_c5)

#     # ---------------------------------------------------------
#     # CASO 2: TÓXICO + INFLAMABLE (H2S)
#     # ---------------------------------------------------------
#     # Objetivo: H2S quema Y es tóxico. El área tóxica suele ser mayor.
#     inp_h2s = COFScenarioInputs(
#         fluid_name="HF", stored_phase="Gas", temperature_k=300.0,
#         component_type="PIPE-8", component_family="Piping",
#         diameter_in=8.0, length_ft=50.0, length_circuit_ft=500.0,
#         pressure_gauge_psi=100.0, patm_psi=14.7,
#         mitigation_system_key="none", toxic_mfrac=1.0 # 100% puro
#     )
#     run_test_case("CASO 2: H2S (Tóxico Dominante)", inp_h2s)

#     # ---------------------------------------------------------
#     # CASO 3: TÓXICO EXPONENCIAL (Amoniaco)
#     # ---------------------------------------------------------
#     # Objetivo: Verificar que la corrección de OverflowError funciona.
#     inp_nh3 = COFScenarioInputs(
#         fluid_name="Ammonia", stored_phase="Liquid", temperature_k=300.0,
#         component_type="PIPE-8", component_family="Piping",
#         diameter_in=8.0, length_ft=50.0, length_circuit_ft=500.0,
#         pressure_gauge_psi=100.0, patm_psi=14.7,
#         mitigation_system_key="none", toxic_mfrac=1.0
#     )
#     run_test_case("CASO 3: AMONIACO (Tóxico Exponencial)", inp_nh3)

#     # ---------------------------------------------------------
#     # CASO 4: TÓXICO MISC (CO)
#     # ---------------------------------------------------------
#     # Objetivo: Verificar corrección de fase y MiscEF (sin números infinitos).
#     inp_co = COFScenarioInputs(
#         fluid_name="CO", stored_phase="Gas", temperature_k=300.0,
#         component_type="PIPE-8", component_family="Piping",
#         diameter_in=8.0, length_ft=50.0, length_circuit_ft=500.0,
#         pressure_gauge_psi=100.0, patm_psi=14.7,
#         mitigation_system_key="none", toxic_mfrac=1.0
#     )
#     run_test_case("CASO 4: MONÓXIDO DE CARBONO (Misc)", inp_co)

#     # ---------------------------------------------------------
#     # CASO 5: NFNT TÉRMICO (Vapor de Agua)
#     # ---------------------------------------------------------
#     # Objetivo: 4.8 y 4.9 deben ser 0. 4.10 debe calcular.
#     inp_steam = COFScenarioInputs(
#         fluid_name="Steam", stored_phase="Gas", temperature_k=450.0,
#         component_type="PIPE-8", component_family="Piping",
#         diameter_in=8.0, length_ft=50.0, length_circuit_ft=500.0,
#         pressure_gauge_psi=600.0, patm_psi=14.7,
#         mitigation_system_key="none", toxic_mfrac=0.0
#     )
#     run_test_case("CASO 5: VAPOR (NFNT Térmico)", inp_steam)

#     # ---------------------------------------------------------
#     # CASO 6: NFNT QUÍMICO (Ácido)
#     # ---------------------------------------------------------
#     # Objetivo: 4.8 y 4.9 deben ser 0. 4.10 debe calcular.
#     inp_acid = COFScenarioInputs(
#         fluid_name="Acid/caustic-LP", stored_phase="Liquid", temperature_k=300.0,
#         component_type="PIPE-8", component_family="Piping",
#         diameter_in=8.0, length_ft=50.0, length_circuit_ft=500.0,
#         pressure_gauge_psi=50.0, patm_psi=14.7,
#         mitigation_system_key="none", toxic_mfrac=0.0
#     )
#     run_test_case("CASO 6: ÁCIDO (NFNT Químico)", inp_acid)

# if __name__ == "__main__":
#     test_unified_logic()

# #########################################################

# # --- CONFIGURACIÓN ECONÓMICA ESTÁNDAR PARA LAS PRUEBAS ---
# ECON_DEFAULTS = {
#     "material_cost_factor": 1.0,
#     "material": "Carbon Steel",      # Debe coincidir con keys de Table 4.16
#     "equipment_cost_ft2": 550,       # $100 USD/ft2 costo reemplazo
#     "production_cost_day": 331742.2, # $50k USD/día por paro
#     "population_density": 1.328E-05, # Pers/ft2
#     "injury_cost_person": 500000,    # $1M USD por lesión
#     "environmental_cost_bbl": 0.0,   # $5k USD por barril derramado
#     "outage_multiplier": 1.0         # Factor de seguridad en tiempo de paro
# }

# def print_header(title):
#     print("\n" + "="*80)
#     print(f" {title}")
#     print("="*80)

# def run_test_case(title, inputs):
#     print_header(title)
#     calc = COFCalculator(inputs)
    
#     try:
#         # --- EJECUCIÓN SECUENCIAL ---
#         print(">>> 1. Calculando Física (4.1 - 4.7)...")
#         calc.execute_step_4_1() # Props
#         calc.execute_step_4_2() # Holes (Aquí se arregló el min(D, dn))
#         calc.execute_step_4_3() # Rates (Aquí se calculan los flujos)
#         calc.execute_step_4_4() # Inventory
#         calc.execute_step_4_5() # Type (Cont/Inst)
#         calc.execute_step_4_6() # Detection
#         calc.execute_step_4_7() # Mass Final
        
#         print(">>> 2. Calculando Áreas de Consecuencia (4.8 - 4.11)...")
#         # Dependiendo del fluido, ejecutamos lo que corresponda
#         calc.execute_step_4_8() # Flammable
#         calc.execute_step_4_9() # Toxic
#         calc.execute_step_4_10() # NFNT
        
#         # Arbitraje Final de Áreas
#         areas = calc.execute_final_consequence()
        
#         print(">>> 3. Calculando Consecuencia Financiera (4.12)...")
#         fin = calc.execute_step_4_12()
        
#         # --- REPORTE DE RESULTADOS ---
#         print("\n" + "-"*40)
#         print(f" RESUMEN: {inputs.fluid_name} en {inputs.component_type}")
#         print("-" * 40)
        
#         # Validación de Corrección de Diámetros (Caso PIPE-2)
#         print(f" [DEBUG] Diámetro Ruptura Usado: {calc.step_4_2_result.dn_in.get('rupture', 0):.2f} in")
        
#         print("-" * 40)
#         print(" ÁREAS DE CONSECUENCIA (ft²):")
#         print(f"  > Daño Componentes:      {areas['final_cmd_area_ft2']:10,.2f} ft²")
#         print(f"  > Lesión Personal:       {areas['final_inj_area_ft2']:10,.2f} ft²")
#         print(f"  > Área Final COF:        {areas['final_cof_area_ft2']:10,.2f} ft²")
        
#         print("-" * 40)
#         print(" CONSECUENCIA FINANCIERA ($ USD):")
#         print(f"  > Daño Equipos (CMD):    ${fin.FC_f_cmd:12,.2f}")
#         print(f"  > Equipos Vecinos (AFFA):${fin.FC_f_affa:12,.2f}")
#         print(f"  > Pérdida Producción:    ${fin.FC_f_prod:12,.2f} (Días: {fin.outage_cmd_days:.1f})")
#         print(f"  > Lesiones (INJ):        ${fin.FC_f_inj:12,.2f}")
#         print(f"  > Limpieza Ambiental:    ${fin.FC_f_environ:12,.2f}")
#         print("  " + "."*35)
#         print(f"  > TOTAL FINANCIAL COF:   ${fin.FC_f_total:12,.2f}")
#         print("=" * 80)
        
#         return True

#     except Exception as e:
#         print(f"\n❌ ERROR CRÍTICO EN {inputs.fluid_name}:")
#         print(f"   {e}")
#         import traceback
#         traceback.print_exc()
#         return False

# def test_unified_logic():
#     print("INICIANDO PRUEBAS DEL MOTOR COF API 581 (COMPLETO)")

#     # ---------------------------------------------------------
#     # CASO 1: TUBERÍA GRANDE (PIPE-8) con C6-C8
#     # Objetivo: Probar flujo normal + Costo Ambiental
#     # ---------------------------------------------------------
#     inp_1 = COFScenarioInputs(
#         fluid_name="C6-C8", stored_phase="Liquid", temperature_k=300.0,
#         component_type="PIPE-8", component_family="Piping",
#         diameter_in=8.0, length_ft=100.0, length_circuit_ft=500.0,
#         pressure_gauge_psi=100.0, patm_psi=14.7,
#         mitigation_system_key="none", toxic_mfrac=0.0,
#         **ECON_DEFAULTS # Inyectamos datos económicos
#     )
#     run_test_case("CASO 1: PIPE-8 (Normal + Ambiental)", inp_1)

#     # ---------------------------------------------------------
#     # CASO 2: TUBERÍA PEQUEÑA (PIPE-2) con Propano (C3-C4)
#     # Objetivo: VERIFICAR CORRECCIÓN DE RUPTURA (dn=D)
#     # Antes fallaba porque Rupture era 0.0. Ahora debe ser 2.0.
#     # ---------------------------------------------------------
#     inp_2 = COFScenarioInputs(
#         fluid_name="C3-C4", 
#         stored_phase="Gas", # Gas
#         temperature_k=300.0,
#         component_type="PIPE-8", 
#         component_family="Piping",
#         diameter_in=8, 
#         length_ft=2.625, 
#         length_circuit_ft=2.625,
#         pressure_gauge_psi=180.0, 
#         patm_psi=12.5,
#         detection_rating=Rating.C, 
#         isolation_rating=Rating.B,
#         mitigation_system_key="fire_water_deluge_and_monitors",
#         toxic_mfrac=0.0,
#         **ECON_DEFAULTS
#     )
#     run_test_case("CASO 2: PIPE-8", inp_2)

#     # ---------------------------------------------------------
#     # CASO 3: TÓXICO (H2S)
#     # Objetivo: Verificar que suma costos de lesión tóxica
#     # ---------------------------------------------------------
#     inp_3 = COFScenarioInputs(
#         fluid_name="H2S", stored_phase="Gas", temperature_k=310.0,
#         component_type="PIPE-4", component_family="Piping",
#         diameter_in=4.0, length_ft=50.0, length_circuit_ft=200.0,
#         pressure_gauge_psi=100.0, patm_psi=14.7,
#         mitigation_system_key="none", 
#         detection_rating=Rating.C, 
#         isolation_rating=Rating.B,
#         # mitigation_system_key="fire_water_deluge_and_monitors",
#         toxic_mfrac=0.5,
#         **ECON_DEFAULTS
#     )
#     run_test_case("CASO 3: H2S (Tóxico)", inp_3)

# if __name__ == "__main__":
#     test_unified_logic()


#########################################################

# --- CONFIGURACIÓN ECONÓMICA ESTÁNDAR PARA LAS PRUEBAS ---
ECON_DEFAULTS = {
    "material_cost_factor": 1.0,
    "material": "Carbon Steel",      # Debe coincidir con keys de Table 4.16
    "equipment_cost_ft2": 550,       # $100 USD/ft2 costo reemplazo
    "production_cost_day": 331742.2, # $50k USD/día por paro
    # "population_density": 1.328E-05, # Pers/ft2
    "injury_cost_person": 500000,    # $1M USD por lesión
    "environmental_cost_bbl": 0.0,   # $5k USD por barril derramado
    "outage_multiplier": 1.0         # Factor de seguridad en tiempo de paro
}

def print_header(title):
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def run_test_case(title, inputs):
    print_header(title)
    calc = COFCalculator(inputs)
    
    try:
        # SECUENCIA COMPLETA 4.1 -> 4.13
        print(">>> 1. Física (4.1 - 4.7)...")
        calc.execute_step_4_1()
        calc.execute_step_4_2()
        calc.execute_step_4_3()
        calc.execute_step_4_4()
        calc.execute_step_4_5()
        calc.execute_step_4_6()
        calc.execute_step_4_7()
        
        print(">>> 2. Áreas (4.8 - 4.11)...")
        calc.execute_step_4_8()
        calc.execute_step_4_9()
        calc.execute_step_4_10()
        areas = calc.execute_final_consequence()
        
        print(">>> 3. Financiero (4.12)...")
        fin = calc.execute_step_4_12()
        
        print(">>> 4. Seguridad Final (4.13)...")
        safe = calc.execute_step_4_13()
        
        # --- REPORTE FINAL ---
        print("\n" + "-"*40)
        print(f" RESUMEN GLOBAL: {inputs.fluid_name}")
        print("-" * 40)
        
        print(" MÉTRICAS CLAVE:")
        print(f"  > Área Final COF:        {areas['final_cof_area_ft2']:10,.2f} ft²")
        print(f"  > Costo Total ($):       ${fin.FC_f_total:10,.2f}")
        print(f"  > Impacto Personas:      {safe.c_f_inj:10.4f} personas")
        print(f"    (Densidad Calc: {safe.popdens:.6f} pers/ft²)")
        
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_logic():
    print("INICIANDO PRUEBAS DEL MOTOR COF API 581 (COMPLETO)")

    # ---------------------------------------------------------
    # CASO 1: TUBERÍA GRANDE (PIPE-8) con C6-C8
    # Objetivo: Probar flujo normal + Costo Ambiental
    # ---------------------------------------------------------
    inp_1 = COFScenarioInputs(
        fluid_name="C6-C8", stored_phase="Liquid", temperature_k=300.0,
        component_type="PIPE-8", component_family="Piping",
        diameter_in=8.0, length_ft=100.0, length_circuit_ft=500.0,
        pressure_gauge_psi=100.0, patm_psi=14.7,
        mitigation_system_key="none", toxic_mfrac=0.0,
        unit_area_ft2=150608.0,  # Área de la unidad para calcular densidad
        personnel_count = 2,     # Número de personas promedio
        personnel_presence_pct = 100.0, # Porcentaje de tiempo presentes
        **ECON_DEFAULTS # Inyectamos datos económicos
    )
    run_test_case("CASO 1: PIPE-8 (Normal + Ambiental)", inp_1)

    # ---------------------------------------------------------
    # CASO 2: TUBERÍA PEQUEÑA (PIPE-2) con Propano (C3-C4)
    # Objetivo: VERIFICAR CORRECCIÓN DE RUPTURA (dn=D)
    # Antes fallaba porque Rupture era 0.0. Ahora debe ser 2.0.
    # ---------------------------------------------------------
    inp_2 = COFScenarioInputs(
        fluid_name="C3-C4", 
        stored_phase="Gas", # Gas
        temperature_k=300.0,
        component_type="PIPE-8", 
        component_family="Piping",
        diameter_in=8, 
        length_ft=2.625, 
        length_circuit_ft=2.625,
        pressure_gauge_psi=180.0, 
        patm_psi=12.5,
        detection_rating=Rating.C, 
        isolation_rating=Rating.B,
        mitigation_system_key="fire_water_deluge_and_monitors",
        toxic_mfrac=0.0,
        
        unit_area_ft2=150608.0,  # Área de la unidad para calcular densidad
        personnel_count = 2,     # Número de personas promedio
        personnel_presence_pct = 100.0, # Porcentaje de tiempo presentes
        **ECON_DEFAULTS
    )
    run_test_case("CASO 2: PIPE-8", inp_2)

    # ---------------------------------------------------------
    # CASO 3: TÓXICO (H2S)
    # Objetivo: Verificar que suma costos de lesión tóxica
    # ---------------------------------------------------------
    inp_3 = COFScenarioInputs(
        fluid_name="H2S", stored_phase="Gas", temperature_k=310.0,
        component_type="PIPE-4", component_family="Piping",
        diameter_in=4.0, length_ft=50.0, length_circuit_ft=200.0,
        pressure_gauge_psi=100.0, patm_psi=14.7,
        mitigation_system_key="none", 
        detection_rating=Rating.C, 
        isolation_rating=Rating.B,
        # mitigation_system_key="fire_water_deluge_and_monitors",
        toxic_mfrac=0.5,
        unit_area_ft2=150608.0,  # Área de la unidad para calcular densidad
        personnel_count = 2,     # Número de personas promedio
        personnel_presence_pct = 100.0, # Porcentaje de tiempo presentes
        **ECON_DEFAULTS
    )
    run_test_case("CASO 3: H2S (Tóxico)", inp_3)

if __name__ == "__main__":
    test_unified_logic()