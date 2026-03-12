import pprint
from app.calculations.cof_4_2_release_hole_size import compute_cof_4_2_release_hole_size

def test_paso_4_2():
    print("="*60)
    print("PRUEBA INTEGRAL PASO 4.2: SELECCIÓN DE AGUJEROS Y GFF")
    print("="*60)
    
    # Caso de prueba: Tubería de 8 pulgadas (PIPE-8)
    # Resultados esperados según tu Excel: 0.25, 1.0, 4.0, 8.0
    componente = "PIPE-2"
    diametro = 2

    try:
        res = compute_cof_4_2_release_hole_size(component_type=componente, D_in=diametro)

        print(f"\n1. DATOS DEL COMPONENTE:")
        print(f"   Tipo: {res.component_type}")
        print(f"   Diámetro Nominal (D): {res.D_in} in")
        print(f"   GFF Total: {res.gff_total} fallas/año")

        print(f"\n2. RESULTADOS POR AGUJERO (dn & GFF):")
        print(f"{'Tamaño':<10} | {'dn (in)':<10} | {'GFF (fallas/año)':<15} | {'Área (in2)':<10}")
        print("-" * 55)

        # Iteramos sobre los objetos ReleaseHole para detalle técnico
        for n, h in res.holes.items():
            # Buscamos la GFF correspondiente en el mapa de resultados
            gff_val = res.gff[h.hole_size]
            print(f"{h.hole_size.value.upper():<10} | {h.dn_in:<10.2f} | {gff_val:<15.2e} | {h.area_in2:<10.4f}")

        print(f"\n3. RESUMEN PARA PASO 4.3 (Payload sugerido):")
        pprint.pprint(res.dn_in)

    except Exception as e:
        print(f"\n[ERROR]: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paso_4_2()