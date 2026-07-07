from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String,
    DateTime,
    Numeric,
    Boolean,
    Text,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Sneaker(Base):
    """Sneaker catalog model representing a unique sneaker product."""

    __tablename__ = "sneakers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )

    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str] = mapped_column(String(300), nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)  # 'men', 'women', 'unisex'
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    material: Mapped[str] = mapped_column(String(150), nullable=False)
    price_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    search_query_used: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="sneakers")
    category: Mapped["Category"] = relationship(
        "Category", back_populates="sneakers"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "brand_id",
            "model_name",
            "category_id",
            "gender",
            "color",
            "material",
            name="uq_sneakers_dedup",
        ),
        CheckConstraint("price_usd >= 0", name="chk_price_positive"),
        CheckConstraint(
            "length(display_name) > 0", name="chk_display_name_not_empty"
        ),
    )

    def __repr__(self) -> str:
        return f"<Sneaker id={self.id} display_name='{self.display_name}'>"
