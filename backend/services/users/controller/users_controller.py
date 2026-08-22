from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from infrastructure.database.models.user import User
from services.users.schema.users_schema import UpdateProfileRequest, UserProfileResponse
from services.users.services import users_service
from services.users.services.users_service import UsersError

T = TypeVar("T")


def _run(fn: Callable[..., T], *args: object, **kwargs: object) -> T:
    try:
        return fn(*args, **kwargs)
    except UsersError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


def me(user: User) -> UserProfileResponse:
    return users_service.get_profile(user)


def update_me(
    payload: UpdateProfileRequest,
    user: User,
    db: Session,
) -> UserProfileResponse:
    return _run(users_service.update_profile, db, user, payload)
