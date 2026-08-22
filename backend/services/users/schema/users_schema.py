from datetime import date
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNSPECIFIED = "unspecified"


class ActivityLevel(StrEnum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"


class VeganStatus(StrEnum):
    YES = "yes"
    NO = "no"


class Allergy(StrEnum):
    NONE = "none"
    LACTOSE = "lactose"
    GLUTEN = "gluten"
    NUTS_BEANS = "nuts_beans"
    EGGS = "eggs"


class HeightPayload(BaseModel):
    feet: int = Field(ge=3, le=8)
    inches: int = Field(ge=0, le=11)


class WeightPayload(BaseModel):
    value: float = Field(gt=0, le=600)
    unit: Literal["kg", "lb"]


class UpdateProfileRequest(BaseModel):
    age: int | None = Field(default=None, ge=10, le=120)
    gender: Gender | None = None
    weight: WeightPayload | None = None
    height: HeightPayload | None = None
    activity_level: ActivityLevel | None = None
    vegan: VeganStatus | None = None
    allergy: Allergy | None = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    age: int | None
    gender: str | None
    weight: WeightPayload | None
    height: HeightPayload | None
    activity_level: str | None
    vegan: str | None
    allergy: str | None
    status: str | None
    start_date: date | None
    target_calories: float | None
    target_protein: float | None
    target_carb: float | None
    target_fat: float | None
    target_bmi: float | None
