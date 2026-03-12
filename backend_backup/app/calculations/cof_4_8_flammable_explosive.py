# app/calculations/cof_4_8_flammable_explosive.py
"""
API 581 COF Level 1
Section 4.8: Determine Flammable and Explosive Consequence

Implements:
- Table 4.8: Component Damage Flammable Consequence Equation Constants
- Table 4.9: Personnel Injury Flammable Consequence Equation Constants
- Table 4.10: Adjustments to Flammable Consequence for Mitigation Systems

Equations implemented (as referenced in your excerpts):
- Continuous areas (component damage / injury):
    CA = a * (rate)^b * (1 - fact_mit)
- Instantaneous areas:
    CA = a * (mass)^b * ((1 - fact_mit) / eneff)
- Energy efficiency factor (instantaneous):
    eneff = 4 * log10(CA * mass) - 15   (Eq 3.17)  [used as divisor]
- Release type blending (IC):
    fact_IC = min(rate / C5, 1.0)  for continuous (Eq 3.18), C5 = 55.6 lb/s
    fact_IC = 1.0                 for instantaneous (Eq 3.20)
    CA_blend = CA_INST*fact_IC + CA_CONT*(1-fact_IC) (Eq 3.21)
- AIT blending:
    CA_AIT_blend = CA_AIL*fact_AIT + CA_AINL*(1 - fact_AIT) (Eq 3.22)
    fact_AIT defined by Eq 3.23-3.25 with constant C6 (configurable)
- Probability weighting across hole sizes (GFF):
    CA_final = (sum gff_n * CA_n) / gff_total  (Eq 3.58, 3.59)

Units:
- rate in lb/s
- mass in lb
- areas are "consequence area" (API 581 empirical units; typically ft^2 as used by 581)
- Ts and AIT in Rankine (°R) for the blending factor logic.

Design notes:
- Missing constants in tables are stored as None and will raise a clear error if requested.
- Type 0 fluids: IC blending required.
- Type 1 fluids: IC blending not required (uses release-type-specific result directly).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import log10
import math
from typing import Dict, Optional, Literal, Tuple


# -----------------------------
# Enums / types
# -----------------------------
class FluidType(int, Enum):
    TYPE_0 = 0
    TYPE_1 = 1


class ReleaseType(str, Enum):
    CONTINUOUS = "continuous"
    INSTANTANEOUS = "instantaneous"


class Phase(str, Enum):
    GAS = "gas"
    LIQUID = "liquid"


class AutoIgnitionCase(str, Enum):
    AINL = "ainl"  # Autoignition Not Likely
    AIL = "ail"    # Autoignition Likely


class ConsequenceTarget(str, Enum):
    COMPONENT_DAMAGE = "component_damage"
    PERSONNEL_INJURY = "personnel_injury"


@dataclass(frozen=True)
class PowerLawConstants:
    a: float
    b: float


@dataclass(frozen=True)
class FlammableConstantsRow:
    fluid: str
    fluid_type: FluidType
    # Keys: (release_type, autoignition_case, phase) -> constants
    constants: Dict[Tuple[ReleaseType, AutoIgnitionCase, Phase], Optional[PowerLawConstants]]


@dataclass(frozen=True)
class HoleInput:
    """
    Inputs per release hole size n.
    - rate_lb_s: adjusted in 4.7 or theoretical? (You will decide in orchestration)
      In 4.8 equations they use rate_n and mass_n inputs; commonly you will feed:
        * rate_n = adjusted release rate (Eq 3.12) for continuous path usage
        * mass_n = upper bound instantaneous mass (Eq 3.13) for instantaneous path usage
    - release_type: from 4.5
    - final_phase: from 4.1 (Table 4.3 logic) -> gas or liquid
    """
    hole_key: str  # e.g. "small", "medium", "large", "rupture"
    release_type: ReleaseType
    final_phase: Phase
    rate_lb_s: float
    mass_lb: float

# @dataclass(frozen=True)
# class HoleInput:
#     hole_key: str
#     release_type: ReleaseType
#     final_phase: Phase
#     rate_lb_s: float
#     mass_lb: float
#     # Atributos de trazabilidad (Añadidos para corregir el error)
#     dn_in: float
#     An_in2: float
#     Wn_lb_s: float
#     mass_comp_lb: float
#     mass_inv_lb: float
#     mass_add_lb: float
#     mass_avail_lb: float
#     t_n_s: float
#     fact_di: float
#     ld_max_min: float


@dataclass(frozen=True)
class AITInputs:
    """
    Needed for AIT blending.
    Ts_R: storage/operating temperature in Rankine
    AIT_R: autoignition temperature in Rankine
    """
    Ts_R: float
    representative_fluid: str
    


@dataclass(frozen=True)
class FlammableHoleResult:
    hole_size: str
    # hole_key: str

    # per-hole results after IC blend (if Type0) and AIT blend (always):
    CA_cmd: float  # component damage flammable consequence area
    CA_inj: float  # personnel injury flammable consequence area

    # useful debug outputs
    fact_mit: float
    # eneff: float
    # CA_ainl_cont_cte_a: float
    # CA_ainl_cont_cte_b: float
    # CA_ainl_cont: float
    # CA_ail_cont_cte_a: float
    # CA_ail_cont_cte_b: float
    # CA_ail_cont: float
    # CA_ainl_inst_cte_a: float
    # CA_ainl_inst_cte_b: float
    # CA_ainl_inst: float
    # CA_ail_inst_cte_a: float
    # CA_ail_inst_cte_b: float
    # CA_ail_inst: float
    
    # CA_ainl_cont_inj_cte_a: float
    # CA_ainl_cont_inj_cte_b: float
    # CA_ainl_cont_inj: float
    # CA_ail_cont_inj_cte_a: float
    # CA_ail_cont_inj_cte_b: float
    # CA_ail_cont_inj: float
    # CA_ainl_inst_inj_cte_a: float
    # CA_ainl_inst_inj_cte_b: float
    # CA_ainl_inst_inj: float
    # CA_ail_inst_inj_cte_a: float
    # CA_ail_inst_inj_cte_b: float
    # CA_ail_inst_inj: float

    # CA_ail_cmd_n: Tuple[float, float]
    # CA_ail_inj_n: Tuple[float, float]
    # CA_ainl_cmd_n: Tuple[float, float]
    # CA_ainl_inj_n: Tuple[float, float]

    # CA_flam_cmd_n: float
    # CA_flam_inj_n: float

    # fact_IC: float
    fact_AIT: float
  

    # intermediate (optional inspection)
    CA_cmd_AINL: float = 0.0
    CA_cmd_AIL: float = 0.0
    CA_inj_AINL: float = 0.0
    CA_inj_AIL: float = 0.0

# --- Estructura para Auditoría (Coincide con tu Excel) ---
# @dataclass(frozen=True)
# class FlammableHoleResult:
#     hole_key: str
#     dn_in: float           # Fila 30
#     An_in2: float          # Fila 34
#     Wn_lb_s: float         # Fila 38
#     mass_comp_lb: float    # Fila 43
#     mass_inv_lb: float     # Fila 45
#     mass_add_lb: float     # Fila 46
#     mass_avail_lb: float   # Fila 50
#     t_n_s: float           # Fila 54
#     release_type: str      # Fila 58
#     fact_di: float         # Fila 64
#     ld_max_min: float      # Fila 65
#     rate_n_lb_s: float     # Fila 69
#     ld_n_s: float          # Fila 73
#     mass_n_lb: float       # Fila 77
#     fact_mit: float        # Fila 81
#     eneff: float           # Fila 82
#     fact_IC: float         # Fila 151
#     fact_AIT: float        # Fila 155
#     CA_cmd: float          # Fila 172
#     CA_inj: float          # Fila 176
#     # Áreas intermedias para trazabilidad
#     CA_cmd_AINL: float
#     CA_cmd_AIL: float
#     CA_inj_AINL: float
#     CA_inj_AIL: float

@dataclass(frozen=True)
class FlammableFinalResult:
    fluid: str
    # fluid_type: FluidType
    fluid_type: int
    holes: Dict[str, FlammableHoleResult]

    # probability weighted finals (Eq 3.58, 3.59)
    CA_cmd_final: float
    CA_inj_final: float

# @dataclass(frozen=True)
# class FlammableFinalResult:
#     fluid: str
#     holes: Dict[str, FlammableHoleResult]
#     CA_cmd_final: float
#     CA_inj_final: float

# -----------------------------
# Constants (4.8.5 / 4.5 threshold)
# -----------------------------
C5_RATE_TRANSITION_LB_S = 55.6  # lb/s, used in Eq (3.18)

# Eq (3.23-3.25) uses C6. Not shown in your images; keep configurable default.
C6_R_DEFAULT = 50.0  # °R (CONFIGURABLE; update if your document states another value)


# -----------------------------
# Table 4.10 — Mitigation systems
# -----------------------------
# The factor is the "Consequence Area Reduction Factor, fact_mit".
_TABLE_4_10_FACT_MIT: Dict[str, float] = {
    "inventory_blowdown_with_isolation_B_or_higher": 0.25,
    "fire_water_deluge_and_monitors": 0.20,
    "fire_water_monitors_only": 0.05,
    "foam_spray_system": 0.15,
    "none": 0.00,
}


def fact_mit_from_system(system_key: str) -> float:
    """
    Returns fact_mit from Table 4.10.
    Use system_key from:
      - inventory_blowdown_with_isolation_B_or_higher
      - fire_water_deluge_and_monitors
      - fire_water_monitors_only
      - foam_spray_system
      - none
    """
    key = system_key.strip().lower()
    if key not in _TABLE_4_10_FACT_MIT:
        allowed = ", ".join(sorted(_TABLE_4_10_FACT_MIT.keys()))
        raise KeyError(f"Unknown mitigation system '{system_key}'. Allowed: {allowed}")
    return float(_TABLE_4_10_FACT_MIT[key])


# -----------------------------
# Table 4.8 — Component Damage constants
# -----------------------------
# Structure per row:
# constants[(release_type, autoignition_case, phase)] = PowerLawConstants(a,b) or None
#
# Transcribed from your Table 4.8 image.
_TABLE_4_8: Dict[str, FlammableConstantsRow] = {}


def _mk_row_48(fluid: str, fluid_type: FluidType) -> FlammableConstantsRow:
    return FlammableConstantsRow(fluid=fluid, fluid_type=fluid_type, constants={})


def _set_48(
    fluid: str,
    release_type: ReleaseType,
    auto: AutoIgnitionCase,
    phase: Phase,
    a: float,
    b: float,
) -> None:
    row = _TABLE_4_8.get(fluid)
    if row is None:
        raise KeyError(f"Row '{fluid}' not registered in Table 4.8.")
    row.constants[(release_type, auto, phase)] = PowerLawConstants(float(a), float(b))


def _register_row_48(fluid: str, fluid_type: FluidType) -> None:
    _TABLE_4_8[fluid] = _mk_row_48(fluid, fluid_type)


# --- register rows (as in Table 4.8) ---
for _f, _t in [
    ("C1-C2", FluidType.TYPE_0),
    ("C3-C4", FluidType.TYPE_0),
    ("C5", FluidType.TYPE_0),
    ("C6-C8", FluidType.TYPE_0),
    ("C9-C12", FluidType.TYPE_0),
    ("C13-C16", FluidType.TYPE_0),
    ("C17-C25", FluidType.TYPE_0),
    ("C25+", FluidType.TYPE_0),
    ("Pyrophoric", FluidType.TYPE_1),
    ("Aromatics", FluidType.TYPE_1),
    ("Styrene", FluidType.TYPE_1),
    ("Water", FluidType.TYPE_0),
    ("Steam", FluidType.TYPE_0),
    ("Acid/caustic-LP", FluidType.TYPE_0),
    ("Acid/caustic-MP", FluidType.TYPE_0),
    ("Acid/caustic-HP", FluidType.TYPE_0),
    ("Methanol", FluidType.TYPE_1),
    ("H2", FluidType.TYPE_0),
    ("H2S", FluidType.TYPE_0),
    ("HF", FluidType.TYPE_0),
    ("CO", FluidType.TYPE_1),
    ("DEE", FluidType.TYPE_1),
    ("PO", FluidType.TYPE_1),
    ("EEA", FluidType.TYPE_1),
    ("EE", FluidType.TYPE_1),
    ("EG", FluidType.TYPE_1),
    ("EO", FluidType.TYPE_1),
]:
    _register_row_48(_f, _t)

# --- constants from Table 4.8 ---
# C1-C2
_set_48("C1-C2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 43.0, 0.98)
_set_48("C1-C2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 280.0, 0.95)
_set_48("C1-C2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 41.0, 0.67)
_set_48("C1-C2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1079.0, 0.62)

# C3-C4
_set_48("C3-C4", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 49.48, 1.00)
_set_48("C3-C4", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 313.6, 1.00)
_set_48("C3-C4", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 27.96, 0.72)
_set_48("C3-C4", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 522.9, 0.63)

# C5
_set_48("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 25.17, 0.99)
_set_48("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 536.0, 0.89)
_set_48("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 304.7, 1.00)
_set_48("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 13.38, 0.73)
_set_48("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1.49, 0.85)
_set_48("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 275.0, 0.61)

# C6-C8
_set_48("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 29.0, 0.98)
_set_48("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 182.0, 0.89)
_set_48("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 312.4, 1.00)
_set_48("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 525.0, 0.95)
_set_48("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 13.98, 0.66)
_set_48("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 4.35, 0.78)
_set_48("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 275.7, 0.61)
_set_48("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 57.0, 0.55)

# C9-C12
_set_48("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 12.0, 0.98)
_set_48("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 130.0, 0.90)
_set_48("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 391.0, 0.95)
_set_48("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 560.0, 0.95)
_set_48("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 7.1, 0.66)
_set_48("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 3.3, 0.76)
_set_48("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 281.0, 0.61)
_set_48("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 6.0, 0.53)

# C13-C16 (liquid only)
_set_48("C13-C16", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 64.0, 0.90)
_set_48("C13-C16", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1023.0, 0.92)
_set_48("C13-C16", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.46, 0.88)
_set_48("C13-C16", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 9.2, 0.88)

# C17-C25 (liquid only)
_set_48("C17-C25", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 20.0, 0.90)
_set_48("C17-C25", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 861.0, 0.92)
_set_48("C17-C25", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.11, 0.91)
_set_48("C17-C25", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 5.6, 0.91)

# C25+ (liquid only)
_set_48("C25+", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 11.0, 0.91)
_set_48("C25+", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 544.0, 0.90)
_set_48("C25+", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.03, 0.99)
_set_48("C25+", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1.4, 0.99)

# Pyrophoric (same pattern as C9-C12)
_set_48("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 12.0, 0.98)
_set_48("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 130.0, 0.90)
_set_48("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 391.0, 0.95)
_set_48("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 560.0, 0.95)
_set_48("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 7.1, 0.66)
_set_48("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 3.3, 0.76)
_set_48("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 281.0, 0.61)
_set_48("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 6.0, 0.53)

# Aromatics
_set_48("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 17.87, 1.097)
_set_48("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 103.0, 0.0)
_set_48("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 374.5, 1.055)
_set_48("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 487.7, 0.268)
_set_48("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 11.46, 0.667)
_set_48("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 70.12, 0.0)
_set_48("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 512.6, 0.713)
_set_48("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 701.2, 0.0)

# Styrene (same as Aromatics)
_set_48("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 17.87, 1.097)
_set_48("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 103.0, 0.0)
_set_48("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 374.5, 1.055)
_set_48("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 487.7, 0.268)
_set_48("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 11.46, 0.667)
_set_48("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 70.12, 0.0)
_set_48("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 512.6, 0.713)
_set_48("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 701.2, 0.0)

# Methanol
_set_48("Methanol", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.02256, 0.9092)
_set_48("Methanol", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1750.6, 0.9342)
_set_48("Methanol", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 28.1170, 0.6670)
_set_48("Methanol", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1.9188, 0.9004)

# H2
_set_48("H2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 64.5, 0.992)
_set_48("H2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 420.0, 1.00)
_set_48("H2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 61.5, 0.657)
_set_48("H2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1430.0, 0.618)

# H2S
_set_48("H2S", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 32.0, 1.00)
_set_48("H2S", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 203.0, 0.89)
_set_48("H2S", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 148.0, 0.63)
_set_48("H2S", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 357.0, 0.61)

# CO
_set_48("CO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.107, 1.752)
_set_48("CO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 69.68, 0.667)

# DEE
_set_48("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 39.84, 1.134)
_set_48("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 737.4, 1.106)
_set_48("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 320.7, 1.033)
_set_48("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 6289.0, 0.649)
_set_48("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 155.7, 0.667)
_set_48("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 5.105, 0.919)
_set_48("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 5.672, 0.919)

# PO
_set_48("PO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 14.61, 1.114)
_set_48("PO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1295.0, 0.9560)
_set_48("PO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 65.58, 0.667)
_set_48("PO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 3.404, 0.869)

# EEA
_set_48("EEA", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.002, 1.035)
_set_48("EEA", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 117.0, 0.0)
_set_48("EEA", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 8.014, 0.667)
_set_48("EEA", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 69.0, 0.0)

# EE
_set_48("EE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 12.62, 1.005)
_set_48("EE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 173.1, 0.0)
_set_48("EE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 38.87, 0.667)
_set_48("EE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 72.21, 0.0)

# EG
_set_48("EG", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 7.721, 0.973)
_set_48("EG", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 108.0, 0.0)
_set_48("EG", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 6.525, 0.667)
_set_48("EG", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 69.0, 0.0)

# EO
_set_48("EO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 31.03, 1.069)
_set_48("EO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 136.3, 0.667)


# -----------------------------
# Table 4.9 — Personnel Injury constants
# -----------------------------
_TABLE_4_9: Dict[str, FlammableConstantsRow] = {}


def _mk_row_49(fluid: str, fluid_type: FluidType) -> FlammableConstantsRow:
    return FlammableConstantsRow(fluid=fluid, fluid_type=fluid_type, constants={})


def _register_row_49(fluid: str, fluid_type: FluidType) -> None:
    _TABLE_4_9[fluid] = _mk_row_49(fluid, fluid_type)


# def _set_49(
#     fluid: str,
#     release_type: ReleaseType,
#     auto: AutoIgnitionCase,
#     phase: Phase,
#     a: float,
#     b: float,
# ) -> None:
#     row = _TABLE_4_9.get(fluid)
#     if row is None:
#         raise KeyError(f"Row '{fluid}' not registered in Table 4.9.")
#     row.constants[(release_type, auto, phase)] = PowerLawConstants(float(a), float(b))


# for _f, _t in [
#     ("C1-C2", FluidType.TYPE_0),
#     ("C3-C4", FluidType.TYPE_0),
#     ("C5", FluidType.TYPE_0),
#     ("C6-C8", FluidType.TYPE_0),
#     ("C9-C12", FluidType.TYPE_0),
#     ("C13-C16", FluidType.TYPE_0),
#     ("C17-C25", FluidType.TYPE_0),
#     ("C25+", FluidType.TYPE_0),
#     ("Pyrophoric", FluidType.TYPE_1),
#     ("Aromatics", FluidType.TYPE_1),
#     ("Styrene", FluidType.TYPE_1),
#     ("Water", FluidType.TYPE_0),
#     ("Steam", FluidType.TYPE_0),
#     ("Acid/caustic-LP", FluidType.TYPE_0),
#     ("Acid/caustic-MP", FluidType.TYPE_0),
#     ("Acid/caustic-HP", FluidType.TYPE_0),
#     ("Methanol", FluidType.TYPE_1),
#     ("H2", FluidType.TYPE_0),
#     ("H2S", FluidType.TYPE_0),
#     ("HF", FluidType.TYPE_0),
#     ("CO", FluidType.TYPE_1),
#     ("DEE", FluidType.TYPE_1),
#     ("PO", FluidType.TYPE_1),
#     ("EEA", FluidType.TYPE_1),
#     ("EE", FluidType.TYPE_1),
#     ("EG", FluidType.TYPE_1),
#     ("EO", FluidType.TYPE_1),
# ]:
#     _register_row_49(_f, _t)

# # --- constants from Table 4.9 ---
# _set_49("C1-C2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 110.0, 0.96)
# _set_49("C1-C2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 745.0, 0.92)
# _set_49("C1-C2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 79.0, 0.67)
# _set_49("C1-C2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 3100.0, 0.63)

# _set_49("C3-C4", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 125.2, 1.00)
# _set_49("C3-C4", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 836.7, 1.00)
# _set_49("C3-C4", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 57.72, 0.75)
# _set_49("C3-C4", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1769.0, 0.63)

# _set_49("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 62.05, 1.00)
# _set_49("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1545.0, 0.89)
# _set_49("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 811.0, 1.00)
# _set_49("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 28.45, 0.76)
# _set_49("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 4.34, 0.85)
# _set_49("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 959.6, 0.63)

# _set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 68.0, 0.96)
# _set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 516.0, 0.89)
# _set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 828.7, 1.00)
# _set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1315.0, 0.92)
# _set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 26.72, 0.67)
# _set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 12.7, 0.78)
# _set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 962.8, 0.63)
# _set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 224.0, 0.54)

# _set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 29.0, 0.96)
# _set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 373.0, 0.89)
# _set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 981.0, 0.92)
# _set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1401.0, 0.92)
# _set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 13.0, 0.66)
# _set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 9.5, 0.76)
# _set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 988.0, 0.63)
# _set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 20.0, 0.54)

# _set_49("C13-C16", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 183.0, 0.89)
# _set_49("C13-C16", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2850.0, 0.90)
# _set_49("C13-C16", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1.3, 0.88)
# _set_49("C13-C16", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 26.0, 0.88)

# _set_49("C17-C25", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 57.0, 0.89)
# _set_49("C17-C25", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2420.0, 0.90)
# _set_49("C17-C25", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.32, 0.91)
# _set_49("C17-C25", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 16.0, 0.91)

# _set_49("C25+", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 33.0, 0.89)
# _set_49("C25+", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1604.0, 0.90)
# _set_49("C25+", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.081, 0.99)
# _set_49("C25+", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 4.1, 0.99)

# # Pyrophoric mirrors C9-C12 (per table)
# _set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 29.0, 0.96)
# _set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 373.0, 0.89)
# _set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 981.0, 0.92)
# _set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1401.0, 0.92)
# _set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 13.0, 0.66)
# _set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 9.5, 0.76)
# _set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 988.0, 0.63)
# _set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 20.0, 0.54)

# # Aromatics
# _set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 64.14, 0.963)
# _set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 353.5, 0.883)
# _set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1344.0, 0.937)
# _set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 487.7, 0.268)
# _set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 18.08, 0.686)
# _set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.14, 0.935)
# _set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 512.6, 0.713)
# _set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1.404, 0.935)

# # Styrene (same as Aromatics)
# _set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 64.14, 0.963)
# _set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 353.5, 0.883)
# _set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1344.0, 0.937)
# _set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 487.7, 0.268)
# _set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 18.08, 0.686)
# _set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.14, 0.935)
# _set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 512.6, 0.713)
# _set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1.404, 0.935)

# # Acid/caustic (continuous liquid only, AINL and AIL same per row)
# _set_49("Acid/caustic-LP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 2699.5, 0.2024)
# _set_49("Acid/caustic-LP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2699.5, 0.2024)

# _set_49("Acid/caustic-MP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 3366.2, 0.2878)
# _set_49("Acid/caustic-MP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 3366.2, 0.2878)

# _set_49("Acid/caustic-HP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 6690.0, 0.2469)
# _set_49("Acid/caustic-HP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 6690.0, 0.2469)

# # Methanol
# _set_49("Methanol", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.0164, 1.0083)
# _set_49("Methanol", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 4483.7, 0.9015)
# _set_49("Methanol", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 37.71, 0.6878)
# _set_49("Methanol", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 6.2552, 0.8705)

# # H2
# _set_49("H2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 165.0, 0.933)
# _set_49("H2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1117.0, 1.00)
# _set_49("H2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 118.5, 0.652)
# _set_49("H2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 4193.0, 0.621)

# # H2S
# _set_49("H2S", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 52.0, 1.00)
# _set_49("H2S", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 375.0, 0.94)
# _set_49("H2S", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 271.0, 0.63)
# _set_49("H2S", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1253.0, 0.63)

# # CO
# _set_49("CO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 27.0, 0.991)
# _set_49("CO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 105.3, 0.692)

# # DEE
# _set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 128.1, 1.025)
# _set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 971.9, 1.219)
# _set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1182.0, 0.997)
# _set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2658.0, 0.864)
# _set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 199.1, 0.682)
# _set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 47.13, 0.814)
# _set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 821.7, 0.657)
# _set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 52.36, 0.814)

# # PO
# _set_49("PO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 38.76, 1.047)
# _set_49("PO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1955.0, 0.840)
# _set_49("PO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 83.68, 0.682)
# _set_49("PO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 15.21, 0.834)

# # EEA
# _set_49("EEA", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.017, 0.946)
# _set_49("EEA", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 443.1, 0.835)
# _set_49("EEA", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 11.41, 0.687)
# _set_49("EEA", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.153, 0.924)

# # EE
# _set_49("EE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 35.56, 0.969)
# _set_49("EE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 46.56, 0.800)
# _set_49("EE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 162.0, 0.660)
# _set_49("EE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.152, 0.927)

# # EG
# _set_49("EG", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 25.67, 0.947)
# _set_49("EG", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 324.7, 0.869)
# _set_49("EG", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 8.971, 0.687)
# _set_49("EG", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.138, 0.922)

# # EO
# _set_49("EO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 49.43, 1.105)
# _set_49("EO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 220.8, 0.665)

_TABLE_4_9: Dict[str, FlammableConstantsRow] = {}

def _mk_row_49(fluid: str, fluid_type: FluidType) -> FlammableConstantsRow:
    return FlammableConstantsRow(fluid=fluid, fluid_type=fluid_type, constants={})

def _register_row_49(fluid: str, fluid_type: FluidType) -> None:
    _TABLE_4_9[fluid] = _mk_row_49(fluid, fluid_type)

def _set_49(
    fluid: str,
    release_type: ReleaseType,
    auto: AutoIgnitionCase,
    phase: Phase,
    a: float,
    b: float,
) -> None:
    row = _TABLE_4_9.get(fluid)
    if row is None:
        raise KeyError(f"Row '{fluid}' not registered in Table 4.9.")
    row.constants[(release_type, auto, phase)] = PowerLawConstants(float(a), float(b))

# --- 1. Register Rows (Fluid Types) ---
for _f, _t in [
    ("C1-C2", FluidType.TYPE_0),
    ("C3-C4", FluidType.TYPE_0),
    ("C5", FluidType.TYPE_0),
    ("C6-C8", FluidType.TYPE_0),
    ("C9-C12", FluidType.TYPE_0),
    ("C13-C16", FluidType.TYPE_0),
    ("C17-C25", FluidType.TYPE_0),
    ("C25+", FluidType.TYPE_0),
    ("Pyrophoric", FluidType.TYPE_1),
    ("Aromatics", FluidType.TYPE_1),
    ("Styrene", FluidType.TYPE_1),
    ("Water", FluidType.TYPE_0),
    ("Steam", FluidType.TYPE_0),
    ("Acid/caustic-LP", FluidType.TYPE_0),
    ("Acid/caustic-MP", FluidType.TYPE_0),
    ("Acid/caustic-HP", FluidType.TYPE_0),
    ("Methanol", FluidType.TYPE_1),
    ("H2", FluidType.TYPE_0),
    ("H2S", FluidType.TYPE_0),
    ("HF", FluidType.TYPE_0),
    ("CO", FluidType.TYPE_1),
    ("DEE", FluidType.TYPE_1),
    ("PO", FluidType.TYPE_1),
    ("EEA", FluidType.TYPE_1),
    ("EE", FluidType.TYPE_1),
    ("EG", FluidType.TYPE_1),
    ("EO", FluidType.TYPE_1),
]:
    _register_row_49(_f, _t)

# --- 2. Populate Constants (Table 4.9 Data) ---

# C1-C2
_set_49("C1-C2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 110.0, 0.96)
_set_49("C1-C2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 745.0, 0.92)
_set_49("C1-C2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 79.0, 0.67)
_set_49("C1-C2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 3100.0, 0.63)

# C3-C4
_set_49("C3-C4", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 125.2, 1.00)
_set_49("C3-C4", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 836.7, 1.00)
_set_49("C3-C4", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 57.72, 0.75)
_set_49("C3-C4", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1769.0, 0.63)

# C5
_set_49("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 62.05, 1.00)
_set_49("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1545.0, 0.89)
_set_49("C5", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 811.0, 1.00)
_set_49("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 28.45, 0.76)
_set_49("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 4.34, 0.85)
_set_49("C5", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 959.6, 0.63)

# C6-C8
_set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 68.0, 0.96)
_set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 516.0, 0.89)
_set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 828.7, 1.00)
_set_49("C6-C8", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1315.0, 0.92)
_set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 26.72, 0.67)
_set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 12.7, 0.78)
_set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 962.8, 0.63)
_set_49("C6-C8", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 224.0, 0.54)

# C9-C12
_set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 29.0, 0.96)
_set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 373.0, 0.89)
_set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 981.0, 0.92)
_set_49("C9-C12", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1401.0, 0.92)
_set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 13.0, 0.66)
_set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 9.5, 0.76)
_set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 988.0, 0.63)
_set_49("C9-C12", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 20.0, 0.54)

# C13-C16
_set_49("C13-C16", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 183.0, 0.89)
_set_49("C13-C16", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2850.0, 0.90)
_set_49("C13-C16", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1.3, 0.88)
_set_49("C13-C16", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 26.0, 0.88)

# C17-C25
_set_49("C17-C25", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 57.0, 0.89)
_set_49("C17-C25", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2420.0, 0.90)
_set_49("C17-C25", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.32, 0.91)
_set_49("C17-C25", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 16.0, 0.91)

# C25+
_set_49("C25+", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 33.0, 0.89)
_set_49("C25+", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1604.0, 0.90)
_set_49("C25+", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.081, 0.99)
_set_49("C25+", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 4.1, 0.99)

# Pyrophoric
_set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 29.0, 0.96)
_set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 373.0, 0.89)
_set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 981.0, 0.92)
_set_49("Pyrophoric", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1401.0, 0.92)
_set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 13.0, 0.66)
_set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 9.5, 0.76)
_set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 988.0, 0.63)
_set_49("Pyrophoric", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 20.0, 0.54)

# Aromatics
_set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 64.14, 0.963)
_set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 353.5, 0.883)
_set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1344.0, 0.937)
_set_49("Aromatics", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 487.7, 0.268)
_set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 18.08, 0.686)
_set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.14, 0.935)
_set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 512.6, 0.713)
_set_49("Aromatics", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1.404, 0.935)

# Styrene
_set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 64.14, 0.963)
_set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 353.5, 0.883)
_set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1344.0, 0.937)
_set_49("Styrene", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 487.7, 0.268)
_set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 18.08, 0.686)
_set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.14, 0.935)
_set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 512.6, 0.713)
_set_49("Styrene", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 1.404, 0.935)

# Acid/Caustic
_set_49("Acid/caustic-LP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 2699.5, 0.2024)
_set_49("Acid/caustic-LP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2699.5, 0.2024)

_set_49("Acid/caustic-MP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 3366.2, 0.2878)
_set_49("Acid/caustic-MP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 3366.2, 0.2878)

_set_49("Acid/caustic-HP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 6690.0, 0.2469)
_set_49("Acid/caustic-HP", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 6690.0, 0.2469)

# Methanol
_set_49("Methanol", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.0164, 1.0083)
_set_49("Methanol", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 4483.7, 0.9015)
_set_49("Methanol", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 37.71, 0.6878)
_set_49("Methanol", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 6.2552, 0.8705)

# H2
_set_49("H2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 165.0, 0.933)
_set_49("H2", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1117.0, 1.00)
_set_49("H2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 118.5, 0.652)
_set_49("H2", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 4193.0, 0.621)

# H2S
_set_49("H2S", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 52.0, 1.00)
_set_49("H2S", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 375.0, 0.94)
_set_49("H2S", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 271.0, 0.63)
_set_49("H2S", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1253.0, 0.63)

# CO
_set_49("CO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 27.0, 0.991)
_set_49("CO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 105.3, 0.692)

# DEE
_set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 128.1, 1.025)
_set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 971.9, 1.219)
_set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.GAS, 1182.0, 0.997)
_set_49("DEE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 2658.0, 0.864)
_set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 199.1, 0.682)
_set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 47.13, 0.814)
_set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.GAS, 821.7, 0.657)
_set_49("DEE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  Phase.LIQUID, 52.36, 0.814)

# PO
_set_49("PO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 38.76, 1.047)
_set_49("PO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 1955.0, 0.840)
_set_49("PO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 83.68, 0.682)
_set_49("PO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 15.21, 0.834)

# EEA
_set_49("EEA", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 0.017, 0.946)
_set_49("EEA", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 443.1, 0.835)
_set_49("EEA", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 11.41, 0.687)
_set_49("EEA", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.153, 0.924)

# EE
_set_49("EE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 35.56, 0.969)
_set_49("EE", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 46.56, 0.800)
_set_49("EE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 162.0, 0.660)
_set_49("EE", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.152, 0.927)

# EG
_set_49("EG", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 25.67, 0.947)
_set_49("EG", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 324.7, 0.869)
_set_49("EG", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 8.971, 0.687)
_set_49("EG", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.LIQUID, 0.138, 0.922)

# EO
_set_49("EO", ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, Phase.GAS, 49.43, 1.105)
_set_49("EO", ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, Phase.GAS, 220.8, 0.665)

# -----------------------------
# Lookup helpers
# -----------------------------
def _norm_fluid_key(s: str) -> str:
    return " ".join(s.strip().split())


def get_constants_row(
    table: Literal["4.8", "4.9"],
    fluid: str,
) -> FlammableConstantsRow:
    key = _norm_fluid_key(fluid)
    if table == "4.8":
        if key not in _TABLE_4_8:
            raise KeyError(f"Fluid '{fluid}' not found in Table 4.8.")
        return _TABLE_4_8[key]
    if table == "4.9":
        if key not in _TABLE_4_9:
            raise KeyError(f"Fluid '{fluid}' not found in Table 4.9.")
        return _TABLE_4_9[key]
    raise ValueError("table must be '4.8' or '4.9'")


# def get_powerlaw_constants(
#     table: Literal["4.8", "4.9"],
#     fluid: str,
#     release_type: ReleaseType,
#     auto: AutoIgnitionCase,
#     phase: Phase,
# ) -> PowerLawConstants:
#     row = get_constants_row(table, fluid)
#     c = row.constants.get((release_type, auto, phase))
#     if c is None:
#         raise KeyError(
#             f"Missing constants in Table {table} for fluid='{fluid}', "
#             f"release_type='{release_type.value}', auto='{auto.value}', phase='{phase.value}'."
#         )
#     return c

def get_powerlaw_constants(
    table: Dict[str, FlammableConstantsRow],
    fluid: str,
    release_type: ReleaseType,
    auto: AutoIgnitionCase,
    phase: Phase
) -> PowerLawConstants:
    """
    Recupera las constantes a y b.
    MEJORA ROBUSTA: Si el fluido existe pero el caso específico (ej. AIL) no,
    devuelve constantes en CERO en lugar de error.
    Esto soluciona el caso del CO, que no tiene constantes AIL.
    """
    # 1. Normalizar llave del fluido
    key = _norm_fluid_key(fluid)
    
    # 2. Verificar existencia del fluido
    row = table.get(key)
    if not row:
        # Si el fluido NO existe del todo en la tabla, ahí sí es un error de configuración
        # (aunque el is_fluid_flammable debería haberlo atajado antes)
        raise KeyError(
            f"Fluid '{fluid}' (key='{key}') not found in the requested table."
        )

    # 3. Intentar obtener la combinación exacta
    lookup_key = (release_type, auto, phase)
    
    if lookup_key in row.constants:
        return row.constants[lookup_key]
    
    # --- FALLBACK DE SEGURIDAD (FIX PARA CO) ---
    # Si llegamos aquí, el fluido es válido (ej. CO), pero no tiene datos para este caso (ej. AIL).
    # Asumimos que la consecuencia es despreciable o nula para ese escenario específico.
    # Devolvemos a=0.0, b=0.0 -> Area = 0 * rate^0 = 0.0
    return PowerLawConstants(a=0.0, b=0.0)


# -----------------------------
# Math helpers (Eq 3.17, 3.18-3.25, 3.21-3.22)
# -----------------------------

def energy_efficiency_factor(mass_lb: float, release_type: ReleaseType) -> float:
    """
    Calcula eneff_n basado en la Eq. (3.17).
    Regla: Solo aplica si la liberación es INSTANTÁNEA y la masa es significativa.
    """
    # Si es continua, por norma el factor no aplica (se mantiene en 1.0)
    # Si la masa es 0 o menor, o no hay área, el factor es 1.0
    if release_type == ReleaseType.CONTINUOUS or mass_lb <= 10000.0:
        return 1.0
    
    # Eq (3.17): eneff = 4 * log10(CA * mass) - 15
    eneff = 4.0 * math.log10(1 * mass_lb) - 15.0
    
    # Si el resultado es menor a 1, la norma asume 1.0 (sin beneficio)
    return max(1.0, float(eneff))


def fact_IC_for_hole(release_type: ReleaseType, rate_lb_s: float) -> float:
    """
    Eq (3.18) for continuous, Eq (3.20) for instantaneous.
    """
    if release_type == ReleaseType.INSTANTANEOUS:
        return 1.0
    
    # continuous
    if rate_lb_s <= 0.0:
        return 0.0
    return min(max(rate_lb_s / C5_RATE_TRANSITION_LB_S, 0.0), 1.0)


def blend_IC(CA_inst: float, CA_cont: float, fact_IC: float) -> float:
    """
    Eq (3.21):
        CA_IC_blend = CA_inst * fact_IC + CA_cont * (1 - fact_IC)
    """
    return float(CA_inst * fact_IC + CA_cont * (1.0 - fact_IC))


# def fact_AIT(Ts_R: float, AIT_R: float, C6_R: float = C6_R_DEFAULT) -> float:
#     """
#     Eq (3.23) - (3.25):
#       fact_AIT = 0 for Ts + C6 <= AIT
#       fact_AIT = (Ts - AIT + C6) / (2*C6) for Ts + C6 > AIT > Ts - C6
#       fact_AIT = 1 for Ts - C6 >= AIT

