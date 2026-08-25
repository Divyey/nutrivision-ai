from infrastructure.database.health import database_health


def check_nutrition_health() -> dict[str, str]:
    return database_health()
