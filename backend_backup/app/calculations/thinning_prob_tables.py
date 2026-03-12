# app/services/thinning_prob_tables.py

PRIOR_PROBABILITIES = {
    "low":    {"Prp1": 0.50, "Prp2": 0.30, "Prp3": 0.20},
    "medium": {"Prp1": 0.70, "Prp2": 0.20, "Prp3": 0.10},
    "high":   {"Prp1": 0.80, "Prp2": 0.15, "Prp3": 0.05},
}

CONDITIONAL_PROBABILITIES = {
    "E": {"C0p1": 0.33, "C0p2": 0.33, "C0p3": 0.33},
    "D": {"C0p1": 0.40, "C0p2": 0.33, "C0p3": 0.27},
    "C": {"C0p1": 0.50, "C0p2": 0.30, "C0p3": 0.20},
    "B": {"C0p1": 0.70, "C0p2": 0.20, "C0p3": 0.10},
    "A": {"C0p1": 0.90, "C0p2": 0.09, "C0p3": 0.01},
}

# Tabla 4.8 - Lining Condition Adjustment (F_LC)
LINING_CONDITION_MULTIPLIERS = {
    "Poor": 10,
    "Average": 2,
    "Good": 1,
}

# Tabla 4.7 - Internal Liner Types (Expected Age in years)
# Guardado como (min_age, max_age)
LINER_EXPECTED_LIFE_RANGES = {
    "Alloy strip liner": (5, 15),
    "Organic coating - low-quality": (1, 3),    # spray applied, to 40 mils
    "Organic coating - medium-quality": (3, 5), # filled, trowel applied, to 80 mils
    "Organic coating - high-quality": (5, 10),  # reinforced, trowel applied, >= 80 mils
    "Thermal resistance service - general": (1, 5),   # castable/plastic/brick/ceramic
    "Thermal resistance service - abrasive": (1, 5),  # castable/ceramic tile in highly abrasive service
    "Glass liners": (5, 10),
    "Acid brick": (10, 20),
}

# Tabla 4.9 - Online Monitoring Adjustment Factors (F_OM)
# Estructura: "Mecanismo": {"Key Process Variable": F_OM, "Electrical Resistance Probes": F_OM, "Corrosion Coupons": F_OM}
ONLINE_MONITORING_FACTORS = {
    "581-Hydrochloric Acid Corrosion": {
        "Key Process Variable": 10, 
        "Electrical Resistance Probes": 10,
        "Corrosion Coupons": 2
    },
    "581-High Temperature Sulfidic and Naphthenic Acid": {
        "Key Process Variable": 10,
        "Electrical Resistance Probes": 10,
        "Corrosion Coupons": 2
    },
    "581-Sulfuric Acid Corrosion": {
        "Key Process Variable": 10,
        "Electrical Resistance Probes": 10,
        "Corrosion Coupons": 1
    },
    "581-Hydrofluoric Acid Corrosion": {
        "Key Process Variable": 10,
        "Electrical Resistance Probes": 1,
        "Corrosion Coupons": 1
    },
    "581-Acid Sour Water Corrosion": {
        "Key Process Variable": 15,
        "Electrical Resistance Probes": 2,
        "Corrosion Coupons": 2
    },
    "581-Amine Corrosion": {
        "Key Process Variable": 10,
        "Electrical Resistance Probes": 10,
        "Corrosion Coupons": 1
    },
    "581-Thinning Damage": {
        "Key Process Variable": 1,
        "Electrical Resistance Probes": 1,
        "Corrosion Coupons": 1
    }
}