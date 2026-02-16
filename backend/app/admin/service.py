from typing import List

from app.admin.interface import AdminRepositoryInterface
from app.admin.schema import (
    AssignRoleRequest,
    AssignRoleResponse,
    DashboardAnalyticsResponse,
    TagWithCount,
    ToggleUserResponse,
    UserWithMentionCount,
    UserWithPostCount,
    UserWithReportCount,
)
from app.middleware.role_verification import clear_user_role_cache
from app.users.model import RoleType, User
from app.users.schema import UserResponse
from app.utils.exceptions import (
    NotFoundException,
    UserNotFoundException,
)
from app.utils.logging import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)


class AdminService:
    def __init__(self, repository: AdminRepositoryInterface):
        self.repository = repository

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """Get all users (Admin only)."""
        users = await self.repository.get_all_users(skip, limit)
        return [self._user_to_response(user) for user in users]

    async def assign_role(
        self, request: AssignRoleRequest, assigned_by_id: int
    ) -> AssignRoleResponse:
        """Assign a role to a user (Admin only)."""
        # Check if target user exists
        user = await self.repository.get_user_by_id(request.user_id)
        if not user:
            raise NotFoundException("User not found")

        # Convert string to RoleType enum
        role_type = RoleType(request.role)

        # Update user role
        user = await self.repository.update_user_role(user, role_type)

        # Clear Redis cache for this user to force role refresh on next request
        await clear_user_role_cache(request.user_id)
        logger.info(
            f"Role updated to {role_type.value} for user {request.user_id} by admin {assigned_by_id}. Redis cache cleared."
        )

        return AssignRoleResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            role=user.role.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _user_to_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse."""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role=user.role.value,
        )

    async def toggle_user(self, user_id: int) -> ToggleUserResponse:
        """Toggle a user's active status (activate/deactivate)."""
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")

        updated_user = await self.repository.toggle_user(user)
        status = "activated" if updated_user.is_active else "deactivated"
        logger.info(f"User {user_id} {status} by admin.")

        return ToggleUserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            is_active=updated_user.is_active,
            role=updated_user.role.value,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

    async def get_dashboard_analytics(self) -> DashboardAnalyticsResponse:
        """Get comprehensive dashboard analytics."""
        # Get user statistics by role
        (
            total_users,
            admin_count,
            moderator_count,
            normal_user_count,
        ) = await self.repository.get_user_stats_by_role()

        # Get active users from websocket connections
        active_users = len(ws_manager.active_connections)

        # Get total posts
        total_posts = await self.repository.get_total_posts()

        # Get user with most posts
        user_most_posts_data = await self.repository.get_user_with_most_posts()
        user_with_most_posts = None
        if user_most_posts_data:
            user_with_most_posts = UserWithPostCount(
                user_id=user_most_posts_data[0],
                username=user_most_posts_data[1],
                profile_image=user_most_posts_data[2],
                post_count=user_most_posts_data[3],
            )

        # Get top 5 mentioned users
        top_mentioned_data = await self.repository.get_top_mentioned_users(limit=5)
        top_5_mentioned_users = [
            UserWithMentionCount(
                user_id=row[0],
                username=row[1],
                profile_image=row[2],
                mention_count=row[3],
            )
            for row in top_mentioned_data
        ]

        # Get top 5 tags
        top_tags_data = await self.repository.get_top_tags(limit=5)
        top_5_tags = [
            TagWithCount(
                tag_id=row[0],
                tag_name=row[1],
                usage_count=row[2],
            )
            for row in top_tags_data
        ]

        # Get top 5 reported users
        top_reported_data = await self.repository.get_top_reported_users(limit=5)
        top_5_reported_users = [
            UserWithReportCount(
                user_id=row[0],
                username=row[1],
                profile_image=row[2],
                report_count=row[3],
            )
            for row in top_reported_data
        ]

        return DashboardAnalyticsResponse(
            total_users=total_users,
            admin_count=admin_count,
            moderator_count=moderator_count,
            normal_user_count=normal_user_count,
            active_users=active_users,
            total_posts=total_posts,
            user_with_most_posts=user_with_most_posts,
            top_5_mentioned_users=top_5_mentioned_users,
            top_5_tags=top_5_tags,
            top_5_reported_users=top_5_reported_users,
        )