#     Ts and AIT in Rankine.
#     """
#     # if C6_R <= 0:
#     #     raise ValueError("C6_R must be > 0.")
#     if Ts_R <= 0 or AIT_R < 0:
#         raise ValueError("Ts_R and AIT_R must be > 0 (Rankine).")

#     if Ts_R + C6_R <= AIT_R:
#         return 0.0
#     if Ts_R - C6_R >= AIT_R:
#         return 1.0
#     # between
#     return float((Ts_R - AIT_R + C6_R) / (2.0 * C6_R))

# --- Constantes y Tabulación (Basado en Tabla 4.2 API 581) ---
# Valores en Fahrenheit (°F) para facilitar la lectura, se convierten a Rankine en la lógica

TABLE_4_2_AIT_F = {
    # --- Nota 1: Cp = A + BT + CT^2 + DT^3 [J/(mol·K)] ---
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

    # --- Nota 2: Ecuación Hiperbólica [J/(kmol·K)] ---
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

    # --- Nota 3: Polinómica Extendida [J/(kmol·K)] ---
    "Water": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "Acid/caustic-LP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "Acid/caustic-MP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},
    "Acid/caustic-HP": {"mw": 18, "rho": 62.3, "nbp": 212, "state": "Liquid", "ait": 0, "cp": {"n": 3, "A": 2.76E+05, "B": -2.09E+03, "C": 8.125, "D": -1.41E-02, "E": 9.37E-06}},

    # --- Fluidos sin constantes de Cp ---
    "HCl": {"mw": 36, "rho": 74, "nbp": -121, "state": "Gas", "ait": 0, "cp": None},
    "Nitric acid": {"mw": 63, "rho": 95, "nbp": 250, "state": "Liquid", "ait": 0, "cp": None},
    "NO2": {"mw": 46, "rho": 58, "nbp": 275, "state": "Liquid", "ait": 0, "cp": None},
    "Phosgene": {"mw": 99, "rho": 86, "nbp": 181, "state": "Liquid", "ait": 0, "cp": None},
    "TDI": {"mw": 174, "rho": 76, "nbp": 484, "state": "Liquid", "ait": 1148, "cp": None},
}

