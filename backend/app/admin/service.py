from typing import List

from app.admin.repository import AdminRepository
from app.admin.schema import AssignRoleRequest
from app.auth.model import RoleType
from app.users.model import User
from app.users.schema import UserResponse
from app.utils.exceptions import NotFoundException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AdminService:
    def __init__(self, repository: AdminRepository):
        self.repository = repository

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """Get all users (Admin only)."""
        users = await self.repository.get_all_users(skip, limit)
        return [self._user_to_response(user) for user in users]

    async def assign_role(
        self, request: AssignRoleRequest, assigned_by_id: int
    ) -> UserResponse:
        """Assign a role to a user (Admin only)."""
        # Check if target user exists
        user = await self.repository.get_user_by_id(request.user_id)
        if not user:
            raise NotFoundException("User not found")

        # Convert string to RoleType enum
        role_type = RoleType(request.role)

        # Update user role
        user = await self.repository.update_user_role(user, role_type)

        return self._user_to_response(user)

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
