"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class UserRegisterRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters")


class UserLoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user response (public data only)"""
    id: UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    """Schema for data extracted from JWT token"""
    user_id: UUID | None = None
    email: str | None = None
