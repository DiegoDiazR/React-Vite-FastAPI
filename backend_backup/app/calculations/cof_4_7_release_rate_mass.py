# app/calculations/cof_4_7_release_rate_mass.py
"""
API 581 COF Level 1
Section 4.7: Determine the Release Rate and Mass for COF

Implements:
- Eq. (3.12): rate_n = W_n * (1 - fact_di)
- Eq. (3.13): mass_n = min(rate_n * ld_n, mass_avail_n)
- Eq. (3.14): ld_n = min( mass_avail_n / rate_n , 60 * ldmax_n )

Notes:
- rate_n is used for CONTINUOUS consequence calculations.
- For INSTANTANEOUS (puff), the mass_n is used (upper bound).
- Leak duration ld_n is capped by ldmax_n from Section 4.6 (minutes).

Units:
- Internal SI:
    W_n, rate_n: kg/s
    mass_avail_n, mass_n: kg
    ld_n: s
    ldmax_n: min (input) -> s (used internally)
- Also returns US mass flow in lbm/s and masses in lbm for convenience.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Any

LBM_TO_KG = 0.45359237
KG_TO_LBM = 1.0 / LBM_TO_KG


# -------------------------
# Data models
# -------------------------

@dataclass(frozen=True)
class ReleaseRateMassInputs:
    """
    Inputs required for Section 4.7 per hole size.

    Parameters
    ----------
    Wn_kg_s:
        Theoretical release mass rate from Section 4.3 (W_n), kg/s.
        If you only have lbm/s, pass Wn_lbm_s instead.

    Wn_lbm_s:
        Alternative to Wn_kg_s. If provided, it will be converted to kg/s.

    fact_di:
        Release reduction factor from Section 4.6 Table 4.6 (dimensionless).
        NOTE: API text uses (1 - fact_di).

    mass_avail_kg:
        Available mass from Section 4.4 (mass_avail,n), kg.
        If you only have lbm, pass mass_avail_lbm instead.

    mass_avail_lbm:
        Alternative to mass_avail_kg. If provided, it will be converted to kg.

    ldmax_min:
        Maximum leak duration from Section 4.6 Table 4.7 (minutes).
    """
    fact_di: float
    ldmax_min: float

    Wn_kg_s: Optional[float] = None
    Wn_lbm_s: Optional[float] = None

    mass_avail_kg: Optional[float] = None
    mass_avail_lbm: Optional[float] = None


@dataclass(frozen=True)
class ReleaseRateMassResult:
    """
    Outputs for Section 4.7 per hole size.
    """
    # Adjusted release rate (Eq. 3.12)
    rate_kg_s: float
    rate_lbm_s: float

    # Leak duration (Eq. 3.14)
    ld_s: float
    ld_min: float

    # Upper bound release mass (Eq. 3.13)
    mass_kg: float
    mass_lbm: float


@dataclass(frozen=True)
class Step47HoleResult:
    """
    Representa el resultado final de masa para un tamaño de agujero específico.
    """
    hole_size: Any        # Enum ReleaseHoleSize o str
    mass_lbm: float       # Masa final liberada (lb)
    rate_lbm_s: float     # Tasa de liberación usada (lb/s)
    release_type: Any     # Enum ReleaseType (Continuous/Instantaneous)

@dataclass(frozen=True)
class Step47Result:
    """
    Contenedor de todos los resultados del Paso 4.7.
    """
    results_by_hole: Dict[Any, Step47HoleResult]

# -------------------------
# Validation / conversions
# -------------------------

def _require_positive(name: str, x: float) -> float:
    if x is None:
        raise ValueError(f"{name} is required.")
    if x < 0:
        raise ValueError(f"{name} must be >= 0. Got {x}.")
    return float(x)


def _coerce_Wn_kg_s(inp: ReleaseRateMassInputs) -> float:
    if inp.Wn_kg_s is not None:
        return _require_positive("Wn_kg_s", inp.Wn_kg_s)
    if inp.Wn_lbm_s is not None:
        wn_lbm_s = _require_positive("Wn_lbm_s", inp.Wn_lbm_s)
        return wn_lbm_s * LBM_TO_KG
    raise ValueError("You must provide either Wn_kg_s or Wn_lbm_s.")


def _coerce_mass_avail_kg(inp: ReleaseRateMassInputs) -> float:
    if inp.mass_avail_kg is not None:
        return _require_positive("mass_avail_kg", inp.mass_avail_kg)
    if inp.mass_avail_lbm is not None:
        m_lbm = _require_positive("mass_avail_lbm", inp.mass_avail_lbm)
        return m_lbm * LBM_TO_KG
    raise ValueError("You must provide either mass_avail_kg or mass_avail_lbm.")


def _validate_fact_di(fact_di: float) -> float:
    fact_di = float(fact_di)
    # Table 4.6 values are between 0 and 0.25 in your screenshot.
    # We'll allow [0, 1] to be safe.
    if not (0.0 <= fact_di <= 1.0):
        raise ValueError(f"fact_di must be between 0 and 1. Got {fact_di}.")
    return fact_di


def _validate_ldmax_min(ldmax_min: float) -> float:
    ldmax_min = float(ldmax_min)
    if ldmax_min <= 0:
        raise ValueError(f"ldmax_min must be > 0 minutes. Got {ldmax_min}.")
    return ldmax_min


# -------------------------
# Core equations (3.12, 3.14, 3.13)
# -------------------------

def adjusted_release_rate_kg_s(Wn_kg_s: float, fact_di: float) -> float:
    """
    Eq. (3.12): rate_n = W_n * (1 - fact_di)
    """
    Wn_kg_s = _require_positive("Wn_kg_s", Wn_kg_s)
    fact_di = _validate_fact_di(fact_di)
    rate = Wn_kg_s * (1.0 - fact_di)
    # Numerical guard
    return max(0.0, float(rate))


def leak_duration_s(mass_avail_kg: float, rate_kg_s: float, ldmax_min: float) -> float:
    """
    Eq. (3.14): ld_n = min( mass_avail_n / rate_n , 60 * ldmax_n )
    """
    mass_avail_kg = _require_positive("mass_avail_kg", mass_avail_kg)
    ldmax_min = _validate_ldmax_min(ldmax_min)

    if rate_kg_s <= 0:
        # If there is no adjusted rate, duration is 0 in practice
        return 0.0

    t_unbounded = mass_avail_kg / rate_kg_s  # s
    t_cap = 60.0 * ldmax_min                 # s
    return float(min(t_unbounded, t_cap))


def instantaneous_release_mass_kg(mass_avail_kg: float, rate_kg_s: float, ld_s: float) -> float:
    """
    Eq. (3.13): mass_n = min( rate_n * ld_n , mass_avail_n )
    """
    mass_avail_kg = _require_positive("mass_avail_kg", mass_avail_kg)
    ld_s = _require_positive("ld_s", ld_s)

    if rate_kg_s <= 0 or ld_s <= 0:
        return 0.0

    m = rate_kg_s * ld_s
    return float(min(m, mass_avail_kg))


def compute_cof_4_7_per_hole(inp: ReleaseRateMassInputs) -> ReleaseRateMassResult:
    """
    Computes 4.7 for a single hole size.

    Returns:
    - rate_n (adjusted) for continuous analysis
    - ld_n leak duration
    - mass_n upper bound puff mass
    """
    Wn_kg_s = _coerce_Wn_kg_s(inp)
    mass_avail_kg = _coerce_mass_avail_kg(inp)
    fact_di = _validate_fact_di(inp.fact_di)
    ldmax_min = _validate_ldmax_min(inp.ldmax_min)

    rate_kg_s = adjusted_release_rate_kg_s(Wn_kg_s=Wn_kg_s, fact_di=fact_di)
    ld_s = leak_duration_s(mass_avail_kg=mass_avail_kg, rate_kg_s=rate_kg_s, ldmax_min=ldmax_min)
    mass_kg = instantaneous_release_mass_kg(mass_avail_kg=mass_avail_kg, rate_kg_s=rate_kg_s, ld_s=ld_s)

    return ReleaseRateMassResult(
        rate_kg_s=rate_kg_s,
        rate_lbm_s=rate_kg_s * KG_TO_LBM,
        ld_s=ld_s,
        ld_min=ld_s / 60.0,
        mass_kg=mass_kg,
        mass_lbm=mass_kg * KG_TO_LBM,
    )


def compute_cof_4_7_for_holes(
    inputs_by_hole: Mapping[str, ReleaseRateMassInputs],
) -> Dict[str, ReleaseRateMassResult]:
    """
    Computes 4.7 for multiple hole sizes.

    Example keys:
      {"small": ..., "medium": ..., "large": ..., "rupture": ...}

    Returns dict with same keys.
    """
    out: Dict[str, ReleaseRateMassResult] = {}
    for hole_key, inp in inputs_by_hole.items():
        out[str(hole_key)] = compute_cof_4_7_per_hole(inp)
    return out

# def compute_cof_4_7_mass_release(
#     wn_val: float,
#     release_type: Any,
#     mass_released_4_5: float,
#     ld_max_minutes: float
# ) -> float:
#     """
#     Calcula la masa final liberada (mass_add) según API 581.
    
