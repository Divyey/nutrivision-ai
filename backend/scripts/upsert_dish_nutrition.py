"""Upsert dish_nutrition from the 30-class CSV. Run from backend/ against Neon.

Does not invent IFCT values. Rows with empty numeric cells are skipped.
Not an Alembic data migration.

Also deletes dummy rows for skipped class_ids and resnapshots meal_entries
so diary kcal match the new per-100g table.

  python scripts/upsert_dish_nutrition.py
  python scripts/upsert_dish_nutrition.py --dry-run
  python scripts/upsert_dish_nutrition.py --no-resnapshot
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from infrastructure.database.session import SessionLocal  # noqa: E402
from services.food.services.food_nutrition_seed import (  # noqa: E402
    DEFAULT_CSV,
    SeedError,
    delete_class_ids,
    load_complete_rows,
    resnapshot_meal_entries,
    upsert_rows,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upsert dish_nutrition from CSV (complete rows only)."
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and print rows; do not write the database.",
    )
    parser.add_argument(
        "--no-resnapshot",
        action="store_true",
        help="Do not rewrite existing meal_entries snapshots.",
    )
    args = parser.parse_args()

    try:
        rows, skipped = load_complete_rows(args.csv)
    except SeedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"complete={len(rows)} skipped_empty={len(skipped)}")
    if not rows:
        print(
            "No complete rows. Fill per-100g + default_serving_grams from a cited "
            "table (IFCT/INDB), then re-run."
        )
        return 0

    for row in rows:
        source = row.source or "(no source)"
        print(
            f"class_id={row.class_id} label={row.label} "
            f"kcal/100g={row.calories_per_100g} serving_g={row.default_serving_grams} "
            f"source={source}"
        )

    if args.dry_run:
        print("dry-run: no database writes")
        return 0

    db = SessionLocal()
    try:
        count = upsert_rows(db, rows)
        removed = delete_class_ids(db, skipped)
        resnapshoted = 0 if args.no_resnapshot else resnapshot_meal_entries(db)
    finally:
        db.close()
    print(f"upserted {count} dish_nutrition rows")
    print(f"deleted {removed} empty-class dummy rows {skipped}")
    if args.no_resnapshot:
        print("meal_entries snapshots left unchanged (--no-resnapshot)")
    else:
        print(f"resnapshoted {resnapshoted} meal_entries from current dish_nutrition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
