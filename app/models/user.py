"""User-related Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user model with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    full_name: str | None = Field(None, max_length=100)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    """User creation request model."""

    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength.

        Args:
            v: Password to validate

        Returns:
            str: Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserUpdate(BaseModel):
    """User update request model."""

    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str | None) -> str | None:
        """Validate password strength if provided.

        Args:
            v: Password to validate

        Returns:
            Optional[str]: Validated password or None

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if v is None:
            return v
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserInDB(UserBase):
    """User model as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    """User response model (excludes password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT token response model."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    username: str | None = None
    role: str | None = Field(None, description="User role for RBAC")
    email: str | None = Field(None, description="User email address")
    user_id: int | None = Field(None, description="User ID from database")


class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., description="JWT refresh token")
