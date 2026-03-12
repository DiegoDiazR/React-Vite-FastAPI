from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Integer, Float, String, DateTime, ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class RBI581ThinningResult(Base):
    __tablename__ = "rbi_581_thinning_results"

    thinning_result_pk: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

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

    dm_thinning_pk: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_thinning.dm_thinning_pk", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    df_thin: Mapped[float] = mapped_column(Float, nullable=False)
    dfb_thin: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    trace_json: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("analysis_pk", "dm_thinning_pk", name="uq_thinres_analysis_dm"),
    )