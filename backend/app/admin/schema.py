from datetime import datetime

from pydantic import BaseModel, Field


class AssignRoleRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to assign role to")
    role: str = Field(
        ..., pattern="^(Admin|User|Moderator)$", description="Role to assign"
    )


class AssignRoleResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ToggleUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
