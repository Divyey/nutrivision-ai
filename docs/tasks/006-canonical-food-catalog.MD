# 006: Canonical food catalog

**Branch:** `006-canonical-food-catalog`

Searchable foods with cited INDB per-100g macros and serving→gram maps. **005 scan logging is unchanged:** Confirm & Log still snapshots from `dish_nutrition`. 006 adds a catalog for typed add/edit.

## Design

- `0005_foods_catalog`: empty `foods`, `food_aliases`, `food_servings` (seed from CSV, not Alembic)
- `0006_typed_meal_entries`: `meal_entries` may be scan (`class_id`) **or** typed (`food_id` + `unit`)
- HTTP catalog is `backend/services/nutrition/` (`GET /nutrition/search`). Detector stays `POST /food/predict`. Tables/CSV stay `foods*`
- Postgres gets the curated CSV (~80–120 rows), not the full INDB workbook

## Delivered

- Seed CSV [`backend/data/foods_catalog.csv`](../../backend/data/foods_catalog.csv) (30 detect foods + curated INDB staples; 3 incomplete)
- `GET /api/v1/nutrition/search?q=` and `GET /api/v1/nutrition/{food_id}` (JWT, complete foods only)
- `GET /api/v1/nutrition/health` + `nutrition` on `/health`
- Typed log: `POST /api/v1/meals/entries` with `{ food_id, unit, quantity }` (`source=typed`)
- Typed edit: `PATCH /api/v1/meals/entries/{id}` with `food_id` / `unit` / `quantity`
- Frontend: `NutritionService` + Tracking **Add** / pencil edit drawer
- Registry: [`backend/data/FOODS.md`](../../backend/data/FOODS.md)

## Non-goals

Scan S/M/L, dropping `dish_nutrition`, Nutritionix, USDA/OFF, recommendations, R2, feedback, committing the INDB xlsx.

## API (JWT)

| Method | Path |
|---|---|
| GET | `/api/v1/nutrition/search?q=` |
| GET | `/api/v1/nutrition/{food_id}` |
| GET | `/api/v1/nutrition/health` |
| POST | `/api/v1/meals/entries` (`class_id` **or** `food_id`+`unit`) |
| PATCH | `/api/v1/meals/entries/{id}` (`quantity`, `slot`, `food_id`, `unit`) |

## Seed

```bash
python scripts/upsert_foods_catalog.py --dry-run
python scripts/upsert_foods_catalog.py
```
