from collections.abc import Callable

from services.auth.services.auth_health import check_auth_health
from services.meals.services.meals_health import check_meals_health
from services.users.services.users_health import check_users_health

ServiceCheck = Callable[[], dict[str, str]]

# Register each backend service here when it is added.
SERVICE_CHECKS: dict[str, ServiceCheck] = {
    "auth": check_auth_health,
    "users": check_users_health,
    "meals": check_meals_health,
}


def collect_service_health() -> dict[str, dict[str, str]]:
    return {name: check() for name, check in SERVICE_CHECKS.items()}


def services_healthy(services: dict[str, dict[str, str]]) -> bool:
    return all(result.get("status") == "healthy" for result in services.values())
