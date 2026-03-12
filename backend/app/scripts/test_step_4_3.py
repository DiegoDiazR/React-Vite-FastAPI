
import pprint
import math
from app.calculations.cof_4_2_release_hole_size import compute_cof_4_2_release_hole_size
from app.calculations.cof_4_3_release_rate import (
    compute_release_rates_for_holes, 
    LiquidInputs, 
    GasInputs, 
    Phase
)

def test_4_3_integral():
    print("="*70)
    print("VALIDACIÓN FINAL PASO 4.3: TASAS DE LIBERACIÓN (LÓGICA EXCEL)")
    print("="*70)

    # 1. Recuperamos diámetros del Paso 4.2 para un PIPE-8
    # Resultados dn: 0.25, 1.0, 4.0, 8.0
    res_4_2 = compute_cof_4_2_release_hole_size(component_type="PIPE-8", D_in=8.0)
    dn_dict = res_4_2.dn_in

    # 2. Definimos Parámetros (Ejemplo: C3-C4 @ 300 psi, 540 R)
    # R=1545, gc=32.2 ya están integrados en la lógica interna del backend
    gas_in = GasInputs(
        ps_psi=192.49,
        ts_rankine=540.0,
        mw=51.0,     # Propano (C3-C4)
        k=1.106,     # Gamma del Propano
        patm_psi=12.49
    )

    # 3. Cálculo masivo para los 4 escenarios de falla
    results_wn = compute_release_rates_for_holes(
        phase=Phase.GAS,
        hole_diameters_in=dn_dict,
        gas=gas_in
    )

    print(f"\nDETALLE TÉCNICO COMPONENTE: {res_4_2.component_type}")
    print(f"Presión: {gas_in.ps_psi} psia | Temp: {gas_in.ts_rankine} R | MW: {gas_in.mw}")
    
    # Agregamos An (in2) al encabezado
    print(f"\n{'TAMAÑO':<10} | {'dn (in)':<8} | {'An (in2)':<10} | {'RÉGIMEN':<10} | {'Wn (lb/s)':<12}")
    print("-" * 72)
    
    for size, res in results_wn.items():
        # Extraemos el valor del dn desde el diccionario del paso anterior
        dn = dn_dict[size]
        
        # Calculamos el área en in2 para mostrarla en la tabla
        # An = (pi/4) * dn^2
        area_in2 = (math.pi / 4.0) * (dn**2)
        
        label = size.value.upper() if hasattr(size, 'value') else str(size).upper()
        regime = res.regime.upper() if res.regime else "N/A"
        
        # Imprimimos la fila incluyendo el área con 4 decimales
        print(f"{label:<10} | {dn:<8.2f} | {area_in2:<10.4f} | {regime:<10} | {res.mdot_lbm_s:<12.4f}")

    print("\n" + "="*70)
    print("PRUEBA COMPLETADA")
    print("="*70)
        
if __name__ == "__main__":
    test_4_3_integral()