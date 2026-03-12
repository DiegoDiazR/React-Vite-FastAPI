from datetime import date
from app.core.db import SessionLocal
from app.core.init_db import init_db

# Importa tus modelos reales
from app.models.asset import Asset
from app.models.asset import RBIComponent
from app.models.asset import RBI581Analysis
from app.models.asset import DMThinning

from app.crud.thinning_result import upsert_thinning_result


def main():
    init_db()
    db = SessionLocal()

    # 1) Asset mínimo
    asset = db.query(Asset).filter(Asset.asset_id == "A-001").one_or_none()
    if asset is None:
        asset = Asset(asset_id="A-001")
        db.add(asset)
        db.commit()
        db.refresh(asset)
        db.add(asset)
        db.commit()
        db.refresh(asset)

    # 2) Componente mínimo
    comp = (
        db.query(RBIComponent)
        .filter(
            RBIComponent.asset_pk == asset.asset_pk,
            RBIComponent.rbi_comp_comp == "PIPE-001",
            RBIComponent.rbi_comp_comp_type == "PIPE",
            ).one_or_none()
            )
    
    if comp is None:
        comp = RBIComponent(
        asset_pk=asset.asset_pk,
        rbi_comp_comp="PIPE-001",
        rbi_comp_comp_type="PIPE",
        rbi_comp_comp_start_date=date(1990, 1, 1),
        rbi_comp_nom_thk=0.235,
        rbi_comp_min_thk=0.110,
        rbi_comp_weldj_eff=1.0,
        rbi_comp_smys=35.0,
        rbi_comp_uts=60.0,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)


    # 3) Analysis mínimo
    analysis = RBI581Analysis(
        component_pk=comp.component_pk,
        analysis_date=date(2023, 1, 1),
        rbi_581_analysis_unique_id="AN-001",
        rbi_581_scenario_id="SCN-001",
        rbi_581_allowable_stress=20.0,
        rbi_581_ove_min_req_thk=0.110,
        )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # 4) DM Thinning mínimo (según tu clase)
    dm = DMThinning(
        analysis_pk=analysis.analysis_pk,
        dm_thinning_dm="THINNING",
        location_key="GLOBAL",
        dm_thinning_last_know_insp_date=None,
        dm_thinning_last_know_thk=0.235,
        dm_thinning_base_mat_corr_rate=0.000090,
        dm_thinning_cladd_mat_corr_rate=0.0,
        dm_thinning_number_a_level_insp=0,
        dm_thinning_number_b_level_insp=1,
        dm_thinning_number_c_level_insp=0,
        dm_thinning_number_d_level_insp=0,
        dm_thinning_online_moni_flag=False,
        dm_thinning_injection_point_flag=False,
        dm_thinning_deadleg_flag=False,
    )
    db.add(dm)
    db.commit()
    db.refresh(dm)

    # 5) Trace dummy (o luego conectamos el cálculo real)
    trace = {
        "status": "ok",
        "step_12": {"DFb_thin": 10.0},
        "step_13": {"DF_thin": 12.3},
    }

    # 6) Guardar resultado
    res = upsert_thinning_result(
        db,
        asset_pk=asset.asset_pk,
        component_pk=comp.component_pk,
        analysis_pk=analysis.analysis_pk,
        dm_thinning_pk=dm.dm_thinning_pk,
        df_thin=trace["step_13"]["DF_thin"],
        dfb_thin=trace["step_12"]["DFb_thin"],
        trace=trace,
    )

    print("✅ Saved thinning result:", res.thinning_result_pk, res.df_thin, res.status)

    db.close()


if __name__ == "__main__":
    main()
