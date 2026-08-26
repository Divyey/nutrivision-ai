"""Gram-based macro snapshots for catalog foods. Meals does not call this in 006."""

from dataclasses import dataclass
from decimal import Decimal

from infrastructure.database.models.food import Food
from services.nutrition.services.nutrition_service import NutritionError

QUANTIZE = Decimal("0.01")


@dataclass(frozen=True)
class MacroSnapshot:
    calories: Decimal
    protein: Decimal
    carb: Decimal
    fat: Decimal


def snapshot_for_grams(food: Food, grams: Decimal) -> MacroSnapshot:
    if food.status != "complete" or food.calories_per_100g is None:
        raise NutritionError(400, "Nutrition data is not available for this food.")
    if grams <= 0:
        raise NutritionError(400, "Grams must be greater than 0.")
    scale = grams / Decimal("100")
    return MacroSnapshot(
        calories=(scale * food.calories_per_100g).quantize(QUANTIZE),
        protein=(scale * food.protein_per_100g).quantize(QUANTIZE),
        carb=(scale * food.carb_per_100g).quantize(QUANTIZE),
        fat=(scale * food.fat_per_100g).quantize(QUANTIZE),
    )
