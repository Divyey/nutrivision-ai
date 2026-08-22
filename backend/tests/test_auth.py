from core.security import verify_password
from helpers import API_V1, VALID_USER, bearer, login, register, soft_delete


class TestRegister:
    def test_successful_registration(self, client):
        response = register(client)
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Ada Lovelace"
        assert body["email"] == "ada@example.com"
        assert "id" in body
        assert "password" not in body
        assert "password_hash" not in body
        assert "deleted_at" not in body

    def test_duplicate_email(self, client):
        assert register(client).status_code == 201
        response = register(client, name="Other")
        assert response.status_code == 409

    def test_duplicate_email_is_case_insensitive(self, client):
        assert register(client).status_code == 201
        response = register(client, email="ADA@example.com")
        assert response.status_code == 409

    def test_invalid_email(self, client):
        response = register(client, email="not-an-email")
        assert response.status_code == 422

    def test_short_password(self, client):
        response = register(client, password="short")
        assert response.status_code == 422

    def test_empty_name(self, client):
        response = register(client, name="   ")
        assert response.status_code == 422

    def test_password_is_hashed_and_deleted_at_is_null(self, client, db_session):
        assert register(client).status_code == 201
        db = db_session()
        try:
            from infrastructure.database.models.user import User

            user = db.query(User).one()
            assert user.deleted_at is None
            assert user.password_hash != VALID_USER["password"]
            assert user.password_hash.startswith("$2")
            assert verify_password(VALID_USER["password"], user.password_hash)
        finally:
            db.close()


class TestLogin:
    def test_successful_login(self, client):
        register(client)
        response = login(client)
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"]

    def test_incorrect_password(self, client):
        register(client)
        response = login(client, password="wrong-password")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_unknown_email(self, client):
        response = login(client)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_deleted_user_cannot_log_in(self, client, db_session):
        register(client)
        soft_delete(db_session, VALID_USER["email"])
        response = login(client)
        assert response.status_code == 401


class TestMe:
    def test_authenticated_request(self, client):
        register(client)
        token = login(client).json()["access_token"]
        response = client.get(f"{API_V1}/auth/me", headers=bearer(token))
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "ada@example.com"
        assert "password_hash" not in body
        assert "deleted_at" not in body

    def test_unauthenticated_request(self, client):
        response = client.get(f"{API_V1}/auth/me")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        response = client.get(f"{API_V1}/auth/me", headers=bearer("not-a-token"))
        assert response.status_code == 401

    def test_deleted_user_cannot_access_me(self, client, db_session):
        register(client)
        token = login(client).json()["access_token"]
        soft_delete(db_session, VALID_USER["email"])
        response = client.get(f"{API_V1}/auth/me", headers=bearer(token))
        assert response.status_code == 401


class TestUpdate:
    def test_patch_name(self, client):
        register(client)
        token = login(client).json()["access_token"]
        response = client.patch(
            f"{API_V1}/auth/me",
            headers=bearer(token),
            json={"name": "Ada Byron"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Ada Byron"
        assert response.json()["email"] == "ada@example.com"

    def test_put_replaces_editable_fields(self, client):
        register(client)
        token = login(client).json()["access_token"]
        response = client.put(
            f"{API_V1}/auth/me",
            headers=bearer(token),
            json={"name": "Ada Byron", "email": "ada.byron@example.com"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "ada.byron@example.com"

    def test_unauthenticated_request(self, client):
        response = client.patch(f"{API_V1}/auth/me", json={"name": "Nope"})
        assert response.status_code == 401

    def test_invalid_email(self, client):
        register(client)
        token = login(client).json()["access_token"]
        response = client.patch(
            f"{API_V1}/auth/me",
            headers=bearer(token),
            json={"email": "bad"},
        )
        assert response.status_code == 422

    def test_empty_patch(self, client):
        register(client)
        token = login(client).json()["access_token"]
        response = client.patch(f"{API_V1}/auth/me", headers=bearer(token), json={})
        assert response.status_code == 400

    def test_duplicate_email(self, client):
        register(client)
        register(client, name="Grace Hopper", email="grace@example.com")
        token = login(client, email="grace@example.com").json()["access_token"]
        response = client.patch(
            f"{API_V1}/auth/me",
            headers=bearer(token),
            json={"email": "ada@example.com"},
        )
        assert response.status_code == 409

    def test_deleted_user_cannot_update(self, client, db_session):
        register(client)
        token = login(client).json()["access_token"]
        soft_delete(db_session, VALID_USER["email"])
        response = client.patch(
            f"{API_V1}/auth/me",
            headers=bearer(token),
            json={"name": "Ghost"},
        )
        assert response.status_code == 401
