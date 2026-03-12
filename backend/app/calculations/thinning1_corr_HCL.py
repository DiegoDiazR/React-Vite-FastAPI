import numpy as np
from scipy.interpolate import RegularGridInterpolator, interp1d

class HClCorrosionCalculator:
    """
    Calculador de tasas de corrosión por HCl basado en la metodología API 581.
    """
    
    def __init__(self):
        # --- DEFINICIÓN DE DATOS MAESTROS ---
        self.TEMPS = np.array([100, 125, 175, 200])
        self.PH_AXIS = np.array([0.5, 0.8, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75, 4.25, 4.75, 5.25, 5.75, 6.25, 6.8])
        self.CL_WT_AXIS = np.array([0.50, 0.75, 1.0])

        # Matrices de Corrosión (Filas = pH o Cl%, Columnas = Temperatura)
        self.DATA_CS = np.array([
            [999, 999, 999, 999], [900, 999, 999, 999], [400, 999, 999, 999],
            [200, 700, 999, 999], [100, 300, 400, 560], [60, 130, 200, 280],
            [40, 70, 100, 140], [30, 50, 90, 125], [20, 40, 70, 100],
            [10, 30, 50, 70], [7, 20, 30, 40], [4, 15, 20, 30],
            [3, 10, 15, 20], [2, 5, 7, 10]
        ])

        self.DATA_SS = np.array([
            [900, 999, 999, 999], [500, 999, 999, 999], [300, 500, 700, 999],
            [150, 260, 400, 500], [80, 140, 200, 250], [50, 70, 100, 120],
            [30, 40, 50, 65], [20, 25, 30, 35], [10, 15, 20, 25],
            [5, 7, 10, 12], [4, 5, 6, 7], [3, 4, 5, 6],
            [2, 3, 4, 5], [1, 2, 3, 4]
        ])

    def _get_ph_from_cl(self, cl_wppm):
        """Determina el pH discreto según Tabla 2.B.2.2."""
        if cl_wppm > 3600: return 0.5
        elif 1200 < cl_wppm <= 3600: return 1.0
        elif 360 < cl_wppm <= 1200:  return 1.5
        elif 120 < cl_wppm <= 360:   return 2.0
        elif 35 < cl_wppm <= 120:    return 2.5
        elif 15 < cl_wppm <= 35:     return 3.0
        elif 5 < cl_wppm <= 15:      return 3.5
        elif 2 < cl_wppm <= 5:       return 4.0
        elif 1 < cl_wppm <= 2:       return 4.5
        else: return 5.0

    def _interpolate_2d(self, x_points, y_points, data_matrix, x_val, y_val):
        """Interpolación bilineal para las tablas de tasas."""
        interp = RegularGridInterpolator((y_points, x_points), data_matrix, bounds_error=False, fill_value=None)
        resultado = interp([y_val, x_val])
        return float(resultado.item())

    def calcular_tasa(self, material, temp_f, ph=None, cl_wppm=None, oxigeno=False):
        """
        Calcula la tasa de corrosión siguiendo el flujo de decisión.
        """
        # material = material.upper()
        
        # RAMA 1: Aceros (Carbon Steel o 300 SS)
        if material in ['Carbon Steel', 
                        'Type 304 Series Stainless Steel', 
                        'Type 316 Series Stainless Steel', 
                        'Type 321 Series Stainless Steel', 
                        'Type 347 Series Stainless Steel']:
            if ph is None:
                if cl_wppm is not None:
                    ph = self._get_ph_from_cl(cl_wppm)
                else:
                    raise ValueError("Se requiere pH o cl_wppm para materiales ferrosos.")
            
            data = self.DATA_CS if 'Carbon Steel' in material else self.DATA_SS
            rate = self._interpolate_2d(self.TEMPS, self.PH_AXIS, data, temp_f, ph)

        # RAMA 2: Aleaciones Superiores
        else:
            cl_wt = cl_wppm / 10000.0 if cl_wppm is not None else 0.5
            
            if 'Alloy B-2' in material:
                matrix = np.array([[4,4,8,16], [4,4,20,80], [8,20,40,100]]) if oxigeno else \
                         np.array([[1,1,2,4], [1,1,5,20], [2,5,10,25]])
            elif 'Alloy 400' in material:
                matrix = np.array([[4,12,120,999], [10,20,320,999], [40,100,600,999]]) if oxigeno else \
                         np.array([[1,3,30,300], [2,5,80,800], [19,25,150,900]])
            elif 'Alloy 825' in material or 'Alloy 20' in material:
                matrix = np.array([[1, 3, 40, 200], [2, 5, 80, 400], [10, 70, 300, 999]])
            elif 'Alloy 625' in material:
                matrix = np.array([[1, 2, 15, 75], [1, 5, 25, 125], [2, 70, 200, 400]])
            elif 'Alloy C-276' in material:
                matrix = np.array([[1, 2, 8, 30], [1, 2, 15, 75], [2, 10, 60, 300]])
            else:
                raise ValueError(f"Material {material} no soportado para calculador de tasas de corrosión por HCl basado en la metodología API 581")

            rate = self._interpolate_2d(self.TEMPS, self.CL_WT_AXIS, matrix, temp_f, cl_wt)

        return round(float(np.clip(rate, 0, 999)), 2)

# --- USO DEL OBJETO ---
calculator = HClCorrosionCalculator()
tasa = calculator.calcular_tasa(material="Alloy B-2", temp_f=125, cl_wppm=35, oxigeno=True)
print(f"Resultado: {tasa} mpy")