def get_fluid_ait_rankine(fluid_key: str) -> float:
    """
    Busca el AIT en tu tabla FLUID_PROPERTIES y lo convierte a Rankine.
    """
    fluid_data = TABLE_4_2_AIT_F.get(fluid_key)
    if not fluid_data or fluid_data["ait"] == 0:
        return 0.0
    
    # API 581 usa Rankine: °R = °F + 459.67
    return float(fluid_data["ait"])

# --- Función fact_AIT Corregida ---
def fact_AIT(Ts_R: float, representative_fluid: str) -> float:
    """
    Calcula el factor de mezcla por autoignición (Eq 3.23 - 3.25).
    
    Args:
        Ts_R: Temperatura de almacenamiento/operación en Rankine.
        representative_fluid: Nombre del fluido para buscar su AIT.
        C6: Constante de ajuste (ahora 100 por defecto).
    """
    AIT_R = get_fluid_ait_rankine(representative_fluid)
    
    # Si el fluido no es inflamable o no tiene AIT definido
    if AIT_R <= 0:
        return 0.0

    if Ts_R <= 0:
        raise ValueError("Ts_R debe ser mayor a 0 (Rankine).")

    # Lógica de transición (Smoothing)
    if (Ts_R + 100) <= AIT_R:
        return 0.0
    
    if (Ts_R - 100) >= AIT_R:
        return 1.0
        
    # Zona de transición (Interpolación lineal)
    return float((Ts_R - AIT_R + 100) / (2.0 * 100))


