# """
# API 581  4th Edition
# STEP 4.1  Determine the Representative Fluid and Associated Properties

# Implements:
# - 4.1.1 Representative Fluid selection (Table 4.1)
# - 4.1.2 Fluid Properties (Table 4.2)
# - 4.1.3 Ideal Gas Cp and k estimation (Eq. 3.1)
# - 4.1.4 Release phase determination (Table 4.3)

# This module performs NO consequence calculations.
# """

# from typing import Dict, Optional
# from dataclasses import dataclass
# import math

# # ---------------------------------------------------------------------
# # Constants
# # ---------------------------------------------------------------------

# R_UNIVERSAL = 8.314  # J/(mol·K) = kJ/(kmol·K)

# # ---------------------------------------------------------------------
# # Representative Fluids – Table 4.1 (keys only, examples handled outside)
# # ---------------------------------------------------------------------

# REPRESENTATIVE_FLUIDS = {
#     "C1-C2": {"fluid_type": "Type 0"},
#     "C3-C4": {"fluid_type": "Type 0"},
#     "C5": {"fluid_type": "Type 0"},
#     "C6-C8": {"fluid_type": "Type 0"},
#     "C9-C12": {"fluid_type": "Type 0"},
#     "C13-C16": {"fluid_type": "Type 0"},
#     "C17-C25": {"fluid_type": "Type 0"},
#     "C25+": {"fluid_type": "Type 0"},
#     "H2": {"fluid_type": "Type 0"},
#     "H2S": {"fluid_type": "Type 0"},
#     "HF": {"fluid_type": "Type 0"},
#     "HCl": {"fluid_type": "Type 0"},
#     "Water": {"fluid_type": "Type 0"},
#     "Steam": {"fluid_type": "Type 0"},
#     "Acid/Caustic": {"fluid_type": "Type 0"},
#     "Aromatics": {"fluid_type": "Type 1"},
#     "CO": {"fluid_type": "Type 1"},
#     "DEE": {"fluid_type": "Type 1"},
#     "Methanol": {"fluid_type": "Type 1"},
#     "PO": {"fluid_type": "Type 1"},
#     "Styrene": {"fluid_type": "Type 1"},
#     "EEA": {"fluid_type": "Type 1"},
#     "EE": {"fluid_type": "Type 1"},
#     "EG": {"fluid_type": "Type 1"},
#     "EO": {"fluid_type": "Type 1"},
# }

# # ---------------------------------------------------------------------
# # Fluid Properties – Table 4.2 (example structure)
# # Units MUST be consistent with API table
# # ---------------------------------------------------------------------