#     Reglas:
#     1. Si es Instantáneo -> Masa = Inventario (mass_released_4_5).
#     2. Si es Continuo -> Masa = min(Inventario, Tasa * Tiempo_Detección).
#     """
#     # Si es instantáneo, 4.5 ya determinó que se libera el inventario
#     if str(release_type) == "Instantaneous" or str(release_type.value) == "Instantaneous":
#         return mass_released_4_5
    
#     # Si es continuo, calculamos basado en detección
#     ld_max_sec = ld_max_minutes * 60.0
#     mass_detection = wn_val * ld_max_sec
    
#     # La masa final no puede exceder lo que 4.5 determinó como disponible/liberable
#     # (aunque 4.5 usa 3 min como base, aquí usamos ld_max como real)
#     # Para ser conservadores en Nivel 1, usamos la masa de detección, 
#     # asumiendo que el inventario es suficiente (o controlado por el orquestador).
#     return mass_detection


# -------------------------
# Quick local test
# -------------------------
if __name__ == "__main__":
    # Example for one hole:
    # Wn = 10 kg/s (from 4.3), fact_di = 0.20 (from 4.6), ldmax=20 min (from 4.6),
    # mass_avail = 5000 kg (from 4.4)
    ex = ReleaseRateMassInputs(
        Wn_kg_s=10.0,
        fact_di=0.20,
        ldmax_min=20.0,
        mass_avail_kg=5000.0,
    )
    r = compute_cof_4_7_per_hole(ex)
    print(r)