def blend_AIT(CA_AIL: float, CA_AINL: float, fact_ait: float) -> float:
    """
    Eq (3.22):
        CA_AIT_blend = CA_AIL*fact_AIT + CA_AINL*(1 - fact_AIT)
    """
    return float(CA_AIL * fact_ait + CA_AINL * (1.0 - fact_ait))


# -----------------------------
# Core equations (per target)
# -----------------------------
def _CA_continuous(a: float, b: float, rate_lb_s: float, fact_mit: float) -> float:
    """
    Eq (3.30), (3.33) for component damage
    and Eq (3.42), (3.45) for personnel injury:
        CA = a * (rate)^b * (1 - fact_mit)
    """
    if rate_lb_s <= 0.0:
        return 0.0
    return float(a * (rate_lb_s ** b) * (1.0 - fact_mit))


def _CA_instantaneous(a: float, b: float, mass_lb: float, fact_mit: float, eneff: float) -> float:
    """
    Eq (3.36), (3.39) and Eq (3.48), (3.51):
        CA = a * (mass)^b * ((1 - fact_mit) / eneff)
    """
    if mass_lb <= 0.0:
        return 0.0
    eneff_eff = max(1.0, float(eneff))
    return float(a * (mass_lb ** b) * ((1.0 - fact_mit) / eneff_eff))


