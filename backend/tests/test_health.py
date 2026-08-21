from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

HEALTHY_AUTH = {"status": "healthy", "database": "healthy"}
UNHEALTHY_AUTH = {"status": "unhealthy", "database": "unhealthy"}


def test_aggregate_health_healthy():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "healthy",
        "api": "healthy",
        "database": "healthy",
        "services": {"auth": HEALTHY_AUTH},
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
    assert body["services"]["auth"] == UNHEALTHY_AUTH
    assert "DATABASE_URL" not in response.text


def test_auth_service_health_healthy():
    with TestClient(app) as client:
        response = client.get("/auth/health")

    assert response.status_code == 200
    assert response.json() == {"service": "auth", **HEALTHY_AUTH}


def test_auth_service_health_unhealthy():
    with patch(
        "infrastructure.database.health.check_database",
        return_value=False,
    ):
        with TestClient(app) as client:
            response = client.get("/auth/health")

    assert response.status_code == 503
    assert response.json() == {"service": "auth", **UNHEALTHY_AUTH}
    assert "postgresql://" not in response.text
