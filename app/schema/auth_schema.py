from pydantic import BaseModel, Field
from typing import Literal, Optional
from uuid import UUID


class TokenResponseSchema(BaseModel):
    """Schema for JWT token response after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Access token expiration time in seconds")


class RefreshTokenRequestSchema(BaseModel):
    """Schema for refresh token request body."""

    refresh_token: str


class UserResponseSchema(BaseModel):
    """Schema for user profile response."""

    id: UUID
    name: str
    email: str
    role: str
    profile_picture: Optional[str] = None
    oauth_provider: Optional[str] = None

    class Config:
        from_attributes = True


class AuthErrorSchema(BaseModel):
    """Schema for authentication error responses."""

    success: bool = False
    message: str
    error: Optional[str] = None


class AdminCreateUserSchema(BaseModel):
    """Schema for admin creating a new user manually."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    role: Literal["user", "admin"] = "user"
    profile_picture: Optional[str] = Field(None, max_length=500)


class AdminUpdateUserSchema(BaseModel):
    """Schema for admin updating a user's details or role."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[Literal["user", "admin"]] = None
    profile_picture: Optional[str] = Field(None, max_length=500)