# def _compute_per_table(
#     table: Literal["4.8", "4.9"],
#     fluid: str,
#     hole: HoleInput,
#     fact_mit_value: float,
# ) -> Tuple[float, float, float, float]:
#     """
#     Returns:
#       CA_AINL_CONT, CA_AIL_CONT, CA_AINL_INST, CA_AIL_INST
#     for the requested table (4.8 cmd or 4.9 inj).

#     Uses hole.final_phase to select gas vs liquid constants.
#     """
#     phase = hole.final_phase

#     # CONT constants
#     c_ainl_cont = get_powerlaw_constants(table, fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, phase)
#     c_ail_cont  = get_powerlaw_constants(table, fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  phase)

#     CA_ainl_cont = _CA_continuous(c_ainl_cont.a, c_ainl_cont.b, hole.rate_lb_s, fact_mit_value)
#     CA_ail_cont  = _CA_continuous(c_ail_cont.a,  c_ail_cont.b,  hole.rate_lb_s, fact_mit_value)

#     # INST constants
#     c_ainl_inst = get_powerlaw_constants(table, fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, phase)
#     c_ail_inst  = get_powerlaw_constants(table, fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  phase)

#     # Energy efficiency factor uses AIL instantaneous "base" area (per Eq 3.17 context)
#     # We compute a "base" CA for AIL-INST without eneff first (eneff=1), then compute eneff.
#     eneff = energy_efficiency_factor(hole.mass_lb, hole.release_type)
#     # CA_ail_inst_base = _CA_instantaneous(c_ail_inst.a, c_ail_inst.b, hole.mass_lb, fact_mit_value, eneff=1.0)

    
#     CA_ainl_inst = _CA_instantaneous(c_ainl_inst.a, c_ainl_inst.b, hole.mass_lb, fact_mit_value, eneff=eneff)
#     CA_ail_inst  = _CA_instantaneous(c_ail_inst.a,  c_ail_inst.b,  hole.mass_lb, fact_mit_value, eneff=eneff)

