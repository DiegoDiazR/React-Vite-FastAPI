class CoolingWaterCorrosion:
    def __init__(self):
        """
        Inicializa la clase con las tablas de referencia según la metodología.
        Los datos numéricos provienen de las Tablas 2.B.11.3 a 2.B.11.7.
        """
        
        # Tabla 2.B.11.3 - Parámetros de cálculo de pH (C2, C3, C4)
        self.C2_table = {
            'temp_F': [33, 39, 46, 53, 60, 67, 76, 85, 94, 105, 117, 128, 140, 154, 170],
            'C2': [2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2]
        }
        self.C3_table = {
            'ca_hardness': [10.5, 12.5, 15.5, 20, 25, 31, 39, 49.5, 62.5, 78.5, 99, 124.5, 156.5, 197.5, 250, 310, 390, 495, 625, 785, 940],
            'C3': [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6]
        }
        self.C4_table = {
            'mo_alkalinity': [10.5, 12.5, 15.5, 20, 25, 31, 40, 50, 62.5, 79, 99.5, 125, 158, 197.5, 250, 315, 400, 500, 625, 790, 945],
            'C4': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]
        }

        # Tabla 2.B.11.4 - Tasa de Corrosión Base (CR_B) en mpy
        self.CRB_table = {
            'chlorides': [5, 10, 50, 100, 250, 500, 750, 1000, 2000, 3000, 5000, 10000],
            'crb_high': [1, 2, 4, 6, 9, 13, 15, 17, 17, 16, 15, 13],    # Para RSI > 6 o Vel > 8 ft/s
            'crb_low': [0.3, 0.6, 1.4, 2, 3, 4.3, 5, 5.7, 5.6, 5.4, 4.9, 4.3] # Para RSI <= 6 y Vel <= 8 ft/s
        }

        # Tabla 2.B.11.5 - Factor de ajuste por temperatura (F_T)
        self.FT_table = {
            'temp_F': [75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210],
            'ft_closed': [0.1, 0.3, 0.4, 0.6, 0.8, 0.9, 1.1, 1.2, 1.4, 1.6, 1.7, 1.9, 2.1, 2.2, 2.4, 2.5, 2.7, 2.9, 3.0, 3.2, 3.4, 3.5, 3.7, 3.8, 4.0, 4.2, 4.3, 4.5],
            'ft_open': [0.1, 0.3, 0.4, 0.6, 0.8, 0.9, 1.1, 1.2, 1.4, 1.6, 1.7, 1.9, 2.1, 2.2, 2.4, 2.5, 2.7, 2.9, 3.0, 3.2, 3.3, 3.3, 3.3, 3.3, 3.1, 2.9, 2.5, 1.7]
        }

        # Tabla 2.B.11.6 - Factor de ajuste por velocidad (F_V)
        self.FV_table = {
            'velocity_fts': [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'fv': [2.25, 2, 1.5, 1, 1, 1, 1, 1, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4]
        }

        # Tabla 2.B.11.7 - Tasa estimada para agua de mar según velocidad
        self.Seawater_table = {
            'velocity_fts': list(range(20)),
            'cr_mpy': [5.2, 8.7, 11.9, 14.9, 17.5, 19.9, 22.1, 24.1, 25.9, 27.5, 29.0, 30.4, 31.6, 32.7, 33.8, 34.7, 35.6, 36.4, 37.2, 38.0]
        }

    # Función auxiliar para interpolación lineal unidimensional
    def _interpolate(self, x, x_arr, y_arr):
        if x <= x_arr[0]: return y_arr[0]
        if x >= x_arr[-1]: return y_arr[-1]
        for i in range(len(x_arr) - 1):
            if x_arr[i] <= x <= x_arr[i+1]:
                x0, x1 = x_arr[i], x_arr[i+1]
                y0, y1 = y_arr[i], y_arr[i+1]
                return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

    def calculate_RSI(self, ph_a, tds, temp_F, ca_hardness, mo_alkalinity):
        """Calcula el índice de Ryznar (RSI)."""
        # Factor C1 según Tabla 2.B.11.3
        C1 = 0.1 if 50 <= tds <= 400 else 0.2 
        
        C2 = self._interpolate(temp_F, self.C2_table['temp_F'], self.C2_table['C2'])
        C3 = self._interpolate(ca_hardness, self.C3_table['ca_hardness'], self.C3_table['C3'])
        C4 = self._interpolate(mo_alkalinity, self.C4_table['mo_alkalinity'], self.C4_table['C4'])
        
        # Ecuación (2.B.11) implícita en la metodología
        ph_s = (9.3 + C1 + C2) - (C3 + C4)
        
        # Ecuación (2.B.10)
        RSI = 2 * ph_s - ph_a
        return RSI

    def evaluate_system(self, is_carbon_steel, is_recirculation, is_treated, is_seawater, 
                        temp_F, velocity_fts, tds=None, ca_hardness=None, 
                        mo_alkalinity=None, ph_a=None, chlorides=None, system_type="open"):
        """
        Evalúa el sistema siguiendo la lógica del diagrama de flujo Figure 2.B.11.1.
        """
        # 1. ¿Es Acero al carbono o de baja aleación?
        if not is_carbon_steel:
            return 0.5  # mpy

        # Lógica general si está tratado (Aplica a Recirculación y Once-Through de agua dulce)
        if is_treated and not is_seawater:
            return 3.0  # El flujograma indica "less than 3 mpy", usamos 3 como valor conservador

        # 2. Análisis por tipo de flujo
        if not is_recirculation and is_seawater:
            # Determine Estimated Corrosion Rate from Table 2.B.11.7
            return self._interpolate(velocity_fts, self.Seawater_table['velocity_fts'], self.Seawater_table['cr_mpy'])

        # 3. Flujo Untreated o Fresh Water (Cálculo completo con factores)
        if None in [tds, ca_hardness, mo_alkalinity, ph_a, chlorides]:
            raise ValueError("Faltan parámetros químicos (tds, ca_hardness, mo_alkalinity, ph_a, chlorides) para sistemas no tratados o de recirculación.")

        # Determinar RSI usando Eq 2.B.10
        RSI = self.calculate_RSI(ph_a, tds, temp_F, ca_hardness, mo_alkalinity)

        # Determinar Base Corrosion Rate (CR_B) desde Tabla 2.B.11.4
        if RSI > 6 or velocity_fts > 8:
            CR_B = self._interpolate(chlorides, self.CRB_table['chlorides'], self.CRB_table['crb_high'])
        else:
            CR_B = self._interpolate(chlorides, self.CRB_table['chlorides'], self.CRB_table['crb_low'])

        # Obtener F_T desde Tabla 2.B.11.5
        if system_type.lower() == "closed":
            F_T = self._interpolate(temp_F, self.FT_table['temp_F'], self.FT_table['ft_closed'])
        else:
            F_T = self._interpolate(temp_F, self.FT_table['temp_F'], self.FT_table['ft_open'])

        # Obtener F_V desde Tabla 2.B.11.6
        F_V = self._interpolate(velocity_fts, self.FV_table['velocity_fts'], self.FV_table['fv'])

        # Calcular Estimated Corrosion Rate con Eq 2.B.8 (CR_B * F_T * F_V)
        final_corrosion_rate = CR_B * F_T * F_V
        return final_corrosion_rate

# ==========================================
# EJEMPLO DE USO
# ==========================================
if __name__ == "__main__":
    corrosion_model = CoolingWaterCorrosion()
    
    # Ejemplo 1: Sistema Untreated Open Recirculating
    tasa_estimada_1 = corrosion_model.evaluate_system(
        is_carbon_steel=True,
        is_recirculation=True,
        is_treated=False,
        is_seawater=False,
        system_type="open",
        temp_F=120,          
        velocity_fts=5,      
        tds=300,             
        ca_hardness=150,     
        mo_alkalinity=100,   
        ph_a=7.5,            
        chlorides=500        
    )
    print(f"Ejemplo 1 (Recirculación, No tratado): {tasa_estimada_1:.2f} mpy")
    
    # Ejemplo 2: Once-Through Seawater
    tasa_estimada_2 = corrosion_model.evaluate_system(
        is_carbon_steel=True,
        is_recirculation=False,
        is_treated=False,
        is_seawater=True,
        temp_F=80,      # Irrelevante para el lookup de seawater según la tabla
        velocity_fts=12 # Interpolado de Tabla 2.B.11.7
    )
    print(f"Ejemplo 2 (Agua de mar, Once-through): {tasa_estimada_2:.2f} mpy")