from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import erf, exp, isfinite, sqrt
from typing import Any, Dict, Optional, Literal, get_args


# -----------------------------
# Helpers
# -----------------------------
def _years_frac(start: date, end: date) -> float:
    """
    Year fraction similar to Excel FRAC.AÑO with basis 2 (Actual/Actual approximation).
    For engineering RBI work, this is typically sufficient.
    """
    if end < start:
        raise ValueError(f"end date {end} is before start date {start}")
    days = (end - start).days
    # Actual/365.25 approximation
    return days / 365.25


def _norm_cdf(x: float) -> float:
    """Standard normal CDF Φ(x) without scipy."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _safe_float(x: Any, name: str) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
    except Exception as e:
        raise TypeError(f"{name} must be a number (got {type(x)}).") from e
    if not isfinite(v):
        raise ValueError(f"{name} must be finite (got {v}).")
    return v


def _clip_min(x: float, xmin: float) -> float:
    return x if x >= xmin else xmin


def _clip_nonneg(x: float) -> float:
    return x if x >= 0.0 else 0.0

# -----------------------------
# Inputs
# -----------------------------
@dataclass(frozen=True)
class ThinningInspectionEffectiveness:
    """
    API 581 uses A/B/C/D effectiveness bins.
    N_* are the number of past inspections by effectiveness.
    """
    N_A: int = 0
    N_B: int = 0
    N_C: int = 0
    N_D: int = 0

@dataclass(frozen=True)
class ThinningPriorsAndConditionals:
    """
    Prp1/2/3: prior probabilities from API 581 Table 4.5 (or your selected policy)
    C0p{1,2,3}{A,B,C,D}: conditional probabilities from API 581 Table 4.6
    """
    Prp1: float
    Prp2: float
    Prp3: float

    C0p1A: float
    C0p1B: float
    C0p1C: float
    C0p1D: float

    C0p2A: float
    C0p2B: float
    C0p2C: float
    C0p2D: float

    C0p3A: float
    C0p3B: float
    C0p3C: float
    C0p3D: float


@dataclass(frozen=True)
class ThinningFactors:
    """
    API 581 Step 13 adjustment factors:
    - F_OM: online monitoring
    - F_IP: injection/mix point
    - F_DL: dead-leg
    """
    F_OM: float = 1.0
    F_IP: float = 1.0
    F_DL: float = 1.0


DAMAGE_MECANISM_OPTIONS = Literal["581-High Temperature Oxidation", 
                                  "581-Cooling Water Corrosion",
                                  "581-High Temperature H2/H2S Corrosion",
                                  "581-Amine Corrosion",
                                  "581-Hydrofluoric Acid Corrosion",
                                  "581-Sulfuric Acid Corrosion",
                                  "581-Hydrochloric Acid Corrosion",
                                  "581-Acid Sour Water Corrosion",
                                  "581-High Temperature Sulfidic and Naphthenic Acid",
                                  "581-Alkaline Sour Water Corrosion",
                                  "581-Soil Side Corrosion",
                                  "581-CO2 Corrosion",
                                  "581-Thinning Damage"]

GOVERNING_THINNING_MECHANISM_OPTIONS = Literal["Ammonium Bisulfide Corrosion (Alkaline SourWater)",
                                               "Cooling Water Corrosion",
                                               "Dealloying",
                                               "Decarburization",
                                               "Erosion/Erosion-Corrosion",
                                               "Flue Gas Dew Point Corrosion",
                                               "Fuel Ash Corrosion",
                                               "Galvanic Corrosion",
                                               "Graphitic Corrosion",
                                               "High Temperature H2/H2S",
                                               "HCl Acid Corrosion",
                                               "Ammonium Chloride Corrosion",
                                               "Hydrofluoric Acid Corrosion",
                                               "Oxidation",
                                               "Metal Dusting",
                                               "Microbiologically Induced Corrosion (MIC)",
                                               "Naphthenic Acid Corrosion (NAC)",
                                               "Nitriding",
                                               "Phenol (Carbonic Acid) Corrosion",
                                               "Phosphoric Acid Corrosion",
                                               "Soil Corrosion",
                                               "Sour Water Corrosion (Acidic)",
                                               "Amine Corrosion",
                                               "Sulfidation",
                                               "Sulfuric Acid Corrosion",
                                               "Other",
                                               "Aqueous Organic Acid Corrosion",
                                               "Boiler Water Condensate (BW/C) Corrosion",
                                               "Carburization",
                                               "Caustic Corrosion",
                                               "Cavitation",
                                               "CO2 Corrosion"]

CORROSION_OPTIONS = Literal["Calculated Rate", 
                            "Estimated Rate", 
                            "Short Term Avg", 
                            "Long Term Avg",
                            "Measured Corrosion Rate"]

THINNING_TYPES = Literal["General", "Localized", "Pitting"]

@dataclass(frozen=True)
class ThinningInputs:

    dm_thinning: DAMAGE_MECANISM_OPTIONS
    governing_thinning_mechanism: GOVERNING_THINNING_MECHANISM_OPTIONS
    select_type_corrosion_rate: CORROSION_OPTIONS
    select_type_corrosion_rate_cladding: CORROSION_OPTIONS
    thinning_type: THINNING_TYPES
    
    # Dates
    install_date: date             
    inspection_date: date
    last_thickness_date: Optional[date] = None

    cladding_present: bool = False
    liner_present: bool = False

    long_term_avg_corr_rate: Optional[float] = None  #
    short_term_avg_corr_rate: Optional[float] = None #
    estimated_corr_rate: Optional[float] = None      #
    measured_corr_rate: Optional[float] = None      #
    calculated_corr_rate: Optional[float] = None #

    long_term_avg_corr_rate_cladding: Optional[float] = None  #
    short_term_avg_corr_rate_cladding: Optional[float] = None #
    estimated_corr_rate_cladding: Optional[float] = None      #
    measured_corr_rate_cladding: Optional[float] = None      #
    calculated_corr_rate_cladding: Optional[float] = None #

    # Thicknesses
    t: float = 0.0                 # is the furnished thickness of the component calculated as the sum of the base material and cladding thickness
    t_rdi: Optional[float] = None  # the furnished thickness, t, or measured thickness reading from previous inspection
    tc: float = 0.0                # is the minimum structural thickness of the component base material,
    tmin: Optional[float] = None   # minimum required thickness (from code/FFS). If None, must supply and use Eq 2.15.
    tcm: float = 0.0               # liner thickness (0 if none); not currently used in age_rc but can be added similarly to cladding
    
    # Variables de Liner
    liner_type: Optional[str] = None
    install_liner_date: Optional[date] = None
    RL_exp_liner: float = 0.0  # Extraído de la Table 4.7
    F_LC: float = 1.0          # Extraído de la Table 4.8
    F_liner_OM: float = 1.0    # 0.1 si hay monitoreo efectivo, 1.0 si no

    # Corrosion rates
    Cr_bm: float = 0.0             # base material corrosion rate
    Cr_cm: float = 0.0             # cladding corrosion rate (0 if none)

    # Strength/stress
    YS: float = 0.0                # yield strength
    TS: float = 0.0                # tensile strength
    S: float = 0.0                 # allowable stress
    E: float = 1.0                 # weld joint efficiency

    # Optional pressure-based SRP (Eq. 2.15)
    P: Optional[float] = None
    D: Optional[float] = None
    alpha: Optional[float] = None  # shape factor

    # Inspection effectiveness counts
    insp: ThinningInspectionEffectiveness = ThinningInspectionEffectiveness()

    # Priors/conditionals
    probs: Optional[ThinningPriorsAndConditionals] = None

    # COVs (API 581 typical suggestions)
    COV_At: float = 0.20
    COV_Sf: float = 0.20
    COV_P: float = 0.05

    # Damage state multipliers (API 581)
    DS1: float = 1.0
    DS2: float = 2.0
    DS3: float = 4.0

    # Adjustment factors
    factors: ThinningFactors = ThinningFactors()

    def __post_init__(self):
        # Validación de Mecanismo
        allowed_dm = get_args(DAMAGE_MECANISM_OPTIONS)
        if self.dm_thinning not in allowed_dm:
            raise ValueError(f"Mecanismo inválido: '{self.dm_thinning}'")
        
        allowed_corrosion = get_args(CORROSION_OPTIONS)
        if self.select_type_corrosion_rate not in allowed_corrosion:
            raise ValueError(f"Corrosión inválida: '{self.select_type_corrosion_rate}'")
                       

# -----------------------------
# Main compute function
# -----------------------------
def compute_df_thinning(inp: ThinningInputs) -> Dict[str, Any]:
    """
    Compute API 581 Thinning Damage Factor (DF) step-by-step and return ALL intermediate variables.

    Notes:
    - Implements the structure shown in API 581 Section 4.5.7 (your screenshot).
    - Uses Eq. (2.10), (2.12)-(2.20) and the Bayesian inspection effectiveness portion (2.16)-(2.18).
    - You MUST provide inp.probs (priors + conditionals) to compute the posterior probabilities and betas.
      If not provided, the function will compute up to SRP and stop with placeholders for later steps.

    Returns:
      dict with:
        - inputs echo
        - step results (age, age_tk, age_rc, A_rt, FS_thin, SRP_thin, I1/I2/I3, P0p*, beta*, DFb, DF)
    """
    # --- Validate / normalize
    t = float(inp.t)
    if t <= 0:
        raise ValueError("t (furnished thickness) must be > 0")

    t_rdi = float(inp.t_rdi) if inp.t_rdi is not None else t
    if t_rdi <= 0:
        raise ValueError("t_rdi (last known thickness) must be > 0")

    tc = float(inp.tc or 0.0)
    if tc < 0:
        raise ValueError("tc (cladding thickness) must be >= 0")
            
    # if Cr_bm < 0 or Cr_cm < 0:
    #     raise ValueError("Corrosion rates must be >= 0")

    YS = float(inp.YS)
    TS = float(inp.TS)
    S = float(inp.S)
    E = float(inp.E)
    if any(v < 0 for v in (YS, TS, S)):
        raise ValueError("YS, TS, S must be >= 0")
    if E <= 0:
        raise ValueError("E must be > 0")

    # --- Step 1: age (years)
    age = _years_frac(inp.install_date, inp.inspection_date)

    # Calcular age_liner si el liner está presente
    age_liner = 0.0
    if inp.liner_present and inp.install_liner_date:
        age_liner = _years_frac(inp.install_liner_date, inp.inspection_date)

    # --- Step 2 - Determine corrosion rate

    Cr_bm = 0.0
    Cr_cm = 0.0

    # --- Step 3.1: age_tk and last thickness date handling
    if inp.last_thickness_date is None:
        last_thickness_date = inp.install_date
        age_tk = age
        used_default_last_thickness_date = True
    else:
        last_thickness_date = inp.last_thickness_date
        age_tk = _years_frac(inp.last_thickness_date, inp.inspection_date)
        used_default_last_thickness_date = False

    # --- Step 3.2: age_rc for cladding (Eq. 2.10) (liner not implemented here; can be added similarly)
    # If no cladding => age_rc = 0
    age_rc = 0.0
    
    if inp.cladding_present:
        tcm = float(inp.tcm)
        if tcm > 0:
            if Cr_cm > 0:
                age_rc = tcm / Cr_cm
            else:
                age_rc = float('inf')
        else:
            age_rc = 0.0
                 
    elif inp.liner_present:
        if inp.F_LC <= 0:
            raise ValueError("F_LC (Lining Condition) debe ser > 0")
        
        age_rc = max(((inp.RL_exp_liner - age_liner) / inp.F_LC) * inp.F_liner_OM, 0.0)
         
    # --- Step 5: A_rt (Eq. 2.12)
    A_rt = max(((Cr_bm) * (age_tk - age_rc)) / t_rdi, 0.0)
  
    # --- Step 6: flow stress FS_thin (Eq. 2.13)
    FS_thin = ((YS + TS) / 2.0) * E * 1.1

    # --- Step 7: SRP_thin
    # Prefer Eq 2.14 when tmin available; else Eq 2.15 with P,D,alpha.
    srp_method = None
    SRP_thin = None

    if inp.tmin is not None:
        tmin = float(inp.tmin)
        if tmin <= 0:
            raise ValueError("tmin must be > 0 if provided")
        srp_method = "Eq(2.14)"
        SRP_thin = (S * E / FS_thin) * (max(tmin, tc) / t_rdi) if FS_thin > 0 else float("inf")
    else:
        # Eq 2.15 requires P, D, alpha
        P = _safe_float(inp.P, "P")
        D = _safe_float(inp.D, "D")
        alpha = _safe_float(inp.alpha, "alpha")
        if P is None or D is None or alpha is None:
            srp_method = "Eq(2.14) required tmin OR provide P,D,alpha for Eq(2.15)"
            SRP_thin = None
        else:
            if alpha <= 0:
                raise ValueError("alpha must be > 0")
            if FS_thin <= 0:
                raise ValueError("FS_thin computed <= 0; check YS/TS/E inputs.")
            srp_method = "Eq(2.15)"
            SRP_thin = (P * D) / (alpha * FS_thin * t_rdi)

    # Prepare output dict
    out: Dict[str, Any] = {
        "inputs": {
            "install_date": inp.install_date.isoformat(),
            "inspection_date": inp.inspection_date.isoformat(),
            "last_thickness_date": None if inp.last_thickness_date is None else inp.last_thickness_date.isoformat(),
            "t": t,
            "t_rdi": t_rdi,
            "tc": tc,
            "tmin": None if inp.tmin is None else float(inp.tmin),
            "Cr_bm": Cr_bm,
            "Cr_cm": Cr_cm,
            "YS": YS,
            "TS": TS,
            "S": S,
            "E": E,
            "P": inp.P,
            "D": inp.D,
            "alpha": inp.alpha,
            "N_A": int(inp.insp.N_A),
            "N_B": int(inp.insp.N_B),
            "N_C": int(inp.insp.N_C),
            "N_D": int(inp.insp.N_D),
            "COV_At": float(inp.COV_At),
            "COV_Sf": float(inp.COV_Sf),
            "COV_P": float(inp.COV_P),
            "DS1": float(inp.DS1),
            "DS2": float(inp.DS2),
            "DS3": float(inp.DS3),
            "F_OM": float(inp.factors.F_OM),
            "F_IP": float(inp.factors.F_IP),
            "F_DL": float(inp.factors.F_DL),
            "has_probs": inp.probs is not None,
        },
        "step_1": {
            "age_years": age,
        },
        "step_3": {
            "used_default_last_thickness_date": used_default_last_thickness_date,
            "effective_last_thickness_date": last_thickness_date.isoformat(),
            "age_tk_years": age_tk,
            "age_rc_years": age_rc,
        },
        "step_5": {
            "A_rt": A_rt,
            "equation": "Eq(2.12)",
        },
        "step_6": {
            "FS_thin": FS_thin,
            "equation": "Eq(2.13)",
        },
        "step_7": {
            "SRP_thin": SRP_thin,
            "method": srp_method,
        },
        # Placeholders; filled if probs provided:
        "step_9": {},
        "step_10": {},
        "step_11": {},
        "step_12": {},
        "step_13": {},
    }

    # If we can't compute SRP, stop early with what we have
    if SRP_thin is None:
        out["status"] = "partial"
        out["message"] = (
            "Computed through Step 6. Step 7 SRP_thin missing: provide tmin (for Eq 2.14) "
            "or provide P, D, alpha (for Eq 2.15)."
        )
        return out

    # If priors/conditionals are missing, stop after SRP
    if inp.probs is None:
        out["status"] = "partial"
        out["message"] = (
            "Computed through Step 7. To compute Steps 9-13, provide priors (Prp1/2/3) "
            "and conditionals (C0p* A/B/C/D) from API 581 Tables 4.5 and 4.6."
        )
        return out

    probs = inp.probs
    N_A, N_B, N_C, N_D = inp.insp.N_A, inp.insp.N_B, inp.insp.N_C, inp.insp.N_D

    # --- Step 9: I1, I2, I3 (Eq. 2.16)
    # I1 = Prp1 * (C0p1A^N_A) * (C0p1B^N_B) * (C0p1C^N_C) * (C0p1D^N_D)
    I1 = probs.Prp1 * (probs.C0p1A ** N_A) * (probs.C0p1B ** N_B) * (probs.C0p1C ** N_C) * (probs.C0p1D ** N_D)
    I2 = probs.Prp2 * (probs.C0p2A ** N_A) * (probs.C0p2B ** N_B) * (probs.C0p2C ** N_C) * (probs.C0p2D ** N_D)
    I3 = probs.Prp3 * (probs.C0p3A ** N_A) * (probs.C0p3B ** N_B) * (probs.C0p3C ** N_C) * (probs.C0p3D ** N_D)

    out["step_9"] = {
        "I1": I1,
        "I2": I2,
        "I3": I3,
        "equation": "Eq(2.16)",
    }

    # --- Step 10: posterior probabilities (Eq. 2.17)
    denom = I1 + I2 + I3
    if denom <= 0:
        raise ValueError("Invalid posterior normalization: I1+I2+I3 <= 0. Check priors/conditionals and N_*.")

    P0p1 = I1 / denom
    P0p2 = I2 / denom
    P0p3 = I3 / denom

    out["step_10"] = {
        "P0p1": P0p1,
        "P0p2": P0p2,
        "P0p3": P0p3,
        "equation": "Eq(2.17)",
    }

    # --- Step 11: betas (Eq. 2.18)
    # beta_i = (1 - DS_i*A_rt - SRP) / sqrt( DS_i^2*A_rt^2*COV_At^2 + (1-DS_i*A_rt)^2*COV_Sf^2 + (SRP^2)*COV_P^2 )
    COV_At = float(inp.COV_At)
    COV_Sf = float(inp.COV_Sf)
    COV_P = float(inp.COV_P)

    def _beta(DS: float) -> float:
        num = 1.0 - (DS * A_rt) - SRP_thin
        den = sqrt(
            (DS ** 2) * (A_rt ** 2) * (COV_At ** 2)
            + ((1.0 - DS * A_rt) ** 2) * (COV_Sf ** 2)
            + ((SRP_thin ** 2) * (COV_P ** 2))
        )
        if den <= 0:
            raise ValueError("Beta denominator <= 0. Check COVs and inputs.")
        return num / den

    beta1 = _beta(inp.DS1)
    beta2 = _beta(inp.DS2)
    beta3 = _beta(inp.DS3)

    out["step_11"] = {
        "beta1": beta1,
        "beta2": beta2,
        "beta3": beta3,
        "equation": "Eq(2.18)",
        "DS1": float(inp.DS1),
        "DS2": float(inp.DS2),
        "DS3": float(inp.DS3),
    }

    # --- Step 12: base DF (Eq. 2.19)
    # DFb_thin = [ P0p1*Phi(-beta1) + P0p2*Phi(-beta2) + P0p3*Phi(-beta3) ] / 1.56E-04
    Phi_m_b1 = _norm_cdf(-beta1)
    Phi_m_b2 = _norm_cdf(-beta2)
    Phi_m_b3 = _norm_cdf(-beta3)

    DFb = (P0p1 * Phi_m_b1 + P0p2 * Phi_m_b2 + P0p3 * Phi_m_b3) / 1.56e-04

    out["step_12"] = {
        "Phi(-beta1)": Phi_m_b1,
        "Phi(-beta2)": Phi_m_b2,
        "Phi(-beta3)": Phi_m_b3,
        "DFb_thin": DFb,
        "equation": "Eq(2.19)",
        "denominator_constant": 1.56e-04,
    }

    # --- Step 13: final DF (Eq. 2.20)
    F_OM = float(inp.factors.F_OM)
    F_IP = float(inp.factors.F_IP)
    F_DL = float(inp.factors.F_DL)

    if F_OM <= 0:
        raise ValueError("F_OM must be > 0")
    if F_IP <= 0 or F_DL <= 0:
        raise ValueError("F_IP and F_DL must be > 0")

    DF = max((DFb * F_IP * F_DL) / F_OM, 0.1)

    out["step_13"] = {
        "DF_thin": DF,
        "equation": "Eq(2.20)",
        "F_OM": F_OM,
        "F_IP": F_IP,
        "F_DL": F_DL,
        "min_df": 0.1,
    }

    out["status"] = "ok"
    return out


