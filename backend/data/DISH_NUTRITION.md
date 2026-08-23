# dish_nutrition seed

[`dish_nutrition.csv`](dish_nutrition.csv) — class ids **0–29**, labels from `FOOD_CLASS_LABELS`.

## Dataset (source of truth)

| Role | Dataset | What we search | Where |
|---|---|---|---|
| **Primary (production)** | **INDB** — Anuvaad Indian Nutrient Databank (Vijayakumar et al., *Current Developments in Nutrition*, 2024) | Recipe-level per-100g energy, protein, carb, fat + serving energy | [INDB.xlsx](https://github.com/lindsayjaacks/Indian-Nutrient-Databank-INDB-/blob/main/INDB.xlsx) (`Nutrient Data` sheet). Codes in `source` are INDB `food_code` (ASC / BFP / OSR). |
| Underlying lab table | ICMR-NIN **IFCT 2017** (and 2004) | Ingredient composition used to *build* INDB recipes | Not redistributed here; request from NIN. Do not type IFCT numbers by hand. |
| Never | Flask `class_mapping` integers | kcal per detection box | Not per-100g. Do not copy into this CSV. |
| Never | Pytest fixtures (`1/2/3/4` kcal + 100 g) | Obvious fakes | Must not be copied into this CSV or Neon. |
| Not in 005 | Live Nutritionix / typed food search | External NLP lookup | Out of scope. Do not call at runtime. Do not fill empty CSV rows from it in this ticket. |

Serving grams = `unit_serving_energy_kcal / energy_kcal × 100`, clamped to 10–400 g. `source` is CSV-only; it is not a database column.

Three detect classes have **no usable INDB row** (empty numeric cells until a cited fill). Do not invent values. Logging these `class_id`s returns **400**.

| class_id | label | why empty |
|---|---|---|
| 4 | ghevar | no INDB recipe |
| 8 | jalebi | no INDB recipe |
| 12 | bhature | only INDB row is ~82 g fat / 100 g (implausible for logging) |

A few labels use the **closest INDB recipe** (stated in `source`): aloo-fry → dry potato; dum-aloo → potato curry (INDB dum-aloo row discarded, 74 g fat/100 g); chicken-seekh-kebab → mutton seekh; chicken-biryani → chicken pulao; chole → white chickpea curry.

## Upsert against Neon

```bash
# from backend/
python scripts/upsert_dish_nutrition.py --dry-run
python scripts/upsert_dish_nutrition.py
```

Writes 27 INDB rows, **deletes** leftover dummy rows for class_ids 4/8/12, and **resnapshots** existing `meal_entries` from the new per-100g table (so old 1 kcal diary lines update). Pass `--no-resnapshot` to leave stored diary macros unchanged.

Incomplete rows (all five numeric cells empty) are skipped. A row with only some numbers filled is an error. This is **not** an Alembic data migration. Alembic `0004` creates empty `dish_nutrition` / `meal_entries` / `water_entries` tables only.

## Snapshots vs PATCH

Diary kcal come from `meal_entries` columns written at insert time:

`calories = quantity * (calories_per_100g * default_serving_grams / 100)` (same for protein, carb, fat). `quantity` is a count of default servings.

| Write | Snapshot |
|---|---|
| `POST /meals/entries` | Snapshot from **current** `dish_nutrition` |
| `PATCH` quantity | Re-snapshot from **current** `dish_nutrition` |
| `PATCH` slot only | Stored kcal/macros **unchanged** |
| `GET` diary | Reads stored snapshots only |
| `upsert_dish_nutrition.py` (default) | Re-snapshots **all** `meal_entries` from current `dish_nutrition` |
