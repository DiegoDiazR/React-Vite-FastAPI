# app/calculations/cof_4_9_toxic.py
"""
API 581 COF Level 1
Section 4.9: Determine Toxic Consequence

Implements:
- Eq (3.60) toxic release rate:    rate_tox = mfrac_tox * Wn
- Eq (3.61) toxic release mass:    mass_tox = mfrac_tox * mass_n
- Eq (3.62) HF/H2S continuous:     CA = C8 * 10^( c*log10(C4B*rate_tox) + d )
- Eq (3.63) HF/H2S instantaneous:  CA = C8 * 10^( c*log10(C4B*mass_tox) + d )
- Eq (3.64) NH3/Cl2 continuous:    CA = exp( e * (rate_tox)^f )
- Eq (3.65) NH3/Cl2 instantaneous: CA = exp( e * (mass_tox)^f )
- Eq (3.66) toxic effective duration:
      ld_tox = min(3600, mass_n/Wn, 60*ldmax_n)   [seconds]
- Eq (3.67) probability-weighted final toxic consequence area:
      CA_final = sum(gff_n * CA_n)/gff_total

Tables included (from your screenshots):
- Table 4.11 constants for HF and H2S (by duration)
- Table 4.12 constants for NH3 and Chlorine (by duration)
- Table 4.13 constants for misc chemicals (gas and liquid, by duration)
- Table 4.14 IDLH and toxic endpoints (for cutoff logic)

Important:
- This module computes TOXIC PERSONNEL INJURY CONSEQUENCE AREAS (CA_tox_inj).
- C8 and C4B are model constants used in API equations; if your project defines them
  elsewhere, pass them in (defaults provided conservatively as 1.0 only to avoid crash).

You should integrate with 4.7 outputs:
- Wn (lbm/s) and mass_n (lbm)
- ldmax_n from 4.6 (minutes)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple, Mapping, Any


# -------------------------
# Types
# -------------------------
class ReleaseType(str, Enum):
    CONTINUOUS = "continuous"
    INSTANTANEOUS = "instantaneous"


class ToxicMethod(str, Enum):
    HF_H2S = "hf_h2s"
    NH3_CL2 = "nh3_cl2"
    MISC = "misc"


@dataclass(frozen=True)
class ToxicInputs:
    chemical: str
    mfrac_tox: float  # mass fraction of toxic component in release fluid (0..1)
    # from 4.7:
    Wn_lbm_s: float   # theoretical or adjusted release rate used for toxic (API note: no factdi)
    mass_n_lbm: float # release mass upper bound used for toxic
    # for duration calc:
    ldmax_n_min: float  # from 4.6 Table 4.7 (minutes)
    # concentration check for cutoff:
    conc_ppm: Optional[float] = None  # stored or released concentration used vs IDLH


@dataclass(frozen=True)
class ToxicResult:
    chemical: str
    release_type: ReleaseType
    ld_tox_s: float
    rate_tox_lbm_s: float
    mass_tox_lbm: float
    CA_tox_inj: float
    used_constants: Dict[str, float]
    # CAMPO NUEVO QUE FALTABA:
    was_cutoff_by_idlh: bool = False
    


# -------------------------
# Table 4.14 (IDLH ppm) — subset (only what is visible in your screenshot)
# If IDLH is None -> no cutoff check available for that chemical.
# -------------------------
def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


TABLE_4_14_IDLH_PPM: Dict[str, Optional[float]] = {
    _norm("Acrolein"): 2,
    _norm("Acrylonitrile"): 85,
    _norm("AlCl3"): None,
    _norm("Ammonia"): 300,
    _norm("Benzene"): 500,
    _norm("Bromine"): 3,
    _norm("CO"): 1200,
    _norm("Carbon tetrachloride"): 200,
    _norm("Chlorine"): 10,
    _norm("EE"): None,
    _norm("EO"): 800,
    _norm("Formaldehyde"): 20,
    _norm("HCl"): 50,
    _norm("Hydrogen cyanide"): 50,
    _norm("HF"): 30,
    _norm("H2S"): 100,
    _norm("Methanol"): None,
    _norm("Methyl bromide"): None,
    _norm("Methyl isocyanate"): None,
    _norm("Nitric acid"): None,
    _norm("NO2"): 20,
    _norm("Phosgene"): 2,
    _norm("PO"): 400,
    _norm("Styrene"): 700,
    _norm("Sulphur dioxide"): 100,
    _norm("Toluene"): 500,
    _norm("TDI"): None,
}


# -------------------------
# Table 4.11 — HF & H2S constants (c, d) by duration (minutes)
# -------------------------
TABLE_4_11_HF_H2S: Dict[str, Dict[float, Tuple[float, float]]] = {
    _norm("HF"): {
        5.0:  (1.1401, 3.5683),
        10.0: (1.1031, 3.8431),
        20.0: (1.0816, 4.1040),
        40.0: (1.0942, 4.3295),
        60.0: (1.1031, 4.4576),
        -1.0: (1.4056, 0.33606),  # instantaneous
    },
    _norm("H2S"): {
        5.0:  (1.2411, 3.9686),
        10.0: (1.2410, 4.0948),
        20.0: (1.2370, 4.2380),
        40.0: (1.2297, 4.3626),
        60.0: (1.2266, 4.4365),
        -1.0: (0.9674, 2.7840),   # instantaneous
    },
}

# -------------------------
# Table 4.12 — NH3 & Chlorine constants (e, f) by duration (minutes)
# -------------------------
TABLE_4_12_NH3_CL2: Dict[str, Dict[float, Tuple[float, float]]] = {
    _norm("Ammonia"): {
        5.0:  (2690.0, 1.183),
        10.0: (3581.0, 1.181),
        15.0: (4459.0, 1.180),
        20.0: (5326.0, 1.178),
        25.0: (6180.0, 1.176),
        30.0: (7022.0, 1.174),
        35.0: (7852.0, 1.172),
        40.0: (8669.0, 1.169),
        45.0: (9475.0, 1.166),
        50.0: (10268.0, 1.161),
        55.0: (11049.0, 1.155),
        60.0: (11817.0, 1.145),
        -1.0: (14.171, 0.9011),  # instantaneous
    },
    _norm("Chlorine"): {
        5.0:  (15150.0, 1.097),
        10.0: (15934.0, 1.095),
        15.0: (17242.0, 1.092),
        20.0: (19074.0, 1.089),
        25.0: (21430.0, 1.085),
        30.0: (24309.0, 1.082),
        35.0: (27712.0, 1.077),
        40.0: (31640.0, 1.072),
        45.0: (36090.0, 1.066),
        50.0: (41065.0, 1.057),
        55.0: (46564.0, 1.046),
        60.0: (52586.0, 1.026),
        -1.0: (14.976, 1.177),   # instantaneous
    },
}


# -------------------------
# Table 4.13 — Misc chemicals (as visible in your screenshot)
# Keys: chemical -> duration(min) -> (phase, e, f)
# phase in {"gas","liquid"}
# -------------------------
@dataclass(frozen=True)
class MiscEF:
    e: float
    f: float


TABLE_4_13_MISC: Dict[str, Dict[str, Dict[float, MiscEF]]] = {
    _norm("AlCl3"): {
        "gas": {  # Release Duration: All
            -999.0: MiscEF(17.663, 0.9411),
        },
        "liquid": {},
    },
    _norm("CO"): {
        "gas": {
            3.0:  MiscEF(41.412, 1.15),
            5.0:  MiscEF(279.79, 1.06),
            10.0: MiscEF(834.48, 1.13),
            20.0: MiscEF(2915.9, 1.11),
            40.0: MiscEF(5346.8, 1.17),
            60.0: MiscEF(6293.7, 1.21),
        },
        "liquid": {},
    },
    _norm("HCl"): {
        "gas": {
            3.0:  MiscEF(215.48, 1.09),
            5.0:  MiscEF(536.28, 1.15),
            10.0: MiscEF(2397.5, 1.10),
            20.0: MiscEF(4027.0, 1.18),
            40.0: MiscEF(7534.5, 1.20),
            60.0: MiscEF(8625.1, 1.23),
        },
        "liquid": {},
    },
    _norm("Nitric acid"): {
        "gas": {
            3.0:  MiscEF(53013.0, 1.25),
            5.0:  MiscEF(68700.0, 1.25),
            10.0: MiscEF(96325.0, 1.24),
            20.0: MiscEF(126942.0, 1.23),
            40.0: MiscEF(146941.0, 1.22),
            60.0: MiscEF(156345.0, 1.22),
        },
        "liquid": {
            3.0:  MiscEF(5110.0, 1.08),
            5.0:  MiscEF(9640.8, 1.02),
            10.0: MiscEF(12453.0, 1.06),
            20.0: MiscEF(19149.0, 1.06),
            40.0: MiscEF(31145.0, 1.12),
            60.0: MiscEF(41999.0, 1.12),
        },
    },
    _norm("NO2"): {
        "gas": {
            3.0:  MiscEF(6633.1, 0.70),
            5.0:  MiscEF(9221.4, 0.68),
            10.0: MiscEF(11965.0, 0.68),
            20.0: MiscEF(14248.0, 0.72),
            40.0: MiscEF(22411.0, 0.70),
            60.0: MiscEF(24994.0, 0.71),
        },
        "liquid": {
            3.0:  MiscEF(2132.9, 0.98),
            5.0:  MiscEF(2887.0, 1.04),
            10.0: MiscEF(6194.4, 1.07),
            20.0: MiscEF(13843.0, 1.08),
            40.0: MiscEF(27134.0, 1.12),
            60.0: MiscEF(41657.0, 1.13),
        },
    },
    _norm("Phosgene"): {
        "gas": {
            3.0:  MiscEF(12902.0, 1.20),
            5.0:  MiscEF(22976.0, 1.29),
            10.0: MiscEF(48985.0, 1.24),
            20.0: MiscEF(108298.0, 1.27),
            40.0: MiscEF(244670.0, 1.30),
            60.0: MiscEF(367877.0, 1.31),
        },
        "liquid": {
            3.0:  MiscEF(3414.8, 1.06),
            5.0:  MiscEF(6857.1, 1.10),
            10.0: MiscEF(21215.0, 1.12),
            20.0: MiscEF(63361.0, 1.16),
            40.0: MiscEF(178841.0, 1.20),
            60.0: MiscEF(314608.0, 1.23),
        },
    },
    _norm("TDI"): {
        "gas": {},
        "liquid": {
            3.0:  MiscEF(3692.5, 1.06),
            5.0:  MiscEF(3849.2, 1.09),
            10.0: MiscEF(4564.9, 1.10),
            20.0: MiscEF(4777.5, 1.06),
            40.0: MiscEF(4953.2, 1.06),
            60.0: MiscEF(5972.1, 1.03),
        },
    },
    _norm("EE"): {
        "gas": {
            1.5: MiscEF(3.819, 1.171),
            3.0: MiscEF(7.438, 1.181),
            5.0: MiscEF(17.735, 1.122),
            10.0: MiscEF(33.721, 1.111),
            20.0: MiscEF(122.68, 0.971),
            40.0: MiscEF(153.03, 0.995),
            60.0: MiscEF(315.57, 0.899),
        },
        "liquid": {
            10.0: MiscEF(3.081, 1.105),
            20.0: MiscEF(16.877, 1.065),
            40.0: MiscEF(43.292, 1.132),
            60.0: MiscEF(105.74, 1.104),
        },
    },
    _norm("EO"): {
        "gas": {
            1.5: MiscEF(2.083, 1.222),
            3.0: MiscEF(12.32, 1.207),
            5.0: MiscEF(31.5, 1.271),
            10.0: MiscEF(185.0, 1.2909),
            20.0: MiscEF(926.0, 1.2849),
            40.0: MiscEF(4563.0, 1.1927),
            60.0: MiscEF(7350.0, 1.203),
        },
        "liquid": {},
    },
    _norm("PO"): {
        "gas": {
            3.0:  MiscEF(0.0019, 1.913),
            5.0:  MiscEF(0.3553, 1.217),
            10.0: MiscEF(0.7254, 1.2203),
            20.0: MiscEF(1.7166, 1.2164),
            40.0: MiscEF(3.9449, 1.2097),
            60.0: MiscEF(4.9155, 1.2522),
        },
        "liquid": {
            5.0:  MiscEF(10.055, 1.198),
            10.0: MiscEF(40.428, 1.111),
            20.0: MiscEF(77.743, 1.114),
            40.0: MiscEF(152.35, 1.118),
            60.0: MiscEF(1812.8, 0.9855),
        },
    },
}


# -------------------------
# Utilities
# -------------------------
def idlh_ppm_for(chemical: str) -> Optional[float]:
    return TABLE_4_14_IDLH_PPM.get(_norm(chemical))


# def _interp_const(duration_min: float, points: Mapping[float, Tuple[float, float]]) -> Tuple[float, float]:
#     """
#     Linear interpolation between duration keys in minutes.
#     Special keys:
#     -1.0 : instantaneous
#     -999.0 / -999.0 : "All" (use directly)
#     """
#     if duration_min <= 0:
#         raise ValueError("duration_min must be > 0 for continuous interpolation.")

