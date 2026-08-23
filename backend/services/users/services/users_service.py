from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from infrastructure.database.models.user import User
from services.users.schema.users_schema import (
    HeightPayload,
    UpdateProfileRequest,
    UserProfileResponse,
    WeightPayload,
)
from services.users.services.users_goals_service import calculate_goals
from services.users.services.users_units_service import (
    cm_to_height,
    height_to_cm,
    weight_to_kg,
)

GOAL_INPUT_FIELDS = ("age", "gender", "weight_kg", "height_cm", "activity_level")
SIMPLE_FIELDS = {
    "age": "age",
    "gender": "gender",
    "activity_level": "activity_level",
    "vegan": "vegan_status",
    "allergy": "allergy",
}


class UsersError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _as_float(value: object | None) -> float | None:
    if value is None:
        return None
    return float(value)


def to_profile(user: User) -> UserProfileResponse:
    weight = None
    if user.weight_kg is not None:
        weight = WeightPayload(value=round(float(user.weight_kg), 2), unit="kg")

    height = None
    if user.height_cm is not None:
        feet, inches = cm_to_height(float(user.height_cm))
        height = HeightPayload(feet=feet, inches=inches)

    return UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        gender=user.gender,
        weight=weight,
        height=height,
        activity_level=user.activity_level,
        vegan=user.vegan_status,
        allergy=user.allergy,
        status=user.status,
        start_date=user.start_date,
        target_calories=_as_float(user.target_calories),
        target_protein=_as_float(user.target_protein),
        target_carb=_as_float(user.target_carb),
        target_fat=_as_float(user.target_fat),
        target_bmi=_as_float(user.target_bmi),
    )


def _has_complete_inputs(user: User) -> bool:
    return all(getattr(user, field) is not None for field in GOAL_INPUT_FIELDS)


def _apply_goals(user: User) -> None:
    if (
        user.age is None
        or user.gender is None
        or user.weight_kg is None
        or user.height_cm is None
        or user.activity_level is None
    ):
        return

    goals = calculate_goals(
        age=user.age,
        gender=user.gender,
        weight_kg=float(user.weight_kg),
        height_cm=float(user.height_cm),
        activity_level=user.activity_level,
    )
    user.target_calories = goals.target_calories
    user.target_protein = goals.target_protein
    user.target_carb = goals.target_carb
    user.target_fat = goals.target_fat
    user.target_bmi = goals.target_bmi
    user.status = goals.status
    if user.start_date is None:
        user.start_date = date.today()


def get_profile(user: User) -> UserProfileResponse:
    return to_profile(user)


def update_profile(
    db: Session,
    user: User,
    payload: UpdateProfileRequest,
) -> UserProfileResponse:
    updates = payload.model_dump(exclude_unset=True, mode="json")
    if not updates:
        raise UsersError(400, "Provide at least one field to update")

    for api_field, column in SIMPLE_FIELDS.items():
        if api_field in updates:
            setattr(user, column, updates[api_field])

    if "weight" in updates:
        weight = updates["weight"]
        user.weight_kg = weight_to_kg(weight["value"], weight["unit"])
    if "height" in updates:
        height = updates["height"]
        user.height_cm = height_to_cm(height["feet"], height["inches"])

    if _has_complete_inputs(user):
        _apply_goals(user)

    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_profile(user)
