# app/calculations/cof_4_10_nonflammable_nontoxic.py
"""
API 581 COF Level 1
Section 4.10: Determine Nonflammable, Nontoxic Consequence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional, Dict

# # Constants
# C5_LB_S = 55.6  # Transition constant (lb/s)

# # Table 4.9 Constants for Acid/Caustic (Personnel Injury)
# TABLE_4_9_ACID_CAUSTIC = {
#     "Acid/caustic-LP": (2699.5, 0.2024),
#     "Acid/caustic-MP": (3366.2, 0.2878),
#     "Acid/caustic-HP": (6690.0, 0.2469),
# }

# class ReleaseType(str, Enum):
#     CONTINUOUS = "continuous"
#     INSTANTANEOUS = "instantaneous"

# class NonFlamCategory(str, Enum):
#     STEAM = "Steam"
#     ACID_CAUSTIC = "acid_caustic"

# @dataclass(frozen=True)
# class SteamConstants:
#     """Constants derived from steam pressure (Text 4.10.2)."""
#     C9: float   # For Eq (3.68)
#     C10: float  # For Eq (3.69)

# @dataclass(frozen=True)
# class NonFlamHoleInputs:
#     """Per-hole inputs coming from Section 4.7."""
#     rate_n_lbm_s: float     # Release rate (lb/s)
#     mass_n_lbm: float       # Release mass (lb)
#     release_type: ReleaseType # Nuevo campo requerido para la lógica condicional

# @dataclass(frozen=True)
# class NonFlamHoleResult:
#     CA_inj_cont: float
#     CA_inj_inst: float
#     fact_ic: float
#     CA_inj_leak: float
#     CA_cmd: float = 0.0
#     used_constants: Dict[str, float] = None

# # -----------------------------------------------------------------------------
# # Core Equations
# # -----------------------------------------------------------------------------

# def steam_ca_cont(rate_n_lbm_s: float) -> float:
#     """Eq (3.68): Continuous Steam CA (Fixed const 0.6 per requirements)."""
#     if rate_n_lbm_s <= 0:
#         return 0.0
#     return float(0.6 * rate_n_lbm_s)

# def steam_ca_inst(mass_n_lbm: float) -> float:
#     """Eq (3.69): Instantaneous Steam CA (Fixed const 63.32 per requirements)."""
#     if mass_n_lbm <= 0:
#         return 0.0
#     return float(63.32 * (mass_n_lbm ** 0.6384))

# def blending_factor_ic(rate_n_lbm_s: float) -> float:
#     """Eq (3.70): Steam blending factor."""
#     if rate_n_lbm_s <= 0:
#         return 0.0
#     return float(min(rate_n_lbm_s / C5_LB_S, 1.0))

# def acid_caustic_ca_cont(rate_n_lbm_s: float, a: float, b: float) -> float:
#     """Eq (3.71): Acid/Caustic Continuous CA."""
#     if rate_n_lbm_s <= 0:
#         return 0.0
#     return float(0.2 * a * (rate_n_lbm_s ** b))

# def blend_ca(CA_inst: float, CA_cont: float, fact_ic: float) -> float:
#     """Eq (3.73): Blending logic."""
#     f = max(0.0, min(1.0, float(fact_ic)))
#     return float(CA_inst * f + CA_cont * (1.0 - f))

# # -----------------------------------------------------------------------------
# # Main Calculation Functions
# # -----------------------------------------------------------------------------

# def compute_nonflammable_nontoxic_for_hole(
#     *,
#     category: NonFlamCategory,
#     hole: NonFlamHoleInputs,
#     fluid_name: str = None,
# ) -> NonFlamHoleResult:
#     """
#     Computes Eq (3.68) through Eq (3.73) for a single hole.
#     Applies logic to zero out the non-applicable release type.
#     """
    
#     # --- STEAM ---
#     if category == NonFlamCategory.STEAM:
                
#         # Lógica Condicional solicitada:
#         if hole.release_type == ReleaseType.CONTINUOUS:
#             CA_cont = steam_ca_cont(hole.rate_n_lbm_s)
#             CA_inst = 0.0  # Forzamos 0.0
#             fact_ic = 0.0  # Forzamos 0.0 para que el blend tome 100% cont
        
#         elif hole.release_type == ReleaseType.INSTANTANEOUS:
#             CA_cont = 0.0  # Forzamos 0.0
#             CA_inst = steam_ca_inst(hole.mass_n_lbm)
#             fact_ic = 1.0  # Forzamos 1.0 para que el blend tome 100% inst
        
