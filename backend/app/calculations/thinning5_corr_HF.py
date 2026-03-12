import bisect

class HFCorrosionCalculator:
    def __init__(self):
        # ---------------------------------------------------------
        # TABLA 2.B.6.2 - Acero al Carbono (Carbon Steel)
        # ---------------------------------------------------------
        # Columnas de Concentración de HF (%)
        self.cs_hf_cols = [1, 3, 7, 20, 30, 40, 60, 80, 90, 100] # 100 representa > 90
        
        # Filas: (Temperatura máxima °F, Velocidad límite '< 5' es False, '>= 5' es True)
        self.cs_temp_rows = [100, 130, 160, 190] # 100 representa 70 to 100
        
        # Matriz de datos de Acero al Carbono: cs_data[temp_idx][vel_idx][hf_idx]
        # vel_idx: 0 para < 5 ft/s, 1 para >= 5 ft/s
        self.cs_data = {
            100: {
                '< 5':  [30, 100, 300, 700, 800, 700, 150, 20, 8, 2],
                '>= 5': [60, 200, 600, 999, 999, 999, 300, 40, 15, 4]
            },
            130: {
                '< 5':  [100, 350, 999, 999, 999, 999, 500, 50, 25, 7],
                '>= 5': [200, 700, 999, 999, 999, 999, 999, 100, 50, 15]
            },
            160: {
                '< 5':  [400, 999, 999, 999, 999, 999, 999, 250, 100, 25],
                '>= 5': [800, 999, 999, 999, 999, 999, 999, 500, 200, 50]
            },
            190: {
                '< 5':  [999, 999, 999, 999, 999, 999, 999, 999, 400, 100],
                '>= 5': [999, 999, 999, 999, 999, 999, 999, 999, 800, 200]
            }
        }

        # ---------------------------------------------------------
        # TABLA 2.B.6.3 - Aleación 400 (Alloy 400)
        # ---------------------------------------------------------
        # Columnas de Concentración de HF (%)
        self.alloy_hf_cols = [1, 2, 5, 6, 63, 64, 80, 81]
        
        # Filas de Temperatura °F
        self.alloy_temp_rows = [80, 125, 175, 200]
        
        # Matriz de datos de Aleación 400: alloy_data[temp_idx][aerated][hf_idx]
        self.alloy_data = {
            80: {
                False: [1, 1, 1, 10, 10, 1, 1, 2],    # No aerado
                True:  [10, 10, 10, 25, 25, 10, 10, 15] # Aerado (Yes)
            },
            125: {
                False: [1, 1, 1, 15, 15, 5, 5, 3],
                True:  [10, 10, 10, 30, 30, 20, 20, 15]
            },
            175: {
                False: [5, 5, 5, 20, 20, 10, 10, 5],
                True:  [20, 20, 20, 100, 100, 50, 50, 20]
            },
            200: {
                False: [10, 10, 10, 20, 20, 20, 20, 10],
                True:  [100, 100, 100, 200, 200, 200, 200, 100]
            }
        }

    def _get_conservative_value(self, value, thresholds):
        """Encuentra el valor límite superior más cercano para ser conservador."""
        idx = bisect.bisect_left(thresholds, value)
        if idx >= len(thresholds):
            return thresholds[-1]  # Devuelve el máximo si excede la tabla
        return thresholds[idx]

    def calc_carbon_steel(self, temp_f, vel_ft_s, hf_conc):
        """Calcula la tasa para Acero al Carbono (Tabla 2.B.6.2)."""
        # Limitar temperatura a la cota conservadora de la tabla
        temp_key = self._get_conservative_value(temp_f, self.cs_temp_rows)
        
        # Determinar categoría de velocidad
        vel_key = '< 5' if vel_ft_s < 5 else '>= 5'
        
        # Limitar concentración de HF
        hf_key = self._get_conservative_value(hf_conc, self.cs_hf_cols)
        hf_idx = self.cs_hf_cols.index(hf_key)
        
        tasa = self.cs_data[temp_key][vel_key][hf_idx]
        return tasa, f"Tabla 2.B.6.2 evaluada en: Temp <= {temp_key}°F, Vel {vel_key} ft/s, HF <= {hf_key if hf_key != 100 else '>90'}%"

    def calc_alloy_400(self, temp_f, is_aerated, hf_conc):
        """Calcula la tasa para Aleación 400 (Tabla 2.B.6.3)."""
        temp_key = self._get_conservative_value(temp_f, self.alloy_temp_rows)
        hf_key = self._get_conservative_value(hf_conc, self.alloy_hf_cols)
        hf_idx = self.alloy_hf_cols.index(hf_key)
        
        tasa = self.alloy_data[temp_key][is_aerated][hf_idx]
        estado_aeracion = "Aerado" if is_aerated else "No aerado"
        return tasa, f"Tabla 2.B.6.3 evaluada en: Temp <= {temp_key}°F, {estado_aeracion}, HF <= {hf_key}%"

    def determinar_tasa(self, material, temp_f, hf_conc, velocidad_ft_s=None, aerado=None):
        """
        Función principal siguiendo el diagrama de flujo Figura 2.B.6.1.
        """
        # material = material.strip().lower()

        # ¿Es el material de construcción Acero al Carbono (Carbon Steel)?
        if material in ['Carbon Steel', 'acero al carbono', 'cs']:
            if velocidad_ft_s is None:
                raise ValueError("Se requiere 'velocidad_ft_s' para Acero al Carbono.")
            tasa, nota = self.calc_carbon_steel(temp_f, velocidad_ft_s, hf_conc)
            return {"Tasa de Corrosión (mpy)": tasa, "Método": "Tabla 2.B.6.2", "Detalles": nota}

        # ¿Es el material de construcción Aleación 400 (Alloy 400)?
        elif material in ['Alloy 400', 'aleacion 400', 'monel']:
            if aerado is None:
                raise ValueError("Se requiere el booleano 'aerado' (True/False) para Aleación 400.")
            tasa, nota = self.calc_alloy_400(temp_f, aerado, hf_conc)
            return {"Tasa de Corrosión (mpy)": tasa, "Método": "Tabla 2.B.6.3", "Detalles": nota}

        # Determinar de literatura publicada
        else:
            return {
                "Tasa de Corrosión (mpy)": "Desconocida", 
                "Método": "Literatura Publicada", 
                "Detalles": f"El material '{material}' no está cubierto por las tablas estándar. Consulte manuales del fabricante o literatura."
            }


