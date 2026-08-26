import logging
import time
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.event_log import elapsed_ms, log_event
from core.health import service_health_http
from infrastructure.database.models.user import User
from infrastructure.database.session import get_db
from services.auth.middleware.auth_middleware import get_current_user
from services.nutrition.controller import nutrition_controller
from services.nutrition.schema.nutrition_schema import FoodSearchHit, FoodSearchResponse
from services.nutrition.services.nutrition_health import check_nutrition_health

logger = logging.getLogger("nutrivision")

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/health", summary="Nutrition catalog service health")
def nutrition_health():
    return service_health_http("nutrition", check_nutrition_health())


@router.get(
    "/search",
    response_model=FoodSearchResponse,
    summary="Search complete catalog foods by name or alias",
)
def search_foods(
    q: str = Query(..., min_length=2, max_length=64, description="Name or alias"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodSearchResponse:
    started = time.perf_counter()
    result = nutrition_controller.search_foods(q, db)
    log_event(
        logger,
        logging.INFO,
        "🥗",
        "[NUTRITION] search",
        "nutrition.search",
        user=str(user.id),
        q=q,
        hits=len(result.items),
        elapsed=elapsed_ms(started),
    )
    return result


@router.get(
    "/{food_id}",
    response_model=FoodSearchHit,
    summary="Get one complete catalog food by id",
)
def get_food(
    food_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodSearchHit:
    started = time.perf_counter()
    result = nutrition_controller.get_food(food_id, db)
    log_event(
        logger,
        logging.INFO,
        "🥗",
        "[NUTRITION] get",
        "nutrition.get",
        user=str(user.id),
        food=str(food_id),
        elapsed=elapsed_ms(started),
    )
    return result
