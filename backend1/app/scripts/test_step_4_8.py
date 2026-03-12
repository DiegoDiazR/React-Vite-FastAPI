from app.calculations.cof_4_8_flammable_explosive import (
    compute_cof_4_8_flammable_explosive, 
    HoleInput, AITInputs, ReleaseType, Phase
)

def test_final_flammable_consequence():
    print("="*85)
    print("PRUEBA MAESTRA PASO 4.8: ÁREAS DE CONSECUENCIA INFLAMABLE (C3-C4)")
    print("="*85)

    # 1. Datos acumulados de los tests anteriores (PIPE-8)
    # Wn_adj y Mass_adj del Paso 4.7
    hole_data = {
        "small": HoleInput("small", ReleaseType.CONTINUOUS, Phase.GAS, 0.213454285, 31.52),
        "medium": HoleInput("medium", ReleaseType.CONTINUOUS, Phase.GAS, 3.415268559, 31.52),
        "large": HoleInput("large", ReleaseType.INSTANTANEOUS, Phase.GAS, 54.64429694, 31.52),
        "rupture": HoleInput("rupture", ReleaseType.INSTANTANEOUS, Phase.GAS, 218.5771878, 31.52)
    }

    # GFF del Paso 4.2
    gff = {"small": 0.000008, "medium": 0.00002, "large": 0.000002, "rupture": 0.0000006}
    gff_tot = sum(gff.values())

    # 2. Ejecución con AIT (Propano AIT ~ 842 °F -> 1302 R)
    # Operando a 80 °F (540 R) -> AINL es lo dominante
    res = compute_cof_4_8_flammable_explosive(
        fluid="C3-C4",
        holes=hole_data,
        ait=AITInputs(Ts_R=540.0,representative_fluid="C3-C4"),
        mitigation_system_key="fire_water_deluge_and_monitors",
        gff_by_hole=gff,
        gff_total=gff_tot
    )

    for hole_name, data in res.holes.items():
        print(f"\n--- Auditoría Agujero: {hole_name} ---")
        print(f"Fact_mit:  {data.fact_mit:.4f}")
        # print(f"eneffn:  {data.eneff:.4f}")
        # print("-" * 55)
        # print(f"CA_ainl_cont-cte_a:  {data.CA_ainl_cont_cte_a:.4f}")
        # print(f"CA_ainl_cont-cte_b:  {data.CA_ainl_cont_cte_b:.4f}")
        # print(f"   -> CA_ainl_cont:  {data.CA_ainl_cont:.4f}")
        # print(f"CA_ail_cont-cte_a:   {data.CA_ail_cont_cte_a:.4f}")
        # print(f"CA_ail_cont-cte_b:   {data.CA_ail_cont_cte_b:.4f}")
        # print(f"   -> CA_ail_cont:   {data.CA_ail_cont:.4f}")
        # print(f"CA_ainl_inst-cte_a:  {data.CA_ainl_inst_cte_a:.4f}")
        # print(f"CA_ainl_inst-cte_b:  {data.CA_ainl_inst_cte_b:.4f}")
        # print(f"   -> CA_ainl_inst:  {data.CA_ainl_inst:.4f}")
        # print(f"CA_ail_inst-cte_a:   {data.CA_ail_inst_cte_a:.4f}")
        # print(f"CA_ail_inst-cte_b:   {data.CA_ail_inst_cte_b:.4f}")
        # print(f"   -> CA_ail_inst:   {data.CA_ail_inst:.4f}")
        # print("-" * 55)
        # print(f"CA_ainl_cont_inj_cte_a:  {data.CA_ainl_cont_inj_cte_a:.4f}")
        # print(f"CA_ainl_cont_inj_cte_b:  {data.CA_ainl_cont_inj_cte_b:.4f}")
        # print(f"   -> CA_ainl_cont_inj:  {data.CA_ainl_cont_inj:.4f}")
        # print(f"CA_ail_cont_inj_cte_a:  {data.CA_ail_cont_inj_cte_a:.4f}")
        # print(f"CA_ail_cont_inj_cte_b:  {data.CA_ail_cont_inj_cte_b:.4f}")
        # print(f"   -> CA_ail_cont_inj:  {data.CA_ail_cont_inj:.4f}")

        # print(f"CA_ainl_inst_inj_cte_a:  {data.CA_ainl_inst_inj_cte_a:.4f}")
        # print(f"CA_ainl_inst_inj_cte_b:  {data.CA_ainl_inst_inj_cte_b:.4f}")
        # print(f"   -> CA_ainl_inst_inj:  {data.CA_ainl_inst_inj:.4f}")
        # print(f"CA_ail_inst_inj_cte_a:  {data.CA_ail_inst_inj_cte_a:.4f}")
        # print(f"CA_ail_inst_inj_cte_b:  {data.CA_ail_inst_inj_cte_b:.4f}")
        # print(f"   -> CA_ail_inst_inj:  {data.CA_ail_inst_inj:.4f}")
        # print("-" * 55)

        # print(f"CA_ail_cmd_n: {data.CA_ail_cmd_n[0]:.4f}")
        # print(f"CA_ail_inj_n: {data.CA_ail_inj_n[0]:.4f}")
        # print(f"CA_ainl_cmd_n: {data.CA_ainl_cmd_n[0]:.4f}")
        # print(f"CA_ainl_inj_n: {data.CA_ainl_inj_n[0]:.4f}")

        # print("-" * 55)
        # print(f"   -> CA_flam_cmd_nj:  {data.CA_flam_cmd_n:.4f}")
        # print(f"   -> CA_flam_inj_n:  {data.CA_flam_inj_n:.4f}")
        
        # print("-" * 55)
        print(f"Fact_IC:  {data.fact_IC:.4f}")
        print(f"Fact_AIT: {data.fact_AIT:.4f}")
        print(f"CA_cmd:   {data.CA_cmd:.2f} ft2")
        print(f"  -> AINL base: {data.CA_cmd_AINL:.2f}")
        print(f"  -> AIL base:  {data.CA_cmd_AIL:.2f}")
    
    
    # 3. Reporte Final
    print(f"\nRESULTADOS PONDERADOS (Pies Cuadrados):")
    print(f"CA Daño a Equipos (CMD): {res.CA_cmd_final:.2f} ft²")
    print(f"CA Lesiones a Personal (INJ): {res.CA_inj_final:.2f} ft²")
    
    print(f"\n{'HUECO':<10} | {'CA_CMD (ft2)':<12} | {'CA_INJ (ft2)':<12} | {'fact_IC':<8}")
    print("-" * 55)
    for hk, hr in res.holes.items():
        print(f"{hk.upper():<10} | {hr.CA_cmd:<12.2f} | {hr.CA_inj:<12.2f} | {hr.fact_IC:<8.2f}")

if __name__ == "__main__":
    test_final_flammable_consequence()

