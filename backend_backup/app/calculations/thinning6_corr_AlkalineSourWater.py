import numpy as np
from scipy.interpolate import RegularGridInterpolator

class AlkalineSourWaterCorrosion:
    def __init__(self):
        """
        Inicializa los datos base a partir de la Tabla 2.B.7.2 
        (Alkaline Sour Water Corrosion—Baseline Corrosion Rates for Carbon Steel).
        """
        # Ejes de la tabla
        self.nh4hs_wt_pct = np.array([2.0, 5.0, 10.0, 15.0]) # Filas (wt %)
        self.velocity_fps = np.array([10.0, 15.0, 20.0, 25.0, 30.0]) # Columnas (ft/s)
        
        # Matriz de tasas de corrosión base (Baseline CR en mpy)
        self.baseline_cr_matrix = np.array([
            [3.0,   4.0,   5.0,   8.0,  11.0],  # Para 2 wt % NH4HS
            [6.0,   9.0,  12.0,  15.0,  18.0],  # Para 5 wt % NH4HS
            [20.0,  27.0,  35.0,  43.0,  50.0], # Para 10 wt % NH4HS
            [45.0,  70.0, 100.0, 150.0, 200.0]  # Para 15 wt % NH4HS
        ])
        
        # Función de interpolación 2D. 
        # bounds_error=False permite extrapolación lineal si los datos salen de la tabla.
        self._interpolator = RegularGridInterpolator(
            (self.nh4hs_wt_pct, self.velocity_fps), 
            self.baseline_cr_matrix, 
            bounds_error=False, 
            fill_value=None
        )

    @staticmethod
    def calculate_nh4hs_concentration(wt_h2s, wt_nh3):
        """
        Calcula la concentración aproximada de NH4HS si no se tiene medida directa.
        Basado en la Tabla 2.B.7.1.
        """
        if wt_h2s < 2.0 * wt_nh3:
            return 1.5 * wt_h2s
        else:
            return 3.0 * wt_nh3

    def calculate_corrosion_rate(self, nh4hs_pct, velocity, ph2s):
        """
        Calcula la tasa de corrosión ajustada siguiendo el diagrama de flujo de la Figura 2.B.7.1.
        
        Parámetros:
        - nh4hs_pct (float): Concentración de NH4HS (wt %)
        - velocity (float): Velocidad del flujo (ft/s)
        - ph2s (float): Presión parcial de H2S (psia)
        
        Retorna:
        - float: Tasa de corrosión estimada (mpy)
        """
        # 1. Determinar Baseline Corrosion Rate interpolando la Tabla 2.B.7.2
        # Extraemos el valor flotante del array devuelto por el interpolador
        baseline_cr = float(self._interpolator((nh4hs_pct, velocity)))
        
        # 2. Ajustar por presión parcial de H2S (Tabla 2.B.7.2, Notas 1 y 2)
        if ph2s < 50.0:
            # Nota 1: Para pH2S < 50 psia
            # Adjusted CR = max[ { (Baseline CR / 25) * (pH2S - 50) + Baseline CR }, 0 ]
            adjusted_cr = max( ((baseline_cr / 25.0) * (ph2s - 50.0)) + baseline_cr, 0.0 )
        else:
            # Nota 2: Para pH2S >= 50 psia
            # Adjusted CR = max[ { (Baseline CR / 40) * (pH2S - 50) + Baseline CR }, 0 ]
            adjusted_cr = max( ((baseline_cr / 40.0) * (ph2s - 50.0)) + baseline_cr, 0.0 )
            
        return adjusted_cr

# ==========================================
# Ejemplo de uso
# ==========================================
if __name__ == "__main__":
    # Inicializar la clase calculadora
    calculator = AlkalineSourWaterCorrosion()
    
    # --- Escenario 1: Uso directo con datos conocidos ---
    nh4hs = 10.0   # wt %
    vel = 20.0     # ft/s
    p_h2s = 60.0   # psia (Mayor a 50 psia -> Aplica Nota 2)
    
    cr_estimada = calculator.calculate_corrosion_rate(nh4hs, vel, p_h2s)
    print("--- Escenario 1 ---")
    print(f"NH4HS: {nh4hs} wt%, Velocidad: {vel} ft/s, p_H2S: {p_h2s} psia")
    print(f"Tasa de Corrosión Estimada: {cr_estimada:.2f} mpy\n")

    # --- Escenario 2: Datos que requieren interpolación y cálculo de NH4HS ---
    wt_h2s = 3.5   # wt %
    wt_nh3 = 2.0   # wt %
    vel_2 = 18.0   # ft/s (Requerirá interpolación entre 15 y 20 ft/s)
    p_h2s_2 = 30.0 # psia (Menor a 50 psia -> Aplica Nota 1)

    # Paso A: Estimar el NH4HS de acuerdo a la Tabla 2.B.7.1
    nh4hs_calc = calculator.calculate_nh4hs_concentration(wt_h2s, wt_nh3)
    
    # Paso B: Calcular la tasa de corrosión
    cr_estimada_2 = calculator.calculate_corrosion_rate(nh4hs_calc, vel_2, p_h2s_2)
    
    print("--- Escenario 2 ---")
    print(f"H2S: {wt_h2s} wt%, NH3: {wt_nh3} wt%")
    print(f"NH4HS Calculado: {nh4hs_calc:.2f} wt%")
    print(f"Velocidad: {vel_2} ft/s, p_H2S: {p_h2s_2} psia")
    print(f"Tasa de Corrosión Estimada: {cr_estimada_2:.2f} mpy")