class CalculadoraOxidacionAltaTemp:
    """
    Clase para calcular la tasa de corrosión estimada (en mpy) para 
    oxidación a alta temperatura, basada en las Tablas 2.B.9.2 y 2.B.9.3.
    """
    
    # Los datos se convierten en un atributo de clase (compartido por todas las instancias)
    TABLAS_CORROSION = {
        "Carbon Steel": {
            925: 2, 975: 4, 1025: 6, 1075: 9, 1125: 14, 1175: 22, 1225: 33, 1275: 48,
            1325: None, 1375: None, 1425: None, 1475: None, 1525: None, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "1 1/4Cr": {
            925: 2, 975: 3, 1025: 4, 1075: 7, 1125: 12, 1175: 18, 1225: 30, 1275: 46,
            1325: None, 1375: None, 1425: None, 1475: None, 1525: None, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "2 1/4Cr": {
            925: 1, 975: 1, 1025: 2, 1075: 4, 1125: 9, 1175: 14, 1225: 24, 1275: 41,
            1325: None, 1375: None, 1425: None, 1475: None, 1525: None, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "5Cr": {
            925: 1, 975: 1, 1025: 1, 1075: 2, 1125: 4, 1175: 6, 1225: 15, 1275: 35,
            1325: 65, 1375: None, 1425: None, 1475: None, 1525: None, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "7Cr": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 2, 1225: 3, 1275: 6,
            1325: 17, 1375: 37, 1425: 60, 1475: None, 1525: None, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "9Cr": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 1, 1225: 1, 1275: 2,
            1325: 5, 1375: 11, 1425: 23, 1475: 40, 1525: 60, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "12Cr": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 1, 1225: 1, 1275: 1,
            1325: 3, 1375: 8, 1425: 15, 1475: 30, 1525: 50, 1575: None, 1625: None,
            1675: None, 1725: None, 1775: None, 1825: None, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "Type 304 Stainless Steel": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 1, 1225: 1, 1275: 1,
            1325: 1, 1375: 2, 1425: 3, 1475: 4, 1525: 6, 1575: 9, 1625: 13,
            1675: 18, 1725: 25, 1775: 35, 1825: 48, 1875: None, 1925: None, 1975: None, 2025: None, 2075: None
        },
        "Type 309 Stainless Steel": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 1, 1225: 1, 1275: 1,
            1325: 1, 1375: 1, 1425: 2, 1475: 3, 1525: 4, 1575: 6, 1625: 8,
            1675: 10, 1725: 13, 1775: 16, 1825: 20, 1875: 30, 1925: 40, 1975: 50, 2025: None, 2075: None
        },
        "310 SS/HK": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 1, 1225: 1, 1275: 1,
            1325: 1, 1375: 1, 1425: 1, 1475: 2, 1525: 3, 1575: 4, 1625: 5,
            1675: 7, 1725: 8, 1775: 10, 1825: 13, 1875: 15, 1925: 19, 1975: 23, 2025: 27, 2075: 31
        },
        "800 H/HP": {
            925: 1, 975: 1, 1025: 1, 1075: 1, 1125: 1, 1175: 1, 1225: 1, 1275: 1,
            1325: 1, 1375: 1, 1425: 1, 1475: 2, 1525: 3, 1575: 4, 1625: 6,
            1675: 8, 1725: 10, 1775: 13, 1825: 17, 1875: 21, 1925: 27, 1975: 33, 2025: 41, 2075: 50
        }
    }

    def __init__(self):
        # Puedes añadir configuraciones iniciales aquí si lo deseas en el futuro
        pass

    def obtener_materiales_soportados(self) -> list:
        """Devuelve una lista con los nombres de los materiales soportados."""
        return list(self.TABLAS_CORROSION.keys())

    def calcular_tasa(self, material: str, temperatura_f: float) -> str:
        """
        Determina la tasa de corrosión estimada (en mpy) para oxidación a alta temperatura.
        Sigue el flujo de la Figura 2.B.9.1.
        """
        if material not in self.TABLAS_CORROSION:
            return f"Error: El material '{material}' no se encuentra en las tablas."

        datos_material = self.TABLAS_CORROSION[material]
        temperaturas_disponibles = sorted(datos_material.keys())
        
        # Validar límites (según sección 2.B.9.1 ocurre usualmente por encima de 900°F)
        temp_min = temperaturas_disponibles[0]
        temp_max = temperaturas_disponibles[-1]

        if temperatura_f < temp_min:
            return f"Temperatura menor a {temp_min}°F. La corrosión por oxidación a alta temp. suele ser mínima/despreciable."
        
        if temperatura_f > temp_max:
            return f"Fuera de rango. Temperatura excede el máximo tabulado ({temp_max}°F)."

        # 1. Búsqueda exacta
        if temperatura_f in datos_material:
            tasa = datos_material[temperatura_f]
            if tasa is None:
                return "Datos no disponibles (—) para esta temperatura. El material puede no ser apto."
            return f"{tasa} mpy"

        # 2. Interpolación lineal si la temperatura está entre dos columnas de la tabla
        temp_inferior = max([t for t in temperaturas_disponibles if t < temperatura_f])
        temp_superior = min([t for t in temperaturas_disponibles if t > temperatura_f])
        
        tasa_inf = datos_material[temp_inferior]
        tasa_sup = datos_material[temp_superior]
        
        if tasa_inf is None or tasa_sup is None:
            return "Interpolación imposible: Faltan datos en los extremos cercanos (probablemente límite operativo excedido)."
            
        # Calcular interpolación lineal: y = y1 + ((x - x1) / (x2 - x1)) * (y2 - y1)
        tasa_interpolada = tasa_inf + ((temperatura_f - temp_inferior) / (temp_superior - temp_inferior)) * (tasa_sup - tasa_inf)
        
        return f"{round(tasa_interpolada, 1)} mpy (Valor interpolado)"


# ==========================================
# EJEMPLO DE USO (Instanciación del Objeto)
# ==========================================
if __name__ == "__main__":
    # 1. Instanciamos el objeto
    calculadora = CalculadoraOxidacionAltaTemp()
    
    print("--- Objeto Calculadora Creado ---")
    
    # Podemos listar los materiales para que el usuario o el sistema sepa qué opciones hay
    print("Materiales soportados:", calculadora.obtener_materiales_soportados())
    print("-" * 50)
    
    # 2. Usamos el método interno para calcular
    print(f"Acero al Carbono (CS) a 1225°F: {calculadora.calcular_tasa('Carbon Steel', 1225)}")
    print(f"9Cr a 1525°F: {calculadora.calcular_tasa('1 1/4Cr', 1275)}")
    print(f"304 SS a 1875°F: {calculadora.calcular_tasa('Type 304 Stainless Steel', 1875)}")
    print(f"5Cr a 1000°F: {calculadora.calcular_tasa('5Cr', 1000)}")
    print(f"CS a 1500°F: {calculadora.calcular_tasa('Carbon Steel', 1500)}")
    print(f"Material Falso a 1000°F: {calculadora.calcular_tasa('Inconel', 1000)}")