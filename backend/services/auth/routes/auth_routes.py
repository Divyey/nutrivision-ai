from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from infrastructure.database.models.user import User
from infrastructure.database.session import get_db
from services.auth.controller.auth_controller import (
    login as login_user,
    me as read_current_user,
    register as register_user,
    update_me,
)
from services.auth.middleware.auth_middleware import get_current_user
from services.auth.schema.auth_schema import (
    LoginRequest,
    RegisterRequest,
    ReplaceUserRequest,
    TokenResponse,
    UpdateUserRequest,
    UserPublic,
)
from services.auth.services.auth_health import check_auth_health

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/health", summary="Auth service health")
def auth_health():
    result = check_auth_health()
    payload = {"service": "auth", **result}
    if result["status"] == "healthy":
        return payload
    return JSONResponse(status_code=503, content=payload)


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserPublic:
    return register_user(payload, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return login_user(payload, db)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get the current authenticated user",
)
def read_me(user: User = Depends(get_current_user)) -> UserPublic:
    return read_current_user(user)


@router.patch(
    "/me",
    response_model=UserPublic,
    summary="Partially update the current user",
)
def patch_me(
    payload: UpdateUserRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    return update_me(payload, user, db)


@router.put(
    "/me",
    response_model=UserPublic,
    summary="Replace editable profile fields",
)
def put_me(
    payload: ReplaceUserRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    return update_me(payload, user, db)