#     keys = sorted(k for k in points.keys() if k > 0)
#     if not keys:
#         raise ValueError("No continuous-duration points available for interpolation.")

#     if duration_min <= keys[0]:
#         return points[keys[0]]
#     if duration_min >= keys[-1]:
#         return points[keys[-1]]

#     for i in range(len(keys) - 1):
#         lo = keys[i]
#         hi = keys[i + 1]
#         if lo <= duration_min <= hi:
#             c_lo, d_lo = points[lo]
#             c_hi, d_hi = points[hi]
#             t = (duration_min - lo) / (hi - lo)
#             c = c_lo + t * (c_hi - c_lo)
#             d = d_lo + t * (d_hi - d_lo)
#             return float(c), float(d)

#     return points[keys[-1]]

def _interp_const_misc(duration_min: float, points: Mapping[float, Any]) -> Any:
    """
    Interpolador ESPECÍFICO para Tabla 4.13 (Misc Chemicals).
    Maneja objetos MiscEF y el caso especial -999.0 (All Durations).
    """
    # 1. Caso Especial: Constante única para todas las duraciones (ej. AlCl3, Pyrophoric)
    # API 581 a veces usa -999 o un solo valor para indicar esto.
    if -999.0 in points:
        return points[-999.0]
    
    # 2. Filtrar llaves válidas de tiempo
    keys = sorted([k for k in points.keys() if k > 0])
    
    if not keys:
        # Si no hay llaves de tiempo y no hay -999, devolvemos el primer valor disponible (fallback)
        if points:
            return next(iter(points.values()))
        raise ValueError("Diccionario de constantes vacío para Misc Chemical.")

    # 3. Interpolación Standard
    if duration_min <= keys[0]: 
        return points[keys[0]]
    if duration_min >= keys[-1]: 
        return points[keys[-1]]

    for i in range(len(keys) - 1):
        lo, hi = keys[i], keys[i+1]
        if lo <= duration_min <= hi:
            t = (duration_min - lo) / (hi - lo)
            val_lo = points[lo]
            val_hi = points[hi]
            
            # Interpolamos atributos .e y .f
            # Creamos un objeto dummy simple con los valores interpolados
            e_new = val_lo.e + t * (val_hi.e - val_lo.e)
            f_new = val_lo.f + t * (val_hi.f - val_lo.f)
            
            # Retornamos una estructura compatible con punto (.)
            return type('MiscEF_Interp', (object,), {'e': e_new, 'f': f_new})

    return points[keys[-1]]


