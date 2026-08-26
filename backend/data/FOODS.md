# Foods catalog (006)

Curated INDB recipes for **typed search**. This is not a dump of the Anuvaad workbook into Postgres, and it does not replace 005 scan nutrition.

## Two lookups (intentional)

| Path | Table / CSV | When |
|---|---|---|
| Scan Confirm & Log | `dish_nutrition` / [`dish_nutrition.csv`](dish_nutrition.csv) | Detector `class_id` (005) |
| Tracking Add / edit | `foods` + servings / [`foods_catalog.csv`](foods_catalog.csv) | Catalog `food_id` + `unit` (006) |

Alembic `0005` creates empty catalog tables. `0006` extends `meal_entries` so a row can be scan (`class_id`) **or** typed (`food_id`). Scan rows stay on `dish_nutrition`; typed rows snapshot from catalog grams.

## What is in git

| File | Role |
|---|---|
| [`foods_catalog.csv`](foods_catalog.csv) | Product catalog: 30 detect foods + curated staples (~80–120 rows). |
| [`dish_nutrition.csv`](dish_nutrition.csv) | 005 scan lookup (unchanged). |

The Anuvaad workbook is **not** in git. Runtime never reads Excel. Rebuild CSV (dev, `openpyxl`) after placing `data/Anuvaad_INDB_2024.11.xlsx` locally:

```bash
python scripts/generate_foods_catalog.py
```

Upstream: [INDB.xlsx](https://github.com/lindsayjaacks/Indian-Nutrient-Databank-INDB-/blob/main/INDB.xlsx) (CC BY 4.0). Vijayakumar et al., *Current Developments in Nutrition* (2024). [Anuvaad INDB](https://www.anuvaad.org.in/indian-nutrient-databank/). Do not redistribute ICMR-NIN IFCT.

## Seed (not Alembic)

```bash
# from backend/
python scripts/upsert_foods_catalog.py --dry-run
python scripts/upsert_foods_catalog.py
```

Incomplete detect classes (ghevar, jalebi, bhature) are stored with `status=incomplete` and **no servings**. Search and GET-by-id omit them.

## API (JWT)

| Method | Path |
|---|---|
| GET | `/api/v1/nutrition/search?q=` |
| GET | `/api/v1/nutrition/{food_id}` |
| GET | `/api/v1/nutrition/health` |
| POST | `/api/v1/meals/entries` (`class_id` **or** `food_id`+`unit`) |
| PATCH | `/api/v1/meals/entries/{id}` (`quantity`, `unit`, `food_id`, `slot`) |
