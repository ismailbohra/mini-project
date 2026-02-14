from typing import List

from app.admin.interface import AdminRepositoryInterface
from app.admin.schema import AssignRoleRequest, AssignRoleResponse, ToggleUserResponse
from app.users.model import RoleType, User
from app.users.schema import UserResponse
from app.utils.exceptions import (
    NotFoundException,
    UserNotFoundException,
)
from app.utils.logging import get_logger
from app.utils.redis import clear_user_role_cache

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