def toxic_duration_seconds(*, mass_n_lbm: float, Wn_lbm_s: float, ldmax_n_min: float) -> float:
    """
    Eq (3.66):
      ld_tox = min(3600, mass_n/Wn, 60*ldmax_n)
    """
    if Wn_lbm_s <= 0:
        return 0.0
    if mass_n_lbm < 0:
        raise ValueError("mass_n_lbm must be >= 0.")
    if ldmax_n_min <= 0:
        raise ValueError("ldmax_n_min must be > 0.")
    return float(min(3600.0, (mass_n_lbm / Wn_lbm_s), 60.0 * ldmax_n_min))


def rate_tox(*, mfrac_tox: float, Wn_lbm_s: float) -> float:
    """Eq (3.60)."""
    if not (0.0 <= mfrac_tox <= 1.0):
        raise ValueError("mfrac_tox must be in [0,1].")
    return float(mfrac_tox * Wn_lbm_s)


def mass_tox(*, mfrac_tox: float, mass_n_lbm: float) -> float:
    """Eq (3.61)."""
    if not (0.0 <= mfrac_tox <= 1.0):
        raise ValueError("mfrac_tox must be in [0,1].")
    if mass_n_lbm < 0:
        raise ValueError("mass_n_lbm must be >= 0.")
    return float(mfrac_tox * mass_n_lbm)


