from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from infrastructure.database.models.user import User
from services.auth.schema.auth_schema import (
    LoginRequest,
    RegisterRequest,
    ReplaceUserRequest,
    TokenResponse,
    UpdateUserRequest,
    UserPublic,
)
from services.auth.services.auth_service import AuthError
from services.auth.services import auth_service

T = TypeVar("T")


def _run(fn: Callable[..., T], *args: object, **kwargs: object) -> T:
    try:
        return fn(*args, **kwargs)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


def register(payload: RegisterRequest, db: Session) -> UserPublic:
    return _run(auth_service.register_user, db, payload)


def login(payload: LoginRequest, db: Session) -> TokenResponse:
    return _run(auth_service.login_user, db, payload)


def me(user: User) -> UserPublic:
    return auth_service.get_current_profile(user)


def update_me(
    payload: UpdateUserRequest | ReplaceUserRequest,
    user: User,
    db: Session,
) -> UserPublic:
    return _run(auth_service.update_user, db, user, payload)
