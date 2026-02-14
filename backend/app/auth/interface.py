# app/auth/interface.py
from abc import ABC, abstractmethod
from typing import Optional

from app.users.model import RoleType, User


class AuthRepositoryInterface(ABC):
    """Interface for authentication repository."""

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: RoleType = RoleType.USER,
    ) -> User:
        """Create a new user with specified role."""
        pass

    @abstractmethod
    async def update_user_password(self, user: User, hashed_password: str) -> User:
        """Update user password."""
        pass