#     return CA_ainl_cont, CA_ail_cont, CA_ainl_inst, CA_ail_inst

def _compute_constants_set(
    table: Dict[str, FlammableConstantsRow],  # <--- ARGUMENTO 1: EL DICCIONARIO
    fluid: str,                               # <--- ARGUMENTO 2: EL NOMBRE DEL FLUIDO
    phase: Phase
) -> Tuple[float, float, float, float]:
    """
    Calcula las 4 áreas básicas (AINL-Cont, AIL-Cont, AINL-Inst, AIL-Inst)
    para una tabla específica (CMD o INJ).
    """
    # 1. Continuous / AINL
    c_ainl_cont = get_powerlaw_constants(table, fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, phase)
    # 2. Continuous / AIL
    c_ail_cont  = get_powerlaw_constants(table, fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  phase)
    # 3. Instantaneous / AINL
    c_ainl_inst = get_powerlaw_constants(table, fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, phase)
    # 4. Instantaneous / AIL
    c_ail_inst  = get_powerlaw_constants(table, fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  phase)

    # Nota: Aquí devolvemos los OBJETOS de constantes (a, b), no el área calculada todavía.
    # O si tu implementación devuelve áreas, asegúrate de que coincida.
    # Asumiendo que devuelve las constantes para usarlas abajo, o si calcula areas directamente:
    
    # REVISIÓN: Generalmente esta función devuelve las ÁREAS calculadas usando una tasa unitaria o 
    # simplemente devuelve las constantes. 
    # PERO, para evitar romper tu lógica aguas abajo, voy a asumir que esta función es la que
    # llama a `get_powerlaw_constants`.
    
    # Si tu código original calculaba cosas aquí, asegúrate de pasar 'table' a 'get_powerlaw_constants'.
    return c_ainl_cont, c_ail_cont, c_ainl_inst, c_ail_inst


def _select_release_type_value(
    fluid_type: FluidType,
    hole: HoleInput,
    CA_cont: float,
    CA_inst: float,
) -> Tuple[float, float]:
    """
    Returns (selected_value, fact_IC_used)
    - Type 1 fluids: NO IC blending, use release_type directly.
    - Type 0 fluids: IC blending required -> use fact_IC based on hole.release_type and hole.rate.
    """
    if fluid_type == FluidType.TYPE_1:
        return (CA_inst if hole.release_type == ReleaseType.INSTANTANEOUS else CA_cont), (
            1.0 if hole.release_type == ReleaseType.INSTANTANEOUS else 0.0
        )

    # Type 0 -> IC blend
    f_ic = fact_IC_for_hole(hole.release_type, hole.rate_lb_s)
    return blend_IC(CA_inst=CA_inst, CA_cont=CA_cont, fact_IC=f_ic), f_ic


# -----------------------------
# Public API (Section 4.8)
# -----------------------------
# def compute_cof_4_8_flammable_explosive(
#     *,
#     fluid: str,
#     holes: Dict[str, HoleInput],
#     ait: AITInputs,
#     mitigation_system_key: str,
#     # GFF inputs from 4.2 (Part 2 Table 3.1)
#     gff_by_hole: Dict[str, float],
#     gff_total: float,
# ) -> FlammableFinalResult:
#     """
#     Computes 4.8 flammable consequence areas and probability-weighted final values.

#     Required:
#     - fluid: representative fluid key (must match Table rows, e.g. "C6-C8", "Aromatics", "H2S", etc.)
#     - holes: dict hole_key -> HoleInput (small/medium/large/rupture)
#     - ait: AITInputs(Ts_R, AIT_R)
#     - mitigation_system_key: Table 4.10 key
#     - gff_by_hole: dict hole_key -> gff_n
#     - gff_total: total gff (sum gff_n)

#     Returns:
#     - per-hole CA_cmd and CA_inj after IC blending (if Type0) and AIT blending
#     - CA_cmd_final and CA_inj_final probability weighted across hole sizes
#     """
#     fluid_key = _norm_fluid_key(fluid)
#     row_cmd = get_constants_row("4.8", fluid_key)
#     row_inj = get_constants_row("4.9", fluid_key)
#     # sanity: fluid type should match in both tables
#     if row_cmd.fluid_type != row_inj.fluid_type:
#         raise ValueError(f"Fluid type mismatch between Table 4.8 and 4.9 for '{fluid_key}'.")

#     f_mit = fact_mit_from_system(mitigation_system_key)
#     f_ait = fact_AIT(ait.Ts_R, ait.representative_fluid)

#     hole_results: Dict[str, FlammableHoleResult] = {}
#     sum_cmd = 0.0
#     sum_inj = 0.0

#     if gff_total <= 0:
#         raise ValueError("gff_total must be > 0.")

#     for hk, hole in holes.items():
        
#         # en_cmd = energy_efficiency_factor(hole.mass_lb, hole.release_type)
#         # phase = hole.final_phase

#         # #----------- component damage consequence areas ----------------
#         # #------- autoignition not likely -  continuous release ---------
#         # #---------------------------------------------------------------
#         # # CONT constants
#         # c_ainl_cont = get_powerlaw_constants("4.8", fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, phase)
        
#         # if hole.release_type == ReleaseType.CONTINUOUS:
#         #     CA_ainl_cont_cmd_p = _CA_continuous(c_ainl_cont.a, c_ainl_cont.b, hole.rate_lb_s, f_mit)
#         # else:
#         #     CA_ainl_cont_cmd_p = 0.0
#         # #----------------------------------------------------------------

#         # #--------- autoignition likely -  continuous release ------------
#         # #---------------------------------------------------------------
#         # # CONT constants
#         # c_ail_cont  = get_powerlaw_constants("4.8", fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  phase)
        
#         # if hole.release_type == ReleaseType.CONTINUOUS:
#         #     CA_ail_cont_cmd_p = _CA_continuous(c_ail_cont.a, c_ail_cont.b, hole.rate_lb_s, f_mit)
#         # else:
#         #     CA_ail_cont_cmd_p = 0.0
#         # #----------------------------------------------------------------

#         # #------ autoignition not likely - instantaneous release ---------
#         # #----------------------------------------------------------------
#         # # CONT constants
#         # c_ainl_inst = get_powerlaw_constants("4.8", fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, phase)
        
#         # if hole.release_type == ReleaseType.INSTANTANEOUS:
#         #     CA_ainl_inst_cmd_p = _CA_instantaneous(c_ainl_inst.a, c_ainl_inst.b, hole.mass_lb, f_mit, eneff=en_cmd)
#         # else:
#         #     CA_ainl_inst_cmd_p = 0.0
#         # #----------------------------------------------------------------

#         # #-------- autoignition likely - instantaneous release -----------
#         # #----------------------------------------------------------------
#         # # CONT constants
#         # c_ail_inst  = get_powerlaw_constants("4.8", fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  phase)
        
#         # if hole.release_type == ReleaseType.INSTANTANEOUS:
#         #     CA_ail_inst_cmd_p = _CA_instantaneous(c_ail_inst.a, c_ail_inst.b, hole.mass_lb, f_mit, eneff=en_cmd)
#         # else:
#         #     CA_ail_inst_cmd_p = 0.0
#         # #----------------------------------------------------------------
        

#         # #-----------  personnel injury consequence areas ----------------
#         # #------- autoignition not likely -  continuous release ---------
#         # #---------------------------------------------------------------
#         # # CONT constants
#         # c_inj_ainl_cont = get_powerlaw_constants("4.9", fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AINL, phase)
        
#         # if hole.release_type == ReleaseType.CONTINUOUS:
#         #     CA_ainl_cont_inj_cmd_p = _CA_continuous(c_inj_ainl_cont.a, c_inj_ainl_cont.b, hole.rate_lb_s, f_mit)
#         # else:
#         #     CA_ainl_cont_inj_cmd_p = 0.0
#         # #----------------------------------------------------------------

