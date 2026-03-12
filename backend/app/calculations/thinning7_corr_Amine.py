class AmineCorrosionCalculator:
    def __init__(self):
        # Datos unificados para Tablas 2.B.8.2 y 2.B.8.3
        # Estructura: { Carga_Gas_Acido: [ [Tasas para Nivel HSAS 1], [Nivel HSAS 2], [Nivel HSAS 3] ] }
        # Cada Nivel HSAS contiene tuplas por Temperatura: [190°F, 200°F, 220°F, 240°F, 260°F, 270°F]
        # Cada tupla es (Tasa_Velocidad_Baja, Tasa_Velocidad_Alta) en MPY
        self.base_data = {
            0.1: [ # Carga < 0.1 (Límite de velocidad: 20 ft/s)
                [(1, 3), (1, 3), (3, 10), (5, 15), (10, 25), (15, 40)],
                [(2, 6), (2, 6), (6, 20), (15, 40), (20, 45), (30, 80)],
                [(5, 10), (5, 15), (15, 40), (30, 60), (40, 90), (60, 120)]
            ],
            0.15: [ # Carga >= 0.15 (Límite de velocidad: 5 ft/s de aquí en adelante)
                [(1, 3), (2, 6), (5, 15), (10, 30), (15, 45), (20, 60)],
                [(2, 6), (4, 12), (10, 30), (20, 60), (30, 90), (40, 80)],
                [(5, 15), (8, 25), (20, 60), (40, 80), (60, 120), (120, 150)]
            ],
            0.25: [
                [(2, 6), (3, 9), (7, 20), (10, 30), (20, 60), (25, 75)],
                [(4, 10), (6, 20), (15, 40), (20, 50), (40, 80), (50, 100)],
                [(8, 25), (15, 45), (30, 60), (40, 80), (80, 120), (100, 150)]
            ],
            0.35: [
                [(2, 6), (4, 10), (7, 20), (15, 40), (25, 70), (30, 80)],
                [(4, 10), (8, 25), (15, 45), (30, 60), (50, 100), (100, 150)],
                [(8, 25), (15, 40), (35, 70), (60, 100), (100, 140), (150, 180)]
            ],
            0.45: [
                [(3, 9), (5, 15), (10, 30), (15, 45), (35, 70), (45, 100)],
                [(6, 15), (10, 30), (20, 60), (45, 90), (70, 130), (90, 150)],
                [(10, 30), (20, 40), (40, 80), (90, 120), (120, 150), (150, 180)]
            ],
            0.55: [
                [(3, 9), (7, 20), (10, 30), (25, 75), (40, 100), (50, 120)],
                [(6, 20), (15, 45), (20, 60), (50, 100), (80, 140), (100, 150)],
                [(10, 30), (30, 60), (45, 90), (100, 150), (140, 180), (160, 200)]
            ],
            0.65: [
                [(4, 10), (9, 30), (15, 40), (30, 100), (50, 120), (60, 150)],
                [(8, 15), (20, 40), (30, 60), (60, 100), (90, 140), (100, 150)],
                [(15, 35), (40, 80), (60, 100), (100, 150), (140, 180), (160, 200)]
            ],
            0.7: [
                [(5, 15), (10, 30), (20, 60), (40, 100), (60, 120), (70, 150)],
                [(10, 30), (20, 60), (40, 80), (70, 120), (100, 150), (120, 150)],
                [(20, 45), (40, 80), (60, 100), (100, 150), (150, 180), (170, 220)]
            ]
        }

        # Listas de referencia para búsqueda conservadora (redondeo hacia arriba)
        self.loadings = [0.1, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.7]
        self.temps = [190, 200, 220, 240, 260, 270]

        # Tabla 2.B.8.5 - Tasas para Acero Inoxidable Serie 300 (en MPY)
        self.ss_rates = {
            0.1: 1, 0.15: 1, 0.25: 1, 0.35: 2, 0.45: 2, 0.55: 3, 0.65: 4, 0.7: 5
        }

    def _get_conservative_val(self, val, array):
        """Devuelve el valor más cercano conservador (igual o superior) de una lista ordenada."""
        for item in array:
            if val <= item:
                return item
        return array[-1] # Si excede, retorna el valor máximo de la tabla

    def _get_multiplier(self, amine, conc):
        """Tabla 2.B.8.4 - Multiplicadores para concentraciones altas."""
        if amine == 'MEA':
            if conc <= 20: return 1.0
            elif conc <= 25: return 1.5
            else: return 2.0
        elif amine == 'DEA':
            if conc <= 30: return 1.0
            elif conc <= 40: return 1.2
            else: return 1.5
        elif amine == 'MDEA':
            return 1.0
        return 1.0

    def calculate_rate(self, material, amine, conc, temp, loading, velocity, hsas):
        """
        Calcula la tasa estimada de corrosión en MPYs.
        
        Parámetros:
        - material (str): 'CS' (Carbon Steel), 'SS' (Serie 300 SS)
        - amine (str): 'MEA', 'DEA', 'MDEA'
        - conc (float): Concentración de amina en wt%
        - temp (float): Temperatura en °F
        - loading (float): Carga de gas ácido (mol/mol)
        - velocity (float): Velocidad en ft/s
        - hsas (float): Concentración de HSAS en wt%
        """
        # material = material.upper()
        amine = amine.upper()

        # Validación inicial según flujograma
        if material not in ['Carbon Steel', 'Stainless Steel', '300 SS']:
            return "Consult with a materials specialist (Material no soportado por estas tablas)."

        # Ajuste conservador para "Acid Gas Loading"
        calc_loading = self._get_conservative_val(loading, self.loadings)

        # Ruta 1: Acero Inoxidable Serie 300
        if material in ['Stainless Steel', '300 SS']:
            if temp > 300:
                return "Consult with a materials specialist (La temperatura excede los 300 °F para SS)."
            return float(self.ss_rates[calc_loading])

        # Ruta 2: Acero al Carbono / Baja Aleación
        if material in ['Carbon Steel', 'CARBON STEEL', 'LOW ALLOY']:
            
            # 1. Determinar índice de Velocidad (<= o > que el límite)
            if calc_loading <= 0.1:
                vel_idx = 0 if velocity <= 20 else 1
            else:
                vel_idx = 0 if velocity <= 5 else 1

            # 2. Determinar índice de HSAS según el tipo de amina
            if amine in ['MEA', 'DEA']:
                hsas_keys = [2.0, 3.0, 4.0]
            elif amine == 'MDEA':
                hsas_keys = [0.5, 2.25, 4.0]
            else:
                return "Tipo de amina no soportado."

            calc_hsas = self._get_conservative_val(hsas, hsas_keys)
            hsas_idx = hsas_keys.index(calc_hsas)

            # 3. Determinar índice de Temperatura
            calc_temp = self._get_conservative_val(temp, self.temps)
            temp_idx = self.temps.index(calc_temp)

            # 4. Obtener tasa base de las Tablas 2.B.8.2 / 2.B.8.3
            base_rate = self.base_data[calc_loading][hsas_idx][temp_idx][vel_idx]

            # 5. Obtener multiplicador de concentración (Tabla 2.B.8.4)
            multiplier = self._get_multiplier(amine, conc)

            # 6. Calcular Tasa Estimada
            estimated_rate = base_rate * multiplier
            
            return float(estimated_rate)

# --- Ejemplo de Uso ---
if __name__ == "__main__":
    calc = AmineCorrosionCalculator()
    
    # Ejemplo 1: Acero al Carbono, DEA 35%, 220°F, Carga 0.35, Vel 6 ft/s, HSAS 3.0%
    tasa_cs = calc.calculate_rate(
        material='Carbon Steel', amine='DEA', conc=35, 
        temp=220, loading=0.35, velocity=6, hsas=3.0
    )
    print(f"Tasa Estimada para CS: {tasa_cs} MPY")  
    # Esperado: Carga 0.35 -> HSAS(3.0) -> Temp(220) -> Vel(>5) = 45 MPY
    # Multiplicador DEA 35% = 1.2.  Total: 45 * 1.2 = 54.0 MPY

    # Ejemplo 2: Acero Inoxidable 300, MEA 20%, 250°F, Carga 0.45
    tasa_ss = calc.calculate_rate(
        material='Stainless Steel', amine='MEA', conc=20, 
        temp=250, loading=0.45, velocity=10, hsas=2.0
    )
    print(f"Tasa Estimada para SS: {tasa_ss} MPY") 
    # Esperado: Carga 0.45 en Tabla SS = 2 MPY