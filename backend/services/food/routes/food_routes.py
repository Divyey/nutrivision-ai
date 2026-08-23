import logging
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from core.event_log import elapsed_ms, log_event
from infrastructure.database.models.user import User
from services.auth.middleware.auth_middleware import get_current_user
from services.food.controller import food_controller
from services.food.schema.food_schema import FoodPredictResponse
from services.food.services.food_classes_service import foods_log_line_from_class_ids
from services.food.services.food_detector_service import FoodDetector, get_food_detector
from services.food.services.food_health import check_food_health

logger = logging.getLogger("nutrivision")

router = APIRouter(prefix="/food", tags=["food"])


@router.get("/health", summary="Food service health")
def food_health():
    result = check_food_health()
    payload = {"service": "food", **result}
    if result["status"] == "healthy":
        return payload
    return JSONResponse(status_code=503, content=payload)


@router.post(
    "/predict",
    response_model=FoodPredictResponse,
    summary="Detect dishes in a meal photo",
)
async def predict(
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    detector: FoodDetector = Depends(get_food_detector),
) -> FoodPredictResponse:
    started = time.perf_counter()
    user_key = str(user.id)
    image_bytes = await image.read()
    # ONNX Runtime is sync; keep the event loop free while the lock is held.
    try:
        payload = await run_in_threadpool(
            food_controller.predict_bytes,
            image_bytes,
            image.content_type,
            detector,
        )
    except HTTPException as exc:
        log_event(
            logger,
            logging.WARNING,
            "🔎",
            "[FOOD] predict_failed",
            "food.predict_failed",
            user=user_key,
            bytes=len(image_bytes),
            type=image.content_type,
            status=exc.status_code,
            elapsed=elapsed_ms(started),
        )
        raise
    log_event(
        logger,
        logging.INFO,
        "🔎",
        "[FOOD] predict",
        "food.predict",
        user=user_key,
        bytes=len(image_bytes),
        type=image.content_type,
        detections=len(payload.items),
        foods=foods_log_line_from_class_ids([item.class_id for item in payload.items]),
        elapsed=elapsed_ms(started),
    )
    return payload
