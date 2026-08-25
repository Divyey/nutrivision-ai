from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.nutrition.schema.nutrition_schema import FoodSearchHit, FoodSearchResponse
from services.nutrition.services import nutrition_service


def search_foods(query: str, db: Session) -> FoodSearchResponse:
    try:
        return nutrition_service.search_foods(db, query)
    except nutrition_service.NutritionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


def get_food(food_id: UUID, db: Session) -> FoodSearchHit:
    try:
        return nutrition_service.get_food(db, food_id)
    except nutrition_service.NutritionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
