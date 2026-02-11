# app/users/schema.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


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
