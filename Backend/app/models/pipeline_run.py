from datetime import datetime
from sqlalchemy import DateTime, Integer, Text, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class PipelineRun(Base):
    """PipelineRun model to audit execution of the data pipeline."""

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    total_products: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("total_products >= 0", name="chk_total_products_non_neg"),
        CheckConstraint("success_count >= 0", name="chk_success_count_non_neg"),
        CheckConstraint("failed_count >= 0", name="chk_failed_count_non_neg"),
        CheckConstraint("skipped_count >= 0", name="chk_skipped_count_non_neg"),
    )

    def __repr__(self) -> str:
        return f"<PipelineRun id={self.id} total={self.total_products}>"
