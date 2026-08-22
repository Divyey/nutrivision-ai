from unittest.mock import patch

from fastapi.testclient import TestClient

from helpers import API_V1
from main import app

HEALTHY = {"status": "healthy", "database": "healthy"}
UNHEALTHY = {"status": "unhealthy", "database": "unhealthy"}


def test_aggregate_health_healthy():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "healthy",
        "api": "healthy",
        "database": "healthy",
        "services": {"auth": HEALTHY, "users": HEALTHY},
    }
    assert "DATABASE_URL" not in response.text
    assert "postgresql://" not in response.text


def test_aggregate_health_auth_unhealthy():
    with patch(
        "infrastructure.database.health.check_database",
        return_value=False,
    ):
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unhealthy"
    assert body["api"] == "healthy"
    assert body["database"] == "unhealthy"
    assert body["services"]["auth"] == UNHEALTHY
    assert body["services"]["users"] == UNHEALTHY
    assert "DATABASE_URL" not in response.text


def test_auth_service_health_healthy():
    with TestClient(app) as client:
        response = client.get(f"{API_V1}/auth/health")

    assert response.status_code == 200
    assert response.json() == {"service": "auth", **HEALTHY}


def test_auth_service_health_unhealthy():
    with patch(
        "infrastructure.database.health.check_database",
        return_value=False,
    ):
        with TestClient(app) as client:
            response = client.get(f"{API_V1}/auth/health")

    assert response.status_code == 503
    assert response.json() == {"service": "auth", **UNHEALTHY}
    assert "postgresql://" not in response.text


def test_users_service_health_healthy():
    with TestClient(app) as client:
        response = client.get(f"{API_V1}/users/health")

    assert response.status_code == 200
    assert response.json() == {"service": "users", **HEALTHY}


def test_users_service_health_unhealthy():
    with patch(
        "infrastructure.database.health.check_database",
        return_value=False,
    ):
        with TestClient(app) as client:
            response = client.get(f"{API_V1}/users/health")

    assert response.status_code == 503
    assert response.json() == {"service": "users", **UNHEALTHY}
    assert "postgresql://" not in response.text
