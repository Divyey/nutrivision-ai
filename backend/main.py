import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.health import collect_service_health, services_healthy
from infrastructure.database import health as db_health
from services.auth.routes.auth_routes import router as auth_router

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
    database_ok = db_health.check_database()
    _log_startup_health(database_ok, collect_service_health())
    yield


app = FastAPI(
    title="NutriVision AI",
    version="0.0.1",
    description="AI-powered food detection, nutrition analysis, and personalized diet recommendations.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)


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