# # API 581 – Table 4.2
# # TABLA 4.2 COMPLETA - API 581 4th Edition
# FLUID_PROPERTIES = {
#     # --- Nota 1: Cp = A + BT + CT^2 + DT^3 [J/(mol·K)] ---
#     "C1-C2": {"mw": 23, "rho": 15.639, "nbp": -193, "state": "Gas", "ait": 1036, "cp": {"n": 1, "A": 12.3, "B": 1.15E-01, "C": -2.87E-05, "D": -1.30E-09, "E": 0}},
#     "C3-C4": {"mw": 51, "rho": 33.61, "nbp": -6.3, "state": "Gas", "ait": 696, "cp": {"n": 1, "A": 2.632, "B": 0.3188, "C": -1.347E-04, "D": 1.466E-08, "E": 0}},
#     "C5": {"mw": 72, "rho": 39.03, "nbp": 97, "state": "Liquid", "ait": 544, "cp": {"n": 1, "A": -3.626, "B": 0.4873, "C": -2.60E-04, "D": 5.30E-08, "E": 0}},
#     "C6-C8": {"mw": 100, "rho": 42.702, "nbp": 210, "state": "Liquid", "ait": 433, "cp": {"n": 1, "A": -5.146, "B": 0.6762, "C": -3.65E-04, "D": 7.658E-08, "E": 0}},
#     "C9-C12": {"mw": 149, "rho": 45.823, "nbp": 364, "state": "Liquid", "ait": 406, "cp": {"n": 1, "A": -8.5, "B": 1.01, "C": -5.56E-04, "D": 1.180E-07, "E": 0}},
#     "C13-C16": {"mw": 205, "rho": 47.728, "nbp": 502, "state": "Liquid", "ait": 396, "cp": {"n": 1, "A": -11.7, "B": 1.39, "C": -7.72E-04, "D": 1.670E-07, "E": 0}},
#     "C17-C25": {"mw": 280, "rho": 48.383, "nbp": 651, "state": "Liquid", "ait": 396, "cp": {"n": 1, "A": -22.4, "B": 1.94, "C": -1.12E-03, "D": -2.53E-07, "E": 0}},
#     "C25+": {"mw": 422, "rho": 56.187, "nbp": 981, "state": "Liquid", "ait": 396, "cp": {"n": 1, "A": -22.4, "B": 1.94, "C": -1.12E-03, "D": -2.53E-07, "E": 0}},
#     "Pyrophoric": {"mw": 149, "rho": 45.823, "nbp": 364, "state": "Liquid", "ait": 0, "cp": {"n": 1, "A": -8.5, "B": 1.01, "C": -5.56E-04, "D": 1.180E-07, "E": 0}},
#     "Ammonia": {"mw": 17.03, "rho": 38.55, "nbp": -28.2, "state": "Gas", "ait": 1204, "cp": {"n": 1, "A": 27.26, "B": 2.31E-04, "C": 2.24E-07, "D": 2.17E-10, "E": 5.41E-14}},
#     "H2": {"mw": 2, "rho": 4.433, "nbp": -423, "state": "Gas", "ait": 752, "cp": {"n": 1, "A": 27.1, "B": 9.27E-03, "C": -1.38E-05, "D": 7.65E-09, "E": 0}},
#     "H2S": {"mw": 34, "rho": 61.993, "nbp": -75, "state": "Gas", "ait": 500, "cp": {"n": 1, "A": 31.9, "B": 1.44E-03, "C": 2.43E-05, "D": -1.18E-08, "E": 0}},
#     "HF": {"mw": 20, "rho": 60.37, "nbp": 68, "state": "Gas", "ait": 32000, "cp": {"n": 1, "A": 29.1, "B": 6.61E-04, "C": -2.03E-06, "D": 2.50E-09, "E": 0}},
#     "AlCl3": {"mw": 133.5, "rho": 152, "nbp": 382, "state": "Powder", "ait": 1036, "cp": {"n": 1, "A": 64.9, "B": 8.74E+01, "C": 1.82E-02, "D": -4.65E-04, "E": 0}},

