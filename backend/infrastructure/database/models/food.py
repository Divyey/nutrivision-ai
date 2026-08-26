import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.models.base import Base


class Food(Base):
    """Canonical catalog food. Detect classes link via detect_class_id.

    Alembic creates empty tables. Seed from data/foods_catalog.csv.
    """

    __tablename__ = "foods"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    detect_class_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, unique=True
    )
    calories_per_100g: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    protein_per_100g: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    carb_per_100g: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    fat_per_100g: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    density_g_per_ml: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), nullable=True
    )
    source_dataset: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_note: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    aliases: Mapped[list["FoodAlias"]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )
    servings: Mapped[list["FoodServing"]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )


class FoodAlias(Base):
    __tablename__ = "food_aliases"
    __table_args__ = (UniqueConstraint("alias", name="uq_food_aliases_alias"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    food_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
    alias: Mapped[str] = mapped_column(String(128), nullable=False)
    food: Mapped[Food] = relationship(back_populates="aliases")


class FoodServing(Base):
    __tablename__ = "food_servings"
    __table_args__ = (
        UniqueConstraint("food_id", "unit", name="uq_food_servings_food_unit"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    food_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    grams: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    milliliters: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    food: Mapped[Food] = relationship(back_populates="servings")
