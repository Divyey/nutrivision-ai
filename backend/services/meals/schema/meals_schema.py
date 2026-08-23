from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MealSlot(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACKS = "snacks"
    DINNER = "dinner"


class MealItemInput(BaseModel):
    class_id: int = Field(ge=0, le=29)
    quantity: float = Field(ge=0.01, le=99)


class LogMealsRequest(BaseModel):
    logged_on: date
    slot: MealSlot
    items: list[MealItemInput] = Field(min_length=1)


class PatchMealEntryRequest(BaseModel):
    quantity: float | None = Field(default=None, ge=0.01, le=99)
    slot: MealSlot | None = None


class LogWaterRequest(BaseModel):
    logged_on: date
    milliliters: int = Field(ge=1, le=5000)


class MealEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    logged_on: date
    slot: MealSlot
    source: str
    class_id: int
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
