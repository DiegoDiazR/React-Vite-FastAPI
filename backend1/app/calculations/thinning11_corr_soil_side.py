"""
Módulo Orientado a Objetos para el cálculo de la Tasa de Corrosión del Lado del Suelo 
(Soil-side Corrosion). Ajustado para °F y mpy. Basado en API 581.
"""

class CalculadoraCorrosionSuelo:
    # ==========================================
    # TABLAS DE REFERENCIA (Atributos de Clase)
    # ==========================================
    
    # Tabla 2.B.12.2 - Base Corrosion Rate (CR_B) en mpy
    TABLA_BASE_MPY = {
        "Arena": 1.0,   # Low chlorides, dry
        "Limo": 5.0,    # Moderate, variable moisture
        "Arcilla": 10.0 # High chlorides, saturated
    }
    
    # Tabla 2.B.12.5 - CP Effectiveness Factors (F_CP)
    TABLA_CP = {
        "Sin CP y con corrientes vagabundas": 10.0,
        "Sin CP": 1.0,
        "CP existe pero no evaluado / falla criterios": 0.8,
        "CP evaluado anualmente, pasa criterio 'on'": 0.4,
        "CP evaluado anualmente, pasa criterio polarizado ('instant-off')": 0.05
    }
    
    # Tabla 2.B.12.6 - Calculating the Total Coating Effectiveness Factor (F_CE)
    # Estructura: "Tipo": (Base, Edad > 20, Temp Excedida, Mantenimiento Raro/Nulo)
    TABLA_REVESTIMIENTOS = {
        "Epoxi adherido por fusion": (1.0, 1.1, 1.5, 1.1),
        "Epoxi liquido": (1.0, 1.1, 1.5, 1.1),
        "Esmalte de asfalto": (1.0, 1.1, 1.5, 1.1),
        "Masilla de asfalto": (1.0, 1.1, 1.5, 1.1),
        "Esmalte de alquitran de hulla": (1.0, 1.2, 2.0, 1.5),
        "PE extruido con masilla o caucho": (1.0, 1.2, 3.0, 1.5),
        "Cinta de PE con masilla (fabrica)": (1.5, 1.2, 3.0, 1.5),
        "Cinta de PE con masilla (campo)": (2.0, 2.0, 3.0, 1.5),
        "PE o PP de tres capas": (1.0, 1.2, 2.0, 1.2)
    }

    def __init__(self, tipo_suelo: str, temperatura_f: float, condicion_cp: str, 
                 resistividad_ohm_cm: float = None, resistividad_ya_considerada_en_base: bool = False,
                 tiene_revestimiento: bool = False, tipo_revestimiento: str = None,
                 edad_mayor_20: bool = False, temp_excedida: bool = False, mantenimiento_raro: bool = False):
        """
        Inicializa el objeto con las condiciones específicas del equipo y el suelo.
        """
        self.tipo_suelo = tipo_suelo
        self.temperatura_f = temperatura_f
        self.condicion_cp = condicion_cp
        self.resistividad_ohm_cm = resistividad_ohm_cm
        self.resistividad_ya_considerada_en_base = resistividad_ya_considerada_en_base
        self.tiene_revestimiento = tiene_revestimiento
        self.tipo_revestimiento = tipo_revestimiento
        self.edad_mayor_20 = edad_mayor_20
        self.temp_excedida = temp_excedida
        self.mantenimiento_raro = mantenimiento_raro

    # ==========================================
    # MÉTODOS PRIVADOS PARA CÁLCULO DE FACTORES
    # ==========================================

    def _obtener_tasa_base_corrosion(self) -> float:
        if self.tipo_suelo not in self.TABLA_BASE_MPY:
            raise ValueError(f"Tipo de suelo no válido. Opciones: {list(self.TABLA_BASE_MPY.keys())}")
        return self.TABLA_BASE_MPY[self.tipo_suelo]

    def _obtener_factor_resistividad(self) -> float:
        if self.resistividad_ya_considerada_en_base:
            return 1.0
        
        if self.resistividad_ohm_cm is None:
            raise ValueError("Debe proporcionar la resistividad del suelo si no está considerada en la tasa base.")
            
        res = self.resistividad_ohm_cm
        if res < 500: return 1.50
        elif 500 <= res <= 1000: return 1.25
        elif 1000 < res <= 2000: return 1.00
        elif 2000 < res <= 10000: return 0.83
        else: return 0.60

    def _obtener_factor_temperatura(self) -> float:
        if self.temperatura_f < 120: return 1.00
        elif 120 <= self.temperatura_f <= 220: return 2.00
        else: return 1.00

    def _obtener_factor_proteccion_catodica(self) -> float:
        if self.condicion_cp not in self.TABLA_CP:
            raise ValueError(f"Condición CP no válida. Opciones: {list(self.TABLA_CP.keys())}")
        return self.TABLA_CP[self.condicion_cp]

    def _obtener_factor_revestimiento(self) -> float:
        if not self.tiene_revestimiento:
            return 1.0

        if self.tipo_revestimiento not in self.TABLA_REVESTIMIENTOS:
            raise ValueError(f"Tipo de revestimiento no válido. Opciones: {list(self.TABLA_REVESTIMIENTOS.keys())}")

        f_base, f_edad_val, f_temp_val, f_mant_val = self.TABLA_REVESTIMIENTOS[self.tipo_revestimiento]

        f_edad = f_edad_val if self.edad_mayor_20 else 1.0
        f_temp = f_temp_val if self.temp_excedida else 1.0
        f_mant = f_mant_val if self.mantenimiento_raro else 1.0

        return f_base * f_edad * f_temp * f_mant

    # ==========================================
    # MÉTODO PÚBLICO PRINCIPAL
    # ==========================================

    def calcular(self) -> dict:
        """
        Ejecuta el cálculo aplicando la Ecuación (2.B.21) y retorna un diccionario con los resultados.
        """
        cr_base = self._obtener_tasa_base_corrosion()
        f_sr = self._obtener_factor_resistividad()
        f_t = self._obtener_factor_temperatura()
        f_cp = self._obtener_factor_proteccion_catodica()
        f_ce = self._obtener_factor_revestimiento()
        
        # Ecuación (2.B.21): CR = CR_B * F_SR * F_T * F_CP * F_CE
        cr_estimada = cr_base * f_sr * f_t * f_cp * f_ce
        
        return {
            "CR_Base (mpy)": cr_base,
            "F_SR (Resistividad)": f_sr,
            "F_T (Temperatura)": f_t,
            "F_CP (Proteccion Catodica)": f_cp,
            "F_CE (Revestimiento)": round(f_ce, 3),
            "Tasa de Corrosion Estimada Final (mpy)": round(cr_estimada, 2)
        }


# ==========================================
# EJEMPLO DE USO COMO OBJETO
# ==========================================
if __name__ == "__main__":
    
    # 1. Instanciamos el objeto con los parámetros del caso de estudio
    equipo_enterrado = CalculadoraCorrosionSuelo(
        tipo_suelo="Arcilla",                      
        resistividad_ohm_cm=800,                   
        resistividad_ya_considerada_en_base=False, 
        temperatura_f=150.0,                       
        condicion_cp="CP existe pero no evaluado / falla criterios", 
        tiene_revestimiento=True,                  
        tipo_revestimiento="Cinta de PE con masilla (fabrica)", 
        edad_mayor_20=True,                        
        temp_excedida=True,                        
        mantenimiento_raro=True                    
    )

    # 2. Llamamos al método calcular()
    print("--- Calculando Tasa de Corrosión Lado Suelo (OOP) ---")
    resultados = equipo_enterrado.calcular()

    # 3. Mostramos los resultados
    for clave, valor in resultados.items():
        print(f"{clave}: {valor}")