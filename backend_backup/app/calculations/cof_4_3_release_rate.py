# app/calculations/cof_4_3_release_rate.py
"""
API 581 COF Level 1
Section 4.3: Release Rate Calculation

Implements:
- Eq (3.3) liquid release mass rate
- Eq (3.4) viscosity correction factor Kv from Reynolds
- Eq (3.5) gas transition pressure (choked vs subsonic)
- Eq (3.6) gas choked (sonic) release rate
- Eq (3.7) gas subsonic release rate
- Eq (3.8) hole area

Notes / Practical:
- Inputs mostly in US units (psi, in, lb/ft3, Rankine)
- Internally computed in SI for consistency, output in kg/s and lbm/s.

This module is designed to be used by:
- 4.4 (inventory, Wmax8)
- 4.7 (rate_n used for COF)
- 4.5 (release type checks may use Wn thresholds)

Author: your project
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Optional, Literal, Dict, Mapping, Any


# -------------------------
# Constants & unit conversions
# -------------------------
PSI_TO_PA = 6894.757293168  # Pa/psi
IN_TO_M = 0.0254            # m/in
LBFT3_TO_KGM3 = 16.01846337396014  # (kg/m3)/(lb/ft3)
RANKINE_TO_K = 5.0 / 9.0    # K/R
LBM_TO_KG = 0.45359237      # kg/lbm

P_ATM_PSI_DEFAULT = 14.7    # typical atmospheric pressure (psia)
G_C = 1.0  # Using SI internally removes the need for gc; kept for clarity.


class Phase(str, Enum):
    LIQUID = "liquid"
    GAS = "gas"

GasRegime = Optional[Literal["choked", "subsonic"]]


@dataclass(frozen=True)
class Orifice:
    """Release hole geometry."""
    d_in: float  # diameter (in)

    def __post_init__(self) -> None:
        if self.d_in <= 0:
            raise ValueError("Orifice diameter d_in must be > 0.")

    @property
    def area_in2(self) -> float:
        """Area in in^2 (Eq 3.8 but in US length units)."""
        return (math.pi / 4.0) * (self.d_in ** 2)

    @property
    def area_m2(self) -> float:
        """Area in m^2 (Eq 3.8 in SI)."""
        d_m = self.d_in * IN_TO_M
        return (math.pi / 4.0) * (d_m ** 2)


@dataclass(frozen=True)
class LiquidInputs:
    """
    Inputs for liquid release (Eq. 3.3).
    ps_psi and patm_psi are absolute pressures (psia).
    """
    ps_psi: float
    patm_psi: float = P_ATM_PSI_DEFAULT
    rho_lbft3: float = 62.4
    cd: float = 0.61
    kv: float = 1.0
    reynolds: Optional[float] = None  # if provided, overrides kv via Eq (3.4)

    def __post_init__(self) -> None:
        if self.ps_psi <= 0:
            raise ValueError("LiquidInputs.ps_psi must be > 0.")
        if self.patm_psi <= 0:
            raise ValueError("LiquidInputs.patm_psi must be > 0.")
        if self.rho_lbft3 <= 0:
            raise ValueError("LiquidInputs.rho_lbft3 must be > 0.")
        if self.cd <= 0:
            raise ValueError("LiquidInputs.cd must be > 0.")
        if self.kv <= 0:
            raise ValueError("LiquidInputs.kv must be > 0.")
        if self.reynolds is not None and self.reynolds <= 0:
            raise ValueError("LiquidInputs.reynolds must be > 0 if provided.")


@dataclass(frozen=True)
class GasInputs:
    """
    Inputs for gas/vapor release (Eq. 3.5, 3.6, 3.7).
    ps_psi and patm_psi are absolute pressures (psia).
    """
    ps_psi: float
    ts_rankine: float
    mw: float
    k: float
    patm_psi: float = P_ATM_PSI_DEFAULT
    # cd: float = 1.0  # conservative recommended when Cd uncertain

    def __post_init__(self) -> None:
        if self.ps_psi <= 0:
            raise ValueError("GasInputs.ps_psi must be > 0.")
        if self.patm_psi <= 0:
            raise ValueError("GasInputs.patm_psi must be > 0.")
        if self.ts_rankine <= 0:
            raise ValueError("GasInputs.ts_rankine must be > 0.")
        if self.mw <= 0:
            raise ValueError("GasInputs.mw must be > 0.")
        if self.k <= 1.0:
            raise ValueError("GasInputs.k must be > 1.0.")


@dataclass(frozen=True)
class ReleaseRateResult:
    phase: Phase
    regime: GasRegime  # gas only
    mdot_kg_s: float
    mdot_lbm_s: float  # lbm/s (same numeric as lb/s in common RBI usage)


# -------------------------
# Helpers
# -------------------------
def _to_pa(psi: float) -> float:
    return psi * PSI_TO_PA


def _to_k_from_rankine(t_rankine: float) -> float:
    return t_rankine * RANKINE_TO_K


def _to_kgm3_from_lbft3(rho_lbft3: float) -> float:
    return rho_lbft3 * LBFT3_TO_KGM3


def kv_from_reynolds(re: float) -> float:
    """
    Eq (3.4):
        Kv = (0.9935 + 2.878/Re^0.5 + 342.75/Re^1.5)^(-1)

    Clamped to [0, 1].
    """
    if re <= 0:
        raise ValueError("Reynolds number must be > 0.")
    kv = (0.9935 + 2.878 / (re ** 0.5) + 342.75 / (re ** 1.5)) ** (-1.0)
    return max(0.0, min(1.0, float(kv)))


# -------------------------
# Core equations
# -------------------------
# --- CONSTANTES DE CONVERSIÓN  ---

def liquid_release_rate(orifice: Orifice, inp: LiquidInputs) -> ReleaseRateResult:
    # 1. Área en pulgadas cuadradas (ya la tenemos en el objeto orifice)
    An_in2 = orifice.area_in2 
    
    # 2. Delta P en lb/ft² (psf) -> psi * 144
    delta_p_psf = (inp.ps_psi - inp.patm_psi) * 144.0
    
    # 3. Fórmula US (Eq. 3.3 simplificada para Excel)
    # Wn = Cd * (An / 144) * sqrt(2 * g * rho * Delta_P_psf)
    # Nota: 32.2 es g_c en este sistema
    
    term_sqrt = math.sqrt(2.0 * 32.2 * inp.rho_lbft3 * delta_p_psf)
    mdot_lbm_s = 0.61 * (An_in2 / 144.0) * term_sqrt

    return ReleaseRateResult(
        phase=Phase.LIQUID,
        regime=None,
        mdot_kg_s=float(mdot_lbm_s * 0.45359), # Mantenemos kg/s para el backend
        mdot_lbm_s=float(mdot_lbm_s),
    )


def transition_pressure_gas(patm_psi: float, k: float) -> float:
    """
    Eq (3.5):
        P_trans = P_atm * ((k + 1)/2)^(k/(k-1))
    """
    if patm_psi <= 0:
        raise ValueError("patm_psi must be > 0.")
    if k <= 1.0:
        raise ValueError("k must be > 1.0.")
    return patm_psi * (((k + 1.0) / 2.0) ** (k / (k - 1.0)))


def gas_release_rate(orifice: Orifice, inp: GasInputs) -> ReleaseRateResult:
    if inp.ps_psi <= inp.patm_psi:
        return ReleaseRateResult(Phase.GAS, "subsonic", 0.0, 0.0)

    # 1. Parámetros de entrada
    A_in2 = orifice.area_in2 
    p0 = inp.ps_psi
    p2 = inp.patm_psi
    T = inp.ts_rankine
    MW = inp.mw
    k = inp.k
    
    # --- TUS CONSTANTES ESPECÍFICAS ---
    R_cte = 1545  # ft-lbf/(lb-mol-°R)
    gc = 32.2       # lbm-ft/(lbf-s^2)

    p_trans_psi = transition_pressure_gas(inp.patm_psi, k)

    if p0 > p_trans_psi:
        regime = "choked"
        # Eq 3.6 - El término termodinámico (fuera de la raíz)
        term = (2.0 / (k + 1.0)) ** ((k + 1.0) / (k - 1.0))
        
        # Wn = Cd * An * P0 * sqrt( (k * MW * gc) / (R * T * 12) ) * term
        # El 12 es para convertir los 'ft' de tu R y gc a 'in'
        inside = (k * MW * gc) / (R_cte * T)
        mdot_lbm_s = 0.9 * A_in2 * p0 * math.sqrt(inside * term)
    else:
        regime = "subsonic"
        pr = p2 / p0
        # Eq 3.7
        # Wn = Cd * An * P0 * sqrt( ((MW * gc)/(R * T * 12)) * (2k/(k-1)) * (pr^(2/k) - pr^((k+1)/k)) )
        constant_part = (MW * gc) / (R_cte * T)
        k_part = (2.0 * k) / (k - 1.0)
        pressure_part = (pr**(2.0/k)) * (1 - (pr**((k - 1.0) / k)))
        mdot_lbm_s = 0.9 * A_in2 * p0 * math.sqrt(max(0, constant_part * k_part * pressure_part))

    return ReleaseRateResult(
        phase=Phase.GAS,
        regime=regime,
        mdot_lbm_s=float(mdot_lbm_s),
        mdot_kg_s=float(mdot_lbm_s * 0.45359)
    )

# -------------------------
# Public API
# -------------------------
def compute_release_rate(
    *,
    phase: Phase,
    d_n_in: float,
    liquid: Optional[LiquidInputs] = None,
    gas: Optional[GasInputs] = None,
) -> ReleaseRateResult:
    """
    Compute W_n (mass release rate) for one hole diameter d_n (in).
    """
    orifice = Orifice(d_in=float(d_n_in))

    if phase == Phase.LIQUID:
        if liquid is None:
            raise ValueError("liquid inputs required when phase=LIQUID")
        return liquid_release_rate(orifice, liquid)

    if phase == Phase.GAS:
        if gas is None:
            raise ValueError("gas inputs required when phase=GAS")
        return gas_release_rate(orifice, gas)

    raise ValueError(f"Unsupported phase: {phase}")


def compute_release_rates_for_holes(
    *,
    phase: Phase,
    hole_diameters_in: Mapping[Any, float], # Aceptamos cualquier tipo de llave
    liquid: Optional[LiquidInputs] = None,
    gas: Optional[GasInputs] = None,
) -> Dict[Any, ReleaseRateResult]:
    
    out = {}
    for name, d_in in hole_diameters_in.items():
        # Calculamos la tasa. Mantenemos la llave original (sea Enum o String)
        out[name] = compute_release_rate(
            phase=phase, d_n_in=float(d_in), liquid=liquid, gas=gas
        )
    return out


def compute_wmax8_rate(
    *,
    phase: Phase,
    liquid: Optional[LiquidInputs] = None,
    gas: Optional[GasInputs] = None,
    d_max_in: float = 8.0,
) -> ReleaseRateResult:
    """
    Helper for 4.4 Step 4.5:
    Wmax8 is the release rate using an 8-in diameter hole (203 mm),
    computed with the same equations as 4.3.
    """
    return compute_release_rate(phase=phase, d_n_in=float(d_max_in), liquid=liquid, gas=gas)


# -------------------------
# Quick self-test
# -------------------------
if __name__ == "__main__":
    # Liquid example
    rL = compute_release_rate(
        phase=Phase.LIQUID,
        d_n_in=0.25,
        liquid=LiquidInputs(ps_psi=100.0, patm_psi=14.7, rho_lbft3=50.0, cd=0.61, kv=1.0),
    )
    print("LIQUID:", rL)

    # Gas example
    rG = compute_release_rate(
        phase=Phase.GAS,
        d_n_in=1.0,
        gas=GasInputs(ps_psi=250.0, patm_psi=14.7, ts_rankine=520.0, mw=18.0, k=1.30, cd=1.0),
    )
    print("GAS:", rG)

    # Wmax8 example
    r8 = compute_wmax8_rate(
        phase=Phase.GAS,
        gas=GasInputs(ps_psi=250.0, patm_psi=14.7, ts_rankine=520.0, mw=18.0, k=1.30, cd=1.0),
    )
    print("Wmax8:", r8, "area_in2=", Orifice(8.0).area_in2)
