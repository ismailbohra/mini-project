# app/auth/interface.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.auth.model import PasswordResetToken
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

    @abstractmethod
    async def create_password_reset_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Create a password reset token."""
        pass

    @abstractmethod
    async def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token by token string."""
        pass

    @abstractmethod
    async def mark_token_as_used(self, token: PasswordResetToken) -> PasswordResetToken:
        """Mark password reset token as used."""
        pass

    @abstractmethod
    async def delete_user_reset_tokens(self, user_id: int) -> None:
        """Delete all password reset tokens for a user."""
        pass
