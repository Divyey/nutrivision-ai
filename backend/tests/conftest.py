import pytest


@pytest.fixture(autouse=True)
def mock_database_health(monkeypatch):
    monkeypatch.setattr(
        "infrastructure.database.health.check_database",
        lambda: True,
    )
