# app/calculations/cof_4_12_financial_consequence.py
"""
API 581 COF Level 1
Section 4.12: Determine the Financial Consequence

Implements:
- Eq. (3.82): Total financial consequence
- Eq. (3.83): Component damage cost
- Eq. (3.84): Damage cost to surrounding equipment
- Eq. (3.85): Outage_cmd (component damage outage)
- Eq. (3.86): Outage_affa (affected area outage)
- Eq. (3.87): Business interruption cost
- Eq. (3.88): Potential injury costs
- Eq. (3.89): frac_evap estimate
- Eq. (3.90): Spill volume for environmental cleanup
- Eq. (3.91): Environmental cleanup cost
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import log10
from typing import Dict, Mapping, Optional, Tuple


# -------------------------
# Constants / helpers
# -------------------------

FT3_PER_BBL = 5.614583333333333  # 1 bbl = 5.61458 ft^3
C13_BBL_PER_FT3 = 1.0 / FT3_PER_BBL  # Eq (3.90) constant

# Eq (3.89): frac_evap polynomial uses (C12*NBP + C41)
# C12_DEFAULT = 1.0 # C12=1.0 for metric/customary generic usage per text context


class HoleSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    RUPTURE = "rupture"


# -------------------------
# Tables
# -------------------------

# Table 4.15 — Example Component Damage Costs (holecost, 2001 USD)
TABLE_4_15_HOLECOST: Dict[str, Dict[HoleSize, Optional[float]]] = {
    # Compressor
    "COMPC": {HoleSize.SMALL: 10_000.0, HoleSize.MEDIUM: 20_000.0, HoleSize.LARGE: 100_000.0, HoleSize.RUPTURE: 300_000.0},
    "COMPR": {HoleSize.SMALL: 5_000.0, HoleSize.MEDIUM: 10_000.0, HoleSize.LARGE: 50_000.0, HoleSize.RUPTURE: 100_000.0},

    # Heat exchanger
    "HEXSS": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 60_000.0},
    "HEXTS": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 60_000.0},
    "HEXTUBE": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 60_000.0},

    # Pipe
    "PIPE-1": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: 20.0},
    "PIPE-2": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: 40.0},
    "PIPE-4": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 10.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: 60.0},
    "PIPE-6": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 20.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: 120.0},
    "PIPE-8": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 30.0, HoleSize.LARGE: 60.0, HoleSize.RUPTURE: 180.0},
    "PIPE-10": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 40.0, HoleSize.LARGE: 80.0, HoleSize.RUPTURE: 240.0},
    "PIPE-12": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 60.0, HoleSize.LARGE: 120.0, HoleSize.RUPTURE: 360.0},
    "PIPE-16": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: 80.0, HoleSize.LARGE: 160.0, HoleSize.RUPTURE: 500.0},
    "PIPEGT16": {HoleSize.SMALL: 10.0, HoleSize.MEDIUM: 120.0, HoleSize.LARGE: 240.0, HoleSize.RUPTURE: 700.0},

    # Pump
    "PUMP2S": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_500.0, HoleSize.LARGE: 5_000.0, HoleSize.RUPTURE: 5_000.0},
    "PUMP1S": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_500.0, HoleSize.LARGE: 5_000.0, HoleSize.RUPTURE: 5_000.0},
    "PUMPR":  {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_500.0, HoleSize.LARGE: 5_000.0, HoleSize.RUPTURE: 10_000.0},

    # Tank
    "TANKBOTTOM": {HoleSize.SMALL: 5_000.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: 120_000.0},
    "TANKBOTEDGE": {HoleSize.SMALL: 5_000.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: 120_000.0},
    "COURSES-10": {HoleSize.SMALL: 5_000.0, HoleSize.MEDIUM: 12_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 40_000.0},

    # FINFAN (Fixed Key: FINFAN_TUBE)
    "FINFAN_TUBE": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 60_000.0},
    "FINFAN HEADER": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 60_000.0},

    # Vessel / FinFan
    "KODRUM": {HoleSize.SMALL: 5_000.0, HoleSize.MEDIUM: 12_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 40_000.0},
    "DRUM":   {HoleSize.SMALL: 5_000.0, HoleSize.MEDIUM: 12_000.0, HoleSize.LARGE: 20_000.0, HoleSize.RUPTURE: 40_000.0},
    "FILTER": {HoleSize.SMALL: 1_000.0, HoleSize.MEDIUM: 2_000.0, HoleSize.LARGE: 4_000.0, HoleSize.RUPTURE: 10_000.0},
    "REACTOR":{HoleSize.SMALL: 10_000.0, HoleSize.MEDIUM: 24_000.0, HoleSize.LARGE: 40_000.0, HoleSize.RUPTURE: 80_000.0},
    "COLTOP": {HoleSize.SMALL: 10_000.0, HoleSize.MEDIUM: 25_000.0, HoleSize.LARGE: 50_000.0, HoleSize.RUPTURE: 100_000.0},
    "COLMID": {HoleSize.SMALL: 10_000.0, HoleSize.MEDIUM: 25_000.0, HoleSize.LARGE: 50_000.0, HoleSize.RUPTURE: 100_000.0},
    "COLBTM": {HoleSize.SMALL: 10_000.0, HoleSize.MEDIUM: 25_000.0, HoleSize.LARGE: 50_000.0, HoleSize.RUPTURE: 100_000.0},
}


# Table 4.16 — Material Cost Factors (matcost)
TABLE_4_16_MATCOST: Dict[str, float] = {
    "CARBON STEEL": 1.0,
    "ORGANIC COATINGS (< 80 MIL)": 1.2,
    "1.25CR-0.5MO": 1.3,
    "2.25CR-1MO": 1.7,
    "5CR-0.5MO": 1.7,
    "7CR-0.5MO": 2.0,
    "CLAD 304 SS": 2.1,
    "FIBERGLASS": 2.5,
    "PP LINED": 2.5,
    "9CR-1MO": 2.6,
    "405 SS": 2.8,
    "410 SS": 2.8,
    "304 SS": 3.2,
    "CLAD 316 SS": 3.3,
    "STRIP LINED ALLOY": 3.3,
    "ORGANIC COATING (> 80 MIL)": 3.4,
    "CS *SAN* LINED": 3.4,
    "CS RUBBER LINED": 4.4,
    "316 SS": 4.8,
    "CS GLASS LINED": 5.8,
    "CLAD ALLOY 400": 6.4,
    "90/10 CU/NI": 6.8,
    "CLAD ALLOY 600": 7.0,
    "CS PTFE LINED": 7.8,
    "CLAD NICKEL": 8.0,
    "ALLOY 800": 8.4,
    "70/30 CU/NI": 8.5,
    "904L": 8.8,
    "ALLOY 20": 11.0,
    "ALLOY 400": 15.0,
    "ALLOY 600": 15.0,
    "NICKEL": 18.0,
    "ACID BRICK": 20.0,
    "REFRACTORY": 20.0,
    "ALLOY 625": 26.0,
    "TITANIUM": 28.0,
    'ALLOY "C"': 29.0,
    'ALLOY "B"': 36.0,
    "ZIRCONIUM": 34.0,
    "TANTALUM": 535.0,
}

# Table 4.17 — Estimated Equipment Outage (days)
TABLE_4_17_OUTAGE_DAYS: Dict[str, Dict[HoleSize, Optional[float]]] = {
    # Compressor
    "COMPC": {HoleSize.SMALL: None, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 7.0, HoleSize.RUPTURE: None},
    "COMPR": {HoleSize.SMALL: None, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 7.0, HoleSize.RUPTURE: None},

    # Heat exchanger
    "HEXSS": {HoleSize.SMALL: 2.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 3.0, HoleSize.RUPTURE: 10.0},
    "HEXTS": {HoleSize.SMALL: 2.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 3.0, HoleSize.RUPTURE: 10.0},
    "HEXTUBE": {HoleSize.SMALL: None, HoleSize.MEDIUM: None, HoleSize.LARGE: None, HoleSize.RUPTURE: None},

    # Pipe
    "PIPE-1": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: None, HoleSize.LARGE: None, HoleSize.RUPTURE: 1.0},
    "PIPE-2": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: None, HoleSize.LARGE: None, HoleSize.RUPTURE: 1.0},
    "PIPE-4": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 1.0, HoleSize.LARGE: None, HoleSize.RUPTURE: 2.0},
    "PIPE-6": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 1.0, HoleSize.LARGE: 2.0, HoleSize.RUPTURE: 3.0},
    "PIPE-8": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 2.0, HoleSize.LARGE: 2.0, HoleSize.RUPTURE: 3.0},
    "PIPE-10": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 2.0, HoleSize.LARGE: 2.0, HoleSize.RUPTURE: 4.0},
    "PIPE-12": {HoleSize.SMALL: 1.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 4.0, HoleSize.RUPTURE: 4.0},
    "PIPE-16": {HoleSize.SMALL: 1.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 4.0, HoleSize.RUPTURE: 5.0},
    "PIPEGT16": {HoleSize.SMALL: 1.0, HoleSize.MEDIUM: 4.0, HoleSize.LARGE: 5.0, HoleSize.RUPTURE: 7.0},

    # Pump
    "PUMP2S": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: None},
    "PUMP1S": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: None},
    "PUMPR":  {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 0.0, HoleSize.RUPTURE: None},

    # Tank
    "TANKBOTTOM": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: None, HoleSize.LARGE: None, HoleSize.RUPTURE: 50.0},
    "TANKBOTEDGE": {HoleSize.SMALL: 5.0, HoleSize.MEDIUM: None, HoleSize.LARGE: None, HoleSize.RUPTURE: 50.0},
    "COURSES-10": {HoleSize.SMALL: 2.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 3.0, HoleSize.RUPTURE: 14.0},

    # FINFAN (Fixed Key: FINFAN_TUBE)
    "FINFAN_TUBE": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: None, HoleSize.LARGE: None, HoleSize.RUPTURE: 1.0},
    "FINFAN HEADER": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 0.0, HoleSize.LARGE: 2.0, HoleSize.RUPTURE: 3.0},

    # Vessel / FinFan
    "KODRUM": {HoleSize.SMALL: 2.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 3.0, HoleSize.RUPTURE: 10.0},
    "FILTER": {HoleSize.SMALL: 0.0, HoleSize.MEDIUM: 1.0, HoleSize.LARGE: 2.0, HoleSize.RUPTURE: 3.0},
    "DRUM":   {HoleSize.SMALL: 2.0, HoleSize.MEDIUM: 3.0, HoleSize.LARGE: 3.0, HoleSize.RUPTURE: 10.0},
    "REACTOR":{HoleSize.SMALL: 4.0, HoleSize.MEDIUM: 6.0, HoleSize.LARGE: 6.0, HoleSize.RUPTURE: 21.0},
    "COLTOP": {HoleSize.SMALL: 3.0, HoleSize.MEDIUM: 4.0, HoleSize.LARGE: 5.0, HoleSize.RUPTURE: 21.0},
    "COLMID": {HoleSize.SMALL: 3.0, HoleSize.MEDIUM: 4.0, HoleSize.LARGE: 5.0, HoleSize.RUPTURE: 21.0},
    "COLBTM": {HoleSize.SMALL: 3.0, HoleSize.MEDIUM: 4.0, HoleSize.LARGE: 5.0, HoleSize.RUPTURE: 21.0},
}

# Table 4.18 — Fluid Leak Properties
TABLE_4_18_FLUID_PROPS: Dict[str, Dict[str, float]] = {
    "C1-C2": {"mw": 23.0, "rho": 15.639, "nbp_f": -193.0, "frac_evap_24h": 1.00},
    "C3-C4": {"mw": 58.0, "rho": 36.209, "nbp_f": 31.0, "frac_evap_24h": 1.00},
    "C5": {"mw": 100.0, "rho": 42.702, "nbp_f": 210.0, "frac_evap_24h": 0.90},
    "C6-C8": {"mw": 100.0, "rho": 42.702, "nbp_f": 210.0, "frac_evap_24h": 0.90},
    "C9-C12": {"mw": 149.0, "rho": 45.823, "nbp_f": 364.0, "frac_evap_24h": 0.50},
    "C13-C16": {"mw": 205.0, "rho": 47.728, "nbp_f": 502.0, "frac_evap_24h": 0.10},
    "C17-C25": {"mw": 280.0, "rho": 48.383, "nbp_f": 651.0, "frac_evap_24h": 0.05},
    "C25+": {"mw": 422.0, "rho": 56.187, "nbp_f": 981.0, "frac_evap_24h": 0.02},
    "ACID": {"mw": 18.0, "rho": 62.3, "nbp_f": 212.0, "frac_evap_24h": 0.90},
    "H2": {"mw": 2.0, "rho": 4.433, "nbp_f": -423.0, "frac_evap_24h": 1.00},
    "H2S": {"mw": 34.0, "rho": 61.993, "nbp_f": -75.0, "frac_evap_24h": 1.00},
    "HF": {"mw": 20.0, "rho": 60.37, "nbp_f": 68.0, "frac_evap_24h": 1.00},
    "CO": {"mw": 28.0, "rho": 50.0, "nbp_f": -312.0, "frac_evap_24h": 1.00},
    "DEE": {"mw": 74.0, "rho": 45.0, "nbp_f": 95.0, "frac_evap_24h": 1.00},
    "HCL": {"mw": 36.0, "rho": 74.0, "nbp_f": -121.0, "frac_evap_24h": 1.00},
    "NITRIC ACID": {"mw": 63.0, "rho": 95.0, "nbp_f": 250.0, "frac_evap_24h": 0.80},
    "NO2": {"mw": 90.0, "rho": 58.0, "nbp_f": 275.0, "frac_evap_24h": 0.75},
    "PHOSGENE": {"mw": 99.0, "rho": 86.0, "nbp_f": 181.0, "frac_evap_24h": 1.00},
    "TDI": {"mw": 174.0, "rho": 76.0, "nbp_f": 484.0, "frac_evap_24h": 0.15},
    "METHANOL": {"mw": 32.0, "rho": 50.0, "nbp_f": 149.0, "frac_evap_24h": 1.00},
    "PO": {"mw": 58.0, "rho": 52.0, "nbp_f": 93.0, "frac_evap_24h": 1.00},
    "STYRENE": {"mw": 104.0, "rho": 42.7, "nbp_f": 293.0, "frac_evap_24h": 0.60},
    "EEA": {"mw": 132.0, "rho": 61.0, "nbp_f": 313.0, "frac_evap_24h": 0.65},
    "EE": {"mw": 90.0, "rho": 58.0, "nbp_f": 275.0, "frac_evap_24h": 0.75},
    "EG": {"mw": 62.0, "rho": 69.0, "nbp_f": 387.0, "frac_evap_24h": 0.45},
    "EO": {"mw": 44.0, "rho": 55.0, "nbp_f": 51.0, "frac_evap_24h": 1.00},
}


# -------------------------
# Inputs / outputs
# -------------------------

@dataclass(frozen=True)
class FinancialInputs:
    """
    Required inputs for Section 4.12.
    """
    component_type: str  # keys like PIPE-8, DRUM, FINFAN_TUBE, etc.

    # From 4.2 (generic failure frequencies by hole size)
    gff_by_hole: Mapping[HoleSize, float]
    gff_total: float

    # From 4.11 (areas)
    CA_f_cmd: float  # ft^2 component damage consequence area (flammable dominates)
    CA_f_inj: float  # ft^2 personnel injury consequence area (max of flamm/tox/nonflamm)

    # Cost inputs (user / site specific)
    costfactor: float        # multiplies holecost_n (Eq 3.83)
    material: str            # to pick matcost from Table 4.16 (or override)
    equipcost: float         # $/ft^2 (unit equipment replacement cost factor)
    prodcost: float          # $/day (production loss cost per day)
    popdens: float           # persons/ft^2
    injcost: float           # $/person
    envcost: float           # $/bbl cleanup

    # Outage multiplier
    outage_mult: float = 1.0

    # Environmental spill fluid properties
    # You can either pass a fluid_key from Table 4.18 OR pass rho_l + nbp_f + frac_evap_24h directly.
    fluid_key: Optional[str] = None
    rho_l_lbft3: Optional[float] = None
    nbp_f: Optional[float] = None
    frac_evap_24h: Optional[float] = None

    # From 4.7: release masses per hole size (lbm) used for spill volume
    # (Use the same n=1..4 mapping you already have)
    mass_by_hole_lbm: Optional[Mapping[HoleSize, float]] = None


@dataclass(frozen=True)
class FinancialResult:
    FC_f_cmd: float
    FC_f_affa: float
    FC_f_prod: float
    FC_f_inj: float
    FC_f_environ: float
    FC_f_total: float

    # optional extra visibility
    outage_cmd_days: float
    outage_affa_days: float
    vol_env_by_hole_bbl: Dict[HoleSize, float]


# -------------------------
# Core math functions
# -------------------------

def _norm_key(s: str) -> str:
    return " ".join(s.strip().upper().split())


def get_matcost(material: str, *, default: Optional[float] = None) -> float:
    key = _norm_key(material)
    if key in TABLE_4_16_MATCOST:
        return float(TABLE_4_16_MATCOST[key])
    if default is not None:
        return float(default)
    raise KeyError(f"Unknown material='{material}'. Provide a valid Table 4.16 key or pass default.")


def get_holecost(component_type: str) -> Dict[HoleSize, Optional[float]]:
    key = _norm_key(component_type)
    try:
        return TABLE_4_15_HOLECOST[key]
    except KeyError as exc:
        raise KeyError(f"Unknown component_type='{component_type}' for Table 4.15 holecost.") from exc


def get_outage_days(component_type: str) -> Dict[HoleSize, Optional[float]]:
    key = _norm_key(component_type)
    try:
        return TABLE_4_17_OUTAGE_DAYS[key]
    except KeyError as exc:
        raise KeyError(f"Unknown component_type='{component_type}' for Table 4.17 outage days.") from exc


def get_fluid_props_from_table(fluid_key: str) -> Tuple[float, float, float]:
    """
    Returns (rho_l_lbft3, nbp_f, frac_evap_24h) from Table 4.18.
    """
    key = _norm_key(fluid_key)
    try:
        row = TABLE_4_18_FLUID_PROPS[key]
        return float(row["rho"]), float(row["nbp_f"]), float(row["frac_evap_24h"])
    except KeyError as exc:
        raise KeyError(f"Unknown fluid_key='{fluid_key}' for Table 4.18.") from exc


def frac_evap_from_nbp(nbp_f: float) -> float:
    """
    Eq. (3.89) - Alternative estimation of fraction evaporated in 24 hours.

    frac_evap = [
        -7.1408 + 8.5827e-3 * X
        -3.5594e-6 * X^2
        +2331.1 / X
        -203545 / X^2
    ]
    where X = (C12*NBP + C41)
    """
    x = 1 * nbp_f + 0
    # guard against division by zero / negative tiny values
    if abs(x) < 1e-9:
        return 0.0

    val = (
        -7.1408
        + 8.5827e-3 * x
        - 3.5594e-6 * (x ** 2)
        + 2331.1 / x
        - 203545.0 / (x ** 2)
    )
    # clamp physically to [0,1]
    return max(0.0, min(1.0, float(val)))


def _weighted_avg(values: Mapping[HoleSize, Optional[float]], gff: Mapping[HoleSize, float], gff_total: float) -> float:
    """
    Probability-weighted average:
      sum(gff_n * value_n) / gff_total

    If a value is None (N/A), it is skipped (effectively treated as 0 contribution).
    """
    if gff_total <= 0:
        raise ValueError("gff_total must be > 0.")
    s = 0.0
    for hs, v in values.items():
        if v is None:
            continue
        s += float(gff.get(hs, 0.0)) * float(v)
    return s / float(gff_total)


# -------------------------
# Section 4.12 calculations
# -------------------------

def calc_FC_f_cmd(
    component_type: str,
    gff_by_hole: Mapping[HoleSize, float],
    gff_total: float,
    *,
    costfactor: float,
    matcost: float,
) -> float:
    """Eq. (3.83): FC_f_cmd."""
    holecost = get_holecost(component_type)
    weighted_holecost = _weighted_avg(holecost, gff_by_hole, gff_total)
    return float(weighted_holecost) * float(matcost) * float(costfactor)


def calc_FC_f_affa(CA_f_cmd: float, equipcost: float) -> float:
    """Eq. (3.84): FC_f_affa."""
    if CA_f_cmd < 0:
        raise ValueError("CA_f_cmd must be >= 0.")
    if equipcost < 0:
        raise ValueError("equipcost must be >= 0.")
    return float(CA_f_cmd) * float(equipcost)


def calc_outage_cmd_days(
    component_type: str,
    gff_by_hole: Mapping[HoleSize, float],
    gff_total: float,
    *,
    outage_mult: float,
) -> float:
    """Eq. (3.85): Outage_cmd."""
    outage = get_outage_days(component_type)
    weighted_outage = _weighted_avg(outage, gff_by_hole, gff_total)
    return float(weighted_outage) * float(outage_mult)


def calc_outage_affa_days(FC_f_affa: float) -> float:
    """
    Eq. (3.86): Outage_affa = 10^( 1.242 + 0.585 * log10( FC_f_affa * 10^-6 ) )
    """
    if FC_f_affa <= 0:
        return 0.0
    x = FC_f_affa * (10.0 ** -6)
    if x <= 0:
        return 0.0
    return 10.0 ** (1.242 + 0.585 * log10(x))


def calc_FC_f_prod(outage_cmd_days: float, outage_affa_days: float, prodcost: float) -> float:
    """Eq. (3.87): FC_f_prod."""
    if prodcost < 0:
        raise ValueError("prodcost must be >= 0.")
    return float(outage_cmd_days + outage_affa_days) * float(prodcost)


def calc_FC_f_inj(CA_f_inj: float, popdens: float, injcost: float) -> float:
    """Eq. (3.88): FC_inj."""
    if CA_f_inj < 0:
        raise ValueError("CA_f_inj must be >= 0.")
    if popdens < 0:
        raise ValueError("popdens must be >= 0.")
    if injcost < 0:
        raise ValueError("injcost must be >= 0.")
    return float(CA_f_inj) * float(popdens) * float(injcost)


def calc_vol_env_bbl_by_hole(
    mass_by_hole_lbm: Mapping[HoleSize, float],
    rho_l_lbft3: float,
    frac_evap_24h: float,
) -> Dict[HoleSize, float]:
    """Eq. (3.90): vol_env_n."""
    if rho_l_lbft3 <= 0:
        raise ValueError("rho_l_lbft3 must be > 0.")
    frac = max(0.0, min(1.0, float(frac_evap_24h)))
    out: Dict[HoleSize, float] = {}
    for hs, m in mass_by_hole_lbm.items():
        m_lbm = max(0.0, float(m))
        vol_bbl = C13_BBL_PER_FT3 * m_lbm * (1.0 - frac) / float(rho_l_lbft3)
        out[hs] = float(max(0.0, vol_bbl))
    return out


def calc_FC_f_environ(
    vol_env_by_hole_bbl: Mapping[HoleSize, float],
    gff_by_hole: Mapping[HoleSize, float],
    gff_total: float,
    envcost: float,
) -> float:
    """Eq. (3.91): FC_f_environ."""
    if envcost < 0:
        raise ValueError("envcost must be >= 0.")
    # weighted avg volume
    vol_map: Dict[HoleSize, Optional[float]] = {hs: float(v) for hs, v in vol_env_by_hole_bbl.items()}
    weighted_vol = _weighted_avg(vol_map, gff_by_hole, gff_total)
    return float(weighted_vol) * float(envcost)


def compute_cof_4_12_financial_consequence(inp: FinancialInputs) -> FinancialResult:
    """
    Master function: computes all cost terms and total financial consequence (Eq. 3.82).
    """
    comp = _norm_key(inp.component_type)

    # matcost
    matcost = get_matcost(inp.material)

    # FC_cmd (Eq 3.83)
    FC_cmd = calc_FC_f_cmd(
        comp,
        inp.gff_by_hole,
        inp.gff_total,
        costfactor=inp.costfactor,
        matcost=matcost,
    )

    # FC_affa (Eq 3.84)
    FC_affa = calc_FC_f_affa(inp.CA_f_cmd, inp.equipcost)

    # Outages (Eq 3.85 & 3.86)
    outage_cmd = calc_outage_cmd_days(
        comp, inp.gff_by_hole, inp.gff_total, outage_mult=inp.outage_mult
    )
    outage_affa = calc_outage_affa_days(FC_affa)

    # FC_prod (Eq 3.87)
    FC_prod = calc_FC_f_prod(outage_cmd, outage_affa, inp.prodcost)

    # FC_inj (Eq 3.88)
    FC_inj = calc_FC_f_inj(inp.CA_f_inj, inp.popdens, inp.injcost)

    # Environmental inputs
    if inp.fluid_key is not None:
        rho_l, nbp_f, frac_evap_24h = get_fluid_props_from_table(inp.fluid_key)
    else:
        if inp.rho_l_lbft3 is None or inp.nbp_f is None:
            raise ValueError("Provide fluid_key OR (rho_l_lbft3 and nbp_f).")
        rho_l = float(inp.rho_l_lbft3)
        nbp_f = float(inp.nbp_f)
        frac_evap_24h = float(inp.frac_evap_24h) if inp.frac_evap_24h is not None else frac_evap_from_nbp(nbp_f)

    # Volumes and FC_environ
    vol_env_by_hole: Dict[HoleSize, float] = {}
    FC_env = 0.0
    if inp.mass_by_hole_lbm is not None:
        vol_env_by_hole = calc_vol_env_bbl_by_hole(inp.mass_by_hole_lbm, rho_l, frac_evap_24h)
        FC_env = calc_FC_f_environ(vol_env_by_hole, inp.gff_by_hole, inp.gff_total, inp.envcost)
    else:
        vol_env_by_hole = {hs: 0.0 for hs in HoleSize}
        FC_env = 0.0

    # Total (Eq 3.82)
    FC_total = float(FC_cmd + FC_affa + FC_prod + FC_inj + FC_env)

    return FinancialResult(
        FC_f_cmd=float(FC_cmd),
        FC_f_affa=float(FC_affa),
        FC_f_prod=float(FC_prod),
        FC_f_inj=float(FC_inj),
        FC_f_environ=float(FC_env),
        FC_f_total=float(FC_total),
        outage_cmd_days=float(outage_cmd),
        outage_affa_days=float(outage_affa),
        vol_env_by_hole_bbl=dict(vol_env_by_hole),
    )


# -------------------------
# Quick local test
# -------------------------
if __name__ == "__main__":
    gff = {
        HoleSize.SMALL: 8e-06,
        HoleSize.MEDIUM: 2e-05,
        HoleSize.LARGE: 2e-06,
        HoleSize.RUPTURE: 6e-07,
    }
    gff_total = sum(gff.values())

    inp = FinancialInputs(
        component_type="PIPE-8",
        gff_by_hole=gff,
        gff_total=gff_total,
        CA_f_cmd=2_000.0,
        CA_f_inj=3_000.0,
        costfactor=1.0,
        material="Carbon steel",
        equipcost=150.0,     # $/ft^2
        prodcost=50_000.0,   # $/day
        popdens=0.0005,      # persons/ft^2
        injcost=1_000_000.0, # $/person
        envcost=5_000.0,     # $/bbl
        outage_mult=1.0,
        fluid_key="C6-C8",
        mass_by_hole_lbm={
            HoleSize.SMALL: 500.0,
            HoleSize.MEDIUM: 5_000.0,
            HoleSize.LARGE: 20_000.0,
            HoleSize.RUPTURE: 100_000.0,
        },
    )

    res = compute_cof_4_12_financial_consequence(inp)
    print(res)