import logging

from sqlalchemy import text

from infrastructure.database.connection import engine

logger = logging.getLogger("nutrivision")


def check_database() -> bool:
    """Return True if the database accepts a lightweight query.

    Failures are logged without connection strings or other secrets.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.error("Database health check failed")
        return False