#     # --- Nota 2: Ecuación Hiperbólica [J/(kmol·K)] ---
#     "Aromatic": {"mw": 104, "rho": 42.7, "nbp": 293, "state": "Liquid", "ait": 914, "cp": {"n": 2, "A": 8.93E+04, "B": 2.15E+05, "C": 7.72E+02, "D": 9.99E+04, "E": 2.44E+03}},
#     "Styrene": {"mw": 104, "rho": 42.7, "nbp": 293, "state": "Liquid", "ait": 914, "cp": {"n": 2, "A": 8.93E+04, "B": 2.15E+05, "C": 7.72E+02, "D": 9.99E+04, "E": 2.44E+03}},
#     "Steam": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Gas", "ait": 0, "cp": {"n": 2, "A": 3.34E+04, "B": 2.68E+04, "C": 2.61E+03, "D": 8.90E+03, "E": 1.17E+03}},
#     "Methanol": {"mw": 32, "rho": 50, "nbp": 149, "state": "Liquid", "ait": 867, "cp": {"n": 2, "A": 3.93E+04, "B": 8.79E+04, "C": 1.92E+03, "D": 5.37E+04, "E": 8.97E+02}},
#     "CO": {"mw": 28, "rho": 50, "nbp": -312, "state": "Gas", "ait": 1128, "cp": {"n": 2, "A": 2.91E+04, "B": 8.77E+03, "C": 3.09E+03, "D": 8.46E+03, "E": 1.54E+03}},
#     "DEE": {"mw": 74, "rho": 45, "nbp": 95, "state": "Liquid", "ait": 320, "cp": {"n": 2, "A": 8.62E+04, "B": 2.55E+05, "C": 1.54E+03, "D": 1.44E+05, "E": -6.89E+02}},
#     "PO": {"mw": 58, "rho": 52, "nbp": 93, "state": "Liquid", "ait": 840, "cp": {"n": 2, "A": 4.95E+04, "B": 1.74E+05, "C": 1.56E+03, "D": 1.15E+05, "E": 7.02E+02}},
#     "EEA": {"mw": 132, "rho": 61, "nbp": 313, "state": "Liquid", "ait": 715, "cp": {"n": 2, "A": 1.06E+05, "B": 2.40E+05, "C": 6.59E+02, "D": 1.50E+05, "E": 1.97E+03}},
#     "EE": {"mw": 90, "rho": 58, "nbp": 275, "state": "Liquid", "ait": 455, "cp": {"n": 2, "A": 3.25E+04, "B": 3.00E+05, "C": 1.17E+03, "D": 2.08E+05, "E": 4.73E+02}},
#     "EG": {"mw": 62, "rho": 69, "nbp": 387, "state": "Liquid", "ait": 745, "cp": {"n": 2, "A": 6.30E+04, "B": 1.46E+05, "C": 1.67E+03, "D": 9.73E+04, "E": 7.74E+02}},
#     "EO": {"mw": 44, "rho": 55, "nbp": 51, "state": "Gas", "ait": 804, "cp": {"n": 2, "A": 3.35E+04, "B": 1.21E+05, "C": 1.61E+03, "D": 8.24E+04, "E": 7.37E+02}},

#     # --- Nota 3: Polinómica Extendida [J/(kmol·K)] ---
#     "Water": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
#     "Acid/caustic-LP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
#     "Acid/caustic-MP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
#     "Acid/caustic-HP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},

#     # --- Fluidos sin constantes de Cp ---
#     "HCl": {"mw": 36, "rho": 74, "nbp": -121, "state": "Gas", "ait": 0, "cp": None},
#     "Nitric acid": {"mw": 63, "rho": 95, "nbp": 250, "state": "Liquid", "ait": 0, "cp": None},
#     "NO2": {"mw": 46, "rho": 58, "nbp": 275, "state": "Liquid", "ait": 0, "cp": None},
#     "Phosgene": {"mw": 99, "rho": 86, "nbp": 181, "state": "Liquid", "ait": 0, "cp": None},
#     "TDI": {"mw": 174, "rho": 76, "nbp": 484, "state": "Liquid", "ait": 1148, "cp": None},
# }

# # ---------------------------------------------------------------------
# # Dataclass for structured output
# # ---------------------------------------------------------------------

# @dataclass
# class Step41Result:
#     representative_fluid: str
#     fluid_type: str
#     stored_phase: str
#     ambient_phase: str
#     final_release_phase: str
#     properties: Dict
#     trace: Dict

# # ---------------------------------------------------------------------
# # Cp and gamma (k) estimation – Eq. (3.1)
# # ---------------------------------------------------------------------

# def calculate_cp(cp_data: Dict, T_k: float) -> float:
#     """Calcula Cp en J/(mol·K)"""
#     n = cp_data["n"]
#     A, B, C, D, E = cp_data["A"], cp_data["B"], cp_data["C"], cp_data["D"], cp_data.get("E", 0)

#     if n == 1:
#         # Polinómica: resultado directo en J/(mol·K) según Nota 6
#         return A + B*T_k + C*(T_k**2) + D*(T_k**3)
    
#     elif n == 2:
#         # Hiperbólica: resultado en J/(kmol·K), dividimos por 1000
#         term1 = (C/T_k) / math.sinh(C/T_k) if T_k > 0 else 0
#         term2 = (E/T_k) / math.cosh(E/T_k) if (T_k > 0 and E > 0) else 0
#         cp_kmol = A + B*(term1**2) + D*(term2**2)
#         return cp_kmol / 1000.0