# -------------------------
# Consequence area models
# -------------------------
def ca_hf_h2s_continuous(
    *,
    chemical: str,
    duration_min: float,
    rate_tox_lbm_s: float,
    C4B: float = 1.0,
    C8: float = 1.0,
) -> Tuple[float, Dict[str, float]]:
    """
    Eq (3.62):
      CA = C8 * 10^( c*log10(C4B*rate_tox) + d )
    constants c,d from Table 4.11 (duration-based)
    """
    if rate_tox_lbm_s <= 0:
        return 0.0, {"c": 0.0, "d": 0.0}

    chem_key = _norm(chemical)
    if chem_key not in TABLE_4_11_HF_H2S:
        raise KeyError(f"Chemical not available in Table 4.11: {chemical}")

    c, d = _interp_const(duration_min, TABLE_4_11_HF_H2S[chem_key])
    x = max(1e-30, C4B * rate_tox_lbm_s)
    CA = C8 * (10.0 ** (c * math.log10(x) + d))
    return float(CA), {"c": float(c), "d": float(d), "C4B": float(C4B), "C8": float(C8)}


def ca_hf_h2s_instantaneous(
    *,
    chemical: str,
    mass_tox_lbm: float,
    C4B: float = 1.0,
    C8: float = 1.0,
) -> Tuple[float, Dict[str, float]]:
    """
    Eq (3.63):
      CA = C8 * 10^( c*log10(C4B*mass_tox) + d )
    constants c,d from Table 4.11 instantaneous row
    """
    if mass_tox_lbm <= 0:
        return 0.0, {"c": 0.0, "d": 0.0}

    chem_key = _norm(chemical)
    if chem_key not in TABLE_4_11_HF_H2S:
        raise KeyError(f"Chemical not available in Table 4.11: {chemical}")

    c, d = TABLE_4_11_HF_H2S[chem_key][-1.0]
    x = max(1e-30, C4B * mass_tox_lbm)
    CA = C8 * (10.0 ** (c * math.log10(x) + d))
    return float(CA), {"c": float(c), "d": float(d), "C4B": float(C4B), "C8": float(C8)}


def ca_nh3_cl2_continuous(
    *,
    chemical: str,
    duration_min: float,
    rate_tox_lbm_s: float,
) -> Tuple[float, Dict[str, float]]:
    """
    Eq (3.64):
      CA = exp( e * (rate_tox)^f )
    constants e,f from Table 4.12 (duration-based)
    """
    if rate_tox_lbm_s <= 0:
        return 0.0, {"e": 0.0, "f": 0.0}

    chem_key = _norm(chemical)
    if chem_key not in TABLE_4_12_NH3_CL2:
        raise KeyError(f"Chemical not available in Table 4.12: {chemical}")

    # interpolate on (e,f)
    points = TABLE_4_12_NH3_CL2[chem_key]
    ef = {k: (v[0], v[1]) for k, v in points.items()}
    e, f = _interp_const(duration_min, ef)

    CA = math.exp(e * (rate_tox_lbm_s ** f))
    return float(CA), {"e": float(e), "f": float(f)}


def ca_nh3_cl2_instantaneous(
    *,
    chemical: str,
    mass_tox_lbm: float,
) -> Tuple[float, Dict[str, float]]:
    """
    Eq (3.65):
      CA = exp( e * (mass_tox)^f )
    constants e,f from Table 4.12 instantaneous row
    """
    if mass_tox_lbm <= 0:
        return 0.0, {"e": 0.0, "f": 0.0}

    chem_key = _norm(chemical)
    if chem_key not in TABLE_4_12_NH3_CL2:
        raise KeyError(f"Chemical not available in Table 4.12: {chemical}")

    e, f = TABLE_4_12_NH3_CL2[chem_key][-1.0]
    CA = math.exp(e * (mass_tox_lbm ** f))
    return float(CA), {"e": float(e), "f": float(f)}


