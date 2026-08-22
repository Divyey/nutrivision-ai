from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from infrastructure.database.models.user import User
from infrastructure.database.session import get_db
from services.auth.middleware.auth_middleware import get_current_user
from services.users.controller.users_controller import me as read_current_profile
from services.users.controller.users_controller import update_me
from services.users.schema.users_schema import UpdateProfileRequest, UserProfileResponse
from services.users.services.users_health import check_users_health

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/health", summary="Users service health")
def users_health():
    result = check_users_health()
    payload = {"service": "users", **result}
    if result["status"] == "healthy":
        return payload
    return JSONResponse(status_code=503, content=payload)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get the current user's profile and goals",
)
def read_me(user: User = Depends(get_current_user)) -> UserProfileResponse:
    return read_current_profile(user)


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update profile fields and recompute stored goals when complete",
)
def patch_me(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    return update_me(payload, user, db)
