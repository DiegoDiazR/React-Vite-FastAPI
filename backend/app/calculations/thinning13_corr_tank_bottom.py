class StorageTankBottomCorrosion:
    def __init__(self):
        # Tasas base por defecto en mpy (mils per year)
        self.DEFAULT_CR_SB = 5.0  # Base Soil-side corrosion rate
        self.DEFAULT_CR_PB = 2.0  # Base Product-side corrosion rate

    # ==========================================
    # TABLAS PARA EL LADO DEL SUELO (SOIL-SIDE)
    # ==========================================

    def get_f_sr(self, resistivity, has_rpb=False):
        """Table 2.B.14.4 - Soil-side Soil Resistivity Adjustment Factor"""
        if has_rpb:
            return 1.0  # Nota en el texto: factor de 1 si tiene RPB
        
        if resistivity < 500:
            return 1.5
        elif 500 <= resistivity <= 1000:
            return 1.25
        elif 1000 < resistivity <= 2000:
            return 1.0
        elif 2000 < resistivity <= 10000:
            return 0.83
        else: # > 10000
            return 0.66

    def get_f_pa(self, pad_type):
        """Table 2.B.14.5 - Soil-side Storage Tank Pad Adjustment Factor"""
        factors = {
            'soil_with_high_salt': 1.5,
            'crushed_limestone': 1.4,
            'native_soil': 1.3,
            'construction_grade_sand': 1.15,
            'continuous_asphalt': 1.0,
            'continuous_concrete': 1.0,
            'oil_sand': 0.7,
            'high_resistivity_low_chloride_sand': 0.7
        }
        return factors.get(pad_type.lower(), 1.0) # 1.0 por defecto si no se encuentra

    def get_f_td(self, drainage_type):
        """Table 2.B.14.6 - Soil-side Storage Tank Drainage Adjustment Factor"""
        factors = {
            'one_third_underwater': 3.0,
            'storm_water_collects': 2.0,
            'storm_water_does_not_collect': 1.0
        }
        return factors.get(drainage_type.lower(), 1.0)

    def get_f_cp(self, cp_type):
        """Table 2.B.14.7 - Soil-side CP Adjustment Factor"""
        factors = {
            'none': 1.0,
            'yes_not_per_api_651': 0.66,
            'yes_per_api_651': 0.33
        }
        return factors.get(cp_type.lower(), 1.0)

    def get_f_tb(self, bottom_type):
        """Table 2.B.14.8 - Soil-side AST Bottom Type Adjustment"""
        factors = {
            'rpb_not_per_api_650': 1.4,
            'rpb_per_api_650': 1.0,
            'single_bottom': 1.0
        }
        return factors.get(bottom_type.lower(), 1.0)

    def get_f_st(self, temp_f):
        """Table 2.B.14.9 - Soil-side Temperature Adjustment"""
        if temp_f <= 75:
            return 1.0
        elif 75 < temp_f <= 150:
            return 1.1
        elif 150 < temp_f <= 200:
            return 1.3
        elif 200 < temp_f <= 250:
            return 1.4
        else: # > 250
            return 1.0

    # ==============================================
    # TABLAS PARA EL LADO DEL PRODUCTO (PRODUCT-SIDE)
    # ==============================================

    def get_f_pc(self, condition):
        """Table 2.B.14.11 - Product-side Product Condition Adjustment"""
        factors = {
            'wet': 2.5,
            'dry': 1.0
        }
        return factors.get(condition.lower(), 1.0)

    def get_f_pt(self, temp_f):
        """Table 2.B.14.12 - Product-side Temperature Adjustment"""
        # Es exactamente la misma lógica que Soil-side (Table 2.B.14.9)
        return self.get_f_st(temp_f)

    def get_f_sc(self, has_steam_coil):
        """Table 2.B.14.13 - Product-side Steam Coil Adjustment"""
        return 1.15 if has_steam_coil else 1.0

    def get_f_wd(self, has_water_draw):
        """Table 2.B.14.14 - Product-side Water Draw-off Adjustment"""
        return 0.7 if has_water_draw else 1.0

    # ==========================================
    # FUNCIONES DE CÁLCULO PRINCIPALES
    # ==========================================

    def calculate_soil_side_rate(self, resistivity, pad_type, drainage_type, cp_type, 
                                 bottom_type, temp_f, has_rpb=False, cr_sb=None):
        """Calcula el CR_S - Ecuación (2.B.37)"""
        cr_sb = cr_sb if cr_sb is not None else self.DEFAULT_CR_SB
        
        f_sr = self.get_f_sr(resistivity, has_rpb)
        f_pa = self.get_f_pa(pad_type)
        f_td = self.get_f_td(drainage_type)
        f_cp = self.get_f_cp(cp_type)
        f_tb = self.get_f_tb(bottom_type)
        f_st = self.get_f_st(temp_f)

        cr_s = cr_sb * f_sr * f_pa * f_td * f_cp * f_tb * f_st
        return cr_s

    def calculate_product_side_rate(self, product_condition, temp_f, has_steam_coil, 
                                    has_water_draw, cr_pb=None):
        """Calcula el CR_P - Ecuación (2.B.38)"""
        cr_pb = cr_pb if cr_pb is not None else self.DEFAULT_CR_PB

        f_pc = self.get_f_pc(product_condition)
        f_pt = self.get_f_pt(temp_f)
        f_sc = self.get_f_sc(has_steam_coil)
        f_wd = self.get_f_wd(has_water_draw)

        cr_p = cr_pb * f_pc * f_pt * f_sc * f_wd
        return cr_p

    def calculate_combined_rate(self, cr_s, cr_p, is_product_generalized=False):
        """
        Calcula la tasa de corrosión combinada final.
        - Option 1: Generalized (Aditiva)
        - Option 2: Localized/Pitting (Se usa la mayor)
        El valor mínimo dictaminado por la norma es de 2 mpy.
        """
        if is_product_generalized:
            combined_cr = cr_s + cr_p
        else:
            combined_cr = max(cr_s, cr_p)

        # "it is recommended that the combined corrosion rate should not be set lower than 2 mils per year."
        return max(combined_cr, 2.0)


