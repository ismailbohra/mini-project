# app/users/schema.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format - no whitespace, only alphanumeric, underscore, hyphen."""
        from app.utils.mentions import validate_username_format

        if not validate_username_format(v):
            raise ValueError(
                "Username must be 3-30 characters, contain no whitespace, "
                "start with alphanumeric or underscore, and only contain "
                "alphanumeric characters, underscores, or hyphens"
            )
        return v


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    role: str
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


class UserMentionResponse(BaseModel):
    """Response schema for user mention autocomplete."""

    id: int
    username: str
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}
