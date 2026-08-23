"""Parse the dish_nutrition CSV and upsert complete rows.

Do not invent IFCT/INDB values. `source` is CSV-only (audit); it is not stored
on dish_nutrition. Incomplete rows (all numeric cells empty) are skipped.

Existing meal_entries keep write-time snapshots until quantity is PATCHed.
PATCH quantity re-reads current dish_nutrition; PATCH slot does not.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy.orm import Session

from infrastructure.database.models.dish_nutrition import DishNutrition
from infrastructure.database.models.meal_entry import MealEntry
from services.food.services.food_classes_service import FOOD_CLASS_LABELS
from services.food.services.food_nutrition_service import (
    get_dish_nutrition,
    snapshot_for_quantity,
)

DEFAULT_CSV = Path(__file__).resolve().parents[3] / "data" / "dish_nutrition.csv"

NUMERIC_FIELDS = (
    "calories_per_100g",
    "protein_per_100g",
    "carb_per_100g",
    "fat_per_100g",
    "default_serving_grams",
)

REQUIRED_COLUMNS = ("class_id", "label", *NUMERIC_FIELDS, "source")

EXPECTED_CLASS_IDS = tuple(range(30))


class SeedError(Exception):
    """CSV is malformed or a row is only partly filled."""


@dataclass(frozen=True)
class SeedRow:
    class_id: int
    label: str
    calories_per_100g: Decimal
    protein_per_100g: Decimal
    carb_per_100g: Decimal
    fat_per_100g: Decimal
    default_serving_grams: Decimal
    source: str


def _cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def _parse_decimal(raw: str, field: str, class_id: int) -> Decimal:
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise SeedError(f"class_id {class_id}: invalid {field} {raw!r}") from exc
    if value <= 0:
        raise SeedError(f"class_id {class_id}: {field} must be > 0")
    return value


def load_complete_rows(path: Path) -> tuple[list[SeedRow], list[int]]:
    """Return (complete rows, class_ids skipped because every numeric cell is empty)."""
    if not path.is_file():
        raise SeedError(f"CSV not found: {path}")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SeedError("CSV has no header.")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise SeedError(f"CSV missing columns: {', '.join(missing)}")

        seen: list[int] = []
        complete: list[SeedRow] = []
        skipped: list[int] = []
        for row in reader:
            raw_id = _cell(row, "class_id")
            try:
                class_id = int(raw_id)
            except ValueError as exc:
                raise SeedError(f"Invalid class_id {raw_id!r}") from exc
            if class_id not in FOOD_CLASS_LABELS:
                raise SeedError(f"class_id {class_id} is not a detect class (0–29).")
            expected_label = FOOD_CLASS_LABELS[class_id]
            label = _cell(row, "label")
            if label != expected_label:
                raise SeedError(
                    f"class_id {class_id}: label {label!r} does not match {expected_label!r}"
                )
            if class_id in seen:
                raise SeedError(f"Duplicate class_id {class_id}")
            seen.append(class_id)

            empty = [field for field in NUMERIC_FIELDS if not _cell(row, field)]
            if len(empty) == len(NUMERIC_FIELDS):
                skipped.append(class_id)
                continue
            if empty:
                raise SeedError(
                    f"class_id {class_id}: fill all numeric columns or leave all empty "
                    f"({', '.join(empty)} empty)"
                )

            complete.append(
                SeedRow(
                    class_id=class_id,
                    label=label,
                    calories_per_100g=_parse_decimal(
                        _cell(row, "calories_per_100g"), "calories_per_100g", class_id
                    ),
                    protein_per_100g=_parse_decimal(
                        _cell(row, "protein_per_100g"), "protein_per_100g", class_id
                    ),
                    carb_per_100g=_parse_decimal(
                        _cell(row, "carb_per_100g"), "carb_per_100g", class_id
                    ),
                    fat_per_100g=_parse_decimal(
                        _cell(row, "fat_per_100g"), "fat_per_100g", class_id
                    ),
                    default_serving_grams=_parse_decimal(
                        _cell(row, "default_serving_grams"),
                        "default_serving_grams",
                        class_id,
                    ),
                    source=_cell(row, "source"),
                )
            )

    if sorted(seen) != list(EXPECTED_CLASS_IDS):
        missing_ids = [i for i in EXPECTED_CLASS_IDS if i not in seen]
        extra = [i for i in seen if i not in EXPECTED_CLASS_IDS]
        raise SeedError(
            f"CSV must list class_id 0–29 once each; missing={missing_ids} extra={extra}"
        )
    return complete, skipped


def upsert_rows(db: Session, rows: list[SeedRow]) -> int:
    """Insert or replace per-100g rows. Does not rewrite existing meal_entries."""
    for row in rows:
        db.merge(
            DishNutrition(
                class_id=row.class_id,
                calories_per_100g=row.calories_per_100g,
                protein_per_100g=row.protein_per_100g,
                carb_per_100g=row.carb_per_100g,
                fat_per_100g=row.fat_per_100g,
                default_serving_grams=row.default_serving_grams,
            )
        )
    db.commit()
    return len(rows)


def delete_class_ids(db: Session, class_ids: list[int]) -> int:
    """Remove dish_nutrition rows that have no cited CSV values (dummy leftovers)."""
    if not class_ids:
        return 0
    deleted = 0
    for class_id in class_ids:
        row = db.get(DishNutrition, class_id)
        if row is None:
            continue
        db.delete(row)
        deleted += 1
    db.commit()
    return deleted


def resnapshot_meal_entries(db: Session) -> int:
    """Recompute stored diary macros from current dish_nutrition (quantity unchanged)."""
    updated = 0
    for entry in db.query(MealEntry).all():
        row = get_dish_nutrition(db, entry.class_id)
        if row is None:
            continue
        snapshot = snapshot_for_quantity(row, entry.quantity)
        entry.calories = snapshot.calories
        entry.protein = snapshot.protein
        entry.carb = snapshot.carb
        entry.fat = snapshot.fat
        updated += 1
    db.commit()
    return updated