# ==========================================
# EJEMPLO DE USO
# ==========================================
if __name__ == "__main__":
    # Instanciamos la clase
    tank_corrosion_calc = StorageTankBottomCorrosion()

    # --- DATOS DE ENTRADA (Simulados) ---
    
    # Suelo (Soil-side)
    soil_resistivity = 1500           # Ohms-cm
    has_rpb = False                   # Release prevention barrier
    tank_pad_type = 'native_soil'     # Ver opciones en get_f_pa()
    drainage = 'storm_water_collects' # Ver opciones en get_f_td()
    cp = 'none'                       # Ver opciones en get_f_cp()
    bottom = 'single_bottom'          # Ver opciones en get_f_tb()
    oper_temp_f = 160                 # Temperatura en Fahrenheit

    # Producto (Product-side)
    prod_condition = 'wet'            # 'wet' o 'dry'
    steam_coil = True                 # True (Yes) o False (No)
    water_draw = False                # True (Yes) o False (No)
    
    # Tipo de corrosión interna (para determinar suma o máximo)
    is_generalized = False            # Falso = Localizada (Pitting)

    # --- CÁLCULOS ---
    cr_s = tank_corrosion_calc.calculate_soil_side_rate(
        resistivity=soil_resistivity, 
        pad_type=tank_pad_type, 
        drainage_type=drainage, 
        cp_type=cp, 
        bottom_type=bottom, 
        temp_f=oper_temp_f, 
        has_rpb=has_rpb
    )

    cr_p = tank_corrosion_calc.calculate_product_side_rate(
        product_condition=prod_condition, 
        temp_f=oper_temp_f, 
        has_steam_coil=steam_coil, 
        has_water_draw=water_draw
    )

    final_cr = tank_corrosion_calc.calculate_combined_rate(
        cr_s=cr_s, 
        cr_p=cr_p, 
        is_product_generalized=is_generalized
    )

    # --- RESULTADOS ---
    print(f"--- Tasa de Corrosión del Fondo del Tanque (mpy) ---")
    print(f"Soil-side Corrosion Rate (CR_S):    {cr_s:.2f} mpy")
    print(f"Product-side Corrosion Rate (CR_P): {cr_p:.2f} mpy")
    print(f"Corrosión Interna Generalizada:     {'Sí (Aditiva)' if is_generalized else 'No (Localizada, se usa el Máximo)'}")
    print(f"----------------------------------------------------")
    print(f"TASA DE CORROSIÓN FINAL ESTIMADA:   {final_cr:.2f} mpy")