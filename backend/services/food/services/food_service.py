from __future__ import annotations

from core.config import settings
from services.food.schema.food_schema import (
    FoodBox,
    FoodPredictItem,
    FoodPredictResponse,
)
from services.food.services.food_detector_service import (
    ALLOWED_IMAGE_TYPES,
    FoodDetector,
    FoodError,
    FoodPredictResult,
)


class FoodService:
    def __init__(self, detector: FoodDetector) -> None:
        self._detector = detector

    def predict(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> FoodPredictResponse:
        if not self._detector.is_ready():
            raise FoodError(503, "Food analysis is not available")
        media_type = (content_type or "").split(";")[0].strip().lower()
        if media_type not in ALLOWED_IMAGE_TYPES:
            raise FoodError(415, "Use a JPEG, PNG, or WebP photo")
        if len(image_bytes) > settings.food_max_image_bytes:
            raise FoodError(413, "Image is too large")
        if not image_bytes:
            raise FoodError(400, "Could not read this image")
        return _to_response(self._detector.predict(image_bytes))


def _to_response(result: FoodPredictResult) -> FoodPredictResponse:
    return FoodPredictResponse(
        image_width=result.image_width,
        image_height=result.image_height,
        items=[
            FoodPredictItem(
                class_id=item.class_id,
                label=item.label,
                confidence=item.confidence,
                box=FoodBox(
                    x1=item.box[0],
                    y1=item.box[1],
                    x2=item.box[2],
                    y2=item.box[3],
                ),
            )
            for item in result.items
        ],
    )
