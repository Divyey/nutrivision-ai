# NutriVision AI backend

Run from this directory (`backend/`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set DATABASE_URL and JWT_SECRET_KEY
alembic upgrade head
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Tests:

```bash
pytest
```

Dish nutrition (30 detect classes) is seeded from **INDB** in `data/dish_nutrition.csv` (ghevar, jalebi, bhature still empty). Dataset notes: [`data/DISH_NUTRITION.md`](data/DISH_NUTRITION.md). Upsert:

```bash
python scripts/upsert_dish_nutrition.py --dry-run
python scripts/upsert_dish_nutrition.py
```

See [`data/DISH_NUTRITION.md`](data/DISH_NUTRITION.md) for snapshot vs PATCH behavior.

Foods catalog (006, nutrition search; Scan still uses `dish_nutrition`): [`data/FOODS.md`](data/FOODS.md).

```bash
python scripts/upsert_foods_catalog.py --dry-run
python scripts/upsert_foods_catalog.py
```

## FastAPI Cloud

Public API: https://nutrivision-ai-backend.fastapicloud.dev/

CI runs `fastapi deploy backend` from the repo root, so the uploaded app root is `backend/` (`main.py`, `pyproject.toml`). In the FastAPI Cloud dashboard, leave **Application Directory empty**. If it is set to `backend`, the builder looks for `backend/backend` and fails with `No such file or directory`.

Configure `DATABASE_URL`, `JWT_SECRET_KEY`, and `CORS_ORIGINS` (must include https://nutrivision-ai-green.vercel.app). Food settings (`FOOD_MODEL_PATH`, `FOOD_DETECTOR`, image limits) are optional — defaults are in `core/config.py`.

Run **one** uvicorn worker. Measured RSS after loading `best.onnx` and one 640×480 predict is **~300 MB** (see `ml/models/food/EXPORT.md`). Start Cloud at **1 GB** until larger photos are measured; do not assume 2 GB. Do not install torch or ultralytics on FastAPI Cloud. Export ONNX locally:

```bash
# separate Python 3.11 venv — not production requirements
python3.11 -m venv /tmp/nv-yolo-export
/tmp/nv-yolo-export/bin/pip install ultralytics==8.3.73 onnx onnxruntime
/tmp/nv-yolo-export/bin/python scripts/export_food_onnx.py
```

CI sets `FOOD_DETECTOR=fake` so tests never load the ONNX session.

GitHub Actions runs tests on `development` and deploys from `production`. Secrets: `FASTAPI_CLOUD_TOKEN`, `FASTAPI_CLOUD_APP_ID`. See [deploy tokens](https://fastapicloud.com/docs/advanced-features/deploy-tokens/).
