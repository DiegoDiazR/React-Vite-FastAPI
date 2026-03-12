class AcidSourWaterCorrosion:
    def __init__(self):
        # Tabla 2.B.10.2 - Tasas de corrosión base estimadas (CR_pH) en mpy
        # Filas corresponden al pH, Columnas a la Temperatura en °F
        self.ph_levels = [4.75, 5.25, 5.75, 6.25, 6.75]
        self.temp_levels_f = [100.0, 125.0, 175.0, 200.0]
        
        self.cr_base_table = [
            [1.0, 3.0, 5.0, 7.0],  # pH 4.75
            [0.7, 2.0, 3.0, 4.0],  # pH 5.25
            [0.4, 1.5, 2.0, 3.0],  # pH 5.75
            [0.3, 1.0, 1.5, 2.0],  # pH 6.25
            [0.2, 0.5, 0.7, 1.0]   # pH 6.75
        ]

    def _bilinear_interpolation(self, ph, temp_f):
        """
        Interpola la tasa de corrosión base de la Tabla 2.B.10.2.
        Si los valores están fuera de los límites de la tabla, se limitan a los extremos.
        """
        # Limitar a los bordes de la tabla
        ph = max(min(ph, self.ph_levels[-1]), self.ph_levels[0])
        temp_f = max(min(temp_f, self.temp_levels_f[-1]), self.temp_levels_f[0])

        # Encontrar los índices circundantes
        i = 0
        while i < len(self.ph_levels) - 1 and ph > self.ph_levels[i + 1]:
            i += 1
        j = 0
        while j < len(self.temp_levels_f) - 1 and temp_f > self.temp_levels_f[j + 1]:
            j += 1

        ph1, ph2 = self.ph_levels[i], self.ph_levels[i + 1]
        t1, t2 = self.temp_levels_f[j], self.temp_levels_f[j + 1]

        q11 = self.cr_base_table[i][j]
        q21 = self.cr_base_table[i][j + 1]
        q12 = self.cr_base_table[i + 1][j]
        q22 = self.cr_base_table[i + 1][j + 1]

        # Evitar división por cero si es un valor exacto
        if ph1 == ph2:
            f_ph_t1 = q11
            f_ph_t2 = q21
        else:
            f_ph_t1 = q11 + (q12 - q11) * ((ph - ph1) / (ph2 - ph1))
            f_ph_t2 = q21 + (q22 - q21) * ((ph - ph1) / (ph2 - ph1))

        if t1 == t2:
            return f_ph_t1
        else:
            return f_ph_t1 + (f_ph_t2 - f_ph_t1) * ((temp_f - t1) / (t2 - t1))

    def _get_oxygen_factor(self, oxygen_ppb):
        """
        Tabla 2.B.10.3 - Factor de ajuste por contenido de oxígeno (Fo)
        """
        if oxygen_ppb <= 50:
            return 1.0
        else:
            return 2.0

    def _get_velocity_factor(self, velocity, unit='fps'):
        """
        Ecuaciones (2.B.2) a (2.B.7) - Factor de ajuste por velocidad de fluido (F_v)
        """
        if unit.lower() in ['fps', 'ft/s']:
            if velocity < 6.0:
                return 1.0
            elif 6.0 <= velocity <= 20.0:
                return 0.25 * velocity - 0.5
            else:
                return 5.0
        elif unit.lower() in ['mps', 'm/s']:
            if velocity < 1.83:
                return 1.0
            elif 1.83 <= velocity <= 6.10:
                return 0.82 * velocity - 0.5
            else:
                return 5.0
        else:
            raise ValueError("Unidad de velocidad no reconocida. Usa 'fps' o 'mps'.")

    def calculate_corrosion_rate(self, water_present: bool, ph: float, 
                                 chlorides_present: bool, is_carbon_or_low_alloy: bool, 
                                 temperature_f: float, oxygen_ppb: float, 
                                 velocity: float, velocity_unit: str = 'fps'):
        """
        Calcula la tasa final de corrosión en base al diagrama de flujo Figure 2.B.10.1.
        Retorna la tasa de corrosión (float) o un mensaje (str) si el caso está fuera del alcance.
        """
        # 1. ¿Hay agua presente?
        if not water_present:
            return 0.0
            
        # 2. Verificar límites de pH
        if ph > 7.0:
            return "Fuera de alcance: El pH > 7. Proceder a la Sección 2.B.7 (Corrosión por Amoníaco)."
        
        if ph < 4.5:
            return "Fuera de alcance: El pH < 4.5. Proceder a la Sección 2.B.2 (Corrosión por Cloruros/Ácido)."
            
        # 3. ¿Hay cloruros presentes?
        if chlorides_present:
            return "Fuera de alcance: Cloruros presentes con pH < 7. Proceder a la Sección 2.B.2."
            
        # 4. ¿El material es acero al carbono o de baja aleación?
        if not is_carbon_or_low_alloy:
            # Según el diagrama de flujo, si no es acero al carbono, se asume un CR de 2 mpy
            return 2.0
            
        # 5. Determinar CR_pH desde la Tabla 2.B.10.2 (Interpolación)
        cr_ph = self._bilinear_interpolation(ph, temperature_f)
        
        # 6. Determinar F_o desde la Tabla 2.B.10.3
        f_o = self._get_oxygen_factor(oxygen_ppb)
        
        # 7. Determinar F_V usando Ecuaciones
        f_v = self._get_velocity_factor(velocity, velocity_unit)
        
        # 8. Calcular Tasa de Corrosión Final (Eq 2.B.1)
        # CR = CR_pH * F_o * F_V
        final_cr = cr_ph * f_o * f_v
        
        return final_cr

# ==========================================
# Ejemplo de uso:
# ==========================================
if __name__ == "__main__":
    evaluator = AcidSourWaterCorrosion()
    
    # Caso 1: Condiciones normales dentro del alcance
    print("--- CASO 1 ---")
    resultado = evaluator.calculate_corrosion_rate(
        water_present=True,
        ph=5.5,
        chlorides_present=False,
        is_carbon_or_low_alloy=True,
        temperature_f=150.0,
        oxygen_ppb=30.0,    # Oxígeno bajo (<=50)
        velocity=10.0,      # ft/s
        velocity_unit='fps'
    )
    if isinstance(resultado, float):
        print(f"Tasa de corrosión estimada: {resultado:.2f} mpy")
    else:
        print(resultado)

    # Caso 2: Alta velocidad y alto oxígeno
    print("\n--- CASO 2 ---")
    resultado2 = evaluator.calculate_corrosion_rate(
        water_present=True,
        ph=4.8,
        chlorides_present=False,
        is_carbon_or_low_alloy=True,
        temperature_f=180.0,
        oxygen_ppb=60.0,    # Oxígeno alto (>50) -> Factor 2.0
        velocity=7.0,       # m/s -> Mayor a 6.10, factor será 5.0
        velocity_unit='mps'
    )
    if isinstance(resultado2, float):
        print(f"Tasa de corrosión estimada: {resultado2:.2f} mpy")
    else:
        print(resultado2)
        
    # Caso 3: Fuera de alcance (pH muy bajo)
    print("\n--- CASO 3 ---")
    resultado3 = evaluator.calculate_corrosion_rate(
        water_present=True,
        ph=3.5,
        chlorides_present=False,
        is_carbon_or_low_alloy=True,
        temperature_f=120.0,
        oxygen_ppb=20.0,
        velocity=4.0,
        velocity_unit='fps'
    )
    print(resultado3)