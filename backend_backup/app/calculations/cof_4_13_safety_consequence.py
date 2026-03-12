# app/calculations/cof_4_13_safety_consequence.py
"""
API 581 COF Level 1
Section 4.13: Determine Safety Consequence

Implements:
- Eq. (3.92): Final Safety Consequence (C_f_inj)
- Eq. (3.93): Average Personnel Calculation (Pers_avg)
- Eq. (3.94): Population Density (popdens)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Iterable

# -------------------------
# Data Models
# -------------------------

@dataclass(frozen=True)
class StaffingCase:
    """
    Represents a specific staffing scenario for Equation (3.93).
    
    Attributes:
        pers_count (float): Number of personnel (Pers#i).
        present_pct (float): Percentage of time present (Present%i). Must be 0-100.
    """
    pers_count: float
    present_pct: float


@dataclass(frozen=True)
class SafetyConsequenceInputs:
    """
    Required inputs for Section 4.13 calculations.
    """
    ca_f_inj_area: float       # Final personnel injury consequence area from Sec 4.11 (ft^2 or m^2)
    area_safety: float         # Area of the unit/boundaries (ft^2 or m^2)
    staffing: List[StaffingCase] # List of staffing scenarios for the unit


@dataclass(frozen=True)
class SafetyConsequenceResult:
    """
    Outputs for Section 4.13.
    """
    pers_avg: float    # Average number of personnel
    popdens: float     # Population density (person/area)
    c_f_inj: float     # Final safety consequence (person)


# -------------------------
# Core Equations
# -------------------------

def compute_pers_avg(staffing: Iterable[StaffingCase]) -> float:
    """
    Eq. (3.93): Calculate average personnel.
    Pers#avg = Sum(Pers#i * Present%i) / 100
    """
    total = 0.0
    has_data = False

    for s in staffing:
        has_data = True
        if s.pers_count < 0:
            raise ValueError(f"Personnel count cannot be negative: {s.pers_count}")
        if not (0.0 <= s.present_pct <= 100.0):
            raise ValueError(f"Percentage must be 0-100: {s.present_pct}")
            
        total += (s.pers_count * s.present_pct)

    if not has_data:
        return 0.0

    return float(total / 100.0)


def compute_popdens(pers_avg: float, area_safety: float) -> float:
    """
    Eq. (3.94): Calculate population density.
    popdens = Pers#avg / Area_safety
    """
    if pers_avg < 0:
        raise ValueError("Average personnel cannot be negative.")
    if area_safety <= 0:
        raise ValueError("Safety area must be greater than zero.")
        
    return float(pers_avg / area_safety)


def compute_safety_consequence(ca_f_inj_area: float, popdens: float) -> float:
    """
    Eq. (3.92): Calculate final safety consequence.
    C_f_inj = CA_f_inj * popdens
    """
    if ca_f_inj_area < 0:
        raise ValueError("Consequence area cannot be negative.")
    if popdens < 0:
        raise ValueError("Population density cannot be negative.")
        
    return float(ca_f_inj_area * popdens)


# -------------------------
# Main Calculation Flow
# -------------------------

def compute_cof_4_13_safety_consequence(inp: SafetyConsequenceInputs) -> SafetyConsequenceResult:
    """
    Orchestrates the calculation steps 13.1 through 13.5.
    """
    # Step 13.2 / Eq (3.93)
    pers_avg = compute_pers_avg(inp.staffing)
    
    # Step 13.4 / Eq (3.94)
    popdens = compute_popdens(pers_avg, inp.area_safety)
    
    # Step 13.5 / Eq (3.92)
    c_f_inj = compute_safety_consequence(inp.ca_f_inj_area, popdens)

    return SafetyConsequenceResult(
        pers_avg=pers_avg,
        popdens=popdens,
        c_f_inj=c_f_inj
    )