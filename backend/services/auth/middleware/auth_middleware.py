from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from core.security import decode_access_token
from infrastructure.database.models.user import User
from infrastructure.database.session import get_db
from services.auth.services.auth_service import AuthError, require_active_user

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_id = decode_access_token(credentials.credentials)
        return require_active_user(db, user_id)
    except (InvalidTokenError, ValueError, AuthError):
        raise HTTPException(
            status_code=401, detail="Could not validate credentials"
        ) from None