#     elif n == 3:
#         # Polinómica extendida: resultado en J/(kmol·K), dividimos por 1000
#         cp_kmol = A + B*T_k + C*(T_k**2) + D*(T_k**3) + E*(T_k**4)
#         return cp_kmol / 1000.0

#     return 0.0

# def calculate_gamma(cp_j_per_mol_k: float) -> float:
#     """
#     k = Cp / (Cp - R)
#     """
#     # R_UNIVERSAL es 8.314 J/(mol·K)
#     cv_molar = cp_j_per_mol_k - R_UNIVERSAL
    
#     if cv_molar <= 0:
#         return 1.4 # Valor por defecto seguro si el cálculo falla
        
#     return cp_j_per_mol_k / cv_molar

# # ---------------------------------------------------------------------
# # Table 4.3 – Final Release Phase Determination
# # ---------------------------------------------------------------------

# def determine_final_release_phase(stored_phase: str, ambient_phase: str, nbp_f: float) -> str:
#     if stored_phase == "Gas":
#         return "Gas"
#     if ambient_phase == "Liquid":
#         return "Liquid"
#     return "Liquid" if nbp_f > 80.0 else "Gas"

# # ---------------------------------------------------------------------
# # Main STEP 4.1 function
# # ---------------------------------------------------------------------

# def step_4_1_determine_representative_fluid(
#     representative_fluid: str, stored_phase: str, ambient_phase: str, temperature_k: Optional[float] = None
# ) -> Step41Result:
#     if representative_fluid not in FLUID_PROPERTIES:
#         raise ValueError(f"Fluido '{representative_fluid}' no encontrado en la Tabla 4.2.")

#     props = FLUID_PROPERTIES[representative_fluid]
#     fluid_type = REPRESENTATIVE_FLUIDS[representative_fluid]["fluid_type"]

#     # Determinación de fase final (Tabla 4.3)
#     if stored_phase == "Gas":
#         final_phase = "Gas"
#     elif ambient_phase == "Liquid":
#         final_phase = "Liquid"
#     else:
#         final_phase = "Liquid" if props["nbp"] > 80.0 else "Gas"

#     # Cálculo termodinámico si es gas
#     cp, gamma = None, None
#     if props["cp"] and temperature_k:
#         cp = calculate_cp(props["cp"], temperature_k)
#         gamma = cp / (cp - R_UNIVERSAL) if cp > R_UNIVERSAL else 1.4

#     return Step41Result(
#         representative_fluid=representative_fluid,
#         fluid_type=fluid_type,
#         stored_phase=stored_phase,
#         ambient_phase=ambient_phase,
#         final_release_phase=final_phase,
#         properties=props,
#         trace={"gamma_calc": gamma, "cp_calc": cp}
#     )


