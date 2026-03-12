from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import erf, isfinite, sqrt
from typing import Any, Dict, Optional, Literal, get_args

# -----------------------------
# Helpers (Misma estructura que thinning_calc_df.py)
# -----------------------------
def _years_frac(start: date, end: date) -> float:
    """Fracción de año (Actual/365.25)."""
    if end < start:
        raise ValueError(f"La fecha final {end} es anterior a la inicial {start}")
    return (end - start).days / 365.25


def _norm_cdf(x: float) -> float:
    """CDF normal estándar Φ(x)."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _safe_float(x: Any, name: str) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
    except Exception as e:
        raise TypeError(f"{name} debe ser un número (got {type(x)}).") from e
    if not isfinite(v):
        raise ValueError(f"{name} debe ser finito (got {v}).")
    return v


# -----------------------------
# Inputs (Adaptados de DF - CUI.pdf)
# -----------------------------
@dataclass(frozen=True)
class CUIInspectionEffectiveness:
    """Pasos 14: Cantidad de inspecciones por categoría[cite: 97, 129]."""
    N_A: int = 0
    N_B: int = 0
    N_C: int = 0
    N_D: int = 0


@dataclass(frozen=True)
class CUIPriorsAndConditionals:
    """Paso 15: Probabilidades previas y condicionales (Tablas 4.5 y 4.6)[cite: 98]."""
    Prp1: float
    Prp2: float
    Prp3: float

    C0p1A: float; C0p1B: float; C0p1C: float; C0p1D: float
    C0p2A: float; C0p2B: float; C0p2C: float; C0p2D: float
    C0p3A: float; C0p3B: float; C0p3C: float; C0p3D: float


@dataclass(frozen=True)
class CUIAdjustmentFactors:
    """Paso 4: Factores de ajuste para CUI (Eq. 2.D.14)[cite: 25, 26, 127]."""
    F_INS: float = 0.0  # Tipo de aislamiento (Tabla 2.D.3.3)
    F_CM: float = 0.0   # Complejidad (0.75, 1.0, 1.25)
    F_IC: float = 0.0   # Condición del aislamiento (1.25, 1.0, 0.75)
    F_EQ: float = 0.0   # Diseño/Fabricación (1 o 2)
    F_IF: float = 0.0   # Interfaz suelo/agua (1 o 2)

CORROSION_OPTIONS = Literal["Estimated", "Calculated", "Measured"]
DAMAGE_MECANISM_OPTIONS = Literal["581-Ferritic Component Atmospheric Corrosion", "581-Ferritic Component Corrosion UnderInsulation"]
EXTERNAL_THINNING_TYPES = Literal["General", "Localized", "Pitting"]
COATING_QUALITY = Literal["No coating or primer only", "Medium", "High"]

@dataclass(frozen=True)
class CUIInputs:
    # --- 1. CAMPOS SIN VALOR POR DEFECTO (PRIMERO) ---
    dm_ext_dm: DAMAGE_MECANISM_OPTIONS
    select_ext_corrosion: CORROSION_OPTIONS
    ext_thinning_type: EXTERNAL_THINNING_TYPES
    ext_coating_quality: COATING_QUALITY
    install_date: date
    calculation_date: date
    coating_install_date: date
        
    # --- 2. CAMPOS CON VALOR POR DEFECTO (DESPUÉS) ---
    last_thickness_date: Optional[date] = None
    base_mat_measured_rate: float = 0.0
    t: float = 0.0
    t_rde_measured: Optional[float] = None
    tmin: Optional[float] = None
    tc: float = 0.0
    Le: float = 0.0
    CrB: float = 0.0
    C_age: float = 0.0
    coating_failed_at_insp: bool = False
    YS: float = 0.0
    TS: float = 0.0
    S: float = 0.0
    E: float = 1.0

    # Objetos y parámetros opcionales
    P: Optional[float] = None
    D: Optional[float] = None
    alpha: Optional[float] = None
    insp: CUIInspectionEffectiveness = CUIInspectionEffectiveness()
    probs: Optional[CUIPriorsAndConditionals] = None
    factors: CUIAdjustmentFactors = CUIAdjustmentFactors()

    COV_At: float = 0.20
    COV_Sf: float = 0.20
    COV_P: float = 0.05

    def __post_init__(self):
        # Validaciones de Literal
        allowed_dm = get_args(DAMAGE_MECANISM_OPTIONS)
        if self.dm_ext_dm not in allowed_dm:
            raise ValueError(f"Mecanismo inválido: '{self.dm_ext_dm}'")

        allowed_corrosion = get_args(CORROSION_OPTIONS)
        if self.select_ext_corrosion not in allowed_corrosion:
            raise ValueError(f"Corrosión inválida: '{self.select_ext_corrosion}'")
        
        # Validación de tasa mayor a 0 si se selecciona manual
        if self.select_ext_corrosion in ("Measured", "Estimated"):
            if self.base_mat_measured_rate <= 0:
                raise ValueError(f"Debe proporcionar una tasa mayor a 0 para {self.select_ext_corrosion}")

        # Validación de factores cuando el cálculo es automático ("Calculated")
        if self.select_ext_corrosion == "Calculated":
            # Factores comunes para AMBOS mecanismos (Eq. 2.D.14) [cite: 26, 40, 41]
            if self.factors.F_EQ <= 0 or self.factors.F_IF <= 0:
                raise ValueError("Debe proporcionar factores de Diseño (F_EQ) e Interfase (F_IF) validos.")
            
            # Factores EXCLUSIVOS para Corrosión Bajo Aislamiento (CUI) [cite: 26, 28, 30, 37]
            if self.dm_ext_dm == "581-Ferritic Component Corrosion UnderInsulation":
                if self.factors.F_INS <= 0 or self.factors.F_CM <= 0 or self.factors.F_IC <= 0:
                    raise ValueError(
                        "Para CUI, los factores de Aislamiento (F_INS), Complejidad (F_CM) "
                        "y Condición (F_IC) deben ser validos."
                        ) 
        
        allowed_quality = get_args(COATING_QUALITY)
        if self.ext_coating_quality not in allowed_quality:
            raise ValueError(f"Calidad de recubrimiento inválida: '{self.ext_coating_quality}'")

# -----------------------------
# Main compute function
# -----------------------------
def compute_df_cui(inp: CUIInputs) -> Dict[str, Any]:
    """
    Calcula el Damage Factor por CUI siguiendo API 581 Annex 2.D.
    Misma estructura que compute_df_thinning.
    """
    # --- Paso 1: t y age total [cite: 15]
    t = float(inp.t)
    age_total = _years_frac(inp.install_date, inp.calculation_date)

    # --- Paso 4: Tasa de corrosión final (Eq. 2.D.14) [cite: 25, 26]
       
    if inp.select_ext_corrosion in ("Measured", "Estimated"):
        Cr = inp.base_mat_measured_rate
    else: 
        # Cálculo según mecanismo seleccionado [cite: 26, 40, 41]
        if inp.dm_ext_dm == "581-Ferritic Component Corrosion UnderInsulation":
            # Aplica todos los factores de CUI [cite: 26, 28, 140]
            Cr = (inp.CrB * inp.factors.F_INS * inp.factors.F_CM * inp.factors.F_IC * max(inp.factors.F_EQ, inp.factors.F_IF))
        else:
            # Corrosión atmosférica (solo factores de diseño/interfase) [cite: 40, 41]
            Cr = inp.CrB * max(inp.factors.F_EQ, inp.factors.F_IF)

    # --- Paso 5: age_tke (tiempo desde última medición) [cite: 42, 44]
    if inp.last_thickness_date is None:
        last_thickness_date = inp.install_date
        age_tke = age_total
        t_rde_p = t
        t_rde = t_rde_p - inp.Le
    else:
        last_thickness_date = inp.last_thickness_date
        age_tke = _years_frac(inp.install_date, last_thickness_date)
        t_rde_p = inp.t_rde_measured if inp.t_rde_measured is not None else t
        t_rde = t_rde_p - inp.Le

    
    # --- Paso 6: age_coat [cite: 47, 48]
    age_coat = _years_frac(inp.coating_install_date, inp.calculation_date)

    # --- Paso 8: Coat_adj (Eq. 2.D.17 & 2.D.18) [cite: 57, 59, 65]
    Cage = inp.C_age
    if age_tke >= age_coat:
        # Eq (2.D.17)
        coat_adj = min(Cage, age_coat)
        coat_eq = "Eq(2.D.17)"
    else:
        # Eq (2.D.18) logic
        if inp.coating_failed_at_insp:
            coat_adj = 0.0
            coat_eq = "Eq(2.D.18)-Failed"
        else:
            term1 = min(Cage, age_coat)
            term2 = min(Cage, age_coat - age_tke)
            coat_adj = term1 - term2
            coat_eq = "Eq(2.D.18)-Intact"

    # --- Paso 9: age (tiempo efectivo de daño CUI) [cite: 67, 68]
    age_cui = max(age_tke - coat_adj, 0.0)

    # --- Paso 11: Art (Eq. 2.D.20) [cite: 72, 73]
    Art = (Cr * age_cui) / t_rde if t_rde > 0 else 0.0

    # --- Paso 12: FS_CUIF (Eq. 2.D.21) [cite: 74, 75]
    FS_cuif = ((inp.YS + inp.TS) / 2.0) * inp.E * 1.1

    # --- Paso 13: SRp_CUIF [cite: 79, 81, 89]
    srp_method = None
    SRp = None
    if inp.tmin is not None:
        tmin_eff = max(inp.tmin, inp.tc)
        SRp = (inp.S * inp.E / FS_cuif) * (tmin_eff / t_rde) if FS_cuif > 0 else 0.0
        srp_method = "Eq(2.D.22)"
    elif all(v is not None for v in (inp.P, inp.D, inp.alpha)):
        SRp = (inp.P * inp.D) / (inp.alpha * FS_cuif * t_rde)
        srp_method = "Eq(2.D.23)"

    # --- Estructura de salida similar a thinning_calc_df.py
    out: Dict[str, Any] = {
        "inputs": {**inp.__dict__},
        "step_1_to_4": {
            "Damage_Mechanism": inp.dm_ext_dm,
            "Tasa_Corr_Select": inp.select_ext_corrosion,
            "External_Thinning_Type": inp.ext_thinning_type,
            "age_total": age_total,
            "Cr_final": Cr,
            "equation_Cr": "Eq(2.D.14)"
        },
        "step_5_to_9": {
            "age_tke": age_tke,
            "age_coat": age_coat,
            "coat_qty": inp.ext_coating_quality,
            "coat_adj": coat_adj,
            "age_cui_damage": age_cui,
            "coat_equation": coat_eq
        },
        "step_11": {"Art": Art, "equation": "Eq(2.D.20)"},
        "step_12": {"FS_CUIF": FS_cuif, "equation": "Eq(2.D.21)"},
        "step_13": {"SRp_CUIF": SRp, "method": srp_method},
    }

    if SRp is None or inp.probs is None:
        out["status"] = "partial"
        return out

    # --- Pasos 15-16: Bayesian Posterior (Eq. 2.D.24 & 2.D.25) [cite: 98, 99, 100, 101]
    p = inp.probs
    n = inp.insp
    I1 = p.Prp1 * (p.C0p1A**n.N_A) * (p.C0p1B**n.N_B) * (p.C0p1C**n.N_C) * (p.C0p1D**n.N_D)
    I2 = p.Prp2 * (p.C0p2A**n.N_A) * (p.C0p2B**n.N_B) * (p.C0p2C**n.N_C) * (p.C0p2D**n.N_D)
    I3 = p.Prp3 * (p.C0p3A**n.N_A) * (p.C0p3B**n.N_B) * (p.C0p3C**n.N_C) * (p.C0p3D**n.N_D)
    
    denom = I1 + I2 + I3
    Pop1, Pop2, Pop3 = I1/denom, I2/denom, I3/denom
    out["step_14_16"] = {"Pop1": Pop1, "Pop2": Pop2, "Pop3": Pop3}

    # --- Paso 17: Betas (Eq. 2.D.26) [cite: 106, 107, 109]
    def _calc_beta(DS: float) -> float:
        num = 1.0 - (DS * Art) - SRp
        den = sqrt((DS**2 * Art**2 * inp.COV_At**2) + 
                   ((1.0 - DS * Art)**2 * inp.COV_Sf**2) + 
                   (SRp**2 * inp.COV_P**2))
        return num / den

    b1 = _calc_beta(1.0) # DS1 = 1
    b2 = _calc_beta(2.0) # DS2 = 2
    b3 = _calc_beta(4.0) # DS3 = 4
    out["step_17"] = {"beta1": b1, "beta2": b2, "beta3": b3}

    # --- Paso 18: DF final (Eq. 2.D.27) [cite: 111, 112]
    df_cui = (Pop1 * _norm_cdf(-b1) + Pop2 * _norm_cdf(-b2) + Pop3 * _norm_cdf(-b3)) / 1.56e-04
    out["step_18"] = {"DF_CUI": max(df_cui, 0.1)}
    
    out["status"] = "ok"
    return out