def ca_misc_continuous(
    *,
    chemical: str,
    phase: str,  # "gas" or "liquid"
    duration_min: float,
    rate_tox_lbm_s: float,
) -> Tuple[float, Dict[str, float]]:
    """
    Misc tox: uses Eq (3.64) style for continuous releases:
      CA = exp( e * (rate_tox)^f )
    constants from Table 4.13 for given phase and duration.
    """
    if rate_tox_lbm_s <= 0:
        return 0.0, {"e": 0.0, "f": 0.0}

    chem_key = _norm(chemical)
    ph = phase.strip().lower()
    if chem_key not in TABLE_4_13_MISC:
        raise KeyError(f"Chemical not available in Table 4.13: {chemical}")
    if ph not in TABLE_4_13_MISC[chem_key]:
        raise KeyError(f"Phase '{phase}' not available for chemical in Table 4.13: {chemical}")

    points = TABLE_4_13_MISC[chem_key][ph]
    if not points:
        raise ValueError(f"No constants for chemical={chemical} phase={phase}")

    # "All" case
    if -999.0 in points or -999.0 in points:
        ef = points.get(-999.0) or points.get(-999.0)
        assert ef is not None
        e, f = ef.e, ef.f
        CA = math.exp(e * (rate_tox_lbm_s ** f))
        return float(CA), {"e": float(e), "f": float(f), "note": "all-durations"}

    # interpolate on (e,f)
    keys = sorted(k for k in points.keys() if k > 0)
    if duration_min <= keys[0]:
        e, f = points[keys[0]].e, points[keys[0]].f
    elif duration_min >= keys[-1]:
        e, f = points[keys[-1]].e, points[keys[-1]].f
    else:
        # linear interpolate
        for i in range(len(keys) - 1):
            lo = keys[i]
            hi = keys[i + 1]
            if lo <= duration_min <= hi:
                t = (duration_min - lo) / (hi - lo)
                e = points[lo].e + t * (points[hi].e - points[lo].e)
                f = points[lo].f + t * (points[hi].f - points[lo].f)
                break

    CA = math.exp(e * (rate_tox_lbm_s ** f))
    return float(CA), {"e": float(e), "f": float(f), "phase": ph}


def probability_weighted_area(
    *,
    ca_by_hole: Mapping[int, float],
    gff_by_hole: Mapping[int, float],
    gff_total: float,
) -> float:
    """
    Eq (3.67) style:
      CA_final = sum(gff_n * CA_n)/gff_total
    """
    if gff_total <= 0:
        raise ValueError("gff_total must be > 0.")
    s = 0.0
    for n, ca in ca_by_hole.items():
        gff = float(gff_by_hole.get(n, 0.0))
        s += gff * float(ca)
    return float(s / gff_total)


# -------------------------
# Main computation per hole
# -------------------------
def compute_toxic_for_hole(
    *,
    inp: ToxicInputs,
    release_type: ReleaseType,
    # for misc: needed to select gas vs liquid constants
    misc_phase: str = "gas",
    # C8 and C4B for HF/H2S equations (project constants)
    C8: float = 1.0,
    C4B: float = 1.0,
) -> ToxicResult:
    """
    Computes CA_tox_inj for a single hole release case.
    - Does IDLH cutoff if conc_ppm is provided and IDLH is known.
    """
    chem_key = _norm(inp.chemical)

    # IDLH cutoff (Section 4.9.9 rule-of-thumb)
    was_cutoff = False
    idlh = idlh_ppm_for(inp.chemical)
    if inp.conc_ppm is not None and idlh is not None:
        if inp.conc_ppm <= idlh:
            was_cutoff = True
            # still return structured output
            ld_s = toxic_duration_seconds(mass_n_lbm=inp.mass_n_lbm, Wn_lbm_s=inp.Wn_lbm_s, ldmax_n_min=inp.ldmax_n_min)
            rt = rate_tox(mfrac_tox=inp.mfrac_tox, Wn_lbm_s=inp.Wn_lbm_s)
            mt = mass_tox(mfrac_tox=inp.mfrac_tox, mass_n_lbm=inp.mass_n_lbm)
            return ToxicResult(
                chemical=inp.chemical,
                release_type=release_type,
                ld_tox_s=ld_s,
                rate_tox_lbm_s=rt,
                mass_tox_lbm=mt,
                CA_tox_inj=0.0,
                used_constants={"idl_h_ppm": float(idlh)},
                was_cutoff_by_idlh=True,
            )

    ld_s = toxic_duration_seconds(
        mass_n_lbm=inp.mass_n_lbm,
        Wn_lbm_s=inp.Wn_lbm_s,
        ldmax_n_min=inp.ldmax_n_min,
    )
    duration_min = ld_s / 60.0 if ld_s > 0 else 0.0

    rt = rate_tox(mfrac_tox=inp.mfrac_tox, Wn_lbm_s=inp.Wn_lbm_s)
    mt = mass_tox(mfrac_tox=inp.mfrac_tox, mass_n_lbm=inp.mass_n_lbm)

    # Decide which correlation set to use
    # HF/H2S always assumed gas/vapor in API note
    if chem_key in TABLE_4_11_HF_H2S:
        if release_type == ReleaseType.CONTINUOUS:
            CA, const = ca_hf_h2s_continuous(
                chemical=inp.chemical,
                duration_min=max(1e-9, duration_min),
                rate_tox_lbm_s=rt,
                C4B=C4B,
                C8=C8,
            )
        else:
            CA, const = ca_hf_h2s_instantaneous(
                chemical=inp.chemical,
                mass_tox_lbm=mt,
                C4B=C4B,
                C8=C8,
            )
        return ToxicResult(
            chemical=inp.chemical,
            release_type=release_type,
            ld_tox_s=ld_s,
            rate_tox_lbm_s=rt,
            mass_tox_lbm=mt,
            CA_tox_inj=CA,
            used_constants=const,
            was_cutoff_by_idlh=was_cutoff,
        )

    # NH3 / Chlorine
    if chem_key in TABLE_4_12_NH3_CL2:
        if release_type == ReleaseType.CONTINUOUS:
            CA, const = ca_nh3_cl2_continuous(
                chemical=inp.chemical,
                duration_min=max(1e-9, duration_min),
                rate_tox_lbm_s=rt,
            )
        else:
            CA, const = ca_nh3_cl2_instantaneous(
                chemical=inp.chemical,
                mass_tox_lbm=mt,
            )
        return ToxicResult(
            chemical=inp.chemical,
            release_type=release_type,
            ld_tox_s=ld_s,
            rate_tox_lbm_s=rt,
            mass_tox_lbm=mt,
            CA_tox_inj=CA,
            used_constants=const,
            was_cutoff_by_idlh=was_cutoff,
        )

    # Misc chemicals (Table 4.13) – only continuous equations are defined in text.
    if chem_key in TABLE_4_13_MISC:
        # For instantaneous in 4.9.15(d)(3), API says use Eq (3.64) for continuous and instantaneous
        # (using 3-minute release for instantaneous). Practically: treat instantaneous as duration=3 min,
        # using mass or rate depends on your interpretation; we follow your text: Eq (3.64)/(3.65) pair
        # is not given for misc; so we use Eq (3.64) with duration=3 min and rate_tox as input.
        if release_type == ReleaseType.INSTANTANEOUS:
            duration_use = 3.0
        else:
            duration_use = max(1e-9, duration_min)

        CA, const = ca_misc_continuous(
            chemical=inp.chemical,
            phase=misc_phase,
            duration_min=duration_use,
            rate_tox_lbm_s=rt,
        )
        const = dict(const)
        const["duration_min_used"] = float(duration_use)

        return ToxicResult(
            chemical=inp.chemical,
            release_type=release_type,
            ld_tox_s=ld_s,
            rate_tox_lbm_s=rt,
            mass_tox_lbm=mt,
            CA_tox_inj=CA,
            used_constants=const,
            was_cutoff_by_idlh=was_cutoff,
        )

    raise KeyError(
        f"Chemical '{inp.chemical}' not covered by Table 4.11/4.12/4.13 in this module."
    )


