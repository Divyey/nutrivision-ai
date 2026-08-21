from infrastructure.database import health as db_health


def check_auth_health() -> dict[str, str]:
    database_ok = db_health.check_database()
    status = "healthy" if database_ok else "unhealthy"
    return {"status": status, "database": status}
