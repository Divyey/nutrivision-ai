from datetime import datetime, timezone

from infrastructure.database.models.user import User

API_V1 = "/api/v1"

VALID_USER = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "password": "supersecret",
}

COMPLETE_PROFILE = {
    "age": 30,
    "gender": "male",
    "weight": {"value": 80, "unit": "kg"},
    "height": {"feet": 5, "inches": 11},
    "activity_level": "sedentary",
    "vegan": "no",
    "allergy": "none",
}


def register(client, **overrides):
    payload = {**VALID_USER, **overrides}
    return client.post(f"{API_V1}/auth/register", json=payload)


def login(client, email=VALID_USER["email"], password=VALID_USER["password"]):
    return client.post(
        f"{API_V1}/auth/login",
        json={"email": email, "password": password},
    )


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def auth_headers(client) -> dict[str, str]:
    register(client)
    token = login(client).json()["access_token"]
    return bearer(token)


def soft_delete(db_session, email: str) -> None:
    db = db_session()
    try:
        user = db.query(User).filter(User.email == email.lower()).one()
        user.deleted_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
    finally:
        db.close()
