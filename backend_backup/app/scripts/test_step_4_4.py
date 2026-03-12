import pprint
from app.calculations.cof_4_4_fluid_inventory import (
    compute_cof_4_4_fluid_inventory, 
    InventoryInputs
)

def test_paso_4_4_inventory():
    print("="*75)
    print("PRUEBA PASO 4.4: MASA DE INVENTARIO DISPONIBLE (Avail)")
    print("="*75)

    # 1. TASAS OBTENIDAS EN EL PASO 4.3 (Valores de tu test anterior)
    wn_dict = {
        "small": 0.2375,
        "medium": 3.8007,
        "large": 60.8117,
        "rupture": 243.2470
    }
    # Wmax8 es la tasa para el agujero de 8", que en este caso es igual a 'rupture'
    wmax8 = 243.2470

    # 2. DEFINICIÓN DEL INVENTARIO (Parámetros de tu Excel)
    # Supongamos que el componente tiene 5,000 lbs 
    # y el resto del grupo tiene 15,000 lbs (Total sistema = 20,000 lbs)
    inv_inputs = InventoryInputs(
        mass_comp_lbm=31.52,
        other_component_masses_lbm={"Tank-V101": 0}
    )

    # 3. CÁLCULO
    resultado = compute_cof_4_4_fluid_inventory(
        inventory=inv_inputs,
        wn_by_hole_lbm_s=wn_dict,
        wmax8_lbm_s=wmax8
    )

    # 4. REPORTE
    print(f"\nMASA COMPONENTE: {inv_inputs.mass_comp_lbm} lb")
    print(f"MASA TOTAL GRUPO (Inv): {resultado.mass_inv_lbm} lb")
    print(f"\n{'TAMAÑO':<10} | {'Wn (lb/s)':<10} | {'Mass_Add (lb)':<15} | {'Mass_Avail (lb)':<15}")
    print("-" * 70)

    for hole, res in resultado.per_hole.items():
        print(f"{hole.upper():<10} | {res.wn_lbm_s:<10.2f} | {res.mass_add_lbm:<15.2f} | {res.mass_avail_lbm:<15.2f}")

    print("\n" + "="*75)
    print("Nota: Si Mass_Avail == Mass_Inv, la fuga es limitada por el inventario total.")
    print("="*75)

if __name__ == "__main__":
    test_paso_4_4_inventory()