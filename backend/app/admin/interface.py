# app/admin/interface.py
from abc import ABC, abstractmethod
from typing import List, Optional

from app.users.model import RoleType, User


class AdminRepositoryInterface(ABC):
    """Interface for admin repository."""

    @abstractmethod
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def update_user_role(self, user: User, role: RoleType) -> User:
        """Update user role."""
        pass

    @abstractmethod
    async def toggle_user(self, user: User) -> User:
        """Toggle a user's active status (activate/deactivate)."""
        pass
