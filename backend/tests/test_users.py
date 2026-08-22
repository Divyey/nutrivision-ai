from helpers import (
    API_V1,
    COMPLETE_PROFILE,
    VALID_USER,
    auth_headers,
    bearer,
    login,
    register,
    soft_delete,
)
from infrastructure.database.models.user import User
from services.users.services.users_goals import (
    CALORIE_DEFICIT,
    calculate_goals,
    calculate_tdee,
)
from services.users.services.users_units import (
    UNSPECIFIED_BMR_OFFSET,
    height_to_cm,
    weight_to_kg,
)

PROFILE_PATH = f"{API_V1}/users/me"
SETUP_HEIGHT_CM = height_to_cm(5, 11)


def _energy(profile: dict) -> float:
    return (
        4 * profile["target_protein"]
        + 4 * profile["target_carb"]
        + 9 * profile["target_fat"]
    )


def _expected_goals(**overrides):
    payload = {
        "age": 30,
        "gender": "male",
        "weight_kg": 80.0,
        "height_cm": SETUP_HEIGHT_CM,
        "activity_level": "sedentary",
        **overrides,
    }
    return calculate_goals(**payload)


class TestCalculateGoals:
    def test_target_calories_is_tdee_minus_500(self):
        goals = calculate_goals(
            age=30,
            gender="male",
            weight_kg=80,
            height_cm=SETUP_HEIGHT_CM,
            activity_level="sedentary",
        )
        tdee = calculate_tdee(
            age=30,
            gender="male",
            weight_kg=80,
            height_cm=SETUP_HEIGHT_CM,
            activity_level="sedentary",
        )
        assert goals.target_calories == round(tdee - CALORIE_DEFICIT, 2)

    def test_macros_are_percentages_of_target_calories(self):
        goals = calculate_goals(
            age=30,
            gender="male",
            weight_kg=80,
            height_cm=SETUP_HEIGHT_CM,
            activity_level="sedentary",
        )
        assert goals.target_protein == round((goals.target_calories * 0.30) / 4, 2)
        assert goals.target_carb == round((goals.target_calories * 0.40) / 4, 2)
        assert goals.target_fat == round((goals.target_calories * 0.30) / 9, 2)
        assert abs(_energy(goals.__dict__) - goals.target_calories) < 1

    def test_unspecified_gender_uses_midpoint_offset(self):
        male = calculate_tdee(
            age=30,
            gender="male",
            weight_kg=80,
            height_cm=SETUP_HEIGHT_CM,
            activity_level="sedentary",
        )
        unspecified = calculate_tdee(
            age=30,
            gender="unspecified",
            weight_kg=80,
            height_cm=SETUP_HEIGHT_CM,
            activity_level="sedentary",
        )
        assert unspecified == male - (5 - UNSPECIFIED_BMR_OFFSET) * 1.2


