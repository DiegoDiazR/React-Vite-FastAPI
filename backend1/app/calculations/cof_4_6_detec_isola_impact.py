# app/calculations/cof_4_6_detec_isola_impact.py
"""
API 581 COF Level 1
Section 4.6: Estimate the Impact of Detection and Isolation Systems on Release Magnitude

Includes:
- Table 4.5: qualitative rating guide (descriptions)
- Table 4.6: release magnitude adjustment -> reduction factor fact_di
- Table 4.7: maximum leak durations ld_max (minutes) based on detection & isolation ratings

Outputs:
- fact_di (dimensionless)
- ld_max_minutes per hole group (small/medium/large/rupture)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Literal


class Rating(str, Enum):
    A = "A"
    B = "B"
    C = "C"


HoleKey = Literal["small", "medium", "large", "rupture"]


# -------------------------
# Table 4.5 (descriptions)
# -------------------------
TABLE_4_5_DETECTION_GUIDE = {
    Rating.A: "Instrumentation designed specifically to detect material losses by changes in operating conditions (i.e. loss of pressure or flow) in the system.",
    Rating.B: "Suitably located detectors to determine when the material is present outside the pressure-containing envelope.",
    Rating.C: "Visual detection, cameras, or detectors with marginal coverage.",
}

TABLE_4_5_ISOLATION_GUIDE = {
    Rating.A: "Isolation or shutdown systems activated directly from process instrumentation or detectors, with no operator intervention.",
    Rating.B: "Isolation or shutdown systems activated by operators in the control room or other suitable locations remote from the leak.",
    Rating.C: "Isolation dependent on manually operated valves.",
}


# -------------------------
# Table 4.6 (fact_di)
# -------------------------
def compute_fact_di(detection: Rating, isolation: Rating) -> float:
    """
    Table 4.6 — Adjustments to Release Based on Detection and Isolation Systems
    Returns: reduction factor fact_di

    Mapping (from your image):
    - A/A => 0.25
    - A/B => 0.20
    - (A or B)/C => 0.10
    - B/B => 0.15
    - C/C => 0.00

    For combos not explicitly listed, we apply the closest conservative interpretation:
    - If isolation is C and detection is A or B => 0.10
    - If detection is C and isolation is C => 0.00
    - If detection is C and isolation is A or B: not in table; choose 0.00 (no credit) by default
      (you can change to 0.10 if your org wants credit; but table doesn't show it).
    """
    d = Rating(detection)
    i = Rating(isolation)

    if d == Rating.A and i == Rating.A:
        return 0.25
    if d == Rating.A and i == Rating.B:
        return 0.20
    if (d in (Rating.A, Rating.B)) and i == Rating.C:
        return 0.10
    if d == Rating.B and i == Rating.B:
        return 0.15
    if d == Rating.C and i == Rating.C:
        return 0.00
    if d == Rating.C and i == Rating.B:
        return 0.10

    # Not explicitly provided in table: be conservative and give no reduction credit
    return 0.00

# -------------------------
# Table 4.7 — Leak durations (minutes)
# -------------------------
# Each entry gives max leak duration for each hole group:
#  - small: < 1/4 in
#  - medium: d2 = 1/4 < D <= 1 in
#  - large: d3 = 1 < D <= 4 in
#  - rupture: d4 = D >= 4 in
#
# Values from your screenshot:

_TABLE_4_7: Dict[str, Dict[HoleKey, float]] = {
    # Detection A, Isolation A
    "A_A": {"small": 20.0, "medium": 10.0, "large": 5.0, "rupture": 60.0},
    # Detection A, Isolation B
    "A_B": {"small": 30.0, "medium": 20.0, "large": 10.0, "rupture": 60.0},
    # Detection A, Isolation C
    "A_C": {"small": 40.0, "medium": 30.0, "large": 20.0, "rupture": 60.0},
    # Detection B, Isolation A or B
    "B_AB": {"small": 40.0, "medium": 30.0, "large": 20.0, "rupture": 60.0},
    # Detection B, Isolation C
    "B_C": {"small": 60.0, "medium": 30.0, "large": 20.0, "rupture": 60.0},
    # Detection C, Isolation A/B/C
    "C_ABC": {"small": 60.0, "medium": 40.0, "large": 20.0, "rupture": 60.0},
}


def compute_ld_max_minutes(detection: Rating, isolation: Rating, hole_key: HoleKey) -> float:
    """
    Table 4.7 — leak duration ld_max (minutes) based on detection & isolation system ratings.
    """
    d = Rating(detection)
    i = Rating(isolation)

    if d == Rating.A and i == Rating.A:
        row = "A_A"
    elif d == Rating.A and i == Rating.B:
        row = "A_B"
    elif d == Rating.A and i == Rating.C:
        row = "A_C"
    elif d == Rating.B and i in (Rating.A, Rating.B):
        row = "B_AB"
    elif d == Rating.B and i == Rating.C:
        row = "B_C"
    else:
        # Detection C with any isolation (A/B/C) => C_ABC
        row = "C_ABC"

    return float(_TABLE_4_7[row][hole_key])


@dataclass(frozen=True)
class DetIsoImpactResult:
    detection: Rating
    isolation: Rating
    fact_di: float
    ld_max_minutes: Dict[HoleKey, float]


def compute_cof_4_6_detection_isolation_impact(
    *, detection: Rating, isolation: Rating
) -> DetIsoImpactResult:
    """
    Full 4.6 output:
    - fact_di from Table 4.6
    - ld_max for each hole group from Table 4.7
    """
    fact = compute_fact_di(detection, isolation)
    ld = {
        "small": compute_ld_max_minutes(detection, isolation, "small"),
        "medium": compute_ld_max_minutes(detection, isolation, "medium"),
        "large": compute_ld_max_minutes(detection, isolation, "large"),
        "rupture": compute_ld_max_minutes(detection, isolation, "rupture"),
    }
    return DetIsoImpactResult(
        detection=Rating(detection),
        isolation=Rating(isolation),
        fact_di=float(fact),
        ld_max_minutes=ld,
    )
