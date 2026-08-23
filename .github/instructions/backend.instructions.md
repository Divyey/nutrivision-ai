---
applyTo: "backend/**/*.py"
---

# Backend

This service is FastAPI + Pydantic v2 + pydantic-settings, SQLAlchemy 2.0 **sync** `Session`, Alembic, PyJWT, bcrypt, `psycopg2-binary`, Neon Postgres (`NullPool`, `pool_pre_ping`). Tests use pytest, FastAPI `TestClient`, and an in-memory SQLite override.

Product contracts (predict JSON, ONNX vs fake detector, class ids, health split) live in the root Copilot instructions. Change them only if the ticket says so.

## Layout

Code lives under `backend/services/{domain}/`:

| Layer | Filename |
|---|---|
| routes | `{domain}_routes.py` |
| controller | `{domain}_controller.py` |
| services | `{domain}_service.py` |
| schema | `{domain}_schema.py` |
| middleware | `{domain}_middleware.py` (auth only today) |

Do not name a layer file after the domain only (`auth.py`). Extra modules keep the domain prefix (`food_detector_service.py`, `food_classes_service.py`, `users_goals_service.py`).

Health checks are **not** a layer folder. Put `{domain}_health.py` in that domain’s `services/` directory (`auth_health.py`, `users_health.py`, `food_health.py`).

`main.py` mounts routers with `API_V1_PREFIX = "/api/v1"`. Domain routers already use `prefix="/auth"`, `"/users"`, `"/food"`.

## Request path

1. **Route** — HTTP, `Depends`, status codes, `response_model`. May `Depends(get_db)` and pass the `Session` through; do not run queries in routes.
2. **Controller** — turn domain errors into `HTTPException`.
3. **Service** — business rules and persistence (or detector calls).
4. **Schema** — Pydantic request/response models. Do not return ORM instances from the API (`from_attributes=True` where that is already used).

## FastAPI, auth, HTTP

- Handlers are **sync** `def` except food predict, which is `async` so it can `await image.read()` and `run_in_threadpool`. Do not move the app onto async SQLAlchemy unless a ticket requires it.
- Keep `InferenceSession.run` and other blocking inference off the event loop; use the existing threadpool + lock.
- Auth: `HTTPBearer` via `get_current_user`. Protected users/food routes depend on it. Unauthenticated → 401 with existing detail strings.
- Status codes already in use: 201 register, 400 unreadable image, 401, 409 duplicate email, 413 too large, 415 unsupported type, 503 unavailable. Empty detection list is **200** with `image_width`, `image_height`, and `items: []`.
- Validate with Pydantic on JSON bodies; validate uploads in the food service (type, size, pixels).

## Config, logging, errors

- Env: `DATABASE_URL`, `JWT_SECRET_KEY`, optional `FOOD_*`. Python: `from core.config import settings` then `settings.database_url`, `settings.jwt_secret_key`, `settings.food_detector` (not `settings.DATABASE_URL`).
- Logging: `logging.getLogger("nutrivision")`. Never log tokens, passwords, or `DATABASE_URL`.
- Domain errors (`AuthError`, `UsersError`, `FoodError`) expose `status_code` and `detail`; controllers map them to `HTTPException`.

## Database

- `Depends(get_db)` yields a sync `Session`. Commit/refresh in services, same as auth/users.
- Schema changes need an Alembic revision under `infrastructure/database/migrations` (`alembic.ini` `script_location`). Users are soft-deleted (`deleted_at`). Unique email applies to active rows.
- Neon: keep `NullPool` unless a ticket changes pooling. DB health: `infrastructure.database.health.check_database`.

## Health

- Each service owns `{name}_health.py` in that domain’s `services/` folder. `"status": "healthy" | "unhealthy"`. No secrets in payloads.
- Register **auth** and **users** in `core.health.SERVICE_CHECKS`. `GET /health` is 503 if the database or a registered check fails.
- Food model readiness is `GET /api/v1/food/health` only. Do not add food to `SERVICE_CHECKS` unless the ticket changes that split.

## Auth / JWT

- `core.security`: bcrypt hashes, JWT `sub` = user id, `exp`, HS256 (`create_access_token` / `decode_access_token`).
- Email is lowercased; names stripped. Do not return `password_hash`. Password max length in schemas is 72 (bcrypt).

## Tests

- `tests/conftest.py` sets `FOOD_DETECTOR=fake` before importing the app so CI never loads ONNX.
- Cover new endpoints and important branches (auth, validation, empty `items`, 503). Follow `test_auth.py`, `test_users.py`, `test_food.py`, `test_health.py`.

## Food / inference (current design)

- Protocol: `FoodDetector` (`is_ready`, `predict`) in `food_detector_service.py`.
- Implementations: `OnnxFoodDetector`, `FakeFoodDetector`, `UnavailableFoodDetector`.
- Lifespan in `main.py` calls `create_food_detector()` / `set_food_detector()`. `OnnxFoodDetector` holds a `threading.Lock` around `session.run`.
- Production deps today: `onnxruntime` (CPU), Pillow, NumPy. Export may use Ultralytics in a **dev** script. Do not add torch or ultralytics to `pyproject.toml` unless the ticket migrates inference.
- Class ids are training ids 0–29 mapped to Flask slugs in `food_classes_service.py`. Do not remap NMS ids through Ultralytics ONNX metadata `names` unless the ticket changes labeling.
- Multipart field `image`; jpeg/png/webp; settings `food_max_image_bytes` (8 MiB, also Starlette part cap); `food_max_pixels` (20e6); `food_confidence_min` 0.4; `food_imgsz` 800.
- Do not add kcal or portion fields to the predict JSON unless the ticket changes the contract.
