from datetime import date
from app.calculations.externalDamage_calc_df import CUIInputs, CUIInspectionEffectiveness, compute_df_cui
from app.calculations.externalDamage_presets import (
    get_cui_base_rate, 
    build_cui_adjustment_factors, 
    build_cui_probabilities
)

def run_full_cui_test():
    print("=== TEST DE CÁLCULO INTEGRAL CUI (API 581) ===")

    # --- CONFIGURACIÓN DE PARÁMETROS DE ENTRADA ---
    damage_mechanism = "581-Ferritic Component Corrosion UnderInsulation" #"581-Ferritic Component Atmospheric Corrosion" "581-Ferritic Component Corrosion UnderInsulation"

    ext_corrosion_mod="Calculated"  # Usamos la tasa medida para validar el ajuste
    measured_crate=0.00    # Tasa medida en 201

    thinning_type = "General" # "General", "Localized", "Pitting"
    coating_quality = "Medium" # "None", "Medium", "High"

    # 1. Condiciones de Proceso y Entorno
    temp_operacion = 300    # °C
    driver = "Moderate"    # Según Tabla 2.D.3.2M
    
    # 2. Datos del Activo (Geometría y Material)
    t_original = 0.235     # mm (t)
    t_min_req = 0.110        # mm (tmin)
    espesor_estructural = 0.110 # mm (tc)
    wall_loss = 0.00         # mm (Le)
    
    yield_strength = 35  # MPa (YS)
    tensile_strength = 60 # MPa (TS)
    allowable_stress = 20 # MPa (S)
    joint_efficiency = 1.0   # (E)

    # 3. Fechas Críticas
    fecha_instalacion = date(1990, 1, 1)
    fecha_calculo = date(2023, 1, 1)
    fecha_coating = date(2010, 1, 1)    # El recubrimiento se renovó en 2010
    fecha_inspeccion = date(2018, 1, 1) # Última medición de espesor
    

    # --- PASOS DE INTEGRACIÓN USANDO PRESETS ---

    # Paso 3: Tasa Base (Interpolada)
    crb = get_cui_base_rate(temp_operacion, driver) # [cite: 17, 134]

    # Paso 4: Factores de Ajuste
    adj_factors = build_cui_adjustment_factors(
        dm_ext_dm=damage_mechanism,
        insulation_type="Unknown/unspecified",      # F_INS = 1.25 [cite: 141]
        complexity="Average",                       # F_CM = 1.0 [cite: 31]
        insulation_condition="Average",             # F_IC = 1.0 [cite: 38]
        pooling_design=False,                       # F_EQ = 1.0 [cite: 40]
        soil_water_interface=False                  # F_IF = 1.0 [cite: 41]
    )

    # Paso 14-16: Inspecciones y Probabilidades
    # Simulamos 1 inspección de Efectividad "B" (Cualitativa)
    cui_inspecciones = CUIInspectionEffectiveness( N_A= 1, N_B=1, N_C=0, N_D=0)
    cui_probs = build_cui_probabilities(confidence="medium")

    # --- EJECUCIÓN DEL CÁLCULO ---

    inputs = CUIInputs(
        dm_ext_dm = damage_mechanism,
        install_date=fecha_instalacion,
        calculation_date=fecha_calculo,
        coating_install_date=fecha_coating,
        last_thickness_date=fecha_inspeccion,

        ext_thinning_type=thinning_type,

        ext_coating_quality = coating_quality,

        select_ext_corrosion=ext_corrosion_mod,
        base_mat_measured_rate=measured_crate,

        t=t_original,
        t_rde_measured=0.323,   # Espesor medido en 2018
        tmin=t_min_req,
        tc=espesor_estructural,
        Le =wall_loss,
        
        CrB=crb,
        C_age=5.0,            # Vida estimada del recubrimiento (Cage) [cite: 55]
        coating_failed_at_insp=False,
        
        YS=yield_strength,
        TS=tensile_strength,
        S=allowable_stress,
        E=joint_efficiency,
        
        insp=cui_inspecciones,
        probs=cui_probs,
        factors=adj_factors
    )

    resultado = compute_df_cui(inputs)

    # --- SALIDA DE RESULTADOS ---
    if resultado["status"] == "ok":
        print(f"\nRESULTADOS PRINCIPALES:")
        print(f"------------------------------------")
        print(f"Mecanismo de Falla:           {resultado['step_1_to_4']['Damage_Mechanism']}")
        print(f"Tasa de Corrosión Selec.:     {resultado['step_1_to_4']['Tasa_Corr_Select']}")
        print(f"Tipo de Corrosión Externa:    {resultado['step_1_to_4']['External_Thinning_Type']}")
        print(f"Tasa de Corrosión Final (Cr): {resultado['step_1_to_4']['Cr_final']:.4f} pulg/y")
        print(f"Tiempo Total (age):           {resultado['step_1_to_4']['age_total']:.4f} años")

        print(f"Tiempo componente (age):      {resultado['step_5_to_9']['age_tke']:.2f} años")
        print(f"Tiempo recubrimiento (age):   {resultado['step_5_to_9']['age_coat']:.2f} años")
        print(f"Calidad de Recubrimiento:     {resultado['step_5_to_9']['coat_qty']}")
        print(f"Ajuste recubrimiento:         {resultado['step_5_to_9']['coat_adj']:.2f} años")
        print(f"Tiempo expuesto a CUI (age):  {resultado['step_5_to_9']['age_cui_damage']:.2f} años")
        print(f"Fracción de pérdida (Art):    {resultado['step_11']['Art']:.4f}")
        print(f"FS:                           {resultado['step_12']['FS_CUIF']:.4f}")
        print(f"Relación de Esfuerzo (SRp):   {resultado['step_13']['SRp_CUIF']:.4f}")
        
        print(f"\nINDICADORES DE CONFIABILIDAD:")
        print(f"Pop1: {resultado['step_14_16']['Pop1']:.3f}")
        print(f"Pop2: {resultado['step_14_16']['Pop2']:.3f}")
        print(f"Pop3: {resultado['step_14_16']['Pop3']:.3f}")

        print(f"Beta 1 (DS1): {resultado['step_17']['beta1']:.3f}")
        print(f"Beta 2 (DS2): {resultado['step_17']['beta2']:.3f}")
        print(f"Beta 3 (DS3): {resultado['step_17']['beta3']:.3f}")

        print(f"\n>>> FACTOR DE DAÑO CUI (DF): {resultado['step_18']['DF_CUI']:.2f} <<<")
        print(f"------------------------------------")
    else:
        print(f"Error en el cálculo: {resultado.get('message', 'Desconocido')}")

if __name__ == "__main__":
    run_full_cui_test()