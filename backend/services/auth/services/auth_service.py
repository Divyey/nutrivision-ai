from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from infrastructure.database.models.user import User
from services.auth.schema.auth_schema import (
    LoginRequest,
    RegisterRequest,
    ReplaceUserRequest,
    TokenResponse,
    UpdateUserRequest,
    UserPublic,
)

# Precomputed bcrypt hash so unknown-email logins still run checkpw.
_DUMMY_PASSWORD_HASH = hash_password("not-used")


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def to_public(user: User) -> UserPublic:
    return UserPublic(id=user.id, name=user.name, email=user.email)


def get_active_user_by_id(db: Session, user_id: UUID) -> User | None:
    user = db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        return None
    return user


def get_active_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email, User.deleted_at.is_(None))
        .one_or_none()
    )


def register_user(db: Session, payload: RegisterRequest) -> UserPublic:
    if get_active_user_by_email(db, payload.email) is not None:
        raise AuthError(409, "An account with this email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_public(user)


def login_user(db: Session, payload: LoginRequest) -> TokenResponse:
    user = get_active_user_by_email(db, payload.email)
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, password_hash)
    if user is None or not password_ok:
        raise AuthError(401, "Invalid email or password")

    return TokenResponse(access_token=create_access_token(user.id))


def get_current_profile(user: User) -> UserPublic:
    return to_public(user)


def update_user(
    db: Session,
    user: User,
    payload: UpdateUserRequest | ReplaceUserRequest,
) -> UserPublic:
    if (
        isinstance(payload, UpdateUserRequest)
        and payload.name is None
        and payload.email is None
    ):
        raise AuthError(400, "Provide at least one field to update")

    if payload.name is not None:
        user.name = payload.name

    if payload.email is not None:
        existing = get_active_user_by_email(db, payload.email)
        if existing is not None and existing.id != user.id:
            raise AuthError(409, "An account with this email already exists")
        user.email = payload.email

    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_public(user)


def require_active_user(db: Session, user_id: UUID) -> User:
    user = get_active_user_by_id(db, user_id)
    if user is None:
        raise AuthError(401, "Could not validate credentials")
    return user
