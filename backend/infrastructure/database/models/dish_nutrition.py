from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base


class DishNutrition(Base):
    """Per-100g macros and default serving size, keyed by food class id.

    Labels live in food_classes_service. Alembic creates this table empty.
    Production values come from data/dish_nutrition.csv via the upsert script.
    """

    __tablename__ = "dish_nutrition"

    class_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    calories_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    protein_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    carb_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    default_serving_grams: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