def _norm(s: str) -> str:
    """Normaliza el nombre del químico para búsqueda."""
    return " ".join(s.strip().lower().split())

def check_toxic_applicability(chemical: str) -> bool:
    """
    OBSERVACIÓN 1: Filtro de Aplicabilidad.
    Verifica si el fluido existe en alguna de las tablas de toxicidad.
    """
    chem_key = _norm(chemical)
    is_in_411 = chem_key in TABLE_4_11_HF_H2S
    is_in_412 = chem_key in TABLE_4_12_NH3_CL2
    is_in_413 = chem_key in TABLE_4_13_MISC
    return (is_in_411 or is_in_412 or is_in_413)

def _interp_const(duration_min: float, points: Mapping[float, Tuple[float, float]]) -> Tuple[float, float]:
    """
    Interpolación lineal de constantes según la duración de la fuga.
    """
    # Filtramos solo claves positivas (las negativas son para instantáneo)
    keys = sorted([k for k in points.keys() if k > 0])
    
    # Límites
    if duration_min <= keys[0]: return points[keys[0]]
    if duration_min >= keys[-1]: return points[keys[-1]]
    
    # Interpolación
    for i in range(len(keys) - 1):
        lo, hi = keys[i], keys[i+1]
        if lo <= duration_min <= hi:
            t = (duration_min - lo) / (hi - lo)
            val1 = points[lo][0] + t * (points[hi][0] - points[lo][0])
            val2 = points[lo][1] + t * (points[hi][1] - points[lo][1])
            return float(val1), float(val2)
    return points[keys[-1]]

def toxic_duration_seconds(mass_n_lbm: float, Wn_lbm_s: float, ldmax_n_min: float) -> float:
    """Eq (3.66): Duración efectiva de la liberación tóxica (máx 1 hora)."""
    if Wn_lbm_s <= 0: return 0.0
    val = min(3600.0, (mass_n_lbm / Wn_lbm_s), 60.0 * ldmax_n_min)
    return float(val)

# =============================================================================
# 4. ORQUESTADOR MAESTRO (CÁLCULO TOTAL)
# =============================================================================

# def compute_step_4_9_total(
#     chemical: str,
#     mfrac_tox: float,
#     holes_data: Dict[str, dict],
#     gff_by_hole: Dict[str, float],
#     ldmax_n_min: float
# ) -> Dict:
    
#     # 1. Filtro de Aplicabilidad
#     if not check_toxic_applicability(chemical) or mfrac_tox <= 0:
#         return {
#             "applies": False,
#             "chemical": chemical,
#             "CA_tox_inj_final": 0.0,
#             "per_hole": {},
#             "message": f"El fluido '{chemical}' no está categorizado como tóxico."
#         }

