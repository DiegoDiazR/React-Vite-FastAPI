import math

class CO2CorrosionModel:
    def __init__(self):
        # Tabla 2.B.13.2 - Función de Temperatura-pH (f(T, pH))
        self.T_array = [68, 86, 104, 122, 140, 158, 176, 194, 212, 230, 248, 266, 284, 302]
        self.pH_array = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]
        self.f_T_pH_matrix = [
            [6.00, 5.45, 4.90, 3.72, 2.55, 1.55, 0.72],
            [8.52, 7.77, 7.02, 5.16, 3.40, 2.00, 0.91],
            [10.98, 10.06, 9.13, 6.49, 4.08, 2.30, 1.02],
            [11.92, 10.96, 10.01, 6.86, 4.10, 2.20, 0.94],
            [12.83, 11.86, 10.89, 7.18, 4.05, 2.03, 0.84],
            [13.42, 12.01, 10.60, 6.58, 3.61, 1.86, 0.87],
            [13.93, 12.12, 10.31, 6.01, 3.20, 1.70, 0.90],
            [9.37, 7.91, 6.45, 2.44, 0.82, 0.49, 0.32],
            [9.23, 8.04, 6.38, 2.19, 0.94, 0.62, 0.42],
            [8.96, 8.09, 6.22, 1.87, 1.07, 0.77, 0.53],
            [8.55, 8.06, 5.98, 1.48, 1.20, 0.92, 0.65],
            [7.38, 6.39, 3.98, 0.96, 0.80, 0.63, 0.47],
            [6.26, 4.91, 2.31, 0.53, 0.46, 0.39, 0.32],
            [5.20, 3.62, 0.98, 0.19, 0.19, 0.19, 0.19]
        ]

    def interpolate_f_T_pH(self, T, pH):
        """Interpolación bilineal para la Tabla 2.B.13.2"""
        # Limitar a los bordes de la tabla
        T = max(min(T, self.T_array[-1]), self.T_array[0])
        pH = max(min(pH, self.pH_array[-1]), self.pH_array[0])

        # Encontrar índices
        i = 0
        while i < len(self.T_array) - 2 and T >= self.T_array[i+1]: i += 1
        j = 0
        while j < len(self.pH_array) - 2 and pH >= self.pH_array[j+1]: j += 1

        T0, T1 = self.T_array[i], self.T_array[i+1]
        pH0, pH1 = self.pH_array[j], self.pH_array[j+1]

        z00 = self.f_T_pH_matrix[i][j]
        z10 = self.f_T_pH_matrix[i+1][j]
        z01 = self.f_T_pH_matrix[i][j+1]
        z11 = self.f_T_pH_matrix[i+1][j+1]

        # Interpolación
        Td = (T - T0) / (T1 - T0) if T1 != T0 else 0
        pHd = (pH - pH0) / (pH1 - pH0) if pH1 != pH0 else 0

        c0 = z00 * (1 - Td) + z10 * Td
        c1 = z01 * (1 - Td) + z11 * Td
        return c0 * (1 - pHd) + c1 * pHd

    def calculate_dew_point(self, pct_w, P_psia):
        """Ecuación (2.B.25)"""
        if pct_w <= 0: return -float('inf')
        log_Td = 2.0866 + 0.2088 * math.log10(pct_w / 100.0) + 0.2242 * math.log10(P_psia)
        return 10 ** log_Td

    def calculate_pH(self, T_F, pCO2_psi, condition_type="condensation"):
        """Ecuaciones (2.B.27), (2.B.28), (2.B.29)"""
        if condition_type == "condensation":
            return 2.8686 + 0.7931 * math.log10(T_F) - 0.57 * math.log10(pCO2_psi)
        elif condition_type == "fe_saturated":
            return 2.5907 + 0.8668 * math.log10(T_F) - 0.49 * math.log10(pCO2_psi)
        elif condition_type == "seawater":
            return 2.7137 + 0.8002 * math.log10(T_F) - 0.57 * math.log10(pCO2_psi)
        else:
            raise ValueError("Tipo de condición de pH no válido.")

    def calculate_fugacity(self, pCO2_bar, T_C):
        """Ecuación (2.B.30)"""
        min_val = min(250, pCO2_bar)
        log_fCO2 = math.log10(pCO2_bar) + min_val * (0.0031 - (1.4 / (T_C + 273)))
        return 10 ** log_fCO2

    def calculate_shear_stress(self, rho_m, u_m, mu_m, D, e):
        """Ecuaciones (2.B.33), (2.B.34), (2.B.35)"""
        # Re = (D * rho_m * u_m) / mu_m (mu_m en Pa*s)
        Re = (D * rho_m * u_m) / mu_m
        
        if Re <= 2300:
            # Flujo laminar aproximado (la norma asume turbulento con Re > 2300)
            f = 64.0 / Re if Re > 0 else 0
        else:
            f = 0.001375 * (1 + (20000 * (e / D) + 10**6 / Re)**0.33)
            
        S = (f * rho_m * u_m**2) / 2.0
        return min(S, 150.0)  # El esfuerzo cortante no necesita exceder 150 Pa

    def calculate_corrosion_rate(self, **kwargs):
        """
        Calcula la tasa de corrosión basándose en el diagrama de flujo Figura 2.B.13.1.
        Parámetros esperados en kwargs:
        - is_carbon_steel (bool)
        - liquid_hcs_present (bool)
        - water_content_pct (float)
        - fluid_velocity_m_s (float)
        - water_weight_pct (float) : para el cálculo del punto de rocío
        - T_F (float) : Temperatura en °F
        - P_psia (float) : Presión en psia
        - co2_mole_pct (float) : Porcentaje molar de CO2
        - pH_value (float, opcional) : Si no se da, se calcula
        - pH_condition (str) : 'condensation', 'fe_saturated', 'seawater'
        - S_Pa (float, opcional) : Esfuerzo cortante en Pa. Si no se da, se calcula con los siguientes:
        - rho_m (float), mu_m_cp (float), D_m (float), e_m (float)
        - glycol_pct (float, opcional) : % peso de glicol
        - inhibitor_efficiency (float, opcional) : % eficiencia del inhibidor
        """
        # 1. ¿Es el material Acero al Carbono o <13% Cr?
        if not kwargs.get('is_carbon_steel', True):
            return 0.0, "Sin corrosión: El material no es acero al carbono."

        T_F = kwargs.get('T_F')
        P_psia = kwargs.get('P_psia')
        
        if T_F > 284:
            print("Advertencia: Las temperaturas superiores a 284 °F no están consideradas en la norma.")

        # --- GESTIÓN DE UNIDADES DE ENTRADA ---
        # Velocidad del fluido: de fps a m/s si es necesario
        if 'fluid_velocity_fps' in kwargs:
            fluid_velocity_m_s = kwargs['fluid_velocity_fps'] * 0.3048
        else:
            fluid_velocity_m_s = kwargs.get('fluid_velocity_m_s', 1.0)
        
        # Diámetro de la tubería: de pulgadas a metros si es necesario
        if 'diameter_in' in kwargs:
            D_m = kwargs['diameter_in'] * 0.0254
        else:
            D_m = kwargs.get('D_m', 0.2)

        # 2. Lógica del Diagrama de Flujo para presencia de agua
        liquid_hcs_present = kwargs.get('liquid_hcs_present', False)
        if liquid_hcs_present:
            water_content = kwargs.get('water_content_pct', 0)
            if water_content < 20 and fluid_velocity_m_s > 1.0:
                return 0.0, "Sin corrosión: HC líquidos presentes arrastran el agua (<20% agua, vel > 1 m/s)."

        # Calcular Punto de Rocío
        pct_w = kwargs.get('water_weight_pct', 0)
        Td = self.calculate_dew_point(pct_w, P_psia)
        
        # ¿La temperatura actual es menor al punto de rocío?
        if T_F >= Td and pct_w < 100: 
            return 0.0, f"Sin corrosión: No hay agua líquida (T={T_F}°F >= T_dew={Td:.2f}°F)."

        # --- CÁLCULO DE LA TASA BASE (Ecuación 2.B.26) ---
        pCO2_psi = min(P_psia * (kwargs.get('co2_mole_pct', 0) / 100.0), 580.0)
        if pCO2_psi <= 0:
            return 0.0, "Sin corrosión: No hay presión parcial de CO2 presente."
            
        pCO2_bar = pCO2_psi / 14.5038
        T_C = (T_F - 32) / 1.8

        fCO2_bar = self.calculate_fugacity(pCO2_bar, T_C)

        if 'pH_value' in kwargs:
            pH = kwargs.get('pH_value')
        else:
            pH = self.calculate_pH(T_F, pCO2_psi, kwargs.get('pH_condition', 'condensation'))

        # Esfuerzo Cortante (Shear Stress)
        if 'S_Pa' in kwargs:
            S = min(kwargs.get('S_Pa'), 150.0)
        else:
            mu_m_Pa_s = kwargs.get('mu_m_cp', 1.0) * 0.001
            S = self.calculate_shear_stress(
                rho_m=kwargs.get('rho_m', 1000), 
                u_m=fluid_velocity_m_s, 
                mu_m=mu_m_Pa_s, 
                D=D_m, 
                e=kwargs.get('e_m', 0.000045)
            )

        f_T_pH = self.interpolate_f_T_pH(T_F, pH)

        # Tasa de Corrosión Base (mm/yr)
        exponent = 0.146 + 0.0324 * fCO2_bar
        CR_base_mm_yr = f_T_pH * (fCO2_bar ** 0.62) * ((S / 19.0) ** exponent)

        # --- FACTORES DE AJUSTE ---
        F_glycol = 1.0
        F_inhib = 1.0
        
        glycol_pct = kwargs.get('glycol_pct', 0)
        if glycol_pct > 0:
            log_F = 1.6 * (math.log10(100 - glycol_pct) - 2)
            F_glycol = max(10 ** log_F, 0.008) 
            
        inhib_eff = kwargs.get('inhibitor_efficiency', 0)
        if inhib_eff > 0:
            F_inhib = 1.0 - (inhib_eff / 100.0)

        CR_final_mm_yr = CR_base_mm_yr * min(F_glycol, F_inhib)
        CR_final_mpy = CR_final_mm_yr * 39.4

        return CR_final_mpy, f"Tasa calculada: {CR_final_mpy:.3f} mpy ({CR_final_mm_yr:.3f} mm/yr). S={S:.2f} Pa, pH={pH:.2f}"

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    modelo = CO2CorrosionModel()
    
    parametros_campo = {
        'is_carbon_steel': True,
        'liquid_hcs_present': False,
        'water_weight_pct': 5.0, 
        'T_F': 140.0,
        'P_psia': 300.0,
        'co2_mole_pct': 10.0,
        'fluid_velocity_fps': 8.2,  # Ingreso directo en fps
        'diameter_in': 8.0,         # Ingreso directo en pulgadas
        'pH_condition': 'condensation',
        'rho_m': 900.0,
        'mu_m_cp': 1.2,
        'e_m': 0.000045,
        'glycol_pct': 0.0,
        'inhibitor_efficiency': 0.0
    }
    
    tasa_mpy, mensaje = modelo.calculate_corrosion_rate(**parametros_campo)
    print(mensaje)