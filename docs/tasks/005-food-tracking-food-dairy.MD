# 005: Food Tracking & Daily Diary

**Branch:** `005-food-tracking-daily-diary`

## Delivered

- `dish_nutrition` table (empty in production migrations — **do not invent seed rows**)
- `meal_entries` / `water_entries` with write-time kcal + macro snapshots
- `GET/POST/PATCH/DELETE /api/v1/meals/*` (JWT, ownership 404)
- Scan Results: meal slot + Confirm & Log (no kcal on Results)
- Tracking: diary date prev/next (no future days), edit quantity, delete, water 250 ml
- Scan Confirm uses `?date=` from Tracking Add and POSTs that `logged_on`
- `quantity` = number of default servings (`1` = `default_serving_grams` grams)
- Formula: `calories = quantity * (calories_per_100g * default_serving_grams / 100)` (same for protein/carb/fat)
- Predict contract unchanged (detections only)
- `GET /health` includes `meals`

## Production blocker

005 is **not production-complete** until a real 30-class per-100g + `default_serving_grams` dataset is supplied and seeded.

Template: [`backend/data/dish_nutrition.csv`](../../backend/data/dish_nutrition.csv) (27 INDB rows; ghevar, jalebi, bhature empty). Dataset registry: [`backend/data/DISH_NUTRITION.md`](../../backend/data/DISH_NUTRITION.md). Upsert: `python scripts/upsert_dish_nutrition.py` from `backend/` (writes INDB, deletes dummy rows for empty classes, resnapshots diary macros).

Do not invent IFCT/INDB values or copy Flask `class_mapping` integers into `calories_per_100g`. Pytest fixture numbers (e.g. 1 kcal/100g) must not be copied into the seed file.

Legacy photo path only had undocumented integer kcal per class (count × int). Macros existed only via Nutritionix on typed add-food. This repo had labels only.
