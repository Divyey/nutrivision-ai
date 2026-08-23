import logging
import time
from datetime import date as Date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.event_log import elapsed_ms, log_event, short_id
from infrastructure.database.models.user import User
from infrastructure.database.session import get_db
from services.auth.middleware.auth_middleware import get_current_user
from services.food.services.food_classes_service import foods_log_line_from_items
from services.meals.controller import meals_controller
from services.meals.schema.meals_schema import (
    DiaryResponse,
    LogMealsRequest,
    LogWaterRequest,
    MealEntryResponse,
    PatchMealEntryRequest,
    WaterEntryResponse,
)
from services.meals.services.meals_health import check_meals_health

logger = logging.getLogger("nutrivision")

router = APIRouter(prefix="/meals", tags=["meals"])


@router.get("/health", summary="Meals service health")
def meals_health():
    result = check_meals_health()
    payload = {"service": "meals", **result}
    if result["status"] == "healthy":
        return payload
    return JSONResponse(status_code=503, content=payload)


@router.get(
    "/diary",
    response_model=DiaryResponse,
    summary="Get the current user's diary for a calendar date",
)
def read_diary(
    logged_on: Date = Query(
        ..., alias="date", description="Local calendar date YYYY-MM-DD"
    ),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiaryResponse:
    started = time.perf_counter()
    diary = meals_controller.get_diary(logged_on, user, db)
    meal_count = sum(len(entries) for entries in diary.slots.values())
    log_event(
        logger,
        logging.INFO,
        "🍽️",
        "[MEALS] diary",
        "meals.diary",
        user=str(user.id),
        date=logged_on,
        meals=meal_count,
        water=len(diary.water.entries),
        elapsed=elapsed_ms(started),
    )
    return diary


@router.post(
    "/entries",
    response_model=list[MealEntryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Confirm and log detected foods into a meal slot",
)
def create_entries(
    payload: LogMealsRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MealEntryResponse]:
    started = time.perf_counter()
    user_key = str(user.id)
    foods = foods_log_line_from_items(
        [(meal_item.class_id, meal_item.quantity) for meal_item in payload.items]
    )
    try:
        created = meals_controller.log_meals(payload, user, db)
    except HTTPException as exc:
        log_event(
            logger,
            logging.WARNING,
            "🍽️",
            "[MEALS] create_failed",
            "meals.create_failed",
            user=user_key,
            date=payload.logged_on,
            slot=payload.slot.value,
            foods=foods,
            count=len(payload.items),
            status=exc.status_code,
            elapsed=elapsed_ms(started),
        )
        raise
    log_event(
        logger,
        logging.INFO,
        "🍽️",
        "[MEALS] create",
        "meals.create",
        user=user_key,
        date=payload.logged_on,
        slot=payload.slot.value,
        foods=foods,
        count=len(created),
        elapsed=elapsed_ms(started),
    )
    return created


@router.patch(
    "/entries/{entry_id}",
    response_model=MealEntryResponse,
    summary="Update quantity and/or meal slot",
)
def patch_entry(
    entry_id: UUID,
    payload: PatchMealEntryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealEntryResponse:
    started = time.perf_counter()
    user_key = str(user.id)
    try:
        updated = meals_controller.patch_meal_entry(entry_id, payload, user, db)
    except HTTPException as exc:
        log_event(
            logger,
            logging.WARNING,
            "🍽️",
            "[MEALS] update_failed",
            "meals.update_failed",
            user=user_key,
            entry=short_id(entry_id),
            status=exc.status_code,
            elapsed=elapsed_ms(started),
        )
        raise
    log_event(
        logger,
        logging.INFO,
        "🍽️",
        "[MEALS] update",
        "meals.update",
        user=user_key,
        entry=short_id(entry_id),
        slot=updated.slot.value,
        quantity=updated.quantity,
        elapsed=elapsed_ms(started),
    )
    return updated


@router.delete(
    "/entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a meal entry",
)
def delete_entry(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    started = time.perf_counter()
    user_key = str(user.id)
    try:
        meals_controller.delete_meal_entry(entry_id, user, db)
    except HTTPException as exc:
        log_event(
            logger,
            logging.WARNING,
            "🍽️",
            "[MEALS] delete_failed",
            "meals.delete_failed",
            user=user_key,
            entry=short_id(entry_id),
            status=exc.status_code,
            elapsed=elapsed_ms(started),
        )
        raise
    log_event(
        logger,
        logging.INFO,
        "🍽️",
        "[MEALS] delete",
        "meals.delete",
        user=user_key,
        entry=short_id(entry_id),
        elapsed=elapsed_ms(started),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/water",
    response_model=WaterEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a water serving",
)
def create_water(
    payload: LogWaterRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WaterEntryResponse:
    started = time.perf_counter()
    user_key = str(user.id)
    try:
        created = meals_controller.log_water(payload, user, db)
    except HTTPException as exc:
        log_event(
            logger,
            logging.WARNING,
            "💧",
            "[MEALS] water_failed",
            "meals.water_failed",
            user=user_key,
            status=exc.status_code,
            elapsed=elapsed_ms(started),
        )
        raise
    log_event(
        logger,
        logging.INFO,
        "💧",
        "[MEALS] water",
        "meals.water",
        user=user_key,
        date=payload.logged_on,
        milliliters=created.milliliters,
        elapsed=elapsed_ms(started),
    )
    return created


@router.delete(
    "/water/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a water entry",
)
def delete_water(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    started = time.perf_counter()
    user_key = str(user.id)
    try:
        meals_controller.delete_water_entry(entry_id, user, db)
    except HTTPException as exc:
        log_event(
            logger,
            logging.WARNING,
            "💧",
            "[MEALS] water_delete_failed",
            "meals.water_delete_failed",
            user=user_key,
            entry=short_id(entry_id),
            status=exc.status_code,
            elapsed=elapsed_ms(started),
        )
        raise
    log_event(
        logger,
        logging.INFO,
        "💧",
        "[MEALS] water_delete",
        "meals.water_delete",
        user=user_key,
        entry=short_id(entry_id),
        elapsed=elapsed_ms(started),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
