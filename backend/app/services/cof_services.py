from __future__ import annotations

from typing import Any, Dict

from app.calculations.cof_4_0_orchestrator import COFCalculator
from app.services.cof_builder import build_cof_inputs_from_rows


def _sa_to_dict(obj: Any) -> Dict[str, Any]:
    """Convierte un objeto de SQLAlchemy a diccionario."""
    if obj is None:
        return {}
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class COFService:
    @staticmethod
    def calculate_cof_from_rows(
        *,
        comp: dict,
        conseq: dict,
    ) -> Dict[str, Any]:
        """
        Construye los inputs, instancia el orquestador COF, ejecuta todos 
        los pasos y retorna un diccionario con los resultados finales.
        """
        # 1. Construir inputs validando los datos del diccionario
        inputs = build_cof_inputs_from_rows(comp=comp, conseq=conseq)

        # 2. Instanciar el Orquestador
        calc = COFCalculator(inputs)

        # 3. Ejecutar la secuencia de la metodología API 581
        calc.execute_step_4_1()
        calc.execute_step_4_2()
        calc.execute_step_4_3()
        calc.execute_step_4_4()
        calc.execute_step_4_5()
        calc.execute_step_4_6()
        calc.execute_step_4_7()
        
        calc.execute_step_4_8()
        calc.execute_step_4_9()
        calc.execute_step_4_10()
        
        # 4. Obtener resultados consolidados
        areas = calc.execute_final_consequence()  # 4.11
        fin = calc.execute_step_4_12()            # 4.12
        safe = calc.execute_step_4_13()           # 4.13

        # 5. Formatear la salida
        return {
            "areas": {
                "final_cmd_area_ft2": areas.get("final_cmd_area_ft2"),
                "final_inj_area_ft2": areas.get("final_inj_area_ft2"),
                "final_cof_area_ft2": areas.get("final_cof_area_ft2"),
            },
            "financial": {
                "total_cost": fin.FC_f_total if fin else 0.0,
                "cmd_cost": fin.FC_f_cmd if fin else 0.0,
                "inj_cost": fin.FC_f_inj if fin else 0.0,
                "env_cost": fin.FC_f_environ if fin else 0.0,
                "prod_cost": fin.FC_f_prod if fin else 0.0,
            },
            "safety": {
                "population_density": safe.popdens if safe else 0.0,
                "personnel_affected": safe.c_f_inj if safe else 0.0,
            },
            "logs": calc.logs, # Muy útil para debugear el cálculo en el frontend
        }

    @staticmethod
    def calculate_cof_from_models(
        *,
        comp_obj: Any,
        conseq_obj: Any,
    ) -> Dict[str, Any]:
        """
        Recibe objetos SQLAlchemy, los convierte a dict, y reutiliza calculate_cof_from_rows.
        """
        return COFService.calculate_cof_from_rows(
            comp=_sa_to_dict(comp_obj),
            conseq=_sa_to_dict(conseq_obj),
        )