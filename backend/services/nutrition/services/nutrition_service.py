from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from infrastructure.database.models.food import Food
from services.nutrition.schema.nutrition_schema import (
    FoodSearchHit,
    FoodSearchResponse,
    FoodServingResponse,
)
from services.nutrition.services.nutrition_catalog_seed import normalize_alias

SEARCH_LIMIT = 20


class NutritionError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def search_foods(db: Session, query: str) -> FoodSearchResponse:
    needle = normalize_alias(query)
    if len(needle) < 2:
        raise NutritionError(400, "Search query must be at least 2 characters.")
    foods = (
        db.query(Food)
        .options(selectinload(Food.aliases), selectinload(Food.servings))
        .filter(Food.status == "complete")
        .all()
    )
    ranked: list[tuple[int, Food]] = []
    for food in foods:
        haystacks = [normalize_alias(food.slug), normalize_alias(food.name)]
        haystacks.extend(alias.alias for alias in food.aliases)
        score = _match_score(needle, haystacks)
        if score is not None:
            ranked.append((score, food))
    ranked.sort(key=lambda item: (item[0], item[1].name.lower()))
    return FoodSearchResponse(
        query=needle,
        items=[_to_hit(food) for _score, food in ranked[:SEARCH_LIMIT]],
    )


def get_food(db: Session, food_id: UUID) -> FoodSearchHit:
    food = (
        db.query(Food)
        .options(selectinload(Food.aliases), selectinload(Food.servings))
        .filter(Food.id == food_id, Food.status == "complete")
        .one_or_none()
    )
    if food is None:
        raise NutritionError(404, "Food not found.")
    return _to_hit(food)


def _match_score(needle: str, haystacks: list[str]) -> int | None:
    contains = False
    for hay in haystacks:
        if hay == needle or hay.startswith(needle):
            return 0
        if needle in hay:
            contains = True
    return 1 if contains else None


def _as_float(value: object | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _to_hit(food: Food) -> FoodSearchHit:
    servings = sorted(food.servings, key=lambda row: (not row.is_default, row.unit))
    return FoodSearchHit(
        id=food.id,
        slug=food.slug,
        name=food.name,
        detect_class_id=food.detect_class_id,
        status=food.status,
        calories_per_100g=_as_float(food.calories_per_100g),
        protein_per_100g=_as_float(food.protein_per_100g),
        carb_per_100g=_as_float(food.carb_per_100g),
        fat_per_100g=_as_float(food.fat_per_100g),
        source_dataset=food.source_dataset,
        source_id=food.source_id,
        source_note=food.source_note,
        aliases=sorted({alias.alias for alias in food.aliases}),
        servings=[
            FoodServingResponse(
                unit=row.unit,
                grams=float(row.grams),
                milliliters=_as_float(row.milliliters),
                is_default=row.is_default,
            )
            for row in servings
        ],
    )
