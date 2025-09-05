"""SQLModel Schema Organization
==========================
This module contains all database models, schemas, and related types
organized by functional area for better maintainability.
"""

import uuid
from datetime import UTC, date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BeforeValidator, EmailStr
from sqlmodel import Field, Relationship, SQLModel

# ============================================================
# VALIDATORS & CUSTOM TYPES
# ============================================================


def lowercase_str(v: str | None) -> str | None:
    """Convert string to lowercase and strip whitespace."""
    if isinstance(v, str):
        return v.lower().strip()
    return v

# Custom type annotations
LowercaseStr = Annotated[str, BeforeValidator(lowercase_str)]
LowercaseEmailStr = Annotated[EmailStr, BeforeValidator(lowercase_str)]


# ============================================================
# ENUMS
# ============================================================


class UserRole(str, Enum):
    """User role enumeration."""

    USER = "user"
    ADMIN = "admin"

# ============================================================
# PHOTO MODULE
# ============================================================


class PhotoBase(SQLModel):
    """Base photo model with common fields."""

    small_uri: str | None = Field(default=None, max_length=500)
    medium_uri: str | None = Field(default=None, max_length=500)
    large_uri: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Photo(PhotoBase, table=True):
    """Photo table model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# ============================================================
# USER MODULE
# ============================================================


class UserBase(SQLModel):
    """Base user model with common fields."""

    name: str = Field(min_length=8, max_length=40)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    account: str = Field(unique=True, max_length=32)
    roles: UserRole = Field(default=UserRole.USER)

    is_active: bool = True
    is_verified: bool = True
    is_superuser: bool = False

    bio: str | None = Field(default=None, max_length=200)
    dob: date | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=20)

    avatar_photo_id: uuid.UUID | None = Field(default=None, foreign_key="photo.id")

    deleted_at: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class User(UserBase, table=True):
    """User table model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str
    avatar_photo: Photo | None = Relationship(back_populates=None)

    # Relationships


# User Schemas
class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """Schema for user registration."""

    name: str = Field(min_length=8, max_length=40)
    email: LowercaseEmailStr = Field(max_length=255)
    account: LowercaseStr = Field(min_length=6, max_length=32)
    bio: str | None = Field(default=None, max_length=1000)
    dob: date | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=40)


class UserUpdate(UserBase):
    """Schema for updating user information."""

    email: LowercaseEmailStr = Field(default=None, max_length=255)  # type: ignore
    account: LowercaseStr = Field(default=None, min_length=6, max_length=32)  # type: ignore
    password: str = Field(default=None, min_length=8, max_length=40)


class UpdatePassword(SQLModel):
    """Schema for updating user password."""

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    """Public user schema (excludes sensitive information)."""

    id: uuid.UUID


class UsersPublic(SQLModel):
    """Schema for paginated user list."""

    data: list[UserPublic]
    count: int

# ============================================================
# AUTHENTICATION MODULE
# ============================================================


class Message(SQLModel):
    """Generic message schema."""

    message: str


class Token(SQLModel):
    """JSON payload containing access token."""

    access_token: str
    token_type: str = "bearer"


class TokenWithRefresh(SQLModel):
    """JSON payload containing both access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(SQLModel):
    """Refresh token request schema."""

    refresh_token: str


class TokenPayload(SQLModel):
    """Contents of JWT token."""

    sub: str | None = None


class NewPassword(SQLModel):
    """Schema for password reset."""

    token: str
    new_password: str = Field(min_length=8, max_length=40)


class EmailPasswordLogin(SQLModel):
    """Schema for email/password login."""

    email: str
    password: str