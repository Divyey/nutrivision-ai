import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from infrastructure.database.models import Base
from infrastructure.database.session import get_db
from main import app


@pytest.fixture(autouse=True)
def mock_database_health(monkeypatch):
    monkeypatch.setattr(
        "infrastructure.database.health.check_database",
        lambda: True,
    )


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)
    try:
        yield TestingSession
    finally:
        engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

