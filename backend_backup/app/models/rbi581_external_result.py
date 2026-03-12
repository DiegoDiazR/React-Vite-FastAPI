from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class RBI581ExternalResult(Base):
    __tablename__ = "rbi_581_external_results"

    external_result_pk: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Relaciones obligatorias
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

    # Referencia al mecanismo de daño específico (CUI / Atmosférico)
    dm_external_pk: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_ExternalDamage.dm_extdamage_pk", ondelete="CASCADE"),   
        nullable=False,
        index=True,
    )

    # Resultados técnicos del motor de cálculo
    df_external: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Estado y trazabilidad
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    ) # <--- Aquí estaba el error de paréntesis cerrado
    
    # Almacena el diccionario completo de pasos del cálculo (Step 1 a 18)
    trace_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Restricción: Un solo resultado por mecanismo en cada análisis
    __table_args__ = (
        UniqueConstraint("analysis_pk", "dm_external_pk", name="uq_external_result_per_dm"),
    )