# 005 — Food Tracking & Daily Diary

**Branch:** `005-food-tracking-daily-diary`

## Pipeline

```text
Scan / Detection  →  class_id  →  dish_nutrition lookup (write time)
    →  quantity × serving nutrition  →  meal_entries snapshot  →  daily diary
```

## Contract

- Nutrition is resolved at **write** time from `dish_nutrition` (CSV → upsert script, not Alembic seed).
- `meal_entries` store kcal + macro **snapshots**.
- `GET /api/v1/meals/diary` reads those snapshots only. It does not re-join `dish_nutrition`.
- `PATCH` quantity re-snapshots from current `dish_nutrition`.
- `PATCH` slot preserves stored nutrition.
- Missing `dish_nutrition` row for a valid `class_id` → **400**. No Flask `class_mapping` integer fallback. No silent 0 kcal.
- `quantity` = count of default servings (`1` = `default_serving_grams` grams).
- Formula: `calories = quantity * (calories_per_100g * default_serving_grams / 100)` (same for protein, carb, fat).
- Slots: `breakfast` \| `lunch` \| `snacks` \| `dinner`.
- Predict remains detections-only. Scan Results show **no kcal** until after Confirm & Log.
- Visual portion / box-to-grams estimation is **not** implemented.
- Typed food search and live Nutritionix lookup are **not** part of 005.
- Multi-day calendar widgets, R2 image storage, retraining, and prediction feedback are out of scope.

## Seed

[`backend/data/dish_nutrition.csv`](../../backend/data/dish_nutrition.csv): 27 INDB-backed rows. Empty numeric cells (do not invent values):

| class_id | label |
|---|---|
| 4 | ghevar |
| 8 | jalebi |
| 12 | bhature |

Registry: [`backend/data/DISH_NUTRITION.md`](../../backend/data/DISH_NUTRITION.md). Upsert: `python scripts/upsert_dish_nutrition.py` from `backend/`.

## API (all JWT)

| Method | Path |
|---|---|
| POST | `/api/v1/meals/entries` |
| PATCH | `/api/v1/meals/entries/{id}` |
| DELETE | `/api/v1/meals/entries/{id}` |
| GET | `/api/v1/meals/diary` |
| POST | `/api/v1/meals/water` |
| DELETE | `/api/v1/meals/water/{id}` |

Ownership misses return **404**. `GET /health` includes `meals`. Food readiness stays on `GET /api/v1/food/health`.