#     chem_key = _norm(chemical)
#     per_hole_results = {}
#     ca_tox_sum = 0.0
#     gff_total = sum(gff_by_hole.values())

#     # 2. Bucle por Agujero
#     for size, data in holes_data.items():
#         Wn = data["Wn_lbm_s"]
#         mass_n = data["mass_n_lbm"]
#         rtype = data["release_type"]

#         ld_s = toxic_duration_seconds(mass_n, Wn, ldmax_n_min)
#         duration_min = ld_s / 60.0
        
#         rate_tox = mfrac_tox * Wn
#         mass_tox = mfrac_tox * mass_n

#         CA_n = 0.0
#         consts = {}

#         # Selección de Modelo
#         if chem_key in TABLE_4_11_HF_H2S:
#             points = TABLE_4_11_HF_H2S[chem_key]
#             if rtype == ReleaseType.CONTINUOUS:
#                 c, d = _interp_const(max(1e-9, duration_min), points)
#                 CA_n = 1.0 * (10.0 ** (c * math.log10(max(1e-30, rate_tox)) + d))
#             else:
#                 c, d = points[-1.0]
#                 CA_n = 1.0 * (10.0 ** (c * math.log10(max(1e-30, mass_tox)) + d))
#             consts = {"c": c, "d": d}

#         elif chem_key in TABLE_4_12_NH3_CL2:
#             points = TABLE_4_12_NH3_CL2[chem_key]
#             if rtype == ReleaseType.CONTINUOUS:
#                 e, f = _interp_const(max(1e-9, duration_min), points)
#                 CA_n = math.exp(e * (max(1e-30, rate_tox) ** f))
#             else:
#                 e, f = points[-1.0]
#                 CA_n = math.exp(e * (max(1e-30, mass_tox) ** f))
#             consts = {"e": e, "f": f}

#         elif chem_key in TABLE_4_13_MISC:
#             points = TABLE_4_13_MISC[chem_key]
#             dur_lookup = 3.0 if rtype == ReleaseType.INSTANTANEOUS else max(1e-9, duration_min)
#             e, f = _interp_const(dur_lookup, points)
#             CA_n = math.exp(e * (max(1e-30, rate_tox) ** f))
#             consts = {"e": e, "f": f}

#         # --- AQUÍ SE ASIGNAN LAS CONSTANTES AL RESULTADO ---
#         per_hole_results[size] = ToxicResult(
#             chemical=chemical,
#             release_type=rtype,
#             ld_tox_s=ld_s,
#             rate_tox_lbm_s=rate_tox,
#             mass_tox_lbm=mass_tox,
#             CA_tox_inj=CA_n,
#             used_constants=consts  # <--- CRÍTICO
#         )
#         # ---------------------------------------------------

#         gff_n = gff_by_hole.get(size, 0.0)
#         ca_tox_sum += gff_n * CA_n

#     ca_tox_final = ca_tox_sum / gff_total if gff_total > 0 else 0.0

#     return {
#         "applies": True,
#         "chemical": chemical,
#         "per_hole": per_hole_results,
#         "CA_tox_inj_final": ca_tox_final
#     }

# EN: app/calculations/cof_4_9_toxic.py

