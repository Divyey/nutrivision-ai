from fastapi import HTTPException

from services.food.schema.food_schema import FoodPredictResponse
from services.food.services.food_detector_service import FoodDetector, FoodError
from services.food.services.food_service import FoodService


def predict_bytes(
    image_bytes: bytes,
    content_type: str | None,
    detector: FoodDetector,
) -> FoodPredictResponse:
    try:
        return FoodService(detector).predict(image_bytes, content_type)
    except FoodError as error:
        raise HTTPException(
            status_code=error.status_code, detail=error.detail
        ) from error
