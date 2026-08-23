from pydantic import BaseModel, Field


class FoodBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class FoodPredictItem(BaseModel):
    class_id: int
    label: str
    confidence: float = Field(gt=0, le=1)
    box: FoodBox


class FoodPredictResponse(BaseModel):
    image_width: int
    image_height: int
    items: list[FoodPredictItem]