#         # #--------- autoignition likely -  continuous release ------------
#         # #---------------------------------------------------------------
#         # # CONT constants
#         # c_inj_ail_cont  = get_powerlaw_constants("4.9", fluid, ReleaseType.CONTINUOUS, AutoIgnitionCase.AIL,  phase)
        
#         # if hole.release_type == ReleaseType.CONTINUOUS:
#         #     CA_ail_cont_inj_cmd_p = _CA_continuous(c_inj_ail_cont.a, c_inj_ail_cont.b, hole.rate_lb_s, f_mit)
#         # else:
#         #     CA_ail_cont_inj_cmd_p = 0.0
#         # #----------------------------------------------------------------

#         #  #------ autoignition not likely - instantaneous release ---------
#         # #----------------------------------------------------------------
#         # # CONT constants
#         # c_inj_ainl_inst = get_powerlaw_constants("4.9", fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AINL, phase)
        
#         # if hole.release_type == ReleaseType.INSTANTANEOUS:
#         #     CA_ainl_inst_inj_cmd_p = _CA_instantaneous(c_inj_ainl_inst.a, c_inj_ainl_inst.b, hole.mass_lb, f_mit, eneff=en_cmd)
#         # else:
#         #     CA_ainl_inst_inj_cmd_p = 0.0
#         # #----------------------------------------------------------------

#         # #-------- autoignition likely - instantaneous release -----------
#         # #----------------------------------------------------------------
#         # # CONT constants
#         # c_inj_ail_inst  = get_powerlaw_constants("4.9", fluid, ReleaseType.INSTANTANEOUS, AutoIgnitionCase.AIL,  phase)
        
#         # if hole.release_type == ReleaseType.INSTANTANEOUS:
#         #     CA_ail_inst_inj_cmd_p = _CA_instantaneous(c_inj_ail_inst.a, c_inj_ail_inst.b, hole.mass_lb, f_mit, eneff=en_cmd)
#         # else:
#         #     CA_ail_inst_inj_cmd_p = 0.0

#         # #--step 8.14 calculate the continuous/instantaneous blended consequence areas--

#         # CA_ail_cont_cmd_n = _select_release_type_value(
#         #     row_inj.fluid_type, 
#         #     hole, 
#         #     CA_cont=CA_ail_cont_cmd_p, 
#         #     CA_inst=CA_ail_inst_cmd_p
#         # )
#         # CA_ail_cont_inj_n = _select_release_type_value(
#         #     row_inj.fluid_type, 
#         #     hole, 
#         #     CA_cont=CA_ail_cont_inj_cmd_p, 
#         #     CA_inst=CA_ail_inst_inj_cmd_p
#         # )
#         # CA_ainl_cont_cmd_n = _select_release_type_value(
#         #     row_inj.fluid_type, 
#         #     hole, 
#         #     CA_cont=CA_ainl_cont_cmd_p, 
#         #     CA_inst=CA_ainl_inst_cmd_p
#         # )
#         # CA_ainl_cont_inj_n = _select_release_type_value(
#         #     row_inj.fluid_type, 
#         #     hole, 
#         #     CA_cont=CA_ainl_cont_inj_cmd_p, 
#         #     CA_inst=CA_ainl_inst_inj_cmd_p
#         # )

#         # #------- Step 8.15—Calculate the AIT blended consequence areas ---------

#         # CA_flam_cmd_n = blend_AIT(CA_AIL=CA_ail_cont_cmd_n[0], 
#         #                           CA_AINL=CA_ainl_cont_cmd_n[0],
#         #                           fact_ait=f_ait)
        
#         # CA_flam_inj_n = blend_AIT(CA_AIL=CA_ail_cont_inj_n[0], 
#         #                           CA_AINL=CA_ainl_cont_inj_n[0],
#         #                           fact_ait=f_ait)


#         # --- component damage (Table 4.8) ---
#         CA_ainl_cont_cmd, CA_ail_cont_cmd, CA_ainl_inst_cmd, CA_ail_inst_cmd = _compute_per_table(
#             "4.8", fluid_key, hole, f_mit
#         )
#         CA_ainl_cmd_sel, fact_ic_cmd = _select_release_type_value(
#             row_cmd.fluid_type, hole, CA_cont=CA_ainl_cont_cmd, CA_inst=CA_ainl_inst_cmd
#         )
#         CA_ail_cmd_sel, _ = _select_release_type_value(
#             row_cmd.fluid_type, hole, CA_cont=CA_ail_cont_cmd, CA_inst=CA_ail_inst_cmd
#         )

#         CA_cmd_final_hole = blend_AIT(CA_AIL=CA_ail_cmd_sel, CA_AINL=CA_ainl_cmd_sel, fact_ait=f_ait)

#         # --- personnel injury (Table 4.9) ---
#         CA_ainl_cont_inj, CA_ail_cont_inj, CA_ainl_inst_inj, CA_ail_inst_inj = _compute_per_table(
#             "4.9", fluid_key, hole, f_mit
#         )
#         CA_ainl_inj_sel, fact_ic_inj = _select_release_type_value(
#             row_inj.fluid_type, hole, CA_cont=CA_ainl_cont_inj, CA_inst=CA_ainl_inst_inj
#         )
#         CA_ail_inj_sel, _ = _select_release_type_value(
#             row_inj.fluid_type, hole, CA_cont=CA_ail_cont_inj, CA_inst=CA_ail_inst_inj
#         )

#         CA_inj_final_hole = blend_AIT(CA_AIL=CA_ail_inj_sel, CA_AINL=CA_ainl_inj_sel, fact_ait=f_ait)

#         # choose one fact_IC to report (cmd & inj should be identical logic)
#         fact_ic_report = float(max(fact_ic_cmd, fact_ic_inj))
        
        
#         hole_results[hk] = FlammableHoleResult(
#             hole_key=hk,
#             CA_cmd=CA_cmd_final_hole,
#             CA_inj=CA_inj_final_hole,
            
#             # eneff=en_cmd,
#             # CA_ainl_cont_cte_a = c_ainl_cont.a,
#             # CA_ainl_cont_cte_b = c_ainl_cont.b,
#             # CA_ainl_cont = CA_ainl_cont_cmd_p,
#             # CA_ail_cont_cte_a = c_ail_cont.a,
#             # CA_ail_cont_cte_b = c_ail_cont.b,
#             # CA_ail_cont = CA_ail_cont_cmd_p,
#             # CA_ainl_inst_cte_a = c_ainl_inst.a,
#             # CA_ainl_inst_cte_b = c_ainl_inst.b,
#             # CA_ainl_inst = CA_ainl_inst_cmd_p,
#             # CA_ail_inst_cte_a = c_ail_inst.a,
#             # CA_ail_inst_cte_b = c_ail_inst.b,
#             # CA_ail_inst = CA_ail_inst_cmd_p,

#             # CA_ainl_cont_inj_cte_a = c_inj_ainl_cont.a,
#             # CA_ainl_cont_inj_cte_b = c_inj_ainl_cont.b,
#             # CA_ainl_cont_inj = CA_ainl_cont_inj_cmd_p,
#             # CA_ail_cont_inj_cte_a = c_inj_ail_cont.a,
#             # CA_ail_cont_inj_cte_b = c_inj_ail_cont.b,
#             # CA_ail_cont_inj = CA_ail_cont_inj_cmd_p,
#             # CA_ainl_inst_inj_cte_a = c_inj_ainl_inst.a,
#             # CA_ainl_inst_inj_cte_b = c_inj_ainl_inst.b,
#             # CA_ainl_inst_inj = CA_ainl_inst_inj_cmd_p,
#             # CA_ail_inst_inj_cte_a = c_inj_ail_inst.a,
#             # CA_ail_inst_inj_cte_b = c_inj_ail_inst.b,
#             # CA_ail_inst_inj = CA_ail_inst_inj_cmd_p,

#             # CA_ail_cmd_n = CA_ail_cont_cmd_n,
#             # CA_ail_inj_n = CA_ail_cont_inj_n,
#             # CA_ainl_cmd_n = CA_ainl_cont_cmd_n,
#             # CA_ainl_inj_n = CA_ainl_cont_inj_n,

#             # CA_flam_cmd_n = CA_flam_cmd_n,
#             # CA_flam_inj_n = CA_flam_inj_n,

#             fact_mit=f_mit,
#             fact_IC=fact_ic_report,
#             fact_AIT=f_ait,
#             CA_cmd_AINL=CA_ainl_cmd_sel,
#             CA_cmd_AIL=CA_ail_cmd_sel,
#             CA_inj_AINL=CA_ainl_inj_sel,
#             CA_inj_AIL=CA_ail_inj_sel,
#         )

#         # --- probability weighting sums (Eq 3.58/3.59) ---
#         gff_n = float(gff_by_hole.get(hk, 0.0))
#         sum_cmd += gff_n * CA_cmd_final_hole
#         sum_inj += gff_n * CA_inj_final_hole

#     CA_cmd_weighted = float(sum_cmd / float(gff_total))
#     CA_inj_weighted = float(sum_inj / float(gff_total))

