from uuid import UUID

from pydantic import BaseModel, Field


class FoodServingResponse(BaseModel):
    unit: str
    grams: float
    milliliters: float | None
    is_default: bool


class FoodSearchHit(BaseModel):
    id: UUID
    slug: str
    name: str
    detect_class_id: int | None
    status: str
    calories_per_100g: float | None
    protein_per_100g: float | None
    carb_per_100g: float | None
    fat_per_100g: float | None
    source_dataset: str | None
    source_id: str | None
    source_note: str | None
    aliases: list[str]
    servings: list[FoodServingResponse]


class FoodSearchResponse(BaseModel):
    query: str
    items: list[FoodSearchHit] = Field(default_factory=list)
