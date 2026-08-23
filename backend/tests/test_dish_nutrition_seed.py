from csv import DictReader
from decimal import Decimal
from pathlib import Path

import pytest

from infrastructure.database.models.dish_nutrition import DishNutrition
from services.food.services.food_classes_service import FOOD_CLASS_LABELS
from services.food.services.food_nutrition_seed import (
    DEFAULT_CSV,
    NUMERIC_FIELDS,
    SeedError,
    delete_class_ids,
    load_complete_rows,
    upsert_rows,
)

TEMPLATE = Path(__file__).resolve().parents[1] / "data" / "dish_nutrition.csv"

EMPTY_CSV = (
    """class_id,label,calories_per_100g,protein_per_100g,carb_per_100g,fat_per_100g,default_serving_grams,source
"""
    + "\n".join(
        f"{class_id},{FOOD_CLASS_LABELS[class_id]},,,,,," for class_id in range(30)
    )
    + "\n"
)


def test_default_csv_path_matches_repo_template():
    assert DEFAULT_CSV.resolve() == TEMPLATE.resolve()


def test_committed_csv_has_indb_rows_and_gaps_are_fully_empty():
    with TEMPLATE.open(newline="", encoding="utf-8") as handle:
        rows = list(DictReader(handle))
    assert [int(row["class_id"]) for row in rows] == list(range(30))
    complete, skipped = load_complete_rows(TEMPLATE)
    assert skipped == [4, 8, 12]
    assert [row.class_id for row in complete] == [
        i for i in range(30) if i not in skipped
    ]
    by_id = {row.class_id: row for row in complete}
    for row in rows:
        class_id = int(row["class_id"])
        assert row["label"] == FOOD_CLASS_LABELS[class_id]
        empty = [field for field in NUMERIC_FIELDS if not row[field].strip()]
        if class_id in skipped:
            assert len(empty) == len(NUMERIC_FIELDS)
            assert row["source"].strip() == ""
        else:
            assert not empty
            assert row["source"].startswith("INDB ")
            assert by_id[class_id].calories_per_100g > 0


def test_empty_csv_skips_all_rows(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text(EMPTY_CSV, encoding="utf-8")
    complete, skipped = load_complete_rows(path)
    assert complete == []
    assert skipped == list(range(30))


def test_partial_numeric_row_is_error(tmp_path):
    path = tmp_path / "partial.csv"
    lines = EMPTY_CSV.splitlines()
    lines[8] = "7,idli,120,,,,,"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(SeedError, match="fill all numeric columns"):
        load_complete_rows(path)


def test_complete_row_parses_and_upserts(tmp_path, db_session):
    path = tmp_path / "filled.csv"
    lines = EMPTY_CSV.splitlines()
    lines[8] = "7,idli,133,3.7,28.2,0.2,40,IFCT test fixture — not production"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    complete, skipped = load_complete_rows(path)
    assert len(complete) == 1
    assert complete[0].class_id == 7
    assert complete[0].calories_per_100g == Decimal("133")
    assert complete[0].source.startswith("IFCT")
    assert skipped == [i for i in range(30) if i != 7]

    db = db_session()
    try:
        upsert_rows(db, complete)
        row = db.get(DishNutrition, 7)
        assert row is not None
        assert float(row.calories_per_100g) == 133
        assert float(row.default_serving_grams) == 40
    finally:
        db.close()


def test_upsert_replaces_existing_row(tmp_path, db_session):
    db = db_session()
    try:
        db.add(
            DishNutrition(
                class_id=7,
                calories_per_100g=Decimal("1"),
                protein_per_100g=Decimal("2"),
                carb_per_100g=Decimal("3"),
                fat_per_100g=Decimal("4"),
                default_serving_grams=Decimal("100"),
            )
        )
        db.commit()
    finally:
        db.close()

    path = tmp_path / "filled.csv"
    lines = EMPTY_CSV.splitlines()
    lines[8] = "7,idli,150,4,30,1,50,cited-table"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    complete, _skipped = load_complete_rows(path)

    db = db_session()
    try:
        upsert_rows(db, complete)
        row = db.get(DishNutrition, 7)
        assert float(row.calories_per_100g) == 150
        assert float(row.default_serving_grams) == 50
    finally:
        db.close()


def test_delete_class_ids_removes_dummy_rows(db_session):
    db = db_session()
    try:
        db.add(
            DishNutrition(
                class_id=4,
                calories_per_100g=Decimal("1"),
                protein_per_100g=Decimal("2"),
                carb_per_100g=Decimal("3"),
                fat_per_100g=Decimal("4"),
                default_serving_grams=Decimal("100"),
            )
        )
        db.commit()
        assert db.get(DishNutrition, 4) is not None
        assert delete_class_ids(db, [4, 8, 12]) == 1
        assert db.get(DishNutrition, 4) is None
    finally:
        db.close()