def compute_step_4_9_total(
    chemical: str,
    mfrac_tox: float,
    holes_data: Dict[str, dict],
    gff_by_hole: Dict[str, float],
    ldmax_n_min: float
) -> Dict:
    
    # 1. Filtro de Aplicabilidad
    if not check_toxic_applicability(chemical) or mfrac_tox <= 0:
        return {
            "applies": False,
            "chemical": chemical,
            "CA_tox_inj_final": 0.0,
            "per_hole": {},
            "message": f"El fluido '{chemical}' no está categorizado como tóxico o mfrac=0."
        }

    chem_key = _norm(chemical)
    per_hole_results = {}
    ca_tox_sum = 0.0
    gff_total = sum(gff_by_hole.values())

    # 2. Bucle por Agujero
    for size, data in holes_data.items():
        Wn = data["Wn_lbm_s"]
        mass_n = data["mass_n_lbm"]
        rtype = data["release_type"]
        
        # IMPORTANTE: Recuperar la fase enviada por el orquestador
        # Si no viene, asumimos "gas" por defecto
        hole_phase = data.get("phase", "gas").lower()

        ld_s = toxic_duration_seconds(mass_n, Wn, ldmax_n_min)
        duration_min = ld_s / 60.0
        
        rate_tox = mfrac_tox * Wn
        mass_tox = mfrac_tox * mass_n

        CA_n = 0.0
        consts = {}

        # --- SELECCIÓN DE MODELO ---
        
        # A. HF / H2S (Tabla 4.11) - Estructura: {Tiempo: (c,d)}
        if chem_key in TABLE_4_11_HF_H2S:
            points = TABLE_4_11_HF_H2S[chem_key]
            if rtype == ReleaseType.CONTINUOUS:
                c, d = _interp_const(max(1e-9, duration_min), points)
                CA_n = 1.0 * (10.0 ** (c * math.log10(max(1e-30, rate_tox)) + d))
            else:
                c, d = points[-1.0] # -1.0 es la clave para instantáneo en esta tabla
                CA_n = 1.0 * (10.0 ** (c * math.log10(max(1e-30, mass_tox)) + d))
            consts = {"c": c, "d": d}

        # B. NH3 / CL2 (Tabla 4.12) - Estructura: {Tiempo: (e,f)}
        # B. NH3 / CL2 (Tabla 4.12)
        elif chem_key in TABLE_4_12_NH3_CL2:
            points = TABLE_4_12_NH3_CL2[chem_key]
            
            # Interpolación de constantes e, f
            if rtype == ReleaseType.CONTINUOUS:
                e, f = _interp_const(max(1e-9, duration_min), points)
                
                # --- CORRECCIÓN AQUÍ ---
                # ANTES (Error Overflow):
                # CA_n = math.exp(e * (max(1e-30, rate_tox) ** f))
                
                # AHORA (Correcto - Power Law):
                CA_n = e * (max(1e-30, rate_tox) ** f)

            else:
                e, f = points[-1.0]
                
                # --- CORRECCIÓN AQUÍ ---
                # ANTES (Error Overflow):
                # CA_n = math.exp(e * (max(1e-30, mass_tox) ** f))
                
                # AHORA (Correcto - Power Law):
                CA_n = e * (max(1e-30, mass_tox) ** f)

            consts = {"e": e, "f": f}

        # C. MISC CHEMICALS (Tabla 4.13) - Estructura: {FASE: {Tiempo: MiscEF}}
        # AQUÍ ESTABA EL ERROR: Necesitamos entrar al nivel de FASE primero
        elif chem_key in TABLE_4_13_MISC:
            phase_dict = TABLE_4_13_MISC[chem_key]
            
            # ... (Lógica de selección de fase queda igual) ...
            if hole_phase in phase_dict and phase_dict[hole_phase]:
                points = phase_dict[hole_phase]
            elif "gas" in phase_dict and phase_dict["gas"]:
                points = phase_dict["gas"]
            
            if points:
                dur_lookup = 3.0 if rtype == ReleaseType.INSTANTANEOUS else max(1e-9, duration_min)
                try:
                    ef_obj = _interp_const_misc(dur_lookup, points)
                    e, f = ef_obj.e, ef_obj.f
                    
                    # --- CORRECCIÓN CRÍTICA AQUÍ ---
                    # ANTES (Incorrecto para Misc):
                    # CA_n = math.exp(e * (max(1e-30, rate_tox) ** f))
                    
                    # AHORA (Correcto - Power Law):
                    # API 581 Eq 3.60/3.61 generalizada para Misc
                    CA_n = e * (max(1e-30, rate_tox) ** f)
                    
                    consts = {"e": e, "f": f, "phase_used": hole_phase}
                except Exception:
                    CA_n = 0.0
            else:
                CA_n = 0.0

        # Asignar resultado
        per_hole_results[size] = ToxicResult(
            chemical=chemical,
            release_type=rtype,
            ld_tox_s=ld_s,
            rate_tox_lbm_s=rate_tox,
            mass_tox_lbm=mass_tox,
            CA_tox_inj=CA_n,
            used_constants=consts,
            was_cutoff_by_idlh=False
        )

        gff_n = gff_by_hole.get(size, 0.0)
        ca_tox_sum += gff_n * CA_n

    ca_tox_final = ca_tox_sum / gff_total if gff_total > 0 else 0.0

    return {
        "applies": True,
        "chemical": chemical,
        "per_hole": per_hole_results,
        "CA_tox_inj_final": ca_tox_final
    }

# # =============================================================================
# # BLOQUE DE PRUEBA RÁPIDA (EJECUCIÓN DIRECTA)
# # =============================================================================
# if __name__ == "__main__":
#     # Simulación de datos que vendrían del Paso 4.7
#     holes_test = {
#         "small":   {"Wn_lbm_s": 0.23, "mass_n_lbm": 31.5, "release_type": ReleaseType.CONTINUOUS},
#         "medium":  {"Wn_lbm_s": 2.85, "mass_n_lbm": 31.5, "release_type": ReleaseType.CONTINUOUS},
#         "large":   {"Wn_lbm_s": 45.6, "mass_n_lbm": 31.5, "release_type": ReleaseType.INSTANTANEOUS},
#         "rupture": {"Wn_lbm_s": 243.2,"mass_n_lbm": 31.5, "release_type": ReleaseType.INSTANTANEOUS}
#     }
#     gff_test = {"small": 8e-6, "medium": 2e-5, "large": 2e-6, "rupture": 6e-7}

#     # PRUEBA 1: H2S (Debe calcular)
#     print("\n--- PRUEBA CON H2S ---")
#     res = compute_step_4_9_total("Hydrogen sulfide", 0.05, holes_test, gff_test, 60.0)
#     if res["applies"]:
#         print(f"Área Final Ponderada: {res['CA_tox_inj_final']:.2f} ft²")
#         print(f"Detalle Rupture: {res['per_hole']['rupture'].CA_tox_inj:.2f} ft²")
#     else:
#         print(res["message"])

#     # PRUEBA 2: AGUA (No debe calcular)
#     print("\n--- PRUEBA CON AGUA ---")
#     res2 = compute_step_4_9_total("Water", 0.0, holes_test, gff_test, 60.0)
#     print(f"Aplica: {res2['applies']}")
#     print(f"Mensaje: {res2['message']}")