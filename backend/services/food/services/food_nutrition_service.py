"""Look up dish_nutrition by class_id and snapshot macros for a serving count.

quantity is the number of default servings. quantity=1 means default_serving_grams
grams. Clients never send kcal or macros.
"""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from infrastructure.database.models.dish_nutrition import DishNutrition

QUANTIZE = Decimal("0.01")


@dataclass(frozen=True)
class MacroSnapshot:
    calories: Decimal
    protein: Decimal
    carb: Decimal
    fat: Decimal


def _round(value: Decimal) -> Decimal:
    return value.quantize(QUANTIZE)


def get_dish_nutrition(db: Session, class_id: int) -> DishNutrition | None:
    return db.get(DishNutrition, class_id)


def snapshot_for_quantity(row: DishNutrition, quantity: Decimal) -> MacroSnapshot:
    """calories = quantity * (per_100g * default_serving_grams / 100)."""
    grams_factor = row.default_serving_grams / Decimal("100")
    scale = quantity * grams_factor
    return MacroSnapshot(
        calories=_round(scale * row.calories_per_100g),
        protein=_round(scale * row.protein_per_100g),
        carb=_round(scale * row.carb_per_100g),
        fat=_round(scale * row.fat_per_100g),
    )
