from datetime import datetime
from typing import List

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


class UserWithPostCount(BaseModel):
    """User with their post count."""

    user_id: int
    username: str
    profile_image: str | None
    post_count: int


class UserWithMentionCount(BaseModel):
    """User with their mention count."""

    user_id: int
    username: str
    profile_image: str | None
    mention_count: int


class TagWithCount(BaseModel):
    """Tag with usage count."""

    tag_id: int
    tag_name: str
    usage_count: int


class UserWithReportCount(BaseModel):
    """User whose posts got reported most."""

    user_id: int
    username: str
    profile_image: str | None
    report_count: int


class DashboardAnalyticsResponse(BaseModel):
    """Complete dashboard analytics response."""

    # User statistics
    total_users: int
    admin_count: int
    moderator_count: int
    normal_user_count: int
    active_users: int  # From websocket connections

    # Post statistics
    total_posts: int
    user_with_most_posts: UserWithPostCount | None

    # Engagement statistics
    top_5_mentioned_users: List[UserWithMentionCount]
    top_5_tags: List[TagWithCount]
    top_5_reported_users: List[UserWithReportCount]
