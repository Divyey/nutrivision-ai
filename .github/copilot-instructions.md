# NutriVisionAI — repository instructions

NutriVisionAI is a meal-scan product: FastAPI backend (SQLAlchemy, PostgreSQL/Neon, JWT) and React + TypeScript + Vite + Ant Design frontend.

These rules are for Copilot review and code generation. They describe this repository. Do not invent a parallel architecture.

## How to decide

1. Explicit current ticket requirements.
2. Existing API, database, and product contracts.
3. Current repository patterns (inspect the code first).
4. These instruction files.
5. General engineering practice.

If a ticket intentionally changes architecture or a contract, do that change, state the conflict, and do not silently edit unrelated areas. Do not implement later tickets (kcal on predict, feedback, recommendations) unless asked.

Inspect existing code before proposing a new pattern. Reuse what is already there. Explain significant architecture or dependency decisions before implementing them. Do not claim something is verified unless it was inspected or tested.

Never silently change public APIs, DB schema, authentication, or deployment behavior. Never hardcode secrets or environment-specific URLs (`core.config.settings` / env; frontend `VITE_API_BASE_URL`). Keep frontend DTOs in `types/` aligned with backend schemas. Add or update pytest for new backend behavior. Flag security, performance, scalability, maintainability, and over-engineering risks.

## Current architecture (change only if the ticket says so)

These are how the product works today, not forever-laws:

- Feature PRs target `development`. Production deploys from `production`.
- `POST /api/v1/food/predict` is detections-only: `image_width`, `image_height`, `items[]` (`class_id`, `label`, `confidence`, `box`). Empty plate is 200 with those fields and `items: []`. No kcal or portions on this endpoint.
- Scan analyzing progress is request UI, not model confidence. Result boxes come from the API.
- Production inference is ONNX Runtime CPU (`onnxruntime`, `best.onnx`) via `FoodDetector`. CI uses `FOOD_DETECTOR=fake`. Do not add torch or Ultralytics to production runtime unless the ticket migrates inference.
- Class ids are training ids 0–29 mapped in `food_classes_service.py`. Do not remap NMS ids through Ultralytics ONNX metadata `names` unless the ticket changes labeling.
- `GET /health` is API + database + registered services (auth, users, meals, nutrition). Food **model** readiness is `GET /api/v1/food/health` and is not on the aggregator.
- Backend food **inference** is `FoodService` (`/food/predict`). Catalog search is `NutritionService` → `/api/v1/nutrition/search`. Frontend predict client is `DetectionService` — do not rename it to `FoodService` unless the ticket says so.
- Meal diary is `MealService` → `/api/v1/meals/*`. Scan logs `{ class_id, quantity }`. Typed logs `{ food_id, unit, quantity }` (`source=typed`). Predict JSON still has no kcal. `dish_nutrition` is filled from `backend/data/dish_nutrition.csv` via the upsert script (Alembic creates empty tables only). Logging a `class_id` with no row returns 400. The curated catalog is `backend/data/foods_catalog.csv` via `upsert_foods_catalog.py`; do not bulk-load the INDB xlsx into Postgres. Frontend catalog client is `NutritionService` → `GET /api/v1/nutrition/search`.

## Review bar

Flag concrete defects, contract breaks, missing tests, and security issues. Do not nitpick style that already matches the surrounding file.
