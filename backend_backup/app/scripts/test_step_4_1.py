# from app.calculations.cof_4_1_representative_fluid import step_4_1_determine_representative_fluid

import pprint
from app.calculations.cof_4_1_representative_fluid import step_4_1_determine_representative_fluid


def test_gas():
    print("\n=== PRUEBA DE GAS (C3-C4) A 300K ===")
    resultado = step_4_1_determine_representative_fluid(
        representative_fluid="C5",
        stored_phase="Liquid",
        temperature_k=300.0  # Añadimos temperatura
    )
    import pprint
    pprint.pprint(resultado.__dict__)

if __name__ == "__main__":
    test_gas()