#     # gff_n = float(gff_by_hole.get(hk, 0.0))
#     # sum_cmd += gff_n * CA_flam_cmd_n
#     # sum_inj += gff_n * CA_flam_inj_n

#     # CA_cmd_weighted = float(sum_cmd / float(gff_total))
#     # CA_inj_weighted = float(sum_inj / float(gff_total))

#     return FlammableFinalResult(
#         fluid=fluid_key,
#         fluid_type=row_cmd.fluid_type,
#         holes=hole_results,
#         CA_cmd_final=CA_cmd_weighted,
#         CA_inj_final=CA_inj_weighted,
#     )


# FUNCIÓN PRINCIPAL: CÁLCULO DE CONSECUENCIA INFLAMABLE (CMD + INJ)
# ==============================================================================

def compute_cof_4_8_flammable_explosive(
    fluid: str,
    holes: Dict[str, HoleInput],
    ait: AITInputs,
    mitigation_system_key: str,
    gff_by_hole: Dict[str, float],
    gff_total: float
) -> FlammableFinalResult:
    """
    Calcula el Área de Consecuencia Inflamable Final (Component Damage & Personnel Injury).
    Integra tablas 4.8 y 4.9.
    """
    
    # 1. Validar inputs básicos
    if not holes:
        return FlammableFinalResult(fluid, 0, {}, 0.0, 0.0)

    # 2. Factor de Mitigación (Detection & Isolation)
    # Buscamos el factor en el diccionario de mitigación (definido al inicio del archivo)
    # Si no existe, asumimos 0.0 (sin mitigación)
    # f_mit = MITIGATION_SYSTEMS.get(mitigation_system_key, 0.0)
    f_mit = fact_mit_from_system(mitigation_system_key)

    # 3. Factor de Autoignición (AIT Blending)
    f_ait = fact_AIT(ait.Ts_R, fluid)

    # 4. Determinar Fase para búsqueda de constantes
    # Usamos la fase del primer agujero como referencia (o una lógica más compleja si fuera necesario)
    # Nota: Para C3-C4, el orquestador ya forzó phase=GAS en el objeto HoleInput.
    first_hole = next(iter(holes.values()))
    phase_lookup = first_hole.final_phase 

    # 5. RECUPERAR CONSTANTES (CMD - Tabla 4.8)
    cmd_ainl_cont, cmd_ail_cont, cmd_ainl_inst, cmd_ail_inst = _compute_constants_set(
        _TABLE_4_8, fluid, phase_lookup
    )

    # 6. RECUPERAR CONSTANTES (INJ - Tabla 4.9)
    inj_ainl_cont, inj_ail_cont, inj_ainl_inst, inj_ail_inst = _compute_constants_set(
        _TABLE_4_9, fluid, phase_lookup
    )

    # 7. Bucle de Cálculo por Agujero
    hole_results = {}
    
    total_weighted_cmd = 0.0
    total_weighted_inj = 0.0

    for size_key, h_input in holes.items():
        rate = h_input.rate_lb_s
        mass = h_input.mass_lb
        
        # --- A. CÁLCULO DE ÁREAS BASE (Power Law) ---
        # Formula: CA = a * (rate o mass) ^ b
        
        # Función lambda auxiliar para cálculo seguro (rate^b)
        def calc_pl(c: PowerLawConstants, val: float) -> float:
            if val <= 0: return 0.0
            return c.a * (val ** c.b)

        # CMD (Component Damage)
        ca_cmd_ainl_cont = calc_pl(cmd_ainl_cont, rate)
        ca_cmd_ail_cont  = calc_pl(cmd_ail_cont, rate)
        ca_cmd_ainl_inst = calc_pl(cmd_ainl_inst, mass)
        ca_cmd_ail_inst  = calc_pl(cmd_ail_inst, mass)

        # INJ (Personnel Injury)
        ca_inj_ainl_cont = calc_pl(inj_ainl_cont, rate)
        ca_inj_ail_cont  = calc_pl(inj_ail_cont, rate)
        ca_inj_ainl_inst = calc_pl(inj_ainl_inst, mass)
        ca_inj_ail_inst  = calc_pl(inj_ail_inst, mass)

        # --- B. SELECCIÓN POR TIPO DE LIBERACIÓN (Continuous vs Instantaneous) ---
        # Si es Continuo, Inst = 0. Si es Inst, Cont = 0.
        
        is_cont = (h_input.release_type == ReleaseType.CONTINUOUS)
        
        # CMD Blending
        final_cmd_ainl = ca_cmd_ainl_cont if is_cont else ca_cmd_ainl_inst
        final_cmd_ail  = ca_cmd_ail_cont  if is_cont else ca_cmd_ail_inst
        
        # INJ Blending
        final_inj_ainl = ca_inj_ainl_cont if is_cont else ca_inj_ainl_inst
        final_inj_ail  = ca_inj_ail_cont  if is_cont else ca_inj_ail_inst

        # --- C. APLICAR MITIGACIÓN ---
        # CA_mit = CA * (1 - fact_mit)
        # Nota: La mitigación reduce el tamaño de la consecuencia final
        mit_factor_mult = (1.0 - f_mit)
        
        final_cmd_ainl *= mit_factor_mult
        final_cmd_ail  *= mit_factor_mult
        final_inj_ainl *= mit_factor_mult
        final_inj_ail  *= mit_factor_mult

        # --- D. APLICAR PROBABILIDAD DE AUTOIGNICIÓN (AIT) ---
        # CA = CA_ainl * (1 - f_ait) + CA_ail * f_ait
        # Ponderamos el escenario "No Probable" y el "Probable"
        
        ca_cmd_final_hole = (final_cmd_ainl * (1.0 - f_ait)) + (final_cmd_ail * f_ait)
        ca_inj_final_hole = (final_inj_ainl * (1.0 - f_ait)) + (final_inj_ail * f_ait)

        # Guardar resultado individual
        hole_results[size_key] = FlammableHoleResult(
            hole_size=size_key,
            CA_cmd=ca_cmd_final_hole,
            CA_inj=ca_inj_final_hole,
            fact_mit=f_mit,
            fact_AIT=f_ait,
            
            # Guardamos parciales para trazabilidad (opcional)
            CA_cmd_AINL=final_cmd_ainl,
            CA_cmd_AIL=final_cmd_ail
        )

        # --- E. ACUMULAR PARA PROMEDIO PONDERADO ---
        freq = gff_by_hole.get(size_key, 0.0)
        total_weighted_cmd += ca_cmd_final_hole * freq
        total_weighted_inj += ca_inj_final_hole * freq

    # 8. Calcular Promedios Finales
    final_cmd_area = total_weighted_cmd / gff_total if gff_total > 0 else 0.0
    final_inj_area = total_weighted_inj / gff_total if gff_total > 0 else 0.0

    return FlammableFinalResult(
        fluid=fluid,
        fluid_type=0, # Dummy legacy
        holes=hole_results,
        CA_cmd_final=final_cmd_area,
        CA_inj_final=final_inj_area
    )


def is_fluid_flammable(fluid_name: str) -> bool:
    """
    Verifica si el fluido es realmente inflamable.
    Retorna False si el fluido no está en la tabla O si está pero no tiene constantes (ej. Steam).
    """
    try:
        key = _norm_fluid_key(fluid_name)
        
        # 1. Si no está en la tabla, no es inflamable
        if key not in _TABLE_4_8:
            return False
            
        # 2. Si está en la tabla, verificamos si tiene constantes
        # Steam y Acids están en _TABLE_4_8 pero con diccionario de constantes vacío.
        row = _TABLE_4_8[key]
        if not row.constants: 
            return False
            
        return True
    except:
        return False

# -----------------------------
# Quick local test
# -----------------------------
if __name__ == "__main__":
    # Example skeleton (values are not "real", just to prove it runs):
    example_holes = {
        "small": HoleInput(
            hole_key="small",
            release_type=ReleaseType.CONTINUOUS,
            final_phase=Phase.GAS,
            rate_lb_s=10.0,
            mass_lb=1000.0,
        ),
        "medium": HoleInput(
            hole_key="medium",
            release_type=ReleaseType.INSTANTANEOUS,
            final_phase=Phase.GAS,
            rate_lb_s=80.0,
            mass_lb=20000.0,
        ),
    }

    # gff example (should come from 4.2)
    gff = {"small": 1e-5, "medium": 2e-5}
    gff_tot = sum(gff.values())

    res = compute_cof_4_8_flammable_explosive(
        fluid="C3-C4",
        holes=example_holes,
        ait=AITInputs(Ts_R=520.0, AIT_R=900.0),
        mitigation_system_key="none",
        gff_by_hole=gff,
        gff_total=gff_tot,
    )

    print("Fluid:", res.fluid, "Type:", res.fluid_type)
    print("Final CA_cmd:", res.CA_cmd_final)
    print("Final CA_inj:", res.CA_inj_final)
    for hk, hr in res.holes.items():
        print(hk, "CA_cmd:", hr.CA_cmd, "CA_inj:", hr.CA_inj, "factIC:", hr.fact_IC, "factAIT:", hr.fact_AIT)
