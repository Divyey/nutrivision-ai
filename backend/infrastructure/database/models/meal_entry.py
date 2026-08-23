import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base


class MealEntry(Base):
    __tablename__ = "meal_entries"
    __table_args__ = (
        Index("ix_meal_entries_user_logged_on", "user_id", "logged_on"),
        Index("ix_meal_entries_user_logged_on_slot", "user_id", "logged_on", "slot"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    logged_on: Mapped[date] = mapped_column(Date, nullable=False)
    slot: Mapped[str] = mapped_column(String(16), nullable=False)
    source: Mapped[str] = mapped_column(String(16), nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    calories: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    protein: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    carb: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
