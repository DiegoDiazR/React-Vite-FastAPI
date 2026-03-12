from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class RBI581COFResult(Base):
    __tablename__ = "rbi_581_cof_results"

    cof_result_pk: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # --- Foreign Keys Jerárquicas ---
    asset_pk: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assets.asset_pk", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    component_pk: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rbi_components.component_pk", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    analysis_pk: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rbi_581_analysis.analysis_pk", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # El cálculo COF se basa en un escenario de Consecuencia específico
    consequence_pk: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rbi_581_consequence.consequence_pk", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Resultados Clave: ÁREAS (ft2) ---
    final_cmd_area_ft2: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_inj_area_ft2: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_cof_area_ft2: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Resultados Clave: FINANCIEROS ($) ---
    financial_total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_cmd_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_inj_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_env_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    financial_prod_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Resultados Clave: SEGURIDAD ---
    safety_population_density: Mapped[float | None] = mapped_column(Float, nullable=True)
    safety_personnel_affected: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Metadata de Ejecución ---
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Aquí guardaremos el JSON gigante con los logs, tasas de descarga por agujero, inventarios, etc.
    trace_json: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("analysis_pk", "consequence_pk", name="uq_cofres_analysis_conseq"),
    )