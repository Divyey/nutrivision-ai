from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _strip_name(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("name cannot be empty")
    return stripped


def _normalize_email(value: EmailStr) -> str:
    return str(value).lower()


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return _strip_name(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return _normalize_email(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return _normalize_email(value)


class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None

    @field_validator("name")
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _strip_name(value)

    @field_validator("email")
    @classmethod
    def normalize_optional_email(cls, value: EmailStr | None) -> str | None:
        if value is None:
            return value
        return _normalize_email(value)


class ReplaceUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return _strip_name(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return _normalize_email(value)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
