from dataclasses import dataclass

from services.users.services.users_units_service import bmr_sex_offset

ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}

CALORIE_DEFICIT = 500
PROTEIN_RATIO = 0.30
CARB_RATIO = 0.40
FAT_RATIO = 0.30
KCAL_PER_GRAM_PROTEIN = 4
KCAL_PER_GRAM_CARB = 4
KCAL_PER_GRAM_FAT = 9


@dataclass(frozen=True)
class ComputedGoals:
    target_calories: float
    target_protein: float
    target_carb: float
    target_fat: float
    target_bmi: float
    status: str


def _round(value: float) -> float:
    return round(value, 2)


def _bmi_status(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy weight"
    if bmi < 30:
        return "overweight"
    return "obese"


def calculate_tdee(
    *,
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    activity_level: str,
) -> float:
    """Metric Mifflin–St Jeor BMR × activity factor. Intermediate only; not stored."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + bmr_sex_offset(gender)

    try:
        multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    except KeyError as exc:
        raise ValueError("unknown activity_level") from exc

    return bmr * multiplier


def calculate_goals(
    *,
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    activity_level: str,
) -> ComputedGoals:
    """Daily cut goal is TDEE − 500. Macros are percentages of that same number."""
    height_m = height_cm / 100
    if height_m <= 0:
        raise ValueError("height_cm must be positive")

    bmi = weight_kg / (height_m**2)
    tdee = calculate_tdee(
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        activity_level=activity_level,
    )
    target_calories = _round(tdee - CALORIE_DEFICIT)
    return ComputedGoals(
        target_calories=target_calories,
        target_protein=_round(
            (target_calories * PROTEIN_RATIO) / KCAL_PER_GRAM_PROTEIN
        ),
        target_carb=_round((target_calories * CARB_RATIO) / KCAL_PER_GRAM_CARB),
        target_fat=_round((target_calories * FAT_RATIO) / KCAL_PER_GRAM_FAT),
        target_bmi=_round(bmi),
        status=_bmi_status(bmi),
    )