#         else:
#             # Fallback en caso de lógica mixta (si se llegara a usar)
#             # Aunque tu requerimiento elimina esto, la API original usa blending.
#             # Aquí respetamos tu lógica binaria.
#             CA_cont = steam_ca_cont(hole.rate_n_lbm_s)
#             CA_inst = steam_ca_inst(hole.mass_n_lbm)
#             fact_ic = blending_factor_ic(hole.rate_n_lbm_s)

#         # Calculamos el leak final con los valores forzados
#         CA_leak = blend_ca(CA_inst, CA_cont, fact_ic)
        
#         return NonFlamHoleResult(
#             CA_cont, CA_inst, fact_ic, CA_leak, 
#             used_constants={"C9": 0.6, "C10": 63.32}
#         )

#     # --- ACID / CAUSTIC ---
#     elif category == NonFlamCategory.ACID_CAUSTIC:
#         if not fluid_name:
#              raise ValueError("fluid_name is required for ACID_CAUSTIC.")
        
#         if fluid_name not in TABLE_4_9_ACID_CAUSTIC:
#              raise ValueError(f"Fluid '{fluid_name}' not found in Table 4.9.")
        
#         a, b = TABLE_4_9_ACID_CAUSTIC[fluid_name]
        
#         # Lógica Condicional solicitada:
#         if hole.release_type == ReleaseType.INSTANTANEOUS:
#             # Si es instantáneo, Acid/Caustic da 0 en todo (no tiene componente inst)
#             CA_cont = 0.0
#             CA_inst = 0.0
#             fact_ic = 0.0
#         else:
#             # Caso Continuo (Normal para Acid/Caustic)
#             CA_cont = acid_caustic_ca_cont(hole.rate_n_lbm_s, a, b)
#             CA_inst = 0.0
#             fact_ic = 0.0
        
#         CA_leak = blend_ca(CA_inst, CA_cont, fact_ic)
        
#         return NonFlamHoleResult(
#             CA_cont, CA_inst, fact_ic, CA_leak,
#             used_constants={"a": a, "b": b}
#         )

#     else:
#         raise ValueError(f"Unknown category: {category}")


# def probability_weighted_nonflammable_area(
#     *,
#     ca_leak_by_hole: Mapping[str, float], 
#     gff_by_hole: Mapping[str, float],     
#     gff_total: float,
# ) -> float:
#     """Eq (3.75): Final Probability Weighted Area."""
#     if gff_total <= 0:
#         return 0.0
        
#     weighted_sum = 0.0
#     for hole_size, ca in ca_leak_by_hole.items():
#         freq = gff_by_hole.get(hole_size, 0.0)
#         weighted_sum += freq * ca
        
#     return float(weighted_sum / gff_total)


# --- CONSTANTS ---
C5_LB_S = 55.6  # Transition constant (lb/s)

# Table 4.9 Constants for Acid/Caustic (Personnel Injury)
# Format: "Fluid Name": (Constant_C, Constant_D) -> mapped to a, b in logic
TABLE_4_9_ACID_CAUSTIC = {
    "Acid/caustic-LP": (2699.5, 0.2024),
    "Acid/caustic-MP": (3366.2, 0.2878),
    "Acid/caustic-HP": (6690.0, 0.2469),
}

class ReleaseType(str, Enum):
    CONTINUOUS = "continuous"
    INSTANTANEOUS = "instantaneous"

class NonFlamCategory(str, Enum):
    STEAM = "Steam"
    ACID_CAUSTIC = "acid_caustic"

@dataclass(frozen=True)
class NonFlamHoleInputs:
    """Per-hole inputs coming from Section 4.7."""
    rate_n_lbm_s: float     # Release rate (lb/s)
    mass_n_lbm: float       # Release mass (lb)
    release_type: ReleaseType # Requerido para tu lógica condicional

@dataclass(frozen=True)
class NonFlamHoleResult:
    CA_inj_cont: float
    CA_inj_inst: float
    fact_ic: float
    CA_inj_leak: float
    CA_cmd: float = 0.0
    used_constants: Dict[str, float] = field(default_factory=dict)

# -----------------------------------------------------------------------------
# Core Equations
# -----------------------------------------------------------------------------

def steam_ca_cont(rate_n_lbm_s: float) -> float:
    """Eq (3.68): Continuous Steam CA (Fixed const 0.6 per requirements)."""
    if rate_n_lbm_s <= 0:
        return 0.0
    return float(0.6 * rate_n_lbm_s)

def steam_ca_inst(mass_n_lbm: float) -> float:
    """Eq (3.69): Instantaneous Steam CA (Fixed const 63.32 per requirements)."""
    if mass_n_lbm <= 0:
        return 0.0
    return float(63.32 * (mass_n_lbm ** 0.6384))