# ==========================================
# EJEMPLO DE USO
# ==========================================
if __name__ == "__main__":
    calculadora = HFCorrosionCalculator()

    print("--- Evaluación de Casos de Corrosión por HF ---\n")

    # Caso 1: Acero al Carbono, 90°F, 3 ft/s, 7% de HF
    resultado1 = calculadora.determinar_tasa(
        material="Carbon Steel", 
        temp_f=90,          # Se redondeará conservadoramente a 100 (rango 70-100)
        hf_conc=7,          
        velocidad_ft_s=3    # '< 5'
    )
    print("CASO 1 (Acero al Carbono):")
    print(resultado1, "\n")

    # Caso 2: Acero al Carbono, 145°F, 6 ft/s, 35% de HF
    resultado2 = calculadora.determinar_tasa(
        material="Acero al Carbono", 
        temp_f=145,         # Limitará a 160
        hf_conc=35,         # Limitará a 40
        velocidad_ft_s=6    # '>= 5'
    )
    print("CASO 2 (Acero al Carbono interpolación conservadora):")
    print(resultado2, "\n")

    # Caso 3: Aleación 400, 160°F, Aerado, 5% de HF
    resultado3 = calculadora.determinar_tasa(
        material="Alloy 400", 
        temp_f=160,         # Limitará a 175
        hf_conc=5, 
        aerado=True         # Aerado
    )
    print("CASO 3 (Aleación 400):")
    print(resultado3, "\n")

    # Caso 4: Material no estándar (ej. Inconel)
    resultado4 = calculadora.determinar_tasa(
        material="Inconel 625", 
        temp_f=150, 
        hf_conc=10
    )
    print("CASO 4 (Otro Material):")
    print(resultado4, "\n")