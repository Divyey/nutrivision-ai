from datetime import date
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MealSlot(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACKS = "snacks"
    DINNER = "dinner"


class MealItemInput(BaseModel):
    class_id: int | None = Field(default=None, ge=0, le=29)
    food_id: UUID | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=16)
    quantity: float = Field(ge=0.01, le=999999.99)

    @model_validator(mode="after")
    def require_scan_or_typed(self) -> Self:
        has_scan = self.class_id is not None
        has_typed = self.food_id is not None
        if has_scan == has_typed:
            raise ValueError("Provide either class_id or food_id.")
        if has_typed and self.unit is None:
            raise ValueError("unit is required when logging a catalog food.")
        if has_scan and self.unit is not None:
            raise ValueError("unit is only valid with food_id.")
        return self


class LogMealsRequest(BaseModel):
    logged_on: date
    slot: MealSlot
    items: list[MealItemInput] = Field(min_length=1)


class PatchMealEntryRequest(BaseModel):
    quantity: float | None = Field(default=None, ge=0.01, le=999999.99)
    slot: MealSlot | None = None
    food_id: UUID | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=16)

    @model_validator(mode="after")
    def require_patch_field(self) -> Self:
        if (
            self.quantity is None
            and self.slot is None
            and self.food_id is None
            and self.unit is None
        ):
            raise ValueError("Provide quantity, slot, food_id, and/or unit.")
        if self.food_id is not None and self.unit is None:
            raise ValueError("unit is required when changing food.")
        return self


class LogWaterRequest(BaseModel):
    logged_on: date
    milliliters: int = Field(ge=1, le=5000)


class MealEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    logged_on: date
    slot: MealSlot
    source: str
    class_id: int | None
    food_id: UUID | None
    unit: str | None
    label: str
    quantity: float
    calories: float
    protein: float
    carb: float
    fat: float


class WaterEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    logged_on: date
    milliliters: int


class MacroTotals(BaseModel):
    calories: float
    protein: float
    carb: float
    fat: float


class WaterDayResponse(BaseModel):
    milliliters: int
    entries: list[WaterEntryResponse]


class DiaryResponse(BaseModel):
    date: date
    slots: dict[MealSlot, list[MealEntryResponse]]
    water: WaterDayResponse
    totals: MacroTotals
