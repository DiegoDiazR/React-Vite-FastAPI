from __future__ import annotations

# app/calculations/cof_4_4_fluid_inventory.py
"""
API 581 COF Level 1
Section 4.4: Estimate the Fluid Inventory Available for Release

Implements:
- Eq. (3.9):  mass_inv = sum(mass_comp,i)
- Eq. (3.10): mass_add,n = 180 * min(Wn, Wmax8)
- Eq. (3.11): mass_avail,n = min( (mass_comp + mass_add,n), mass_inv )

Inputs expected:
- mass_comp_lbm: mass in the leaking component
- other_component_masses_lbm: masses of other components in the inventory group
- Wn_lbm_s: release rate for each hole size (from 4.3)
- Wmax8_lbm_s: max add flow rate based on 8-in hole (computed using 4.3, dn=8.0 in)

Outputs:
- per hole size: mass_add_n, mass_avail_n
"""
"""
API 581 COF Level 1
Section 4.4: Estimate the Fluid Inventory Available for Release

Implements:
- Eq. (3.9):  mass_inv = sum(mass_comp,i)
- Eq. (3.10): mass_add,n = 180 * min(Wn, Wmax8)
- Eq. (3.11): mass_avail,n = min( (mass_comp + mass_add,n), mass_inv )
"""

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Any

SECONDS_IN_3_MIN = 180.0

@dataclass(frozen=True)
class InventoryInputs:
    mass_comp_lbm: float
    other_component_masses_lbm: Optional[Mapping[str, float]] = None

@dataclass(frozen=True)
class InventoryPerHoleResult:
    wn_lbm_s: float
    wmax8_lbm_s: float
    mass_inv_lbm: float
    mass_add_lbm: float
    mass_avail_lbm: float

@dataclass(frozen=True)
class InventoryResult:
    mass_inv_lbm: float
    wmax8_lbm_s: float
    per_hole: Dict[Any, InventoryPerHoleResult] # Supports Enum or Str keys

def compute_mass_inventory_group(inputs: InventoryInputs) -> float:
    """Eq. (3.9): mass_inv = sum(mass_comp,i)"""
    if inputs.mass_comp_lbm < 0:
        raise ValueError("mass_comp_lbm must be >= 0")

    total = float(inputs.mass_comp_lbm)
    if inputs.other_component_masses_lbm:
        for k, v in inputs.other_component_masses_lbm.items():
            if v < 0:
                raise ValueError(f"Inventory mass for '{k}' must be >= 0")
            total += float(v)
    return total

def compute_mass_add(wn_lbm_s: float, wmax8_lbm_s: float) -> float:
    """Eq. (3.10): mass_add,n = 180 * min(Wn, Wmax8)"""
    if wn_lbm_s < 0 or wmax8_lbm_s < 0:
        raise ValueError("Release rates must be >= 0")
    return SECONDS_IN_3_MIN * min(float(wn_lbm_s), float(wmax8_lbm_s))

def compute_mass_avail(mass_comp_lbm: float, mass_add_lbm: float, mass_inv_lbm: float) -> float:
    """Eq. (3.11): mass_avail,n = min( (mass_comp + mass_add,n), mass_inv )"""
    if mass_comp_lbm < 0 or mass_add_lbm < 0 or mass_inv_lbm < 0:
        raise ValueError("Masses must be >= 0")
    return min(float(mass_comp_lbm) + float(mass_add_lbm), float(mass_inv_lbm))

def compute_cof_4_4_fluid_inventory(
    *,
    inventory: InventoryInputs,
    wn_by_hole_lbm_s: Mapping[Any, float], # Accepts Enum or Str
    wmax8_lbm_s: float,
) -> InventoryResult:
    """
    Full 4.4 calculation.
    """
    mass_inv = compute_mass_inventory_group(inventory)

    per_hole: Dict[Any, InventoryPerHoleResult] = {}
    
    for hole_id, wn in wn_by_hole_lbm_s.items():
        mass_add = compute_mass_add(wn_lbm_s=float(wn), wmax8_lbm_s=float(wmax8_lbm_s))
        
        mass_avail = compute_mass_avail(
            mass_comp_lbm=float(inventory.mass_comp_lbm),
            mass_add_lbm=float(mass_add),
            mass_inv_lbm=float(mass_inv),
        )
        
        per_hole[hole_id] = InventoryPerHoleResult(
            wn_lbm_s=float(wn),
            wmax8_lbm_s=float(wmax8_lbm_s),
            mass_inv_lbm=float(mass_inv),
            mass_add_lbm=float(mass_add),
            mass_avail_lbm=float(mass_avail),
        )

    return InventoryResult(
        mass_inv_lbm=float(mass_inv),
        wmax8_lbm_s=float(wmax8_lbm_s),
        per_hole=per_hole,
    )