import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from core.config import settings
from core.health import collect_service_health, services_healthy
from infrastructure.database import health as db_health
from services.auth.routes.auth_routes import router as auth_router
from services.food.routes.food_routes import router as food_router
from services.food.services.food_detector_service import (
    create_food_detector,
    get_food_detector,
    set_food_detector,
)
from services.users.routes.users_routes import router as users_router

logger = logging.getLogger("nutrivision")


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.setLevel(logging.INFO)


def _log_startup_health(database_ok: bool, services: dict[str, dict[str, str]]) -> None:
    logger.info("[✓] API        HEALTHY")
    if database_ok:
        logger.info("[✓] DATABASE   HEALTHY")
    else:
        logger.error("[✗] DATABASE   UNHEALTHY")
    for name, result in services.items():
        label = name.upper().ljust(10)
        if result.get("status") == "healthy":
            logger.info("[✓] %s HEALTHY", label)
        else:
            logger.error("[✗] %s UNHEALTHY", label)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _configure_logging()
    set_food_detector(create_food_detector())
    database_ok = db_health.check_database()
    _log_startup_health(database_ok, collect_service_health())
    if get_food_detector().is_ready():
        logger.info("[✓] FOOD       HEALTHY")
    else:
        logger.info("[✗] FOOD       MODEL UNAVAILABLE")
    yield


app = FastAPI(
    title="NutriVision AI",
    version="0.0.1",
    description="AI-powered food detection, nutrition analysis, and personalized diet recommendations.",
    lifespan=lifespan,
)

_original_form = Request.form


def _form_with_image_cap(self, *args, **kwargs):
    # Starlette defaults to 1 MiB per part; Scan photos may be up to food_max_image_bytes.
    kwargs.setdefault("max_part_size", settings.food_max_image_bytes)
    return _original_form(self, *args, **kwargs)


Request.form = _form_with_image_cap  # type: ignore[method-assign]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API_V1_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(food_router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["health"], summary="Aggregate service health")
def health():
    database_ok = db_health.check_database()
    services = collect_service_health()
    healthy = database_ok and services_healthy(services)
    payload = {
        "status": "healthy" if healthy else "unhealthy",
        "api": "healthy",
        "database": "healthy" if database_ok else "unhealthy",
        "services": services,
    }
    if healthy:
        return payload
    return JSONResponse(status_code=503, content=payload)
