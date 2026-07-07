from datetime import datetime
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class PipelineCache(Base):
    """PipelineCache model to track progress of sneaker data enrichment."""

    __tablename__ = "pipeline_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_key: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    brand_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # string representation of pipeline stages: cleaned, searched, imaged, described, uploaded, imported
    stage: Mapped[str] = mapped_column(String(50), nullable=False)

    # string representation of status: pending, success, failed, skipped
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )

    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PipelineCache key={self.product_key} status={self.status}>"