def blending_factor_ic(rate_n_lbm_s: float) -> float:
    """Eq (3.70): Steam blending factor."""
    if rate_n_lbm_s <= 0:
        return 0.0
    return float(min(rate_n_lbm_s / C5_LB_S, 1.0))

def acid_caustic_ca_cont(rate_n_lbm_s: float, a: float, b: float) -> float:
    """Eq (3.71): Acid/Caustic Continuous CA."""
    if rate_n_lbm_s <= 0:
        return 0.0
    # Fórmula específica solicitada: 0.2 * a * rate^b
    return float(0.2 * a * (rate_n_lbm_s ** b))

def blend_ca(CA_inst: float, CA_cont: float, fact_ic: float) -> float:
    """Eq (3.73): Blending logic."""
    f = max(0.0, min(1.0, float(fact_ic)))
    return float(CA_inst * f + CA_cont * (1.0 - f))

# -----------------------------------------------------------------------------
# Main Calculation Functions
# -----------------------------------------------------------------------------

def compute_nonflammable_nontoxic_for_hole(
    *,
    category: NonFlamCategory,
    hole: NonFlamHoleInputs,
    fluid_name: str = None,
) -> NonFlamHoleResult:
    """
    Computes Eq (3.68) through Eq (3.73) for a single hole.
    Applies logic to zero out the non-applicable release type.
    """
    
    # --- STEAM ---
    if category == NonFlamCategory.STEAM:
        
        # Lógica Condicional solicitada:
        if hole.release_type == ReleaseType.CONTINUOUS:
            CA_cont = steam_ca_cont(hole.rate_n_lbm_s)
            CA_inst = 0.0  # Forzamos 0.0
            fact_ic = 0.0  # Forzamos 0.0 para que el blend tome 100% cont
        
        elif hole.release_type == ReleaseType.INSTANTANEOUS:
            CA_cont = 0.0  # Forzamos 0.0
            CA_inst = steam_ca_inst(hole.mass_n_lbm)
            fact_ic = 1.0  # Forzamos 1.0 para que el blend tome 100% inst
        
        else:
            # Fallback teórico (aunque no debería ocurrir con Enums)
            CA_cont = steam_ca_cont(hole.rate_n_lbm_s)
            CA_inst = steam_ca_inst(hole.mass_n_lbm)
            fact_ic = blending_factor_ic(hole.rate_n_lbm_s)

        # Calculamos el leak final con los valores forzados
        CA_leak = blend_ca(CA_inst, CA_cont, fact_ic)
        
        return NonFlamHoleResult(
            CA_cont, CA_inst, fact_ic, CA_leak, 
            used_constants={"C9": 0.6, "C10": 63.32}
        )

    # --- ACID / CAUSTIC ---
    elif category == NonFlamCategory.ACID_CAUSTIC:
        if not fluid_name:
             raise ValueError("fluid_name is required for ACID_CAUSTIC.")
        
        # Normalización simple para búsqueda
        # Intentamos buscar directo, si no, normalizamos
        tgt = fluid_name
        if tgt not in TABLE_4_9_ACID_CAUSTIC:
             # Intento de fallback (opcional)
             raise ValueError(f"Fluid '{fluid_name}' not found in Table 4.9. Options: {list(TABLE_4_9_ACID_CAUSTIC.keys())}")
        
        a, b = TABLE_4_9_ACID_CAUSTIC[tgt]
        
        # Lógica Condicional solicitada:
        if hole.release_type == ReleaseType.INSTANTANEOUS:
            # Si es instantáneo, Acid/Caustic da 0 en todo (no tiene componente inst definido aquí)
            CA_cont = 0.0
            CA_inst = 0.0
            fact_ic = 0.0
        else:
            # Caso Continuo (Normal para Acid/Caustic)
            CA_cont = acid_caustic_ca_cont(hole.rate_n_lbm_s, a, b)
            CA_inst = 0.0
            fact_ic = 0.0
        
        CA_leak = blend_ca(CA_inst, CA_cont, fact_ic)
        
        return NonFlamHoleResult(
            CA_cont, CA_inst, fact_ic, CA_leak,
            used_constants={"a": a, "b": b}
        )

    else:
        raise ValueError(f"Unknown category: {category}")


def probability_weighted_nonflammable_area(
    *,
    ca_leak_by_hole: Mapping[str, float], 
    gff_by_hole: Mapping[str, float],     
    gff_total: float,
) -> float:
    """Eq (3.75): Final Probability Weighted Area."""
    if gff_total <= 0:
        return 0.0
        
    weighted_sum = 0.0
    for hole_size, ca in ca_leak_by_hole.items():
        freq = gff_by_hole.get(hole_size, 0.0)
        weighted_sum += freq * ca
        
    return float(weighted_sum / gff_total)