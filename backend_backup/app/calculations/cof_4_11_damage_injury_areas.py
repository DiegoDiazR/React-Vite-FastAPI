# app/calculations/cof_4_11_damage_injury_areas.py
"""
API 581 COF Level 1
Section 4.11: Determine the Component Damage and Personnel Injury Consequence Areas

Implements:
- Eq (3.78) / (3.79): Final Component Damage Area
- Eq (3.80): Final Personnel Injury Area
- Eq (3.81): Final Consequence Area
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


def _val(x: Optional[float]) -> float:
    """
    Helper: Converts None to 0.0 and validates non-negativity.
    """
    if x is None:
        return 0.0
    if x < 0:
        raise ValueError(f"Consequence area cannot be negative: {x}")
    return float(x)


@dataclass(frozen=True)
class ConsequenceAreasByMechanism:
    """
    Input bundle: Consequence areas by mechanism (outputs from 4.8, 4.9, 4.10).
    
    Level 1 Notes:
    - Toxic and Nonflammable releases generally do not produce component damage 
      (caf_cmd_tox and caf_cmd_nfnt are usually 0.0).
    """
    # Component damage areas (cmd)
    caf_cmd_flam: Optional[float] = None
    caf_cmd_tox: Optional[float] = None
    caf_cmd_nfnt: Optional[float] = None

    # Personnel injury areas (inj)
    caf_inj_flam: Optional[float] = None
    caf_inj_tox: Optional[float] = None
    caf_inj_nfnt: Optional[float] = None


@dataclass(frozen=True)
class FinalConsequenceAreas:
    """
    Final Output for Section 4.11.
    """
    # Eq (3.79) — Final component damage consequence area
    caf_cmd: float
    
    # Eq (3.80) — Final personnel injury consequence area
    caf_inj: float
    
    # Eq (3.81) — Final consequence area
    caf: float

    # Traceability fields (useful for reporting)
    caf_cmd_flam: float
    caf_inj_flam: float
    caf_inj_tox: float
    caf_inj_nfnt: float


def compute_cof_4_11_damage_injury_areas(inp: ConsequenceAreasByMechanism) -> FinalConsequenceAreas:
    """
    Calculates the final consequence areas per Section 4.11.5 Steps 11.1 - 11.3.
    """
    
    # -----------------------------
    # Step 11.1: Component Damage Area (Eq 3.78 / 3.79)
    # -----------------------------
    # Note: Text states CA_cmd_tox and CA_cmd_nfnt are 0.0 for Level 1,
    # so CA_cmd usually equals CA_cmd_flam. Max() handles this safely.
    val_cmd_flam = _val(inp.caf_cmd_flam)
    val_cmd_tox = _val(inp.caf_cmd_tox)
    val_cmd_nfnt = _val(inp.caf_cmd_nfnt)

    caf_cmd = max(val_cmd_flam, val_cmd_tox, val_cmd_nfnt)

    # -----------------------------
    # Step 11.2: Personnel Injury Area (Eq 3.80)
    # -----------------------------
    val_inj_flam = _val(inp.caf_inj_flam)
    val_inj_tox = _val(inp.caf_inj_tox)
    val_inj_nfnt = _val(inp.caf_inj_nfnt)

    caf_inj = max(val_inj_flam, val_inj_tox, val_inj_nfnt)

    # -----------------------------
    # Step 11.3: Final Consequence Area (Eq 3.81)
    # -----------------------------
    caf = max(caf_cmd, caf_inj)

    return FinalConsequenceAreas(
        caf_cmd=caf_cmd,
        caf_inj=caf_inj,
        caf=caf,
        # Traceability
        caf_cmd_flam=val_cmd_flam,
        caf_inj_flam=val_inj_flam,
        caf_inj_tox=val_inj_tox,
        caf_inj_nfnt=val_inj_nfnt,
    )
