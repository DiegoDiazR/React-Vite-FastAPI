from __future__ import annotations

from datetime import date
from typing import Any, Optional

from app.calculations.thinning_calc_df import (
    ThinningInputs,
    ThinningInspectionEffectiveness,
    ThinningFactors,
)
from app.calculations.thinning_presets import build_thinning_probabilities


def _as_date(x: Any) -> Optional[date]:
    if x is None or x == "":
        return None
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x))


def _as_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    if x is None or x == "":
        return default
    return float(x)


def _as_int(x: Any, default: int = 0) -> int:
    if x is None or x == "":
        return default
    return int(float(x))


def build_thinning_inputs_from_rows(
    *,
    comp: dict,
    analysis: dict,
    dm: dict,
    confidence: str = "medium",
) -> ThinningInputs:
    # --- Dates
    install_date = _as_date(comp.get("rbi_comp_comp_start_date"))
    inspection_date = _as_date(analysis.get("analysis_date"))
    last_thickness_date = _as_date(dm.get("dm_thinning_last_know_insp_date"))

    if install_date is None or inspection_date is None:
        raise ValueError("Faltan fechas: rbi_comp_comp_start_date y/o analysis_date")

    # --- Thickness
    t = _as_float(comp.get("rbi_comp_nom_thk"))
    if t is None or t <= 0:
        raise ValueError("Falta rbi_comp_nom_thk (t) o es <= 0")

    t_rdi = _as_float(dm.get("dm_thinning_last_know_thk"), default=t)
    if t_rdi is None or t_rdi <= 0:
        raise ValueError("t_rdi inválido (dm_thinning_last_know_thk / rbi_comp_nom_thk)")

    tc = _as_float(comp.get("rbi_comp_furn_cladd_thk"), default=0.0) or 0.0
    if tc < 0:
        raise ValueError("tc (rbi_comp_furn_cladd_thk) no puede ser negativo")

    # Tmin priority: analysis override -> component specified
    tmin = _as_float(analysis.get("rbi_581_ove_min_req_thk"))
    if tmin is None:
        tmin = _as_float(comp.get("rbi_comp_min_thk"))
    if tmin is None or tmin <= 0:
        raise ValueError("Falta tmin (>0): rbi_581_ove_min_req_thk o rbi_comp_min_thk")

    # --- Corrosion rates
    Cr_bm = _as_float(dm.get("dm_thinning_base_mat_corr_rate"), default=0.0) or 0.0
    Cr_cm = _as_float(dm.get("dm_thinning_cladd_mat_corr_rate"), default=0.0) or 0.0
    if Cr_bm < 0 or Cr_cm < 0:
        raise ValueError("Cr_bm / Cr_cm no pueden ser negativas")

    # --- Stress / strength (por ahora obligatorios)
    YS = _as_float(comp.get("rbi_comp_smys"))
    if YS is None or YS <= 0:
        raise ValueError("Falta rbi_comp_smys (YS) o es <= 0")

    TS = _as_float(comp.get("rbi_comp_uts"))
    if TS is None or TS <= 0:
        raise ValueError("Falta rbi_comp_uts (TS) o es <= 0")

     
    S = _as_float(analysis.get("rbi_581_allowable_stress"))
    E = _as_float(comp.get("rbi_comp_weldj_eff"), default=1.0) or 1.0

    if YS is None or TS is None or S is None or YS <= 0 or TS <= 0 or S <= 0:
        raise ValueError("YS, TS y rbi_581_allowable_stress deben ser > 0 (define columnas o lookup)")

    # --- Inspection effectiveness counts
    insp = ThinningInspectionEffectiveness(
        N_A=_as_int(dm.get("dm_thinning_number_a_level_insp"), 0),
        N_B=_as_int(dm.get("dm_thinning_number_b_level_insp"), 0),
        N_C=_as_int(dm.get("dm_thinning_number_c_level_insp"), 0),
        N_D=_as_int(dm.get("dm_thinning_number_d_level_insp"), 0),
    )

    # --- Step 13 factors (policy defaults)
    online = bool(dm.get("dm_thinning_online_moni_flag") or False)
    inj = bool(dm.get("dm_thinning_injection_point_flag") or False)
    dl = bool(dm.get("dm_thinning_deadleg_flag") or False)

    F_OM = 0.9 if online else 1.0
    F_IP = 1.2 if inj else 1.0
    F_DL = 1.3 if dl else 1.0

    factors = ThinningFactors(F_OM=F_OM, F_IP=F_IP, F_DL=F_DL)

    # --- Probabilities
    probs = build_thinning_probabilities(confidence=confidence)

    return ThinningInputs(
        install_date=install_date,
        inspection_date=inspection_date,
        last_thickness_date=last_thickness_date,
        t=float(t),
        t_rdi=float(t_rdi),
        tc=float(tc),
        tmin=float(tmin),
        Cr_bm=float(Cr_bm),
        Cr_cm=float(Cr_cm),
        YS=float(YS),
        TS=float(TS),
        S=float(S),
        E=float(E),
        insp=insp,
        probs=probs,
        factors=factors,
    )
