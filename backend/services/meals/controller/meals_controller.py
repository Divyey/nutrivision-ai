from collections.abc import Callable
from datetime import date
from typing import TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from infrastructure.database.models.user import User
from services.meals.schema.meals_schema import (
    DiaryResponse,
    LogMealsRequest,
    LogWaterRequest,
    MealEntryResponse,
    PatchMealEntryRequest,
    WaterEntryResponse,
)
from services.meals.services import meals_service
from services.meals.services.meals_service import MealsError

T = TypeVar("T")


def _run(fn: Callable[..., T], *args: object, **kwargs: object) -> T:
    try:
        return fn(*args, **kwargs)
    except MealsError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


def log_meals(
    payload: LogMealsRequest, user: User, db: Session
) -> list[MealEntryResponse]:
    return _run(meals_service.log_meals, db, user, payload)


def patch_meal_entry(
    entry_id: UUID,
    payload: PatchMealEntryRequest,
    user: User,
    db: Session,
) -> MealEntryResponse:
    return _run(meals_service.patch_meal_entry, db, user, entry_id, payload)


def delete_meal_entry(entry_id: UUID, user: User, db: Session) -> None:
    _run(meals_service.delete_meal_entry, db, user, entry_id)


def log_water(payload: LogWaterRequest, user: User, db: Session) -> WaterEntryResponse:
    return _run(meals_service.log_water, db, user, payload)


def delete_water_entry(entry_id: UUID, user: User, db: Session) -> None:
    _run(meals_service.delete_water_entry, db, user, entry_id)


def get_diary(logged_on: date, user: User, db: Session) -> DiaryResponse:
    return _run(meals_service.get_diary, db, user, logged_on)
