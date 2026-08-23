from services.food.services.food_detector_service import food_detector_health


def check_food_health() -> dict[str, str]:
    """Readiness for GET /food/health. Not registered on GET /health."""
    return food_detector_health()
