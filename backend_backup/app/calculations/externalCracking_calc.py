# app/calculations/externalCracking_calc.py

from dataclasses import dataclass
from datetime import date
from typing import Literal, Dict, Any, Optional, get_args
from .externalCracking_presets import get_external_cracking_susceptibility, get_scc_base_df
from .externalCracking_tables import SEVERITY_INDEX_TABLE

DAMAGE_MECANISM_OPTIONS = Literal["581-Austenitic Component Atmospheric Cracking", 
                                  "581-Austenitic Component Cracking Under Insulation"]
SUSCEPTIBILITY_OPTIONS = Literal["Estimated", "Calculated", "Measured"]
SUSCEPTIBILITY_VALUES = Literal["None_", "Low", "Medium", "High"]
COATING_QUALITY = Literal["No coating or primer only", "Medium", "High"]

@dataclass
class ExternalCrackingInputs:
    # mechanism: DAMAGE_MECANISM_OPTIONS
    # susceptibility_type: SUSCEPTIBILITY_OPTIONS
    # susceptibility: Optional[SUSCEPTIBILITY_VALUES]
    # coating_quality: Optional[COATING_QUALITY]
    # temp_op: float
    # driver: str
    # calculation_date: date
    # last_insp_date: date
    
    # coating_present: bool = False
    # coating_install_date: date
    # anticipated_coating_life: float  
    # coating_failed_at_insp: bool = False

    # # Ajustes CUI
    # complexity: str = "Average"
    # insulation: str = "Average"
    # chloride_free: bool = False

    # # Inspection
    # highest_effectiveness: str = "E"
    # number_of_inspections: int = 0


    mechanism: DAMAGE_MECANISM_OPTIONS
    susceptibility_type: SUSCEPTIBILITY_OPTIONS
    # susceptibility: Optional[SUSCEPTIBILITY_VALUES] = None
    # coating_quality: Optional[COATING_QUALITY] = None
    temp_op: float                    
    driver: str
    calculation_date: date
    last_insp_date: date
    coating_install_date: date
    anticipated_coating_life: float

    # --- BLOQUE 2: CAMPOS OPCIONALES (Con "=") ---
    susceptibility: Optional[SUSCEPTIBILITY_VALUES] = None
    coating_quality: Optional[COATING_QUALITY] = None
    coating_present: bool = False
    coating_failed_at_insp: bool = False
    complexity: str = "Average"
    insulation: str = "Average"
    chloride_free: bool = False
    highest_effectiveness: str = "E"
    number_of_inspections: int = 0

    def __post_init__(self):
        # Validación de Mecanismo
        allowed_dm = get_args(DAMAGE_MECANISM_OPTIONS)
        if self.mechanism not in allowed_dm:
            raise ValueError(f"Mecanismo inválido: '{self.mechanism}'")
        
        # Validación de Susceptibilidad Manual [cite: 40, 181]
        # Si es medido/estimado, no puede ser "None_"
        if self.susceptibility_type in ("Measured", "Estimated"):
            if self.susceptibility == None:
                raise ValueError(
                    f"Debe proporcionar un nivel (None, Low, Medium o High)."
                )
        
            
def compute_df_external_cracking(inp: ExternalCrackingInputs) -> Dict[str, Any]:
    trace = {}
    
    # STEP 1: Susceptibilidad [cite: 105, 246]

    if inp.susceptibility_type == "Calculated":
        suscept = get_external_cracking_susceptibility(
            inp.mechanism, 
            inp.temp_op, 
            inp.driver, 
            inp.complexity, 
            inp.insulation, 
            inp.chloride_free
            )
    else:
        suscept = inp.susceptibility
        
    trace["step_1"] = {"susceptibility_type": inp.susceptibility_type, 
                       "susceptibility": suscept}
    
    if suscept == "None_":
        return {"df_cracking": 1.0, "status": "ok", "trace": trace}

    # STEP 2: Severity Index
    svi = SEVERITY_INDEX_TABLE.get(suscept, 0)
    trace["step_2"] = {"SVI": svi}

    # STEPS 3-7: Effective Age [cite: 66-67, 208-209]
    age_crack = (inp.calculation_date - inp.last_insp_date).days / 365.25

    if inp.coating_present == False:
        coat_adj = 0.0
        
    else:
        age_coat = (inp.calculation_date - inp.coating_install_date).days / 365.25
        coat_adj = min(inp.anticipated_coating_life, age_coat)
        Cage = inp.anticipated_coating_life
        if age_crack >= age_coat: 
            coat_adj = min(Cage, age_coat)
        else:
            if inp.coating_failed_at_insp:
                coat_adj = 0.0
            else:
             term1 = min(Cage, age_coat)
             term2 = min(Cage, age_coat - age_crack)
             coat_adj = term1 - term2
            
    eff_age = max(age_crack - coat_adj, 0.0)

    trace["steps_3_7"] = {"age_crack": round(age_crack, 2), "eff_age": round(eff_age, 2)}

    # STEP 9: Base DF
    dfb = get_scc_base_df(svi, inp.highest_effectiveness, inp.number_of_inspections)
    trace["step_9"] = {"DfB": dfb}

    # STEP 10: Escalación 
    # Df = min( DfB * (max(age, 1.0))^1.1, 5000 )
    df_final = min(dfb * (max(eff_age, 1.0) ** 1.1), 5000.0)
    trace["step_10"] = {"df_final": round(df_final, 2)}

    return {
        "df_cracking": round(df_final, 2),
        "dfb_cracking": dfb,
        "trace": trace,
        "status": "ok"
    }
