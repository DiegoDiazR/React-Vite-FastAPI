# app/calculations/cof_4_5_release_type.py
"""
API 581 COF Level 1
Section 4.5: Determine the Release Type (Continuous or Instantaneous)

Rules (per 4.5.2):
1) Small hole (< 0.25 in) => Continuous
2) Medium/Large/Rupture:
   - if mass released in 3 minutes > 10,000 lbm => Instantaneous
   - OR if Wn > 55.6 lbm/s => Instantaneous
   - else => Continuous

We compute "mass released in 3 minutes" as:
    m_3min = min(mass_avail_n, Wn * 180)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Mapping, Any


SECONDS_IN_3_MIN = 180.0
SMALL_HOLE_THRESHOLD_IN = 0.25
INSTANT_MASS_THRESHOLD_LBM = 10_000.0
INSTANT_RATE_THRESHOLD_LBM_S = 55.6


class ReleaseType(str, Enum):
    CONTINUOUS = "continuous"
    INSTANTANEOUS = "instantaneous"

@dataclass(frozen=True)
class ReleaseTypeResult:
    """
    Resultado del Paso 4.5 para un tamaño de agujero específico.
    """
    release_type: ReleaseType
    release_time_sec: float
    mass_released_lb: float
    rate_released_lb_s: float

@dataclass(frozen=True)
class ReleaseTypePerHole:
    dn_in: float
    wn_lbm_s: float
    mass_avail_lbm: float
    mass_3min_lbm: float
    release_type: ReleaseType


def determine_release_type_for_hole(
    *,
    dn_in: float,
    wn_lbm_s: float,
    mass_avail_lbm: float,
) -> ReleaseTypePerHole:
    if dn_in <= 0:
        raise ValueError("dn_in must be > 0")
    if wn_lbm_s < 0:
        raise ValueError("wn_lbm_s must be >= 0")
    if mass_avail_lbm < 0:
        raise ValueError("mass_avail_lbm must be >= 0")

    # Rule 1: small hole < 0.25 in => continuous
    if dn_in < SMALL_HOLE_THRESHOLD_IN:
        m3 = min(float(mass_avail_lbm), float(wn_lbm_s) * SECONDS_IN_3_MIN)
        return ReleaseTypePerHole(
            dn_in=float(dn_in),
            wn_lbm_s=float(wn_lbm_s),
            mass_avail_lbm=float(mass_avail_lbm),
            mass_3min_lbm=float(m3),
            release_type=ReleaseType.CONTINUOUS,
        )

    # For others: check mass in 3 min and/or rate
    mass_3min = min(float(mass_avail_lbm), float(wn_lbm_s) * SECONDS_IN_3_MIN)

    if (mass_3min > INSTANT_MASS_THRESHOLD_LBM) or (wn_lbm_s > INSTANT_RATE_THRESHOLD_LBM_S):
        rtype = ReleaseType.INSTANTANEOUS
    else:
        rtype = ReleaseType.CONTINUOUS

    return ReleaseTypePerHole(
        dn_in=float(dn_in),
        wn_lbm_s=float(wn_lbm_s),
        mass_avail_lbm=float(mass_avail_lbm),
        mass_3min_lbm=float(mass_3min),
        release_type=rtype,
    )


def compute_cof_4_5_release_types(
    *,
    dn_by_hole: Mapping[str, float],
    wn_by_hole_lbm_s: Mapping[str, float],
    mass_avail_by_hole_lbm: Mapping[str, float],
) -> Dict[str, ReleaseTypePerHole]:
    """
    Batch compute release type for each hole size.
    Keys must match across dicts (e.g. 'small','medium','large','rupture').
    """
    out: Dict[str, ReleaseTypePerHole] = {}
    for hole_name, dn in dn_by_hole.items():
        if hole_name not in wn_by_hole_lbm_s or hole_name not in mass_avail_by_hole_lbm:
            raise KeyError(f"Missing wn/mass_avail for hole '{hole_name}'")
        out[str(hole_name)] = determine_release_type_for_hole(
            dn_in=float(dn),
            wn_lbm_s=float(wn_by_hole_lbm_s[hole_name]),
            mass_avail_lbm=float(mass_avail_by_hole_lbm[hole_name]),
        )
    return out