"""
API 581 4th Edition
STEP 4.1 Determine the Representative Fluid and Associated Properties

Implements:
- 4.1.1 Representative Fluid selection (Table 4.1)
- 4.1.2 Fluid Properties (Table 4.2)
- 4.1.3 Ideal Gas Cp and k estimation (Eq. 3.1)
- 4.1.4 Release phase determination (Table 4.3)
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
import math

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
R_UNIVERSAL = 8.314  # J/(mol·K)
AMBIENT_TEMP_CUTOFF_F = 80.0  # Threshold from Table 4.3 to decide Gas/Liquid phase

# ---------------------------------------------------------------------
# Representative Fluids Map
# ---------------------------------------------------------------------
REPRESENTATIVE_FLUIDS = {
    "C1-C2": "Type 0", 
    "C3-C4": "Type 0", 
    "C5": "Type 0", 
    "C6-C8": "Type 0",
    "C9-C12": "Type 0", 
    "C13-C16": "Type 0", 
    "C17-C25": "Type 0", 
    "C25+": "Type 0",
    "H2": "Type 0", 
    "H2S": "Type 0", 
    "HF": "Type 0", 
    "HCl": "Type 0",
    "Water": "Type 0", 
    "Steam": "Type 0",
    "Acid/caustic-LP": "Type 0", 
    "Acid/caustic-MP": "Type 0", 
    "Acid/caustic-HP": "Type 0",
    "Aromatic": "Type 1", 
    "CO": "Type 1", 
    "DEE": "Type 1", 
    "Methanol": "Type 1",
    "PO": "Type 1", 
    "Styrene": "Type 1", 
    "EEA": "Type 1", 
    "EE": "Type 1",
    "EG": "Type 1", 
    "EO": "Type 1", 
    "Nitric acid": "Type 0", 
    "NO2": "Type 0",
    "Phosgene": "Type 0", 
    "TDI": "Type 0", 
    "Ammonia": "Type 0",
    "Chlorine": "Type 0", 
    "AlCl3": "Type 0", 
    "Pyrophoric": "Type 0",
}

# ---------------------------------------------------------------------
# Fluid Properties – Table 4.2
# ---------------------------------------------------------------------
FLUID_PROPERTIES = {
    "C1-C2": {"mw": 23, "rho": 15.639, "nbp": -193, "state": "Gas", "ait": 1036, "cp": {"n": 1, "A": 12.3, "B": 1.15E-01, "C": -2.87E-05, "D": -1.30E-09, "E": 0}},
    "C3-C4": {"mw": 51, "rho": 33.61, "nbp": -6.3, "state": "Gas", "ait": 696, "cp": {"n": 1, "A": 2.632, "B": 0.3188, "C": -1.347E-04, "D": 1.466E-08, "E": 0}},
    "C5": {"mw": 72, "rho": 39.03, "nbp": 97, "state": "Liquid", "ait": 544, "cp": {"n": 1, "A": -3.626, "B": 0.4873, "C": -2.60E-04, "D": 5.30E-08, "E": 0}},
    "C6-C8": {"mw": 100, "rho": 42.702, "nbp": 210, "state": "Liquid", "ait": 433, "cp": {"n": 1, "A": -5.146, "B": 0.6762, "C": -3.65E-04, "D": 7.658E-08, "E": 0}},
    "C9-C12": {"mw": 149, "rho": 45.823, "nbp": 364, "state": "Liquid", "ait": 406, "cp": {"n": 1, "A": -8.5, "B": 1.01, "C": -5.56E-04, "D": 1.180E-07, "E": 0}},
    "C13-C16": {"mw": 205, "rho": 47.728, "nbp": 502, "state": "Liquid", "ait": 396, "cp": {"n": 1, "A": -11.7, "B": 1.39, "C": -7.72E-04, "D": 1.670E-07, "E": 0}},
    "C17-C25": {"mw": 280, "rho": 48.383, "nbp": 651, "state": "Liquid", "ait": 396, "cp": {"n": 1, "A": -22.4, "B": 1.94, "C": -1.12E-03, "D": -2.53E-07, "E": 0}},
    "C25+": {"mw": 422, "rho": 56.187, "nbp": 981, "state": "Liquid", "ait": 396, "cp": {"n": 1, "A": -22.4, "B": 1.94, "C": -1.12E-03, "D": -2.53E-07, "E": 0}},
    "Pyrophoric": {"mw": 149, "rho": 45.823, "nbp": 364, "state": "Liquid", "ait": 0, "cp": {"n": 1, "A": -8.5, "B": 1.01, "C": -5.56E-04, "D": 1.180E-07, "E": 0}},
    "Ammonia": {"mw": 17.03, "rho": 38.55, "nbp": -28.2, "state": "Gas", "ait": 1204, "cp": {"n": 1, "A": 27.26, "B": 2.31E-04, "C": 2.24E-07, "D": 2.17E-10, "E": 5.41E-14}},
    "H2": {"mw": 2, "rho": 4.433, "nbp": -423, "state": "Gas", "ait": 752, "cp": {"n": 1, "A": 27.1, "B": 9.27E-03, "C": -1.38E-05, "D": 7.65E-09, "E": 0}},
    "H2S": {"mw": 34, "rho": 61.993, "nbp": -75, "state": "Gas", "ait": 500, "cp": {"n": 1, "A": 31.9, "B": 1.44E-03, "C": 2.43E-05, "D": -1.18E-08, "E": 0}},
    "HF": {"mw": 20, "rho": 60.37, "nbp": 68, "state": "Gas", "ait": 32000, "cp": {"n": 1, "A": 29.1, "B": 6.61E-04, "C": -2.03E-06, "D": 2.50E-09, "E": 0}},
    "AlCl3": {"mw": 133.5, "rho": 152, "nbp": 382, "state": "Powder", "ait": 1036, "cp": {"n": 1, "A": 64.9, "B": 8.74E+01, "C": 1.82E-02, "D": -4.65E-04, "E": 0}},
    "Aromatic": {"mw": 104, "rho": 42.7, "nbp": 293, "state": "Liquid", "ait": 914, "cp": {"n": 2, "A": 8.93E+04, "B": 2.15E+05, "C": 7.72E+02, "D": 9.99E+04, "E": 2.44E+03}},
    "Styrene": {"mw": 104, "rho": 42.7, "nbp": 293, "state": "Liquid", "ait": 914, "cp": {"n": 2, "A": 8.93E+04, "B": 2.15E+05, "C": 7.72E+02, "D": 9.99E+04, "E": 2.44E+03}},
    "Steam": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Gas", "ait": 0, "cp": {"n": 2, "A": 3.34E+04, "B": 2.68E+04, "C": 2.61E+03, "D": 8.90E+03, "E": 1.17E+03}},
    "Methanol": {"mw": 32, "rho": 50, "nbp": 149, "state": "Liquid", "ait": 867, "cp": {"n": 2, "A": 3.93E+04, "B": 8.79E+04, "C": 1.92E+03, "D": 5.37E+04, "E": 8.97E+02}},
    "CO": {"mw": 28, "rho": 50, "nbp": -312, "state": "Gas", "ait": 1128, "cp": {"n": 2, "A": 2.91E+04, "B": 8.77E+03, "C": 3.09E+03, "D": 8.46E+03, "E": 1.54E+03}},
    "DEE": {"mw": 74, "rho": 45, "nbp": 95, "state": "Liquid", "ait": 320, "cp": {"n": 2, "A": 8.62E+04, "B": 2.55E+05, "C": 1.54E+03, "D": 1.44E+05, "E": -6.89E+02}},
    "PO": {"mw": 58, "rho": 52, "nbp": 93, "state": "Liquid", "ait": 840, "cp": {"n": 2, "A": 4.95E+04, "B": 1.74E+05, "C": 1.56E+03, "D": 1.15E+05, "E": 7.02E+02}},
    "EEA": {"mw": 132, "rho": 61, "nbp": 313, "state": "Liquid", "ait": 715, "cp": {"n": 2, "A": 1.06E+05, "B": 2.40E+05, "C": 6.59E+02, "D": 1.50E+05, "E": 1.97E+03}},
    "EE": {"mw": 90, "rho": 58, "nbp": 275, "state": "Liquid", "ait": 455, "cp": {"n": 2, "A": 3.25E+04, "B": 3.00E+05, "C": 1.17E+03, "D": 2.08E+05, "E": 4.73E+02}},
    "EG": {"mw": 62, "rho": 69, "nbp": 387, "state": "Liquid", "ait": 745, "cp": {"n": 2, "A": 6.30E+04, "B": 1.46E+05, "C": 1.67E+03, "D": 9.73E+04, "E": 7.74E+02}},
    "EO": {"mw": 44, "rho": 55, "nbp": 51, "state": "Gas", "ait": 804, "cp": {"n": 2, "A": 3.35E+04, "B": 1.21E+05, "C": 1.61E+03, "D": 8.24E+04, "E": 7.37E+02}},
    "Water": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "Acid/caustic-LP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "Acid/caustic-MP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "Acid/caustic-HP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "HCl": {"mw": 36, "rho": 74, "nbp": -121, "state": "Gas", "ait": 0, "cp": None},
    "Nitric acid": {"mw": 63, "rho": 95, "nbp": 250, "state": "Liquid", "ait": 0, "cp": None},
    "NO2": {"mw": 46, "rho": 58, "nbp": 275, "state": "Liquid", "ait": 0, "cp": None},
    "Phosgene": {"mw": 99, "rho": 86, "nbp": 181, "state": "Liquid", "ait": 0, "cp": None},
    "TDI": {"mw": 174, "rho": 76, "nbp": 484, "state": "Liquid", "ait": 1148, "cp": None},
    "Chlorine": {"mw": 70.91, "rho": 0.20, "nbp": -29.27, "state": "Gas", "ait": 0, "cp": None},
}

# ---------------------------------------------------------------------
# Output Model
# ---------------------------------------------------------------------
@dataclass
class Step41Result:
    representative_fluid: str
    fluid_type: str
    stored_phase: str
    ambient_phase: str      # Calculated
    final_release_phase: str
    properties: Dict[str, Any]
    trace: Dict[str, float]

# ---------------------------------------------------------------------
# Thermodynamics
# ---------------------------------------------------------------------
def calculate_cp(cp_data: Dict, T_k: float) -> float:
    """Calculates Cp in J/(mol·K)."""
    n = cp_data["n"]
    A, B, C, D = cp_data["A"], cp_data["B"], cp_data["C"], cp_data["D"]
    E = cp_data.get("E", 0)

    if n == 1:
        return A + B*T_k + C*(T_k**2) + D*(T_k**3)
    elif n == 2:
        term1 = (C/T_k) / math.sinh(C/T_k) if T_k > 0 else 0
        term2 = (E/T_k) / math.cosh(E/T_k) if (T_k > 0 and E > 0) else 0
        cp_kmol = A + B*(term1**2) + D*(term2**2)
        return cp_kmol / 1000.0
    elif n == 3:
        cp_kmol = A + B*T_k + C*(T_k**2) + D*(T_k**3) + E*(T_k**4)
        return cp_kmol / 1000.0
    return 0.0

# ---------------------------------------------------------------------
# Main Function: Step 4.1
# ---------------------------------------------------------------------
def step_4_1_determine_representative_fluid(
    representative_fluid: str, 
    stored_phase: str, 
    temperature_k: Optional[float] = None
) -> Step41Result:
    """
    Determines fluid properties and Release Phase (Step 4.1).
    ambient_phase is AUTOMATICALLY calculated based on NBP.
    """
    
    # 1. Lookup Properties
    if representative_fluid not in FLUID_PROPERTIES:
        raise ValueError(f"Fluid '{representative_fluid}' not found in Table 4.2 database.")
    
    props = FLUID_PROPERTIES[representative_fluid]
    fluid_type = REPRESENTATIVE_FLUIDS.get(representative_fluid, "Type 0")
    
    # 2. Determine Ambient Phase (Internal Logic)
    # If NBP > 80°F, it's liquid at ambient conditions. Otherwise, it's gas.
    # This aligns with the cutoff logic in Table 4.3.
    nbp = props["nbp"]
    computed_ambient_phase = "Liquid" if nbp > AMBIENT_TEMP_CUTOFF_F else "Gas"

    # 3. Determine Final Release Phase (Table 4.3 logic)
    if stored_phase == "Gas":
        final_phase = "Gas"
    elif computed_ambient_phase == "Liquid":
        # Stored Liquid, Ambient Liquid -> Final Liquid
        final_phase = "Liquid" 
    else:
        # Stored Liquid, Ambient Gas (e.g. C3-C4) -> Model as Gas
        # (Table 4.3 says: Model as Gas UNLESS NBP > 80F... which we already checked)
        final_phase = "Gas"

    # 4. Calc Cp/Gamma if needed
    cp, gamma = None, None
    if props["cp"] and temperature_k:
        cp = calculate_cp(props["cp"], temperature_k)
        if cp > R_UNIVERSAL:
            gamma = cp / (cp - R_UNIVERSAL)
        else:
            gamma = 1.4 # Fallback
    elif final_phase == "Gas":
        gamma = 1.4

    return Step41Result(
        representative_fluid=representative_fluid,
        fluid_type=fluid_type,
        stored_phase=stored_phase,
        ambient_phase=computed_ambient_phase, # Retornamos lo que calculamos
        final_release_phase=final_phase,
        properties=props,
        trace={"gamma_calc": gamma, "cp_calc": cp}
    )