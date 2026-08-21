from collections.abc import Callable

from services.auth.services.auth_health import check_auth_health

ServiceCheck = Callable[[], dict[str, str]]

# Register each backend service here when it is added.
SERVICE_CHECKS: dict[str, ServiceCheck] = {
    "auth": check_auth_health,
}


def collect_service_health() -> dict[str, dict[str, str]]:
    return {name: check() for name, check in SERVICE_CHECKS.items()}


def services_healthy(services: dict[str, dict[str, str]]) -> bool:
    return all(result.get("status") == "healthy" for result in services.values())
