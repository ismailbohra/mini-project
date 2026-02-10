from pydantic import BaseModel, Field


class AssignRoleRequest(BaseModel):
    user_id: int
    role: str = Field(..., pattern="^(Admin|User|Moderator)$")
