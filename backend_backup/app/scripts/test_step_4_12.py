from app.calculations.cof_4_12_financial_consequence import (
    compute_cof_4_12_financial_consequence,
    FinancialInputs,
    HoleSize
)

def print_financial_audit(title: str, res):
    print("\n" + "="*80)
    print(f"AUDITORÍA FINANCIERA 4.12: {title}")
    print("="*80)

    # 1. Resumen de Costos Principales
    print(f"{'CONCEPTO':<40} | {'COSTO (USD)':>15}")
    print("-" * 60)
    print(f"{'Daño al Componente (FC_cmd)':<40} | ${res.FC_f_cmd:,.2f}")
    print(f"{'Daño Área Afectada (FC_affa)':<40} | ${res.FC_f_affa:,.2f}")
    print(f"{'Pérdida de Producción (FC_prod)':<40} | ${res.FC_f_prod:,.2f}")
    print(f"{'Lesiones al Personal (FC_inj)':<40} | ${res.FC_f_inj:,.2f}")
    print(f"{'Limpieza Ambiental (FC_env)':<40} | ${res.FC_f_environ:,.2f}")
    print("-" * 60)
    print(f"{'CONSECUENCIA FINANCIERA TOTAL':<40} | ${res.FC_f_total:,.2f}")
    print("="*80)

    # 2. Detalles Operativos (Días de Parada)
    print("\n--- DETALLES DE PARADA (OUTAGE) ---")
    print(f"Días parados por reparación equipo (Outage_cmd): {res.outage_cmd_days:.2f} días")
    print(f"Días parados por daño área circundante (Outage_affa): {res.outage_affa_days:.2f} días")
    print(f"TOTAL DÍAS PARADA: {res.outage_cmd_days + res.outage_affa_days:.2f} días")

    # 3. Detalles Ambientales
    if res.FC_f_environ > 0:
        print("\n--- VOLUMEN DE DERRAME (Limpieza) ---")
        for size, vol in res.vol_env_by_hole_bbl.items():
            print(f"  - Agujero {size.value.upper():<8}: {vol:,.2f} bbl")

def run_test_4_12():
    # ---------------------------------------------------------
    # DATOS DE ENTRADA SIMULADOS
    # ---------------------------------------------------------
    
    # 1. Frecuencias de Falla (Generic Failure Frequencies)
    gff = {
        HoleSize.SMALL: 8e-06,
        HoleSize.MEDIUM: 2e-05,
        HoleSize.LARGE: 2e-06,
        HoleSize.RUPTURE: 6e-07,
    }
    gff_total = sum(gff.values())

    # 2. Masas liberadas (Simulando outputs del Paso 4.7)
    # Supongamos una fuga masiva de hidrocarburo líquido
    mass_lbm = {
        HoleSize.SMALL: 12.80,
        HoleSize.MEDIUM: 31.52,
        HoleSize.LARGE: 31.52,
        HoleSize.RUPTURE: 31.52,
    }

    # 3. Inputs del Escenario (Tubería de 8" con Hidrocarburo C6-C8)
    inp = FinancialInputs(
        component_type="PIPE-8",
        gff_by_hole=gff,
        gff_total=gff_total,
        
        # Áreas de consecuencia (Simulando outputs de 4.11)
        CA_f_cmd=121.90,  # Área de daño a equipos (ft2)
        CA_f_inj=299.05,  # Área de lesiones (ft2)
        
        # Factores de Costo (Usuario / Sitio)
        costfactor=1.0,
        material="Carbon steel",      # Material común
        equipcost=550,                # $/ft2 (Costo reemplazo equipo circundante)
        prodcost=331742.2,            # $/día (Lucro cesante)
        popdens=1.328E-05,            # personas/ft2 (Densidad poblacional planta)
        injcost=500000,               # $/persona (Costo por lesión/muerte)
        envcost=0,                    # $/bbl (Costo limpieza ambiental)
        outage_mult=1,                # Multiplicador de días de parada
        
        # Propiedades del Fluido (Para cálculo ambiental)
        fluid_key="C3-C4",            # Gasolina/Nafta típica
        mass_by_hole_lbm=mass_lbm     # Masas para calcular volumen derrame
    )

    # ---------------------------------------------------------
    # EJECUCIÓN DEL CÁLCULO
    # ---------------------------------------------------------
    result = compute_cof_4_12_financial_consequence(inp)
    
    # ---------------------------------------------------------
    # REPORTE
    # ---------------------------------------------------------
    print_financial_audit("TUBERÍA 8\" - GASOLINA (C3-C4)", result)

if __name__ == "__main__":
    run_test_4_12()