class TestGetProfile:
    def test_incomplete_profile_returns_null_goals(self, client):
        headers = auth_headers(client)
        response = client.get(PROFILE_PATH, headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == VALID_USER["email"]
        assert body["age"] is None
        assert body["weight"] is None
        assert body["height"] is None
        assert body["vegan"] is None
        assert body["allergy"] is None
        assert body["target_calories"] is None
        assert body["target_protein"] is None
        assert body["start_date"] is None

    def test_unauthenticated(self, client):
        response = client.get(PROFILE_PATH)
        assert response.status_code == 401

    def test_invalid_token(self, client):
        response = client.get(PROFILE_PATH, headers=bearer("not-a-token"))
        assert response.status_code == 401

    def test_deleted_user_cannot_read_profile(self, client, db_session):
        register(client)
        token = login(client).json()["access_token"]
        soft_delete(db_session, VALID_USER["email"])
        response = client.get(PROFILE_PATH, headers=bearer(token))
        assert response.status_code == 401


class TestPatchProfile:
    def test_setup_persists_recomputed_goals(self, client, db_session):
        headers = auth_headers(client)
        response = client.patch(PROFILE_PATH, headers=headers, json=COMPLETE_PROFILE)
        assert response.status_code == 200
        body = response.json()
        expected = _expected_goals()
        assert body["height"] == {"feet": 5, "inches": 11}
        assert body["weight"] == {"value": 80.0, "unit": "kg"}
        assert body["vegan"] == "no"
        assert body["allergy"] == "none"
        assert body["target_calories"] == expected.target_calories
        assert body["target_protein"] == expected.target_protein
        assert body["target_carb"] == expected.target_carb
        assert body["target_fat"] == expected.target_fat
        assert body["target_bmi"] == expected.target_bmi
        assert body["status"] == expected.status
        assert body["start_date"] is not None
        assert abs(_energy(body) - body["target_calories"]) < 1

        db = db_session()
        try:
            user = db.query(User).one()
            assert float(user.target_calories) == expected.target_calories
            assert float(user.height_cm) == SETUP_HEIGHT_CM
            assert user.vegan_status == "no"
            assert user.allergy == "none"
            assert user.start_date is not None
        finally:
            db.close()

    def test_weight_lb_converts_to_kg(self, client, db_session):
        headers = auth_headers(client)
        response = client.patch(
            PROFILE_PATH,
            headers=headers,
            json={
                **COMPLETE_PROFILE,
                "weight": {"value": 176.37, "unit": "lb"},
            },
        )
        assert response.status_code == 200
        stored_kg = weight_to_kg(176.37, "lb")
        assert response.json()["weight"] == {"value": stored_kg, "unit": "kg"}
        db = db_session()
        try:
            user = db.query(User).one()
            assert float(user.weight_kg) == stored_kg
        finally:
            db.close()

    def test_patch_weight_recomputes_and_persists(self, client, db_session):
        headers = auth_headers(client)
        client.patch(PROFILE_PATH, headers=headers, json=COMPLETE_PROFILE)
        before = client.get(PROFILE_PATH, headers=headers).json()
        start_date = before["start_date"]

        response = client.patch(
            PROFILE_PATH,
            headers=headers,
            json={"weight": {"value": 95, "unit": "kg"}},
        )
        assert response.status_code == 200
        body = response.json()
        expected = _expected_goals(weight_kg=95)
        assert body["target_calories"] == expected.target_calories
        assert body["target_calories"] != before["target_calories"]
        assert body["target_protein"] == expected.target_protein
        assert body["start_date"] == start_date

        db = db_session()
        try:
            user = db.query(User).one()
            assert float(user.weight_kg) == 95
            assert float(user.target_calories) == expected.target_calories
        finally:
            db.close()

    def test_patch_age_and_activity_recomputes(self, client):
        headers = auth_headers(client)
        client.patch(
            PROFILE_PATH,
            headers=headers,
            json={
                **COMPLETE_PROFILE,
                "gender": "female",
                "weight": {"value": 65, "unit": "kg"},
                "height": {"feet": 5, "inches": 7},
            },
        )
        response = client.patch(
            PROFILE_PATH,
            headers=headers,
            json={"age": 40, "activity_level": "very_active"},
        )
        expected = _expected_goals(
            age=40,
            gender="female",
            weight_kg=65,
            height_cm=height_to_cm(5, 7),
            activity_level="very_active",
        )
        body = response.json()
        assert body["target_calories"] == expected.target_calories
        assert body["target_protein"] == expected.target_protein

    def test_incomplete_patch_does_not_invent_goals(self, client, db_session):
        headers = auth_headers(client)
        response = client.patch(
            PROFILE_PATH,
            headers=headers,
            json={"weight": {"value": 80, "unit": "kg"}, "age": 30},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["weight"] == {"value": 80.0, "unit": "kg"}
        assert body["age"] == 30
        assert body["target_calories"] is None
        assert body["status"] is None
        assert body["start_date"] is None

        db = db_session()
        try:
            user = db.query(User).one()
            assert user.target_calories is None
        finally:
            db.close()

    def test_empty_patch(self, client):
        headers = auth_headers(client)
        response = client.patch(PROFILE_PATH, headers=headers, json={})
        assert response.status_code == 400

    def test_invalid_activity_level(self, client):
        headers = auth_headers(client)
        response = client.patch(
            PROFILE_PATH,
            headers=headers,
            json={"activity_level": "lightly active"},
        )
        assert response.status_code == 422

    def test_patch_allergy(self, client):
        headers = auth_headers(client)
        client.patch(PROFILE_PATH, headers=headers, json=COMPLETE_PROFILE)
        response = client.patch(
            PROFILE_PATH,
            headers=headers,
            json={"allergy": "gluten"},
        )
        assert response.status_code == 200
        assert response.json()["allergy"] == "gluten"

    def test_unauthenticated(self, client):
        response = client.patch(
            PROFILE_PATH,
            json={"weight": {"value": 80, "unit": "kg"}},
        )
        assert response.status_code == 401
