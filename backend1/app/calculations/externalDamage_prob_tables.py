# cui_prob_tables.py

# Tabla 2.D.3.2M - Tasas de Corrosión Base (mm/y) según Temperatura y Driver
# Estructura: { temperatura_c: [Severe, Moderate, Mild, Dry] }
# CUI_CORROSION_RATES = {
#     10:  [0.000, 0.000, 0.000, 0.000],
#     18:  [3.000, 1.000, 0.000, 0.000],
#     43:  [10.00, 5.000, 3.000, 1.000],
#     90:  [10.00, 5.000, 3.000, 1.000],
#     160: [20.00, 10.00, 5.000, 2.000],
#     225: [10.00, 5.000, 1.000, 1.000],
#     275: [10.00, 2.000, 1.000, 0.000],
#     325: [5.000, 1.000, 0.000, 0.000],
#     350: [0.000, 0.000, 0.000, 0.000],
# }

CUI_CORROSION_RATES = {
    10:  [0.0000, 0.0000, 0.0000, 0.0000],
    18:  [0.0030, 0.0010, 0.0000, 0.0000],
    43:  [0.0100, 0.0050, 0.0030, 0.0010],
    90:  [0.0100, 0.0050, 0.0030, 0.0010],
    160: [0.0200, 0.0100, 0.0050, 0.0020],
    225: [0.0100, 0.0050, 0.0010, 0.0010],
    275: [0.0100, 0.0020, 0.0010, 0.0000],
    325: [0.0050, 0.0010, 0.0000, 0.0000],
    350: [0.0000, 0.0000, 0.0000, 0.0000],
}

# Tabla 2.D.3.3 - Factor de Ajuste por Tipo de Aislamiento (F_INS) [cite: 312]
INSULATION_TYPE_FACTORS = {
    "Unknown/unspecified": 1.5,
    "Asbestos": 1.5,
    "Cellular glass": 0.75,
    "Expanded perlite": 1.0,
    "Fiberglass": 1.25,
    "Type E fiberglass": 1.25,
    "Mineral wool": 1.5,
    "Mineral wool (water resistant)": 1.25,
    "Calcium silicate": 1.25,
    "Flexible aerogel": 1.25,
    "Microporous blanket": 1.0,
    "Intumescent coating": 0.75,
    "Cementitious coating": 1.0,
}

# Factores de Ajuste por Complejidad (F_CM) [cite: 201-203]
COMPLEXITY_FACTORS = {
    "Below Average": 0.75,
    "Average": 1.0,
    "Above Average": 1.25,
}

# Factores de Ajuste por Condición de Aislamiento (F_IC) [cite: 208-210]
INSULATION_CONDITION_FACTORS = {
    "Below Average": 1.25,
    "Average": 1.0,
    "Above Average": 0.75,
}

# Factores de Ajuste por Diseño de Equipo e Interface [cite: 211, 212]
EQUIPMENT_DESIGN_FACTORS = {"Yes": 2.0, "No": 1.0}
INTERFACE_FACTORS = {"Yes": 2.0, "No": 1.0}

# Probabilidades de Inspección (Mismas de Thinning según API 581 Step 15) [cite: 269]
# Se incluyen aquí para independencia del módulo
PRIOR_PROBABILITIES_CUI = {
    "low": {"Prp1": 0.5, "Prp2": 0.3, "Prp3": 0.2},
    "medium": {"Prp1": 0.7, "Prp2": 0.2, "Prp3": 0.1},
    "high": {"Prp1": 0.8, "Prp2": 0.15, "Prp3": 0.05},
}

CONDITIONAL_PROBABILITIES_CUI = {
    "E": {"C0p1": 0.33, "C0p2": 0.33, "C0p3": 0.33},
    "D": {"C0p1": 0.40, "C0p2": 0.33, "C0p3": 0.27},
    "C": {"C0p1": 0.50, "C0p2": 0.30, "C0p3": 0.20},
    "B": {"C0p1": 0.70, "C0p2": 0.20, "C0p3": 0.10},
    "A": {"C0p1": 0.90, "C0p2": 0.09, "C0p3": 0.01},
}